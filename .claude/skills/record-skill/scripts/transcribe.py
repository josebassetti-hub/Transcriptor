#!/usr/bin/env python3
"""Transcreve a narração de um vídeo com timestamps por segmento E por palavra.

Extrai o áudio com ffmpeg (wav 16 kHz mono) e transcreve com faster-whisper.
Gera no diretório de saída:
  - transcript.json : [{"start", "end", "text", "words": [{"w","s","e"}]}]
  - transcript.txt  : versão legível "[MM:SS - MM:SS] texto"

Os timestamps por palavra permitem casar a fala com o quadro exato da tela
(pares antes/depois do extract_frames.py).

Uso:
  python3 transcribe.py --video video.mp4 --outdir saida/ \
      [--model small] [--language pt|auto] \
      [--initial-prompt "Sistema Protheus, SEFAZ, DANFE"]

--language auto: detecta o idioma automaticamente (informa a confiança).
--initial-prompt: vocabulário de domínio (nomes de sistemas, siglas) para o
  Whisper reconhecer termos que de outra forma erraria.
--model: nome do modelo (baixado do Hugging Face) OU caminho de um diretório
  com um modelo CTranslate2 já baixado (modo offline — para ambientes onde o
  Hugging Face é bloqueado). Se existir um modelo em models/ ao lado deste
  script, ele é usado automaticamente.
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
    ap.add_argument("--language", default="pt",
                    help="idioma da narração, ou 'auto' para detectar")
    ap.add_argument("--initial-prompt", default=None,
                    help="vocabulário de domínio: nomes de sistemas, siglas, termos técnicos")
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

    # modo offline: --model pode ser um diretório local com o modelo CT2; se
    # não for, procura em models/ ao lado do script antes de tentar o download
    # do Hugging Face. Um único modelo na pasta é usado independente do nome —
    # o usuário não precisa casar o nome da pasta com o --model.
    model_ref = args.model
    if not Path(model_ref).is_dir():
        local_dir = Path(__file__).resolve().parent / "models"
        local_models = sorted(
            d for d in (local_dir.iterdir() if local_dir.is_dir() else [])
            if (d / "model.bin").exists()
        )
        matching = [d for d in local_models if args.model in d.name]
        chosen = (matching or local_models)[:1]
        if len(local_models) > 1 and not matching:
            print(f"[transcribe] AVISO: vários modelos em {local_dir} e nenhum "
                  f"casa com '{args.model}' — usando {chosen[0].name}; passe "
                  f"--model <caminho> para escolher outro.")
        if chosen:
            model_ref = str(chosen[0])
            print(f"[transcribe] usando modelo local: {model_ref}")

    language = None if args.language == "auto" else args.language
    print(f"[transcribe] transcrevendo com faster-whisper "
          f"({model_ref}, idioma={'auto' if language is None else language})...")
    from faster_whisper import WhisperModel

    try:
        model = WhisperModel(model_ref, device="cpu", compute_type="int8")
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
        str(wav), language=language, vad_filter=True, beam_size=5,
        word_timestamps=True, initial_prompt=args.initial_prompt,
    )

    if language is None:
        prob = getattr(info, "language_probability", 0.0) or 0.0
        print(f"[transcribe] idioma detectado: {info.language} (confiança {prob:.0%})")
        if prob < 0.7:
            print("[transcribe] AVISO: confiança baixa na detecção — confirme o "
                  "idioma com o usuário e rode de novo com --language se preciso.")

    out = []
    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
                 for w in (seg.words or [])]
        out.append({"start": round(seg.start, 2), "end": round(seg.end, 2),
                    "text": text, "words": words})
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
