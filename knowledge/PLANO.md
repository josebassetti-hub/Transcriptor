# Plano v2 (REVISADO): Fábrica de Projetos de Crédito Rural BNB/FNE

## Contexto

O plano v1 foi aprovado e a **Fase 0 está concluída** (scaffolding, protocolo de extração
do usuário incorporado, 7 documentos do curso extraídos, 3 commits pushed). O usuário pediu
revisão crítica passo a passo antes de executar o restante. A revisão (auditoria própria +
revisor independente que releu repo/plano/scripts) encontrou **3 defeitos concretos** e
produziu ~15 correções. Este v2 substitui o v1 como plano de execução.

## Defeitos concretos encontrados (corrigir ANTES de tudo)

1. **`.gitignore` engole as saídas da Fase 2**: o padrão `frames/` (pensado para
   `materiais/frames/`) também ignora `knowledge/frames/` — destino das tabelas-mestras.
   Verificado com `git check-ignore`. Correção: ancorar como `materiais/frames/`.
2. **CPF + nome do cliente-exemplo já estão no GitHub** (commits `40b0e24` e `c79a626`,
   em 3 arquivos knowledge/). Correção LGPD: mascarar nos arquivos e **reescrever o
   histórico da branch** (seguro: os 3 commits pós-`a6f40bf` são exclusivamente desta
   sessão) — `git reset --soft a6f40bf` → recommit com dados mascarados → push
   `--force-with-lease`. Guarda permanente: teste pytest que gréppa padrão de CPF em
   `knowledge/` (extratores de visão vão tentar reintroduzir).
3. **huggingface.co bloqueado pelo proxy (000, verificado)** — o faster-whisper baixa o
   modelo de lá na 1ª execução; a transcrição travaria. Correção: incluir os domínios do
   HF na MESMA liberação de rede da Rota A (lista única abaixo).

## O que mais a revisão mudou

| # | Problema no v1 | Correção no v2 |
|---|---|---|
| 1 | Transcrição de ~10h em job único (sessão instável perde horas) | Áudio fatiado em **blocos de ~20 min com 10s de sobreposição**; timestamps somam o offset do bloco; modelo carregado 1×; **commit por bloco**; retomável |
| 2 | Whisper `small` pode errar vocabulário técnico | `hotwords` de domínio (FNE, PRONAF, custeio, parição, garrote, adimplência, INVRUR...) + triagem automática por `avg_logprob` → re-transcrição pontual com `medium` + auditoria humana de 3 trechos |
| 3 | Ler milhares de frames com visão às cegas | Extração de frames continua na F1 (com o .mov em mãos), mas a LEITURA é dirigida: transcrição → gavetas → visão só nas janelas de procedimento; pré-filtro phash CLASSIFICA em subpastas planilha/câmera (nunca deleta; contagem registrada) |
| 4 | openpyxl sobre XLSM assumido como certo (pode corromper) | Gate na F3: dissecar `.INVRUR`/XLSM primeiro (também é pré-requisito da F4); fallback definido: roteiro de digitação célula a célula + planilha-espelho XLSX própria |
| 5 | Sem defesa contra reciclagem do container em jobs longos | `send_later` **encadeado** (~45 min; cron tem mínimo 1h) com **lock/pidfile** — cada wake: processo vivo? → commit/push parciais → relança do último bloco se morto; nunca duplica |
| 6 | Downloader manual | `gdown --continue` como principal (resiliente à página de confirmação); manual como fallback; piloto testa resume de verdade (matar no meio e retomar) |
| 7 | Fases estritamente sequenciais | **Por vídeo, ponta a ponta** (download→áudio+frames→verificar→apagar .mov→blocos+commit→classificar→visão dirigida→tabela-mestra) e, em paralelo, motores já especificados |
| 8 | Vídeos ocupando disco | Apagar .mov local só após **gate de integridade**: tamanho baixado = inventário; duração WAV = duração vídeo (ffprobe); frames > 0 |
| 9 | F2 em subagentes background (morreram 2× nesta sessão) | Orquestração **síncrona na sessão principal**; visão em lotes de ~20–50 pares com **manifesto JSONL** por vídeo (par→pendente/lido) e append+commit da tabela-mestra por lote — queda perde no máximo 1 lote; subagentes só para tarefas ≤10 min |
| 10 | Estado do pipeline implícito | `knowledge/status.json` por vídeo (baixado→áudio→frames→blocos→classificado→visão) commitado — sessão nova retoma após reciclo sem redescobrir nada |

