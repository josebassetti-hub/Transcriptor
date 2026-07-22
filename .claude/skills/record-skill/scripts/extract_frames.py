#!/usr/bin/env python3
"""Extrai quadros representativos da tela de um vídeo de treinamento.

Estratégia (espelha o que o Record a Skill oficial captura ao vivo):
  1. Mudanças de cena detectadas em UMA passada do ffmpeg (scores em memória,
     threshold ajustado sem redecodificar) — cada mudança vira um PAR
     causa→efeito: um quadro imediatamente antes (estado da tela em que a
     ação foi feita) e um logo depois (resultado). É o substituto, em vídeo
     pré-gravado, dos eventos de clique/tecla.
  2. Amostragem periódica — cobertura de segurança em trechos sem mudança.

Saída: frames/frame_NNNN_t<segundos>s_<papel>.jpg e frames/frames_index.json
com [{frame, time, role}] em ordem cronológica. Papéis: inicio, antes,
depois, periodico, fim.

Uso:
  python3 extract_frames.py --video video.mp4 --outdir saida/ \
      [--max-frames 120] [--scene-threshold 0.1] [--interval 20] [--min-gap 2.0]

Ações muito rápidas (vários cliques em poucos segundos): reduza --min-gap
(ex.: 0.8) — é ele que separa duas mudanças de cena próximas.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PRE_OFFSET = 0.6    # s antes da mudança: tela onde a ação aconteceu
POST_OFFSET = 0.3   # s depois: resultado já renderizado
BASE_THRESHOLD = 0.03  # piso da passada única de detecção


def probe_duration(video: Path) -> float:
    """Duração em s; 0.0 = desconhecida (ex.: WebM de gravador de tela)."""
    for entries in ("format=duration", "stream=duration"):
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", entries,
             "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
            capture_output=True, text=True,
        )
        for line in proc.stdout.splitlines():
            try:
                d = float(line.strip())
                if d > 0:
                    return d
            except ValueError:
                continue
    return 0.0


def scene_candidates(video: Path) -> list:
    """Uma passada de detecção: retorna [(timestamp, score)] para todo score
    acima do piso; thresholds maiores são aplicados em memória depois."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(video),
         "-vf", f"select='gt(scene,{BASE_THRESHOLD})',metadata=print",
         "-vsync", "vfr", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print("ERRO: ffmpeg falhou na detecção de cenas — sem isso não há "
              "pares causa→efeito. Saída do ffmpeg:\n" + proc.stderr[-1500:],
              file=sys.stderr)
        sys.exit(1)
    pairs = []
    pending_t = None
    for line in proc.stderr.splitlines():
        m_t = re.search(r"pts_time:([0-9.]+)", line)
        if m_t:
            pending_t = float(m_t.group(1))
            continue
        m_s = re.search(r"lavfi\.scene_score=([0-9.]+)", line)
        if m_s and pending_t is not None:
            pairs.append((pending_t, float(m_s.group(1))))
            pending_t = None
    return pairs


def pick_threshold(cands: list, base: float, duration: float) -> float:
    """Ajusta o threshold em memória à densidade do vídeo. Sem duração
    conhecida, não há densidade confiável — mantém o threshold pedido."""
    if duration <= 0:
        return base
    thr = base
    for _ in range(3):
        n = sum(1 for _, s in cands if s > thr)
        per_min = n / max(duration / 60.0, 0.01)
        if per_min < 1.0 and thr > BASE_THRESHOLD and duration > 30:
            thr = max(BASE_THRESHOLD, round(thr / 2, 3))
        elif n > duration / 2 and thr < 0.6:
            thr = round(thr * 2, 3)
        else:
            break
    return thr


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--max-frames", type=int, default=120)
    ap.add_argument("--scene-threshold", type=float, default=0.1)
    ap.add_argument("--interval", type=float, default=20.0,
                    help="segundos entre quadros periódicos de segurança")
    ap.add_argument("--min-gap", type=float, default=2.0,
                    help="distância mínima (s) entre duas mudanças de cena; "
                    "reduza (ex.: 0.8) para capturar ações muito rápidas")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"ERRO: {tool} não encontrado — rode scripts/setup.sh antes.",
                  file=sys.stderr)
            return 1
    if args.max_frames < 4:
        print("ERRO: --max-frames deve ser >= 4 (início, fim e ao menos um "
              "par causa→efeito).", file=sys.stderr)
        return 1
    video = Path(args.video)
    if not video.exists():
        print(f"ERRO: vídeo não encontrado: {video}", file=sys.stderr)
        return 1
    frames_dir = Path(args.outdir) / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(video)
    print(f"[frames] duração do vídeo: "
          + (f"{duration:.1f}s" if duration else "desconhecida (seguindo sem poda por densidade)"))

    print(f"[frames] detectando mudanças de cena (passada única, piso {BASE_THRESHOLD})...")
    cands = scene_candidates(video)
    threshold = pick_threshold(cands, args.scene_threshold, duration)
    scenes = sorted(t for t, s in cands if s > threshold)
    print(f"[frames] {len(scenes)} mudanças de cena (threshold={threshold})")

    # dedup das cenas entre si; cada cena mantida vira um par antes/depois
    kept_scenes = []
    for t in scenes:
        if not kept_scenes or t - kept_scenes[-1] >= args.min_gap:
            kept_scenes.append(t)

    # teto respeitando PARES: reserva início+fim, reamostra cenas inteiras
    reserved = 2 if duration > 1.0 else 1
    max_pairs = max(1, (args.max_frames - reserved) // 2)
    if len(kept_scenes) > max_pairs:
        step = (len(kept_scenes) - 1) / (max_pairs - 1) if max_pairs > 1 else 0
        idx = sorted({round(i * step) for i in range(max_pairs)})
        kept_scenes = [kept_scenes[i] for i in idx]
        print(f"[frames] acima do teto — reamostrado para {len(kept_scenes)} pares (cenas inteiras)")

    events = [(0.0, "inicio")]
    for t in kept_scenes:
        pre = max(0.0, t - PRE_OFFSET)
        post = t + POST_OFFSET
        if duration > 0:
            post = min(max(0.0, duration - 0.05), post)
        events.append((pre, "antes"))
        events.append((post, "depois"))
    if duration > 1.0:
        events.append((max(0.0, duration - 0.5), "fim"))

    # periódicos só onde não há quadro de evento por perto e se sobrar teto
    if duration > 0:
        for i in range(int(duration / args.interval) + 1):
            t = i * args.interval
            if (t < duration and len(events) < args.max_frames
                    and all(abs(t - e[0]) >= args.min_gap for e in events)):
                events.append((t, "periodico"))
    events.sort(key=lambda e: e[0])

    index = []
    for i, (t, role) in enumerate(events, start=1):
        name = f"frame_{i:04d}_t{t:07.1f}s_{role}.jpg"
        out = frames_dir / name
        proc = subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{max(0.0, t):.2f}", "-i", str(video),
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
