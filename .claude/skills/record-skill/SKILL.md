---
name: record-skill
description: Aprende um procedimento de trabalho assistindo a um vídeo já gravado (tela + narração em áudio) e gera um SOP passo a passo e uma nova skill reutilizável no formato Agent Skills — a versão para vídeos pré-gravados do "Record a Skill" oficial do Claude Cowork. Use sempre que o usuário enviar ou apontar um arquivo de vídeo (mp4, mkv, webm, mov, avi) e pedir para "assistir", "aprender com o vídeo", "ver o treinamento", "criar uma skill a partir do vídeo", mencionar "record skill", gravação de tela, videoaula, tutorial gravado, ou disser que o vídeo ensina a mexer em um sistema/programa/serviço — mesmo que não use a palavra "skill". Também dispare quando o vídeo estiver no Google Drive e o usuário pedir para aprender o que é ensinado nele.
---

# Record Skill — aprender procedimentos a partir de vídeos gravados

Esta skill replica, para vídeos já gravados, o que o Record a Skill oficial do
Cowork faz com gravações ao vivo: assistir a demonstração (tela + voz),
entender a **intenção semântica** do fluxo de trabalho, e sintetizar o
conhecimento em artefatos reutilizáveis. O produto final são duas coisas:

1. **SOP** (`aprendizados/<nome-do-video>/SOP.md`) — o procedimento passo a
   passo documentado, com capturas de tela e citações da narração.
2. **Nova skill** (`.claude/skills/<nome-do-procedimento>/`) — o procedimento
   destilado em uma skill padrão Agent Skills, invocável em conversas futuras.

O princípio central, herdado do recurso oficial: extrair **o que a pessoa está
tentando fazer e por quê** — não uma repetição literal de cliques. Uma skill
que diz "no sistema X, abra o cadastro do cliente e preencha o CNPJ antes de
emitir, porque o sistema bloqueia emissão sem CNPJ" sobrevive a mudanças de
interface; uma que diz "clique no terceiro botão azul" não.

## Fluxo de trabalho

Siga as etapas na ordem. Use o scratchpad da sessão como área de trabalho
(`<scratchpad>/record-skill/<nome-do-video>/`).

### 1. Obter o vídeo

- **Arquivo na conversa**: use o caminho local informado.
- **Google Drive**: localize com as ferramentas MCP do Drive (busque pelo nome
  se o usuário não der o ID) e baixe para o scratchpad.
- Confirme com `ffprobe` que o arquivo é um vídeo válido e anote a duração.

### 2. Preparar o ambiente

Execute `scripts/setup.sh` (instala ffmpeg e faster-whisper apenas se
faltarem). Se falhar por falta de rede, avise o usuário e pare — não há como
transcrever sem as ferramentas.

Requisitos de rede: apt/PyPI para instalar as ferramentas, e
**huggingface.co + cdn-lfs.huggingface.co** para o download do modelo Whisper
na primeira transcrição (depois fica em cache). Em ambientes com política de
rede restritiva, esses domínios precisam estar na lista de permitidos —
`transcribe.py` acusa isso com mensagem clara (código de saída 2); nesse caso
peça ao usuário para liberar os domínios na configuração do ambiente.

### 3. Ouvir e ver (podem rodar em paralelo)

```bash
python3 scripts/transcribe.py --video <video> --outdir <workdir>
python3 scripts/extract_frames.py --video <video> --outdir <workdir>
```

- `transcribe.py` gera `transcript.json` (segmentos com start/end/texto) e
  `transcript.txt`. Padrões: modelo `small`, idioma `pt` — ajuste `--language`
  se a narração não for em português; use `--model medium` se a transcrição
  vier ruim e o vídeo for importante.
- `extract_frames.py` gera `frames/frame_NNNN_t<segundos>s.jpg` +
  `frames_index.json`, combinando mudanças de cena (o efeito de cada ação na
  tela) com amostragem periódica. Para vídeos com muitas ações rápidas,
  aumente a cobertura com `--max-frames 150 --interval 10`.

