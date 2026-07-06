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

Esquemas (v3; leitores aceitam os anteriores como fallback):
  cnpj_agregados_demo.csv: cnae, uf, [regime], porte, faixa_idade,
                           qtd_empresas, qtd_estabelecimentos
  cnpj_dinamica_demo.csv:  ano, [regime], [porte|segmento], aberturas, fechamentos
  cnpj_redes_demo.csv:     cnae, uf, faixa_unidades (1|2-5|6+),
                           qtd_empresas, qtd_estabelecimentos   (opcional)
  cnpj_atividades_demo.csv: cnae, empresas_principal,
                           empresas_somente_secundaria           (opcional)

Regime: MEI|SIMPLES|FORA_SIMPLES (Presumido x Real é sigilo fiscal — ver
docs/metodologia-v3.md). Quando o CSV não traz a coluna, regime = N/D e as
visões por regime ficam ocultas no relatório (nada é inventado).
"""

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ / "dados"


def _ler_csv(nome: str):
    with open(DIR_DADOS / nome, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _arq_setor(config: dict, sufixo: str) -> str:
    """Nome do CSV do setor: cada setor-piloto tem seus próprios arquivos de
    dados via `cnpj_prefixo` (default 'cnpj', o piloto de estética)."""
    return "{}_{}_demo.csv".format(config.get("cnpj_prefixo", "cnpj"), sufixo)


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
    linhas = _ler_csv(_arq_setor(config, "agregados"))
    cnaes = {c["codigo"] for c in config["cnaes"]}
    uf = config["regiao"]["sigla"]
    filtradas = []
    for l in linhas:
        if l["cnae"] in cnaes and l["uf"] == uf:
            # fallbacks dos esquemas anteriores
            emp = int(l.get("qtd_empresas") or l.get("qtd_ativas", 0))
            est = int(l.get("qtd_estabelecimentos") or l.get("qtd_ativas", 0))
            regime = l.get("regime") or ("MEI" if l["porte"] == "MEI" else "N/D")
            filtradas.append({**l, "qtd_empresas": emp, "qtd_estabelecimentos": est,
                              "regime": regime})
    extracao = config.get("cnpj_extracao", "desconhecida")
    return filtradas, _proveniencia(demo, extracao)


def contar_icp(linhas, icp: dict) -> dict:
    """Conta empresas-alvo (ICP, em EMPRESAS) e o universo nas duas unidades."""
    faixas_ok = set(icp["faixas_idade"])
    portes_ok = set(icp["portes"])
    universo_empresas = sum(l["qtd_empresas"] for l in linhas)
    universo_estab = sum(l["qtd_estabelecimentos"] for l in linhas)
    por_porte = {}
    por_regime = {}
    n_icp = 0
    for l in linhas:
        por_porte[l["porte"]] = por_porte.get(l["porte"], 0) + l["qtd_empresas"]
        por_regime[l["regime"]] = por_regime.get(l["regime"], 0) + l["qtd_empresas"]
        if l["porte"] in portes_ok and l["faixa_idade"] in faixas_ok:
            n_icp += l["qtd_empresas"]
    tem_regime = set(por_regime) - {"MEI", "N/D"} != set()
    return {
        "n_icp": n_icp,
        "universo_empresas": universo_empresas,
        "universo_estabelecimentos": universo_estab,
        "por_porte": por_porte,
        "por_regime": por_regime if tem_regime else None,
    }


def dinamica(config: dict, demo: bool = True):
    """Aberturas x fechamentos por ano, com regime/porte quando disponíveis.

    Retorna lista de dicts {ano, regime, porte, aberturas, fechamentos}.
    Fallbacks: esquema com `segmento` (MEI|NAO_MEI) vira regime; esquema
    antigo sem dimensão vira regime=TOTAL.
    """
    linhas = _ler_csv(_arq_setor(config, "dinamica"))
    serie = []
    for l in linhas:
        regime = l.get("regime") or l.get("segmento") or "TOTAL"
        serie.append({
            "ano": l["ano"],
            "regime": regime,
            "porte": l.get("porte", "N/D"),
            "aberturas": int(l["aberturas"]),
            "fechamentos": int(l["fechamentos"]),
        })
    return serie, _proveniencia(demo, config.get("cnpj_extracao", "desconhecida"))


def redes(config: dict):
    """Distribuição de empresas por nº de estabelecimentos na região (consulta D).

    Retorna None se o CSV ainda não existir — a seção fica oculta.
    """
    caminho = DIR_DADOS / _arq_setor(config, "redes")
    if not caminho.exists():
        return None
    linhas = _ler_csv(_arq_setor(config, "redes"))
    cnaes = {c["codigo"] for c in config["cnaes"]}
    agg = {}
    for l in linhas:
        if l["cnae"] in cnaes:
            faixa = l["faixa_unidades"]
            emp, est = agg.get(faixa, (0, 0))
            agg[faixa] = (emp + int(l["qtd_empresas"]), est + int(l["qtd_estabelecimentos"]))
    return agg or None


def atividades_concorrencia(config: dict):
    """Concorrentes por atividade: principal + só-secundária (consulta E).

    Retorna {cnae: (principal, somente_secundaria)} ou None se ainda sem dados.
    """
    caminho = DIR_DADOS / _arq_setor(config, "atividades")
    if not caminho.exists():
        return None
    return {
        l["cnae"]: (int(l["empresas_principal"]), int(l["empresas_somente_secundaria"]))
        for l in _ler_csv(_arq_setor(config, "atividades"))
    }


def rais_regiao(config: dict):
    """Peso regional pela RAIS (consulta G): vínculos formais da subclasse por UF.

    Participação da região = vínculos da UF ÷ soma de todas as UFs. Retorna
    None enquanto o CSV não existir (o peso fica fora da triangulação).
    """
    nome = config.get("rais_csv", "rais_regiao_demo.csv")
    caminho = DIR_DADOS / nome
    if not caminho.exists():
        return None
    linhas = _ler_csv(nome)
    uf = config["regiao"]["sigla"]
    ano = max(l["ano"] for l in linhas)
    total = sum(int(l["vinculos"]) for l in linhas if l["ano"] == ano)
    da_uf = sum(int(l["vinculos"]) for l in linhas
                if l["ano"] == ano and l["sigla_uf"] == uf)
    if not total:
        return None
    return {
        "ano": ano,
        "vinculos_uf": da_uf,
        "vinculos_total": total,
        "share": da_uf / total,
        "proveniencia": {
            "origem": "live",
            "fonte": ("Ministério do Trabalho — RAIS (vínculos ativos da subclasse "
                      f"CNAE, via Base dos Dados), ano {ano}"),
            "url": "https://basedosdados.org/dataset/br-me-rais",
            "consultado_em": f"consulta G no BigQuery (RAIS {ano})",
        },
    }


def fator_revisao(prefixo: str = "cnpj"):
    """Revisão dos fechamentos entre extrações mensais arquivadas (vintages).

    Compara a extração mais antiga e a mais nova em dados/vintages/ para o ano
    mais recente comum: fechamentos sobem entre extrações porque baixas são
    registradas com atraso. Retorna None com menos de 2 extrações.
    """
    pasta = DIR_DADOS / "vintages"
    arquivos = sorted(pasta.glob(prefixo + "_dinamica_*.csv")) if pasta.exists() else []
    if len(arquivos) < 2:
        return None

    def _fech_por_ano(caminho):
        agg = {}
        with open(caminho, newline="", encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                agg[l["ano"]] = agg.get(l["ano"], 0) + int(l["fechamentos"])
        return agg

    antiga, nova = arquivos[0], arquivos[-1]
    fe_antiga, fe_nova = _fech_por_ano(antiga), _fech_por_ano(nova)
    comuns = sorted(set(fe_antiga) & set(fe_nova))
    if not comuns:
        return None
    ano = comuns[-1]
    if not fe_antiga[ano]:
        return None
    return {
        "ano": ano,
        "fator": fe_nova[ano] / fe_antiga[ano],
        "de": antiga.stem.replace(prefixo + "_dinamica_", ""),
        "para": nova.stem.replace(prefixo + "_dinamica_", ""),
    }
