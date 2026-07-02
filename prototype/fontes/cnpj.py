"""Agregados da base de CNPJ da Receita Federal.

Em produção, estes agregados são gerados por ETL mensal a partir dos dumps
abertos (https://dadosabertos.rfb.gov.br/CNPJ/) ou consultados na Base dos Dados
(BigQuery) — ver dados/sql/agregados_cnpj_basedosdados.sql. O aplicativo NUNCA
consulta a base bruta em tempo de geração: só estas tabelas agregadas, pequenas
o bastante para o Postgres do Supabase.

No protótipo, os agregados vêm de CSVs em dados/ (rotulados como demonstração).

Esquema de dados/cnpj_agregados_demo.csv:
  cnae, uf, porte (MEI|ME|EPP|DEMAIS), faixa_idade (0-2|2-5|5-10|10+), qtd_ativas

Esquema de dados/cnpj_dinamica_demo.csv:
  ano, aberturas, fechamentos
"""

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ / "dados"


def _ler_csv(nome: str):
    with open(DIR_DADOS / nome, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _proveniencia(demo: bool, extracao: str):
    return {
        "origem": "fixture" if demo else "live",
        "fonte": (
            "Receita Federal — dados abertos do CNPJ, agregado por CNAE x UF x porte x idade "
            f"(extração {extracao})"
        ),
        "url": "https://dadosabertos.rfb.gov.br/CNPJ/",
        "consultado_em": "dados de demonstração (fixture)" if demo else extracao,
    }


def agregados(config: dict, demo: bool = True):
    """Retorna (linhas, proveniencia) dos agregados filtrados por CNAE+UF do setor."""
    linhas = _ler_csv("cnpj_agregados_demo.csv")
    cnaes = {c["codigo"] for c in config["cnaes"]}
    uf = config["regiao"]["sigla"]
    filtradas = [l for l in linhas if l["cnae"] in cnaes and l["uf"] == uf]
    extracao = config.get("cnpj_extracao", "desconhecida")
    return filtradas, _proveniencia(demo, extracao)


def contar_icp(linhas, icp: dict) -> dict:
    """Conta empresas-alvo (ICP) e devolve o detalhamento usado no relatório."""
    faixas_ok = set(icp["faixas_idade"])
    portes_ok = set(icp["portes"])
    total_universo = sum(int(l["qtd_ativas"]) for l in linhas)
    por_porte = {}
    n_icp = 0
    for l in linhas:
        por_porte[l["porte"]] = por_porte.get(l["porte"], 0) + int(l["qtd_ativas"])
        if l["porte"] in portes_ok and l["faixa_idade"] in faixas_ok:
            n_icp += int(l["qtd_ativas"])
    return {"n_icp": n_icp, "universo": total_universo, "por_porte": por_porte}


def dinamica(config: dict, demo: bool = True):
    """Aberturas x fechamentos por ano para os CNAEs/UF do setor."""
    linhas = _ler_csv("cnpj_dinamica_demo.csv")
    serie = [
        (l["ano"], int(l["aberturas"]), int(l["fechamentos"]))
        for l in linhas
    ]
    return serie, _proveniencia(demo, config.get("cnpj_extracao", "desconhecida"))
