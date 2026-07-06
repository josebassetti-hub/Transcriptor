# Plano: Fábrica Automatizada de Projetos de Crédito Rural (BNB/FNE)

## Contexto

O usuário concluiu um curso de elaboração de projetos de crédito rural para o Banco do Nordeste (BNB/FNE) e possui todo o material no Google Drive: ~5 vídeo-aulas (.mov, 1–2,5 GB cada) onde o professor demonstra o passo a passo, a planilha macro **"Automatizador para Projetistas"** (XLSM), PDFs didáticos (Apresentação, Custos e Despesas, Capacidade de Pagamento, Evolução de Rebanho de Leite), exemplos prontos em formatos próprios (`.INVRUR`, `.CUSTEIOPECUARIO`), checklist externo do BNB, ferramenta de coordenadas geodésicas, shapefiles/KML de georreferenciamento e planilhas de apoio.

Objetivo: como projetos rurais são altamente técnicos e padronizados (ex.: espaçamento de café → nº exato de plantas/ha → produtividade provável → custos → capacidade de pagamento), construir um **sistema de agentes** que absorva a metodologia do curso e produza projetos completos automaticamente, com o usuário apenas fornecendo os dados do cliente e revisando o resultado.

O repositório `Transcriptor` já contém um ativo valioso de sessão anterior: `index.html` — simulador financeiro BNB/FNE validado (motor de cálculo de parcelas, CET, dias úteis, bônus de adimplência, XIRR) — que será reaproveitado como motor financeiro do produto final.

## Fatos verificados nesta investigação

| Item | Verificado |
|---|---|
| Conector Google Drive | Funcionando; leitura de PDF/XLSX/DOCX como texto e download base64 disponíveis, mas exigem **aprovação única do usuário** (fora do modo plano) |
| Arquivos pequenos (PDFs, XLSM, CSV, KML, exemplos) | Todos ≤ 2 MB → **baixáveis direto pelo conector** |
| Vídeos (2.mov–5.mov vistos; ~8 GB total) | **Grandes demais para o conector** (base64). Download direto bloqueado: proxy nega `drive.google.com` (403 CONNECT — política de rede do ambiente) |
| Ambiente | Python 3.11, Node 22, 4 CPUs, 15 GB RAM, ~30 GB disco livre. `ffmpeg` ausente, mas **PyPI acessível** → instalar `static-ffmpeg`, `faster-whisper`, `openpyxl`, `oletools` etc. |
| Claude lê frames? | **Sim** — Claude lê imagens nativamente. O que não faz é "assistir" vídeo direto; a solução padrão open source é: ffmpeg extrai áudio → Whisper transcreve (pt-BR, com timestamps); ffmpeg extrai frames nas mudanças de cena → Claude lê os frames e correlaciona com a transcrição |
| Repo atual | 1 commit; branch `claude/rural-credit-automation-j4fn5s`; simulador HTML funcional com autoteste |

### Como o Claude lê o Google Drive (resposta ao usuário — incluir no relatório final)
Via conector oficial (MCP): busca de arquivos, leitura de Docs/Sheets/PDFs/Office como texto, download em base64 e upload de resultados de volta ao Drive (`create_file`). Limites: chamadas exigem aprovação do usuário na primeira vez; arquivos de vídeo multi-GB não passam pelo conector — precisam de rota alternativa (abaixo).

## Decisões assumidas (a janela de perguntas fechou sem resposta — o usuário pode trocar qualquer uma a qualquer momento; nenhuma trava a Fase 0)

1. **Rota dos vídeos**: Rota A — usuário libera na política de rede do ambiente (claude.ai/code → Environment → Network) os domínios `drive.google.com`, `drive.usercontent.google.com`, `*.googleapis.com` e compartilha a pasta dos vídeos como "qualquer pessoa com o link – leitor"; eu baixo e processo na nuvem. **Fallback pronto (Rota B)**: script local de 1 clique que extrai áudio (~60 MB/h) + frames e sobe artefatos pequenos ao Drive, que eu baixo pelo conector. Instruções das duas rotas serão entregues ao final da Fase 0; a escolha só é necessária no gate da Fase 1.
2. **Primeiro tipo de projeto a validar**: Custeio pecuário (recria/engorda) — é o tipo com mais material de validação (2 exemplos prontos do professor em `.CUSTEIOPECUARIO`), o caminho mais seguro para o primeiro motor 100% conferido. Em seguida, investimento rural (café/benfeitorias, exemplo `.INVRUR` + orçamento de depósito), depois evolução de rebanho de leite. Se os primeiros clientes reais do usuário forem de outro tipo, inverte-se a ordem.
3. **Interface de uso diário**: Conversa no Claude Code (skill `/novo-projeto` + subagentes) como via principal — é a forma "agentes fazem tudo" pedida pelo usuário e a mais fácil de evoluir. Um app-formulário HTML (nos moldes do simulador já existente) fica como Fase 6 opcional, depois da validação.

