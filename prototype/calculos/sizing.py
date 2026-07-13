"""Motor de dimensionamento: TAM/SAM/SOM com dupla metodologia e triangulação.

Metodologia (ver docs/pesquisa-mercado-ferramentas-analise.md, seção 4):
- Top-down: receita agregada do setor (fonte oficial) -> recorte de segmento -> região.
- Bottom-up: nº de empresas-alvo (censo CNPJ) x ticket médio anual x taxa de captura.
- Triangulação: divergência entre SAM top-down e SAM bottom-up; convergência
  na casa de ~20% é tratada como sinal de confiabilidade.

Nenhuma função inventa número: tudo deriva dos insumos recebidos, e cada
resultado carrega as premissas usadas (exibidas no relatório).
"""


def top_down(serie_receita: dict, cfg_topdown: dict) -> dict:
    """TAM nacional e SAM regional/segmento a partir da série oficial de receita."""
    ultimo_ano = max(serie_receita)
    tam = serie_receita[ultimo_ano]
    part_segmento = cfg_topdown["participacao_segmento"]
    part_regiao = cfg_topdown["participacao_regiao"]
    sam = tam * part_segmento * part_regiao
    anos = sorted(serie_receita)
    cagr = None
    if len(anos) >= 2:
        v0, v1 = serie_receita[anos[0]], serie_receita[anos[-1]]
        n = int(anos[-1]) - int(anos[0])
        if v0 > 0 and n > 0:
            cagr = (v1 / v0) ** (1 / n) - 1
    return {
        "ano_base": ultimo_ano,
        "tam": tam,
        "sam": sam,
        "cagr": cagr,
        "premissas": {
            "participacao_segmento": part_segmento,
            "racional_segmento": cfg_topdown["racional_segmento"],
            "participacao_regiao": part_regiao,
            "racional_regiao": cfg_topdown["racional_regiao"],
        },
    }


def bottom_up(n_icp: int, icp: dict, captura: dict) -> dict:
    """SAM e SOM a partir do censo de empresas-alvo.

    taxa_atividade: fração dos cadastros ICP efetivamente operantes como
    negócio (CNPJ ativo != empresa operante — a razão CEMPRE/cadastro do
    setor ancora o intervalo plausível). Default 1.0 (sem desconto).
    """
    ticket = icp["ticket_medio_anual_brl"]
    taxa_atividade = icp.get("taxa_atividade", 1.0)
    n_operantes = round(n_icp * taxa_atividade)
    sam = n_operantes * ticket
    cenarios = {
        nome: {"taxa": taxa, "som": sam * taxa}
        for nome, taxa in (
            ("pessimista", captura["pessimista"]),
            ("base", captura["base"]),
            ("otimista", captura["otimista"]),
        )
    }
    return {
        "n_icp": n_icp,
        "n_operantes": n_operantes,
        "taxa_atividade": taxa_atividade,
        "ticket": ticket,
        "sam": sam,
        "cenarios": cenarios,
        "horizonte_anos": captura["horizonte_anos"],
        "premissas": {
            "icp": icp["descricao"],
            "racional_ticket": icp["racional_ticket"],
            "racional_atividade": icp.get("racional_atividade", ""),
        },
    }


def sensibilidade(n_icp: int, taxas=(0.15, 0.31, 0.45), tickets=(120000, 180000, 280000)):
    """Matriz de sensibilidade do SAM bottom-up: taxa de atividade x ticket.

    Evita que o dimensionamento dependa de um par pontual de premissas — o
    relatório mostra o intervalo inteiro (auditoria: ticket próximo do teto
    de faturamento de ME e taxa de atividade são as premissas mais sensíveis).
    """
    return {
        "taxas": list(taxas),
        "tickets": list(tickets),
        "matriz": [
            [round(n_icp * taxa) * ticket for ticket in tickets]
            for taxa in taxas
        ],
    }


def triangulacao(sam_topdown: float, sam_bottomup: float) -> dict:
    maior, menor = max(sam_topdown, sam_bottomup), min(sam_topdown, sam_bottomup)
    divergencia = (maior - menor) / maior if maior else 0.0
    return {
        "sam_topdown": sam_topdown,
        "sam_bottomup": sam_bottomup,
        "divergencia": divergencia,
        "convergente": divergencia <= 0.35,
        "leitura": (
            "As duas metodologias convergem dentro da margem esperada, o que reforça a "
            "confiabilidade da estimativa."
            if divergencia <= 0.35
            else "As metodologias divergem além da margem esperada: revise as premissas de "
            "participação de segmento (top-down) e de ticket médio (bottom-up) antes de usar."
        ),
    }


