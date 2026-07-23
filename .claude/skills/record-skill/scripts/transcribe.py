#!/usr/bin/env python3
"""Transcreve a narração de um vídeo com timestamps por segmento E por palavra.

Extrai o áudio com ffmpeg (wav 16 kHz mono) e transcreve com faster-whisper.
Gera no diretório de saída (gravando INCREMENTALMENTE — um processo morto no
meio preserva o que já foi transcrito):
  - transcript.json : [{"start", "end", "text", "words": [{"w","s","e"}]}]
  - transcript.txt  : versão legível "[MM:SS - MM:SS] texto"

Uso:
  python3 transcribe.py --video video.mp4 --outdir saida/ \
      [--model large-v3-turbo] [--language pt|auto] \
      [--initial-prompt "Sistema Protheus, SEFAZ, DANFE"]

--model: nome (tiny/base/small/medium/large-v3-turbo...) baixado do Hugging
  Face, OU caminho de um diretório com um modelo CTranslate2 (modo offline).
  Sem --model explícito, um modelo colocado em scripts/models/ é usado
  automaticamente.
--language auto: detecta o idioma automaticamente (informa a confiança).
--initial-prompt: vocabulário de domínio (nomes de sistemas, siglas).

ATENÇÃO (para quem chama): transcrição demora (~45-90 min por hora de vídeo
com o padrão large-v3-turbo em CPU) — rode em background ou com timeout
estendido, nunca com o timeout padrão de 2 min.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

FLUSH_EVERY = 10  # grava o JSON a cada N segmentos


def fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def resolve_model(model_arg: str, explicit: bool) -> str:
    """Resolve nome/caminho do modelo. Um modelo local em scripts/models/ é
    usado quando o usuário não pediu outro nome explicitamente (ou quando o
    nome pedido casa com ele)."""
    p = Path(model_arg)
    if ("/" in model_arg or p.is_absolute()) and p.is_dir():
        if not (p / "model.bin").exists():
            print(f"ERRO: {p} não parece um modelo CTranslate2 completo "
                  "(falta model.bin) — o upload pode ter vindo incompleto; "
                  "reenvie a pasta inteira do modelo.", file=sys.stderr)
            sys.exit(1)
        return str(p)

    local_dir = Path(__file__).resolve().parent / "models"
    local_models = sorted(
        d for d in (local_dir.iterdir() if local_dir.is_dir() else [])
        if (d / "model.bin").exists()
    )
    matching = [d for d in local_models if model_arg in d.name]
    if matching:
        print(f"[transcribe] usando modelo local: {matching[0]}")
        return str(matching[0])
    if local_models and not explicit:
        print(f"[transcribe] usando modelo local: {local_models[0]}")
        return str(local_models[0])
    if local_models and explicit:
        print(f"[transcribe] AVISO: há modelo local ({local_models[0].name}) "
              f"mas você pediu '{model_arg}' — tentando baixar '{model_arg}' "
              "do Hugging Face; use --model <caminho> para forçar o local.")
    return model_arg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True, help="caminho do arquivo de vídeo")
    ap.add_argument("--outdir", required=True, help="diretório de saída")
    ap.add_argument("--model", default=None,
                    help="modelo Whisper (tiny/base/small/medium/large-v3-turbo) "
                    "ou caminho de modelo local (default: large-v3-turbo, ou modelo em scripts/models/)")
    ap.add_argument("--language", default="pt",
                    help="idioma da narração, ou 'auto' para detectar")
    ap.add_argument("--initial-prompt", default=None,
                    help="vocabulário de domínio: nomes de sistemas, siglas, termos técnicos")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ERRO: ffmpeg não encontrado — rode scripts/setup.sh antes.", file=sys.stderr)
        return 1
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

    model_ref = resolve_model(args.model or "large-v3-turbo", explicit=args.model is not None)
    language = None if args.language == "auto" else args.language
    print(f"[transcribe] transcrevendo com faster-whisper "
          f"({model_ref}, idioma={'auto' if language is None else language})...")
    from faster_whisper import WhisperModel

    try:
        model = WhisperModel(model_ref, device="cpu", compute_type="int8")
    except Exception as exc:  # noqa: BLE001 - diagnóstico legível
        msg = f"{type(exc).__name__}: {exc}"
        if "403" in msg or "Proxy" in msg or "Connection" in msg or "Name or service" in msg:
            print(
                "ERRO: não consegui baixar o modelo Whisper do Hugging Face.\n"
                "A rede deste ambiente provavelmente bloqueia huggingface.co /\n"
                "cdn-lfs.huggingface.co. Opções: liberar esses domínios na\n"
                "política de rede do ambiente, OU usar o modo offline descrito\n"
                "no SKILL.md (colocar um modelo baixado em scripts/models/).\n"
                "Detalhe técnico: " + msg,
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

    json_path = outdir / "transcript.json"
    txt_path = outdir / "transcript.txt"
    out = []
    with txt_path.open("w", encoding="utf-8") as txt:
        for seg in segments:
            text = seg.text.strip()
            if not text:
                continue
            words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
                     for w in (seg.words or [])]
            out.append({"start": round(seg.start, 2), "end": round(seg.end, 2),
                        "text": text, "words": words})
            line = f"[{fmt(seg.start)} - {fmt(seg.end)}] {text}"
            txt.write(line + "\n")
            txt.flush()
            print(line)
            if len(out) % FLUSH_EVERY == 0:
                json_path.write_text(
                    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    wav.unlink(missing_ok=True)

    if not out:
        print("[transcribe] AVISO: o áudio existe mas nenhuma fala foi detectada "
              "(pode ser só música/ruído). Confirme com o usuário — o aprendizado "
              "seguirá apenas pelas telas.", file=sys.stderr)
        txt_path.write_text("(áudio sem fala detectável)\n", encoding="utf-8")

    dur = getattr(info, "duration", 0.0) or 0.0
    print(f"[transcribe] {len(out)} segmentos, duração {fmt(dur)} -> {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