## Fases revisadas

### Fase 0b — Correções imediatas (não dependem do usuário; fazer JÁ)
1. Corrigir `.gitignore` (`materiais/frames/` ancorado).
2. LGPD: mascarar CPF/nome nos 3 knowledge/ + reescrever histórico da branch
   (`reset --soft a6f40bf` → recommit → `push --force-with-lease`) + teste-guarda pytest.
3. Atualizar `transcrever.py` (blocos retomáveis + overlap + offset + hotwords + logprob)
   e `download_drive.py` (gdown primário; placeholder do 1.mov documentado).
4. **Ensaio geral com vídeo sintético** (ffmpeg `testsrc` + tom, 2–3 min): valida blocos
   retomáveis, offsets, colapso de rajadas, pares antes/depois, lock e wake-up — sem
   depender da Rota A.
5. `knowledge/status.json` + script utilitário de status.

### Fase 1 — Ingestão dos vídeos (gate: 2 ações do usuário)
- **Ação do usuário (1): liberar rede** do ambiente (claude.ai/code → Environment →
  Network) — lista única: `drive.google.com`, `drive.usercontent.google.com`,
  `*.googleapis.com`, `huggingface.co`, `cdn-lfs.huggingface.co`, `*.hf.co`.
- **Ação do usuário (2): compartilhar** a pasta do curso como "qualquer pessoa com o link
  – leitor" (reversível após o download). Confirmar se existe `1.mov` (inventário só achou
  2–5.mov).
- Ordem pós-liberação: (a) baixar PRIMEIRO os binários pequenos — XLSM Automatizador,
  `.INVRUR`, `.CUSTEIOPECUARIO`, checklist zip, ferramenta coordenadas (destravam F3/F4
  mesmo se vídeo falhar); (b) baixar modelo whisper; (c) piloto ponta a ponta no 2.mov
  (menor) com auditoria do usuário (3 trechos + 5 pares de frames); (d) demais vídeos, um
  por vez, com wake-ups e commits por bloco.
- Risco mapeado: quota do Drive em link público ("too many users") → backoff e retry;
  fallback Rota B (script local de áudio) permanece pronto.

### Fase 2 — Extração de conhecimento (protocolo do usuário; síncrona, checkpoint fino)
1. Etapa 0: varredura de fontes nas transcrições → `fontes-citadas.md`; buscar MCR/normas
   públicas na web.
2. Classificação em gavetas por vídeo (só transcrição) → mapa de janelas.
3. Visão dirigida nas janelas de procedimento, lotes de 20–50 pares, manifesto JSONL,
   append+commit por lote (escala de confiança, identidade PF/PJ, estado acumulado).
4. Tabela-mestra por vídeo → `knowledge/frames/` (agora fora do gitignore).
5. Síntese: manual por módulo + `coeficientes-tecnicos.json` (número → vídeo+timestamp).
6. Dissecar binários (openpyxl+olevba; formato `.INVRUR`) → decisão do gate F3/F4.

### Fase 3 — Motores (começa em paralelo, já na Fase 0b/1)
1. Independentes dos vídeos (spec dos PDFs, começar já): port `runSim()`/`xirr()` do
   `index.html` para Python com teste de paridade contra o autoteste do simulador; motor
   de evolução de rebanho (golden numbers do PDF; pontos incertos documentados como
   `xfail`: U.A. 40 vs 72 no Ano 1, comportamento Ano 13+); regras fixas 2,5%/0,2%.
