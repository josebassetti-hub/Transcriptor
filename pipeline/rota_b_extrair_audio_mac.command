#!/bin/bash
# ROTA B (alternativa): extrai só o ÁUDIO das aulas no seu Mac, sem instalar nada.
#
# COMO USAR (3 passos):
#   1. Coloque este arquivo na MESMA PASTA onde estão os vídeos (1.mov, 2.mov, ...)
#      no seu computador.
#   2. Clique duas vezes nele. (Se o Mac bloquear: clique com o botão direito >
#      Abrir > Abrir. Ou em Ajustes > Privacidade e Segurança > "Abrir mesmo assim".)
#   3. Ao final, suba os arquivos da pasta "audio_para_claude" para a pasta do
#      curso no seu Google Drive. São pequenos (~60 MB por hora de aula).
#
# O áudio é o que o Claude precisa para transcrever as aulas. As imagens da tela
# (frames) podem vir depois pela Rota A, ou me avise que eu adapto este script.

cd "$(dirname "$0")" || exit 1
mkdir -p audio_para_claude

total=0; ok=0
for video in *.mov *.MOV *.mp4 *.MP4; do
  [ -e "$video" ] || continue
  total=$((total+1))
  nome="${video%.*}"
  destino="audio_para_claude/${nome}.m4a"
  if [ -e "$destino" ]; then
    echo "Já existe: $destino"; ok=$((ok+1)); continue
  fi
  echo "Extraindo áudio de $video ..."
  if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -hide_banner -loglevel error -i "$video" -vn -c:a aac -b:a 64k "$destino"
  else
    # afconvert vem instalado em todo Mac
    afconvert -f m4af -d aac -b 65536 "$video" "$destino"
  fi
  if [ -s "$destino" ]; then
    echo "  OK: $destino"; ok=$((ok+1))
  else
    rm -f "$destino"
    echo "  FALHOU: $video (me mande esta mensagem de erro)"
  fi
done

echo
echo "=================================================================="
echo "Concluído: $ok de $total vídeos."
echo "Agora suba a pasta 'audio_para_claude' para o Google Drive do curso."
echo "=================================================================="
read -r -p "Pressione Enter para fechar..."
