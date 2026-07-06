# Protocolo de Extração e Estruturação de Videoaulas (pesquisa original do usuário)

> Documento entregue pelo usuário em 06/07/2026, preservado na íntegra.
> Versão operacional adaptada a este repositório: `knowledge/PROTOCOLO-EXTRACAO.md`.

### Da captura do vídeo até a base de uma skill/agente

> **Objetivo:** transformar uma videoaula (professor + alunos, com tela de planilha e trechos só de câmera) em material estruturado, sem perder nada de valioso, já organizado para virar skill executora, skill decisora e base de conhecimento — lendo os prints com disciplina, identificando o arquivo (PF ou PJ) e rastreando o estado de cada documento ao longo da aula.

---

## Princípio central — o tempo amarra tudo

Tudo que for capturado carrega **o segundo de origem** e **a identificação do vídeo**. O carimbo de tempo nunca se separa do conteúdo — nem no procedimento, nem no conhecimento, nem no descarte.

É o tempo que permite três coisas:
1. **Casar** a fala com o print (o que estava na tela no instante em que ele falou).
2. **Voltar ao vídeo** em qualquer dúvida, no ponto exato.
3. **Revisar e corrigir** uma classificação minha — você pula direto pro segundo e confere.

Dois níveis de localização, sempre:
- **Tempo no vídeo** (`mm:ss`) → amarra o trecho ao ponto exato da aula.
- **Identificação do vídeo** (nome / data da aula) → amarra o trecho ao arquivo certo, pra não misturar quando houver vários vídeos.

---

## Princípios de honestidade (regem TODAS as etapas)

Estes princípios têm prioridade sobre a vontade de "entregar rápido". Preferir um buraco honesto a um dado errado.

1. **Incerteza:** se eu não tiver certeza de um fato, eu digo claramente ("Acredito que...", "Você deve verificar isso"). **Antes** de admitir incerteza sobre um fato do mundo (regra vigente, versão de norma, preço, prazo), eu **faço uma pesquisa profunda** na internet primeiro — só depois sinalizo a dúvida.
2. **Fontes:** não inventar título, URL ou referência. Se eu não souber a fonte, admito. Cito capítulo/página do documento que você me deu, não da memória.
3. **Números:** todo dado numérico com qualquer incerteza é sinalizado com recomendação de conferir (valor borrado, CPF/CNPJ ilegível, casa decimal ambígua).
4. **Eventos recentes:** aviso quando o tema pode ter mudado desde meu treinamento. Não apresento norma/condição possivelmente desatualizada como atual.
5. **Citações:** nunca atribuo uma fala a alguém sem certeza. Se não puder confirmar, digo: "Não consigo confirmar essa citação."

---

## ETAPA 0 — Varredura de fontes (montar o repertório ANTES)

> Esta etapa existe porque eu só reconheço como "importante" aquilo que já sei que é importante. Se o professor cita um manual ou normativo que eu não tenho na mão, posso passar batido. Carregar a teoria antes = ouvir o vídeo com ouvido treinado, não leigo.

**Passos:**
1. Primeira passada na transcrição **só para caçar menções** — nada é classificado ainda.
2. Listar tudo que o professor referencia: manuais, normativos, instruções, leis, entendimentos, planilhas-modelo, capítulos.
3. Para cada fonte, anotar **a versão / ano** que o professor está usando.
4. Eu pesquiso e baixo o que conseguir; **o que eu não achar, você me envia** antes de a gente seguir.
5. Esse acervo vira a **base de conhecimento permanente** — cresce a cada vídeo novo e alimenta a skill decisora.

**Modelo da lista de fontes:**

| Fonte citada | Tipo | Versão/Ano citado | Consegui baixar? | Você precisa enviar? | Tempo da menção |
|---|---|---|---|---|---|
| Ex: Manual do Crédito Rural | Normativo | (a confirmar) | ☐ | ☐ | mm:ss |

> ⚠️ **Cuidado de atualização:** manuais e normativos mudam com o tempo (revoga artigo, troca número de instrução). Se o vídeo for antigo, a regra ensinada pode já estar desatualizada hoje. Eu **pesquiso** e sinalizo — *"ele cita a versão X, verifique se mudou"* — pra você não replicar numa planilha de hoje uma regra que o banco já alterou.

---

## ETAPA 1 — Captura

### 1.1 Transcrição com tempo + separação de quem fala

