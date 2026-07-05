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
