# Plano Mestre — Plataforma de Serviços 100% Automatizada por IA

**Data-base:** agosto/2026 · **Status:** blueprint para decisão e construção do MVP

> **Conceito em uma frase:** o cliente descreve o que precisa em linguagem natural (texto ou áudio, como num WhatsApp) e recebe o serviço **pronto** — site, vídeo, logo, apresentação, planilha, contrato, campanha — executado por um time de agentes de IA orquestrados, com preço fechado na hora, entrega em minutos/horas e revisões por chat. Não é um marketplace que *encontra alguém* para fazer: é um **delivery de serviço** que *faz*.

---

## 1. Visão e posicionamento

### 1.1 A lacuna de mercado

O mercado hoje se divide em três grupos, e nenhum entrega o ciclo completo:

| Grupo | Exemplos | O que entregam | O que falta |
|---|---|---|---|
| Marketplaces de humanos | GetNinjas, Workana, 99Freelas, Fiverr, Upwork | Encontram um profissional | Dias de espera, qualidade imprevisível, negociação, preço variável |
| Marketplaces com IA assistiva | Fiverr Go, Upwork "Uma" | IA ajuda o humano a vender/produzir | O gargalo continua sendo o humano |
| Ferramentas de IA por área | Midjourney, Veo, ElevenLabs, Lovable, Gamma | Executam UMA tarefa, para quem sabe usar | O cliente comum não sabe qual usar, nem como, nem integra os resultados |

**A lacuna:** ninguém — especialmente no Brasil — oferece um balcão único onde o pedido em linguagem natural vira serviço entregue, com a **melhor IA de cada área** trabalhando em conjunto, preço fechado e garantia de qualidade. É o espaço entre "contratar um freelancer" e "aprender 10 ferramentas de IA". A pesquisa de mercado (`01-pesquisa-mercado.md`) confirmou essa lacuna em detalhe: são 8 vazios documentados, entre eles preço fixo por entregável (a dor nº 1 dos agentes de IA atuais, todos cobrando créditos imprevisíveis), QA que assina a entrega, revisões incluídas, direitos comerciais garantidos e consistência de marca entre mídias.

### 1.2 Posicionamento

- **Para o cliente:** "Peça como pedir a um funcionário. Receba como de uma agência. Pague como um aplicativo."
- **Contra marketplaces:** entrega em minutos, não dias; preço fixo na hora, sem orçamentos nem leilão.
- **Contra ferramentas de IA:** zero curva de aprendizado; o cliente não precisa saber o que é "prompt".
- **Mercado inicial:** PMEs brasileiras (30+ milhões de CNPJs, maioria sem acesso a agência ou designer) — atendimento em português, pagamento via Pix, entrada pelo WhatsApp.

---

## 2. Como funciona — o fluxo automático ponta a ponta

```
Cliente pede (chat/voz/WhatsApp)
        │
        ▼
[1] AGENTE DE ATENDIMENTO  → entende o pedido, faz no máx. 3 perguntas
        │                     essenciais (nunca um formulário)
        ▼
[2] MOTOR DE ESCOPO E PREÇO → decompõe em tarefas, estima custo de
        │                     execução, devolve proposta com preço fixo
        │                     e prazo em < 60 segundos
        ▼
[3] PAGAMENTO (Pix/cartão)  → aprovação libera a execução
        │
        ▼
[4] ORQUESTRADOR (maestro)  → roteia cada tarefa para o agente
        │                     especialista + melhor modelo da área;
        │                     execução em PARALELO
        ▼
[5] QA AUTOMÁTICO           → um agente crítico avalia cada entregável
        │                     contra o pedido original (rubrica);
        │                     reprova → refaz sozinho (até 2 ciclos)
        ▼
[6] ENTREGA                 → página de entrega com preview, arquivos
        │                     e botão "pedir ajuste"
        ▼
[7] REVISÕES POR CHAT       → "deixa o fundo azul", "encurta o texto"
                              → reexecução dirigida, incluída no preço
```

**Humano no circuito (interno, não do cliente):** nas fases iniciais, um operador humano revisa amostras e todos os pedidos sinalizados pelo QA como de baixa confiança. A meta é começar com ~30% de revisão humana e cair para <5% conforme as rubricas amadurecem. O cliente nunca precisa saber — para ele a plataforma "simplesmente funciona".

