#!/usr/bin/env python3
"""Extrai AÇÕES de interface (cursor, cliques, digitação) dos pixels de um vídeo.

Complementa transcribe.py (fala) e extract_frames.py (telas): reconstrói a
telemetria que uma gravação de tela não tem como dado — trajetória do mouse,
cliques e texto digitado — analisando os próprios quadros.

Uso:
  python3 extract_actions.py --video video.mp4 --outdir saida/ [--fps 10]

Saídas no outdir:
  actions.json : {"trajetoria": [{t,x,y,conf}...],
                  "acoes": [{t, tipo: click|type, x, y, alvo_texto, valor,
                             cadencia_cps, confianca}...]}
  actions.txt  : versão legível "[MM:SS] clique em (x,y) 'texto próximo'"

Como funciona (v1):
  cursor   — template matching multi-escala de setas padrão (Windows/browser),
             geradas internamente; trilha suavizada, saltos rejeitados.
  clique   — micro-pausa da trajetória + mudança local da tela logo após
             (diff numa janela ao redor do cursor).
  digitação— crescimento monotônico de "tinta" numa região estável após um
             clique (episódio de digitação); texto final via tesseract (se
             instalado); cadência = caracteres / duração.
Limites conhecidos: cursores fora do padrão, vídeos < 720p e digitação sem
eco visual (senhas) reduzem a confiança — ações duvidosas saem com
confianca < 0.5 e devem ser tratadas como hipótese no SOP.
"""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np


def fmt(t: float) -> str:
    m, s = divmod(int(t), 60)
    return f"{m:02d}:{s:02d}"


# --- templates de cursor ------------------------------------------------------
def cursor_templates():
    """Setas padrão (branca com contorno preto e a variante invertida), em
    3 escalas — cobre o cursor clássico do Windows e o do navegador."""
    base = np.array([[0, 0], [0, 16], [4, 12], [7, 19], [10, 18], [7, 11],
                     [12, 11]], np.int32)
    temps = []
    for scale in (0.8, 1.0, 1.4):
        pts = (base * scale).astype(np.int32)
        w, h = pts[:, 0].max() + 3, pts[:, 1].max() + 3
        for fill, edge in (((255,), (0,)), ((0,), (255,))):
            img = np.full((h, w), 127, np.uint8)
            cv2.fillPoly(img, [pts + 1], fill)
            cv2.polylines(img, [pts + 1], True, edge, 1, cv2.LINE_AA)
            temps.append(img)
    return temps


def track_cursor(frames, min_score=0.55):
    """Trilha (t_idx -> (x, y, conf)); None quando não achado."""
    temps = cursor_templates()
    track = []
    last = None
    for gray in frames:
        best = (None, 0.0)
        for tp in temps:
            res = cv2.matchTemplate(gray, tp, cv2.TM_CCOEFF_NORMED)
            _, score, _, loc = cv2.minMaxLoc(res)
            if score > best[1]:
                best = ((loc[0] + 2, loc[1] + 2), score)
        pos, score = best
        if pos is None or score < min_score:
            track.append(None)
            continue
        if last and abs(pos[0] - last[0]) + abs(pos[1] - last[1]) > 600:
            track.append(None)          # salto impossível — provável falso positivo
            continue
        track.append((pos[0], pos[1], round(float(score), 3)))
        last = pos
    return track


# --- detecção de cliques ------------------------------------------------------
def detect_clicks(frames, track, fps, win=70, pct_thresh=0.8):
    """Pausa do cursor + mudança local da tela DURANTE a pausa (o feedback do
    clique — botão afundando, campo focando, tela trocando — acontece com o
    cursor parado) ou logo depois dela. Métrica: % de pixels da janela que
    mudaram de verdade (>25 níveis) — pega tanto um botão inteiro escurecendo
    quanto uma borda fina de campo + caret."""
    cliques = []
    i = 0
    n = len(track)
    while i < n:
        p = track[i]
        if p is None:
            i += 1
            continue
        j = i
        while j + 1 < n and track[j + 1] and \
                abs(track[j + 1][0] - p[0]) + abs(track[j + 1][1] - p[1]) < 6:
            j += 1
        pausa_frames = j - i + 1
        if pausa_frames >= max(2, int(0.2 * fps)):
            x, y = p[0], p[1]
            ref = frames[i]
            y0, y1 = max(0, y - win), min(ref.shape[0], y + win)
            x0, x1 = max(0, x - win), min(ref.shape[1], x + win)
            k_fim = min(n - 1, j + int(0.8 * fps))
            t_click, pico = None, 0.0
            for k in range(i + 1, k_fim + 1):
                d = cv2.absdiff(ref[y0:y1, x0:x1], frames[k][y0:y1, x0:x1])
                # o movimento do PRÓPRIO cursor não é mudança de UI: apaga a
                # área dele (no quadro de referência e no atual) antes de medir
                for pk in (track[i], track[k] if k < len(track) else None):
                    if pk:
                        cx, cy = pk[0] - x0 - 6, pk[1] - y0 - 6
                        d[max(0, cy):max(0, cy) + 40, max(0, cx):max(0, cx) + 34] = 0
                pct = float((d > 25).mean() * 100)
                if pct > pico:
                    pico = pct
                if t_click is None and pct >= pct_thresh:
                    t_click = k / fps
            if t_click is not None:
                conf = min(0.95, 0.45 + pico / 60 + p[2] / 5)
                cliques.append({"t": round(t_click, 2), "x": x, "y": y,
                                "confianca": round(conf, 2)})
        i = j + 1
    # dois cliques quase simultâneos no mesmo lugar = duplo clique
    dedup = []
    for c in cliques:
        if dedup and c["t"] - dedup[-1]["t"] < 0.5 and \
                abs(c["x"] - dedup[-1]["x"]) + abs(c["y"] - dedup[-1]["y"]) < 12:
            dedup[-1]["duplo"] = True
            continue
        dedup.append(c)
    return dedup


