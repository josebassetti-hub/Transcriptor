#!/usr/bin/env bash
# Teste ponta a ponta da transcrição da record-skill.
# Pré-requisito: política de rede do ambiente liberando huggingface.co,
# cdn-lfs.huggingface.co e cas-bridge.xethub.hf.co (ou *.hf.co).
#
# Uso: bash teste-transcricao/rodar_teste.sh [modelo]
#   modelo: tiny/base/small/... (default: large-v3-turbo, o padrão da skill)
set -uo pipefail

MODEL="${1:-large-v3-turbo}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${TMPDIR:-/tmp}/teste-record-skill"
SKILL_BRANCH="claude/record-skill-video-learning-n65ef2"

mkdir -p "$WORK"
cd "$REPO"

echo "== [1/5] Obtendo a skill da branch $SKILL_BRANCH =="
git fetch origin "$SKILL_BRANCH" || exit 1
rm -rf "$WORK/skill" && mkdir -p "$WORK/skill-tmp"
git archive FETCH_HEAD .claude/skills/record-skill | tar -x -C "$WORK/skill-tmp"
mv "$WORK/skill-tmp/.claude/skills/record-skill" "$WORK/skill"
rm -rf "$WORK/skill-tmp"

echo "== [2/5] Checando a rede (domínios do Hugging Face) =="
net_ok=1
for d in huggingface.co cdn-lfs.huggingface.co cas-bridge.xethub.hf.co; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 15 "https://$d/" 2>/dev/null)
  echo "   $d -> HTTP ${code:-falha}"
  [ "${code:-000}" = "000" ] && net_ok=0
done
if [ "$net_ok" = "0" ]; then
  echo "AVISO: pelo menos um domínio ainda parece bloqueado — o download do"
  echo "modelo pode falhar. Seguindo mesmo assim para confirmar."
fi

echo "== [3/5] Setup da skill (ffmpeg, faster-whisper, tesseract) =="
bash "$WORK/skill/scripts/setup.sh" || exit 1

echo "== [4/5] Transcrevendo o vídeo de teste (modelo $MODEL, idioma pt) =="
echo "   (primeira execução baixa o modelo do Hugging Face — pode demorar)"
python3 "$WORK/skill/scripts/transcribe.py" \
  --video "$REPO/teste-transcricao/video_teste.mp4" \
  --outdir "$WORK/saida" \
  --model "$MODEL" --language pt \
  --initial-prompt "guia de recolhimento, CNPJ, boleto, prefeitura"
rc=$?
if [ $rc -ne 0 ]; then
  echo "FALHA: transcribe.py saiu com código $rc (2 = rede bloqueada)."
  exit $rc
fi

echo "== [5/5] Conferindo o resultado =="
echo "--- transcript.txt ---"
cat "$WORK/saida/transcript.txt"
echo "----------------------"
hits=0
for palavra in guia prefeitura Financeiro CNPJ julho boleto; do
  if grep -qi "$palavra" "$WORK/saida/transcript.txt"; then
    hits=$((hits+1))
  else
    echo "   (palavra-chave ausente: $palavra)"
  fi
done
echo "Palavras-chave reconhecidas: $hits/6"
if [ "$hits" -ge 4 ]; then
  echo "RESULTADO: TESTE APROVADO — transcrição em português funcionando."
else
  echo "RESULTADO: transcrição rodou, mas com precisão baixa ($hits/6)."
  echo "Obs.: a voz do vídeo de teste é sintética (espeak-ng), o que reduz a"
  echo "precisão; com voz humana o resultado é melhor. Tente --model small ou medium."
fi
