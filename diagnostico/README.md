# Diagnóstico · Pesquisa Clínica

Aplicativo de **apoio à decisão para médicos**. Você digita a **doença suspeita + dados do paciente** e o sistema faz uma **pesquisa detalhada e adaptada àquela doença**, consultando **várias bases públicas/gratuitas ao mesmo tempo**, para:

1. **Não deixar passar nada no diagnóstico** — o que perguntar, examinar, pedir de exames, sinais de alarme e diferenciais que não podem ser esquecidos;
2. **Tratar minimizando riscos** — condutas por diretriz, ajustes por idade/comorbidade/gestação e segurança de medicamentos.

O relatório **cruza os dados do paciente** contra os critérios da doença, aponta **o que ainda falta perguntar/pedir** (o que o médico pode estar esquecendo) e entrega uma **aproximação diagnóstica** — sempre com **fontes reais e link**.

> ⚕️ **Não substitui o julgamento clínico.** É ferramenta de apoio para profissionais. Confira sempre doses e condutas em fonte oficial/bulário.

É um **arquivo único** (`index.html`, HTML/CSS/JS puro, sem dependências) — abre direto no navegador do PC ou do celular, no mesmo estilo do simulador deste repositório.

---

## Como funciona

Pipeline por pesquisa: **normalizar termo (MeSH) → estratégia de busca (IA) → consultar todas as fontes → síntese do relatório (IA, em tempo real) → salvar**.

- **IA (Anthropic/Claude)** chamada direto do navegador com **a sua chave de API** (fica só no seu dispositivo). Modelo padrão `claude-sonnet-5`; opção "profunda" usa `claude-opus-4-8`.
- **Literatura e bases** chamadas direto do navegador (grátis, sem chave):
  - **PubMed** e **NCBI Bookshelf/StatPearls**, **OMIM/MedGen** (genética/raras) — via NCBI E-utilities
  - **Europe PMC** (MEDLINE + texto completo + preprints)
  - **openFDA** (bulas: indicações, contraindicações, doses, interações)
  - **ClinicalTrials.gov** (ensaios)
  - **MedlinePlus** (tópicos em espanhol)

### Relatório — 13 seções fixas
Visão geral · Critérios diagnósticos e escores · **Anamnese completa (perguntas que não podem faltar)** · Exame físico direcionado · Exames complementares · 🚩 Sinais de alarme · Diferenciais que não podem ser esquecidos · **Cruzamento com o paciente e aproximação diagnóstica** · **Checklist de verificação (interativo)** · Tratamento · Monitoramento e sinais de piora · Armadilhas comuns · Referências.

Cada citação `[PMID …]` / `[NCT…]` vira **link real**; toda menção a medicamento traz "confira dose no bulário/fonte oficial".

---

## Uso rápido

1. Abra `diagnostico/index.html` no navegador (ou hospede — veja abaixo).
2. Em **⚙️ Configurações**, cole sua **chave de API Anthropic** (recomendado criar uma chave com **limite de gasto**).
3. Na home, clique **Exemplo — Mieloma Múltiplo** para ver o fluxo, ou **Nova pesquisa**.
4. Sem chave/rede? Use **"Ver relatório-amostra (offline)"** para conhecer o formato.

> **Exemplo semente:** o sistema já vem com **mieloma múltiplo** pré-cadastrado (caso pré-preenchido + relatório-amostra offline). Para "cadastrar" outra doença é só usar o formulário — nada é específico por doença no código.

---

## Nuvem (Supabase) — login e histórico *(opcional)*

Sem Supabase, o app funciona **sem login** (sem histórico salvo). Para salvar o histórico na nuvem, configure um projeto Supabase (uma vez):

