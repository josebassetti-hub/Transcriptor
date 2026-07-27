---
name: record-skill
description: Aprende um procedimento de trabalho assistindo a um vídeo gravado (tela + narração) e/ou lendo manuais, e gera um SOP e uma nova skill reutilizável no formato Agent Skills — a versão para material pré-gravado do "Record a Skill" do Claude Cowork. Use sempre que o usuário enviar ou apontar um vídeo (mp4, mkv, webm, mov, avi) e pedir para "assistir", "aprender com o vídeo", "criar uma skill a partir do vídeo", mencionar "record skill", gravação de tela, videoaula ou tutorial, ou disser que o vídeo ensina a mexer em um sistema/programa — mesmo sem a palavra "skill". Dispare também para manuais ("aprenda esse manual", "crie uma skill desse PDF", apostila, documentação — sozinhos ou complementando um vídeo), material no Google Drive, e cursos com várias aulas/módulos/playlist ("aprenda esse curso", "continue o curso") — há modos curso e manual com memória acumulada por ferramenta.
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

### 1. Obter o material (vídeo e/ou manual)

- **Arquivo na conversa**: use o caminho local informado.
- **Google Drive**: localize com as ferramentas MCP do Drive (busque pelo nome
  se o usuário não der o ID) e baixe para o scratchpad. Atenção: ferramentas
  MCP retornam o conteúdo na resposta — para vídeos grandes (centenas de MB)
  isso pode falhar; nesse caso peça ao usuário um link de download direto ou
  upload na conversa.
- **Link de YouTube/streaming ou vídeo com DRM**: não há como baixar/decodificar —
  peça ao usuário o arquivo exportado (nunca tente burlar proteções).
- **Manual/documento (PDF, DOCX, prints)**: também é material de aprendizado —
  sozinho ou complementando o vídeo; leia `references/modo-manual.md`.
- Confirme com `ffprobe` que o vídeo é válido e anote a duração. Casos
  especiais: **vídeo sem áudio** → aprenda só de tela+OCR e peça ao usuário
  narração ou manual complementar; **arquivo só de áudio** (mp3/m4a) → pule a
  extração de quadros e aprenda só da fala.

### 2. Preparar o ambiente

Execute `scripts/setup.sh` (instala ffmpeg, faster-whisper e tesseract com
português, apenas o que faltar; nunca trava pedindo senha de sudo). Se falhar
por falta de rede ou permissão, avise o usuário e pare — não há como
transcrever sem as ferramentas.

Requisitos de rede: apt/PyPI para instalar as ferramentas, e
**huggingface.co + cdn-lfs.huggingface.co** para o download do modelo Whisper
na primeira transcrição (depois fica em cache). Em ambientes com política de
rede restritiva, esses domínios precisam estar na lista de permitidos —
`transcribe.py` acusa isso com mensagem clara (código de saída 2).

Bloqueado e sem como liberar? Use o **modo offline**: o usuário baixa o
modelo uma única vez em um computador com internet (site huggingface.co) e
envia a pasta para a sessão (upload ou Google Drive). Download:
**`deepdml/faster-whisper-large-v3-turbo-ct2`** (~1,6 GB — precisão de
modelo grande com velocidade de medium; o modelo padrão desta skill, usado
para qualquer duração de vídeo). Coloque a pasta em
`scripts/models/` — o `transcribe.py` a detecta e usa automaticamente,
qualquer que seja o nome — ou passe `--model /caminho/da/pasta`. A partir daí
a transcrição funciona sem rede. Modelos maiores transcrevem mais devagar
(minutos a mais por vídeo), mas erram muito menos nomes, números e termos
técnicos — o que melhora diretamente a skill gerada.

### 3. Ouvir e ver (podem rodar em paralelo)

Antes de rodar, pergunte ao usuário (ou extraia da conversa) os **nomes dos
sistemas/termos técnicos** que aparecem no vídeo — eles entram no
`--initial-prompt` e evitam que o Whisper erre nomes próprios e siglas.

