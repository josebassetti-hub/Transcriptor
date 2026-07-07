# Protocolo de Extração e Estruturação das Videoaulas

Protocolo operacional da Fase 2 (extração de conhecimento). Origem: pesquisa do usuário
(06/07/2026), adaptada às ferramentas deste repositório. **Os agentes de análise DEVEM
seguir este protocolo.** Versão integral da pesquisa: `knowledge/protocolo-original.md`.

## Princípio central — o tempo amarra tudo

Todo item capturado carrega **vídeo + segundo de origem** (`aula`, `mm:ss`), inclusive o
descarte. É o que permite: casar fala com print, voltar ao vídeo na dúvida, e o usuário
auditar qualquer classificação pulando direto para o segundo.

## Princípios de honestidade (prioridade sobre "entregar rápido")

1. Incerteza declarada ("acredito que...", "confira em mm:ss") — nunca mascarada.
2. Não inventar fonte/título/URL; citar capítulo/página do documento em mãos, não de memória.
3. Número com qualquer dúvida (borrado, decimal ambíguo) → sinalizado para conferência.
4. Norma pode ter mudado desde a gravação → avisar "ele cita a versão X, verifique se mudou".
5. Formato numérico BR (`1.000,00`); ambiguidade não se resolve por palpite.
6. Valor digitado ≠ resultado calculado (barra de fórmulas distingue; sem ela, marcar dúvida).
7. Nunca "arredondar" o lido: `R$ 47.81_,__ (dígito ilegível, conferir em mm:ss)`.

## Etapa 0 — Varredura de fontes (antes de classificar)

Primeira passada na transcrição SÓ para caçar menções a manuais, normativos, planilhas-
modelo, sites e leis. Saída: `knowledge/fontes-citadas.md`:

| Fonte citada | Tipo | Versão/Ano citado | Já temos? | Usuário precisa enviar? | Vídeo + tempo |
|---|---|---|---|---|---|

O acervo cresce a cada vídeo e alimenta a skill decisora. Fonte que não conseguirmos
baixar → pedir ao usuário ANTES da síntese final.

## Etapa 1 — Captura (implementada em `pipeline/`)

- **Transcrição**: `pipeline/transcrever.py` — faster-whisper pt-BR, timestamps,
  `condition_on_previous_text=False` (anti-loop). Sem diarização automática: os vídeos são
  professor-dominante; na análise, falas com cara de pergunta são marcadas `[ALUNO?]` e o
  professor é a **fonte canônica** (em conflito, vence o professor).
- **Frames**: `pipeline/extrair_audio_frames.py` — duas passadas:
  1. Detecta os tempos T de mudança de cena (`scene>0.04`, sensível porque planilha muda pouco).
  2. Para cada T extrai o par **antes** (`T−0,5s` = tela anterior FINALIZADA, com os números
     digitados) e **depois** (`T+0,2s` = tela nova assentada), mais frames forçados no
     segundo 0 e no último segundo, e frames de segurança se passar 60s sem mudança.
  Nome do arquivo carrega o tempo e o papel: `f_HHMMSS_a.jpg` / `f_HHMMSS_d.jpg`.
- Vai-e-volta do curso: a detecção não tem memória — voltar a uma tela já vista dispara de
  novo, com o tempo atual. Correto: a fala continua batendo.

## Etapa 2 — Leitura dos prints (agentes de visão)

**Regra-mãe: ler o que ESTÁ no print, não o que se imagina.**

Pré-condições de leitura confiável (senão, registrar a limitação):
barra de fórmulas visível? cabeçalhos de coluna visíveis? aba ativa identificável?
legibilidade real (compressão pode virar 8→3, vírgula→ponto)?

Como ler: identificar **o que mudou** entre antes/depois (não descrever a tela inteira);
distinguir mudança de DADO de mudança de VISTA (rolagem/zoom = navegação); cuidado com
"antes" pego no meio da digitação (comparar com o próximo estado estável).

**Identidade do arquivo (ler ANTES de interpretar)** — sinais em ordem de confiança:
cabeçalho/rodapé (nome, CPF/CNPJ, projeto, data-base, logo) → título da janela → nome da
aba → aplicativo (Excel? PDF? navegador? sistema do banco?) → impressão digital visual →
narração. Ficha de identidade por arquivo com selo por campo:
**Natureza PF/PJ** (CPF 11 dígitos ≠ CNPJ 14 — borrado não se chuta), documento, nome,
projeto/operação, data-base, origem (modelo oficial ≠ dado de cliente).
CPF/CNPJ/nome = dado sensível: usar só para identificar o arquivo, não expor além do necessário.

**Rastreamento de estado (a interpretação TEM memória):** o projeto é construído — a
planilha do minuto 40 é a do minuto 5 mais preenchida. Ficha viva por arquivo:

```
projeto.xlsx
  05:00 → aberto, vazio
  12:00 → coluna "faturamento 12 meses" preenchida
  40:00 → adicionada amortização (CONTINUANDO, não recomeçando)
```

