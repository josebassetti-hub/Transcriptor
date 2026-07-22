#!/usr/bin/env bash
# Prepara o ambiente para a skill record-skill: ffmpeg (extração de áudio e
# quadros) e faster-whisper (transcrição local da narração). Idempotente —
# só instala o que estiver faltando.
set -uo pipefail

ok=1

if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  echo "[setup] ffmpeg já instalado: $(ffmpeg -version | head -1)"
else
  echo "[setup] instalando ffmpeg via apt..."
  if command -v sudo >/dev/null 2>&1 && [ "$(id -u)" != "0" ]; then APT="sudo apt-get"; else APT="apt-get"; fi
  $APT update -qq && $APT install -y -qq ffmpeg
  if command -v ffmpeg >/dev/null 2>&1; then
    echo "[setup] ffmpeg instalado: $(ffmpeg -version | head -1)"
  else
    echo "[setup] ERRO: não consegui instalar o ffmpeg (sem rede ou sem permissão apt)." >&2
    ok=0
  fi
fi

if python3 -c "import faster_whisper" >/dev/null 2>&1; then
  echo "[setup] faster-whisper já instalado."
else
  echo "[setup] instalando faster-whisper via pip..."
  pip3 install --quiet faster-whisper
  if python3 -c "import faster_whisper" >/dev/null 2>&1; then
    echo "[setup] faster-whisper instalado."
  else
    echo "[setup] ERRO: não consegui instalar o faster-whisper (verifique acesso ao PyPI)." >&2
    ok=0
  fi
fi

if [ "$ok" = "1" ]; then
  echo "[setup] ambiente pronto."
else
  echo "[setup] ambiente incompleto — veja os erros acima." >&2
  exit 1
fi