## Arquitetura alvo

```
FASE DE APRENDIZADO (uma vez)
  Drive ──► Ingestão ──► Extração multi-agente ──► Base de Conhecimento
  (vídeos, planilhas,     • transcrição Whisper      knowledge/
   PDFs, exemplos)        • frames + visão Claude    • manual-metodologia/ (por módulo)
                          • dissecação XLSM/VBA      • coeficientes-tecnicos.json
                          • parse dos exemplos       • templates/ (Excel, docs)
                                                     • checklist-documental.json

FASE DE PRODUÇÃO (por cliente, para sempre)
  Dados do cliente ──► /novo-projeto (skill orquestradora)
       │
       ├── agente Entrevistador  → valida/coleta dados faltantes
       ├── agente Calculista     → coeficientes técnicos + motores Python
       ├── agente Financeiro     → motor do simulador (index.html) p/ parcelas/CET/capacidade
       ├── agente Preenchedor    → openpyxl preenche template do Automatizador + orçamentos
       ├── agente Documentalista → checklist BNB, coordenadas/KML, documentos
       └── agente Revisor        → confere contra regras do manual + golden tests
       │
       ▼
  Pacote do projeto: Excel compatível + PDFs + checklist → upload ao Drive → REVISÃO HUMANA → banco
```

## Fases de execução

### Fase 0 — Fundação (primeira sessão de execução)
1. Usuário aprova as permissões do conector Drive (leitura/download) quando solicitadas.
2. Baixar via conector **todos os arquivos não-vídeo** (~20 arquivos, todos pequenos) para `materiais/` local (fora do git; adicionar `.gitignore`).
3. Instalar toolchain Python: `static-ffmpeg`, `faster-whisper`, `openpyxl`, `oletools`, `pandas` (PyPI já acessível).
4. Dissecar o **Automatizador para Projetistas.xlsm**: abas, células de entrada, fórmulas, validações, código VBA (olevba) → `knowledge/automatizador-estrutura.md`.
5. Inspecionar `.INVRUR` / `.CUSTEIOPECUARIO` (provável formato de salvamento da própria ferramenta) e os PDFs didáticos.
6. Scaffolding do repo: `pipeline/` (scripts de ingestão), `knowledge/`, `engines/`, `templates/`, `.claude/skills/`, `CLAUDE.md` do projeto.
7. Commit + push na branch designada.

### Fase 1 — Ingestão dos vídeos (depende da decisão 1)
- **Rota A (recomendada)**: usuário ajusta a política de rede do ambiente (claude.ai/code → Environment → Network policy) para permitir `drive.google.com`, `drive.usercontent.google.com`, `*.googleapis.com` e compartilha a pasta como "qualquer pessoa com o link – leitor". Eu baixo os vídeos com gdown/curl no próprio ambiente.
- **Rota B (fallback)**: eu gero um script local (1 clique) que o usuário roda no computador dele: extrai áudio (~60 MB/h) + frames de mudança de cena, compacta e sobe ao Drive → esses artefatos pequenos eu baixo pelo conector.
- Extração: áudio 16 kHz mono (WAV/OPUS) + frames por detecção de cena (`scene>0.1`) + 1 frame/45s de segurança; dedup perceptual.