# --- detecção de digitação ----------------------------------------------------
def detect_typing(frames, cliques, fps, span=(280, 44)):
    """Após cada clique, procura crescimento monotônico de tinta escura à
    direita do ponto clicado (texto surgindo). Retorna episódios."""
    episodios = []
    for c in cliques:
        x, y = c["x"], c["y"]
        x0, x1 = max(0, x - span[0]), min(frames[0].shape[1], x + span[0])
        y0, y1 = max(0, y - span[1] // 2), min(frames[0].shape[0], y + span[1] // 2)
        k0 = int(c["t"] * fps)
        tinta = []
        for k in range(k0, min(len(frames), k0 + int(10 * fps))):
            crop = frames[k][y0:y1, x0:x1]
            tinta.append(int((crop < 90).sum()))
        if len(tinta) < int(1.5 * fps):
            continue
        base = tinta[0]
        cresc = [v - base for v in tinta]
        pico = max(cresc)
        if pico < 250:                      # nada substancial digitado
            continue
        # texto digitado PERSISTE na tela; flash de botão/transição REVERTE.
        if cresc[-1] < 0.6 * pico:
            continue
        # início/fim do crescimento sustentado
        ini = next((k for k, v in enumerate(cresc) if v > pico * 0.08), 0)
        fim = next((len(cresc) - 1 - k for k, v in enumerate(reversed(cresc))
                    if v >= pico * 0.92), len(cresc) - 1)
        if fim <= ini + int(0.5 * fps):     # surgiu de uma vez = colagem, não digitação
            tipo = "paste"
        else:
            tipo = "type"
        t_ini, t_fim = round(c["t"] + ini / fps, 2), round(c["t"] + fim / fps, 2)
        texto = ocr_crop(frames[min(len(frames) - 1, k0 + fim)][y0:y1, x0:x1])
        texto = texto.strip(" |").strip()   # caret piscando vira '|' no OCR
        if not texto:                       # sem texto legível = só hipótese fraca
            continue
        cad = round(len(texto) / max(t_fim - t_ini, 0.5), 1) if texto else None
        episodios.append({"t": t_ini, "t_fim": t_fim, "tipo": tipo,
                          "x": x, "y": y, "valor": texto,
                          "cadencia_cps": cad if tipo == "type" else None,
                          "confianca": 0.7 if texto else 0.4})
    return episodios


def ocr_crop(gray_crop) -> str:
    if not shutil.which("tesseract"):
        return ""
    big = cv2.resize(gray_crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, big)
        p = subprocess.run(["tesseract", f.name, "stdout", "--psm", "7", "-l",
                            "por+eng"], capture_output=True, text=True)
    Path(f.name).unlink(missing_ok=True)
    return p.stdout.strip().replace("\n", " ")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--fps", type=float, default=10.0, help="taxa de análise")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"ERRO: não abri o vídeo {args.video}")
        return 1
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    passo = max(1, round(src_fps / args.fps))
    fps = src_fps / passo

    frames = []
    k = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if k % passo == 0:
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if g.shape[1] > 1280:
                esc = 1280 / g.shape[1]
                g = cv2.resize(g, None, fx=esc, fy=esc)
            frames.append(g)
        k += 1
    cap.release()
    if not frames:
        print("ERRO: vídeo sem quadros legíveis")
        return 1
    print(f"[actions] {len(frames)} quadros analisados a {fps:.1f} fps")

    track = track_cursor(frames)
    achados = sum(1 for p in track if p)
    print(f"[actions] cursor localizado em {achados}/{len(track)} quadros")

    cliques = detect_clicks(frames, track, fps)
    digitacoes = detect_typing(frames, cliques, fps)

    acoes = sorted(
        [{"tipo": "click", **c} for c in cliques] +
        [{"tipo": d.pop("tipo"), **d} for d in digitacoes],
        key=lambda a: a["t"])

    traj = [{"t": round(i / fps, 2), "x": p[0], "y": p[1], "conf": p[2]}
            for i, p in enumerate(track) if p]
    (outdir / "actions.json").write_text(json.dumps(
        {"fps_analise": round(fps, 2), "trajetoria": traj, "acoes": acoes},
        ensure_ascii=False, indent=1), encoding="utf-8")

    with (outdir / "actions.txt").open("w", encoding="utf-8") as f:
        for a in acoes:
            if a["tipo"] == "click":
                linha = (f"[{fmt(a['t'])}] clique{' DUPLO' if a.get('duplo') else ''} "
                         f"em ({a['x']},{a['y']}) conf={a['confianca']}")
            else:
                linha = (f"[{fmt(a['t'])}-{fmt(a['t_fim'])}] {a['tipo']} "
                         f"'{a['valor']}' ({a.get('cadencia_cps') or '-'} cps) "
                         f"conf={a['confianca']}")
            f.write(linha + "\n")
            print(linha)

    print(f"[actions] {len(acoes)} ações -> {outdir/'actions.json'}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
