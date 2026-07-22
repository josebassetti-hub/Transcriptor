#!/usr/bin/env python3
"""Extrai quadros representativos da tela de um vídeo de treinamento.

Combina duas fontes de quadros e deduplica:
  1. Mudanças de cena (filtro scene do ffmpeg) — capturam o efeito de cada
     ação na tela (janela aberta, menu clicado, campo preenchido).
  2. Amostragem periódica — garante cobertura em trechos sem mudança visual.

Cada quadro é salvo como frames/frame_NNNN_t<segundos>s.jpg — o timestamp no
nome permite casar o quadro com o trecho correspondente do transcript.
Também gera frames/frames_index.json com a lista ordenada.

Uso:
  python3 extract_frames.py --video video.mp4 --outdir saida/ \
      [--max-frames 100] [--scene-threshold 0.1] [--interval 20]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def probe_duration(video: Path) -> float:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True,
    )
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def scene_timestamps(video: Path, threshold: float) -> list:
    """Roda o detector de cena do ffmpeg e retorna os timestamps (s)."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(video),
         "-vf", f"select='gt(scene,{threshold})',showinfo",
         "-fps_mode", "vfr", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return [float(m) for m in re.findall(r"pts_time:\s*([0-9.]+)", proc.stderr)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--max-frames", type=int, default=100)
    ap.add_argument("--scene-threshold", type=float, default=0.1)
    ap.add_argument("--interval", type=float, default=20.0,
                    help="segundos entre quadros periódicos de segurança")
    ap.add_argument("--min-gap", type=float, default=2.0,
                    help="distância mínima (s) entre dois quadros")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"ERRO: vídeo não encontrado: {video}", file=sys.stderr)
        return 1
    frames_dir = Path(args.outdir) / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(video)
    print(f"[frames] duração do vídeo: {duration:.1f}s")

    print(f"[frames] detectando mudanças de cena (threshold={args.scene_threshold})...")
    scenes = scene_timestamps(video, args.scene_threshold)
    print(f"[frames] {len(scenes)} mudanças de cena encontradas")

    # quadros de cena têm prioridade na deduplicação: são o efeito de uma ação
    # na tela, enquanto os periódicos são só cobertura de segurança
    priority = [0.0] + scenes
    if duration > 1.0:
        priority.append(max(0.0, duration - 0.5))  # última tela (resultado final)
    selected = []
    for t in sorted(set(priority)):
        if not selected or t - selected[-1] >= args.min_gap:
            selected.append(t)

    periodic = [t for t in
                (i * args.interval for i in range(int(duration / args.interval) + 1))
                if t < duration]
    for t in periodic:
        if all(abs(t - s) >= args.min_gap for s in selected):
            selected.append(t)
    selected.sort()

    # respeita o teto reamostrando uniformemente (mantém início e fim)
    if len(selected) > args.max_frames:
        step = (len(selected) - 1) / (args.max_frames - 1)
        selected = [selected[round(i * step)] for i in range(args.max_frames)]
        print(f"[frames] acima do teto — reamostrado para {len(selected)} quadros")

    index = []
    for i, t in enumerate(selected, start=1):
        name = f"frame_{i:04d}_t{t:07.1f}s.jpg"
        out = frames_dir / name
        proc = subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video),
             "-frames:v", "1", "-q:v", "3", str(out)],
            capture_output=True, text=True,
        )
        if proc.returncode == 0 and out.exists():
            index.append({"frame": name, "time": round(t, 2)})
        else:
            print(f"[frames] aviso: falha ao extrair t={t:.1f}s", file=sys.stderr)

    (frames_dir / "frames_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[frames] {len(index)} quadros salvos em {frames_dir}/")
    return 0 if index else 1


if __name__ == "__main__":
    sys.exit(main())
