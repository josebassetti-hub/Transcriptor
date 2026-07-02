"""Conector para a API SGS do Banco Central (séries temporais, JSON, sem autenticação).

Documentação: https://dadosabertos.bcb.gov.br/
Padrão: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}?formato=json

Códigos usados no protótipo (reais):
  432 — Meta Selic definida pelo Copom (% a.a.)
  433 — IPCA, variação mensal (%)
"""

BASE = "https://api.bcb.gov.br/dados/serie"


def serie_sgs(cliente, codigo: int, nome: str, ultimos: int = 24):
    """Retorna (pontos: list[(data 'MM/AAAA', float)], proveniencia)."""
    url = f"{BASE}/bcdata.sgs.{codigo}/dados/ultimos/{ultimos}?formato=json"
    bruto, prov = cliente.buscar_json(url, fixture=f"bcb_{codigo}.json")
    pontos = [(p["data"][3:], float(p["valor"])) for p in bruto]
    prov["fonte"] = f"Banco Central do Brasil — SGS série {codigo} ({nome})"
    return pontos, prov