- Transcrever **toda** a fala (com câmera na tela ou nas pessoas — tudo).
- Usar ferramenta com **diarização** (separa locutores) e **timestamp**.
- Exportar em **SRT ou VTT** (formatos que carregam o tempo).

**Ferramentas (verificar preço/recursos atuais antes de assinar — isso muda):**
- *Local, grátis, privado (roda no seu Mac M3):* Whisper por terminal (modelo `medium` é o ideal pra 8 GB de RAM; `large` fica apertado). Não separa locutor sozinho.
- *Local, pago, fácil (arrasta e solta):* MacWhisper Pro — diarização em beta, precisa revisão; processa no próprio Mac, **não sobe pra internet**.
- *Local, grátis, técnico:* WhisperX (Whisper + pyannote) — melhor diarização, mas instalação complicada (token Hugging Face) e sem GPU dedicada roda lento no M3.
- *Online (sobem o vídeo pra nuvem):* Sonix, ElevenLabs — evitar para material sensível de cliente.

> Anti-loop do Whisper: se ele repetir a mesma frase sem parar, usar `--condition_on_previous_text False` e/ou subir o modelo.

**Marcar o professor:**
- Identificar uma vez quem é o professor → trocar por `[PROFESSOR]`.
- Demais → `[ALUNO]`.
- **Regra de hierarquia:** o `[PROFESSOR]` é a **fonte canônica**. Aluno serve para complementar/contextualizar. Em conflito, **vence o professor**.
- Se o vídeo é **professor dominante** (alunos só perguntam de vez em quando), a diarização automática pode ser dispensável: identifico o professor pelo conteúdo e as perguntas de aluno são marcadas na mão.

### 1.2 Prints só na mudança de tela (não segundo a segundo)

Capturar **apenas quando a tela muda de verdade** (detecção de cena). Tela parada não gera print. Resultado: centenas de imagens úteis, não milhares idênticas.

Comando base (ffmpeg):

```
ffmpeg -i video.mp4 -vf "select='gt(scene,0.04)',showinfo" -vsync vfr print_%04d.png
```

- `scene` mede a mudança de 0 a 1; o número é o **gatilho**.
- Planilha muda pouco a cada ação → começar **sensível** (`0.02`–`0.05`).
- `showinfo` cospe o `pts_time` (segundo exato) de cada print no log → é o que amarra o print ao tempo.

> ⚠️ A flag `-frame_pts true` (nomear arquivo com o tempo) **varia conforme a versão do ffmpeg**. Testar num trecho curto antes das 3h. O caminho `showinfo` + log é o mais previsível.

### 1.3 Par antes/depois em cada transição

Numa videoaula de planilha, o quadro que interessa é **o fim da etapa anterior**, não o começo da próxima. A finalização (últimos números digitados) muda pouco e **não dispara** o gatilho; quem dispara é a troca brusca de tela depois. Por isso, em cada mudança `T`:

- **`T − 0,5s`** → tela antiga **finalizada** (números já no lugar).
- **`T + 0,2s`** → tela nova já assentada.

São **dois prints diferentes** (telas distintas — fechamento de uma coisa, abertura de outra). Recuos são chute inicial; **calibrar num trecho curto**.

**Duas exceções obrigatórias:**
- Forçar print no **segundo 0** (estado inicial — não tem mudança antes).
- Forçar print no **último segundo** (estado final — não tem mudança depois).

**Vai-e-volta do curso:** a detecção compara só com o quadro anterior — **não tem memória**. Voltar pra uma tela já vista conta como mudança e **dispara igual**, com o segundo daquele momento. A fala continua batendo porque o print sai marcado com o tempo atual, não com o da primeira aparição.

### 1.4 Processo de duas passadas (resumo técnico)
1. **Passada 1:** detectar os tempos das mudanças (`showinfo`, sem salvar imagem).
2. **Passada 2:** para cada `T`, extrair `T−0,5s` e `T+0,2s` com `-ss`, mais os dois forçados, nomeando pelo tempo.

---

## ETAPA 2 — Leitura e interpretação dos prints

> A captura garante o **quando**. Esta etapa garante o **o quê** — ler o print sem errar. A captura é sem memória de propósito; **a interpretação carrega memória** (o projeto é construído, não recomeça a cada tela).

### Regra-mãe: leio o que ESTÁ no print, não o que eu imagino
Um print é uma foto congelada — não mostra tudo. Se não está visível, **eu sinalizo a dúvida e aponto o segundo**; eu não completo com suposição. Vale especialmente para números de financiamento.

