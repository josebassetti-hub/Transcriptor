#!/usr/bin/env python3
"""Renderiza a "sessão simulada": o vídeo original com a telemetria
reconstruída DESENHADA por cima — cursor com anel destacado, pulso vermelho
nos cliques, faixa inferior durante a digitação — e gera demo_script.md
(o roteiro da demonstração, ação a ação).

Para que serve: transformar um vídeo cru em uma DEMONSTRAÇÃO legível — para
humanos revisarem as ações reconstruídas, e para gravações "assistidas"
(ex.: tocar em tela cheia numa sessão do Record a Skill oficial do Cowork,
que enxerga melhor cliques e digitação já sinalizados).

Uso:
  python3 render_demo.py --video video.mp4 --actions <workdir>/actions.json \
      --outdir <workdir>/sessao_simulada
O áudio original (narração) é preservado no vídeo final.
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import cv2


def fmt(t: float) -> str:
    m, s = divmod(int(t), 60)
    return f"{m:02d}:{s:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--actions", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(args.actions).read_text(encoding="utf-8"))
    traj = data.get("trajetoria", [])
    acoes = data.get("acoes", [])

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"ERRO: não abri o vídeo {args.video}")
        return 1
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    esc = W / min(W, 1280)  # a análise foi feita em quadros <=1280 de largura

    tmp = out / "_sem_audio.mp4"
    wr = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    ts = [p["t"] for p in traj]
    k, n = 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        t = n / fps
        while k + 1 < len(ts) and ts[k + 1] <= t:
            k += 1
        if traj and abs(traj[k]["t"] - t) <= 0.3:
            cv2.circle(fr, (int(traj[k]["x"] * esc), int(traj[k]["y"] * esc)),
                       22, (0, 220, 255), 3, cv2.LINE_AA)
        for ac in acoes:
            if ac["tipo"] == "click" and 0 <= t - ac["t"] <= 0.6:
                f = (t - ac["t"]) / 0.6
                x, y, r = int(ac["x"] * esc), int(ac["y"] * esc), int(24 + 36 * f)
                cv2.circle(fr, (x, y), r, (0, 0, 255), 4, cv2.LINE_AA)
                cv2.putText(fr, "CLIQUE", (x - 42, y - r - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            elif ac["tipo"] in ("type", "paste") and \
                    ac["t"] - 0.2 <= t <= ac.get("t_fim", ac["t"]) + 0.8:
                verbo = "DIGITANDO" if ac["tipo"] == "type" else "COLADO"
                faixa = f"{verbo}: {ac.get('valor', '')}"[:90]
                cv2.rectangle(fr, (0, H - 46), (W, H), (30, 30, 30), -1)
                cv2.putText(fr, faixa, (16, H - 14),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2,
                            cv2.LINE_AA)
        wr.write(fr)
        n += 1
    cap.release()
    wr.release()

    final = out / "video_demo.mp4"
    if shutil.which("ffmpeg"):
        p = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
             "-i", args.video, "-map", "0:v", "-map", "1:a?",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
             "-c:a", "copy", str(final)])
        if p.returncode == 0:
            tmp.unlink(missing_ok=True)
        else:
            tmp.rename(final)
    else:
        tmp.rename(final)

    linhas = ["# Roteiro da demonstração (reconstruído do vídeo)", ""]
    for ac in acoes:
        if ac["tipo"] == "click":
            linhas.append(f"- **{fmt(ac['t'])}** — clique"
                          + (" DUPLO" if ac.get("duplo") else "")
                          + f" em ({ac['x']},{ac['y']}) — confiança {ac['confianca']}")
        else:
            cad = f" ({ac['cadencia_cps']} caracteres/s)" if ac.get("cadencia_cps") else ""
            verbo = "digitou" if ac["tipo"] == "type" else "colou"
            linhas.append(f"- **{fmt(ac['t'])}–{fmt(ac.get('t_fim', ac['t']))}** — "
                          f"{verbo} `{ac.get('valor', '')}`{cad}")
    (out / "demo_script.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"[demo] {final.name} + demo_script.md ({len(acoes)} ações) em {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