### Fase 2 — Extração de conhecimento (multi-agente, processamento em background)
1. **Transcrição**: faster-whisper (modelo small→medium, int8, pt-BR) com timestamps → `knowledge/transcricoes/videoN.md`. ~10 h de aula ≈ 2–6 h de CPU em background.
2. **Leitura de frames**: agentes de visão leem lotes de frames → "no minuto M o professor preenche a célula X da aba Y com o valor Z / acessa o site W" → `knowledge/frames/videoN-eventos.md`.
3. **Síntese (orquestração Workflow)**: agentes correlacionam transcrição + eventos de frame + estrutura do XLSM → **Manual de Metodologia** por módulo (investimento, custeio pecuário, evolução de rebanho, capacidade de pagamento, georreferenciamento, documentação, cotações) com validação cruzada contra os exemplos prontos do professor.
4. **Coeficientes técnicos** citados no curso (espaçamentos→plantas/ha, produtividades, índices zootécnicos, custos padrão) → `knowledge/coeficientes-tecnicos.json` (editável pelo usuário).
- Critério de saída: manual cobre 100% dos vídeos; cada regra cita vídeo+timestamp de origem (rastreabilidade).

### Fase 3 — Motores e geradores (o produto)
1. `engines/` em Python: cálculo de investimento (inversões/glebas), custeio pecuário, evolução de rebanho, produtividade por cultura/espaçamento, capacidade de pagamento — funções puras e testáveis.
2. Motor financeiro: portar/reusar `runSim()`/`xirr()` do `index.html` (fonte da verdade já validada contra planilha oficial BNB).
3. **Preenchedor Excel** (openpyxl): preenche o próprio template do Automatizador do professor preservando macros/fórmulas → saída compatível com o fluxo que o banco/projetista já conhece.
4. Geradores auxiliares: checklist documental BNB preenchido, planilha de coordenadas/KML, orçamentos, memorial descritivo (Markdown→PDF).
5. Upload do pacote final ao Drive via conector (`create_file`).

### Fase 4 — Validação (golden tests)
- Reproduzir **byte a byte os números** dos exemplos do professor (`Exemplo investimento rural.INVRUR`, `Exemplo recria e engorda.CUSTEIOPECUARIO`, `Exemplo com ração`, `Orçamento depósito.xlsx`) a partir apenas dos dados de entrada → diff automático.
- Suite `pytest` + autoteste no estilo do que o simulador HTML já tem.
- Só avançar para uso real quando os 3+ exemplos baterem 100%.

### Fase 5 — Operação assistida por agentes
1. `.claude/skills/novo-projeto/` — skill orquestradora: entrevista → cálculo → preenchimento → revisão → pacote no Drive.
2. `.claude/agents/` — subagentes especializados (entrevistador, calculista, preenchedor, revisor) conforme arquitetura acima.
3. `CLAUDE.md` ensina qualquer sessão futura a operar a fábrica.
4. Piloto: 1º caso real do usuário ponta a ponta, comparado manualmente.
5. Ciclo de melhoria: cada projeto revisado vira caso de teste novo.

## Salvaguardas (inegociáveis no design)
- **Revisão humana obrigatória** antes de qualquer envio ao banco — o sistema gera minutas técnicas; responsabilidade profissional (ART/CREA quando aplicável) permanece humana.
- **Sem automação de login/envio nos sistemas do BNB** — o pacote final é entregue pronto para o usuário protocolar; automatizar credenciais bancárias fica fora do escopo.
- Material do curso: uso interno para a prática profissional do usuário (não redistribuir conteúdo do professor).
- Vídeos e materiais brutos ficam fora do git (`.gitignore`); só conhecimento derivado e código são commitados.

## Verificação
1. Fase 0: `python -c "import faster_whisper, openpyxl"` OK; estrutura do XLSM documentada; commit na branch `claude/rural-credit-automation-j4fn5s`.
2. Fase 2: transcrição de 1 vídeo auditada por amostragem (usuário confere 3 trechos); eventos de frame conferidos contra o vídeo.
3. Fase 4: golden tests batendo 100% nos exemplos do professor (critério de aceite principal).
4. Fase 5: piloto real ponta a ponta gerando pacote no Drive revisado e aprovado pelo usuário.

## Estimativa honesta
- Fase 0: 1 sessão. Fases 1–2: 1–2 sessões + horas de processamento em background. Fases 3–4: 2–4 sessões (parte mais trabalhosa). Fase 5: 1–2 sessões + piloto real.
- Único gargalo fora do meu controle: a rota dos vídeos (ação do usuário na Fase 1).