---

## 3. Arquitetura de orquestração

### 3.1 Camadas

1. **Atendimento** — agente conversacional (Claude) com memória do cliente (marca, logo, tom de voz, pedidos anteriores). É a única interface: chat web + WhatsApp.
2. **Orquestração** — o maestro (Claude Agent SDK) decompõe o pedido num grafo de tarefas com dependências, dispara subagentes em paralelo e consolida.
3. **Especialistas** — um subagente por área (§4), cada um com as ferramentas/APIs do seu domínio e "skills" (playbooks) versionadas — o conhecimento de como fazer bem cada tipo de serviço fica em skills, não no código.
4. **QA** — agente crítico independente (nunca o mesmo que produziu) com rubrica por tipo de entregável; produz nota + laudo; abaixo do corte, devolve para refação com instruções específicas.
5. **Entrega e memória** — armazenamento dos entregáveis, histórico e perfil de marca do cliente (reuso em pedidos futuros = fidelização e margem crescente).

### 3.2 Por que essa arquitetura vence

- **Roteamento por área** = usa sempre a melhor IA de cada domínio (ninguém é bom em tudo; plataformas presas a um único modelo entregam qualidade média).
- **Skills versionadas** = a qualidade melhora sem reescrever a plataforma; cada serviço novo é uma skill nova, não um projeto de engenharia.
- **QA adversarial** = ataca o maior risco do modelo de negócio (alucinação/qualidade) com um mecanismo estrutural, não com esperança.
- **Memória de marca** = a segunda compra é melhor e mais barata que a primeira — o inverso dos marketplaces, onde cada pedido recomeça do zero.

---

## 4. As melhores IAs por área (data-base ago/2026 — revisar trimestralmente)

| Área | Ferramenta principal | Alternativas | Uso na plataforma |
|---|---|---|---|
| Orquestração e atendimento | Claude (Agent SDK) | OpenAI Agents SDK | Maestro, atendimento, QA |
| Texto, estratégia, contratos | Claude (topo de linha) | GPT-5.x | Copys, planos, documentos |
| Código, sites, apps | Claude Code | Devin, Lovable, Replit Agent | Sites e landing pages |
| Imagem e design | FLUX / Midjourney / GPT Image | Ideogram (texto em imagem) | Logos, artes, posts |
| Vídeo | Veo 3 | Runway, Kling, Pika | Vídeos de divulgação |
| Avatar/apresentador | HeyGen | Synthesia | Vídeos institucionais |
| Voz e dublagem | ElevenLabs | — | Locução, áudio de anúncios |
| Música | Suno | Udio | Trilhas, jingles |
| Apresentações | Gamma + geração própria (pptx) | — | Decks comerciais |
| Planilhas e docs Office | Skills próprias (xlsx/docx/pdf) | — | Relatórios, propostas |
| Pesquisa de mercado | Deep research (Claude/Perplexity) | — | Estudos, análises |
| Automação/integrações | n8n / MCP | Zapier | Conectar sistemas do cliente |

*(A tabela definitiva com preços de API e fontes está no relatório `01-pesquisa-mercado.md`.)*

**Princípio de engenharia:** cada especialista chama a ferramenta da sua área **por trás de uma interface própria** (adapter). Trocar Midjourney por FLUX (ou o que liderar em 2027) é trocar um adapter — a plataforma não casa com fornecedor nenhum.

---

## 5. Stack técnica recomendada

| Camada | Escolha | Justificativa |
|---|---|---|
| Frontend | Next.js (Vercel) | Padrão de mercado, SEO, rápido de evoluir |
| Backend/dados | Supabase (Postgres + Auth + Storage + Edge Functions) | Já disponível no seu ambiente; auth, banco e arquivos prontos |
| Motor de agentes | Claude Agent SDK (workers Node) | Orquestração, subagentes, skills e MCP nativos |
| Fila de execução | Fila em Postgres (pg-boss) → migrar se escalar | Simplicidade primeiro |
| Pagamentos | Stripe ou Pagar.me/Asaas (Pix + cartão + assinatura) | Pix é obrigatório no Brasil |
| WhatsApp | API oficial (Meta) via provedor (ex.: Z-API/Twilio) | Canal nº 1 da PME brasileira |
| Observabilidade | Logs por pedido + custo de tokens por pedido | Margem é gerida por pedido |

