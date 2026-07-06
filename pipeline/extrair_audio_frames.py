#!/usr/bin/env python3
"""Extrai áudio (para transcrição) e frames (para leitura visual) dos vídeos do curso.

Implementa a Etapa 1 do knowledge/PROTOCOLO-EXTRACAO.md:
  - Passada 1: detecta os tempos T de mudança de tela (scene>0.04, showinfo).
  - Passada 2: para cada T extrai o par ANTES (T-0,5s: tela anterior finalizada,
    números digitados) e DEPOIS (T+0,2s: tela nova assentada); frames forçados no
    segundo 0 e no último segundo; frames de segurança a cada 60s sem mudança.
  - Rajadas de digitação (mudanças a <2s) são colapsadas: guarda o primeiro e o
    último instante da rajada — a narração cobre o meio.
  - Dedup por hash perceptual ao final.

Uso:
  python3 pipeline/extrair_audio_frames.py materiais/videos/2.mov
  python3 pipeline/extrair_audio_frames.py --todos
  (opcional: --gatilho 0.02 para trechos de preenchimento campo a campo)

Saídas:
  materiais/audio/<video>.wav              — 16 kHz mono (entrada do faster-whisper)
  materiais/frames/<video>/f_HHMMSS.CC_a.jpg  (antes) / _d.jpg (depois) / _s.jpg (segurança)
"""
import glob
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import imagehash
import imageio_ffmpeg
import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
GATILHO = 0.04        # sensível: planilha muda pouco (protocolo: 0,02–0,05)
RECUO_ANTES = 0.5     # T-0,5s = tela anterior finalizada
AVANCO_DEPOIS = 0.2   # T+0,2s = tela nova assentada
JANELA_RAJADA = 2.0   # mudanças a <2s = mesma rajada de digitação
SEGURANCA_SEG = 60    # frame extra se passar 60s sem mudança
DIST_HASH = 3         # dedup: distância phash para "mesma tela"
# phash ignora cor e não vê mudança de UMA célula em tela quase uniforme (bug pego no
# ensaio sintético). Duplicata exige phash ≤ DIST_HASH **E** pixels quase idênticos:
LIMIAR_PIXEL = 0.002  # fração de pixels (64x64 cinza) com diferença > 10/255


