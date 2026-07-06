# Relatório "Custos / Despesas" (saída da ferramenta do curso)

Fonte: `Custos e despesas.pdf` (Drive, gerado 05/06/2026 pela "Planilha Investimento Rural
– Procedimento Simplificado"). Mesmo cliente-exemplo do relatório de capacidade de
pagamento: CLIENTE-EXEMPLO A.P.M. (nome/CPF pseudonimizados — LGPD; original só em
materiais/, fora do git), PF, agência CRUZ DAS ALMAS-BA.
Extração completa, sem truncamento (4 páginas).

## Estrutura do relatório

Linhas por atividade, agrupadas em categorias, colunas Atual + Ano 1..Ano 30:

| Categoria | Linhas no exemplo |
|---|---|
| Custos Agrícolas | Café Conilon Sequeiro (1) [linha principal]; Café Conilon Sequeiro (1) [2ª linha, só "Atual"]; Café Arábica Sequeiro |
| Custos Pecuários | Bovinocultura de Leite |
| Outras Atividades | Apicultura |
| Outras Despesas | Conservação de Edif./Instal./Maq./Equip./Impl./Veíc. (**2,5% s/ Total**); Impostos (**0,2% sobre o valor total da terra nua**) |
| **Total** | soma geral |

## REGRAS FIXAS DA FERRAMENTA (descobertas — usar nos motores)

1. **Conservação de benfeitorias/máquinas = 2,5% sobre o valor total** desses bens.
   No exemplo: 5.610,00/ano constante → valor dos bens = 224.400,00.
2. **Impostos = 0,2% sobre o valor total da terra nua.**
   No exemplo: 3.400,00/ano constante → terra nua avaliada em 1.700.000,00.
3. Horizonte do relatório de custos: **30 anos** (o de capacidade de pagamento mostra 12).
4. Culturas têm flag de continuidade ("Não" aparece na transição) — o café zera a partir
   do Ano 12 → vida útil da lavoura ≈ 11 anos neste exemplo (a confirmar nos vídeos).

## Números do exemplo (golden test)

| Linha | Atual | Ano 1 | Ano 2 | Ano 3 | Ano 12 | Ano 21+ |
|---|---|---|---|---|---|---|
| Café Conilon Sequeiro | 151.200,00 | 151.200,00 | 151.200,00 | 151.200,00 | 0,00 | 0,00 |
| Café Conilon Sequeiro (2ª linha) | 25.200,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| Café Arábica Sequeiro | 0,00 | 0,00 | 75.600,00 | 151.200,00 | 0,00 | 0,00 |
| **Custos Agrícolas** | 176.400,00 | 151.200,00 | 226.800,00 | 302.400,00 | 0,00 | 0,00 |
| Bovinocultura de Leite | 40.000,00 | 159.931,80 | 235.355,40 | 221.373,60 | 240.353,40 | 222.839,40 |
| Apicultura | 0,00 | 18.000,00 | 18.000,00 | 18.000,00 | 18.000,00 | 18.000,00 |
| Conservação (2,5%) | 5.610,00 | 5.610,00 | 5.610,00 | 5.610,00 | 5.610,00 | 5.610,00 |
| Impostos (0,2% terra nua) | 3.400,00 | 3.400,00 | 3.400,00 | 3.400,00 | 3.400,00 | 3.400,00 |
| **Total** | **225.410,00** | **338.141,80** | **489.165,40** | **550.783,60** | **267.363,40** | **249.849,40** |

Consistência cruzada: os totais Atual..Ano 12 batem exatamente com a linha "Custos Totais"
do relatório de capacidade de pagamento (`relatorio-capacidade-pagamento.md`). ✓

Observações finas:
- Café Arábica entra no Ano 2 com **metade** do custo pleno (75.600 = 151.200/2) → plantio
  em implantação; custo pleno a partir do Ano 3.
- Bovinocultura de Leite varia ano a ano (159.931,80 → 235.355,40 → 221.373,60 → ...) —
  reflexo da evolução do rebanho; estabiliza em 240.353,40 e cai para 222.839,40 no Ano 21
  (rebanho estabilizado). Detalhe vem do relatório de evolução de rebanho.
- 2ª linha "Café Conilon Sequeiro" com 25.200 só no Atual: provável custo de manutenção de
  lavoura jovem pré-existente (a confirmar nos vídeos).