2. Dependentes da F2: custeio pecuário completo, investimento/café, capacidade de
   pagamento fim-a-fim (fórmula exata do % de utilização), cotações.
3. Gate do formato de saída (pós-dissecação): gerar `.INVRUR` OU roteiro de digitação +
   planilha-espelho.
4. Auxiliares: checklist preenchido, coordenadas/KML, memorial.

### Fase 4 — Golden tests
Reproduzir os exemplos do professor a partir só das entradas (2× `.CUSTEIOPECUARIO`,
2× `.INVRUR`, orçamento depósito, 3 relatórios PDF já cruzados ✓). `pytest` + guarda LGPD.
Critério de avanço para uso real: 100% batendo.

### Fase 5 — Operação por agentes
Skill `/novo-projeto` + subagentes (entrevistador, calculista, financeiro, preenchedor,
documentalista, revisor com os "erros comuns" da apresentação). Piloto com caso real.
Salvaguardas mantidas: minuta técnica + revisão humana; sem login/envio automático no BNB.

## Verificação

1. F0b: `pytest` do guarda-CPF passa; ensaio sintético completa as 5 etapas; histórico
   reescrito confere (`git log` sem CPF em nenhum blob).
2. F1: piloto 2.mov auditado pelo usuário; integridade antes de apagar cada .mov.
3. F2: tabela-mestra auditada por amostragem (pular ao mm:ss do vídeo e conferir).
4. F3: paridade Python×simulador; motor leite reproduz o PDF (116.640 L; 45.388,20).
5. F4: golden tests 100%. F5: piloto real revisado pelo usuário.

## Decisões pendentes do usuário
1. Gate da F1: liberar rede (lista de 6 domínios acima) + compartilhar pasta por link.
2. Confirmar existência/fileId do `1.mov`.
Sem isso, executo F0b + motores independentes da F3 — trabalho útil imediato, nada bloqueado.

---

# Plano v2.1 — ADIÇÕES (memória total, generalização "consultor sênior", Excel legado)

## Contexto das adições

Com a Fase 1 já disparada em sessão paralela, o usuário pediu três garantias:
(1) que TUDO seja salvo — curso, telas e entendimentos — de forma auditável depois;
(2) que o conhecimento seja gravado de forma GENERALIZÁVEL: um ensinamento dado num
exemplo (ex.: café conilon) deve servir para projetos rurais diferentes, como faria um
consultor sênior; (3) que o problema "algumas planilhas só funcionam no Excel 2003"
(tutorial enviado pelo professor) tenha solução planejada.

## Adição 1 — Memória total ("salvar tudo para julgar depois")

O que JÁ está garantido no v2: transcrição INTEGRAL commitada (com ⚠️ de baixa
confiança), gaveta 3 (descartes) rastreável com tempo, tabela-mestra com todo evento de
preenchimento citando vídeo+timestamp, fontes-citadas, status.json.

O que se ADICIONA (refinado por revisão independente):
1. **Contact sheets commitados** (`knowledge/frames/<video>-contatos/`): grades de
   miniaturas (~24 frames/folha) — navegação visual rápida da aula inteira. Gerador em
   `pipeline/gerar_contact_sheets.py` (PIL). Miniatura serve para NAVEGAR;
   para JULGAR célula fina, vale o item 3.
2. **Frames-evidência commitados dos itens PROVÁVEL/INCERTO**: todo item da tabela-mestra
   sem selo CONFIRMADO tem seu par de frames copiado em resolução plena para
   `knowledge/frames/<video>-evidencias/` — é exatamente o conjunto que o usuário precisa
   julgar (centenas de KB, não GB). CONFIRMADO não precisa (tem golden/tripla checagem).
3. **Manifesto JSONL por vídeo commitado** (`knowledge/frames/<video>-manifesto.jsonl`):
   1 linha por frame extraído (tempo, papel antes/depois, hash perceptual, classificação
   tela/câmera, descartado-por-quê) + versões pinadas (ffmpeg, thresholds) — torna a
   regeneração VERIFICÁVEL, não só prometida.