---

## 6. Modelo de negócio

### 6.1 Precificação

- **Por entregável, preço fixo** (ex.: logo + identidade R$ 149; landing page R$ 299; vídeo 30s R$ 199; apresentação R$ 129; pacote lançamento R$ 499). Preço fechado **antes** do pagamento, sempre.
- **Assinatura PME** (ex.: R$ 297–997/mês): X créditos de serviço por mês + memória de marca + prioridade. A assinatura é o produto principal a partir da fase 2 — receita recorrente e retenção.
- **Regra de margem:** custo direto de IA por pedido (tokens + APIs de mídia) deve ficar **< 15% do preço**. O motor de escopo calcula o custo estimado antes de precificar; pedidos fora da curva sobem preço ou são recusados automaticamente.

### 6.2 Unit economics (ordem de grandeza, a validar no MVP)

- Logo/identidade: custo de IA ~R$ 3–10 → preço R$ 149 → margem bruta >90%
- Vídeo 30s (Veo): custo ~R$ 15–40 → preço R$ 199 → margem ~80%
- Landing page: custo ~R$ 5–15 → preço R$ 299 → margem >90%
- O custo real por pedido é medido desde o dia 1 (observabilidade §5) — sem isso não há gestão de preço.

### 6.3 Garantia

"Ajustes ilimitados por 7 dias ou dinheiro de volta." Com custo marginal de refação perto de zero, a garantia agressiva é barata para nós e mata a maior objeção contra IA (medo de qualidade).

---

## 7. Roadmap

### Fase 0 — Validação (2–4 semanas)
- Landing page + WhatsApp. **Atendimento por trás pode ser semi-manual** (você + Claude Cowork/Code executando): valida demanda, preço e qualidade antes de automatizar.
- 3 serviços só: **apresentação comercial, logo+identidade, landing page**.
- Meta: 20 pedidos pagos, NPS e custo real por pedido medidos.

### Fase 1 — MVP automatizado (4–8 semanas)
- Fluxo §2 completo para os 3 serviços: escopo+preço automático, pagamento, orquestrador, QA, página de entrega, revisões por chat.
- Revisão humana interna em 100% das entregas no início, caindo com as métricas.

### Fase 2 — Expansão de verticais (contínuo)
- Um serviço novo por vez = uma skill nova + rubrica de QA nova. Ordem sugerida: vídeo de divulgação → posts/social (assinatura mensal) → planilhas e relatórios → tradução/legendagem → contratos e documentos padronizados.
- Lançar **assinatura PME**.

### Fase 3 — Plataforma
- API e white-label (agências revendem), agentes que operam rotinas contínuas para o cliente (social media autônomo, relatórios mensais), voz como interface completa.

**Regra do roadmap:** nunca lançar vertical nova enquanto a taxa de aprovação sem retrabalho da anterior estiver abaixo de 85%.

---

## 8. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Qualidade/alucinação | QA adversarial estrutural (§3), revisão humana decrescente, garantia de 7 dias |
| Custo de IA volátil | Margem-alvo <15%, medição por pedido, adapters para trocar de fornecedor |
| Dependência de fornecedor | Arquitetura multi-modelo por design (§4) |
| LGPD / dados do cliente | Dados no Supabase (região BR quando possível), sem treinar modelos com dados de cliente, termos claros |
| Incumbentes (Fiverr/Canva/OpenAI) lançarem o mesmo | Vantagens locais: português, Pix, WhatsApp, memória de marca, nicho PME BR — e velocidade |
| Direitos autorais de mídia gerada | Usar fornecedores com indenização comercial (ex.: linhas "commercially safe"), termos de uso explícitos |

---

## 9. Por que "melhor que todas" — resumo executivo

1. **Entrega, não indicação** — o concorrente entrega um contato; nós entregamos o serviço pronto.
2. **Melhor IA de cada área, invisível** — o cliente não escolhe ferramenta; o roteador escolhe por ele, sempre a melhor do momento.
3. **Minutos e preço fixo** — contra dias e orçamento incerto dos marketplaces.
4. **Qualidade como sistema** — QA adversarial + rubricas + garantia, não promessa.
5. **Memória de marca** — cada pedido melhora o próximo; retenção que marketplace não tem.
6. **Brasil-first** — português, Pix, WhatsApp, preço de PME brasileira.
