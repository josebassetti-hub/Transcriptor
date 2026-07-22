#!/usr/bin/env python3
"""Transcreve a narração de um vídeo com timestamps.

Extrai o áudio com ffmpeg (wav 16 kHz mono) e transcreve com faster-whisper.
Gera no diretório de saída:
  - transcript.json : [{"start": s, "end": s, "text": "..."}, ...]
  - transcript.txt  : versão legível "[MM:SS - MM:SS] texto"

Uso:
  python3 transcribe.py --video video.mp4 --outdir saida/ [--model small] [--language pt]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True, help="caminho do arquivo de vídeo")
    ap.add_argument("--outdir", required=True, help="diretório de saída")
    ap.add_argument("--model", default="small", help="modelo Whisper (tiny/base/small/medium)")
    ap.add_argument("--language", default="pt", help="idioma da narração")
    args = ap.parse_args()

    video = Path(args.video)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if not video.exists():
        print(f"ERRO: vídeo não encontrado: {video}", file=sys.stderr)
        return 1

    wav = outdir / "audio.wav"
    print(f"[transcribe] extraindo áudio de {video.name}...")
    proc = subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "pcm_s16le", str(wav)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        if "does not contain any stream" in proc.stderr or "Output file does not contain" in proc.stderr:
            print("[transcribe] o vídeo não tem trilha de áudio — gerando transcript vazio.")
            (outdir / "transcript.json").write_text("[]", encoding="utf-8")
            (outdir / "transcript.txt").write_text("(vídeo sem áudio)\n", encoding="utf-8")
            return 0
        print(proc.stderr[-2000:], file=sys.stderr)
        return 1

    print(f"[transcribe] transcrevendo com faster-whisper ({args.model}, {args.language})...")
    from faster_whisper import WhisperModel

    try:
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
    except Exception as exc:  # noqa: BLE001 - diagnóstico de rede legível
        msg = f"{type(exc).__name__}: {exc}"
        if "403" in msg or "Proxy" in msg or "Connection" in msg or "Name or service" in msg:
            print(
                "ERRO: não consegui baixar o modelo Whisper do Hugging Face.\n"
                "A política de rede deste ambiente provavelmente bloqueia o site.\n"
                "Libere os domínios huggingface.co e cdn-lfs.huggingface.co na\n"
                "configuração de rede do ambiente (Claude Code web -> Environments)\n"
                "e rode novamente. Detalhe técnico: " + msg,
                file=sys.stderr,
            )
            return 2
        raise
    segments, info = model.transcribe(
        str(wav), language=args.language, vad_filter=True, beam_size=5,
    )

    out = []
    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        out.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": text})
        lines.append(f"[{fmt(seg.start)} - {fmt(seg.end)}] {text}")
        print(lines[-1])

    (outdir / "transcript.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    wav.unlink(missing_ok=True)

    dur = getattr(info, "duration", 0.0) or 0.0
    print(f"[transcribe] {len(out)} segmentos, duração {fmt(dur)} -> {outdir}/transcript.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
