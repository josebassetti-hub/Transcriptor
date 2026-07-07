# Passo a passo da Analista de Vídeos — do arquivo bruto ao conhecimento auditável

Roteiro operacional completo para quem for analisar as vídeo-aulas (humano ou agente),
consolidando tudo o que foi desenvolvido: plano v2/v2.1/v2.2 + PROTOCOLO-EXTRACAO.md.
Pressupõe as ferramentas prontas (pipeline/ deste repo). **A regra que governa todas as
outras: o tempo amarra tudo — nenhum fato existe sem vídeo + mm:ss de origem.**

---

## ETAPA A — Preparação (antes de tocar no vídeo)

1. **Carregar o repertório**: ler `knowledge/INDICE.md`, `PROTOCOLO-EXTRACAO.md`,
   `fontes-citadas.md` e as destilações em `knowledge/curso/`. Só se reconhece como
   importante aquilo que já se sabe que é importante — ouvir a aula com ouvido treinado.
2. **Conferir o estado**: `knowledge/status.json` diz em que etapa cada vídeo está.
   Nunca refazer o que já tem checkpoint; sempre retomar do último ponto commitado.
3. **Verificar integridade do vídeo**: tamanho baixado = inventário
   (`knowledge/inventario-drive.md`). Vídeo corrompido gera interpretação corrompida.

## ETAPA B — Captura mecânica (determinística — sem interpretação ainda)

4. **Extrair o áudio** (16 kHz mono): `pipeline/extrair_audio_frames.py`.
5. **Transcrever em blocos retomáveis** (`pipeline/transcrever.py`): blocos de ~20 min com
   10 s de sobreposição; vocabulário do domínio injetado (hotwords: FNE, parição,
   custeio...); anti-loop ativado; **commit no git a cada bloco** (queda de conexão perde
   no máximo 1 bloco). Trechos de baixa confiança saem marcados com ⚠️ e listados em
   `<video>-revisar.md`.
6. **Extrair os frames em 2 passadas**: detectar os tempos T de mudança de tela
   (gatilho sensível 0,04) e capturar o **par antes/depois** de cada T —
   `T−0,5s` (tela anterior FINALIZADA, com os números já digitados) e `T+0,2s` (tela nova
   assentada). Frames forçados no segundo 0 e no último segundo; rajadas de digitação
   (<2 s) colapsadas em primeira+última; frame de segurança a cada 60 s sem mudança.
7. **Dedup honesto**: duplicata só quando phash E diferença de pixels concordam (phash
   sozinho apagaria a mudança de UMA célula — bug real pego no ensaio). Todo frame,
   mantido ou descartado, entra no **manifesto JSONL** com hash e motivo — a captura é
   verificável, não prometida.
8. **Gerar contact sheets** (`pipeline/gerar_contact_sheets.py`) e classificar frames em
   tela-de-planilha vs câmera-nas-pessoas (mover para subpastas — NUNCA apagar; contagem
   no manifesto).
9. **Gate de integridade** antes de apagar o .mov local: duração do WAV = duração do
   vídeo; frames > 0; manifesto escrito. (O Drive do usuário é a cópia-mestra.)

## ETAPA C — Primeira leitura (só texto — as imagens esperam)

10. **Varredura de fontes (Etapa 0 do protocolo)**: passar a transcrição inteira SÓ
    caçando menções a manuais, normativos, sites, planilhas-modelo → atualizar
    `fontes-citadas.md` com versão/ano citado + mm:ss. Norma pode ter mudado desde a
    gravação — anotar "confira vigência".
11. **Classificar em 3 gavetas, por BLOCO** (não por frase solta — o ensino tem ritmo:
    explica→faz, faz→explica, fala-enquanto-faz):
    - Gaveta 1 **Procedimento** (tela→ação→resultado) → vira skill executora;
    - Gaveta 2 **Conhecimento decisório** (regra do banco, "nunca faça X", capacidade de
      pagamento — o OURO; não depende de tela) → vira skill decisora;
    - Gaveta 3 **Conversa paralela** → `descartes.md` com tempo e motivo (recuperável).
    **Na dúvida entre 2 e 3, NUNCA descartar.**
12. **Mapa de janelas**: delimitar os intervalos de tempo em que o professor está
    preenchendo/mostrando tela — só essas janelas vão para leitura visual (não se lê
    milhares de frames às cegas).

## ETAPA D — Leitura dos frames (interpretação disciplinada — o coração anti-erro)

13. **Lotes pequenos** (20–50 pares antes/depois), só nas janelas de procedimento;
    resultado gravado e commitado a cada lote.
14. **Identidade ANTES de interpretação**: que arquivo está na tela? Sinais em ordem de
    confiança: cabeçalho/rodapé → título da janela → nome da aba → aplicativo →
    impressão digital visual → narração. Tomador PF (CPF 11 dígitos) ou PJ (CNPJ 14)?
    Documento borrado não se chuta — `[INCERTO] conferir em mm:ss`.
15. **Regra-mãe: ler o que ESTÁ no print, nunca o que se imagina.** Pré-condições de
    leitura: barra de fórmulas visível? cabeçalhos de coluna? aba identificável? número
    legível (compressão transforma 8 em 3, vírgula em ponto)? Se falta, registrar a
    limitação em vez de completar por suposição.
