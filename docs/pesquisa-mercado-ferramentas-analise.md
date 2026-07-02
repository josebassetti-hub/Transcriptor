# Pesquisa de mercado: ferramentas e empresas de análise de mercado (Brasil + mundo)

**Objetivo:** embasar a criação de uma ferramenta SaaS de pesquisa de mercado automática, voltada principalmente a **consultorias e agências** que produzem relatórios de mercado para clientes no Brasil.

**Data da pesquisa:** 02/07/2026
**Método:** pesquisa profunda multi-agente (88 agentes: 5 ângulos de busca em paralelo, 24 fontes coletadas, 19 alegações extraídas e submetidas a verificação adversarial com 3 votos independentes cada — 16 confirmadas, 3 refutadas), complementada por buscas dirigidas para lacunas.

**Legenda de confiança:**
- ✅ **Verificado** — alegação confirmada por verificação adversarial 3-0 contra fontes primárias.
- ⚠️ **Coletado** — informação de fonte identificada (página oficial do player, review site, imprensa), mas não submetida/aprovada na verificação adversarial. Confirmar antes de usar em decisão crítica (ex.: precificação).

---

## 1. Sumário executivo

1. **O gap competitivo existe e é claro:** nenhum player global entrega dimensionamento de mercado (TAM/SAM/SOM) automatizado ancorado em fontes públicas brasileiras (CNPJ, IBGE, Bacen). Os players brasileiros que usam essas bases (Econodata, Neoway, Cortex) as usam para **prospecção B2B/vendas**, não para **gerar relatórios de market research** — o formato que consultorias e agências vendem. ✅ (gap derivado de achados verificados)
2. **A matéria-prima é gratuita e legalmente sólida:** a base completa de CNPJ da Receita Federal (todas as ~60M+ empresas do país, com CNAE, porte, sócios, localização, regime tributário) é aberta, mensal, com layout oficialmente documentado, sem custo de licenciamento (IN RFB 2.119/2022 + LAI). O IBGE e o Banco Central expõem APIs REST públicas. ✅
3. **O padrão de qualidade a replicar é a Statista Market Insights:** metodologia publicada e nomeada (ARIMA, Bass/S-Curve, ETS), até 10 anos de histórico + 5 anos de previsão, dashboard interativo com exportação em XLSX/PNG/**PPTX** (slides prontos — crítico para consultorias), atualização semestral. ✅
4. **A metodologia que o mercado espera é a triangulação:** top-down (dado agregado de fonte sindicada, afunilado) + bottom-up (preço × contagem de ICPs × volume), apresentadas juntas, com TAM/SAM/SOM e SOM em horizonte de 3–5 anos. A base CNPJ permite bottom-up com **contagem real de empresas-alvo** — algo que nem a Statista oferece para o Brasil em granularidade de empresa. ✅
5. **O piso competitivo é gratuito:** Sebrae Inteligência Setorial (centenas de relatórios infográficos por setor) e o stack Google Trends + fontes públicas. Uma ferramenta paga precisa demonstrar valor incremental em profundidade, customização por nicho, automação e triangulação citável. ⚠️/✅

---

## 2. Concorrentes no Brasil

### 2.1 Ferramentas SaaS de inteligência de mercado

| Player | O que faz | Modelo de negócio / preço | Público-alvo | Relação com a ferramenta proposta |
|---|---|---|---|---|
| **Cortex Intelligence** ⚠️ | Go-to-Market Intelligence: tamanho de mercado real, novos nichos, dimensionamento de segmentos, ICP, prospecção com IA, geomarketing | Enterprise, sob cotação (sem preço público) | Grandes empresas B2B (clientes: Visa, Itaú, Carrefour, Basf, Raízen) | Concorrente mais próximo em *sizing*, mas vendido como plataforma enterprise de vendas, não como gerador de relatórios para consultorias |
| **Neoway** (B3) ⚠️ | Big data analytics: compliance, crédito, jurídico, vendas; dados de RFB, juntas comerciais, diários oficiais | Enterprise, sob cotação | Grandes empresas (bancos, seguros, indústria) | Mesma base pública (CNPJ etc.), foco em risco/vendas — não gera relatório de mercado |
| **Econodata** ⚠️ | Prospecção B2B sobre base CNPJ: busca/segmentação de empresas, contatos, API | Assinatura SaaS por usuário (planos comerciais; equipes 10+) | Times comerciais B2B | Prova que a base CNPJ sustenta produto SaaS; foco 100% em vendas, não em research |
| **Opinion Box** ⚠️ | Pesquisa de mercado DIY com painel próprio de respondentes | Transacional: pesquisas a partir de ~R$300, sem mensalidade, resultado em até 5 dias úteis | PMEs e times de marketing/CX | Pesquisa primária (survey), não análise secundária/sizing — complementar, não concorrente direto |
| **MindMiners** ⚠️ | Plataforma de pesquisa digital (surveys com painel) | Freemium; planos ~R$99–249/mês; enterprise de ~R$600 a R$100 mil/mês por volume | PMEs a enterprise | Idem Opinion Box: pesquisa primária |
| **Emergentes com IA** (ex.: Sai by Simular, Station AI) ⚠️ | Agentes de IA que executam pesquisa end-to-end: análise SERP, scraping de concorrentes, síntese de tendências, relatório SWOT | SaaS, entrada acessível | Startups e marketing | Sinal de que a categoria "relatório automático por IA" está nascendo no Brasil, ainda sem dados estruturados BR (CNPJ/IBGE) como diferencial |

### 2.2 Casas de research e consultorias tradicionais

| Player | O que entrega | Modelo | Observações |
|---|---|---|---|
| **IEMI Inteligência de Mercado** ⚠️ | Relatórios de potencial de mercado anuais, publicações setoriais (5 anos de série: produção, consumo, varejo, comércio exterior, perfil dos grandes players), share, NPS, pricing | Venda de relatórios + projetos sob medida | 30+ anos; referência em setores industriais (moda, construção etc.); processo manual/painéis próprios |
| **IPC Maps (IPC Marketing)** ⚠️ | Índice de potencial de consumo por município/bairro, usado por varejo para expansão | Licença anual da base | Referência clássica de dimensionamento geográfico de consumo |
| **Euromonitor International** ⚠️ | Relatórios setoriais Brasil (Passport), sizing e share por categoria | Assinatura enterprise (Passport) / relatórios avulsos | O player global com melhor cobertura setorial do Brasil; caro; muito citado por consultorias |
| **NielsenIQ / Kantar** ⚠️ | Dados de varejo/painel de consumo (sell-out, share real) | Enterprise | Fonte de share "de verdade" em bens de consumo; inacessível para PME/consultoria pequena |

### 2.3 Sebrae Inteligência Setorial — o "concorrente" gratuito

⚠️ Catálogo com **centenas de produtos gratuitos** mediante cadastro (na coleta: 426 relatórios de inteligência e 198 boletins de tendências), nos setores Alimentos, Construção Civil, Moda, Petróleo e Gás, Turismo, entre outros:

- **Relatório de Inteligência (mensal):** análise aprofundada dos temas do "Mapa de Informações Estratégicas" do setor; formato PDF elaborado com **conceito de infografia**.
- **Relatório Trimestral:** aprofunda os conteúdos das "Notícias de Impacto" mais relevantes do trimestre.
- **Boletim de Tendência:** análise preditiva breve e direta, também infográfica.

Exemplo público íntegro: [Relatório de Inteligência — Cadeia Produtiva no Agronegócio (Sebrae Goiás, PDF)](https://polosebraeagro.sebrae.com.br/wp-content/uploads/2023/05/Cadeia-Produtiva-no-Agronegocio-Relatorio-de-Inteligencia-Sebrae-Goias.pdf).

**Implicação:** o Sebrae define a expectativa de formato do público brasileiro (PDF infográfico, linguagem acessível), mas os relatórios são genéricos por setor — não customizados por nicho/região/cliente e sem dados de empresa. É exatamente aí que uma ferramenta automática paga pode superar o gratuito.

---

## 3. Melhores ferramentas globais

| Ferramenta | Categoria | Anatomia/entrega | Preço público (⚠️ conferir na contratação) |
|---|---|---|---|
| **Statista Market Insights** ✅ | Sizing/dados secundários | 1.000+ mercados em 190+ países (99% do PIB mundial), inclusive páginas Brasil (ex.: Food Brazil: US$200,6 bi em 2025, CAGR 6,37%); 10 anos de histórico + 5 de previsão; dashboard + XLSX/PNG/PPTX; metodologia publicada (ARIMA, Bass, ETS); atualização semestral | Starter ~US$149/mês (cobrança anual; €199 na Europa); pacotes maiores até ~US$1.399/mês |
| **Similarweb** ⚠️ | Inteligência digital (tráfego, apps, e-commerce) | Dashboards por site/categoria; agentes de IA (Trend Analyzer, SEO Agent) que geram relatórios prontos | Starter ~US$199/mês (ou ~US$125/mês anual); tiers até ~US$542/mês; enterprise sob cotação |
| **CB Insights** ⚠️ | Inteligência de tecnologia/startups | Market maps, market sizings, industry landscapes, scores proprietários (Mosaic, Commercial Maturity, Exit Probability), assistente ChatCBI, relatórios anuais | Enterprise, ~US$1.000+/mês, sob cotação |
| **AlphaSense** ⚠️ | Research com IA sobre documentos (filings, transcripts, broker research) | Busca semântica + sumarização generativa sobre conteúdo licenciado | Enterprise, sob cotação |
| **Crunchbase / PitchBook** ⚠️ | Dados de empresas/investimentos | Perfis, rodadas, comparáveis | Crunchbase acessível; PitchBook enterprise |
| **Osum** ⚠️ | **Relatório automático por IA** (análogo mais próximo do produto proposto) | A partir de uma URL/produto, gera em segundos: pesquisa competitiva, SWOT, buyer personas, oportunidades de crescimento | SaaS com trial de 7 dias |
| **SparkToro** ⚠️ | Audience intelligence | Perfil de audiência (o que segue, lê, ouve) | SaaS acessível |
| **Exploding Topics** ⚠️ | Detecção de tendências | Séries de crescimento de tópicos emergentes | SaaS acessível |
| **Perplexity / ChatGPT deep research** ⚠️ | Research generalista com IA | Scan rápido de fontes com citações | Assinatura ~US$20/mês |
| **Gapscout** ⚠️ | Análise de reviews (gaps de mercado) | Mineração de avaliações de concorrentes | SaaS |

✅ **Como o mercado se segmenta por caso de uso** (verificado 3-0): dados secundários/sizing (Statista, Grand View Research, Similarweb), surveys (SurveyMonkey, Qualtrics), pesquisa primária/painéis (Quantilope, Suzy), audiência (SparkToro), scans rápidos com IA (Perplexity). Compradores avaliam ferramentas em 5 dimensões: fit primário vs. secundário, capacidades de IA, utilidade do free tier, profundidade de integrações (CRM, Slack, BI) e ratings G2/Capterra/Product Hunt.

❌ **Refutado na verificação (não usar):** os preços "Statista US$79/mês, Similarweb US$149/mês, SurveyMonkey US$25/mês" que circulam em blogs de comparação estão **desatualizados** (refutados 0-3; valores corretos aproximados na tabela acima, apurados em Vendr/páginas oficiais em 2026).

---

## 4. Anatomia dos relatórios: a estrutura padrão do mercado

Estrutura canônica consolidada a partir de: amostras públicas reais da **Mordor Intelligence** (Global Dairy Market, Drones Market), metodologia publicada da **Grand View Research**, metodologia da **Statista** e frameworks de consultoria (Slideworks, ex-McKinsey/BCG). ⚠️ (fontes identificadas; estrutura consistente entre todas)

1. **Introdução e escopo**
   - Premissas do estudo (*study assumptions*), definição do mercado, escopo (geografia, segmentos, período), moeda e ano-base.
2. **Metodologia de pesquisa**
   - Fontes primárias e secundárias usadas, abordagem de sizing (top-down/bottom-up/combinada), modelo de previsão, triangulação e validação.
3. **Sumário executivo**
   - Tamanho atual e projetado, CAGR, 3–5 destaques, principais players. Uma página, muito visual.
4. **Tamanho de mercado e previsão**
   - Série histórica + previsão (padrão do setor: 5 anos ✅), TAM/SAM/SOM, CAGR por segmento.
5. **Dinâmica de mercado**
   - Drivers, restrições (*restraints*), oportunidades; tendências; fatores regulatórios; análise da cadeia de valor.
6. **Atratividade da indústria — 5 Forças de Porter**
   - Poder de fornecedores/compradores, ameaça de entrantes/substitutos, rivalidade.
7. **Segmentação**
   - Por produto/serviço, canal, geografia (no Brasil: UF/município), perfil de cliente — cada segmento com tamanho e crescimento.
8. **Cenário competitivo**
   - Market share (quando disponível), matriz de posicionamento/market map, perfis dos principais players (receita, portfólio, movimentos recentes, M&A), SWOT dos líderes.
9. **Perfis de consumidor/persona** (relatórios voltados a marketing — ex.: Osum inclui buyer personas)
10. **Previsões e cenários**
    - Cenários (base/otimista/pessimista), premissas explícitas dos modelos.
11. **Apêndice**
    - Tabelas completas, glossário, bibliografia/fontes citadas.

**Metodologia de sizing esperada** ✅ (verificado 3-0):
- **Top-down:** parte de dado agregado de fonte sindicada (Statista, Gartner, Euromonitor; no Brasil: IBGE, associações setoriais) e afunila até a fatia relevante. Rápido, porém propenso a superestimação otimista.
- **Bottom-up:** constrói de unit economics — preço médio × contagem de clientes-alvo (ICP) × volume/frequência de compra. Mais lento, porém mais defensável perante investidores.
- **Triangulação:** os melhores materiais apresentam **ambos**, e a convergência entre eles (~20%) é usada como sinal de confiabilidade. TAM = todos que poderiam comprar; SAM = fatia atendível dado geografia/modelo; **SOM = capturável em 3–5 anos**.
- **Modelos de previsão nomeados** (padrão Statista ✅): ARIMA, S-Curve/Bass Diffusion (adoção de tecnologia), ETS (mercados de crescimento estável).

---

## 5. Referências/fontes usadas em cada tipo de análise

### 5.1 O que os players globais citam (por seção)

| Seção do relatório | Fontes tipicamente usadas/citadas |
|---|---|
| Tamanho de mercado (top-down) | Bases sindicadas (Statista, Euromonitor, Gartner/IDC), estatísticas governamentais, Banco Mundial/OMS/FMI, associações setoriais ⚠️ |
| Tamanho de mercado (bottom-up) | Demonstrações financeiras/annual reports das empresas, bases pagas de firmografia (ex.: HG Insights para technographics), contagem de empresas-alvo ⚠️ |
| Validação/triangulação | Entrevistas primárias com executivos e especialistas (KoLs), broker/analyst reports comprados, regressão multivariada (metodologia Grand View Research) ⚠️ |
| Concorrência/share | Filings públicos, imprensa especializada, dados de painel (Nielsen/Kantar), scraping de presença digital ⚠️ |
| Tendências | Google Trends, dados de tráfego (Similarweb), patentes, notícias, redes sociais ⚠️ |
| Comportamento do consumidor | Surveys próprios (Statista Consumer Insights, painéis), POF/pesquisas oficiais ⚠️ |

### 5.2 Fontes brasileiras para automatizar cada análise (o mapa para o produto)

| Análise | Fonte BR | Acesso | Uso na ferramenta |
|---|---|---|---|
| **Contagem de empresas por setor/porte/região** (bottom-up sizing, análise competitiva) | **Dados abertos CNPJ — Receita Federal** ✅ | Dumps mensais gratuitos em [dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj) e [dadosabertos.rfb.gov.br/CNPJ](https://dadosabertos.rfb.gov.br/CNPJ/); layout oficial ([cnpj-metadados.pdf](https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf)); sem licenciamento (IN RFB 2.119/2022 + LAI). Volume: já eram ~17 GB descompactados em 2021 — ETL real, viável com Python+PostgreSQL (pipeline de referência: [aphonsoar/Receita_Federal…CNPJ](https://github.com/aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ/)) | Núcleo do produto: contagem real de ICPs por CNAE × município × porte × idade × regime (Simples). É a mesma base sobre a qual Econodata/Neoway operam ✅ |
| **Demografia, renda, consumo, produção e serviços** (TAM top-down, segmentação) | **IBGE — API de agregados v3 / SIDRA** (PNAD Contínua, POF, PIA, PAS, PAC, Censo, PIB municipal) ⚠️ | API REST pública e documentada: [servicodados.ibge.gov.br/api/docs/agregados](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3); granularidade por UF/município | Dimensionamento top-down por setor e região; perfis de consumo (POF) |
| **Contexto macroeconômico e previsões** | **Banco Central — API SGS** ⚠️ | JSON/CSV sem autenticação: `api.bcb.gov.br/dados/serie/bcdata.sgs.{código}` ([dadosabertos.bcb.gov.br](https://dadosabertos.bcb.gov.br/)); limite de 10 anos por requisição; lib [python-bcb](https://wilsonfreitas.github.io/python-bcb/sgs.html) | Seção "cenário macro" automática (Selic, câmbio, crédito, atividade) |
| **Emprego e massa salarial por setor/município** (proxy de tamanho e crescimento setorial) | **RAIS / Novo CAGED** ⚠️ | Microdados públicos; acesso tratado via **[Base dos Dados](https://basedosdados.org)** (BigQuery/SQL + pacotes Python/R) — que também serve CNPJ, PNAD etc. já padronizados | Crescimento setorial regional, salário médio (proxy de pricing de mão de obra), sazonalidade de contratação |
| **Demanda/tendências** | **Google Trends** ⚠️ | Gratuito (API não oficial) | Curvas de interesse por nicho/região |
| **Dados setoriais específicos** | **Associações setoriais** (ABRAS, ABIA, Abicalçados, ABIMAQ etc.), **Comex Stat** (exportação/importação), **ANVISA/ANS/ANATEL/BCB** (setores regulados) ⚠️ | Relatórios anuais públicos; Comex Stat tem dados abertos | Benchmarks de faturamento setorial, comércio exterior, dados regulatórios |
| **Consumo potencial por geografia** | IPC Maps (pago) ⚠️ | Licença anual | Alternativa: reconstruir com POF + PNAD + Censo (gratuito) |
| ⚠️ **Atenção** | **Conecta gov.br** cataloga APIs federais, mas várias (ex.: Consulta CNPJ online) são **restritas a órgãos públicos**; acesso privado em tempo real é pago via Serpro/Dataprev — por isso o caminho certo é o **dump mensal aberto** | | |

---

## 6. Como os players apresentam os dados

### 6.1 Formatos de entrega por player

| Player | Formato principal | Detalhe |
|---|---|---|
| Statista Market Insights ✅ | **Dashboard interativo + exports XLSX / PNG / PPTX** (e PDF) | Gráficos comutáveis (barra/linha/tabela), comparação entre países, slides prontos e diagramas editáveis; metodologia e cadência publicadas |
| Mordor / Grand View / Euromonitor ⚠️ | **PDF longo (100–300 pág.) + planilha de dados** | TOC padronizado (seção 4); amostras públicas usadas como isca comercial |
| CB Insights ⚠️ | **Plataforma com visualizações pré-construídas** | Market maps, market sizings, industry landscapes, gráficos de tendência/M&A, dashboards customizáveis, assistente de IA (ChatCBI) |
| Similarweb ⚠️ | Dashboard web + relatórios gerados por agentes de IA | Métricas digitais contínuas, não relatório estático |
| Sebrae Inteligência Setorial ⚠️ | **PDF infográfico curto** | Mensal/trimestral, linguagem acessível, muito visual |
| Osum ⚠️ | **Relatório web gerado por IA em segundos** | Seções navegáveis: SWOT, personas, tendências, oportunidades |

### 6.2 Visualizações típicas por seção (padrão consultoria — Slideworks/McKinsey/BCG ⚠️)

- **TAM/SAM/SOM:** funil, círculos concêntricos ou waterfall.
- **Crescimento:** série histórica em barras/linha com previsão tracejada + CAGR anotado no gráfico.
- **Segmentação:** barras empilhadas (share por segmento) e mapa coroplético (por UF/município — especialmente relevante no Brasil).
- **Concorrência:** market map (agrupamento por categoria), matriz 2×2 de posicionamento, tabela de perfis, radar/aranha para comparações multi-critério.
- **Porter:** diagrama de 5 forças com intensidade (baixa/média/alta) codificada por cor.
- **SWOT:** matriz 2×2 clássica.
- **Sumário executivo:** "painel de KPIs" — 4 a 6 números grandes (tamanho, CAGR, nº de players, ticket médio).

**Padrão de mercado consolidado:** dashboard interativo para explorar + **PPTX/PDF prontos para apresentar ao cliente final**. Para consultorias/agências (que revendem o relatório), a exportação em slides editáveis e possibilidade de white-label é o atributo decisivo. ✅ (formato Statista verificado; inferência sobre white-label)

---

## 7. Síntese competitiva: gaps e recomendações

### 7.1 Mapa de posicionamento

| | Gera relatório completo | Dados BR granulares (empresa) | Automático/IA | Acessível p/ consultorias | Metodologia transparente |
|---|---|---|---|---|---|
| Statista | parcial (dashboard) | não (só agregado) | parcial | médio (US$149+/mês) | **sim** ✅ |
| Mordor/GVR/Euromonitor | **sim** (PDF) | não | não (analistas) | não (US$3–8k/relatório típico ⚠️) | sim |
| CB Insights/AlphaSense | parcial | não | sim | não (US$1k+/mês ⚠️) | parcial |
| Osum/Perplexity | sim (raso) | não | **sim** | **sim** | não |
| Cortex/Neoway/Econodata | não (plataforma de vendas) | **sim** | parcial | não (enterprise) | não |
| Opinion Box/MindMiners | não (survey) | n/a | parcial | sim | n/a |
| Sebrae | sim (genérico) | não | não | gratuito | parcial |
| **Ferramenta proposta** | **sim** | **sim (CNPJ+IBGE)** | **sim** | **sim** | **sim** |

### 7.2 Gaps identificados

1. **Ninguém cruza os dois mundos:** os geradores automáticos (Osum, Perplexity) não têm dados estruturados do Brasil; os donos dos dados BR (Cortex, Neoway, Econodata) não geram relatórios de research; as casas tradicionais (IEMI, Euromonitor) são caras e lentas; o Sebrae é gratuito mas genérico. ✅ (derivado de achados verificados)
2. **Bottom-up real é inédito como produto self-service:** com a base CNPJ, dá para contar *exatamente* quantas empresas-alvo existem por CNAE × município × porte — bottom-up com censo, não amostra. Statista não tem isso para o Brasil. ✅
3. **Citabilidade:** consultorias precisam defender números perante clientes. Relatórios de IA generalista não citam fontes oficiais verificáveis; um relatório com cada número linkado à fonte pública (IBGE tabela X, CNPJ extração de mês Y) é defensável de forma única.

### 7.3 Recomendações para o produto (derivadas dos achados ✅/⚠️)

1. **Camada fundacional de dados:** ETL mensal da base CNPJ (usar Base dos Dados/BigQuery como atalho inicial e pipeline próprio depois) + conectores para APIs do IBGE (agregados v3) e Bacen (SGS). Orçar infraestrutura: a base CNPJ já passava de 17 GB descompactados em 2021 e cresceu desde então. ✅
2. **Anatomia do relatório gerado** = a estrutura canônica da seção 4, com: TAM/SAM/SOM em **dupla metodologia explicitada e triangulada** (top-down IBGE/associações + bottom-up CNPJ), histórico + previsão de 5 anos com **modelos nomeados** (ARIMA/ETS), SOM em 3–5 anos, Porter, segmentação com mapa por UF/município, cenário competitivo com contagem e perfis de players locais.
3. **Formato de entrega no padrão da categoria:** dashboard interativo + exportação **PPTX editável, XLSX e PDF**, com **white-label** (logo da consultoria) — o atributo que transforma a ferramenta em motor de produção das agências, não só em fonte de consulta. ✅ (formato) / ⚠️ (white-label como diferencial — validar com clientes)
4. **Publicar a metodologia** (página pública, como a Statista) e a cadência de atualização (mensal, ancorada na extração do CNPJ) — transparência metodológica é fator de confiança comprovado no benchmark. ✅
5. **Cada número com fonte citada e linkada** (tabela SIDRA, série SGS, extração CNPJ do mês) — diferencial de defensabilidade contra IA generalista e contra o piso gratuito.
6. **Posicionamento de preço:** entre o gratuito (Sebrae) e o enterprise (Cortex/Neoway, sob cotação; globais US$149–1.000+/mês). Espaço claro para um tier de consultoria/agência com preço por relatório ou assinatura mensal em reais, abaixo do custo de 1 dia de analista.
7. **Onde não competir agora:** pesquisa primária (Opinion Box/MindMiners já resolvem; integrar depois via parceria), dados de painel de varejo (Nielsen/Kantar) e share "real" de bens de consumo — usar proxies públicos e declarar a limitação.

---

## 8. Limitações desta pesquisa e questões abertas

A verificação adversarial cobriu com alta confiança: benchmark Statista, viabilidade jurídica/técnica da base CNPJ, metodologia de sizing e a taxonomia global de ferramentas. **Não foram verificados adversarialmente** (permanecem ⚠️): modelo de negócio/preços detalhados dos players brasileiros (páginas oficiais e reviews bloquearam fetch direto — 403), anatomia interna dos relatórios de CB Insights/AlphaSense/Osum, e o uso de fontes IBGE/RAIS/Bacen pelos players. Também foram **refutados** e excluídos: preços antigos de blog (Statista US$79/mês etc.), o dado "Carta 2025: rounds fecham 40% mais rápido" e a contagem de "9 tabelas" do pipeline CNPJ (são 10 no total, 4 principais + referência).

Questões abertas que valem pesquisa de campo (não de mesa):
1. Algum player BR já gera relatório automatizado de sizing (vs. prospecção/survey)? Monitorar Cortex e os emergentes de IA.
2. Como consultorias/agências brasileiras compram research hoje (relatório avulso vs. assinatura, ticket médio, aceitação de white-label)? → entrevistas com 10–15 consultorias.
3. Granularidade/licença exata de cada pesquisa do IBGE para uso comercial derivado (uso é livre com citação, mas validar caso a caso).
4. Pricing 2026 verificado dos players globais direto nas páginas de contratação (valores mudam com frequência; blogs estão sistematicamente desatualizados — comprovado pela refutação).

---

## 9. Principais fontes

**Verificadas (primárias):**
- Statista Market Insights — [getting started](https://www.statista.com/getting-started/insights-market-insights) · [metodologia](https://www.statista.com/outlook/methodology) · [PDF de metodologia](https://cdn.statcdn.com/static/img/outlook/methodology/methodology-en.pdf)
- Dados abertos CNPJ — [dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj) · [layout oficial RFB](https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf) · [dadosabertos.rfb.gov.br/CNPJ](https://dadosabertos.rfb.gov.br/CNPJ/) · [pipeline ETL de referência](https://github.com/aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ/)
- Metodologia de sizing — [Waveup: top-down vs bottom-up](https://waveup.com/blog/top-down-and-bottom-up-market-size-calculation/) · [Waveup: top 14 market research software 2026](https://waveup.com/blog/top-12-market-research-software/) (blog; claims metodológicos verificados 3-0, claims de preço refutados)

**Coletadas (⚠️):**
- Brasil: [Cortex Intelligence](https://www.cortex-intelligence.com/) · [Neoway (Capterra)](https://www.capterra.com/p/192359/Neoway-Platform/) · [Econodata (Capterra)](https://www.capterra.com/p/191380/Econodata/) · [Opinion Box](https://www.opinionbox.com/plataforma-de-pesquisa/) · [MindMiners](https://mindminers.com/plans) · [Sebrae Inteligência Setorial](https://sebraeinteligenciasetorial.com.br/produtos) · [exemplo de relatório Sebrae (PDF)](https://polosebraeagro.sebrae.com.br/wp-content/uploads/2023/05/Cadeia-Produtiva-no-Agronegocio-Relatorio-de-Inteligencia-Sebrae-Goias.pdf) · [IEMI](https://iemi.com.br/) · [IEMI publicações setoriais](https://iemi.com.br/publicacoes-setoriais/)
- Globais: [CB Insights — visualizações](https://www.cbinsights.com/what-we-offer/market-analytics-and-visualizations/) · [AlphaSense vs CB Insights](https://www.alpha-sense.com/compare/cb-insights-alternatives/) · [Osum](https://osum.com/) · [Similarweb packages](https://www.similarweb.com/packages/marketing/) · [Preuve: 17 tools com preços 2026](https://preuve.ai/best-market-research-tools-2026) · [HBR: AI tools transforming market research](https://hbr.org/2025/11/the-ai-tools-that-are-transforming-market-research)
- Anatomia de relatório: [amostra Mordor — Global Dairy (Scribd)](https://www.scribd.com/document/517117746/Sample-Global-Dairy-Market-2020-2025-Mordor-Intelligence) · [amostra Mordor — Drones (Scribd)](https://www.scribd.com/document/461483916/Sample-Drones-Market-2019-2024-Mordor-Intelligence-pdf) · [metodologia Grand View Research](https://www.grandviewresearch.com/info/research-methodology) · [Slideworks: market analysis framework](https://slideworks.io/resources/how-to-write-a-market-analysis-framework-template) · [Slideworks: TAM/SAM/SOM slides](https://slideworks.io/resources/market-sizing-slides-tam-sam-som-examples) · [HG Insights: market sizing guide](https://hginsights.com/blog/market-sizing-the-complete-guide-to-calculating-tam-sam-som-and-building-a-data-driven-growth-strategy/)
- Fontes de dados BR: [API agregados IBGE v3](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3) · [Dados abertos Bacen (SGS)](https://dadosabertos.bcb.gov.br/) · [python-bcb](https://wilsonfreitas.github.io/python-bcb/sgs.html) · [Base dos Dados (BigQuery)](https://basedosdados.org) · [Conecta gov.br — catálogo de APIs](https://www.gov.br/conecta/catalogo/)
