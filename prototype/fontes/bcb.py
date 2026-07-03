"""Conector para a API SGS do Banco Central (séries temporais, JSON, sem autenticação).

Documentação: https://dadosabertos.bcb.gov.br/
A API tem instabilidade e limite de requisições intermitentes (respostas 400/406
esporádicas), então o conector tenta três variantes equivalentes da consulta —
"ultimos/N" com e sem formato=json e o intervalo por datas — usando a primeira
que responder. Com o cache de 7 dias, um sucesso serve várias gerações.

Códigos usados no protótipo (reais):
  4189 — Selic acumulada no mês anualizada (% a.a.)
   433 — IPCA, variação mensal (%)
"""

import datetime as _dt

BASE = "https://api.bcb.gov.br/dados/serie"


def serie_sgs(cliente, codigo: int, nome: str, ultimos: int = 24):
    """Retorna (pontos: list[(data 'MM/AAAA', float)], proveniencia)."""
    hoje = _dt.date.today()
    inicio = hoje - _dt.timedelta(days=ultimos * 45)
    urls = [
        f"{BASE}/bcdata.sgs.{codigo}/dados/ultimos/{ultimos}?formato=json",
        f"{BASE}/bcdata.sgs.{codigo}/dados/ultimos/{ultimos}",
        (
            f"{BASE}/bcdata.sgs.{codigo}/dados?formato=json"
            f"&dataInicial={inicio:%d/%m/%Y}&dataFinal={hoje:%d/%m/%Y}"
        ),
    ]
    bruto, prov = cliente.buscar_json_variantes(urls, fixture=f"bcb_{codigo}.json")
    pontos = [(p["data"][3:], float(p["valor"])) for p in bruto][-ultimos:]
    prov["fonte"] = f"Banco Central do Brasil — SGS série {codigo} ({nome})"
    return pontos, prov