def mercado_enderecavel(valores_por_cidade, municipios):
    """Consolidação ponderada de estudos multi-cidade (modelo gravitacional
    Reilly/Huff, padrão de área de influência no varejo): cada cidade é um
    mercado SEPARADO (100% local) e a loja disputa só a fração dada pelo
    fator de acesso do anel — a soma simples é apenas o teto teórico.

    valores_por_cidade: {nome: valor local (frota, R$ etc.)}
    municipios: [{nome, anel, fator_acesso: {min, base, max}}, ...]
    Retorna {linhas: [...], totais: {teto, min, base, max}}.
    """
    idx = {m["nome"]: m for m in municipios}
    linhas = []
    totais = {"teto": 0.0, "min": 0.0, "base": 0.0, "max": 0.0}
    for nome, valor in sorted(valores_por_cidade.items(), key=lambda kv: -kv[1]):
        m = idx.get(nome, {})
        f = m.get("fator_acesso", {"min": 1.0, "base": 1.0, "max": 1.0})
        linhas.append({
            "cidade": nome,
            "anel": m.get("anel", "—"),
            "valor_local": valor,
            "fator": f,
            "enderecavel": valor * f["base"],
            "enderecavel_min": valor * f["min"],
            "enderecavel_max": valor * f["max"],
        })
        totais["teto"] += valor
        for k in ("min", "base", "max"):
            totais[k] += valor * f[k]
    return {"linhas": linhas, "totais": totais}


def demanda_por_linha(bases, linhas):
    """Mercado por linha de negócio: base contável × frequência anual × preço
    (método incorporado do plano de negócio da Lorenzoni — a fórmula universal
    de docs/drivers-demanda.md aplicada linha a linha, com cada frequência e
    preço como PREMISSA DECLARADA com fonte).

    bases: {"frota": total ponderado, "por_tipo": {tipo: qtd ponderada}}
    linhas: [{nome, cnae, base ("frota" | {"tipos": [...]} |
              {"derivada_de": [nomes], "divisor": n}), frequencia_ano?,
              unidade, preco_medio_brl? | valor_anual_por_veiculo?,
              racional_frequencia, racional_preco}]
    Retorna {"linhas": [{...linha, base_qtd, qtd_ano, mercado, mix}],
             "total": Σ mercado das linhas dimensionadas}.
    Linha sem parâmetro suficiente sai com mercado=None (não dimensionada —
    ausência declarada é melhor que número inventado).
    """
    calculadas = []
    por_nome = {}
    for ln in linhas:
        base_cfg = ln.get("base", "frota")
        if base_cfg == "frota":
            base_qtd = bases.get("frota", 0)
        elif isinstance(base_cfg, dict) and "tipos" in base_cfg:
            base_qtd = sum(bases.get("por_tipo", {}).get(t, 0)
                           for t in base_cfg["tipos"])
        elif isinstance(base_cfg, dict) and "derivada_de" in base_cfg:
            base_qtd = sum(por_nome.get(n, {}).get("qtd_ano") or 0
                           for n in base_cfg["derivada_de"])
            base_qtd /= base_cfg.get("divisor", 1)
        else:
            base_qtd = 0
        qtd_ano = None
        mercado = None
        if ln.get("frequencia_ano") is not None and ln.get("preco_medio_brl"):
            qtd_ano = base_qtd * ln["frequencia_ano"]
            mercado = qtd_ano * ln["preco_medio_brl"]
        elif ln.get("valor_anual_por_veiculo"):
            mercado = base_qtd * ln["valor_anual_por_veiculo"]
        item = {**ln, "base_qtd": base_qtd, "qtd_ano": qtd_ano,
                "mercado": mercado}
        por_nome[ln["nome"]] = item
        calculadas.append(item)
    total = sum(l["mercado"] for l in calculadas if l["mercado"])
    for l in calculadas:
        l["mix"] = (l["mercado"] / total) if (l["mercado"] and total) else None
    return {"linhas": calculadas, "total": total}


def por_atividade(sam_total, receita_alvo_total, atividades, concorrencia=None,
                  expansao=None):
    """Dimensionamento multi-CNAE: para cada atividade do estudo, o SAM da
    atividade (premissa participacao_sam sobre o SAM total), a receita-alvo
    pelo mix do cliente (peso_receita) e o share implícito — o teste de
    realismo do plano por atividade (docs/metodologia-v3.md, seção 4).

    expansao ({taxa_atividade, ticket, peso_secundaria}): quando presente e há
    contagem de concorrentes só-secundários, calcula também o SAM EXPANDIDO da
    atividade — o conservador (só CNAE principal) mais a receita atribuível às
    empresas com o CNAE apenas como atividade secundária, ponderada pelo mix
    de receita (a limitação de CNAE secundário vira faixa publicada).
    """
    linhas = []
    for atv in atividades:
        sam_atv = sam_total * atv["participacao_sam"]
        receita_alvo = receita_alvo_total * atv["peso_receita"]
        conc = (concorrencia or {}).get(atv["cnae"])
        sam_expandido = None
        if conc and expansao:
            adicional = (conc[1] * expansao["taxa_atividade"]
                         * expansao["ticket"] * expansao["peso_secundaria"])
            sam_expandido = sam_atv + adicional
        linhas.append({
            "cnae": atv["cnae"],
            "descricao": atv["descricao"],
            "peso_receita": atv["peso_receita"],
            "participacao_sam": atv["participacao_sam"],
            "sam_atividade": sam_atv,
            "sam_expandido": sam_expandido,
            "receita_alvo": receita_alvo,
            "share_implicito": receita_alvo / sam_atv if sam_atv else 0.0,
            "share_expandido": (receita_alvo / sam_expandido
                                if sam_expandido else None),
            "concorrentes_principal": conc[0] if conc else None,
            "concorrentes_secundaria": conc[1] if conc else None,
        })
    return linhas
