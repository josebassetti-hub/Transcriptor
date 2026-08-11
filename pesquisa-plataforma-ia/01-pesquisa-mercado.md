# Pesquisa de Mercado — Plataformas de Serviços Sob Demanda e IA (Brasil e Mundo)

**Data da pesquisa:** 11/08/2026 · Fontes citadas em cada seção · Companion do `02-plano-mestre.md`

---

## Sumário executivo

1. **Velvo:** não foi encontrada nenhuma evidência pública de "velvo.com.br" como plataforma de serviços. O acesso direto ao domínio foi bloqueado pela rede deste ambiente; buscas na web, Reclame Aqui e bases de CNPJ só encontram o **Velvo Gin** (destilaria de Belo Horizonte, site velvogin.com.br). A pesquisa abaixo cobre, por isso, o espectro completo de plataformas de "cliente solicita → serviço entregue". *Se você colar aqui um print ou descrição da Velvo, o comparativo direto pode ser refinado.*

2. **Brasil — mercado polarizado, espaço vazio no meio.** De um lado, marketplaces onde humanos executam (GetNinjas, Workana, 99Freelas, Vintepila, Triider, Parafuzo, Singu), com comissões de 16–30% e fricção de orçamento/lead; do outro, plataformas de IA que só executam *conversas* — atendimento e vendas no WhatsApp (Blip, Weni/VTEX, Zaia, GPT Maker, Darwin AI, Halk, Toolzz). **Nenhuma plataforma brasileira combina "pedido em linguagem natural → IA produz o serviço final → validação humana mínima".**

3. **Mundo — incumbentes automatizaram a metade errada.** Fiverr (Fiverr Go, Neo) e Upwork (agente "Uma", apps no ChatGPT/Claude, servidor MCP) automatizaram *intake, matching e gestão* — mas a **execução** continua humana. Enquanto isso, o trabalho freelancer básico derrete (queda de 20–50% na demanda por escrita/tradução; Fiverr perdeu ~22% dos compradores ativos em 12 meses) e as categorias de IA explodem (habilidades de IA +109% a/a na Upwork; vídeo por IA +329%).

4. **IA-nativos entregam, mas vendem errado.** Manus, Genspark, Lovable, Replit e afins executam de ponta a ponta, porém cobram **créditos imprevisíveis** (a reclamação nº 1 documentada), não oferecem QA/garantia, não mantêm consistência de marca entre mídias e exigem que o cliente saiba o que pedir.

5. **A janela:** o empacotamento comercial de agência — preço fixo por entregável, revisões incluídas, QA que assina a entrega, direitos comerciais garantidos, memória de marca — sobre um roteador best-of-breed (a melhor IA de cada área) **não existe em nenhum dos três grupos**, no Brasil ou fora. É exatamente o plano do `02-plano-mestre.md`.

---

# PARTE 1 — BRASIL

**Metodologia e ressalva:** dados coletados via busca na web em 11/08/2026, com URL da fonte em cada ficha. Onde o dado não foi localizado (especialmente preços consultivos), isso está registrado — nada foi estimado ou inventado.

## Categoria A — Marketplaces de serviços (cliente pede → humano executa)

### 1. GetNinjas (getninjas.com.br)