def rodar(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([FFMPEG, "-hide_banner", *args], capture_output=True, text=True)


def extrair_audio(video: str, destino: str) -> None:
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.exists(destino):
        print(f"  áudio já existe: {destino}")
        return
    r = rodar(["-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
               "-c:a", "pcm_s16le", destino])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg áudio falhou: {r.stderr[-800:]}")
    print(f"  áudio OK: {destino} ({os.path.getsize(destino) >> 20} MB)")


def detectar_mudancas(video: str, gatilho: float) -> tuple:
    """Passada 1: devolve (lista de tempos T de mudança, duração total)."""
    r = rodar(["-i", video, "-vf", f"select='gt(scene,{gatilho})',showinfo",
               "-f", "null", "-"])
    tempos = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        raise RuntimeError(f"não achei a duração: {r.stderr[-400:]}")
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return tempos, dur


def colapsar_rajadas(tempos: list) -> list:
    """Mudanças a <JANELA_RAJADA viram [primeira, última] da rajada."""
    if not tempos:
        return []
    grupos, atual = [], [tempos[0]]
    for t in tempos[1:]:
        if t - atual[-1] < JANELA_RAJADA:
            atual.append(t)
        else:
            grupos.append(atual)
            atual = [t]
    grupos.append(atual)
    saida = []
    for g in grupos:
        saida.append(g[0])
        if g[-1] - g[0] >= JANELA_RAJADA / 2:
            saida.append(g[-1])
    return saida


def plano_de_captura(mudancas: list, dur: float) -> list:
    """Monta [(tempo, papel)] com pares antes/depois, forçados e segurança."""
    plano = [(0.0, "d")]                                   # estado inicial forçado
    for t in mudancas:
        antes = max(t - RECUO_ANTES, 0.0)
        depois = min(t + AVANCO_DEPOIS, dur - 0.1)
        plano.append((antes, "a"))
        plano.append((depois, "d"))
    plano.append((max(dur - 1.0, 0.0), "a"))               # estado final forçado
    # frames de segurança em vãos longos
    pontos = sorted(t for t, _ in plano)
    ultimo = 0.0
    for p in pontos + [dur]:
        while p - ultimo > SEGURANCA_SEG:
            ultimo += SEGURANCA_SEG
            plano.append((ultimo, "s"))
        ultimo = max(ultimo, p)
    plano.sort()
    return plano


def nome_frame(pasta: str, t: float, papel: str) -> str:
    s = int(t)
    cc = int(round((t - s) * 100))
    return os.path.join(pasta, f"f_{s//3600:02d}{(s%3600)//60:02d}{s%60:02d}.{cc:02d}_{papel}.jpg")


def extrair_um(video: str, t: float, destino: str) -> bool:
    r = rodar(["-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
               "-q:v", "3", destino])
    return r.returncode == 0 and os.path.exists(destino)


def extrair_frames(video: str, pasta: str, gatilho: float) -> None:
    os.makedirs(pasta, exist_ok=True)
    print("  passada 1: detectando mudanças de tela...", flush=True)
    tempos, dur = detectar_mudancas(video, gatilho)
    mudancas = colapsar_rajadas(tempos)
    plano = plano_de_captura(mudancas, dur)
    print(f"  {len(tempos)} mudanças brutas -> {len(mudancas)} após colapso de rajadas "
          f"-> {len(plano)} frames a extrair (duração {int(dur//60)}min)", flush=True)

    print("  passada 2: extraindo pares antes/depois...", flush=True)
    trabalhos = [(t, nome_frame(pasta, t, papel)) for t, papel in plano
                 if not os.path.exists(nome_frame(pasta, t, papel))]
    with ThreadPoolExecutor(max_workers=3) as ex:
        oks = list(ex.map(lambda w: extrair_um(video, w[0], w[1]), trabalhos))
    falhas = oks.count(False)

    # dedup: duplicata só se phash E diferença de pixels concordarem (ver LIMIAR_PIXEL)
    arquivos = sorted(glob.glob(os.path.join(pasta, "f_*.jpg")))
    ultimo_hash, ultima_matriz, removidos = None, None, 0
    for arq in arquivos:
        img = Image.open(arq)
        h = imagehash.phash(img)
        matriz = np.asarray(img.convert("L").resize((64, 64)), dtype=np.int16)
        if ultimo_hash is not None and h - ultimo_hash <= DIST_HASH:
            frac_dif = float(np.mean(np.abs(matriz - ultima_matriz) > 10))
            if frac_dif < LIMIAR_PIXEL:
                os.remove(arq)
                removidos += 1
                continue
        ultimo_hash, ultima_matriz = h, matriz
    mantidos = len(arquivos) - removidos
    print(f"  frames OK: {mantidos} únicos ({removidos} duplicados removidos, "
          f"{falhas} falhas) em {pasta}")


def processar(video: str, gatilho: float) -> None:
    nome = os.path.splitext(os.path.basename(video))[0]
    print(f"== {video} ==")
    extrair_audio(video, os.path.join(RAIZ, "materiais", "audio", f"{nome}.wav"))
    extrair_frames(video, os.path.join(RAIZ, "materiais", "frames", nome), gatilho)


def main() -> int:
    args = sys.argv[1:]
    gatilho = GATILHO
    if "--gatilho" in args:
        i = args.index("--gatilho")
        gatilho = float(args[i + 1])
        del args[i:i + 2]

    if "--todos" in args:
        videos = sorted(glob.glob(os.path.join(RAIZ, "materiais", "videos", "*.mov")))
        if not videos:
            print("Nenhum vídeo em materiais/videos/ — rode antes o download_drive.py")
            return 1
    else:
        videos = args
        if not videos:
            print(__doc__)
            return 1
    for v in videos:
        processar(v, gatilho)
    return 0


if __name__ == "__main__":
    sys.exit(main())
