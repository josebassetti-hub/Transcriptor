# Plano para fechar as 4 lacunas do estudo (benchmark Brasil + internacional)

**Pergunta:** como plataformas brasileiras e internacionais resolvem as 4 limitações declaradas
no relatório-piloto — e como fechá-las na nossa ferramenta da forma correta.

**Método:** pesquisa multi-agente (4 frentes × busca + aprofundamento com fontes primárias),
com verificação adversarial de afirmações-chave (2 votos independentes cada).
**Legenda:** ✅ afirmação verificada contra fonte primária · ⚠️ coletado de fonte citada, verificação
adversarial pendente (interrompida por limite de conta) · ❌ refutado (excluído do plano).

---

## Lacuna 1 — "CNPJ ativo ≠ empresa operante"

### Como os players resolvem

| Player | Método | Acesso | Fonte |
|---|---|---|---|
| **Enigma** (EUA) ✅ | "Operating Status" com níveis de confiança: transações de cartão nos últimos 3 meses e/ou presença online ativa; "very high" (cartão + online) com precisão declarada >85% | API enterprise | [documentation.enigma.com](https://documentation.enigma.com/v1/reference/attributes/identity-and-firmographics-attributes/operating-status) |
| **Neoway** (BR/B3) ✅ | "Nível de atividade": probabilidade de estar aberta, combinando localização, CNAE, contratações/demissões, composição societária e pagamento de impostos federais | SaaS enterprise | [neoway.com.br](https://www.neoway.com.br/solucoes/b2b-intelligence) |
| **Econodata** (BR) ⚠️ | "Faturamento Presumido": capital social × CNAE × faixa de funcionários × tempo de mercado — as 4 variáveis têm fonte pública | SaaS centenas de R$/mês | [blog.econodata.com.br](https://blog.econodata.com.br/novo-recurso-faturamento-presumido/) |
| **BigDataCorp** (BR) ⚠️ | APIs por CNPJ: faturamento estimado, funcionários, presença digital, telefones validados com as teles | pay-per-use (acessível a startup) | [docs.bigdatacorp.com.br](https://docs.bigdatacorp.com.br/plataforma/docs/dados-dispon%C3%ADveis) |
| **Serasa Experian** ⚠️ | Sinais comportamentais: protestos, dívidas, consultas ao CNPJ, score PJ — CNPJ sem rastro de crédito tende a ser casca | pago por consulta | [serasaexperian.com.br](https://www.serasaexperian.com.br/solucoes/consulta-cnpj/) |
| **Dun & Bradstreet** ⚠️ | Viability Rating: probabilidade de fechar/ficar dormente em 12 meses (score 1-9 + profundidade de dado) | enterprise | [dnb.com](https://www.dnb.com/en-us/resources/supplier-risk/viability-rating.html) |

### O método correto

Score **probabilístico multi-sinal com faixas de confiança** (padrão Enigma/Neoway/D&B) — nunca um
binário. Nosso proxy atual (opção pelo Simples) está metodologicamente alinhado, mas é UM sinal; o
plano empilha os demais sinais públicos.

### Implementação na ferramenta

1. **Frescor cadastral** (grátis): manter snapshots mensais do dump CNPJ e derivar "alteração de
   sócios/capital/CNAE/endereço/regime nos últimos 24 meses" = empresa administrada.
2. **Sinal fiscal público** ✅: para CNAEs de comércio, situação da Inscrição Estadual no
   CADESP/Sintegra — "inapta: cassada por inatividade presumida" é rótulo oficial por omissão de
   GIA 3 meses (Portaria CAT 95/2006; ex.: [10.567 cassações set-nov/2023](https://portal.fazenda.sp.gov.br/Noticias/Paginas/Sefaz-SP-efetua-a-cassa%C3%A7%C3%A3o-da-inscri%C3%A7%C3%A3o-estadual-de-10,5-mil-contribuintes-por-inatividade-presumida.aspx)).
   Para serviços (ISS), análogo = cadastro mobiliário municipal (CCM), como enriquecimento amostral.
3. **Fator CEMPRE/RF** ✅: razão "empresas ativas no CEMPRE ÷ CNPJs ativos na RF" por CNAE×UF como
   calibrador agregado. Atenção verificada: usar séries até ano-base 2021 como cenário conservador —
   a partir de 2022 o critério do CEMPRE afrouxou (inclui "ativa na RF sem indicativo de inatividade").
4. **Presença viva** (barato): Google Places API — `business_status` (OPERATIONAL/CLOSED) + recência
   de avaliações (~US$ 0,017/consulta, cota gratuita mensal); Instagram com post nos últimos 90 dias
   (forte para beleza); validação dos telefones/e-mails do próprio dump da RF.
5. **Protestos** (grátis, unitário): [pesquisaprotesto.com.br](https://www.pesquisaprotesto.com.br/)
   para amostras de validação (protesto = empresa transacionava).
6. **Score final**: combinar em rótulo "operante muito provável / provável / indeterminado / provável
   casca", exibido no relatório com os sinais que o compõem.

**Esforço:** 2–4 semanas · **Custo:** ~zero + Places (~US$ 30/1.000 consultas, amostral).

---

## Lacuna 2 — Informalidade (a mais importante para o setor beleza)

### Como se mede corretamente

| Quem | Método | Acesso |
|---|---|---|
| **OECD/IMF/ILO** ✅ | *Labor Input Method* (padrão internacional para serviços intensivos em trabalho): emprego total da pesquisa domiciliar − emprego captado nos registros de empresas = trabalho não observado × receita por trabalhador | [Handbook gratuito](https://www.oecd.org/content/dam/oecd/en/publications/reports/2002/05/measuring-the-non-observed-economy-a-handbook_g1ghge7e/9789264175358-en.pdf) |
| **IBGE PNAD Contínua** ✅ | Desde o 4º tri/2015 pergunta ao conta própria/empregador se o negócio tem CNPJ (variável V4019); ~74% dos conta própria do Brasil não têm | microdados gratuitos ([Base dos Dados](https://basedosdados.org) / FTP IBGE) |
| **ETCO/FGV-IBRE** ✅ | Índice de Economia Subterrânea: ~17,8% do PIB (2022) — economy-wide, serve só como piso/sanity check | [etco.org.br](https://en.etco.org.br/economia-subterranea/?sub=resumo) |
| **Euromonitor** ⚠️ | Inclui canais informais no sizing por triangulação oferta-demanda (trade interviews + store checks) | assinatura |
| **Kantar Worldpanel** ⚠️ | Painel domiciliar (~11 mil lares no Brasil): mede o gasto do consumidor, capturando o informal pelo lado da demanda | parceria paga |

❌ Excluído: âncora "84% dos 342 mil salões são MEI" (Sebrae) — refutada como desatualizada e
internamente inconsistente na verificação.

### Implementação na ferramenta (100% dados públicos)

1. Query trimestral na PNAD-C via BigQuery (`basedosdados.br_ibge_pnadc.microdados`): ocupações
   COD **5141** (cabeleireiros) e **5142** (esteticistas/manicures), cruzando V4019 (tem CNPJ),
   V4012 (posição na ocupação) e carteira, somando o peso V1028, por UF → **N_informal vira dado
   trimestral**, não premissa.
2. Receita informal publicada como **intervalo**: piso = soma dos rendimentos (VD4016) dos
   informais; teto = N_informal × receita/ocupado do segmento formal (PAS) × fator de produtividade
   0,4–0,6 [premissa declarada, ancorada na ECINF/literatura].
3. Reconciliação automática: N_formal da PNAD vs estoque CNPJ 9602-5 vs estatísticas do MEI —
   divergência grande dispara alerta (também reforça a lacuna 1).
4. Sanity checks: share informal do setor > piso ETCO; validação com o
   [Panorama Senac do mercado de beleza](https://forumsetorial.senac.br/assets/images/panorama_mercado_beleza.pdf)
   (construído sobre a mesma PNAD-C).

**Esforço:** 1–2 semanas · **Custo:** zero (free tier BigQuery).

---

## Lacuna 3 — Participações de segmento e região (de premissa para dado)

### A descoberta que muda o jogo ⚠️

A PAS publica receita **por atividade CNAE dentro de "serviços prestados às famílias"** — incluindo
o detalhe de cabeleireiros/tratamento de beleza (9602-5) — na **[SIDRA Tabela 2611](https://sidra.ibge.gov.br/tabela/2611)**.
Ou seja: a nossa premissa de "50% de beleza dentro de serviços pessoais" pode ser **substituída por
leitura direta da fonte oficial** (mesma API de agregados que já usamos). *(Verificação adversarial
pendente — validar o nível de detalhe na primeira consulta real.)*

### Como os players fazem

- **Statista** ⚠️ (metodologia pública): "driver-based projection" — aloca mercado por drivers
  correlacionados (população, renda, penetração) quando não há dado observado.
- **Euromonitor** ⚠️: triangulação com fontes oficiais + associações setoriais (no Brasil, ABIHPEC —
  que representa ~90% do setor HPPC) + trade interviews.
- **Grand View/Mordor** ⚠️: split regional emerge da estimação por país/região, não de rateio.
- Playbook de consultoria ([Umbrex](https://umbrex.com/resources/market-sizing-playbook/top-down-market-sizing-methodology/)) ⚠️:
  usar *scaling keys* que **causam** a demanda, testadas por back-casting.

### Implementação na ferramenta

1. **Segmento = dado**: ler a fração 9602-5 / serviços às famílias da PAS Tab. 2611 via API.
2. **Região = triangulação de 3 pesos independentes**, publicando o intervalo (nunca ponto seco):
   - *wage-weighted*: massa salarial da subclasse CNAE por UF (RAIS via
     `basedosdados.br_me_rais`, BigQuery) ⚠️;
   - *consumption-weighted*: despesa familiar com cabeleireiro/manicuro por região (POF,
     [SIDRA 3615/3618](https://sidra.ibge.gov.br/tabela/3618)) — de quebra captura consumo informal;
   - *production-weighted* (sanity): participação da UF no VAB de serviços
     ([Contas Regionais](https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9054-contas-regionais-do-brasil.html)).
3. **Benchmark setorial**: [Panorama ABIHPEC](https://abihpec.org.br/mercado/panorama-do-setor/)
   (gratuito, feito com IEMI/Euromonitor/Kantar) como triangulação citável — a mesma prática do Euromonitor.
4. **Rotulagem**: todo número do relatório ganha tag `[DADO: tabela/ano]` ou `[PREMISSA DECLARADA]`.

**Esforço:** 1–2 semanas · **Custo:** zero.

---

## Lacuna 4 — Share de mercado e pesquisa primária

### Share sem Nielsen/Kantar (dados alternativos)

| Fonte | O que dá | Acesso |
|---|---|---|
| **Cielo ICVA** ⚠️ | Índice mensal de varejo sobre transações reais de ~1 milhão de credenciados, 18 setores — calibra a dinâmica de crescimento do top-down | gratuito ([blog.cielo.com.br/indice-icva](https://blog.cielo.com.br/indice-icva/)) |
| **Cielo Inteligência de Dados / Stone** ⚠️ | Faturamento agregado por CNAE × município — o caminho brasileiro para share transacional | comercial/parceria; [Índice Stone](https://conteudo.stone.com.br/indice-do-varejo/) gratuito |
| **Bloomberg Second Measure** ⚠️ | Blueprint internacional: share/retention por painel de transações de cartão de 20M+ consumidores (só EUA) | referência de arquitetura |
| **Google Places** ⚠️ | `user_ratings_total` como peso de share relativo local; Places ∩ CNPJ = formal operante; Places − CNPJ = piso do informal local | ~US$ 30/1.000 buscas |
| **NFC-e** ⚠️ | Sem open data nacional; onde existe ([Preço da Hora BA](https://precodahora.ba.gov.br), Menor Preço Nota Paraná): preço/ticket por item × estabelecimento | gratuito, cobertura parcial (declarar) |

### Pesquisa primária embutida na plataforma

| Fornecedor | Modelo | Preço ⚠️ |
|---|---|---|
| **Opinion Box** (BR) | painel próprio 1M+ respondentes, self-service | a partir de ~R$ 6/resposta, pesquisa mínima ~R$ 300 |
| **MindMiners** (BR) | painel MeSeems 5M+ | sob consulta |
| **Cint Exchange (ex-Lucid)** | marketplace global com **Demand API** — cria survey, define cotas e compra respostas programaticamente (o caminho para embutir survey na nossa plataforma) | CPI dinâmico, [developer.cint.com](https://developer.cint.com/demand/docs/2025-12-18/getting-started/) |
| **SurveyMonkey Audience** | benchmark de UX self-service | ~US$ 1/resposta |
| **Statista Consumer Insights** | modelo alternativo: ondas trimestrais sindicalizadas (~2.000 respondentes/BR por onda) vendidas a todos os assinantes | assinatura |

Amostra mínima padrão: **n ≈ 385** (95% de confiança, 5% de margem — fórmula de Cochran) →
custo de campo no Brasil na ordem de **R$ 2,5–4 mil por estudo** via painéis nacionais. ⚠️

---

## Priorização e roadmap

| # | Solução | Lacuna | Esforço | Custo | Impacto |
|---|---|---|---|---|---|
| 1 | PAS 2611 (segmento = dado) + triangulação regional (RAIS/POF/Contas Regionais) | 3 | 1–2 sem | zero | alto — elimina as 2 premissas mais criticáveis |
| 2 | Informalidade via PNAD-C (labor input method) | 2 | 1–2 sem | zero | alto — o setor é majoritariamente informal |
| 3 | Score de operância multi-sinal (snapshots + CEMPRE + Places + IE) | 1 | 2–4 sem | ~US$ 30/1k | alto — refina o coração do bottom-up |
| 4 | ICVA/Índice Stone como calibrador de crescimento | 4 (parcial) | dias | zero | médio |
| 5 | Survey embutido (Cint Demand API ou parceria Opinion Box) | 4 | 3–6 sem | por uso | médio-alto — vira feature vendável |
| 6 | Dados transacionais licenciados (Cielo/Stone comercial) | 4 | negociação | R$ mil+/mês | alto, porém caro — só com receita |

**Onda 1 (imediata, custo zero):** itens 1, 2 e 4 — três das quatro limitações saem do relatório ou
viram intervalos com dado.
**Onda 2 (MVP+):** item 3 (score de operância) + item 5 (survey embutido) — diferenciais de produto.
**Onda 3 (com receita):** item 6 (parcerias de dados transacionais) — share real por CNAE×município.

## O que descartamos e por quê

- **Fator ETCO como correção setorial**: economy-wide (~17,8% do PIB); a informalidade da beleza é
  muito maior que a média — usar só como piso/sanity ✅.
- **Âncora Sebrae "84% de 342 mil salões"**: refutada (desatualizada/inconsistente) ❌.
- **Comprar Nielsen/Kantar/Euromonitor no MVP**: custo enterprise incompatível; a triangulação
  pública + ABIHPEC cobre o essencial e os badges de proveniência mantêm a honestidade.
- **NFC-e como fonte nacional**: não existe open data nacional; usar apenas nos estados que expõem ⚠️.

---

*Pesquisa executada em 04/07/2026 com verificação adversarial parcial (16 votos concluídos, 14
confirmações, concentrados nas lacunas 1–2; lacunas 3–4 com fontes citadas e verificação pendente).
Documentos relacionados: `auditoria-numeros-piloto.md`, `metodologia-v3.md`,
`especificacao-produto-mvp.md`.*

---

# Parte 2 — as limitações 5–8 (pesquisa 05/07/2026)

As auditorias do piloto acrescentaram 4 limitações às 4 originais. Benchmark e fechamento:

## Limitação 5 — CNAE secundário fora da contagem principal

- **Mercado:** plataformas de prospecção B2B ([Econodata](https://www.econodata.com.br/consulta-cnae),
  Speedio, Casa dos Dados) tratam o filtro por CNAE secundário como recurso padrão — para LISTAS.
  Para SIZING, nenhum player publica método; o correto é ponderar pela receita da atividade.
- **Fechado na ferramenta:** a seção 7b publica o SAM por atividade como **faixa** — conservador
  (só CNAE principal) ↔ expandido (empresas só-secundárias × taxa de atividade × ticket × peso de
  receita 15% [premissa do mix 40/15, declarada]). Dados da consulta E.

## Limitação 6 — lag de registro de baixas (fechamentos revisados para cima)

- **Mercado:** vendors de dados cadastrais mantêm *vintages* (fotografias mensais) e medem a
  revisão entre elas; a estatística oficial de fluxo é o
  [Mapa de Empresas](https://www.gov.br/empresas-e-negocios/pt-br/mapa-de-empresas) (boletim
  quadrimestral: aberturas, baixas, tempo de baixa; não cobre MEI).
- **Fechado na ferramenta:** extração 2026-06 arquivada em `dados/vintages/`; `cnpj.fator_revisao()`
  compara a extração mais antiga com a mais nova e o relatório passa a exibir o fator medido
  ("fechamentos de X revisados em +Y%"). Selo de referência ao Mapa de Empresas na seção 7.

## Limitação 7 — faixa de idade por estabelecimento (matriz × filiais)

- **Mercado:** padrão D&B/"year founded" — a idade da EMPRESA é a do estabelecimento matriz.
- **Fechado na ferramenta:** consulta **A4** (mesmo agregado da A3, com
  `MIN(data_inicio_atividade)` da matriz como idade da empresa). Flag `cnpj_idade_matriz` no JSON
  do setor troca o texto da limitação quando o CSV vier da A4.

## Limitação 8 — Lucro Presumido × Lucro Real (sigilo fiscal)

- **Confirmado:** não existe consulta pública ([Contabilizei](https://www.contabilizei.com.br/contabilizei-responde/como-consultar-o-regime-tributario-de-uma-empresa/),
  [Oobj](https://oobj.com.br/bc/como-consultar-regime-tributario-empresa/)) — só Simples/MEI são
  públicos. Vendors ([dbdireto](https://dbdireto.com.br/consulta-regime-tributario/), BigDataCorp)
  vendem o regime inferido via NF-e (campo CRT), Sintegra/regime de apuração estadual e códigos
  de DARF.
- **Na ferramenta:** dado público = proxy por porte (declarado, docs/metodologia-v3.md), grupo
  "Fora do Simples". Add-on de produto: enriquecimento pago por CNPJ para estudos premium.

## Status consolidado das 8 limitações

| # | Limitação | Status |
|---|---|---|
| 1 | CNPJ ativo ≠ operante | MITIGADA (proxy Simples MEDIDO 30,8%); score multi-sinal = Onda 2 |
| 2 | Informalidade | **FECHADA** (seção 7c, PNAD labor input) |
| 3 | Segmento e região premissas | **FECHADA** (PAS 2611 + triangulação regional CNPJ/CEMPRE/RAIS) |
| 4 | Share varejo / pesquisa primária | ABERTA por natureza (alt-data + survey = Onda 3; painéis pagos) |
| 5 | CNAE secundário | **FECHADA** (faixa conservador ↔ expandido na 7b) |
| 6 | Lag de baixas | EM MEDIÇÃO (vintages iniciados; fator automático na 2ª extração) |
| 7 | Idade matriz × filial | **FECHADA** (consulta A4 — aguarda 1 rodada no BigQuery) |
| 8 | Presumido × Real | LIMITE LEGAL (proxy por porte declarado; add-on pago mapeado) |