Trabalho vs Consulta: desvio para olhar um dado é parêntese, não arquivo novo; registrar a
**origem do dado** ("valor digitado às 39:00 veio do balancete consultado às 38:30").
Voltar = continuar, salvo sinal explícito de reset (arquivo em branco, "vamos do zero",
trocou de cliente). Buraco de captura → sinalizar ("entre 20:00 e 25:00 pode ter havido
preenchimento não capturado"), nunca preencher com suposição.

**Escala de confiança (obrigatória em cada fato):**
- **CONFIRMADO** — print claro E fala batem.
- **PROVÁVEL** — só um dos dois sustenta; marcar "a confirmar".
- **INCERTO** — nem print nem fala; "não consegui determinar, confira em mm:ss".

## Etapa 3 — Classificação em três gavetas

| Gaveta | Conteúdo | Vira |
|---|---|---|
| 1. Procedimento | tela→ação→resultado (o "como") | **Skill executora** (preenchedor de planilhas) |
| 2. Conhecimento de financiamento | regra do banco, enquadramento, capacidade de pagamento, lógica FNE, "nunca faça X" — **o ouro**; não depende de tela | **Skill decisora** (calculista/revisor) |
| 3. Conversa fiada / a-verificar | papo paralelo — não é lixo, é recuperável | `knowledge/descartes.md` com tempo e motivo |

Regras: leitura por **BLOCO** (padrões: explica→faz — fala de 30–60s antes da ação;
faz→explica; fala-enquanto-faz; marcadores "agora eu vou colocar...").
Tripla checagem no procedimento: a palavra aponta pra tela? o print confirma? o tempo bate?
Preenchimento campo a campo → captura mais densa (baixar gatilho) e a narração é o dado.
**Na dúvida entre gaveta 2 e 3 → NÃO descartar.** Ação invisível → marcar dúvida.

## Etapa 4 — Tabela-mestra (espinha dorsal por vídeo)

Saída: `knowledge/frames/<video>-tabela-mestra.md` — sequência ordenada da primeira tela
ao resultado final:

| # | Tempo | Vídeo | Arquivo | PF/PJ | Tipo | Explicou (porquê) | Fez na tela (como) | Estado do arquivo | Origem do dado | Depende de | Regra/Normativo | Confiança | Pérola/Aviso |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- **Depende de** = ordem de execução da cadeia, inclusive entre arquivos → vira a ordem em
  que o agente executor roda.
- **Regra/Normativo** = gancho procedimento↔conhecimento (com versão; avisar se o professor
  simplificou uma regra que tem exceção).
- **Estado/Origem** = a memória do projeto sendo construído.

## Saídas finais da Fase 2

1. Passo a passo executável por módulo (gaveta 1 consolidada) → `knowledge/manual-metodologia/`
2. Documento de conhecimento decisório (gaveta 2 consolidada) → `knowledge/manual-metodologia/`
   (inclui `principios-decisorios.md`: heurísticas do professor com citação)
3. `knowledge/descartes.md` (gaveta 3, rastreável)
4. `knowledge/fontes-citadas.md` (Etapa 0)
5. `knowledge/coeficientes-tecnicos.json` (base OPERACIONAL, append-only, schema no próprio
   arquivo) — fixtures congelados dos exemplos ficam em `tests/fixtures/` (goldens imutáveis)
6. `knowledge/anti-escopo.md` revisado (o que o curso NÃO cobriu — fora dele o agente não
   extrapola: pesquisa/cota/pergunta)
7. `knowledge/casos/` — cada exemplo do professor vira um caso (template no README; sempre
   pseudonimizado)

## Memória total por vídeo (plano v2.1 — o que fica commitado no git)

| Artefato | Caminho | Conteúdo |
|---|---|---|
| Transcrição integral | `transcricoes/<video>.md` (+ blocos/) | toda a fala, ⚠️ nos trechos de baixa confiança |
| Tabela-mestra | `frames/<video>-tabela-mestra.md` | todo evento de tela com tempo/estado/dependências |
| Manifesto de frames | `frames/<video>-manifesto.jsonl` | 1 linha/frame: tempo, papel a/d, phash, mantido/descartado+motivo; cabeçalho com versões pinadas (ffmpeg, thresholds) — regeneração VERIFICÁVEL |
| Contact sheets | `frames/<video>-contatos/` | miniaturas com timestamp para navegar a aula sem o vídeo |
| Frames-evidência | `frames/<video>-evidencias/` | pares antes/depois em resolução plena de TODO item PROVÁVEL/INCERTO (o que o usuário julga; CONFIRMADO dispensa) |
| Notas de entendimento | `frames/<video>-notas.md` | "caderno do aluno": contexto e conexões — TODA nota com mm:ss + selo (sem exceção) |
| Descartes | `descartes.md` | gaveta 3 com tempo e motivo |

Frames full-res completos e áudio ficam FORA do git (materiais/, efêmero) — regeneráveis
por script determinístico a partir dos vídeos no Drive (cópia-mestra do próprio usuário,
owner verificado) e conferíveis pelo manifesto.