1. Crie um projeto em supabase.com e copie **Project URL** e **anon/publishable key**.
2. No **SQL Editor**, rode o conteúdo de [`supabase/001_pesquisas.sql`](supabase/001_pesquisas.sql) — cria a tabela `pesquisas` e as políticas **RLS** (cada usuário só vê as próprias pesquisas).
3. Em **Authentication → Sign In / Up → Email**, **desligue "Confirm email"** (senão o cadastro não devolve sessão e o login falha com `email_not_confirmed`). O app trata os dois casos, mas desligar simplifica.
4. No app, em **⚙️ Configurações → Nuvem**, cole **Project URL** e **anon key**. Cadastre-se/entre.

**Segurança:** só a *anon key* (pública) fica no app; a fronteira de segurança é a **RLS**. A chave da Anthropic **nunca** vai para o Supabase. **LGPD:** identifique o paciente **apenas por iniciais/código** (o formulário não tem campo de nome completo); há botão **Excluir** para remover os dados de uma pesquisa.

**Prova de RLS (recomendada após configurar):** crie dois usuários; confirme que o segundo **não** vê as pesquisas do primeiro.

---

## Hospedagem (para usar no celular)

O jeito mais simples é **GitHub Pages**: habilite Pages para este repositório e o app fica em
`https://<usuario>.github.io/Transcriptor/diagnostico/`. Isso dá uma origem https real (melhor que `file://`).
As três integrações (Anthropic com o header `anthropic-dangerous-direct-browser-access`, E-utilities/Europe PMC/openFDA/ClinicalTrials/MedlinePlus) enviam CORS aberto e funcionam do navegador.

---

## Limitações importantes

- **Interações medicamentosas:** a API oficial de interações do NLM/RxNav foi **descontinuada em jan/2024**. Não há base oficial gratuita de interações. O app faz o **melhor esforço** (seções de bula do openFDA + conhecimento do modelo, sempre marcado "confirme") — **não é um verificador validado**.
- Fontes podem estar temporariamente fora do ar: nesse caso o relatório é gerado **sem verificação na literatura**, com aviso visível, e **nunca inventa citações**.

---

## Verificação (desenvolvimento)

Testes que rodam **sem internet** (mocks/`page.route`), com Playwright + Chromium local:

```bash
# instale o playwright-core em algum diretório e aponte PW_CORE para ele:
PW_CORE=/caminho/node_modules/playwright-core/index.js \
  node verify/e2e.mjs        # esqueleto, autoteste, relatório, impressão, mobile
PW_CORE=... node verify/pipeline.mjs   # pipeline completo (estratégia→fan-out→streaming→relatório) com fixtures
```

- **Autoteste embutido** (sem rede): botão em ⚙️ Configurações → "Rodar autoteste" — 23 checagens das funções puras (parser SSE, mdRender/XSS, splitSections, checklist, extractJson, fallbackQueries, buildRefs, needsRefresh, dedupe, throttle, esc).
- **Mock local da IA** para testar no navegador sem gastar créditos: `node verify/mock_anthropic.mjs` e aponte "Base da API" para `http://127.0.0.1:8787` nas Configurações.

---

## Apps parecidos (pesquisa de mercado)

Afya **Whitebook** (nº 1 no Brasil; ferramenta DDX de diagnóstico diferencial), **OpenEvidence** (IA com citações NEJM/JAMA, gratuito para profissionais verificados), **UpToDate**, **Isabel DDx**, **Glass Health**. Nenhum reúne exatamente **doença → pesquisa multi-fonte adaptada ao paciente + checklist anti-erro em pt-BR** — que é o que este app faz.

---

## Estrutura

```
diagnostico/
├── index.html                 # o app inteiro
├── README.md
├── supabase/001_pesquisas.sql # tabela + RLS
└── verify/                    # harness de teste (não é carregado pelo app)
    ├── e2e.mjs
    ├── pipeline.mjs
    └── mock_anthropic.mjs
```

### Fase 2 (futuro)
Bases que exigem login/proxy — **ICD-11 (OMS)**, **Orphanet/HPO** (doenças raras/fenótipo), **UMLS** — via uma **Edge Function** no Supabase que guarda os segredos no servidor e se pluga no mesmo registry de fontes.
