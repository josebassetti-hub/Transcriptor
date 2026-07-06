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
    elif ag.get("recorte_pendente"):
        # Sem o recorte, a consulta ao vivo traria a receita do agregado
        # INTEIRO com selo de dado vivo — número real do recorte errado é
        # pior que demonstração. Fica na fixture até a descoberta.
        bruto = cliente._fixture(ag["fixture"])
        cliente.usou_fixture = True
        prov = {
            "origem": "fixture",
            "url": url,
            "consultado_em": "dados de demonstração (fixture)",
            "motivo": ("recorte de atividade pendente de descoberta "
                       "(rode testar_fontes.py e cole a saída no chat)"),
            "fonte": ag["citacao"],
        }
        serie = _extrair_serie(bruto)
        fator = ag.get("fator_unidade", 1)
        return {ano: valor * fator for ano, valor in serie.items()}, prov
    bruto, prov = cliente.buscar_json(url, fixture=ag["fixture"])
    serie = _extrair_serie(bruto)
    if not serie:
        # resposta ao vivo sem nenhum valor (períodos vazios/sigilo/recorte
        # errado): cair para a fixture com o motivo declarado — nunca quebrar
        bruto = cliente._fixture(ag["fixture"])
        cliente.usou_fixture = True
        serie = _extrair_serie(bruto)
        prov = {
            "origem": "fixture",
            "url": url,
            "consultado_em": "dados de demonstração (fixture)",
            "motivo": ("a consulta ao vivo respondeu SEM VALORES (períodos vazios "
                       "ou sigilo) — recorte a revisar; cole a resposta da URL do "
                       "selo no chat para diagnóstico"),
        }
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


def fracao_segmento(cliente, cfg: dict):
    """Fração do segmento lida da PAS 2611 (receita do setor ÷ receita do grupo).

    Substitui a premissa manual de participação do segmento por dado oficial —
    docs/plano-fechamento-lacunas.md, lacuna 3. Retorna (fracao, ano, prov).
    """
    def _consulta(classificacao, fixture):
        url = (
            f"{BASE}/agregados/{cfg['agregado']}/periodos/{cfg['periodos']}/"
            f"variaveis/{cfg['variavel']}?localidades={cfg['localidade']}"
            f"&classificacao={classificacao}"
        )
        bruto, prov = cliente.buscar_json(url, fixture=fixture)
        return _extrair_serie(bruto), prov

    serie_setor, prov = _consulta(cfg["classificacao_setor"], cfg["fixture_setor"])
    serie_total, prov_total = _consulta(cfg["classificacao_total"], cfg["fixture_total"])
    anos_comuns = sorted(set(serie_setor) & set(serie_total))
    if not anos_comuns:
        raise ValueError("fracao_segmento: consultas sem ano em comum ou sem valores")
    ano = anos_comuns[-1]
    fracao = serie_setor[ano] / serie_total[ano]
    prov["fonte"] = cfg["citacao"]
    if prov_total["origem"] == "fixture":
        prov["origem"] = prov_total["origem"]
        prov.setdefault("motivo", prov_total.get("motivo"))
    return fracao, ano, prov


def _extrair_apisidra(resposta):
    """Extrai (ano, valor) do formato da API SIDRA clássica (apisidra.ibge.gov.br).

    A resposta é uma lista: a primeira linha é o cabeçalho {chave: rótulo};
    as demais trazem "V" (valor) e as dimensões D*N. O ano é a chave cujo
    rótulo no cabeçalho é "Ano" (ou similar)."""
    cabecalho, linhas = resposta[0], resposta[1:]
    chave_ano = None
    for k, rotulo in cabecalho.items():
        if k.endswith("N") and str(rotulo).lower().startswith("ano"):
            chave_ano = k
    valores = {}
    for l in linhas:
        v = l.get("V")
        if v in ("...", "-", "..", None):
            continue
        ano = l.get(chave_ano, "?") if chave_ano else "?"
        valores[str(ano)[:4]] = float(v)
    return dict(sorted(valores.items()))


def domicilios(cliente, cfg: dict):
    """Nº de domicílios particulares permanentes ocupados (Censo 2022, tab. 4712).

    Converte a despesa média mensal familiar (POF) em mercado total de demanda.
    Retorna (ano, valor, proveniencia) do período mais recente disponível.
    """
    url = (
        f"{BASE}/agregados/{cfg['agregado']}/periodos/{cfg['periodos']}/"
        f"variaveis/{cfg['variavel']}?localidades={cfg['localidade']}"
    )
    bruto, prov = cliente.buscar_json(url, fixture=cfg["fixture"])
    serie = _extrair_serie(bruto)
    ano = max(serie)
    prov["fonte"] = cfg["citacao"]
    return ano, serie[ano], prov


def demanda_pof(cliente, cfg: dict):
    """Top-down de DEMANDA: despesa familiar com o setor (POF) x domicílios.

    Para setores MEI-intensivos, o lado da demanda enxerga o mercado inteiro
    (formal + informal) — docs/plano-fechamento-lacunas.md, lacuna 3/4.
    Tabelas antigas da POF retornam HTTP 500 na API de agregados v3, então o
    conector tenta também a API SIDRA clássica (apisidra.ibge.gov.br), que
    serve as mesmas tabelas em outro formato.
    Retorna dict com despesa mensal por família, ano da POF e proveniências.
    """
    total_mensal = 0.0
    ano_pof = None
    provs = []
    for cat in cfg["categorias"]:
        cls_id, cat_id = cat["classificacao"].replace("]", "").split("[")
        url_v3 = (
            f"{BASE}/agregados/{cfg['agregado']}/periodos/{cfg['periodos']}/"
            f"variaveis/{cfg['variavel']}?localidades={cfg['localidade']}"
            f"&classificacao={cat['classificacao']}"
        )
        # A API clássica exige TODAS as dimensões da tabela no caminho (a 3615
        # tem também "classes de rendimento" — o total vai em
        # sidra_dimensoes_fixas) e não aceita query string: JSON já é o padrão.
        dims_fixas = ""
        for dim in cfg.get("sidra_dimensoes_fixas", []):
            d_cls, d_cat = dim.replace("]", "").split("[")
            dims_fixas += f"/c{d_cls}/{d_cat}"
        url_sidra = (
            f"https://apisidra.ibge.gov.br/values/t/{cfg['agregado']}/n1/all/"
            f"v/{cfg['variavel']}/p/last/c{cls_id}/{cat_id}{dims_fixas}"
        )
        bruto, prov = cliente.buscar_json_variantes([url_v3, url_sidra],
                                                    fixture=cat["fixture"])
        if isinstance(bruto, list) and bruto and isinstance(bruto[0], dict) \
                and "resultados" in bruto[0]:
            serie = _extrair_serie(bruto)  # formato da API de agregados v3
        else:
            serie = _extrair_apisidra(bruto)
        ano_pof = max(serie)
        total_mensal += serie[ano_pof]
        prov["fonte"] = cat["nome"] + " — " + cfg["citacao"]
        provs.append(prov)
    return {"despesa_mensal_familia": total_mensal, "ano_pof": ano_pof, "provs": provs}