### 4. Assistir (correlacionar tela ↔ fala)

1. Leia `transcript.txt` inteiro primeiro para entender o arco geral: qual
   serviço está sendo ensinado, quais programas aparecem, onde começa e
   termina cada tarefa.
2. Leia os quadros com a ferramenta Read em lotes de ~10, **em ordem
   cronológica**. O timestamp no nome do arquivo diz qual trecho da narração
   acompanha aquela tela.
3. Para cada quadro, anote em um arquivo de notas: programa/site visível,
   tela/menu aberto, campos e valores preenchidos, qual ação acabou de
   acontecer, e o que o instrutor estava dizendo naquele momento — em especial
   critérios de decisão ("se aparecer X, faça Y"), regras de nomenclatura,
   conferências visuais e os *porquês* narrados. Essas decisões implícitas são
   o conhecimento mais valioso do vídeo.
4. Vídeos longos (>15 min): processe por segmentos de ~10 min. Se o contexto
   ficar pesado, delegue cada segmento a um subagente que recebe o transcript
   do trecho + os quadros do trecho e devolve as notas estruturadas.

### 5. Sintetizar

Reconstrua o procedimento como uma sequência de ações intencionais. Regras:

- Cada passo descreve **objetivo + onde + como + por quê** (quando narrado).
- **Nunca invente passos não mostrados.** Se o áudio estiver inaudível, uma
  tela cortada, ou um trecho pular etapas, registre como lacuna — não
  preencha com suposição.
- Nomeie programas, menus e campos pelos nomes visíveis na tela.

Produza:

- **SOP** em `aprendizados/<nome-do-video>/SOP.md` seguindo o modelo abaixo, e
  copie os quadros-chave (um por passo importante) para
  `aprendizados/<nome-do-video>/telas/`.
- **Rascunho da nova skill** em `.claude/skills/<nome-do-procedimento>/`
  seguindo `references/skill-authoring.md` (leia antes de escrever). A skill
  não é uma cópia do SOP: é o procedimento destilado em instruções acionáveis
  para o Claude executar ou guiar alguém pela tarefa. Inclua prints em
  `references/` da nova skill apenas se uma tela for difícil de descrever.

Modelo do SOP:

```markdown
# SOP — [nome do procedimento]
Fonte: [arquivo do vídeo], [duração], transcrito em [data]

## Visão geral
[O que o procedimento realiza, em que sistema(s), quando é usado]

## Programas e acessos necessários
[lista com o que aparece no vídeo]

## Passo a passo
### 1. [objetivo do passo]
- Onde: [programa > tela > menu]
- Como: [ações]
- Por quê / critério: "[citação da narração]" (t=MM:SS)
- Tela: telas/frame_XXXX.jpg

## Decisões e regras narradas
[condições, exceções, conferências que o instrutor menciona]

## Lacunas e dúvidas
[o que o vídeo não mostrou ou ficou ambíguo]
```

### 6. Revisar com o usuário (obrigatório)

Como o Record a Skill oficial, **não finalize sem revisão**: apresente ao
usuário um resumo do que foi aprendido, o rascunho da nova skill e a lista de
lacunas/ambiguidades, e pergunte o que ajustar antes de gravar a versão
final. As respostas do usuário resolvem as lacunas — incorpore-as.

### 7. Validar

Rode 1–2 prompts de teste realistas (o tipo de pedido que dispararia a nova
skill) em um subagente com acesso à skill gerada e confira se ela guia a
tarefa corretamente. Ajuste o que falhar.

### 8. Relatar

Entregue ao usuário: resumo do procedimento aprendido, caminho do SOP, nome
da nova skill e exemplos de frases que a disparam, e lacunas que permaneceram
abertas.

## Qualidade do vídeo de entrada

A qualidade do vídeo determina a qualidade da skill gerada. Se o resultado
vier fraco (narração ausente, tela ilegível, várias tarefas misturadas),
compartilhe com o usuário o guia `references/como-gravar-um-bom-video.md` e
sugira regravar seguindo-o.
