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
    proveniencia} ou None se o CSV do setor ainda não existir.

    `driver_demanda.tipos_atendidos` (lista de tipos, nomes da consulta H)
    restringe o driver ao mercado que a empresa realmente atende — quando o
    driver abrange vários sub-mercados (motos, caminhões...), o recorte é
    decisão do cliente e deve ser PERGUNTADO, nunca assumido. Com o filtro,
    total/por_tipo/por_municipio contam só os tipos atendidos; `total_geral`
    e `excluidos` ficam disponíveis para o relatório declarar o que saiu.
    """
    dd = config.get("driver_demanda") or {}
    nome = dd.get("csv_frota")
    if not nome:
        return None
    caminho = DIR_DADOS / nome
    if not caminho.exists():
        return None
    tipos_ok = set(dd.get("tipos_atendidos") or [])
    municipios_ok = {m["nome"] for m in config["regiao"].get("municipios", [])}
    por_tipo = {}
    por_municipio = {}
    total_geral = 0
    excluidos = {}
    referencia = None
    with open(caminho, newline="", encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            # estudos municipais trazem a coluna opcional `municipio`; linhas
            # de cidades fora do recorte atual do config não contam
            mun = (l.get("municipio") or "").strip()
            if mun and municipios_ok and mun not in municipios_ok:
                continue
            referencia = max(referencia or l["referencia"], l["referencia"])
            q = int(l["quantidade"])
            total_geral += q
            if tipos_ok and l["tipo"] not in tipos_ok:
                excluidos[l["tipo"]] = excluidos.get(l["tipo"], 0) + q
                continue
            por_tipo[l["tipo"]] = por_tipo.get(l["tipo"], 0) + q
            if mun:
                por_municipio[mun] = por_municipio.get(mun, 0) + q
    if not por_tipo:
        return None
    demo = dd.get("frota_origem", "demo") != "real"
    return {
        "total": sum(por_tipo.values()),
        "total_geral": total_geral,
        "excluidos": excluidos or None,
        "por_tipo": por_tipo,
        "por_municipio": por_municipio or None,
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
