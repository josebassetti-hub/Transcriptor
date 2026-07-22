# Kit de teste — transcrição da record-skill

Testa ponta a ponta a transcrição da skill `record-skill`
(branch `claude/record-skill-video-learning-n65ef2`).

- `narracao.txt` — roteiro da narração em PT-BR.
- `video_teste.mp4` — vídeo de 33 s com a narração sintetizada (espeak-ng).
- `rodar_teste.sh` — busca a skill, roda o setup, transcreve o vídeo e
  confere se as palavras-chave da narração aparecem no resultado.

Pré-requisito: política de rede do ambiente com os domínios
`huggingface.co`, `*.huggingface.co` e `*.hf.co` liberados
(nível **Custom**, mantendo a lista padrão de gerenciadores de pacote).

Uso:
```bash
bash teste-transcricao/rodar_teste.sh          # modelo small (padrão da skill)
bash teste-transcricao/rodar_teste.sh tiny     # mais rápido, só p/ validar rede
```

Status do último teste (22/07/2026, sessão claude/session-h7d2wk):
setup.sh OK (ffmpeg, faster-whisper, tesseract+por), extração de áudio OK,
falha controlada no download do modelo (rede bloqueada — exit 2, como
documentado no SKILL.md).
