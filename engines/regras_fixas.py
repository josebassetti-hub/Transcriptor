"""Regras fixas da ferramenta do professor + parâmetros FNE com vigência.

Fontes: knowledge/curso/relatorio-custos-despesas.md (regras) e
knowledge/curso/00-apresentacao-curso.md (tabela de juros). Taxas FNE mudam por
resolução/Plano Safra — sempre conferir vigência antes de usar em projeto real.
"""

TAXA_CONSERVACAO = 0.025      # 2,5% a.a. sobre edif./instal./máq./equip./impl./veíc.
TAXA_IMPOSTOS_TERRA = 0.002   # 0,2% a.a. sobre o valor total da terra nua


def conservacao_anual(valor_bens: float) -> float:
    """CONFIRMADO: exemplo 224.400 × 2,5% = 5.610,00/ano."""
    return round(valor_bens * TAXA_CONSERVACAO, 2)


def impostos_terra_nua_anual(valor_terra_nua: float) -> float:
    """CONFIRMADO: exemplo 1.700.000 × 0,2% = 3.400,00/ano."""
    return round(valor_terra_nua * TAXA_IMPOSTOS_TERRA, 2)


# Tabela de juros FNE (slide do curso; vigência = data do curso, 05/2026)
# fator = Fator de Programa (FP); taxas % a.a. prefixadas
JUROS_FNE_VIGENCIA = "2026-05"
JUROS_FNE = {
    ("investimento", "mini_peq_peqmedio"): {"fp": 0.4352640, "taxa": 6.50, "taxa_bonus": 6.25},
    ("investimento", "medio"):             {"fp": 0.6852849, "taxa": 7.44, "taxa_bonus": 7.18},
    ("investimento", "grande"):            {"fp": 0.9293268, "taxa": 8.36, "taxa_bonus": 8.19},
    ("custeio", "mini_peq_peqmedio"):      {"fp": 0.5111349, "taxa": 6.78, "taxa_bonus": 6.49},
    ("custeio", "medio"):                  {"fp": 0.6892302, "taxa": 7.46, "taxa_bonus": 7.19},
    ("custeio", "grande"):                 {"fp": 1.0580553, "taxa": 8.85, "taxa_bonus": 8.62},
    ("florestal_conservacao", "qualquer"): {"fp": 0.3655846, "taxa": 6.23, "taxa_bonus": 6.02},
}


def taxa_fne(finalidade: str, porte: str) -> dict:
    """Retorna {'fp', 'taxa', 'taxa_bonus'} (% a.a.). KeyError se combinação inválida."""
    return JUROS_FNE[(finalidade, porte)]