### Parte A — O que o print precisa conter (senão a leitura já nasce furada)
1. **Barra de fórmulas visível** → distingue valor digitado de fórmula. Sem ela, marco "não dá pra saber se é valor ou fórmula".
2. **Cabeçalhos das colunas** → um número solto sem cabeçalho não diz o que representa.
3. **Aba/planilha ativa identificável** → sem a barra de abas, não afirmo em qual aba estava.
4. **Legibilidade real** → fonte pequena + compressão de vídeo pode virar `8` em `3`, vírgula em ponto. Se borrado, não adivinho o número.

### Parte B — Como leio cada print
5. **Identificar o que mudou, não o print inteiro** (comparar antes/depois e isolar a célula/campo alterado).
6. **Não afirmar posição do cursor** só pelo quadro congelado — cruzo com a fala; se nem print nem fala confirmam, marco dúvida.
7. **Distinguir mudança de DADO de mudança de VISTA** (rolar página / dar zoom não é preenchimento, é navegação).
8. **Cuidado com o "antes" pego no meio da digitação** (`T−0,5s` pode ter pegado campo parcial) → comparo com o próximo estado estável para pegar o valor **fechado**.

### Parte C — Disciplina de números (crítica)
9. **Formato BR vs US:** `1.000,00` (BR) ≠ `1,000.00` (US). No material é sempre BR; se ambíguo, confirmo com você — não assumo a casa decimal.
10. **Nunca "arredondar" o lido:** registro `R$ 47.812,35` exato; se o último dígito é ilegível → `R$ 47.81_,__ (dígito ilegível, conferir em mm:ss)`.
11. **Valor digitado ≠ resultado calculado:** se a barra mostra `=B2*C2`, o número é resultado, não entrada.

### Parte D — Escala de confiança (o coração do "não errar")
12. **CONFIRMADO** — print claro **e** fala bate → afirmo com segurança.
13. **PROVÁVEL** — só um dos dois mostra → registro, marco "a confirmar".
14. **INCERTO** — nem print nem fala deixam claro, ou ilegível → "não consegui determinar, confira em mm:ss". Não invento.

### Parte E — Cruzamento print ↔ fala ↔ norma
15. **A fala explica o print?** Se divergem, não forço o encaixe — registro a divergência e aponto o segundo.
16. **Casar com o normativo** só quando eu tiver a fonte na mão; senão "parece corresponder a X, verificar no manual".

### Parte F — Identidade do arquivo (que documento está na tela)
Antes de interpretar, identifico a **carteira de identidade** do arquivo. Sinais, do mais confiável ao menos:
1. **Cabeçalho / rodapé** — muitas vezes o mais rico: traz **empresa/nome, CPF/CNPJ, projeto, data-base, versão, logo do banco**. Ler primeiro.
2. **Título na barra da janela** (nome do arquivo).
3. **Nome da aba** (abas do Excel).
4. **Aplicativo** (Excel? PDF do balancete? navegador? sistema do banco?).
5. **Impressão digital visual** (layout, cabeçalhos, estrutura → reconhecer "é a mesma planilha do minuto 12").
6. **Narração** ("volta pro projeto", "aqui é o balancete").

Cuidados de cabeçalho:
- **Pode estar rolado pra fora da tela** → se não visível, `[INCERTO] cabeçalho não visível`, busco em outro print/na fala; não assumo empresa só pelo layout.
- **Dado sensível** (CPF, CNPJ, nome, sócio) → registro para identificar, tratando como informação de cliente.
- **Não ler número errado** (CPF/CNPJ/data borrados → não chutar, sinalizar).
- **Modelo oficial ≠ dado do cliente** → "Banco do Nordeste — Plano de Negócio" é texto fixo do modelo (diz o *tipo*); o nome preenchido diz *qual* projeto.

### Parte G — Pessoa Física ou Jurídica (primeiro julgamento da identidade)
O tomador pode ser **PF** ou **PJ**, e isso muda documento, planilha/formulário e, possivelmente, a regra.
- **PJ:** razão social, **CNPJ** (14 dígitos), sócio, tipo societário.
- **PF:** nome da pessoa, **CPF** (11 dígitos), atividade (ex: produtor rural).
- **CPF ≠ CNPJ:** se borrado, não chuto qual é → `[INCERTO] documento — conferir em mm:ss`.
- **Regra do banco pode diferir entre PF e PJ** (ex: crédito rural PF). **Não afirmo de memória** — registro o que o professor disse e, para confirmar a norma, **pesquiso ou peço o manual**.
- **Formulário de cadastro é outro** (a skill `cadastro-bnb` já separa PF versão 06/2025 de PJ versão 07/2024) → tento identificar qual está na tela.
- **CPF é dado pessoal sensível** — cuidado reforçado.