16. **Comparar antes/depois e isolar O QUE MUDOU** (não descrever a tela inteira).
    Distinguir mudança de DADO de mudança de VISTA (rolagem/zoom = navegação). Cuidado
    com "antes" pego no meio da digitação — conferir contra o próximo estado estável.
17. **Disciplina de números**: formato BR (`1.000,00`); nunca "arredondar" o lido;
    dígito ilegível = `R$ 47.81_,__ (ilegível, conferir em mm:ss)`; barra mostrando
    `=B2*C2` = resultado calculado, não valor digitado.
18. **Tripla checagem do procedimento**: a fala aponta para a tela? o print confirma?
    o tempo bate? Fala e print divergem → registrar a divergência, não forçar encaixe.
19. **Selo de confiança em TODO fato** — o coração do "não errar":
    - **CONFIRMADO** = print claro E fala batem;
    - **PROVÁVEL** = só um dos dois sustenta;
    - **INCERTO** = nenhum; "não determinei, confira em mm:ss".
    Todo item PROVÁVEL/INCERTO tem seu par de frames copiado em resolução plena para
    `knowledge/frames/<video>-evidencias/` — é exatamente o conjunto que o dono do
    projeto julga depois.
20. **Interpretação TEM memória** (a captura, de propósito, não tem): ficha viva por
    arquivo (min 05 aberto vazio → min 12 coluna X preenchida → min 40 CONTINUANDO).
    Desvio para consultar outro arquivo = parêntese, registrando a ORIGEM do dado
    ("valor digitado às 39:00 veio do balancete das 38:30"). Voltar = continuar, salvo
    sinal explícito de recomeço. Buraco de captura = sinalizado, jamais preenchido.

## ETAPA E — Estruturação (a espinha dorsal)

21. **Tabela-mestra por vídeo** (`knowledge/frames/<video>-tabela-mestra.md`), linha a
    linha do primeiro ao último evento: Tempo · Vídeo · Arquivo · PF/PJ · Tipo ·
    Explicou (porquê) · Fez na tela (como) · Estado do arquivo · Origem do dado ·
    **Depende de** (a ordem de execução, inclusive entre arquivos) · Regra/Normativo ·
    Confiança · Pérola/Aviso. Append + commit por lote.
22. **Notas de entendimento** (`<video>-notas.md`) — o caderno do aluno: contexto,
    conexões entre aulas, dúvidas abertas. TODA nota com mm:ss + selo (sem exceção —
    senão vira canal paralelo inauditável).
23. Atualizar `status.json` e commitar.

## ETAPA F — Consolidação (transformar registro em conhecimento generalizável)

24. **Coeficientes técnicos** → `knowledge/coeficientes-tecnicos.json` (via
    `engines/coeficientes.py`): cada número com unidade, **abrangência declarada** (onde
    vale: cultura/região/tecnologia), vigência, fonte (vídeo+mm:ss) e selo. Append-only.
    Os números dos exemplos do professor são CONGELADOS em `tests/fixtures/` (goldens
    imutáveis) — cotação nova nunca reescreve o golden.
25. **Manual por módulo** (`knowledge/manual-metodologia/`): procedimentos (gaveta 1),
    regras duras validáveis por código, e `principios-decisorios.md` (heurísticas do
    professor, com citação). Se o professor simplificou uma regra que tem exceção,
    anotar "ele simplificou; a norma tem um detalhe a mais".
26. **Anti-escopo** (`knowledge/anti-escopo.md`): atualizar o que o curso NÃO cobriu —
    fora dele, nenhum agente extrapola em silêncio (pesquisa/cota/pergunta).
27. **Triangulação**: cruzar números entre fontes independentes (ex.: preços do
    orçamento × receitas do relatório de leite bateram ao centavo → selo subiu para
    CONFIRMADO). Upgrade de selo só com prova, nunca por conveniência.
28. **Golden tests**: toda fórmula deduzida vira código + teste que reproduz o exemplo
    do professor ao centavo (padrão provado em `engines/rebanho_leite.py`); pontos
    incertos ficam como `xfail` documentado até o vídeo confirmar.
29. **Auditoria humana por amostragem**: o dono do projeto confere 3 trechos de
    transcrição + 5 pares de frames por vídeo (pulando direto ao mm:ss citado) e julga
    as evidências dos PROVÁVEL/INCERTO. Só depois o vídeo é dado por concluído.

---

## Princípios transversais (valem em toda etapa — os "nunca")

- **Tempo em tudo**, inclusive no descarte.
- **Professor = fonte canônica**; em conflito com aluno, vence o professor.
- **Na dúvida, não descartar.** **Não inventar — marcar a dúvida e o segundo.**
- **Fonte na mão vence memória** (citar capítulo/página do documento, não lembrança).
- **LGPD**: CPF/CNPJ/nomes reais nunca vão para o git (pseudonimizar; teste automático
  vigia).
- **Commit frequente** (bloco/lote): nenhum resultado vive só na memória de quem analisa.
- **Modelos por etapa** (adendo v2.2): leitura fina de números e síntese = modelo topo de
  linha (Fable 5/Opus 4.8), sem exceção; classificação em massa de texto = Sonnet 5 com
  regra de escalar na dúvida; transcrição = Whisper local (não é Claude); mecânica de
  frames = Python puro.
