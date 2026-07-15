#!/usr/bin/env bash
# Converte pranchas HTML em PDF A4 e, opcionalmente, junta tudo num caderno.
#
# Uso:
#   ./gerar_pdf.sh prancha1.html prancha2.html ...            # gera um .pdf ao lado de cada .html
#   ./gerar_pdf.sh -o caderno.pdf capa.html prancha1.html ... # gera os PDFs e junta em caderno.pdf
#
# Requisitos: Chromium (pré-instalado em /opt/pw-browsers/chromium) e poppler (pdfunite).
set -euo pipefail

CHROMIUM="${CHROMIUM:-/opt/pw-browsers/chromium}"
if [[ ! -x "$CHROMIUM" ]]; then
  CHROMIUM="$(command -v chromium || command -v chromium-browser || command -v google-chrome)" \
    || { echo "chromium não encontrado" >&2; exit 1; }
fi

CADERNO=""
if [[ "${1:-}" == "-o" ]]; then
  CADERNO="$2"; shift 2
fi

PDFS=()
for HTML in "$@"; do
  [[ -f "$HTML" ]] || { echo "não existe: $HTML" >&2; exit 1; }
  PDF="${HTML%.html}.pdf"
  "$CHROMIUM" --headless --no-sandbox --disable-gpu \
    --no-pdf-header-footer --print-to-pdf="$PDF" \
    "file://$(readlink -f "$HTML")" 2>/dev/null
  echo "gerado: $PDF"
  PDFS+=("$PDF")
done

if [[ -n "$CADERNO" && ${#PDFS[@]} -gt 0 ]]; then
  pdfunite "${PDFS[@]}" "$CADERNO"
  echo "caderno: $CADERNO ($(pdfinfo "$CADERNO" | awk '/^Pages/{print $2}') páginas)"
fi
