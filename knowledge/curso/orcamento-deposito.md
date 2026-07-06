# Orçamento de benfeitoria: Depósito de ferramentas 40 m² (golden test)

Fonte: `Orçamento depósito.xlsx` (Drive) — extração completa.

## Orçamento (modelo de inversão/benfeitoria)

| Item | Quant | Unid | Valor unit | Total |
|---|---|---|---|---|
| Areia | 2 | caçamba | 400,00 | 800,00 |
| Tijolos | 1,5 | mil | 1.050,00 | 1.575,00 |
| Blocos calha | 100 | und | 5,00 | 500,00 |
| Ferragem | 1 | verba | 1.500,00 | 1.500,00 |
| Cimento | 50 | sc | 47,00 | 2.350,00 |
| Telha | 1 | mil | 1.200,00 | 1.200,00 |
| Madeira | 1 | verba | 2.000,00 | 2.000,00 |
| Brita | 2 | m³ | 200,00 | 400,00 |
| Portão | 1 | und | 2.000,00 | 2.000,00 |
| Prego | 2 | kg | 20,00 | 40,00 |
| Tinta | 1 | lt | 200,00 | 200,00 |
| *Subtotal materiais* | | | | *12.565,00 (64%)* |
| Pedreiro | 30 | h/d | 160,00 | 4.800,00 |
| Ajudante | 30 | h/d | 80,00 | 2.400,00 |
| **Total** | | | | **19.765,00** |

Estrutura-modelo de orçamento: materiais (com % do total) + mão de obra em homens-dia.
Custo/m² implícito: 19.765/40 = 494,13 R$/m² (referência para validação de orçamentos).

## Tabela auxiliar de preços de gado (na mesma planilha) — CONFIRMADO como tabela de preços

Números soltos ao lado do orçamento, aparentam ser a régua de preços pecuários:

| Categoria | Fator | Valor intermediário | Valor final |
|---|---|---|---|
| Boi gordo | 300 (R$/arroba?) | — | — |
| Vaca | 0,85 (× boi) | 255 | 3.570,00 |
| Bezerro | 1 | 300 | 1.500,00 |
| Garrote | 1 | 300 | 2.100,00 |
| Garrota | 1,3 | 390 | 2.730,00 |

**CONFIRMADO por triangulação** (engines/rebanho_leite.py + tests): estes preços de venda
(vaca/matriz 3.570, garrota 2.730, garrote 2.100, bezerro 1.500) combinados com leite a
**R$ 2,30/L** reproduzem AO CENTAVO as receitas do relatório de bovinocultura
(228.474,00 no Ano 1; 336.222,00 no Ano 2). A DERIVAÇÃO por arroba (boi R$ 300/@, vaca
85%, 14@ etc.) segue [PROVÁVEL]; o fator solto `0,004` segue [INCERTO].
