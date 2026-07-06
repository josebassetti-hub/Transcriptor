"""Frota de veículos (SENATRAN) — base do arquétipo de demanda "b2c_frota".

Fonte oficial: SENATRAN/Ministério dos Transportes, estatísticas mensais de
frota por UF x município x tipo (e por ano de fabricação, para a idade da
frota). Consulta pela Base dos Dados (BigQuery) ou CSVs de dados abertos —
ver dados/sql/consultas_oficinas_sp.sql (consulta H). O resultado colado vive
em um CSV por setor:

  {prefixo}_frota_demo.csv: referencia, tipo, quantidade
  (referencia ex.: "2026-05"; tipo ex.: AUTOMOVEL, MOTOCICLETA, CAMINHONETE)

Retorna None enquanto o CSV não existir — a seção fica oculta (nada é
inventado). A origem live/demo vem de config["driver_demanda"]["frota_origem"].
"""

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ / "dados"


def frota_regiao(config: dict):
    """Frota da região por tipo. Retorna dict {total, por_tipo, referencia,
    proveniencia} ou None se o CSV do setor ainda não existir."""
    dd = config.get("driver_demanda") or {}
    nome = dd.get("csv_frota")
    if not nome:
        return None
    caminho = DIR_DADOS / nome
    if not caminho.exists():
        return None
    por_tipo = {}
    referencia = None
    with open(caminho, newline="", encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            referencia = max(referencia or l["referencia"], l["referencia"])
            por_tipo[l["tipo"]] = por_tipo.get(l["tipo"], 0) + int(l["quantidade"])
    if not por_tipo:
        return None
    demo = dd.get("frota_origem", "demo") != "real"
    return {
        "total": sum(por_tipo.values()),
        "por_tipo": por_tipo,
        "referencia": referencia,
        "proveniencia": {
            "origem": "fixture" if demo else "live",
            "fonte": ("SENATRAN/Ministério dos Transportes — frota de veículos "
                      f"registrados, {config['regiao']['nome']} ({referencia})"),
            "url": ("https://www.gov.br/transportes/pt-br/assuntos/transito/"
                    "conteudo-Senatran/estatisticas-frota-de-veiculos-senatran"),
            "consultado_em": ("dados de demonstração (aguardando consulta H)"
                              if demo else f"consulta H no BigQuery ({referencia})"),
            "motivo": "consulta H (frota) ainda não colada" if demo else None,
        },
    }
