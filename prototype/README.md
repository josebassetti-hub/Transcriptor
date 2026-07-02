# Protótipo técnico — gerador de relatório de análise de mercado

Prova de conceito do pipeline descrito na [especificação](../docs/especificacao-produto-mvp.md):
**coleta** (IBGE, Banco Central, agregados CNPJ) → **cálculo** (TAM/SAM/SOM com dupla
metodologia e triangulação) → **redação** (determinística aqui; LLM com guard-rail em
produção) → **render** (HTML autocontido com gráficos SVG, claro/escuro).

Somente biblioteca-padrão do Python — sem dependências.

## Rodar

```bash
cd prototype
python3 gerar_relatorio.py --setor setores/estetica_sp.json --modo auto
# abre saida/relatorio-estetica_sp.html no navegador
```

Modos:

| Modo | Comportamento |
|---|---|
| `auto` (padrão) | tenta as APIs reais; se a rede bloquear, cai para as fixtures |
| `live` | só APIs reais (IBGE agregados v3, Bacen SGS) — use em rede aberta |
| `fixture` | só dados de demonstração (offline) |

Quando qualquer fixture é usada, o relatório abre com um aviso de **demonstração** e o
selo de fonte de cada seção indica a proveniência. Nenhum número é inventado: o texto
analítico é gerado por template a partir do JSON de dados calculados (em produção, a
redação por LLM passa pelo mesmo guard-rail — todo número do texto precisa existir no
JSON).

## Estrutura

```
gerar_relatorio.py        orquestrador (CLI) — espelha as Edge Functions da spec
setores/estetica_sp.json  configuração do setor-piloto (CNAEs, região, ICP, fontes)
fontes/
  http_client.py          cache em disco + fallback de fixtures + proveniência
  ibge.py                 API de agregados v3 do IBGE (SIDRA)
  bcb.py                  API SGS do Banco Central
  cnpj.py                 agregados da base CNPJ (CSV demo; SQL de produção em dados/sql/)
calculos/sizing.py        top-down, bottom-up, cenários e triangulação
relatorio/render.py       HTML + SVG (paleta validada, claro/escuro, tabelas de dados)
dados/
  fixtures/               respostas de exemplo NO FORMATO REAL das APIs
  cnpj_agregados_demo.csv agregados CNPJ de demonstração (CNAE x UF x porte x idade)
  sql/agregados_cnpj_basedosdados.sql  consulta de produção (Base dos Dados/BigQuery)
```

## O que este protótipo prova

1. **O pipeline fecha de ponta a ponta**: de configuração de setor a relatório navegável,
   com citação de fonte por seção e premissas explícitas.
2. **Os conectores são os de produção**: URLs reais das APIs do IBGE e do Bacen; as
   fixtures reproduzem o formato real das respostas, então trocar para `--modo live`
   não muda o código.
3. **A base CNPJ vira agregado pequeno**: o produto nunca toca os dumps brutos em tempo
   de geração — só tabelas agregadas (ver SQL), que cabem no Postgres do Supabase.
4. **Anti-alucinação por construção**: números só saem do motor de cálculo.

## Diferenças para produção (mapeamento para a spec)

| Protótipo | Produção (Supabase) |
|---|---|
| CLI síncrona | Edge Functions em etapas (collect → compute → write → render) com status via Realtime |
| CSV de agregados demo | tabela `agg_empresas` alimentada por ETL mensal (Base dos Dados no MVP) |
| cache em disco | tabelas de cache com TTL no Postgres |
| redação por template | Claude API com guard-rail de números + citações obrigatórias |
| HTML | HTML + export PDF/PPTX com white-label |

## Dados de demonstração

Os valores das fixtures e dos CSVs são **ilustrativos** (rotulados no relatório).
A curadoria real por setor — qual tabela SIDRA dimensiona cada CNAE, participação do
segmento etc. — é o trabalho de configuração de cada setor-piloto no MVP, e fica
registrada no JSON do setor para citação exata.
