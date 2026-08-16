# SIMULAÇÃO DE CAPACIDADE DE PAGAMENTO — FNE/BNB (algoritmo oficial)

**GTK Pré-Moldados Ltda** · 16/08/2026 · Motor que replica a macro VBA `calcularAmortizacaoIndustrial` da planilha oficial do BNB (validado ao centavo em 3 projetos reais — 76/76 valores). Cenário A (regra oficial: aplicação integral no ano 1).

## Premissas (confirmadas pelo consultor)

| Parâmetro | Valor |
|---|---|
| Taxa nominal | **8,8945% a.a.** (juros mensais compostos; taxa em Currency como no VBA; sem considerar bônus de adimplência) |
| Prazo total | 144 meses (12 anos) |
| Carência testada | 12 / 24 / 36 meses (juros pagos trimestralmente na carência; capitalização dos não pagos) |
| Receita BRUTA anual | Estudo v3: ano 1 R$ 2.750.000 · ano 2 R$ 3.850.000 · anos 3–12 R$ 4.791.000 (teto EPP) |
| Custo padrão | **Faixa indicada pelo consultor: 76,72% a 84,39%** (o enquadramento exato é do sistema do BNB — resultados nos dois extremos) |
| Dívidas existentes (SER) | Nenhuma — empresa constituída em 28/04/2026 |
| Amortização | Anual (12º mês), curva **equalizada** (comprometimento igual em todos os anos, como a planilha faz nativo) |
| Janela do banco | Comprometimento da capacidade de pagamento entre **30% e 50%** |

## Resultado 1 — O pleito de R$ 4.800.000 NÃO passa em nenhuma combinação

| Custo padrão | Carência 12m | Carência 24m | Carência 36m |
|---|---|---|---|
| 76,72% (piso) | 51,3% — fora | 54,9% — fora | 61,2% — fora |
| 84,39% (teto) | 91,3–91,5% — fora | 96,8–96,9% — fora | 108,0–108,2% — fora |

## Resultado 2 — Principal MÁXIMO aprovável (comprometimento equalizado ≤ 50%)

| Custo padrão | Carência 12m | Carência 24m | Carência 36m |
|---|---|---|---|
| **76,72% (piso)** | **R$ 4.700.000** (49,9%) | **R$ 4.460.000** (50,0%) | R$ 4.090.000 (49,9%) |
| **84,39% (teto)** | R$ 3.150.000 (49,8%) | **R$ 2.990.000** (50,0%) | R$ 2.740.000 (49,9%) |

Leituras importantes:
1. **O custo padrão decide o projeto.** Entre os extremos da faixa (76,72% × 84,39%), o financiamento aprovável varia de ~R$ 3,0 mi a ~R$ 4,5–4,7 mi — exatamente a sensibilidade documentada na skill (nota de honestidade). Antes de protocolar, vale confirmar no sistema/analista qual enquadramento (natureza indústria × porte pequena) será aplicado.
2. **Carência menor melhora o comprometimento** neste caso: com 12 meses de carência sobram 11 amortizações anuais (em vez de 10 ou 9), diluindo o principal — e o ramp-up do ano 2 (R$ 3,85 mi) já sustenta a primeira amortização equalizada.
3. **Coerência com o estudo v3:** no piso da faixa de custo, a simulação oficial confirma a recomendação do §13.4 (financiar ~R$ 4,0–4,5 mi em 12 anos) — R$ 4.460.000 com carência de 24 meses fecha a janela em 50,0%. No teto da faixa (84,39% ≈ o custo operacional reconstruído do próprio estudo, 83%), o aprovável cai para ~R$ 3,0 mi, exigindo mais contrapartida própria (o capital subscrito de R$ 7,5 milhões comporta).
4. **Ano 1 (carência):** capacidade de pagamento positiva nos dois extremos (R$ 227 mil no piso; R$ 16 mil no teto do custo) — sem gatilho de alerta, mas no custo alto a folga do ano 1 é mínima: o cronograma de aporte dos sócios deve cobrir os juros trimestrais da carência com margem.

## Cenário recomendado para o protocolo

**Pleito de R$ 4.400.000, prazo 144 meses, carência 24 meses** — passa no piso da faixa (comprometimento equalizado de 49,1%) e deixa claro o plano B negociado: se o analista aplicar custo padrão no teto da faixa, redimensionar para ~R$ 3,0 mi com contrapartida própria maior, sem alterar o projeto físico. Alternativa de defesa: demonstrar com o próprio estudo (margem de contribuição de 30–31% + fixos de 13%) que o custo operacional real da planta automática fica abaixo do teto da faixa.

| Detalhe do cenário R$ 4.400.000 · custo 76,72% · carência 24m | valor |
|---|---|
| Comprometimento equalizado (anos 3–12) | 49,1% (dentro de 30–50%) |
| Capacidade de pagamento no regime | R$ 0,74–1,08 mi/ano (crescente com a queda dos juros) |
| Juros da carência (pagos trimestralmente) | ~R$ 379 mil/ano |

*Notas de rigor: (i) simulação pela regra oficial de desembolso (aplicação integral no ano 1 — conservadora: superestima os juros iniciais; o desembolso real escalonado do cronograma físico só melhora o quadro); (ii) taxa cheia, sem bônus de adimplência (pagamento pontual reduz o desembolso efetivo); (iii) valores a validar na simulação do sistema do BNB no protocolo — este anexo usa o mesmo algoritmo da planilha oficial, mas o enquadramento de custo padrão e a taxa contratual final são definidos pelo banco.*

---
*Continuidade: este anexo alimenta o **dossiê de protocolo** em `dossie-bnb/` (memória de cálculo espelho com Mapa de Origem e Conferência, justificativa técnica, kit de defesa do analista e checklist de providências contábeis).*