Ficha de identidade (cada campo com selo *confirmado / provável / incerto*):
- **Natureza:** PF ou PJ
- **Documento:** CPF (PF) ou CNPJ (PJ)
- **Nome:** pessoa (PF) ou razão social + sócio (PJ)
- **Projeto / tipo de operação**
- **Data-base / versão**
- **Origem:** modelo oficial? planilha própria?

### Parte H — Rastreamento de estado (a interpretação tem memória)
Um projeto é **construído**: a planilha do minuto 40 é a do minuto 5, mais preenchida. Nunca tratar uma volta como recomeço.

- **Ficha viva por arquivo** (estado acumulado com o tempo):

```
projeto.xlsx
  05:00 → aberto, vazio
  12:00 → coluna "faturamento 12 meses" preenchida
  40:00 → adicionada amortização (CONTINUANDO, não recomeçando)
```

- **Trabalho vs Consulta:** *trabalho* = está editando; *consulta* = abriu só pra olhar um dado e volta. Ligo os dois → registro a **origem do dado** ("valor digitado às 39:00 veio do balancete consultado às 38:30"). Desvio para consulta **não** abre projeto novo — é parêntese.
- **Continuar vs recomeçar de verdade:** por padrão, voltar = continuar. Só é reset se houver **sinal explícito** (arquivo novo em branco / "vamos do zero" / mudou de cliente). Ambíguo → marco a dúvida.
- **Trilhas paralelas:** uma linha do tempo por arquivo, todas no mesmo relógio-mestre.

Limites honestos:
- Título/aba nunca visível → identidade **provável, não confirmada**.
- Passo perdido (mudança abaixo do gatilho e não narrada) → ficha fica com **buraco sinalizado** ("entre 20:00 e 25:00 pode ter havido preenchimento não capturado, confira"). Não preencho buraco com suposição.
- Valor copiado de consulta → leio o que o print mostra; não assumo que bateu com o consultado sem os dois prints confirmarem.

---

## ETAPA 3 — Classificação em três gavetas

> A âncora depende do tipo de conteúdo: no procedimento, a âncora é o **print**; no conhecimento sem tela, a âncora é a **fala**. Tudo carimbado com o tempo.

### Gaveta 1 — Procedimento → vira a **skill executora**
Tela → ação → resultado. O "como fazer".

**Tripla checagem ("aquilo é aquilo"):**
1. A palavra aponta pra tela? ("clica aqui", "essa célula").
2. O print confirma?
3. O tempo bate?

### Gaveta 2 — Conhecimento de financiamento → base da **skill decisora** (o ouro)
Raciocínio, regra do banco, enquadramento, capacidade de pagamento, lógica do FNE, "nunca faça X senão rejeita".
- **Preservado na íntegra, com o tempo.**
- **Não depende de tela** — fala valiosa de câmera nas pessoas entra igual.
- Critério de entrada = **o assunto**, não a tela.

### Gaveta 3 — Conversa fiada / a-verificar → arquivo separado, **rastreável**
Papo paralelo. **Não é lixo** — lista recuperável, **com carimbo de tempo** (para você resgatar no ponto exato).

| Vídeo/Aula | Tempo | Trecho (fiel) | Por que classifiquei como descarte |
|---|---|---|---|
| | mm:ss | | |

### Regras de classificação
- **Leitura por BLOCO, não por segundo solto** (o ensino tem ritmo):
  - *Explica → faz* (mais comum): fala dos 30s–1min **antes** explica a ação; ancoro no print da ação e puxo a fala anterior.
  - *Faz → explica*: pego a fala **depois**.
  - *Fala enquanto faz*: mesmo tempo.
  - Marcadores: "agora eu vou colocar...", "aqui a gente põe...".
- **Preenchimento campo a campo** (descrição, valor, coluna): cada um muda pouco; salva a **narração**. Nesses trechos, **baixar o gatilho** (captura mais densa).
- **Na dúvida entre conhecimento e conversa fiada → NÃO descartar** (vai pra Gaveta 2 ou "revisar").
- **Ação invisível** (mudou pouco + não narrado) → **marcar dúvida**, nunca inventar.

---

## ETAPA 4 — Estruturação (a tabela-mestra)

