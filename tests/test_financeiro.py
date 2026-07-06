"""Paridade do porte Python contra o autoteste do simulador (index.html).

Cenário DEF e valores GOLD copiados literalmente do index.html (motor validado 100%
contra a planilha oficial BNB). Tolerâncias idênticas às do runAutoteste().
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engines.financeiro import run_sim  # noqa: E402

DEF = dict(
    data0=date(2026, 3, 5), valor=15_000_000.0, dia=5,
    taxaSem=0.094776, taxaCom=0.08056,
    prazoAmort=120, carencia=24,
    periodPrinc="MENSAL", periodCar="TRIMESTRAL",
    parcelasIguais=True, reembolso={},
    desembolsos=[
        {"data": date(2026, 3, 5), "valor": 2_800_000},
        {"data": date(2026, 6, 24), "valor": 4_020_000},
        {"data": date(2027, 9, 24), "valor": 1_250_000},
        {"data": date(2027, 12, 24), "valor": 1_250_000},
        {"data": date(2028, 3, 5), "valor": 4_820_000},
        {"data": date(2028, 6, 5), "valor": 860_000},
    ],
    custos=[
        {"nome": "Tarifa de análise", "valor": 187_500},
        {"nome": "Custo cartório/avaliação", "valor": 25_000},
        {"nome": "Seguro prestamista", "valor": 300_000},
    ],
)

GOLD = dict(
    qtdPrest=120, data1a=date(2028, 4, 5), venc=date(2038, 3, 5),
    totalJurosSem=8_047_998.84, totalJurosCom=6_881_903.91,
    totalPrincipal=15_000_000.0, totalBonus=1_166_094.93,
    mediaPrestCom=173_756.15, cetAnual=0.10407309, cetAnualComBonus=0.08929488,
    custosTotal=512_500.0, p1Total=213_801.51, pUltTotal=125_955.89,
    carenciaQtd=8, carencia1=53_888.64, numRows=145,
)

R = run_sim(DEF)
TOL = 0.011


def test_estrutura_do_cronograma():
    assert R["qtdPrest"] == GOLD["qtdPrest"]
    assert R["data1a"] == GOLD["data1a"]
    assert R["venc"] == GOLD["venc"]
    assert len(R["rows"]) == GOLD["numRows"]


def test_totais():
    assert abs(R["totalJurosSem"] - GOLD["totalJurosSem"]) <= TOL
    assert abs(R["totalJurosCom"] - GOLD["totalJurosCom"]) <= TOL
    assert abs(R["totalPrincipal"] - GOLD["totalPrincipal"]) <= TOL
    assert abs(R["totalBonus"] - GOLD["totalBonus"]) <= TOL
    assert abs(round(R["mediaPrestCom"], 2) - GOLD["mediaPrestCom"]) <= TOL
    assert R["custosTotal"] == GOLD["custosTotal"]


def test_cet():
    assert abs(R["cetAnual"] - GOLD["cetAnual"]) <= 1e-7
    assert abs(R["cetAnualComBonus"] - GOLD["cetAnualComBonus"]) <= 1e-7


def test_parcelas_extremas():
    amort = [s for s in R["rows"] if s["principal"] > 0.001]
    primeira = next(s for s in R["rows"] if s["isAmort"] and s["principal"] > 0.001)
    assert abs(primeira["totalCom"] - GOLD["p1Total"]) <= TOL
    assert abs(amort[-1]["totalCom"] - GOLD["pUltTotal"]) <= TOL


def test_carencia():
    graça = [s for s in R["rows"] if s["isGrace"] and s["juroPagoCom"] > 0.01]
    assert len(graça) == GOLD["carenciaQtd"]
    assert abs(graça[0]["juroPagoCom"] - GOLD["carencia1"]) <= TOL
