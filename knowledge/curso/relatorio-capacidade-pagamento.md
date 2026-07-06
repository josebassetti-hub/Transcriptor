# Relatório "Capacidade de Pagamento" (saída da ferramenta do curso)

Fonte: `Capacidade de pagamento.pdf` (Drive, exemplo gerado em 05/06/2026 pela ferramenta
**"PLANILHA INVESTIMENTO RURAL — PROCEDIMENTO SIMPLIFICADO"**).
Cliente-exemplo: CLIENTE-EXEMPLO A.P.M. (pseudonimizado — LGPD), agência CRUZ DAS
ALMAS-BA, projeto 01/07/2026.

## O que este documento prova

1. Os arquivos `.INVRUR` são o formato de salvamento da ferramenta "Planilha Investimento
   Rural – Procedimento Simplificado" (a mesma família do Automatizador para Projetistas).
2. O relatório de capacidade de pagamento projeta **12 anos** (Atual + Ano 1..12).
3. Estrutura de linhas do relatório (ordem exata):
   - Receitas Totais
   - Custos Totais
   - **Rédito Operacional** = Receitas − Custos
   - Encargos Operações **em SER** (dívidas já existentes do cliente)
   - Encargos Operações **em Estudo** (o financiamento novo sendo proposto)
   - **Lucro Operacional** = Rédito − Encargos(SER) − Encargos(Estudo)
   - **CAPACIDADE DE PAGAMENTO** (= Lucro Operacional neste exemplo)
   - Amortização Operações em SER
   - Amortização Operações em Estudo
   - **PERCENTUAL DE UTILIZAÇÃO** = (amortizações+encargos?) / capacidade — fórmula exata a
     confirmar nos vídeos; no exemplo fica sempre entre **14,6% e 59,96%**, nunca ≥ 60%.

## Números do exemplo (para golden test futuro)

| Especificação | Atual | Ano 1 | Ano 2 | Ano 3 | Ano 12 |
|---|---|---|---|---|---|
| Receitas Totais | 342.000,00 | 510.474,00 | 744.222,00 | 850.248,00 | 877.362,00 |
| Custos Totais | 225.410,00 | 338.141,80 | 489.165,40 | 550.783,60 | 569.763,40 |
| Rédito Operacional | 116.590,00 | 172.332,20 | 255.056,60 | 299.464,40 | 307.598,60 |
| Encargos em SER | — | 1.044,53 | 3.754,83 | 2.839,88 | 0,00 |
| Encargos em Estudo | — | 0,00 | 0,00 | 36.363,27 | 153.469,35 |
| Lucro Operacional | 116.590,00 | 171.287,67 | 251.301,77 | 260.261,25 | 154.129,25 |
| Amort. em SER | — | 25.000,00 | 50.000,00 | 25.000,00 | 0,00 |
| Amort. em Estudo | — | 0,00 | 0,00 | 129.000,00 | 90.265,00 |
| % Utilização | — | 14,60% | 19,90% | 59,17% | 58,56% |

Receita estabiliza em 877.362,00 do Ano 4 em diante (custos em 569.763,40) — típico de
projeto que atinge maturidade produtiva no ano 4.

## Hipóteses a confirmar nos vídeos
- [ ] Regra do banco: % de utilização deve ficar **< 60%** (o exemplo tangencia 59,96%).
- [ ] Como os "Encargos em Estudo" são calculados (juros do novo financiamento por ano).
- [ ] Carência do exemplo: amortização do novo financiamento começa no Ano 3 → carência de 2 anos.
