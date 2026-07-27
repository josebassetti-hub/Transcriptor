#!/usr/bin/env bash
# Prepara o ambiente para a skill record-skill: ffmpeg (áudio/quadros),
# faster-whisper (transcrição) e tesseract com português (OCR, opcional).
# Idempotente — só instala o que estiver faltando.
set -uo pipefail

LOG="${TMPDIR:-/tmp}/record-skill-setup.log"
: > "$LOG"
ok=1
apt_updated=0

apt_cmd() {
  # nunca trava pedindo senha: sudo só no modo não interativo (-n)
  if [ "$(id -u)" = "0" ]; then apt-get "$@"
  elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then sudo -n apt-get "$@"
  else return 127; fi
}

apt_install() {
  if [ "$apt_updated" = "0" ]; then apt_cmd update -qq >>"$LOG" 2>&1 || true; apt_updated=1; fi
  apt_cmd install -y -qq "$@" >>"$LOG" 2>&1
}

pip_install() {
  # PEP 668 (externally-managed-environment): tenta normal, depois os fallbacks
  python3 -m pip install --quiet "$@" 2>>"$LOG" \
    || python3 -m pip install --quiet --break-system-packages "$@" 2>>"$LOG" \
    || python3 -m pip install --quiet --user --break-system-packages "$@" 2>>"$LOG"
}

# --- ffmpeg -----------------------------------------------------------------
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  echo "[setup] ffmpeg já instalado: $(ffmpeg -version 2>/dev/null | head -1)"
else
  echo "[setup] instalando ffmpeg via apt..."
  if apt_install ffmpeg && command -v ffmpeg >/dev/null 2>&1; then
    echo "[setup] ffmpeg instalado."
  else
    echo "[setup] ERRO: não consegui instalar o ffmpeg (sem root/sudo sem senha," >&2
    echo "        ou sem rede). Instale manualmente e rode de novo. Log: $LOG" >&2
    ok=0
  fi
fi

# --- faster-whisper ---------------------------------------------------------
if python3 -c "import faster_whisper" >/dev/null 2>&1; then
  echo "[setup] faster-whisper já instalado."
else
  echo "[setup] instalando faster-whisper via pip..."
  if pip_install faster-whisper && python3 -c "import faster_whisper" >/dev/null 2>&1; then
    echo "[setup] faster-whisper instalado."
  else
    echo "[setup] ERRO: pip não conseguiu instalar o faster-whisper." >&2
    echo "        Causas comuns: sem acesso ao PyPI, ou Python gerenciado pelo" >&2
    echo "        sistema (PEP 668) sem permissão. Alternativa manual:" >&2
    echo "        python3 -m venv ~/.record-skill-venv && ~/.record-skill-venv/bin/pip install faster-whisper" >&2
    echo "        Log: $LOG" >&2
    ok=0
  fi
fi

# --- opencv + numpy (extração de ações: cursor/cliques/digitação) -----------
if python3 -c "import cv2, numpy" >/dev/null 2>&1; then
  echo "[setup] opencv/numpy já instalados."
else
  echo "[setup] instalando opencv-python-headless + numpy via pip..."
  if pip_install opencv-python-headless numpy && python3 -c "import cv2, numpy" >/dev/null 2>&1; then
    echo "[setup] opencv/numpy instalados."
  else
    echo "[setup] AVISO: sem opencv — extract_actions.py (mouse/cliques/digitação)" >&2
    echo "        fica indisponível; transcrição e quadros seguem normais. Log: $LOG" >&2
  fi
fi

# --- tesseract + português (OCR é opcional: falha não derruba o setup) ------
if ! command -v tesseract >/dev/null 2>&1; then
  echo "[setup] instalando tesseract (OCR, opcional)..."
  apt_install tesseract-ocr tesseract-ocr-por \
    && echo "[setup] tesseract instalado." \
    || echo "[setup] AVISO: tesseract não instalado — OCR será pulado. Log: $LOG"
fi
if command -v tesseract >/dev/null 2>&1; then
  if tesseract --list-langs 2>/dev/null | grep -qx por; then
    echo "[setup] tesseract com idioma 'por' ok."
  else
    echo "[setup] tesseract sem o idioma 'por' — instalando tesseract-ocr-por..."
    apt_install tesseract-ocr-por \
      && echo "[setup] idioma 'por' instalado." \
      || echo "[setup] AVISO: sem o idioma 'por' — o OCR usará inglês (qualidade menor em PT). Log: $LOG"
  fi
fi

if [ "$ok" = "1" ]; then
  echo "[setup] ambiente pronto."
else
  echo "[setup] ambiente incompleto — veja os erros acima." >&2
  exit 1
fi
