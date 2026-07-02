# Especificação de produto/MVP — Ferramenta de pesquisa de mercado automática

**Base:** este documento transforma as recomendações da [pesquisa competitiva](./pesquisa-mercado-ferramentas-analise.md) (seção 7) em especificação executável. Onde um dado vem da pesquisa verificada, está referenciado; onde é hipótese de produto a validar, está marcado como **[hipótese]**.

**Backend definido:** Supabase (Postgres, Auth, Edge Functions, Storage).

---

## 1. Visão e posicionamento

**Proposta de valor:** gerar, em minutos, um relatório completo de análise de mercado para qualquer nicho brasileiro — com tamanho de mercado calculado por dupla metodologia (top-down IBGE + bottom-up com censo real de empresas da base CNPJ), concorrência mapeada, cada número linkado à fonte pública oficial, e exportação em PPTX/PDF pronta para a consultoria apresentar ao cliente com a marca dela.

**Posicionamento contra os 4 grupos de concorrentes** (mapa completo na [pesquisa, seção 7.1](./pesquisa-mercado-ferramentas-analise.md#71-mapa-de-posicionamento)):

| Contra | Nossa resposta |
|---|---|
| **Gratuito (Sebrae, Google Trends)** | Customização por nicho/região/cliente e profundidade de dados (empresa a empresa), que o relatório setorial genérico não tem |
| **IA generalista (Osum, Perplexity, ChatGPT)** | Dados estruturados brasileiros e citabilidade: números que a consultoria consegue defender perante o cliente |
| **Enterprise BR (Cortex, Neoway, Econodata)** | Produto é o *relatório de research*, não plataforma de vendas; preço acessível e self-service, sem contrato enterprise |
| **Casas tradicionais (IEMI, Euromonitor, Mordor)** | Velocidade (minutos vs. semanas) e preço (fração do custo de um relatório avulso) |

**Diferenciais defensáveis** (derivados dos gaps verificados na pesquisa):
1. **Bottom-up com censo, não amostra:** contagem real de empresas-alvo por CNAE × município × porte a partir da base aberta de CNPJ — nem a Statista oferece isso para o Brasil.
2. **Todo número com fonte citada e linkada** (tabela SIDRA, série SGS, extração CNPJ do mês) — defensabilidade única contra IA generalista.
3. **Exportação PPTX white-label** — a ferramenta vira motor de produção da consultoria, não só fonte de consulta.

## 2. Personas e casos de uso

| Persona | Contexto | Job-to-be-done | Disposição a pagar [hipótese] |
|---|---|---|---|
| **Consultoria boutique** (2–20 pessoas) | Vende diagnósticos e planejamento estratégico; a seção de mercado consome 2–5 dias de analista por projeto | "Montar a seção de mercado de um diagnóstico em 1 hora, com números defensáveis, no template da minha marca" | Assinatura mensal ou pacote de relatórios |
| **Agência de marketing** | Precisa de contexto de mercado para propostas comerciais e planejamentos anuais de clientes | "Impressionar o prospect na proposta com dados de mercado que a concorrência não traz" | Por relatório, uso esporádico |
| **Consultor autônomo / contador consultivo** | Atende PMEs; não tem acesso a Euromonitor/Statista | "Entregar um estudo de viabilidade profissional sem pagar milhares de reais por base de dados" | Ticket baixo, por relatório |

Usuário secundário (não foco do MVP): empreendedor validando negócio — atendido como efeito colateral do self-service.

## 3. O relatório gerado (produto núcleo)

**Input do usuário (formulário de geração):**
- Nicho: busca em linguagem natural mapeada para 1+ códigos **CNAE** (com sugestão automática e ajuste manual);
- Região: Brasil / UF(s) / município(s);
- Parâmetros de sizing: ticket médio anual estimado do cliente-alvo (com faixas sugeridas) e definição do ICP (porte, idade da empresa, regime tributário) — para o bottom-up;
- Opcional: nome do cliente final e logo (white-label básico).

**Seções do relatório (anatomia canônica da [pesquisa, seção 4](./pesquisa-mercado-ferramentas-analise.md#4-anatomia-dos-relatórios-a-estrutura-padrão-do-mercado)), com dados, fonte, cálculo e visualização:**

| # | Seção | Dados e fonte exata | Cálculo/geração | Visualização |
|---|---|---|---|---|
| 1 | Sumário executivo | Agregado das seções seguintes | Redação por LLM sobre os números calculados | Painel de 4–6 KPIs (tamanho, CAGR, nº de empresas, ticket) |
| 2 | Escopo e metodologia | Estático + parâmetros do usuário | Template com CNAEs, região, mês da extração CNPJ, tabelas IBGE usadas | Texto + tabela de fontes |
| 3 | Contexto macroeconômico | Bacen **API SGS** (Selic, IPCA, câmbio, atividade); séries com código citado | Últimos 5 anos + leitura por LLM | Linhas de série temporal |
| 4 | Tamanho de mercado — top-down | IBGE **API agregados v3/SIDRA**: receita/valor da produção do setor (PAS/PIA/PAC), população e renda (PNAD/POF) por região | TAM = agregado setorial ajustado à região; SAM = filtro de segmento/região; citação da tabela SIDRA | Funil TAM/SAM/SOM |
| 5 | Tamanho de mercado — bottom-up | **Agregados CNPJ**: contagem de empresas ativas por CNAE × município × porte × idade | SOM/SAM = nº de ICPs × ticket médio × taxa de captura (cenários 3–5 anos) | Waterfall + tabela de premissas |
| 6 | Triangulação e cenários | Seções 4 e 5 | Comparação top-down vs bottom-up, divergência % comentada (padrão: convergência ~20% como sinal de confiabilidade), cenários base/otimista/pessimista | Barras comparativas |
| 7 | Dinâmica do mercado | Novo CAGED (saldo de empregos do setor), CNPJ (aberturas × fechamentos por ano), Google Trends (interesse) | Drivers e restrições redigidos por LLM **somente sobre os dados coletados** | Linhas de tendência (aberturas/fechamentos, empregos, buscas) |
| 8 | Concorrência | CNPJ: empresas do CNAE na região (quantidade por porte, idade média, concentração geográfica, entrantes recentes) | Densidade competitiva, ranking de municípios, 5 Forças qualitativa por LLM com os indicadores como evidência | Mapa coroplético por município + matriz/tabela |
| 9 | Segmentação | CNPJ (subclasses CNAE, porte) + IBGE (segmentos da pesquisa setorial) | Tamanho por segmento | Barras empilhadas |
| 10 | Riscos, limitações e fontes | Estático + gerado | Limitações declaradas (ex.: CNPJ ativo ≠ operante; informalidade não capturada) + bibliografia com links | Lista |

**Regra de ouro da geração por LLM:** o modelo redige e interpreta, **nunca inventa número**. Todo valor citado no texto vem do JSON de dados calculados, com marcador de fonte; a renderização valida que cada número do texto existe no JSON (guard-rail anti-alucinação).

## 4. Arquitetura de dados

**Decisão-chave: não carregar a base CNPJ bruta no Supabase.** A base bruta (>20 GB descompactados, crescendo) fica fora; o Supabase guarda **agregados pré-computados**, que são pequenos e respondem todas as consultas do relatório.

```
[Fontes públicas]                [ETL mensal - fora do Supabase]        [Supabase Postgres]
CNPJ dumps (RFB) ──────────────► staging (DuckDB/Polars ou             ► agg_empresas
                                  Base dos Dados/BigQuery no início)      (cnae, municipio, porte,
                                                                           idade_faixa, regime,
                                                                           ano_mes, qtd, aberturas,
                                                                           fechamentos)
IBGE API agregados v3 ─────────► runtime com cache ────────────────────► cache_ibge (json, ttl)
Bacen API SGS ─────────────────► runtime com cache ────────────────────► cache_sgs (json, ttl)
Google Trends ─────────────────► runtime (fase 2, API não oficial)
```

- **ETL CNPJ:** job mensal (fora do Supabase — ex.: GitHub Actions com runner maior, ou VM barata) que baixa os dumps, processa com DuckDB/Polars e grava só os agregados no Postgres. **Atalho para o MVP:** consultar a [Base dos Dados](https://basedosdados.org) (BigQuery) para gerar os agregados sem construir o pipeline de download — trocar pelo pipeline próprio quando o custo/controle justificar.
- **Estimativa de tamanho dos agregados:** CNAE subclasse (~1.300) × municípios (~5.570) × porte (4) × faixas de idade (5) — esparso na prática; ordem de poucos milhões de linhas ≈ poucos GB no Postgres. Cabe no Supabase com folga.
- **IBGE/Bacen em runtime:** as APIs são públicas e sem autenticação; consultar na hora da geração com cache em tabela (`ttl` de semanas — dados mudam devagar). Pré-mapear por setor-piloto quais tabelas SIDRA alimentam o top-down (curadoria manual inicial, 1 vez por setor).
- **Versionamento:** cada relatório grava o `ano_mes` da extração CNPJ e os IDs das tabelas/séries usadas — reprodutibilidade e citação exata.

## 5. Arquitetura de aplicação (Supabase)

| Componente | Uso |
|---|---|
| **Auth** | Contas e times (consultoria com múltiplos usuários); RLS por organização |
| **Postgres** | `orgs`, `users`, `reports` (parâmetros, status, versão dos dados), `report_sections` (JSON de dados + texto gerado), `agg_empresas`, caches IBGE/SGS, `cnae_map` (busca de nicho → CNAE) |
| **Edge Functions** | Orquestração da geração em etapas: `collect` (consultas agregados + APIs) → `compute` (TAM/SAM/SOM, indicadores) → `write` (LLM redige seção a seção com citações) → `render` (PDF/PPTX) — cada etapa atualiza o status do report (fila simples via tabela + `pg_cron`/trigger; evita estourar timeout de function única) |
| **Storage** | PDFs e PPTX gerados, logos white-label |
| **Realtime** | Progresso da geração na UI ("coletando dados… calculando… redigindo…") |

- **Frontend:** Next.js (Vercel) com o cliente Supabase; gráficos com Recharts/ECharts.
- **Render:** PDF via HTML→PDF (ex.: Playwright/Chromium ou serviço tipo react-pdf); PPTX via `pptxgenjs` com template de marca.
- **LLM:** Claude API para redação das seções (modelo econômico por seção; ver risco de custo na seção 9). Prompt recebe o JSON de dados + instruções de citação; saída validada pelo guard-rail da seção 3.
- **Sem servidor próprio no MVP** além do job de ETL mensal.

## 6. Escopo do MVP (fase 1)

**Dentro:**
- 3–5 setores-piloto **[hipótese a escolher com as entrevistas — candidatos: alimentação fora do lar, beleza/estética, saúde (clínicas), educação, serviços de TI]**;
- Geração de 1 relatório por vez, com as 10 seções da seção 3 (versões enxutas);
- Top-down IBGE + bottom-up CNPJ com triangulação;
- Export PDF + PPTX básico (template único, logo do cliente);
- Página pública de metodologia (padrão Statista — fator de confiança verificado na pesquisa).

**Fora (explicitamente):**
- Pesquisa primária/surveys (Opinion Box/MindMiners já resolvem; possível parceria futura);
- Share real de varejo (Nielsen/Kantar) — declarar limitação;
- Dashboard interativo completo (MVP entrega documento; dashboard é v1);
- White-label avançado (fontes, cores, templates múltiplos);
- Todos os CNAEs liberados (curadoria por setor-piloto primeiro);
- Monitoramento contínuo/alertas.

## 7. Roadmap

| Fase | Conteúdo | Critério de saída |
|---|---|---|
| **MVP (0→3 meses)** | Escopo da seção 6 + **entrevistas com 10–15 consultorias** (respondendo às questões abertas da pesquisa: como compram research, ticket, aceitação de white-label) | 10 relatórios reais gerados para usuários externos; 3+ dispostos a pagar |
| **v1 (3→9 meses)** | Todos os CNAEs, white-label completo, dashboard interativo, mais fontes (Comex Stat, associações setoriais), cenários editáveis pelo usuário | Receita recorrente; retenção 3 meses > 60% [hipótese] |
| **v2 (9+ meses)** | Monitoramento contínuo do nicho (alertas mensais pós-extração CNPJ), API para integração, multi-idioma (relatórios para investidor estrangeiro) | Expansão de receita por conta |

## 8. Modelo de negócio e pricing [hipóteses a validar nas entrevistas]

Âncoras da pesquisa: piso gratuito (Sebrae), globais US$149–1.000+/mês, relatório avulso de casa tradicional US$3–8k, e o custo real que substituímos: **dias de analista da própria consultoria**.

| Plano | Preço [hipótese] | Inclui |
|---|---|---|
| Avulso | R$297–497/relatório | 1 relatório completo, PDF + PPTX |
| Profissional | R$497–997/mês | 5–10 relatórios/mês, white-label básico |
| Agência | R$1.500–2.500/mês | Ilimitado justo, times, white-label completo (v1) |

Racional: abaixo de 1 dia de analista por relatório; ordem de grandeza acima de IA generalista (US$20/mês) justificada pela citabilidade e dados BR.

## 9. Métricas de sucesso e riscos

**Métricas:** ativação (% de cadastros que geram o 1º relatório em 48h), relatórios/conta/mês, tempo médio de geração, taxa de export PPTX (proxy de uso em cliente final), retenção M3, NPS das consultorias-piloto.

| Risco | Mitigação |
|---|---|
| **CNPJ ativo ≠ empresa operante** (superestima o bottom-up) | Filtros por situação cadastral + idade + regime; declarar premissas na seção de limitações; calibrar com dados de emprego (CAGED) |
| Informalidade não capturada (setores como beleza, alimentação) | Fator de ajuste por setor citando IBGE/Sebrae; declarar limitação |
| Instabilidade/limites das APIs IBGE e dos dumps RFB (atrasos, mudanças de layout já ocorreram) | Cache agressivo, ETL tolerante a atraso, monitoramento do layout; relatório usa última versão disponível com data explícita |
| Custo de LLM por relatório | Redigir por seção com modelo econômico; dados pesados ficam fora do prompt (só JSON agregado); medir custo/relatório como métrica interna |
| Concorrente com distribuição (Sebrae, Cortex ou player de IA) lança similar | Velocidade de ciclo + profundidade de curadoria por setor + marca junto a consultorias (comunidade/conteúdo) |
| Uso comercial de dados públicos | Uso é livre com citação (LAI/dados abertos — verificado na pesquisa para CNPJ); validar caso a caso as notas de rodapé das pesquisas IBGE |

---

*Documento derivado da pesquisa em `docs/pesquisa-mercado-ferramentas-analise.md` (02/07/2026). Hipóteses marcadas devem ser validadas nas entrevistas do MVP antes de virarem compromisso de produto.*
