"""Agregados da base de CNPJ da Receita Federal.

Em produção, estes agregados são gerados por ETL mensal a partir dos dumps
abertos (https://dadosabertos.rfb.gov.br/CNPJ/) ou consultados na Base dos Dados
(BigQuery) — ver dados/sql/agregados_cnpj_basedosdados.sql. O aplicativo NUNCA
consulta a base bruta em tempo de geração: só estas tabelas agregadas, pequenas
o bastante para o Postgres do Supabase.

Unidades (pós-auditoria, docs/auditoria-numeros-piloto.md):
- qtd_empresas: CNPJs-base distintos (uma rede com filiais conta 1) — usado no ICP.
- qtd_estabelecimentos: pontos de atendimento (cada filial conta 1).
O esquema antigo (coluna única qtd_ativas) é aceito como fallback, valendo pelas
duas medidas.

Esquema de dados/cnpj_agregados_demo.csv:
  cnae, uf, porte (MEI|ME|EPP|DEMAIS), faixa_idade (0-2|2-5|5-10|10+),
  qtd_empresas, qtd_estabelecimentos

Esquema de dados/cnpj_dinamica_demo.csv:
  ano, segmento (MEI|NAO_MEI), aberturas, fechamentos
  (fallback antigo sem a coluna segmento = TOTAL)
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
    filtradas = []
    for l in linhas:
        if l["cnae"] in cnaes and l["uf"] == uf:
            # fallback do esquema antigo (qtd_ativas única)
            emp = int(l.get("qtd_empresas") or l.get("qtd_ativas", 0))
            est = int(l.get("qtd_estabelecimentos") or l.get("qtd_ativas", 0))
            filtradas.append({**l, "qtd_empresas": emp, "qtd_estabelecimentos": est})
    extracao = config.get("cnpj_extracao", "desconhecida")
    return filtradas, _proveniencia(demo, extracao)


def contar_icp(linhas, icp: dict) -> dict:
    """Conta empresas-alvo (ICP, em EMPRESAS) e o universo nas duas unidades."""
    faixas_ok = set(icp["faixas_idade"])
    portes_ok = set(icp["portes"])
    universo_empresas = sum(l["qtd_empresas"] for l in linhas)
    universo_estab = sum(l["qtd_estabelecimentos"] for l in linhas)
    por_porte = {}
    n_icp = 0
    for l in linhas:
        por_porte[l["porte"]] = por_porte.get(l["porte"], 0) + l["qtd_empresas"]
        if l["porte"] in portes_ok and l["faixa_idade"] in faixas_ok:
            n_icp += l["qtd_empresas"]
    return {
        "n_icp": n_icp,
        "universo_empresas": universo_empresas,
        "universo_estabelecimentos": universo_estab,
        "por_porte": por_porte,
    }


def dinamica(config: dict, demo: bool = True):
    """Aberturas x fechamentos por ano e segmento (MEI|NAO_MEI|TOTAL)."""
    linhas = _ler_csv("cnpj_dinamica_demo.csv")
    serie = [
        (l["ano"], l.get("segmento", "TOTAL"), int(l["aberturas"]), int(l["fechamentos"]))
        for l in linhas
    ]
    return serie, _proveniencia(demo, config.get("cnpj_extracao", "desconhecida"))