```bash
# caminhos a partir do diretório DESTA skill (.claude/skills/record-skill/)
python3 <skill>/scripts/transcribe.py --video <video> --outdir <workdir> \
    --initial-prompt "<nomes de sistemas, siglas, termos do domínio>"
python3 <skill>/scripts/extract_frames.py --video <video> --outdir <workdir>
python3 <skill>/scripts/ocr_frames.py --outdir <workdir>   # depois do extract_frames
python3 <skill>/scripts/extract_actions.py --video <video> --outdir <workdir>  # mouse/cliques/digitação
```

**Importante — tempo de execução**: transcrição leva ~45–90 min por hora de
vídeo com o `large-v3-turbo` (o modelo padrão — **use-o sempre, mesmo em
vídeos longos**: decisão do usuário, precisão acima de velocidade; apenas
avise a estimativa de tempo antes de começar), e a extração de quadros
decodifica o vídeo inteiro. **Rode os dois em background** (`run_in_background`
do Bash) e aguarde a notificação de conclusão — o timeout padrão de 2 min
mataria o processo. O mesmo vale para o primeiro download do modelo (em
sessões remotas novas o modelo é baixado de novo — minutos; com rede
bloqueada, use o modo offline). O transcript é gravado incrementalmente: se
algo morrer no meio, o parcial sobrevive.

- `transcribe.py` gera `transcript.json` (segmentos com texto E timestamps
  por palavra — use as palavras para casar a fala com o quadro exato) e
  `transcript.txt`. Padrões: modelo `large-v3-turbo` (o mais preciso para
  PT) e idioma `pt`; use `--language auto` quando não souber o idioma (o
  script informa a detecção e a confiança). Não troque de modelo por conta
  própria — o `large-v3-turbo` é a regra para qualquer duração de vídeo.
- `extract_frames.py` gera `frames/frame_NNNN_t<segundos>s_<papel>.jpg` e o
  índice `frames/frames_index.json`. Cada mudança de cena vira um **par
  causa→efeito**: quadro `antes` (a tela em que a ação foi feita) e `depois`
  (o resultado) — é assim que se enxerga o clique sem ter os eventos de
  mouse. O threshold de cena se ajusta sozinho à densidade do vídeo; para
  ações muito rápidas (vários cliques em poucos segundos), reduza
  `--min-gap 0.8` — é o dedup de cenas próximas que as separa.
- `ocr_frames.py` gera `frames_text.json` com o texto visível de cada quadro
  (OCR) — use como índice pesquisável para menus/campos pequenos; ele
  complementa, não substitui, a leitura visual dos quadros.