Monta-se a **espinha dorsal do começo ao fim**: sequência ordenada da primeira tela ao resultado final. Cada etapa carrega o "como" (professor) **e** o "porquê" (normativo) — casamento teoria ↔ prática.

**Tabela-mestra (molde oficial de captura):**

| # | Tempo | Vídeo | Arquivo | PF/PJ | Tipo | Explicou (porquê/teoria) | Fez na tela (como) | Estado do arquivo aqui | Origem do dado | Depende de | Regra/Normativo | Confiança | Pérola/Aviso |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | mm:ss | aula_14-03 | projeto.xlsx | PJ | Procedimento | "capacidade tem que caber na janela do banco" | puxou faturamento 12 meses | faturamento preenchido | — | — | (norma + versão) | Confirmado | — |
| 2 | mm:ss | aula_14-03 | projeto.xlsx | PJ | Procedimento | "agora some e dê enter" | fórmula na célula Y | soma calculada | balancete 38:30 | etapa 1 | — | Provável | "se der negativo, revisar" |

- **"Depende de"** = ordem da cadeia; **atravessa arquivos** (célula Y depende do nº vindo do balancete consultado).
- **"Regra/Normativo"** = gancho procedimento ↔ conhecimento.
- **"Confiança"** = confirmado / provável / incerto (da escala de leitura de prints).
- **"Estado do arquivo" + "Origem do dado"** = a memória do projeto sendo construído.

### Camada teoria ↔ prática (o coração)
A norma diz **o que pode**; o professor traduz em **como fazer**.
- **O passo** (jeito simples do professor) → fluência.
- **O porquê** (norma na mão) → segurança e adaptação a casos novos.

> ⚠️ **Quando o professor simplifica:** se ele "arredonda" a regra ("sempre faça assim" quando há exceção), eu aviso: *"ele simplificou; a norma tem um detalhe a mais"*.

> ⚠️ **Fonte na mão > fonte de memória:** cito capítulo/página do documento que você me deu.

---

## Como tudo isso vira skill/agente

A separação da captura **já é** o desenho da arquitetura.

| Gaveta da captura | Vira… | Alimentada por |
|---|---|---|
| Procedimento | **Skill executora** (preenche planilha em branco) | tabela-mestra: "Fez na tela" + "Depende de" + "Estado/Origem" |
| Conhecimento de financiamento | **Skill decisora** (sabe o porquê, sabe adaptar) | acervo normativo (Etapa 0) + coluna "Regra aplicada" |
| Conversa fiada | nada (recuperável, com tempo) | — |

- **"Depende de"** dá a ordem em que o agente roda (inclusive entre arquivos).
- O **acervo normativo** da Etapa 0 é a biblioteca permanente da decisora.
- A distinção **PF/PJ** pode ramificar a skill (fluxo/regra diferente por natureza do tomador).

---

## Princípios transversais (valem em todas as etapas)

1. **Carimbo de tempo em absolutamente tudo** — inclusive no descarte.
2. **Professor = fonte canônica.** Em conflito, vence o professor.
3. **Na dúvida, não descartar.**
4. **Não inventar — marcar a dúvida** e apontar o segundo pra conferir.
5. **Fonte na mão sempre vence fonte de memória.**
6. **Interpretação tem memória:** o projeto é construído; voltar ≠ recomeçar.
7. **Identidade primeiro:** PF ou PJ? qual arquivo? (ler cabeçalho/rodapé).
8. **Incerteza → pesquisar primeiro, depois sinalizar.** Números e citações sempre com selo de confiança; avisar quando norma pode estar desatualizada.

---

## Ordem de execução resumida

```
ETAPA 0  Varredura de fontes → lista de manuais/normativos (+versão) → você completa o acervo
ETAPA 1  Captura → transcrição com tempo + diarização (marcar PROFESSOR)
                  → prints na mudança (par antes/depois + extremos forçados)
ETAPA 2  Leitura dos prints → o que está (não o que imagino) + identidade (PF/PJ, cabeçalho)
                  → rastrear estado por arquivo (memória: construído, não recomeça)
                  → escala de confiança (confirmado/provável/incerto)
ETAPA 3  Classificação → 3 gavetas, leitura por bloco, tripla checagem, dúvida marcada
ETAPA 4  Estruturação → tabela-mestra (espinha + dependências entre arquivos + teoria↔prática)
SAÍDA    3 entregáveis: passo a passo executável | documento de conhecimento | descartes rastreáveis
         → semente das skills executora e decisora
```
