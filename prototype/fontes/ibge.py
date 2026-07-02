"""Conector para a API de agregados do IBGE (v3) — a mesma que alimenta o SIDRA.

Documentação: https://servicodados.ibge.gov.br/api/docs/agregados?versao=3

Padrão de URL:
  /api/v3/agregados/{agregado}/periodos/{periodos}/variaveis/{variavel}?localidades={nivel}[{codigo}]

A curadoria de QUAL agregado/variável dimensiona cada setor é feita uma vez por
setor-piloto e fica registrada no arquivo de configuração do setor (campo
`topdown.agregado_sidra`), garantindo citação exata no relatório.
"""

BASE = "https://servicodados.ibge.gov.br/api/v3"


def receita_setorial(cliente, cfg_topdown: dict):
    """Receita bruta do setor (série anual, R$) para o agregado configurado.

    Retorna (serie: dict ano->valor_brl, proveniencia).
    """
    ag = cfg_topdown["agregado_sidra"]
    url = (
        f"{BASE}/agregados/{ag['agregado']}/periodos/{ag['periodos']}/"
        f"variaveis/{ag['variavel']}?localidades={ag['localidade']}"
    )
    if ag.get("classificacao"):
        # recorte de atividade/CNAE, ex.: "12354[118012]" (descoberto via testar_fontes.py)
        url += f"&classificacao={ag['classificacao']}"
    bruto, prov = cliente.buscar_json(url, fixture=ag["fixture"])
    serie = _extrair_serie(bruto)
    fator = ag.get("fator_unidade", 1)  # ex.: 1000 quando a unidade é "mil reais"
    serie = {ano: valor * fator for ano, valor in serie.items()}
    prov["fonte"] = ag["citacao"]
    return serie, prov


def _extrair_serie(resposta) -> dict:
    """Extrai {ano: float} do formato de resposta da API de agregados v3."""
    serie_bruta = resposta[0]["resultados"][0]["series"][0]["serie"]
    out = {}
    for periodo, valor in serie_bruta.items():
        if valor in ("-", "...", "..", None):
            continue
        out[periodo] = float(valor)
    return dict(sorted(out.items()))


def contagem_empresas(cliente, cfg: dict):
    """Nº oficial de empresas (CEMPRE) para a classe CNAE/região configuradas.

    Retorna (ano, valor, proveniencia) do período mais recente disponível.
    """
    url = (
        f"{BASE}/agregados/{cfg['agregado']}/periodos/{cfg['periodos']}/"
        f"variaveis/{cfg['variavel']}?localidades={cfg['localidade']}"
        f"&classificacao={cfg['classificacao']}"
    )
    bruto, prov = cliente.buscar_json(url, fixture=cfg["fixture"])
    serie = _extrair_serie(bruto)
    ano = max(serie)
    prov["fonte"] = cfg["citacao"]
    prov["url"] = url
    return ano, serie[ano], prov