- **O que faz:** maior marketplace generalista de serviços do Brasil (reformas, assistência técnica, aulas, serviços domésticos, eventos etc.). O cliente preenche um formulário descrevendo a necessidade; o pedido é distribuído a profissionais cadastrados, que compram o direito de ver o contato do cliente. Recebe mais de 4 milhões de pedidos por ano ([Jornal do Brás](https://jornaldobras.com.br/noticia/69690/diaristas-estao-entre-os-servicos-mais-solicitados-no-app-getninjas)).
- **Modelo e preços:** gratuito para o cliente. Profissional compra "moedas" em pacotes para desbloquear o contato de cada pedido. Sem mensalidade e sem comissão — a plataforma não intermedia o pagamento ([Blog GetNinjas — moedas](https://blog.getninjas.com.br/como-funcionam-as-moedas-do-getninjas/), [Wise](https://wise.com/br/blog/getninjas-como-funciona)).
- **Automação por IA:** **nenhuma** na execução — é matching de leads.
- **Forças:** marca mais conhecida da categoria, enorme volume de demanda, cobertura nacional.
- **Fraquezas:** modelo "leilão de leads" muito criticado — o profissional paga pelo lead sem garantia de fechar ([Outras Palavras](https://outraspalavras.net/tecnologiaemdisputa/getninjas-o-perverso-leilao-digital-de-trabalho-humano/)); sem escrow; a empresa passou por IPO reverso virando Reag Investimentos, com operação encolhendo e processo sancionador na CVM ([Seu Dinheiro](https://www.seudinheiro.com/2025/empresas/getninjas-ninj3-da-adeus-a-bolsa-empresa-muda-nome-para-reaginvest-e-passar-a-ter-novo-ticker-saiba-quando-comeca-a-valer-ccgg/), [InvestNews](https://investnews.com.br/negocios/getninjas-crise-reag-aquisicao/)).

### 2. Workana (workana.com)

- **O que faz:** marketplace de trabalho freelance remoto (design, TI, marketing, redação) líder na América Latina; cliente publica projeto, freelancers propõem, pagamento em escrow ([Nomad](https://www.nomadglobal.com/conteudos/workana)).
- **Modelo e preços:** comissão de 5% a 15% sobre o freelancer (decrescente por relacionamento) + ~4,5% do cliente; assinaturas opcionais ([Workana Community](https://community.workana.com/community//3321113/Como-funcionam-as-comiss%C3%B5es-da-Workana-Percentuais-incidentes-sobre-o-freelancer-e-sobre-o-cliente)).
- **Automação por IA:** **nenhuma na execução**.
- **Forças:** escrow, base grande de talentos LATAM. **Fraquezas:** comissão inicial alta, competição por preço, só serviços digitais.

### 3. 99Freelas (99freelas.com.br)

- **O que faz:** maior marketplace 100% brasileiro de freelancers digitais ([Wise](https://wise.com/br/blog/99freelas-como-funciona)).
- **Modelo e preços:** taxa de **20% no plano gratuito, 15% no Pro (R$ 49,90/mês) e 10% no Premium (R$ 89,90/mês)** ([Central de Ajuda 99Freelas](https://99freelas.zendesk.com/hc/pt-br/articles/360007908393-Quanto-custa-usar-o-99Freelas-Cliente)).
- **Automação por IA:** **nenhuma na execução**.
- **Forças:** adaptado ao Brasil (Pix, conta BR). **Fraquezas:** taxa de 20% é a mais alta do segmento.

### 4. Vintepila (vintepila.com.br)

- **O que faz:** modelo "Fiverr" brasileiro — o profissional publica **pacotes de serviço com preço fixo a partir de R$ 20** e o cliente compra direto ([Wise](https://wise.com/br/blog/vintepila-como-funciona), [TechTudo](https://www.techtudo.com.br/listas/2020/08/vintepila-vale-a-pena-veja-como-funciona-site-para-trabalhos-freelance.ghtml)).
- **Modelo e preços:** comissão de **20%**; estorno se prazo/requisitos não forem cumpridos.
- **Automação por IA:** **nenhuma**. (É o modelo de UX mais próximo de "compro um entregável pronto" — referência de produto direta para a nossa plataforma.)
- **Forças:** compra em 1 clique de serviço pré-precificado. **Fraquezas:** ticket baixo pressiona qualidade; alcance de marca menor.

### 5. Triider (triider.com.br)

- **O que faz:** serviços residenciais (50 tipos) com orçamento em 24h e modalidade **"Preço Fixo"** sem orçamento ([Triider](https://www.triider.com.br/), [Blog Triider](https://www.triider.com.br/blog/conheca-o-preco-fixo-nova-modalidade-de-servicos-do-triider/)).
- **Modelo e preços:** pagamento pelo app liberado só após conclusão; comissão de **16%** ([InfraFM](https://infrafm.com.br/Textos/1/19512/Voce-conhece-o-Triider-plataforma-com-50-tipos-de-servicos-domesticos)).
- **Automação por IA:** **nenhuma**; fluxo transacional completo dentro da plataforma.
- **Forças:** pagamento retido até conclusão, preço fixo em serviços padronizáveis. **Fraquezas:** poucas capitais, só residencial.

### 6. Parafuzo (parafuzo.com)

- **O que faz:** limpeza, passadoria, montagem e pós-obra; agendamento em <3 min com preço fechado; +1,5 milhão de serviços, +200 cidades; assinatura semanal e vertical B2B ([Parafuzo](https://parafuzo.com/), [Data Mercantil](https://datamercantil.com.br/conheca-a-startup-que-esta-levando-o-servico-de-faxina-para-a-casas-bahia/)).
- **Modelo e preços:** preço fechado por serviço, cobrança pós-execução; assinatura recorrente. Comissão não localizada.
- **Automação por IA:** **nenhuma**; é o marketplace doméstico mais "produtizado".

### 7. Singu (singu.com.br)

- **O que faz:** "delivery de beleza" a domicílio com **preço dinâmico** estilo Uber ([TechTudo](https://www.techtudo.com.br/dicas-e-tutoriais/2018/08/massagem-e-corte-de-cabelo-como-agendar-servico-de-beleza-pelo-singu.ghtml)).
- **Modelo e preços:** take rate ~30% ([Correio Braziliense](https://www.correiobraziliense.com.br/app/noticia/economia/2018/04/27/internas_economia,676660/o-que-e-singu.shtml)).
- **Automação por IA:** **nenhuma** na execução; só preço dinâmico algorítmico.

**Síntese da categoria A:** nenhum marketplace brasileiro relevante usa IA para *executar* o serviço. Os modelos são (i) venda de leads (GetNinjas), (ii) escrow + comissão (Workana, 99Freelas, Vintepila) e (iii) preço fixo transacional (Triider, Parafuzo, Singu) — este último é o padrão de UX mais próximo de uma plataforma onde a IA entrega.

## Categoria B — Plataformas brasileiras de IA/agentes

### 1. Blip (ex-Take Blip) — blip.ai
Plataforma enterprise de comunicação conversacional omnichannel (WhatsApp oficial Meta, Instagram, voz) com construtor de agentes de IA; ~2.500 empresas em 32 países. Pricing consultivo; **Blip Go a partir de R$ 99/mês** para SMB; excedentes R$ 1,25–1,40/conversa ([AI Hub Brasil](https://botaihub.com.br/ferramentas/take-blip/), [BossBot](https://bossbot.uk/blog/take-blip-pricing-review-2026)). **IA executa atendimento/venda conversacional** — não entregáveis. Líder capitalizada, mas pesada para PME e focada em conversa.

### 2. Weni by VTEX — weni.ai
IA conversacional adquirida pela VTEX; agentes "Auto-pilot" com **91,5% de resolução autônoma**. Cobrança por **tarifa de sucesso por interação resolvida sem humano** — modelo de monetização por resultado, referência valiosa ([VTEX](https://vtex.com/pt-pt/blog/vtex-adquire-weni-cx-potenciada-por-ia/)). Amarrada ao ecossistema VTEX/varejo.

### 3. Zaia — zaia.app
"Funcionários de IA" no-code para suporte e vendas em WhatsApp/Instagram/site; qualificam leads, agendam e levam ao checkout ([Zaia](https://zaia.app/en/lp/empresario)). Assinatura com créditos mensais por mensagem/LLM; créditos não acumulam ([Zaia Docs](https://zaiadocs.gitbook.io/recursos/gestao-da-sua-conta/planos-e-assinaturas)). Escopo limitado a conversação.

### 4. GPT Maker — gptmaker.ai
Agentes de IA "em menos de 5 minutos", sem programação; forte em **white-label para agências revenderem** ([GPT Maker](https://gptmaker.ai/), [Data Hackers](https://www.datahackers.news/p/gpt-maker-o-que-e-como-us-lo-para-criar-seu-pr-prio-agente-de-ia)). Créditos por uso; tabela oficial não localizada. Canal de revenda é um aprendizado interessante.

### 5. Darwin AI — getdarwin.ai
"AI workers" nomeados para PMEs LATAM (Alba/vendas, Sophia/pós-venda, Lucas/cobrança, Eva/suporte); produção em <1 semana; escala leads quentes para humano ([TechCrunch](https://techcrunch.com/2024/02/26/darwin-ai-latam-ai-sales-assistant/)). ARR > US$ 2 mi já em 2024; captou R$ 25 mi ([Lets News](https://lets-news.beehiiv.com/p/darwin-ai-acelerar-expansao-brasil-mexico)). **O desenho "IA executa, humano valida exceções" é o mais próximo do nosso conceito** — mas restrito a funções comerciais.

### 6. Halk — halk.io
Agente de vendas WhatsApp em produção em <1 dia; fecha o funil até o link de pagamento ([Halk Blog](https://www.halk.io/blog/pt/melhor-plataforma-agente-ia-brasil-2026)). Assinatura "em reais e previsível"; valores não públicos. Fontes majoritariamente do próprio blog (viés).

### 7. EVO IA / Evo AI — três produtos distintos com o mesmo nome
Open-source Apache 2.0 (infra de agentes, A2A/MCP/LangGraph — [Evo AI Docs](https://evoai.mintlify.app/pt/index)); EVO IA comercial de WhatsApp ([lp.evoialab.com.br](https://lp.evoialab.com.br/)); e ecossistema evoai.app. Preços não localizados. A marca fragmentada é em si um achado: não é um player único consolidado.

### 8. Outros: Toolzz AI, Moveo.AI, Botmaker
Toolzz: "superapp" de agentes B2B, cobrança por uso, claims do próprio fornecedor ([Toolzz Blog](https://blog.toolzz.net/blog/toolzz-ai-a-plataforma-mais-completa-do-brasil-835bd56c/)). Moveo.AI: verticais reguladas, caso com 76% de automação total ([Moveo.ai](https://moveo.ai/blog/melhores-agentes-de-ia)). Botmaker: conversacional LATAM mid-market ([Botmaker](https://botmaker.com/pt/)).

### IA que "cria o entregável" — a lacuna brasileira
O único player nacional relevante encontrado onde a IA **produz o serviço final** é o Criador de Sites com IA da HostGator Brasil ([HostGator](https://www.hostgator.com.br/blog/como-criar-site-com-ia/)). As demais ferramentas dos rankings 2026 (Durable, Framer, LogoAI, Looka) são estrangeiras ([Plustag](https://plustag.com.br/10-plataformas-de-ia-para-criar-sites-em-2026/)). **Não foi encontrada nenhuma plataforma brasileira generalista de "pedido em linguagem natural → IA executa → validação humana mínima".**

## Verificação "velvo.com.br"

- Buscas por "velvo" + app/serviços/plataforma **não retornaram nenhuma plataforma de serviços** — só homônimos irrelevantes (companion da MWM, Veloe/Velge/Belvo).
- No Reclame Aqui não há registro de velvo.com.br ([Reclame Aqui — velve](https://www.reclameaqui.com.br/detector-site-confiavel/velve.com.br)).
- O que existe consolidado com essa marca é o **Velvo Gin**, destilaria de BH fundada em 2019 ([Velvo Gin](https://velvogin.com.br/)).
- O acesso direto ao domínio foi bloqueado pela rede deste ambiente. **Conclusão: não há evidência pública de "Velvo" como plataforma de serviços.**

## Tabela-síntese Brasil

| Plataforma | Categoria | Automação IA | Preço | Fonte |
|---|---|---|---|---|
| GetNinjas | A — marketplace generalista | Nenhuma (leads) | Profissional compra moedas por lead; 0% comissão | [blog.getninjas.com.br](https://blog.getninjas.com.br/como-funcionam-as-moedas-do-getninjas/) |
| Workana | A — freelance digital | Nenhuma | 5–15% freelancer + ~4,5% cliente | [community.workana.com](https://community.workana.com/community//3321113/Como-funcionam-as-comiss%C3%B5es-da-Workana-Percentuais-incidentes-sobre-o-freelancer-e-sobre-o-cliente) |
| 99Freelas | A — freelance digital | Nenhuma | 20% / 15% (R$ 49,90) / 10% (R$ 89,90) | [99freelas.zendesk.com](https://99freelas.zendesk.com/hc/pt-br/articles/360007908393-Quanto-custa-usar-o-99Freelas-Cliente) |
| Vintepila | A — serviços pré-precificados | Nenhuma | Desde R$ 20; comissão 20% | [wise.com](https://wise.com/br/blog/vintepila-como-funciona) |
| Triider | A — residencial | Nenhuma | Comissão 16%; pós-pago em até 6x | [infrafm.com.br](https://infrafm.com.br/Textos/1/19512/Voce-conhece-o-Triider-plataforma-com-50-tipos-de-servicos-domesticos) |
| Parafuzo | A — doméstico | Nenhuma | Preço fechado; assinatura | [parafuzo.com](https://parafuzo.com/) |
| Singu | A — beleza | Nenhuma (preço dinâmico) | Take ~30% | [correiobraziliense.com.br](https://www.correiobraziliense.com.br/app/noticia/economia/2018/04/27/internas_economia,676660/o-que-e-singu.shtml) |
| Blip | B — conversacional enterprise | Executa atendimento | Consultivo; Go desde R$ 99/mês | [botaihub.com.br](https://botaihub.com.br/ferramentas/take-blip/) |
| Weni by VTEX | B — CX e-commerce | Executa (91,5% resolução) | Tarifa de sucesso por resolução | [vtex.com](https://vtex.com/pt-pt/blog/vtex-adquire-weni-cx-potenciada-por-ia/) |
| Zaia | B — funcionários de IA | Executa suporte/vendas | Créditos mensais | [zaiadocs.gitbook.io](https://zaiadocs.gitbook.io/recursos/gestao-da-sua-conta/planos-e-assinaturas) |
| GPT Maker | B — no-code/white-label | Executa atendimento | Créditos por uso | [gptmaker.ai](https://gptmaker.ai/) |
| Darwin AI | B — AI workers | Executa vendas/cobrança c/ humano | Não público; ARR > US$ 2 mi | [techcrunch.com](https://techcrunch.com/2024/02/26/darwin-ai-latam-ai-sales-assistant/) |
| Halk | B — vendas WhatsApp | Executa funil até pagamento | Não público | [halk.io/blog](https://www.halk.io/blog/pt/melhor-plataforma-agente-ia-brasil-2026) |
| EVO IA (3 produtos) | B — agentes/infra | Conversação / infra | Não localizados | [lp.evoialab.com.br](https://lp.evoialab.com.br/) |
| Toolzz / Moveo / Botmaker | B — conversacional | Executam atendimento | Por uso / não públicos | [blog.toolzz.net](https://blog.toolzz.net/blog/toolzz-ai-a-plataforma-mais-completa-do-brasil-835bd56c/) |
| HostGator Criador IA | B — IA cria site | Executa produção do site | Embutido na hospedagem | [hostgator.com.br](https://www.hostgator.com.br/blog/como-criar-site-com-ia/) |
| **Velvo** | — não identificada como plataforma | — | — | [velvogin.com.br](https://velvogin.com.br/) (apenas gin) |

---

# PARTE 2 — MARKETPLACES GLOBAIS E A CORRIDA DA IA

## 1. Fiverr

**O que faz:** marketplace de "gigs" com preço fixo; migrando para alto valor (Pro, Managed Services) e integração agêntica.

**Taxas:** vendedor **20% fixo**; comprador **5,5%** + US$ 2,50 em pedidos < US$ 50; take rate de marketplace de **28,0%** no Q2 2026 ([FreelanceCompare](https://freelancecompare.com/blog/fiverr-fees-explained), [StockTitan — Q2 2026](https://www.stocktitan.net/news/FVRR/fiverr-announces-second-quarter-2026-o0quisjjfetp.html)).

**IA na plataforma:**
- **Fiverr Go** (fev/2025): freelancers Level 2+ treinam um modelo de IA no próprio portfólio; o comprador gera entregas instantâneas "no estilo" do criador, que define preço e mantém direitos; + assistente pessoal que negocia e coleta briefing. US$ 25/mês para o criador. É o exemplo mais próximo hoje de "IA entrega o trabalho" dentro de um marketplace tradicional ([Startups Magazine](https://startupsmagazine.co.uk/article-fiverr-unveils-fiverr-go-ai-platform-protect-creatives), [Unkoa](https://www.unkoa.com/fiverr-go-review-2025-turn-your-unique-style-into-a-passive-income-ai-model/)).
- **Neo / Dynamic Matching:** matching conversacional e briefs algorítmicos ([VentureBeat](https://venturebeat.com/ai/fiverr-launches-business-solutions-and-neo-ai-matching-algorithm)).
- **Ambição declarada:** ser "fulfillment partner" dentro de workflows agênticos ([Forbes](https://www.forbes.com/sites/kolawolesamueladebayo/2025/09/21/fiverrs-bold-ai-bet-and-what-it-reveals-about-the-future-of-work/)).

**Números:** FY2025 US$ 430,9 mi (+10,1%), Services +50,9%; mas 2026 é "ano de reset": Q2 2026 **-10% a/a**, compradores ativos **-21,9%**, guidance cortado, ~30% de demissões ([Fiverr IR](https://investors.fiverr.com/news-releases/news-release-details/fiverr-announces-fourth-quarter-and-full-year-2025-results), [Investing.com](https://www.investing.com/news/transcripts/earnings-call-transcript-fiverr-q2-2026-miss-and-outlook-spark-sharp-selloff-93CH-4820585)).

**Forças:** catálogo produtizado, pioneirismo do Fiverr Go, margem alta. **Fraquezas:** o núcleo (gigs baratos) é exatamente o que a IA come; tráfego de busca em erosão (AI Overviews); reação negativa dos freelancers.

## 2. Upwork

**O que faz:** maior marketplace por volume (GSV > US$ 4 bi/ano); projetos por hora/preço fixo, escrow, enterprise.

**Taxas:** freelancer **0–15% variável por contrato** (desde mai/2025); cliente 5% (Basic) ou 10% (Business Plus); take rate 19% ([goLance](https://golance.com/blogs/upwork-fees-explained-2026), [Upwork IR — FY2025](https://investors.upwork.com/news-releases/news-release-details/upwork-reports-fourth-quarter-and-full-year-2025-financial)).

**IA na plataforma:**
- **Uma** virou "**AI work agent**": gera job posts (já responde pela maioria dos novos), conduz **entrevistas instantâneas** com candidatos, resume, rascunha contratos; +8% de matches em projetos de alto valor ([Upwork IR — Uma](https://investors.upwork.com/news-releases/news-release-details/upwork-evolves-uma-ai-ai-work-agent-advances-human-ai)).
- **Distribuição dentro das IAs (2026):** app no ChatGPT (abr/2026), **Claude Connector** e **servidor MCP** — agentes de terceiros contratam e gerenciam humanos na Upwork ("Upwork Talent Is Now Everywhere AI Works", ago/2026) ([GlobeNewswire](https://www.globenewswire.com/news-release/2026/08/10/3342153/0/en/upwork-talent-is-now-everywhere-ai-works.html)).

**Números:** FY2025 recorde US$ 787,8 mi (+2%); GSV de IA +53% a/a (Q3 25); Q2 2026: US$ 191,7 mi, GSV/cliente recorde (US$ 5.230), mas clientes ativos **-4% a/a** ([GlobeNewswire — Q2 2026](https://www.globenewswire.com/news-release/2026/08/10/3342306/0/en/upwork-reports-second-quarter-2026-financial-results.html)).

**Forças:** maior GSV, Uma em todo o funil, primeiro a se distribuir via ChatGPT/Claude/MCP. **Fraquezas:** base de clientes encolhendo; crescimento vem de take rate, não de volume.

## 3. Freelancer.com

Leilão de projetos + concursos; +80 mi cadastrados; grupo ASX com Escrow.com e Loadshift. Marketplace em queda (1S 2026: receita -12,4%), grupo cresce por escrow/frete ([SIA](https://www.staffingindustry.com/news/global-daily-news/australias-freelancer-h1-revenue-slides-124)). IA mais retórica que produto ("hub de desenvolvimento de agentes" como aposta 2026) ([Freelancer press](https://www.freelancer.com/about/press)).

## 4. Toptal

Rede premium vetada ("top 3%"), markup embutido de ~40–100%, talento não paga ([The Frontend Company](https://www.thefrontendcompany.com/posts/toptal-pricing)). IA aparece como categoria de talento vendida, não como produto. É o segmento menos exposto à substituição (trabalho complexo de confiança) — e o menos escalável.

## 5. Contra

Rede "commission-free" (1,2 mi criativos; US$ 200 mi+ pagos sem comissão); monetiza cliente + assinaturas ([Contra](https://contra.com/home?userType=independent)). Indy AI: recomendações, chatbot, lead finder ([Digino](https://digino.org/tools/contra/)). Referência do nicho "freelancers que vendem automações de IA".

## 6. 99designs (Vista)

Concursos de design (logo Bronze US$ 299 → Platinum US$ 1.299; identidade até US$ 2.499; +5% fee; vencedor fica com ~60%) ([ITQlick](https://www.itqlick.com/99designs/pricing)). Postura **defensiva** com IA: cliente opta por permitir/proibir IA generativa nos concursos ([99designs Help](https://support.99designs.com/hc/en-us/articles/29341768376212-Generative-AI-in-Design-Contests)). Logo simples é das categorias mais atacadas por geradores de imagem.

## 7. Outros

**Braintrust** (15% só do cliente, talento fica com 100%, forte em vagas de IA — [SelectSoftware Reviews](https://www.selectsoftwarereviews.com/reviews/braintrust)); **Turing/Andela/Arc.dev** (staffing de IA). Mercado de agentes de IA: US$ 7,84 bi (2025) → projeção US$ 52,6 bi (2030); mas +3.800 startups de agentes fecharam em 2025 — sobrevivem as que dominam um vertical com comprador que já paga um humano pela tarefa ([Demandsage](https://www.demandsage.com/ai-agents-startups/)).

## Tendência: a IA está comendo o trabalho básico — e os marketplaces reagem

**Substituição comprovada:** estudo com 3 milhões de job posts (*Journal of Economic Behavior & Organization*, jan/2025): queda de **20–50% na demanda** por escrita, copywriting e tradução ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0167268124004591)). Tradutores: 98% das atividades sobrepostas à IA ([Washington Post](https://www.washingtonpost.com/business/2025/09/26/ai-translation-jobs/)). Fiverr: -22% compradores ativos; Upwork: -4% clientes ativos.

**O que cresce:** skills de IA +109% a/a; **vídeo por IA +329%**, integração de IA +178% ([Upwork In-Demand Skills 2026](https://www.upwork.com/press/releases/upworks-in-demand-skills-2026-demand-for-top-ai-skills-more-than-doubles-as-ai-is-embedded-into-everyday-work), [CNBC](https://www.cnbc.com/2026/02/09/upwork-fastest-growing-in-demand-skills-companies-are-hiring-for.html)).

**Os 4 movimentos de resposta:** (1) subir na cadeia de valor (Fiverr Pro, Upwork enterprise); (2) transformar o freelancer em "dono de uma IA" (Fiverr Go); (3) agentes operando o funil (Uma, Neo) — o intake em linguagem natural já é padrão dos incumbentes, **mas a execução continua humana**; (4) ir aonde os agentes estão (Upwork no ChatGPT/Claude/MCP).

**Implicação:** o gap aberto é a **orquestração ponta a ponta com execução por agentes** + escalonamento humano para o que a IA não resolve. Upwork (via MCP) pode inclusive virar o "braço humano" plugável da nossa plataforma para exceções.

## Tabela-síntese global

| Plataforma | Modelo | Papel da IA hoje | Taxas | Fonte |
|---|---|---|---|---|
| Fiverr | Gigs + Pro/Managed (US$ 430,9 mi/2025) | Fiverr Go (entrega no estilo do freelancer), Neo, matching | 20% vendedor + 5,5% comprador; take 28% | [Fiverr IR](https://investors.fiverr.com/news-releases/news-release-details/fiverr-announces-fourth-quarter-and-full-year-2025-results) |
| Upwork | Projetos + enterprise (US$ 787,8 mi/2025; GSV US$ 4 bi+) | Uma "AI work agent"; apps ChatGPT/Claude + MCP | 0–15% freelancer; 5–10% cliente; take 19% | [Upwork IR](https://investors.upwork.com/news-releases/news-release-details/upwork-reports-fourth-quarter-and-full-year-2025-financial) |
| Freelancer.com | Leilão + Escrow.com + Loadshift | Produtividade; retórica de "hub de agentes" | Comissões + memberships | [SIA](https://www.staffingindustry.com/news/global-daily-news/australias-freelancer-h1-revenue-slides-124) |
| Toptal | Rede premium vetada | Categoria de talento vendida | Markup ~40–100% embutido | [The Frontend Company](https://www.thefrontendcompany.com/posts/toptal-pricing) |
| Contra | 0% comissão (1,2 mi criativos) | Indy AI (recomendações, leads) | 0% freelancer; monetiza cliente | [Contra](https://contra.com/home?userType=independent) |
| 99designs | Concursos de design | Defensiva (opt-in/out de IA) | US$ 299–2.499 + 5%; take 30–40% | [ITQlick](https://www.itqlick.com/99designs/pricing) |
| Braintrust | Open talent de IA/tech | Matching com IA | 15% só do cliente | [SelectSoftware Reviews](https://www.selectsoftwarereviews.com/reviews/braintrust) |

---

# PARTE 3 — PLATAFORMAS IA-NATIVAS E AS MELHORES IAs POR ÁREA

## Frente A — Agentes generalistas / orquestradores

### Manus AI
Agente autônomo generalista — de um prompt, planeja, navega, executa código e entrega sites/relatórios/planilhas prontos. O produto mais próximo do "descreva e receba pronto". Free (300 créditos/dia); US$ 20–200/mês por créditos, sem rollover ([No Code MBA](https://www.nocode.mba/articles/manus-ai-pricing), [FelloAI](https://felloai.com/manus-ai-pricing/)). **Limitação:** custo imprevisível por créditos.

### OpenAI — ChatGPT Agent (ex-Operator)
Automação de navegador via loop visão-ação, embutida nos planos (Plus US$ 20, Pro US$ 200); API CUA US$ 3/US$ 12 por 1M tokens ([AI Agent Square](https://aiagentsquare.com/agents/openai-operator), [OpsLyft](https://www.opslyft.com/blog/chatgpt-pricing-2026)). Exige confirmação humana em ações sensíveis; melhor em tarefas web estruturadas.

### Anthropic — Claude (Cowork, Agent SDK, Managed Agents)
**Cowork** (GA abr/2026): agente autônomo de escritório, incluído nos planos pagos (Pro US$ 20; Max US$ 100–200). **Agent SDK**: o loop agêntico do Claude Code para construir agentes próprios; planos incluem crédito mensal de SDK desde jun/2026. **Managed Agents**: agentes hospedados sem cuidar de infra ([anúncio 9/abr/2026](https://pasqualepillitteri.it/en/news/755/anthropic-managed-agents-cowork-ga-april-9-2026), [Agensi](https://www.agensi.io/learn/claude-cowork-pricing)). É a base tecnológica recomendada no plano mestre — mas é produtividade pessoal/infra, não plataforma de serviços a clientes.

### Lindy · Relevance AI · Zapier Agents · CrewAI
Automação de negócio no-code/low-code (e-mail, SDR, CRM, workflows): Lindy US$ 49,99–199,99/mês ([CloudTalk](https://www.cloudtalk.io/blog/lindy-ai-pricing/)); Relevance Free–US$ 349/mês por "Actions" ([ColdIQ](https://coldiq.com/blog/relevance-ai-pricing)); Zapier Agents ~US$ 20/mês add-on ([AICX Stack](https://www.aicxstack.com/blog/zapier-agents-review)); CrewAI open-source + enterprise US$ 60–120 mil/ano estimado ([TechJack](https://techjacksolutions.com/ai-tools/crewai/crewai-pricing/)). Todos exigem que o usuário desenhe o fluxo — não são "peça e receba".

### Devin (Cognition)
Engenheiro de software autônomo (ticket → PR). Pro US$ 20/assento; Teams US$ 80 + US$ 40/assento; cobrança por ACUs. Corte de 96% no preço levou ARR de US$ 1M a US$ 73M em 9 meses ([Pensero](https://pensero.ai/blog/devin-pricing)). Só código; sofre com tarefas ambíguas.

### Lovable · Replit Agent 3
Builders chat-first de apps/sites. Lovable: US$ 25/mês + top-ups; US$ 20M ARR em 2 meses; custos imprevisíveis (debug consome créditos do cliente) ([eesel](https://www.eesel.ai/blog/lovable-pricing)). Replit Agent 3: autônomo por até 200 min; modelo "effort-based" com forte reação negativa (relatos de US$ 1.000/semana) ([Usecarly](https://www.usecarly.com/blog/replit-agent-pricing-explained/)).

### Genspark
"Super agent" tudo-em-um (sites, apresentações, imagens, vídeos, até ligações) — com Manus, o concorrente mais direto do conceito unificado. Plus US$ 24,99/mês; Pro US$ 249,99; créditos expiram mensalmente ([eesel](https://www.eesel.ai/blog/genspark-ai-pricing)).

## Frente B — Melhor ferramenta por área (ago/2026)

| Área | Melhor ferramenta | Alternativas | Preço aprox. | Fonte |
|---|---|---|---|---|
| Texto / estratégia | Claude (topo de linha) — melhor prosa e consistência em docs longos | GPT-5.5/5.6, Gemini 3.1 Pro (US$ 2/US$ 12 por 1M tokens) | Pro US$ 20/mês | [BenchLM](https://benchlm.ai/blog/posts/best-llm-writing) |
| Código / sites | Claude Code (agêntico complexo) + Lovable (leigos) | Cursor, OpenAI Codex, Bolt.new, v0 | US$ 20–200/mês | [Cosmic JS](https://www.cosmicjs.com/changelog/claude-code-vs-codex-vs-cursor) |
| Imagem / design | Midjourney V8.2 (líder artístico) | Ideogram 4.0 (texto em imagem), FLUX.2 (US$ 0,014/MP), GPT Image 2 (US$ 0,005–0,211/img), Firefly (IP-safe), Recraft V3 | Desde US$ 10/mês | [AI Comparison](https://aicomparison.ai/best-ai-image-generators/) |
| Vídeo | Google Veo 3.1 (4K/60fps, áudio nativo; desde US$ 0,15/s) | Kling 3.0 (~US$ 0,10/s), Runway Gen-4.5, Pika. Sora 2 descontinuado (API encerra 24/09/2026) | vide coluna | [Kingy](https://kingy.ai/news/best-ai-video-generator-2026/), [Crazyrouter](https://crazyrouter.com/en/blog/ai-video-generation-api-pricing-may-2026-comparison) |
| Voz / dublagem | ElevenLabs (TTS, clonagem, dublagem multilíngue) | Fish Audio | Free–US$ 1.320/mês (Creator US$ 22) | [Flexprice](https://flexprice.io/blog/elevenlabs-pricing-breakdown) |
| Música | Suno (download nos pagos; Suno Studio/DAW) | Udio (US$ 10–30, sem download livre pós-UMG) | Pro US$ 10/mês | [Neuronad](https://neuronad.com/suno-vs-udio/) |
| Apresentações | Gamma (multi-formato) | Presentations.AI, Beautiful.ai, Canva | Free–US$ 100/mês (Pro US$ 25) | [Presentations.ai](https://www.presentations.ai/blog/gamma-pricing) |
| Pesquisa profunda | Perplexity (2–4 min/relatório; API Sonar US$ 2/US$ 8 por 1M + US$ 5/1.000 buscas) | Gemini Deep Research, ChatGPT Deep Research | Pro US$ 20/mês | [Tech-Insider](https://tech-insider.org/perplexity-vs-chatgpt-vs-gemini-2026/) |
| Avatares | HeyGen Avatar IV (fotorrealista, direitos plenos) | Synthesia (US$ 18–89/mês, restrições em anúncios) | ~US$ 29/mês + créditos | [Vidico](https://vidico.com/news/heygen-vs-synthesia/) |

**Nota transversal:** a prática recomendada em 2026 valida a tese da plataforma — "roteamento que envia tarefas diferentes a modelos diferentes vence qualquer aposta em modelo único", com economia de até 75% em custo de LLM ([Iternal](https://iternal.ai/llm-selection-guide), [Coworker](https://coworker.ai/blog/ai-agent-orchestration-platform)).

## O que ainda NÃO existe — as 8 lacunas

1. **Roteamento best-of-breed comercial:** Manus/Genspark usam pipelines internos; ninguém roteia para a melhor IA de cada área como produto de consumo.
2. **Preço fixo por entregável:** a dor nº 1 documentada (Manus, Replit, Lovable, Genspark) é crédito imprevisível. Ninguém vende "um site: R$ X" fechado antes de começar.
3. **Revisões como produto:** nos agentes de IA, cada correção custa mais créditos; "N revisões incluídas + garantia" não existe.
4. **QA e responsabilidade:** nenhuma camada que *assine* a entrega; o risco fica 100% com o cliente.
5. **Marketplace agêntico é aspiração, não realidade:** Fiverr e Upwork ainda vendem humanos; experimentos como 47jobs são embrionários ([Hacker News](https://news.ycombinator.com/item?id=45264755)). A janela está aberta.
6. **Projetos multi-mídia coerentes:** "lance minha marca" (logo + site + vídeo + jingle + deck com identidade consistente) exige hoje 6+ assinaturas e um humano integrando. Nenhum orquestrador mantém um "brand brief" persistente.
7. **Direitos comerciais unificados:** licenciamento fragmentado (Udio sem download, Synthesia restrita em ads, ElevenLabs Free sem uso comercial). "Tudo que entregamos é comercialmente utilizável" seria diferencial real.
8. **Interface para leigo:** Devin quer tickets, CrewAI quer engenheiros, Lindy quer desenho de fluxo. Falta o "account manager de IA" que entrevista o cliente leigo, transforma pedido vago em briefing, orça e dispara.

**Síntese final:** os blocos técnicos existem e estão baratos (agentes desde US$ 20/mês, APIs criativas por centavos). O que não existe — em nenhum dos três grupos, no Brasil ou no mundo — é o **empacotamento comercial de agência**: preço fechado por entregável, revisões incluídas, QA, direitos garantidos e consistência de marca, sobre um roteador best-of-breed. Essa é a posição vaga que o `02-plano-mestre.md` ocupa.
