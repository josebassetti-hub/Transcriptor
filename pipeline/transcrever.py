#!/usr/bin/env python3
"""Transcreve o áudio das aulas com faster-whisper (pt-BR) de forma RETOMÁVEL.

Desenho (plano v2, revisão): sessão/container podem cair a qualquer momento, então:
  - o WAV é fatiado em blocos de ~20 min com 10 s de sobreposição;
  - cada bloco vira knowledge/transcricoes/blocos/<video>/bloco_NN.md, COMMITADO ao
    concluir (durabilidade em git, não em disco efêmero);
  - timestamps somam o offset do bloco (tempo real do vídeo);
  - retomada automática: blocos com arquivo pronto são pulados;
  - lock com PID em materiais/transcricao.lock impede execução dupla (wake-ups);
  - hotwords com o vocabulário do domínio; segmentos com avg_logprob baixo vão para
    <video>-revisar.md (candidatos a re-transcrição pontual com modelo maior);
  - ao final, blocos são fundidos em knowledge/transcricoes/<video>.md
    (segmentos totalmente dentro da zona de sobreposição são descartados).

Uso:
  python3 pipeline/transcrever.py materiais/audio/2.wav [--modelo small] [--sem-git]
  python3 pipeline/transcrever.py --todos
  python3 pipeline/transcrever.py materiais/audio/2.wav --simular   # ensaio sem modelo
"""
import glob
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCO_SEG = 20 * 60
OVERLAP_SEG = 10
LIMIAR_LOGPROB = -0.8   # abaixo disso o segmento entra na lista de revisão
LOCK = os.path.join(RAIZ, "materiais", "transcricao.lock")
HOTWORDS = ("BNB, FNE, PRONAF, custeio, crédito rural, adimplência, carência, "
            "amortização, INVRUR, garrote, garrota, novilha, bezerro, parição, "
            "ordenha, rebanho, pastagem, capacidade de pagamento, inversões, "
            "gleba, benfeitoria, café conilon, café arábica, sequeiro, CAR, CCIR")


def ts(seg: float) -> str:
    s = int(seg)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def rodar_ffmpeg(args: list) -> subprocess.CompletedProcess:
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    return subprocess.run([exe, "-hide_banner", "-y", *args],
                          capture_output=True, text=True)


def duracao_wav(caminho: str) -> float:
    import wave
    with wave.open(caminho, "rb") as w:
        return w.getnframes() / w.getframerate()


def adquirir_lock() -> bool:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    if os.path.exists(LOCK):
        try:
            pid = int(open(LOCK).read().strip())
            os.kill(pid, 0)          # processo existe?
            print(f"Já há transcrição em curso (pid {pid}) — abortando esta instância.")
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            print("Lock órfão encontrado — assumindo.")
    open(LOCK, "w").write(str(os.getpid()))
    return True


def soltar_lock() -> None:
    try:
        if os.path.exists(LOCK) and open(LOCK).read().strip() == str(os.getpid()):
            os.remove(LOCK)
    except OSError:
        pass