- `extract_actions.py` gera `actions.json` + `actions.txt` — a telemetria
  reconstruída dos pixels: trajetória do cursor, **cliques** (instante e
  posição), **digitação** (texto, início/fim, cadência) e colagens. Use para
  dar precisão operacional ao SOP ("clique em X às 00:41, digite Y no campo
  Z") e para desambiguar quando a narração diz "clique aqui". Ações com
  `confianca < 0.5` são hipótese — confirme no quadro correspondente antes de
  afirmar no SOP. Requer opencv (o setup instala); vídeos < 720p ou com
  cursor fora do padrão reduzem a taxa de acerto — nesses casos o fluxo
  antigo (pares antes→depois) continua sendo a fonte da verdade.

### 4. Assistir (correlacionar tela ↔ fala)

1. Leia `transcript.txt` inteiro primeiro para entender o arco geral: qual
   serviço está sendo ensinado, quais programas aparecem, onde começa e
   termina cada tarefa. **Antes de assistir**, verifique se já existe
   conhecimento acumulado dos programas envolvidos em
   `aprendizados/ferramentas/` (na raiz do projeto) e leia-o — o Claude
   assiste o vídeo já "conhecendo" a planilha/sistema.
2. Leia os quadros com a ferramenta Read em lotes de ~10, **em ordem
   cronológica**. O timestamp no nome diz qual trecho da narração acompanha
   aquela tela; leia os pares `antes`/`depois` juntos para entender cada ação
   (o que estava na tela → o que a ação produziu) e consulte
   `frames_text.json` quando um texto estiver pequeno demais no JPEG.
3. Para cada quadro, anote em um arquivo de notas: programa/site visível,
   tela/menu aberto, campos e valores preenchidos, qual ação acabou de
   acontecer, e o que o instrutor estava dizendo naquele momento — em especial
   critérios de decisão ("se aparecer X, faça Y"), regras de nomenclatura,
   conferências visuais e os *porquês* narrados. Essas decisões implícitas são
   o conhecimento mais valioso do vídeo.
4. Vídeos longos (>15 min): processe por segmentos de ~10 min. Se o contexto
   ficar pesado, delegue cada segmento a um subagente que recebe o transcript
   do trecho + os quadros do trecho e devolve as notas estruturadas.

### 4b. Pesquisar normas citadas

Se o instrutor citar lei, decreto, resolução, portaria, instrução normativa,
NBR ou qualquer documento oficial (na fala OU visível na tela/OCR), **leia
`references/pesquisa-normativa.md` e siga o protocolo**: identificar a
citação, pesquisar com WebSearch, validar que a fonte é oficial (planalto,
in.gov.br, site do órgão em gov.br...), confirmar que é o documento certo,
baixar com WebFetch e destilar o extrato relevante para o aprendizado.

O motivo: o instrutor resume; o texto oficial detalha. Uma skill que cita "o
art. 75, I, da Lei 14.133/2021" com o extrato anexo é muito mais confiável do
que uma que repete o resumo falado. Normas pagas, bloqueadas pela rede ou
internas da empresa não são contornadas — viram pendências apresentadas na
revisão (o protocolo detalha os fallbacks).

### 5. Sintetizar

Reconstrua o procedimento como uma sequência de ações intencionais. Regras:

- Cada passo descreve **objetivo + onde + como + por quê** (quando narrado).
- **Nunca invente passos não mostrados.** Se o áudio estiver inaudível, uma
  tela cortada, ou um trecho pular etapas, registre como lacuna — não
  preencha com suposição.
- Nomeie programas, menus e campos pelos nomes visíveis na tela.
- **Correções do instrutor**: se ele erra e corrige ("ops, na verdade é
  assim", desfaz algo, refaz um passo), a skill aprende o **caminho
  corrigido** — e o erro vira um aviso útil ("cuidado: X parece certo mas
  causa Y"). Nunca documente o passo errado como se fosse o fluxo.
- **Skill já existente para o mesmo procedimento?** Verifique
  `.claude/skills/` antes de criar. Se o novo vídeo ensina o mesmo
  procedimento, é uma **atualização**: preserve o nome da skill, mescle o
  conteúdo novo e apresente ao usuário o que mudou em vez de um rascunho do
  zero.

Produza (todos os artefatos de `aprendizados/` ficam na **raiz do projeto**,
que persiste entre sessões — nunca no scratchpad, que é apagado):

- **SOP** em `aprendizados/<nome-do-video>/SOP.md` seguindo o modelo abaixo, e
  copie os quadros-chave (um por passo importante) para
  `aprendizados/<nome-do-video>/telas/`.
- **Conhecimento da ferramenta**: para cada programa/planilha/sistema que o
  material ensina, crie ou ATUALIZE `aprendizados/ferramentas/<programa>.md`
  com o que este material acrescentou — telas e menus mapeados, campos e
  variáveis (e o que significam), funções e recursos, macetes, mudanças de
  interface observadas, e a lista de serviços que já se sabe executar nele
  (com as skills correspondentes). É esse acúmulo que faz um novo serviço na
  MESMA ferramenta nascer sabendo tudo que os materiais anteriores ensinaram;
  a parte relevante entra nas `references/` da skill gerada.
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

## Base normativa
| Norma | O que o instrutor disse | O que o texto oficial detalha | Fonte oficial | Arquivo |
|---|---|---|---|---|
[uma linha por norma citada; divergências fala×texto destacadas]

## Lacunas e dúvidas
[o que o vídeo não mostrou ou ficou ambíguo, incluindo normas não resolvidas]
```

### 6. Revisar com o usuário (obrigatório)

Como o Record a Skill oficial, **não finalize sem revisão**: apresente ao
usuário um resumo do que foi aprendido, o rascunho da nova skill e a lista de
lacunas/ambiguidades, e pergunte o que ajustar antes de gravar a versão
final. As respostas do usuário resolvem as lacunas — incorpore-as.

Inclua na revisão o resultado da pesquisa normativa (etapa 4b): normas
encontradas e incorporadas com suas fontes, divergências entre o que foi
falado e o texto oficial, e citações pendentes (ambíguas, pagas, bloqueadas
ou internas) que dependem de resposta ou documento do usuário.

### 7. Validar em um exemplo novo

Como no Record a Skill oficial, teste a skill gerada **em um exemplo novo**,
não em recontar o próprio vídeo: rode 1–2 prompts de teste realistas com
dados diferentes dos usados na demonstração (outro cliente, outro valor,
outro arquivo) em um subagente com acesso à skill, e confira se ela guia a
tarefa corretamente. Ajuste o que falhar.

Sem subagentes no ambiente, ou com a skill recém-criada ainda não carregada
na sessão: valide **inline** — leia o SKILL.md gerado como se fosse sua única
fonte e execute o prompt de teste passo a passo seguindo apenas o que está
escrito nele; onde você precisar de algo que não está lá, a skill está
incompleta.

### 8. Entregar e limpar

- **Entregar**: resumo do procedimento aprendido, caminho do SOP, nome da
  nova skill e frases que a disparam, e lacunas que permaneceram abertas.
  Se a ferramenta SendUserFile estiver disponível, empacote a skill
  (`python -m scripts.package_skill` do skill-creator, se instalado, ou um
  zip da pasta renomeado para `.skill`) e envie — o cartão mostra o botão
  "Save skill", que instala a skill na biblioteca pessoal do usuário, como o
  Record a Skill oficial faz.
- **Limpar (privacidade)**: a gravação captura tudo que estava na tela —
  possivelmente dados de clientes, números de conta, nomes. Após a síntese,
  apague do scratchpad o vídeo baixado, o áudio e os quadros não citados no
  SOP; mantenha apenas as telas referenciadas. Se alguma tela mantida exibir
  dado sensível, avise o usuário explicitamente.

## Manuais e documentos

Se o material incluir (ou for apenas) um manual, apostila, PDF, DOCX ou
prints de tela, **leia `references/modo-manual.md`**: ele cobre aprender só
do documento (com a marcação honesta "não demonstrado em tela"), usar o
manual como complemento oficial do vídeo (cruzamento passo a passo, como na
pesquisa normativa) e a integração com o modo curso e com o conhecimento por
ferramenta.

## Cursos completos e vídeos longos

Se o material for um curso/treinamento com várias aulas (ou o usuário disser
"curso", "aulas", "módulos", "playlist"), **leia
`references/modo-curso.md` e siga aquele protocolo** em vez do fluxo de vídeo
único: inventário com ordem confirmada, um vídeo por vez com limpeza de
disco, memória acumulada do curso, detecção de continuidade entre aulas,
checkpoint com commit por módulo (retomável entre sessões via
`progresso.json`) e consolidação final em uma skill (ou família de skills +
skill mestre). Vídeos com mais de ~1 h: divida sem reencodar com
`ffmpeg -c copy -f segment` (comando no protocolo) — o usuário não precisa
recortar nada.

## Qualidade do vídeo de entrada

A qualidade do vídeo determina a qualidade da skill gerada. Se o resultado
vier fraco (narração ausente, tela ilegível, várias tarefas misturadas),
compartilhe com o usuário o guia `references/como-gravar-um-bom-video.md` e
sugira regravar seguindo-o.
