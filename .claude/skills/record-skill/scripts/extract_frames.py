#!/usr/bin/env python3
"""Extrai quadros representativos da tela de um vídeo de treinamento.

Estratégia (espelha o que o Record a Skill oficial captura ao vivo):
  1. Mudanças de cena (filtro scene do ffmpeg) com threshold ADAPTATIVO —
     cada mudança vira um PAR causa→efeito: um quadro imediatamente antes
     (estado da tela em que a ação foi feita) e um logo depois (resultado).
     É o substituto, em vídeo pré-gravado, dos eventos de clique/tecla.
  2. Amostragem periódica — cobertura de segurança em trechos sem mudança.

Saída: frames/frame_NNNN_t<segundos>s_<papel>.jpg e frames_index.json com
[{frame, time, role}] em ordem cronológica. Papéis: inicio, antes, depois,
periodico, fim.

Uso:
  python3 extract_frames.py --video video.mp4 --outdir saida/ \
      [--max-frames 120] [--scene-threshold 0.1] [--interval 20]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PRE_OFFSET = 0.6   # s antes da mudança: tela onde a ação aconteceu
POST_OFFSET = 0.3  # s depois: resultado já renderizado


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
    proc = subprocess.run(
        ["ffmpeg", "-i", str(video),
         "-vf", f"select='gt(scene,{threshold})',showinfo",
         "-fps_mode", "vfr", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return [float(m) for m in re.findall(r"pts_time:\s*([0-9.]+)", proc.stderr)]


def adaptive_scenes(video: Path, threshold: float, duration: float) -> tuple:
    """Ajusta o threshold até a densidade de cenas ficar plausível.

    Poucas cenas (<1/min) em geral significam threshold alto demais para
    gravações de tela (mudanças sutis); cenas demais (>1 a cada 2s) indicam
    vídeo com animações e threshold baixo demais.
    """
    for _ in range(3):
        scenes = scene_timestamps(video, threshold)
        per_min = len(scenes) / max(duration / 60.0, 0.01)
        if per_min < 1.0 and threshold > 0.03 and duration > 30:
            threshold = round(threshold / 2, 3)
            print(f"[frames] poucas cenas ({len(scenes)}) — reduzindo threshold para {threshold}")
            continue
        if len(scenes) > duration / 2 and threshold < 0.6:
            threshold = round(threshold * 2, 3)
            print(f"[frames] cenas demais ({len(scenes)}) — subindo threshold para {threshold}")
            continue
        return scenes, threshold
    return scenes, threshold


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--max-frames", type=int, default=120)
    ap.add_argument("--scene-threshold", type=float, default=0.1)
    ap.add_argument("--interval", type=float, default=20.0,
                    help="segundos entre quadros periódicos de segurança")
    ap.add_argument("--min-gap", type=float, default=2.0,
                    help="distância mínima (s) entre duas mudanças de cena distintas")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"ERRO: vídeo não encontrado: {video}", file=sys.stderr)
        return 1
    frames_dir = Path(args.outdir) / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(video)
    print(f"[frames] duração do vídeo: {duration:.1f}s")

    print(f"[frames] detectando mudanças de cena (threshold inicial={args.scene_threshold})...")
    scenes, threshold = adaptive_scenes(video, args.scene_threshold, duration)
    print(f"[frames] {len(scenes)} mudanças de cena (threshold final={threshold})")

    # dedup das cenas entre si; cada cena mantida vira um par antes/depois
    kept_scenes = []
    for t in sorted(set(scenes)):
        if not kept_scenes or t - kept_scenes[-1] >= args.min_gap:
            kept_scenes.append(t)

    events = [(0.0, "inicio")]
    for t in kept_scenes:
        pre = max(0.0, t - PRE_OFFSET)
        post = min(duration - 0.05, t + POST_OFFSET) if duration else t + POST_OFFSET
        events.append((pre, "antes"))
        events.append((post, "depois"))
    if duration > 1.0:
        events.append((max(0.0, duration - 0.5), "fim"))

    # periódicos só onde não há nenhum quadro de evento por perto
    for i in range(int(duration / args.interval) + 1):
        t = i * args.interval
        if t < duration and all(abs(t - e[0]) >= args.min_gap for e in events):
            events.append((t, "periodico"))
    events.sort(key=lambda e: e[0])

    # teto: descarta periódicos primeiro; depois reamostra pares uniformemente
    if len(events) > args.max_frames:
        core = [e for e in events if e[1] != "periodico"]
        if len(core) <= args.max_frames:
            events = core
            print(f"[frames] acima do teto — periódicos descartados ({len(events)} quadros)")
        else:
            step = (len(core) - 1) / (args.max_frames - 1)
            events = [core[round(i * step)] for i in range(args.max_frames)]
            print(f"[frames] acima do teto — reamostrado para {len(events)} quadros")

    index = []
    for i, (t, role) in enumerate(events, start=1):
        name = f"frame_{i:04d}_t{t:07.1f}s_{role}.jpg"
        out = frames_dir / name
        proc = subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video),
             "-frames:v", "1", "-q:v", "3", str(out)],
            capture_output=True, text=True,
        )
        if proc.returncode == 0 and out.exists():
            index.append({"frame": name, "time": round(t, 2), "role": role})
        else:
            print(f"[frames] aviso: falha ao extrair t={t:.1f}s", file=sys.stderr)

    (frames_dir / "frames_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    pares = sum(1 for e in index if e["role"] == "antes")
    print(f"[frames] {len(index)} quadros salvos ({pares} pares causa→efeito) em {frames_dir}/")
    return 0 if index else 1


if __name__ == "__main__":
    sys.exit(main())
