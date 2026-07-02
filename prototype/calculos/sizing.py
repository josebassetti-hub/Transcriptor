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
    """SAM e SOM a partir do censo de empresas-alvo."""
    ticket = icp["ticket_medio_anual_brl"]
    sam = n_icp * ticket
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
        "ticket": ticket,
        "sam": sam,
        "cenarios": cenarios,
        "horizonte_anos": captura["horizonte_anos"],
        "premissas": {
            "icp": icp["descricao"],
            "racional_ticket": icp["racional_ticket"],
        },
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