def atualizar_status(video: str, campo: str, valor) -> None:
    caminho = os.path.join(RAIZ, "knowledge", "status.json")
    status = {}
    if os.path.exists(caminho):
        status = json.load(open(caminho, encoding="utf-8"))
    status.setdefault(video, {})[campo] = valor
    status[video]["atualizado_em"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(status, open(caminho, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2, sort_keys=True)


def commit_git(caminhos: list, msg: str) -> None:
    try:
        subprocess.run(["git", "-C", RAIZ, "add", *caminhos],
                       capture_output=True, check=True)
        r = subprocess.run(["git", "-C", RAIZ, "commit", "-q", "-m", msg],
                           capture_output=True, text=True)
        if r.returncode == 0:
            subprocess.run(["git", "-C", RAIZ, "push", "-q"],
                           capture_output=True, timeout=120)
    except Exception as e:  # git indisponível não pode derrubar a transcrição
        print(f"  (aviso: commit falhou: {e})")


def fatiar_bloco(wav: str, indice: int, destino: str) -> None:
    inicio = indice * (BLOCO_SEG - OVERLAP_SEG)
    r = rodar_ffmpeg(["-ss", str(inicio), "-t", str(BLOCO_SEG), "-i", wav,
                      "-c", "copy", destino])
    if r.returncode != 0:
        raise RuntimeError(f"fatiar bloco {indice} falhou: {r.stderr[-400:]}")


def transcrever_bloco(modelo, wav_bloco: str, offset: float, simular: bool) -> list:
    """Devolve [(inicio_abs, fim_abs, texto, avg_logprob)]."""
    if simular:
        dur = duracao_wav(wav_bloco)
        return [(offset + t, offset + t + 30,
                 f"[SIMULAÇÃO bloco offset {ts(offset)} t={ts(offset + t)}]", -0.2)
                for t in range(0, int(dur), 30)]
    segmentos, _info = modelo.transcribe(
        wav_bloco, language="pt", vad_filter=True, beam_size=5,
        condition_on_previous_text=False,   # anti-loop (protocolo, Etapa 1)
        hotwords=HOTWORDS)
    return [(offset + s.start, offset + s.end, s.text.strip(), s.avg_logprob)
            for s in segmentos]


def transcrever(wav: str, modelo_nome: str, simular: bool, usar_git: bool) -> None:
    nome = os.path.splitext(os.path.basename(wav))[0]
    dir_blocos = os.path.join(RAIZ, "knowledge", "transcricoes", "blocos", nome)
    os.makedirs(dir_blocos, exist_ok=True)
    dur = duracao_wav(wav)
    passo = BLOCO_SEG - OVERLAP_SEG
    n_blocos = max(1, int(dur // passo) + (1 if dur % passo > OVERLAP_SEG else 0))
    print(f"== {nome}: {ts(dur)} de áudio, {n_blocos} blocos de ~{BLOCO_SEG//60}min ==",
          flush=True)

    modelo = None
    if not simular:
        from faster_whisper import WhisperModel
        modelo = WhisperModel(modelo_nome, device="cpu", compute_type="int8")

    inicio_geral = time.time()
    for i in range(n_blocos):
        destino = os.path.join(dir_blocos, f"bloco_{i:02d}.md")
        if os.path.exists(destino):
            print(f"  bloco {i+1}/{n_blocos}: já pronto, pulando.")
            continue
        offset = i * passo
        wav_bloco = os.path.join(RAIZ, "materiais", f"_bloco_{nome}_{i:02d}.wav")
        fatiar_bloco(wav, i, wav_bloco)
        t0 = time.time()
        segs = transcrever_bloco(modelo, wav_bloco, offset, simular)
        os.remove(wav_bloco)

        with open(destino + ".part", "w", encoding="utf-8") as f:
            f.write(f"<!-- bloco {i} offset {ts(offset)} modelo "
                    f"{'SIMULACAO' if simular else modelo_nome} -->\n\n")
            for ini, fim, texto, lp in segs:
                marca = " ⚠️" if lp < LIMIAR_LOGPROB else ""
                f.write(f"**[{ts(ini)}]**{marca} {texto}\n\n")
        os.replace(destino + ".part", destino)
        atualizar_status(nome, "blocos_prontos", f"{i+1}/{n_blocos}")
        if usar_git:
            commit_git([destino, os.path.join(RAIZ, "knowledge", "status.json")],
                       f"Transcrição {nome}: bloco {i+1}/{n_blocos}")
        velocidade = (min(BLOCO_SEG, dur - offset)) / max(time.time() - t0, 1)
        restante = (n_blocos - i - 1) * BLOCO_SEG / max(velocidade, 0.1)
        print(f"  bloco {i+1}/{n_blocos} OK ({velocidade:.1f}x tempo real; "
              f"~{ts(restante)} restantes)", flush=True)

    fundir_blocos(nome, dir_blocos, usar_git)
    print(f"== {nome} concluído em {ts(time.time() - inicio_geral)} ==")


def fundir_blocos(nome: str, dir_blocos: str, usar_git: bool) -> None:
    """Une blocos descartando segmentos totalmente dentro da zona de sobreposição."""
    saida = os.path.join(RAIZ, "knowledge", "transcricoes", f"{nome}.md")
    revisar = os.path.join(RAIZ, "knowledge", "transcricoes", f"{nome}-revisar.md")
    blocos = sorted(glob.glob(os.path.join(dir_blocos, "bloco_*.md")))
    passo = BLOCO_SEG - OVERLAP_SEG
    linhas, duvidas, fim_anterior = [], [], -1.0

    for i, arq in enumerate(blocos):
        offset = i * passo
        for linha in open(arq, encoding="utf-8"):
            if not linha.startswith("**["):
                continue
            hh, mm, ss = linha[3:11].split(":")
            inicio_abs = int(hh) * 3600 + int(mm) * 60 + int(ss)
            # bloco i>0: os primeiros OVERLAP_SEG segundos já vieram do bloco anterior
            if i > 0 and inicio_abs < offset + OVERLAP_SEG and inicio_abs <= fim_anterior:
                continue
            fim_anterior = inicio_abs
            linhas.append(linha.rstrip("\n"))
            if "⚠️" in linha:
                duvidas.append(linha.rstrip("\n"))

    with open(saida, "w", encoding="utf-8") as f:
        f.write(f"# Transcrição — {nome}\n\n(gerada por blocos retomáveis; ⚠️ = "
                f"confiança baixa, ver {os.path.basename(revisar)})\n\n")
        f.write("\n\n".join(linhas) + "\n")
    with open(revisar, "w", encoding="utf-8") as f:
        f.write(f"# {nome} — segmentos de baixa confiança (re-transcrever com medium "
                f"e/ou conferir no vídeo)\n\n")
        f.write("\n\n".join(duvidas) + ("\n" if duvidas else "(nenhum)\n"))
    atualizar_status(nome, "transcricao", "concluída")
    if usar_git:
        commit_git([saida, revisar, os.path.join(RAIZ, "knowledge", "status.json")],
                   f"Transcrição {nome}: fusão final ({len(linhas)} segmentos, "
                   f"{len(duvidas)} a revisar)")


def main() -> int:
    args = sys.argv[1:]
    modelo = "small"
    if "--modelo" in args:
        i = args.index("--modelo")
        modelo = args[i + 1]
        del args[i:i + 2]
    simular = "--simular" in args
    usar_git = "--sem-git" not in args
    args = [a for a in args if not a.startswith("--")]

    if not args and "--todos" not in sys.argv:
        print(__doc__)
        return 1
    arquivos = (sorted(glob.glob(os.path.join(RAIZ, "materiais", "audio", "*.wav")))
                if "--todos" in sys.argv else args)
    if not arquivos:
        print("Nenhum áudio encontrado.")
        return 1

    if not adquirir_lock():
        return 2
    try:
        for a in arquivos:
            transcrever(a, modelo, simular, usar_git)
    finally:
        soltar_lock()
    return 0


if __name__ == "__main__":
    sys.exit(main())
