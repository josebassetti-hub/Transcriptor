"""Informalidade setorial via PNAD Contínua — labor input method (OECD/IMF/ILO).

Metodologia: docs/plano-fechamento-lacunas.md (lacuna 2). Os números vêm da
consulta F (dados/sql/pnad_informalidade_basedosdados.sql) rodada na Base dos
Dados e colados em dados/pnad_informalidade_demo.csv:

  uf, ano, trimestre, categoria, trabalhadores, rendimento_medio_mensal
  categoria: FORMAL (conta própria/empregador COM CNPJ ou empregado com
             carteira) | INFORMAL (sem CNPJ / sem carteira)

A seção do relatório só aparece quando o CSV existe — nada é inventado.
"""

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "dados" / "pnad_informalidade_demo.csv"


def informalidade(config: dict):
    """Retorna dict com contagens e rendimento, ou None se ainda sem dados."""
    if not ARQ.exists():
        return None
    uf = config["regiao"]["sigla"]
    linhas = [l for l in csv.DictReader(open(ARQ, encoding="utf-8")) if l["uf"] == uf]
    if not linhas:
        return None
    ref = max((l["ano"], l["trimestre"]) for l in linhas)
    atuais = [l for l in linhas if (l["ano"], l["trimestre"]) == ref]
    dados = {"FORMAL": (0, 0.0), "INFORMAL": (0, 0.0)}
    for l in atuais:
        n = int(float(l["trabalhadores"]))
        dados[l["categoria"]] = (n, float(l["rendimento_medio_mensal"]))
    n_inf, rend_inf = dados["INFORMAL"]
    n_for, _ = dados["FORMAL"]
    piso = n_inf * rend_inf * 12  # rendimento anual dos informais ~ receita líquida
    return {
        "referencia": f"{ref[0]} T{ref[1]}",
        "n_formal": n_for,
        "n_informal": n_inf,
        "rendimento_medio_informal": rend_inf,
        "receita_informal_piso": piso,
        "proveniencia": {
            "origem": "live",
            "fonte": (
                "IBGE — PNAD Contínua (microdados via Base dos Dados), ocupações COD 5141 "
                "(cabeleireiros) e 5142 (esteticistas/manicures), classificação formal/informal "
                "pela posse de CNPJ (V4019) e carteira assinada; labor input method OECD/IMF/ILO"
            ),
            "url": "https://basedosdados.org/dataset/br-ibge-pnadc",
            "consultado_em": f"PNAD-C {ref[0]} T{ref[1]}",
        },
    }