4. **Notas de entendimento por vídeo** (`knowledge/frames/<video>-notas.md`): o "caderno
   do aluno" — contexto, conexões entre aulas, dúvidas abertas. REGRA: toda nota carrega
   mm:ss + selo de confiança (sem isso viraria canal paralelo inauditável).
5. **Cópia-mestra confirmada**: os vídeos no Drive pertencem à conta do próprio usuário
   (verificado no inventário — owner josebassetti@gmail.com), então a fonte primária está
   segura; o gate de apagar .mov local permanece condicionado à verificação de
   integridade por vídeo. Frames full-res/áudio continuam regeneráveis por script.

## Adição 2 — Arquitetura de generalização (o "consultor sênior")

Princípio: separar o que é ESPECÍFICO do exemplo do que é GERAL, em 4 camadas + memória
de casos. O padrão já foi provado no motor de leite (fórmula geral + parâmetros do
exemplo + golden test): engines/rebanho_leite.py é o template.

| Camada | O que guarda | Onde | Quem usa |
|---|---|---|---|
| **0. Enquadramento** | cliente+pedido → finalidade/porte/linha/motor aplicável (determinístico; `regras_fixas.taxa_fne` é o embrião) | engines/enquadramento.py (F3) | porta de entrada de todo projeto |
| 1. Procedimento | como operar cada planilha/tela (mecânico) | manual-metodologia/procedimentos/ | agente Preenchedor |
| 2. Regras duras | norma/banco: limites (<60%), prazos, documentos, zoneamento | manual-metodologia/regras-duras.md + validadores em engines/ | agente Revisor (valida por código) |
| 3. Motores paramétricos | FÓRMULA geral separada dos COEFICIENTES | engines/*.py + knowledge/coeficientes-tecnicos.json | agente Calculista |
| 4. Heurísticas de julgamento | POR QUE o professor decide assim: prioridades de inversão, red flags, "nunca faça X" | manual-metodologia/principios-decisorios.md | Calculista/Revisor (aplica citando fonte) |
| **Anti-escopo** | o que o curso NÃO cobre (declarado) — fora dele o agente NÃO extrapola: degrada para "cotar/pesquisar/perguntar ao usuário" | knowledge/anti-escopo.md | todos (evita o modo de falha nº 1: extrapolação silenciosa) |
| Memória de casos | cada exemplo do professor E cada projeto real futuro (**pseudonimizado por template** — guarda LGPD já existe): entradas → decisões → saídas → resultado no banco | knowledge/casos/ | todos (raciocínio por analogia) |

Esquema do `coeficientes-tecnicos.json` (revisado): `{id, valor, unidade_canonica,
abrangencia, fonte:{video,mmss|doc}, selo (MESMA escala do protocolo:
CONFIRMADO/PROVÁVEL/INCERTO), vigencia:{data_base,validade}, historico[]}` —
**append-only** (nunca sobrescrever; atualização de cotação vira nova entrada no
histórico). **Separação crítica**: fixtures CONGELADOS dos exemplos do professor vivem em
`tests/fixtures/` (goldens imutáveis); o JSON operacional vive em `knowledge/` e pode ser
atualizado com cotação do dia — externalizar `PRECOS_PADRAO` de engines/rebanho_leite.py
nesse padrão. O lookup devolve `dentro/fora de abrangência`; uso fora de abrangência é
BLOQUEADO pelo Revisor sem aval humano.

Novos artefatos: `knowledge/INDICE.md` ("que pergunta → qual arquivo → quando consultar",
apontado pelo CLAUDE.md — o único arquivo que toda sessão nova lê);
`knowledge/mercado/fontes-cotacao.md` (sites que o professor usa + como atualizar, com
data); testes de generalização nos motores (invariantes: balanço de cabeças fecha; custo
∝ área; capacidade nunca negativa com receita positiva) além dos goldens.

## Adição 3 — Excel legado ("só funciona no Excel 2003")

Diagnóstico provável (revisor): "só funciona no Excel 2003" quase sempre = **macros
XLM/Excel 4.0 bloqueadas por padrão no Excel moderno** — e o tutorial do professor deve
ensinar a destravar (Central de Confiabilidade). Se for isso, a "dependência do 2003" se
dissolve com configuração.

1. **Ler o fato antes da estratégia**: extrair `Tutorial de Configuração do Excel.pdf`
   (437 KB, cabe no conector) → `knowledge/curso/tutorial-configuracao-excel.md` ANTES de
   dissecar os binários e decidir qualquer coisa sobre legado.
2. **Segurança no Excel do usuário**: se o tutorial mandar baixar a segurança de macros,
   orientar o usuário a usar **pasta confiável isolada** só para os arquivos do professor
   — nunca desativar proteção global.
3. **Dissecação legado-aware**: .xls/BIFF8 e macros XLM antigas (xlrd + oletools, já
   instalados) além do .xlsm moderno. Limite honesto: essas ferramentas EXTRAEM o código
   mas não o executam → semântica deduzida de macro carrega selo máximo PROVÁVEL até
   validar contra os relatórios/exemplos.
4. **Conferência primária NÃO depende do Excel legado**: a validação oficial é
   planilha-espelho + golden tests contra os relatórios PDF e exemplos do professor (já
   em knowledge/curso/). Rodar a ferramenta original vira conferência OPCIONAL do
   usuário, seguindo o tutorial. Solução definitiva da dependência 2003 = a própria
   fábrica (motores Python + saída moderna).
5. Gate da Fase 3 (inalterado): se o `.INVRUR` depender de macro legada para ser gerado,
   vale o plano B já aprovado (roteiro de digitação + planilha-espelho).

## Execução das adições

- **Nesta sessão** (rede bloqueada não impede — git funciona):
  1. Atualizar PROTOCOLO-EXTRACAO.md (saídas novas: manifesto JSONL, frames-evidência de
     PROVÁVEL/INCERTO, notas.md com mm:ss+selo, contact sheets) e PLANO.md (este v2.1).
  2. `pipeline/gerar_contact_sheets.py` + manifesto JSONL no extrator (versões pinadas,
     hash por frame) — validados re-rodando o ensaio sintético.
  3. Externalizar coeficientes do motor de leite: `tests/fixtures/exemplo-professor.json`
     (congelado, goldens) + `knowledge/coeficientes-tecnicos.json` (operacional,
     append-only, schema revisado) + lookup com dentro/fora de abrangência.
  4. Esqueletos: `knowledge/INDICE.md` (pergunta→arquivo, apontado no CLAUDE.md),
     `knowledge/anti-escopo.md`, `knowledge/casos/README.md` (template com
     pseudonimização obrigatória), `knowledge/mercado/fontes-cotacao.md`.
  5. Ler o Tutorial PDF via conector (se a conexão MCP cooperar; senão fica para a sessão
     F1 que o baixa como binário) → knowledge/curso/tutorial-configuracao-excel.md.
  6. pytest completo + commit/push com `git pull --rebase` antes (a sessão da Fase 1
     também escreve na branch).
- **Na sessão da Fase 1/2** (lê as instruções no PLANO/PROTOCOLO commitados): contact
  sheets + manifesto + evidências por vídeo real, notas.md por vídeo, dissecação
  legado-aware, camada de enquadramento (F3).

## Resposta curta às 3 perguntas do usuário (para a mensagem final)

1. Sim — transcrição integral, cada preenchimento com tempo, descartes e dúvidas já são
   salvos; adicionamos evidência visual commitada dos pontos duvidosos, manifesto
   verificável, notas de entendimento e contact sheets para navegar tudo depois.
2. Generalização = separar fórmula (geral) de coeficiente (do exemplo), + regras duras,
   + heurísticas do professor com citação, + anti-escopo (não extrapolar em silêncio),
   + biblioteca de casos crescente — o padrão já provado no motor de leite.
3. Excel 2003 = provavelmente macros antigas bloqueadas; ler o tutorial do professor
   primeiro, destravar com pasta confiável isolada, e a fábrica em si nunca dependerá do
   Excel legado (motores Python + planilha-espelho moderna).

## Verificação das adições
1. Contact sheet do vídeo sintético do ensaio gerado e legível (grade com timestamps).
2. INDICE.md aponta para todos os artefatos existentes (link-check simples).
3. Schema do coeficientes JSON validado com os coeficientes já extraídos do leite
   (parição 70%, 12 L/dia, 270 dias, R$ 2,30/L, 394,68/cabeça) sem violar o teste LGPD.
4. pytest continua 15 verdes + 1 xfail (nada quebrado).

---

# Adendo v2.2 — Política de modelos por etapa (pergunta do usuário, respondida com a
referência oficial de modelos/preços consultada em 2026-07-07)

Preços por 1M tokens (entrada/saída): Haiku 4.5 $1/$5 · Sonnet 5 $3/$15 (promo $2/$10 até
2026-08-31) · Opus 4.8 $5/$25 · Fable 5 $10/$50. Em assinatura (Pro/Max), a mesma ordem
vale para a velocidade com que o limite de uso é consumido. Visão de alta resolução
(2576px, leitura fina de tela): Opus 4.7+ e Sonnet 5 têm; Haiku 4.5 não.

**Princípio: gastar modelo caro onde o erro custa caro; modelo barato onde o PROCESSO
corrige erro barato** (selos de confiança, evidências commitadas, golden tests e auditoria
humana já blindam o pipeline contra erro pontual de classificação — mas NÃO contra erro de
leitura de número, que contamina a base na origem).

| Etapa | Quem executa | Modelo | Racional |
|---|---|---|---|
| Transcrição das ~10h de áudio | faster-whisper local (NÃO é Claude) | n/a | grátis, roda no container; Claude só revisa/corrige com hotwords e triagem |
| Frames, manifesto, contact sheets, dedup | Python/ffmpeg determinístico | n/a | sem modelo |
| Classificação da transcrição em gavetas (lotes grandes de texto) | subagentes | **Sonnet 5** (Haiku 4.5 só para triagem bruta de "conversa fiada" óbvia) | tarefa com rubrica clara do protocolo; regra: na dúvida → escala para o modelo da sessão; "na dúvida não descartar" já protege |
| **Leitura de frames (células, números BR, barra de fórmulas) + tabela-mestra** | sessão principal / subagentes síncronos | **Fable 5 (sessão atual) ou Opus 4.8 — nunca menos** | passo mais crítico: número mal lido em vídeo comprimido vira erro na fonte; percepção fina é força do topo da linha |
| Síntese (manual, princípios decisórios, coeficientes) | sessão principal | Fable 5 / Opus 4.8 | julgamento e generalização |
| Motores, código, testes | sessão | Fable 5 (atual; paridade provada na 1ª execução) | qualidade de engenharia |
| Produção por cliente (Fase 5, para sempre) | sessão do usuário | **Opus 4.8 como padrão** (Fable 5 para caso atípico/difícil) | golden tests + agente Revisor + revisão humana seguram a qualidade; metade do custo do Fable |

Implementação: os subagentes aceitam override de modelo (sonnet/haiku) por chamada — a
skill /novo-projeto e os prompts da Fase 2 declaram o modelo por lote conforme a tabela.
A sessão paralela da Fase 1 usa o modelo selecionado nela (seletor de modelo da sessão) —
recomendação ao usuário: manter o padrão atual para o piloto; o custo dominante da Fase
1-2 é a leitura de frames, e é justamente onde não se economiza.

Roteiro operacional completo da analista (consolidação de tudo acima em 29 passos):
`knowledge/manual-metodologia/passo-a-passo-analista.md`.
