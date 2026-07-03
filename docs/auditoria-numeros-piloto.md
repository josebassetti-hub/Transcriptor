# Auditoria dos números do relatório-piloto (estética/beleza — SP)

Auditoria número a número do relatório gerado em 03/07/2026, motivada por duas
suspeitas levantadas pelo usuário — ambas procedentes. Para cada número: o que
ele **realmente** mede, a direção do viés e o veredito.

## Respostas diretas às duas perguntas

**"Uma empresa com vários CNAEs é contada duas vezes?"**
Não, pelo desenho atual: as consultas filtram pelo **CNAE principal**, e cada
estabelecimento tem exatamente um principal — então um mesmo CNPJ nunca é
contado nos dois CNAEs do setor ao mesmo tempo. O risco de dupla contagem só
existiria ao incluir os **CNAEs secundários** (uma empresa poderia bater em
9602-5/01 e 9602-5/02 simultaneamente), e a consulta nova (C) trata isso com
`COUNT(DISTINCT cnpj_basico)`.

**"E a empresa que faz beleza mas registrou outro CNAE como principal?"**
Essa é a distorção real e é de **subcontagem**: quem tem beleza apenas como
atividade secundária ficava de fora. A consulta C mede exatamente quantas são
(deduplicadas, excluindo as já contadas pelo principal), e o relatório passa a
exibir a faixa: "N empresas pelo CNAE principal + M adicionais pela secundária".

## Auditoria número a número

| Nº no relatório | O que mede de fato | Viés | Veredito |
|---|---|---|---|
| **380.890** (universo) | **Estabelecimentos** ativos com CNAE principal 9602-5 em SP — cada filial conta 1 | Superconta empresas (filiais); subconta atividade (secundários de fora) | 🔧 **Corrigir**: reportar empresas (`DISTINCT cnpj_basico`) e estabelecimentos lado a lado (consulta A2) |
| **80.728** (ICP) | Estabelecimentos ME/EPP com 2+ anos | Mesmos vieses acima; e compara unidade errada com o CEMPRE (que conta **empresas**) | 🔧 **Corrigir**: ICP passa a ser contado em empresas |
| **12.880** (CEMPRE) | Empresas "ativas de fato" pela metodologia do IBGE, ano-base 2021 | Subconta (critérios de atividade mais duros; MEIs parcialmente fora); defasado 5 anos | ✅ Mantém, como âncora inferior — agora comparável (empresa vs empresa) |
| **R$ 25,9 bi / CAGR 13,3%** (PAS) | Receita formal do grupo "serviços pessoais" (inclui lavanderias, funerárias etc.) | Premissa de 50% beleza não verificada na própria PAS | ⚠️ Manter com premissa declarada; refinar com a abertura por classe da publicação da PAS |
| **25% atividade → 20.182 operantes** | Premissa, ancorada na razão CEMPRE/cadastro — mas essa razão comparava empresas (CEMPRE) com estabelecimentos (cadastro) | A base errada da razão distorcia a âncora | 🔧 **Recalibrar** com a contagem de empresas da A2 + tabela de sensibilidade no relatório |
| **Ticket R$ 280 mil** | Premissa de receita média por empresa operante | 96% do ICP é ME (teto legal de faturamento: R$ 360 mil/ano) — média de 280 mil é agressiva | 🔧 Tabela de sensibilidade (150/280/360 mil) na seção 6; recalibrar após A2 |
| **55–66 mil aberturas/ano** | Aberturas de estabelecimentos de TODOS os portes e idades — na prática ~80% MEI | Não contradiz o ICP (universos diferentes), mas o texto sugeria "expansão da base de clientes", sendo que MEI está fora do ICP | 🔧 **Corrigir**: separar MEI × não-MEI (consulta B2) e reescrever o texto |
| **36 mil fechamentos em 2025** | Baixas/inaptidões REGISTRADAS — baixas demoram meses/anos para entrar no cadastro | Último ano sistematicamente subcontado ("lag de baixas") | 🔧 Nota automática quando o último ano desvia do padrão |

## Sobre a aparente contradição "66 mil aberturas vs 20 mil empresas-alvo"

Não é contradição — são recortes diferentes do mesmo mercado:

```
380.890 estabelecimentos ativos (todos os portes/idades)
   └─ 290.896 MEI (76%)  ← é daqui que vem a maior parte das ~60 mil aberturas/ano
   └─  89.994 ME/EPP/DEMAIS
        └─ 80.728 ME/EPP com 2+ anos (ICP cadastral)
             └─ ~20 mil "operantes" (premissa de atividade de 25%)
```

O problema era de **comunicação e de unidade** (estabelecimento vs empresa), não
de aritmética. As consultas v2 alinham as unidades e o relatório passa a mostrar
a pirâmide explicitamente.

## Correções aplicadas nesta rodada

1. Consulta **A2**: empresas (`DISTINCT cnpj_basico`) + estabelecimentos por CNAE × porte × idade.
2. Consulta **C**: empresas com o CNAE do setor **apenas como secundário** (dedup, sem interseção com o principal).
3. Consulta **B2**: dinâmica separada MEI × não-MEI.
4. Motor: ICP em empresas; tabela de sensibilidade (ticket × taxa de atividade); nota de lag de baixas; nota de CNAE secundário; limitações ampliadas.

Ressalva conhecida da A2: a faixa de idade é do estabelecimento; uma empresa com
matriz antiga e filial nova pode aparecer em duas faixas (dupla contagem marginal
entre faixas, não no total por porte). Aceitável para o piloto; a v2 do produto
resolve fixando a idade pela matriz.
