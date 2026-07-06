# Relatório "Bovinocultura de Leite" (evolução de rebanho + indicadores)

Fonte: `Evolução rebanho de leite.pdf` (Drive, gerado 05/06/2026 pela "Planilha Investimento
Rural – Procedimento Simplificado"). Mesmo cliente-exemplo: CLIENTE-EXEMPLO A.P.M. (PF,
pseudonimizado — LGPD).
Extração completa, sem truncamento (4 páginas). Horizonte: Atual + Ano 1..20.

## Parte I — Evolução do Rebanho Bovino

Categorias animais (linhas): TOUROS, MATRIZES, NOVILHAS, NOVILHOS, GARROTAS, GARROTES,
BEZERRAS, BEZERROS. Seções: A) Composição do Rebanho; B) Aquisições; C) Mortalidade;
D) Vendas (com NOVILHOS P/ABATE e P/REPRODUÇÃO separados); E) Total de U.A.

### Números do exemplo (golden test — composição)

| Categoria | Atual | Ano 1 | Ano 2 | Ano 3 | Ano 5 | Ano 6+ (estável) |
|---|---|---|---|---|---|---|
| Touros | 1 | 1 | 2 | 2 | 2 | 2 |
| Matrizes | 20 | 20 | 51 | 48 | 52 | 52 |
| Novilhas | 5 | 5 | 2 | 7 | 8 | 7 |
| Garrotas | 5 | 5 | 17 | 17 | 17 | 17 |
| Garrotes | 0 | 0 | 1 | 1 | 1 | 1 |
| Bezerras | 9 | 18 | 18 | 17 | 18 | 18 |
| Bezerros | 9 | 18 | 18 | 17 | 18 | 18 |
| **Total cabeças** | **49** | **67** | **109** | **109** | **116** | **115** |
| **Total U.A.** | 34 | 72* | 76 | 77 | 83 | 82 |

Aquisições (só no Atual/implantação): 1 touro + 30 matrizes (subtotal 32 U.A.).
Mortalidade típica/ano: 1 matriz, 1 garrota, 1 bezerra, 1 bezerro (~4 cab.).
Vendas/ano (estável): 6 matrizes (descarte), 9 garrotas, 1 garrote, 18 bezerros (~34 cab.).
*Composição A mostra 40 U.A. no Ano 1, mas linha E (total) mostra 72 — a diferença é a
aquisição de 32 U.A.; investigar na ferramenta como A e E se relacionam no ano da compra.

## Parte II — INDICADORES TÉCNICOS (coeficientes-fonte dos motores)

| Indicador | Anos 1–12 | Ano 13+ |
|---|---|---|
| Parição | **70,0%** | 75,0% |
| Mortalidade bezerros(as) | **6,0%** | 6,0% |
| Mortalidade garrotes(as) | **3,0%** | 3,0% |
| Mortalidade bovinos adultos | **2,0%** | 2,0% |
| Descarte matriz | 0,0% | 0,0% |
| Período de ordenha | **270 dias** | 210 dias |
| Produção leite/vaca/dia | **12,0 L** | 8,0 L |
| Relação leite/queijo | 10,0 | 10,0 |
| Relação touro/vaca | **30** | 30 |
| % venda bezerros | 100% | 0% |
| % venda bezerras | 0% | 0% |
| % venda garrotes | 100% | 0% |
| % venda garrotas | 50% | 0% |
| % venda novilhos p/reprod. | 100% (a partir Ano 2) | 0% |

(Nota: a mudança nos indicadores do Ano 13+ coincide com o projeto zerando o rebanho no
relatório a partir do Ano 13/14 — parece ser o comportamento pós-horizonte da ferramenta,
não uma regra de manejo. Confirmar nos vídeos.)

## Produção e financeiro (golden test)

| Item | Ano 1 | Ano 2 | Ano 3 | Ano 5 | Estável (6–13) |
|---|---|---|---|---|---|
| Comercialização de leite (L) | 79.380 | 116.640 | 110.160 | 116.640 | 116.640 |
| Salário pecuária (cabeça/oper. = 1.518) | 26.444 | 43.020 | 43.020 | 45.783 | 45.388 |
| Receita anual rebanho | 228.474,00 | 336.222,00 | 316.248,00 | 346.932,00 | 343.362,00 |
| Custo anual rebanho | 26.443,56 | 43.020,12 | 43.020,12 | 45.782,88 | 45.388,20 |
| Utilizando custo padrão | Sim | | | | |

## Fórmulas CONFIRMADAS por triangulação (engines/rebanho_leite.py, 15 testes verdes)

- **Leite** = round(matrizes × parição 70%) lactantes × 12 L × 270 dias — bate anos 2,3,5
  ao litro (arredondamento half-up: 35,7→36; 33,6→34; 36,4→36). Ano 1 (formação): média
  de matrizes sem arredondar lactantes (35 × 0,7 = 24,5 → 79.380 L) [PROVÁVEL].
- **Preço do leite = R$ 2,30/L** e preços de venda (matriz 3.570, garrota 2.730, garrote
  2.100, bezerro 1.500 — a tabela do orçamento!) reproduzem as receitas ao centavo:
  Ano 1 = 79.380×2,30 + 3×3.570 + 3×2.730 + 18×1.500 = 228.474,00 ✓
  Ano 2 = 116.640×2,30 + 4×3.570 + 9×2.730 + 1×2.100 + 18×1.500 = 336.222,00 ✓
- **Custo de mão de obra = R$ 394,68/cabeça/ano** (= 26% × salário mínimo 1.518 —
  interpretação do rótulo "CABEÇA/OPER.=1518" [PROVÁVEL]; valor bate os 5 anos ✓).

## Fórmulas ainda deduzidas (validar nos vídeos e no binário)

1. **Leite (L/ano) = matrizes em lactação × produção/dia × dias de ordenha**
   Ano 2: 116.640 = 36 × 12 × 270 → 36 lactantes ≈ 51 matrizes × 70% parição ✓
   Ano 1: 79.380 = 24,5 × 12 × 270 → transição da compra das 30 matrizes no meio do ciclo.
2. **Custo padrão de mão-de-obra pecuária = R$ 1.518 × nº de cabeças/operação** (rótulo
   "SAL. PECUARIA -CABEÇA/OPER.=1518"; flag "utilizando custo padrão: Sim").
3. RAÇÃO e VACINAS/MEDICAMENTOS/SAIS zerados neste exemplo (o exemplo `.CUSTEIOPECUARIO`
   "com ração" deve preencher essas linhas).
4. Receita = leite × preço + vendas de animais × preços por categoria (preços não aparecem
   neste relatório — estão na ferramenta/vídeos).
5. Cruzamento OK com os outros relatórios: Receitas Totais Ano 1 (510.474) − rebanho
   (228.474) = 282.000 de café+apicultura; Custos "Bovinocultura de Leite" no relatório de
   custos (159.931,80 no Ano 1) ≠ "custo anual rebanho" daqui (26.443,56) → o relatório de
   custos soma outras parcelas (alimentação/pastagem etc.) — decompor nos vídeos.
