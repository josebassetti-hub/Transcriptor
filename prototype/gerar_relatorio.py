#!/usr/bin/env python3
"""Gera um relatório de análise de mercado para um setor configurado.

Uso:
  python3 gerar_relatorio.py --setor setores/estetica_sp.json [--modo auto|live|fixture]

Pipeline (espelha as Edge Functions da especificação):
  collect  -> fontes/ (IBGE, Bacen, agregados CNPJ), com proveniência por dado
  compute  -> calculos/sizing.py (TAM/SAM/SOM top-down + bottom-up + triangulação)
  write    -> redação determinística por template (produção: LLM com guard-rail)
  render   -> relatorio/render.py (HTML autocontido com SVG)

Somente biblioteca-padrão do Python — roda em qualquer lugar.
"""

import argparse
import json
import time
from pathlib import Path

from fontes.http_client import ClienteHTTP
from fontes import ibge, bcb, cnpj, pnad, frota
from calculos import sizing
from relatorio import render as R
from relatorio.memoria import Memoria, _tabela as tabela_aberta

RAIZ = Path(__file__).resolve().parent


def secao(titulo, *blocos):
    return f"<section><h2>{titulo}</h2>" + "".join(blocos) + "</section>"


def _num(v):
    """Número completo com separador de milhar — a memória de cálculo mostra a
    substituição exata, não o valor abreviado ("R$ 1,2 bi") do corpo."""
    return f"{v:,.0f}".replace(",", ".")


def _dec(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def gerar(config: dict, modo: str) -> str:
    cliente = ClienteHTTP(modo)
    mem = Memoria()
    m_consol = None  # verbete municipal, citado pela chave regional quando existe

    # ---- collect -------------------------------------------------------------
    receita, prov_ibge = ibge.receita_setorial(cliente, config["topdown"])
    prov_segmento = None
    det_frac = None
    if config["topdown"].get("segmento_dado"):
        # a fração do segmento vem de tabela oficial (dado), substituindo a
        # premissa; se a consulta ao vivo vier sem valores, mantém a premissa
        # declarada em vez de quebrar
        try:
            fracao, ano_frac, prov_segmento, det_frac = ibge.fracao_segmento(
                cliente, config["topdown"]["segmento_dado"])
            config["topdown"]["participacao_segmento"] = fracao
            modelo = config["topdown"]["segmento_dado"].get(
                "racional_modelo",
                "DADO (PAS Tab. 2611, {ano}): receita de cabeleireiros/tratamento "
                "de beleza ÷ receita de serviços pessoais = {fracao:.1%}")
            config["topdown"]["racional_segmento"] = modelo.format(
                ano=ano_frac, fracao=fracao)
        except Exception as exc:
            prov_segmento = None
            det_frac = None
            config["topdown"]["racional_segmento"] = (
                config["topdown"].get("racional_segmento", "premissa declarada")
                + f" [fração medida indisponível na consulta ao vivo: {exc}]")
    series_macro = [
        bcb.serie_sgs(cliente, s["codigo"], s["nome"], s["ultimos"])
        for s in config["series_bcb"]
    ]
    # os CSVs de CNPJ passam a contar como dado real quando o usuário os
    # substitui pelos agregados da Base dos Dados e marca cnpj_origem: "real"
    cnpj_demo = config.get("cnpj_origem", "demo") != "real"
    linhas_cnpj, prov_cnpj = cnpj.agregados(config, demo=cnpj_demo)
    contagem = cnpj.contar_icp(linhas_cnpj, config["icp"])
    emp_mun = cnpj.empresas_por_municipio(config)
    din, _ = cnpj.dinamica(config, demo=cnpj_demo)
    cempre = None
    if config.get("bottomup_validacao"):
        cempre = ibge.contagem_empresas(cliente, config["bottomup_validacao"])
    # região: de premissa única para triangulação de pesos públicos (mediana)
    regiao_pesos = []
    rm = config["topdown"].get("regiao_medida")
    if rm:
        if rm.get("cnpj_share") is not None:
            regiao_pesos.append({"rotulo": "CNPJ", "valor": rm["cnpj_share"],
                                 "prov": None, "racional": rm["racional_cnpj"]})
        if rm.get("cempre_brasil") and cempre:
            ano_br, qtd_br, prov_br = ibge.contagem_empresas(
                cliente, rm["cempre_brasil"])
            if qtd_br:
                regiao_pesos.append({
                    "rotulo": "CEMPRE {}".format(ano_br),
                    "valor": cempre[1] / qtd_br, "prov": prov_br,
                    "racional": "empresas da classe na UF ÷ Brasil (IBGE)"})
        rais = cnpj.rais_regiao(config)
        if rais:
            regiao_pesos.append({
                "rotulo": "RAIS {}".format(rais["ano"]),
                "valor": rais["share"], "prov": rais["proveniencia"],
                "racional": "vínculos formais da subclasse na UF ÷ Brasil"})
    if len(regiao_pesos) >= 2:
        vals = sorted(p["valor"] for p in regiao_pesos)
        n = len(vals)
        mediana = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        config["topdown"]["participacao_regiao"] = mediana
        config["topdown"]["racional_regiao"] = (
            "DADO (mediana de {} pesos públicos independentes — "
            "detalhe nesta seção)".format(n))
    dist_redes = cnpj.redes(config)
    informal = pnad.informalidade(config)
    demanda = None
    if config.get("topdown_demanda"):
        demanda = ibge.demanda_pof(cliente, config["topdown_demanda"])
        demanda["domicilios"] = ibge.domicilios(
            cliente, config["topdown_demanda"]["domicilios"])
        # inflator integral: IPCA acumulado desde o ano de referência da POF
        demanda["ipca_pof"] = bcb.serie_sgs_periodo(
            cliente, 433, "IPCA — variação mensal (%)",
            "15/01/{}".format(str(demanda["ano_pof"])[:4]))
    conc_atividades = cnpj.atividades_concorrencia(config)
    frota_info = frota.frota_regiao(config)

    # ---- compute -------------------------------------------------------------
    td = sizing.top_down(receita, config["topdown"])
    # bottom-up ponderado (estudos municipais): concorrente de cidade-satélite
    # disputa o mesmo mercado que a loja só na fração do fator de acesso, então
    # o ICP que alimenta o SAM é o ENDEREÇÁVEL = Σ (ICP da cidade × fator base)
    funil_mun = cnpj.funil_por_municipio(linhas_cnpj, config["icp"])
    munis_cfg = config["regiao"].get("municipios", [])
    fatores_mun = {m["nome"]: m["fator_acesso"]
                   for m in munis_cfg if "fator_acesso" in m}
    icp_enderecavel = None
    if funil_mun and fatores_mun:
        icp_enderecavel = sum(
            f["icp"] * fatores_mun.get(mun, {"base": 1.0})["base"]
            for mun, f in funil_mun.items())
    bu = sizing.bottom_up(
        round(icp_enderecavel) if icp_enderecavel is not None
        else contagem["n_icp"],
        config["icp"], config["captura"])
    # demanda por linha de negócio (base × frequência × preço, premissas com
    # fonte) sobre a frota atendível ponderada pelos fatores de acesso
    demanda_linhas = None
    if config.get("linhas_negocio") and frota_info:
        if frota_info.get("por_municipio_tipo") and fatores_mun:
            por_tipo_pond = {}
            for mun_dl, tipos_m in frota_info["por_municipio_tipo"].items():
                fb = fatores_mun.get(mun_dl, {"base": 1.0})["base"]
                for t, q in tipos_m.items():
                    por_tipo_pond[t] = por_tipo_pond.get(t, 0) + q * fb
        else:
            por_tipo_pond = dict(frota_info["por_tipo"])
        demanda_linhas = sizing.demanda_por_linha(
            {"frota": sum(por_tipo_pond.values()), "por_tipo": por_tipo_pond},
            config["linhas_negocio"])
    tri = sizing.triangulacao(td["sam"], bu["sam"])
    sens = sizing.sensibilidade(bu["n_icp"])
    som_base = bu["cenarios"]["base"]["som"]
    usa_bu_central = config.get("sam_central") == "bottom_up"
    sam_central = bu["sam"] if usa_bu_central else (td["sam"] + bu["sam"]) / 2
    detalhe_sam = config.get("rotulo_sam_detalhe", "bottom-up; PAS = piso")
    rotulo_sam = ("SAM " + config["regiao"].get("apelido", config["regiao"]["sigla"])
                  + (f" ({detalhe_sam})" if usa_bu_central else " (triangulado)"))

    # ---- write + render ------------------------------------------------------
    s = []

    # 1. Sumário executivo
    kpis = "".join(
        f'<div class="kpi"><b>{v}</b><span>{k}</span></div>'
        for k, v in [
            (f"TAM Brasil ({td['ano_base']}, top-down)", R.brl(td["tam"])),
            (rotulo_sam, R.brl(sam_central)),
            (f"SOM base em {bu['horizonte_anos']} anos", R.brl(som_base)),
            ("Empresas-alvo operantes (ICP)", R.inteiro(bu["n_operantes"])),
            ("CAGR do mercado (série oficial)", R.pct(td["cagr"]) if td["cagr"] else "n/d"),
        ]
    )
    s.append(secao(
        "1. Sumário executivo",
        f'<div class="kpis">{kpis}</div>',
        ("<p>O dimensionamento por duas metodologias independentes chega a valores "
         f"próximos (divergência de {R.pct(tri['divergencia'])}): "
         if tri["convergente"] else
         "<p>As duas metodologias divergem de forma relevante "
         f"(divergência de {R.pct(tri['divergencia'])} — ver diagnóstico na seção 6): ")
        + 
        f"{R.brl(td['sam'])} pelo recorte top-down da receita setorial oficial e "
        f"{R.brl(bu['sam'])} pelo bottom-up sobre o censo da base CNPJ "
        f"({R.inteiro(bu['n_icp'])} cadastros ICP, {R.inteiro(bu['n_operantes'])} operantes "
        f"pela premissa de atividade). No cenário-base de captura "
        f"({R.pct(bu['cenarios']['base']['taxa'])} em {bu['horizonte_anos']} anos), o "
        f"objetivo de receita anual (SOM) é {R.brl(som_base)}.</p>",
        '<p class="explicacao"><b>Em palavras simples:</b> o estudo mediu um '
        f"mercado anual de <b>{R.brl(sam_central)}</b> em "
        f"{config['regiao'].get('apelido', config['regiao']['nome'])}; nele "
        f"operam de verdade cerca de <b>{R.inteiro(bu['n_operantes'])}</b> "
        "concorrentes do perfil-alvo; no cenário-base, a empresa captura "
        f"{R.pct(bu['cenarios']['base']['taxa'])} disso — "
        f"<b>{R.brl(som_base)}</b> por ano. Termos técnicos: ver o "
        '<a href="#glossario">Glossário</a> no fim do relatório.</p>',
        '<p class="premissas">A conta completa de cada número deste estudo — '
        "fórmula, entradas, substituição numérica e links de verificação — está "
        'no <a href="#memoria-calculo">Anexo — Memória de cálculo</a>, no fim '
        "do relatório.</p>",
    ))

    # 2. Metodologia — passo a passo em linguagem simples (analista júnior
    # precisa conseguir seguir o estudo inteiro sem tradutor)
    s.append(secao(
        "2. Escopo e metodologia — o passo a passo do estudo",
        "<p>O estudo responde seis perguntas, nesta ordem, sempre com fonte "
        "oficial citada e conta aberta:</p>"
        "<ol>"
        "<li><b>Quem pode comprar?</b> Contamos a base de clientes potenciais "
        "(o “driver de demanda”: domicílios ou frota de veículos, "
        "conforme o setor) — seção 3b.</li>"
        "<li><b>Qual o tamanho do bolo, de cima para baixo?</b> Partimos da "
        "receita nacional oficial do setor (IBGE) e recortamos por segmento e "
        "região — o <b>top-down</b>, seção 4.</li>"
        "<li><b>Quem já disputa esse bolo?</b> Contamos os concorrentes um a "
        "um na base oficial de CNPJ, separando cadastro morto de negócio real "
        "— o <b>bottom-up</b>, seção 5.</li>"
        "<li><b>Os caminhos batem?</b> Cruzamos as estimativas independentes "
        "(triangulação) e montamos os cenários de captura — seção 6.</li>"
        "<li><b>Onde exatamente está o dinheiro?</b> Abrimos o mercado por "
        "atividade/linha de negócio e testamos o realismo da meta — seções 7 "
        "e 7b.</li>"
        "<li><b>O que o estudo NÃO enxerga?</b> Limitações declaradas — "
        "seção 8.</li>"
        "</ol>"
        "<p>Toda fonte é citada no selo da respectiva seção; a extração da "
        "base CNPJ usada é a de <b>" + config["cnpj_extracao"] + "</b>. "
        "Termos técnicos estão no <a href=\"#glossario\">Glossário</a> e toda "
        "conta na <a href=\"#memoria-calculo\">Memória de cálculo</a>.</p>",
        '<p class="premissas">ICP (o perfil de empresa contado como '
        "concorrente/cliente-alvo): " + config["icp"]["descricao"] + "</p>",
    ))

    # 3. Contexto macroeconômico
    graficos_macro = []
    for (pontos, prov), cfg_serie in zip(series_macro, config["series_bcb"]):
        graficos_macro.append(R.grafico_linhas([(cfg_serie["nome"], pontos)], "%"))
        graficos_macro.append(R.selo_fonte(prov))
    s.append(secao(
        "3. Contexto macroeconômico",
        "<p>Séries oficiais do Banco Central usadas como pano de fundo do plano de entrada: "
        "juros (custo de capital e crédito ao consumo dos clientes finais) e inflação.</p>",
        *graficos_macro,
    ))

    # 3b. Quem compra — driver de demanda por arquétipo (docs/drivers-demanda.md):
    # demanda = base contável x penetração/frequência x valor, tudo com fonte
    dd = config.get("driver_demanda")
    if dd:
        blocos_dd = [f"<p>{dd['descricao']}</p>"]
        if dd.get("arquetipo") == "b2c_populacao_domicilios" and demanda:
            ano_dom_dd, n_dom_dd, prov_dom_dd = demanda["domicilios"]
            blocos_dd.append(
                f"<p><b>Base contável:</b> <b>{R.inteiro(n_dom_dd)}</b> domicílios "
                f"particulares ocupados na região (Censo {ano_dom_dd}). "
                f"<b>Conversão em demanda:</b> despesa média mensal familiar com o setor "
                f"de {R.brl(demanda['despesa_mensal_familia'])} (POF {demanda['ano_pof']}), "
                "corrigida pela inflação — a âncora completa está na seção 6 "
                "(triangulação).</p>"
            )
            blocos_dd.append(R.selo_fonte(prov_dom_dd))
        elif dd.get("arquetipo") == "b2c_frota" and frota_info:
            # recorte de tipos atendidos: quando o driver abrange vários
            # sub-mercados (motos, caminhões...), o recorte é DECISÃO DO
            # CLIENTE, declarada no config — nunca assumida
            m_tipos = None
            if dd.get("tipos_atendidos"):
                exc = frota_info.get("excluidos") or {}
                exc_top = sorted(exc.items(), key=lambda kv: -kv[1])
                n_exc = frota_info["total_geral"] - frota_info["total"]
                m_tipos = mem.registrar(
                    "Tipos de veículo atendidos (recorte do driver)",
                    "PREMISSA DECLARADA",
                    "frota atendível = frota total da área − tipos que a "
                    "empresa não atende (decisão do cliente)",
                    [{"nome": "tipos atendidos: "
                              + ", ".join(dd["tipos_atendidos"]),
                      "valor": R.inteiro(frota_info["total"]) + " veículos"},
                     {"nome": "excluídos do estudo ({} tipos)".format(len(exc)),
                      "valor": "; ".join("{} {}".format(R.inteiro(q), tp)
                                         for tp, q in exc_top[:6])
                               + ("; …" if len(exc_top) > 6 else "")},
                     {"nome": "frota total da área (todos os tipos)",
                      "valor": R.inteiro(frota_info["total_geral"]),
                      "fonte": "SENATRAN, consulta H",
                      "url": frota_info["proveniencia"].get("url")}],
                    "{} − {}".format(R.inteiro(frota_info["total_geral"]),
                                     R.inteiro(n_exc)),
                    R.inteiro(frota_info["total"]) + " veículos atendíveis",
                    racional=dd.get("racional_tipos", ""),
                    provs=[frota_info["proveniencia"]],
                    sql_ref="CONSULTA H",
                    explicacao=("A área tem mais veículos do que a empresa atende: motos e caminhões ficam fora da conta desde o início, por decisão declarada do cliente."),
                )
            tipos = sorted(frota_info["por_tipo"].items(), key=lambda kv: -kv[1])
            blocos_dd.append(
                f"<p><b>Base contável:</b> <b>{R.inteiro(frota_info['total'])}</b> "
                + ("veículos ATENDÍVEIS" if m_tipos else "veículos registrados")
                + f" na região (SENATRAN, {frota_info['referencia']})."
                + (f" Ficam fora do estudo, por decisão da empresa, "
                   f"{R.inteiro(frota_info['total_geral'] - frota_info['total'])} "
                   f"veículos de tipos não atendidos (motocicletas, caminhões "
                   f"etc.).{mem.ref(m_tipos)}" if m_tipos else "")
                + f" <b>Conversão em demanda:</b> "
                f"{dd.get('conversao', 'ver metodologia')}.</p>"
            )
            blocos_dd.append(R.grafico_barras_h(tipos[:6], "veículos", esq=140))
            munis = config["regiao"].get("municipios", [])
            if frota_info.get("por_municipio") and any("fator_acesso" in m for m in munis):
                # cada cidade é um mercado SEPARADO; a consolidação é ponderada
                # pelo fator de acesso (Reilly/Huff) — nunca soma simples
                me = sizing.mercado_enderecavel(frota_info["por_municipio"], munis)
                frota_info["enderecavel"] = me
                t = me["totais"]
                # densidade competitiva MEDIDA por cidade (empresas do setor,
                # todos os regimes e portes, ÷ frota × 1.000) — o dado que
                # calibrou os fatores de acesso deixa de viver só no racional
                dens_mun = {}
                if emp_mun:
                    for l in me["linhas"]:
                        emp_cid = emp_mun.get(l["cidade"])
                        if emp_cid is not None and l["valor_local"]:
                            dens_mun[l["cidade"]] = (
                                emp_cid, emp_cid / l["valor_local"] * 1000)
                m_dens = None
                if dens_mun:
                    m_dens = mem.registrar(
                        "Densidade competitiva por cidade",
                        "DADO",
                        "densidade = empresas ativas do setor na cidade ÷ frota "
                        "da cidade × 1.000",
                        [{"nome": l["cidade"],
                          "valor": ("{} empresas ÷ {} veículos × 1.000 = {}/mil"
                                    .format(R.inteiro(dens_mun[l["cidade"]][0]),
                                            R.inteiro(l["valor_local"]),
                                            _dec(dens_mun[l["cidade"]][1], 1))
                                    if l["cidade"] in dens_mun
                                    else "n/d (cidade sem linha na consulta A4)"),
                          "fonte": "consultas A4 (empresas) e H (frota)"}
                         for l in me["linhas"]],
                        "por cidade (coluna Valor acima)",
                        "coluna Densidade da tabela da seção 3b",
                        racional=("Empresas de TODOS os regimes e portes (inclusive "
                                  "MEI) dos CNAEs do estudo — mede a oferta local "
                                  "total, que retém o mercado da própria cidade."),
                        provs=[prov_cnpj, frota_info["proveniencia"]],
                        sql_ref="CONSULTAS A4 e H",
                        explicacao=("Mede quanta oferta já existe em cada cidade: quantas empresas do ramo para cada mil veículos. Cidade com densidade baixa depende do polo — bom para a loja."),
                    )
                entradas_fat = []
                for l in me["linhas"]:
                    e_fat = {"nome": "{} ({})".format(l["cidade"], l["anel"]),
                             "valor": "{}–{}–{}".format(
                                 R.pct(l["fator"]["min"], 0),
                                 R.pct(l["fator"]["base"], 0),
                                 R.pct(l["fator"]["max"], 0))}
                    if m_dens:
                        e_fat["ref"] = m_dens
                    entradas_fat.append(e_fat)
                m_fatores = mem.registrar(
                    "Fatores de acesso por cidade (modelo gravitacional)",
                    "PREMISSA DECLARADA",
                    "fator de acesso = fração do mercado local que a loja disputa "
                    "(mín–base–máx por cidade)",
                    entradas_fat,
                    "",
                    "intervalos por cidade (acima)",
                    racional=config["regiao"].get("racional_fatores", ""),
                    explicacao=("Que fatia do mercado de cada cidade a loja consegue disputar: 100% na cidade-sede e menos nas vizinhas, calibrado pela oferta local medida."),
                )
                refs_cidades = []
                for l in me["linhas"]:
                    f = l["fator"]
                    cod = mem.registrar(
                        "Frota endereçável — " + l["cidade"],
                        "DADO × PREMISSA",
                        "endereçável = frota local × fator de acesso (mín/base/máx)",
                        [{"nome": "frota local ({})".format(frota_info["referencia"]),
                          "valor": R.inteiro(l["valor_local"]),
                          "fonte": "SENATRAN, consulta H",
                          "url": frota_info["proveniencia"].get("url")},
                         {"nome": "fator de acesso ({})".format(l["anel"]),
                          "valor": "{}–{}–{}".format(R.pct(f["min"], 0),
                                                     R.pct(f["base"], 0),
                                                     R.pct(f["max"], 0)),
                          "ref": m_fatores}],
                        "{fr} × {fmin} = {emin}; {fr} × {fbase} = {ebase}; "
                        "{fr} × {fmax} = {emax}".format(
                            fr=R.inteiro(l["valor_local"]),
                            fmin=R.pct(f["min"], 0),
                            emin=R.inteiro(round(l["enderecavel_min"])),
                            fbase=R.pct(f["base"], 0),
                            ebase=R.inteiro(round(l["enderecavel"])),
                            fmax=R.pct(f["max"], 0),
                            emax=R.inteiro(round(l["enderecavel_max"]))),
                        "{} veículos (base)".format(
                            R.inteiro(round(l["enderecavel"]))),
                        sql_ref="CONSULTA H",
                        explicacao=("Da frota atendível desta cidade, a loja "
                                    "disputa só a fração dada pelo fator de "
                                    "acesso."),
                    )
                    refs_cidades.append(cod)
                m_consol = mem.registrar(
                    "Frota endereçável consolidada — "
                    + config["regiao"].get("apelido", config["regiao"]["sigla"]),
                    "DERIVADO",
                    "consolidado = Σ (frota endereçável de cada cidade); a soma "
                    "simples das frotas locais é só o teto teórico",
                    [{"nome": l["cidade"],
                      "valor": R.inteiro(round(l["enderecavel"])), "ref": cod}
                     for l, cod in zip(me["linhas"], refs_cidades)],
                    " + ".join(R.inteiro(round(l["enderecavel"]))
                               for l in me["linhas"]),
                    "{} veículos (base; mín {}, máx {}; teto teórico {})".format(
                        R.inteiro(round(t["base"])), R.inteiro(round(t["min"])),
                        R.inteiro(round(t["max"])), R.inteiro(round(t["teto"]))),
                    explicacao=("Somando a fatia disputável de cada cidade chega-se à frota que realmente conta para o negócio — somar tudo a 100% inflaria o mercado."),
                )
                dens_completa = dens_mun and len(dens_mun) == len(me["linhas"])
                linhas_me = []
                for l in me["linhas"]:
                    emp_dens = dens_mun.get(l["cidade"])
                    linhas_me.append((
                        l["cidade"], l["anel"], R.inteiro(l["valor_local"]),
                        R.inteiro(emp_dens[0]) if emp_dens else "n/d",
                        _dec(emp_dens[1], 1) if emp_dens else "n/d",
                        f'{R.pct(l["fator"]["min"], 0)}–{R.pct(l["fator"]["base"], 0)}'
                        f'–{R.pct(l["fator"]["max"], 0)}',
                        "{}–<b>{}</b>–{}".format(
                            R.inteiro(round(l["enderecavel_min"])),
                            R.inteiro(round(l["enderecavel"])),
                            R.inteiro(round(l["enderecavel_max"]))),
                    ))
                soma_emp = sum(v[0] for v in dens_mun.values())
                linhas_me.append((
                    "CONSOLIDADO", "ponderado",
                    R.inteiro(round(t["teto"])) + " (teto teórico)",
                    R.inteiro(soma_emp) if dens_completa else "n/d",
                    (_dec(soma_emp / t["teto"] * 1000, 1)
                     if dens_completa and t["teto"] else "—"),
                    "",
                    "{}–<b>{}</b>–{}".format(
                        R.inteiro(round(t["min"])), R.inteiro(round(t["base"])),
                        R.inteiro(round(t["max"]))),
                ))
                blocos_dd.append(
                    "<p><b>Mercado por cidade e consolidação ponderada:</b> cada cidade "
                    "é um mercado próprio (frota local = 100% daquela cidade); a loja "
                    "disputa apenas a fração dada pelo fator de acesso. A soma simples "
                    f"({R.inteiro(round(t['teto']))} veículos) é só o TETO TEÓRICO — o "
                    "que alimenta o dimensionamento é a <b>frota endereçável "
                    f"consolidada: {R.inteiro(round(t['base']))} veículos</b> "
                    f"(intervalo {R.inteiro(round(t['min']))}–{R.inteiro(round(t['max']))} "
                    "pela sensibilidade dos fatores)." + mem.ref(m_consol) + "</p>"
                )
                blocos_dd.append(R.tabela(
                    ["Cidade", "Anel", "Frota local (100%)", "Empresas do setor",
                     "Densidade (emp./mil veíc.)",
                     "Fator de acesso (mín–base–máx)",
                     "Frota endereçável (mín–base–máx)"],
                    linhas_me,
                ))
                blocos_dd.append(
                    '<p class="premissas">'
                    + config["regiao"].get("racional_fatores", "")
                    + (mem.ref(m_dens) if m_dens else "")
                    + mem.ref(m_fatores) + "</p>"
                )
                if dd.get("contexto_regional"):
                    blocos_dd.append(f"<p>{dd['contexto_regional']}.</p>")
            elif frota_info.get("por_municipio"):
                aneis = {m["nome"]: m.get("anel", "") for m in munis}
                blocos_dd.append(
                    "<p>Frota por cidade da área de influência:</p>"
                )
                blocos_dd.append(R.tabela(
                    ["Cidade", "Anel", "Frota"],
                    [(mun, aneis.get(mun, "—"), R.inteiro(q))
                     for mun, q in sorted(frota_info["por_municipio"].items(),
                                          key=lambda kv: -kv[1])],
                ))
            blocos_dd.append(R.selo_fonte(frota_info["proveniencia"]))
        if len(blocos_dd) > 1:
            s.append(secao("3b. Quem compra — o driver de demanda da região", *blocos_dd))

    # 4-6. Tamanho de mercado
    anos = sorted(receita)
    regiao_dado = len(regiao_pesos) >= 2

    # ---- memória de cálculo: cadeia top-down ---------------------------------
    ag_td = config["topdown"]["agregado_sidra"]
    fator_un = ag_td.get("fator_unidade", 1)
    m_tam = mem.registrar(
        "TAM Brasil — receita nacional do setor ({})".format(td["ano_base"]),
        "DADO",
        "TAM = receita do último ano da série oficial × fator de unidade da tabela",
        [{"nome": "receita {} (na unidade da tabela)".format(td["ano_base"]),
          "valor": _num(td["tam"] / fator_un),
          "fonte": ag_td["citacao"], "url": prov_ibge.get("url")},
         {"nome": "fator de unidade", "valor": _num(fator_un),
          "fonte": ("tabela publicada em mil R$" if fator_un == 1000
                    else "unidade da tabela")},
         {"nome": "tabela navegável", "valor": "SIDRA {}".format(ag_td["agregado"]),
          "url": "https://sidra.ibge.gov.br/tabela/{}".format(ag_td["agregado"])}],
        "{} × {}".format(_num(td["tam"] / fator_un), _num(fator_un)),
        R.brl(td["tam"]),
        provs=[prov_ibge],
        explicacao=("Quanto o setor inteiro fatura por ano no Brasil, segundo a pesquisa oficial do IBGE."),
    )
    m_cagr = None
    if td["cagr"] is not None and len(anos) >= 2:
        v0, v1 = receita[anos[0]], receita[anos[-1]]
        n_anos = int(anos[-1]) - int(anos[0])
        m_cagr = mem.registrar(
            "CAGR do mercado ({}–{})".format(anos[0], anos[-1]),
            "DADO",
            "CAGR = (receita final ÷ receita inicial)^(1 ÷ nº de anos) − 1",
            [{"nome": "receita {}".format(anos[0]), "valor": "R$ " + _num(v0),
              "ref": m_tam},
             {"nome": "receita {}".format(anos[-1]), "valor": "R$ " + _num(v1),
              "ref": m_tam},
             {"nome": "nº de anos", "valor": str(n_anos)}],
            "({} ÷ {})^(1/{}) − 1".format(_num(v1), _num(v0), n_anos),
            R.pct(td["cagr"]),
            explicacao=("A velocidade média de crescimento do setor por ano no período da série."),
        )
    rac_seg = td["premissas"]["racional_segmento"]
    if rac_seg.startswith("DADO-PROXY"):
        classif_seg = "DADO-PROXY"
    elif rac_seg.startswith("DADO"):
        classif_seg = "DADO"
    else:
        classif_seg = "PREMISSA DECLARADA"
    part_seg = td["premissas"]["participacao_segmento"]
    if det_frac:
        cfg_seg = config["topdown"]["segmento_dado"]
        m_frac = mem.registrar(
            "Fração do segmento no setor ({})".format(det_frac["ano"]),
            classif_seg,
            "fração = valor do segmento ÷ valor do total, na tabela oficial",
            [{"nome": "segmento (numerador)", "valor": _num(det_frac["numerador"]),
              "fonte": cfg_seg["citacao"], "url": det_frac.get("url_setor")},
             {"nome": "total (denominador)",
              "valor": _num(det_frac["denominador"]),
              "url": det_frac.get("url_total")},
             {"nome": "tabela navegável",
              "valor": "SIDRA {}".format(cfg_seg["agregado"]),
              "url": "https://sidra.ibge.gov.br/tabela/{}".format(
                  cfg_seg["agregado"])}],
            "{} ÷ {}".format(_num(det_frac["numerador"]),
                             _num(det_frac["denominador"])),
            R.pct(part_seg),
            racional=rac_seg,
            provs=[prov_segmento] if prov_segmento else [],
            explicacao=("Do setor inteiro, qual pedaço é do segmento estudado — medido na tabela oficial, com o viés (quando houver) declarado."),
        )
    else:
        m_frac = mem.registrar(
            "Fração do segmento no setor",
            classif_seg,
            "participação do segmento aplicada sobre o TAM (valor declarado "
            "no estudo)",
            [{"nome": "participação do segmento", "valor": R.pct(part_seg)}],
            "",
            R.pct(part_seg),
            racional=rac_seg,
            explicacao=("Do setor inteiro, qual pedaço é do segmento estudado."),
        )
    part_reg = td["premissas"]["participacao_regiao"]
    pct_chave = R.pct(part_reg, 1 if part_reg >= 0.01 else 4)
    if regiao_dado:
        vals_reg = sorted(p["valor"] for p in regiao_pesos)
        m_chave = mem.registrar(
            "Chave regional — participação de {} no Brasil".format(
                config["regiao"]["sigla"]),
            "DADO",
            "chave = mediana dos pesos públicos independentes (detalhe na seção 4)",
            [{"nome": p["rotulo"], "valor": R.pct(p["valor"]),
              "fonte": p["racional"], "url": (p["prov"] or {}).get("url")}
             for p in regiao_pesos],
            "mediana de {{{}}}".format("; ".join(R.pct(v) for v in vals_reg)),
            pct_chave,
            explicacao=("Qual fatia do mercado nacional está na região: medida por mais de um caminho independente, ficando com o valor do meio."),
        )
    else:
        rac_reg = td["premissas"]["racional_regiao"]
        entradas_reg = [{"nome": "participação da região", "valor": pct_chave}]
        if m_consol:
            entradas_reg.append({"nome": "frota endereçável consolidada",
                                 "valor": "ver verbete", "ref": m_consol})
        m_chave = mem.registrar(
            "Chave regional — participação da área no Brasil",
            "DADO" if rac_reg.startswith("DADO") else "PREMISSA DECLARADA",
            "chave regional declarada no estudo (a conta está no racional abaixo)",
            entradas_reg,
            "",
            pct_chave,
            racional=rac_reg,
            sql_ref="CONSULTAS H e H2 (frota)" if m_consol else None,
            explicacao=("Qual fatia do mercado nacional está na área do estudo."),
        )
    m_sam_td = mem.registrar(
        "SAM top-down — {}".format(config["regiao"]["nome"]),
        "DERIVADO",
        "SAM top-down = TAM × fração do segmento × chave regional",
        [{"nome": "TAM", "valor": R.brl(td["tam"]), "ref": m_tam},
         {"nome": "fração do segmento", "valor": R.pct(part_seg), "ref": m_frac},
         {"nome": "chave regional", "valor": pct_chave, "ref": m_chave}],
        "{} × {} × {}".format(_num(td["tam"]), R.pct(part_seg), pct_chave),
        R.brl(td["sam"]),
        explicacao=("O bolo nacional recortado para o segmento e para a região — o mercado local calculado de cima para baixo."),
    )

    blocos_td = [
        f"<p>A receita nacional do setor somou <b>{R.brl(td['tam'])}</b> em {td['ano_base']}"
        + mem.ref(m_tam)
        + (f", com CAGR de <b>{R.pct(td['cagr'])}</b> desde {anos[0]}" + mem.ref(m_cagr)
           if td["cagr"] else "")
        + f". Aplicando a participação do segmento ({R.pct(td['premissas']['participacao_segmento'],0)}) "
        f"e da região ({R.pct(td['premissas']['participacao_regiao'], 0 if td['premissas']['participacao_regiao'] >= 0.01 else 3)}), o SAM top-down de "
        f"{config['regiao']['nome']} é <b>{R.brl(td['sam'])}</b>." + mem.ref(m_sam_td)
        + "</p>",
        R.tabela(["Ano", "Receita (R$)"], [(a, R.brl(receita[a])) for a in anos]),
        f'<p class="premissas">{"Segmento (DADO oficial)" if prov_segmento else "Premissas: segmento"} — '
        f'{td["premissas"]["racional_segmento"]};{mem.ref(m_frac)} '
        f'região ({"DADO triangulado" if regiao_dado else "premissa"}) — '
        f'{td["premissas"]["racional_regiao"]}.{mem.ref(m_chave)}</p>',
    ]
    if regiao_dado:
        blocos_td.append(
            "<p><b>Participação regional triangulada</b> — pesos públicos "
            "independentes (a mediana entra no SAM; o intervalo mostra a "
            "incerteza da chave regional):</p>"
        )
        blocos_td.append(R.tabela(
            ["Peso", "Participação de " + config["regiao"]["sigla"], "Base"],
            [(p["rotulo"], R.pct(p["valor"]), p["racional"]) for p in regiao_pesos],
        ))
    if config.get("benchmarks_externos"):
        blocos_td.append(
            "<p><b>Referências externas</b> (declaradas e NÃO verificadas — "
            "servem para contraste de ordem de grandeza e nunca entram no "
            "cálculo):</p>"
        )
        blocos_td.append(R.tabela(
            ["Referência", "O que diz", "Fonte"],
            [(b["rotulo"], b["texto"],
              ('<a href="{}">{}</a>'.format(b["url"], b["fonte"])
               if b.get("url") else b["fonte"]))
             for b in config["benchmarks_externos"]],
        ))
    blocos_td.append(R.selo_fonte(prov_ibge))
    if prov_segmento:
        blocos_td.append(R.selo_fonte(prov_segmento))
    for p in regiao_pesos:
        if p["prov"]:
            blocos_td.append(R.selo_fonte(p["prov"]))
    s.append(secao("4. Tamanho de mercado — top-down", *blocos_td))

    nota_secundaria = ""
    n_sec = config["icp"].get("empresas_somente_cnae_secundario")
    if n_sec:
        nota_secundaria = (
            f"<p>Nota metodológica: além dessas, <b>{R.inteiro(n_sec)}</b> empresas têm o "
            "CNAE do setor apenas como atividade secundária e não entram na contagem "
            "(somatório por CNAE — uma empresa com os dois códigos como secundários conta "
            "duas vezes; detalhe por atividade na seção 7b). O dimensionamento pelo CNAE "
            "principal é, portanto, a faixa conservadora.</p>"
        )
    # ---- memória de cálculo: cadeia bottom-up --------------------------------
    rac_atv = bu["premissas"]["racional_atividade"]
    m_icp = mem.registrar(
        "ICP — empresas-alvo cadastradas",
        "DADO",
        "ICP = universo do CNAE na região filtrado por porte e faixa de idade",
        [{"nome": "universo (empresas ativas)",
          "valor": R.inteiro(contagem["universo_empresas"]),
          "fonte": prov_cnpj.get("fonte"), "url": prov_cnpj.get("url")},
         {"nome": "portes aceitos", "valor": ", ".join(config["icp"]["portes"])},
         {"nome": "faixas de idade aceitas (anos)",
          "valor": ", ".join(config["icp"]["faixas_idade"])}],
        "filtro sobre o agregado por CNAE × regime × porte × idade (consulta A4)",
        R.inteiro(contagem["n_icp"]) + " empresas",
        racional=bu["premissas"]["icp"],
        provs=[prov_cnpj],
        sql_ref="CONSULTA A4",
        explicacao=("Concorrentes cadastrados com o perfil que interessa (tamanho e tempo de vida) — ainda sem separar quem opera de verdade."),
    )
    m_comp = None
    m_funil_v = None
    m_icp_end = None
    if funil_mun:
        cidades_ord = sorted(funil_mun.items(), key=lambda kv: -kv[1]["universo"])
        m_comp = mem.registrar(
            "Composição do universo por cidade e atividade",
            "DADO",
            "universo da cidade = empresas ativas dos CNAEs do estudo, todos "
            "os regimes e portes (inclusive MEI) — NÃO ler como lojas da "
            "linha-âncora; a abertura por CNAE está na tabela da seção 5",
            [{"nome": mun,
              "valor": "{} empresas; maior linha: {} ({} empresas)".format(
                  R.inteiro(f["universo"]),
                  max(f["por_cnae"].items(),
                      key=lambda kv: kv[1]["universo"])[0],
                  R.inteiro(max(pc["universo"]
                                for pc in f["por_cnae"].values()))),
              "fonte": "consulta A4 (coluna municipio)"}
             for mun, f in cidades_ord],
            "detalhe por CNAE × cidade na tabela da seção 5",
            R.inteiro(contagem["universo_empresas"]) + " empresas no total",
            provs=[prov_cnpj],
            sql_ref="CONSULTA A4",
            explicacao=("Abre o que existe em cada cidade, linha por linha — evita confundir o total de empresas do ramo com lojas da linha principal."),
        )
        m_funil_v = mem.registrar(
            "Funil bottom-up por cidade",
            "DADO",
            "por cidade: universo → ICP (porte e idade) → optantes do Simples "
            "no ICP (proxy de operação)",
            [{"nome": mun,
              "valor": "universo {} → ICP {} → Simples {}".format(
                  R.inteiro(f["universo"]), R.inteiro(f["icp"]),
                  R.inteiro(f["icp_simples"])),
              "ref": m_comp}
             for mun, f in cidades_ord],
            "consolidado: universo {} → ICP {} → Simples {} (taxa medida {})".format(
                R.inteiro(sum(f["universo"] for _, f in cidades_ord)),
                R.inteiro(sum(f["icp"] for _, f in cidades_ord)),
                R.inteiro(sum(f["icp_simples"] for _, f in cidades_ord)),
                R.pct(sum(f["icp_simples"] for _, f in cidades_ord)
                      / max(1, sum(f["icp"] for _, f in cidades_ord)), 1)),
            "ver tabela da seção 5",
            sql_ref="CONSULTA A4",
            explicacao=("De todas as empresas de cada cidade, quantas têm o perfil-alvo e quantas mostram sinal de operação real."),
        )
        if icp_enderecavel is not None:
            m_icp_end = mem.registrar(
                "ICP endereçável (ponderado pelos fatores de acesso)",
                "DERIVADO",
                "ICP endereçável = Σ (ICP da cidade × fator de acesso base) — "
                "concorrente de cidade-satélite disputa o mesmo mercado que a "
                "loja só na fração do fator; contá-lo em 100% superestimaria "
                "o SAM local",
                [{"nome": mun,
                  "valor": "{} × {} = {}".format(
                      R.inteiro(f["icp"]),
                      R.pct(fatores_mun.get(mun, {"base": 1.0})["base"], 0),
                      _dec(f["icp"]
                           * fatores_mun.get(mun, {"base": 1.0})["base"], 1)),
                  "ref": m_funil_v}
                 for mun, f in sorted(funil_mun.items(),
                                      key=lambda kv: -kv[1]["icp"])],
                " + ".join(
                    _dec(f["icp"] * fatores_mun.get(mun, {"base": 1.0})["base"], 1)
                    for mun, f in sorted(funil_mun.items(),
                                         key=lambda kv: -kv[1]["icp"])),
                "{} concorrentes-equivalentes (ICP real da área: {})".format(
                    R.inteiro(round(icp_enderecavel)),
                    R.inteiro(contagem["n_icp"])),
                explicacao=("Concorrente de cidade vizinha só disputa parte do mesmo mercado que a loja — então ele conta só essa parte na soma."),
            )
    m_taxa = mem.registrar(
        "Taxa de atividade efetiva",
        "DADO-PROXY" if rac_atv.startswith("MEDIDO") else "PREMISSA DECLARADA",
        "taxa = fração do ICP efetivamente operante (proxy: adesão ao Simples "
        "Nacional, medida no próprio agregado)",
        [{"nome": "taxa aplicada", "valor": R.pct(bu["taxa_atividade"], 1)}],
        "",
        R.pct(bu["taxa_atividade"], 1),
        racional=rac_atv,
        sql_ref="CONSULTA A4 (coluna regime)",
        explicacao=("De cada 100 empresas cadastradas com o perfil, quantas mostram sinal de funcionar de verdade (optar pelo Simples é o sinal usado); as demais tendem a ser cadastros que nunca viraram negócio."),
    )
    m_oper = mem.registrar(
        "Empresas-alvo operantes",
        "DERIVADO",
        "operantes = ICP {} × taxa de atividade (arredondado)".format(
            "endereçável" if m_icp_end else ""),
        [{"nome": "ICP" + (" endereçável" if m_icp_end else ""),
          "valor": R.inteiro(bu["n_icp"]),
          "ref": m_icp_end if m_icp_end else m_icp},
         {"nome": "taxa de atividade", "valor": R.pct(bu["taxa_atividade"], 1),
          "ref": m_taxa}],
        "{} × {}".format(R.inteiro(bu["n_icp"]), R.pct(bu["taxa_atividade"], 1)),
        R.inteiro(bu["n_operantes"]) + " empresas",
        explicacao=("Quantos concorrentes de verdade existem no mercado disputado."),
    )
    m_ticket = mem.registrar(
        "Ticket médio anual por empresa",
        "PREMISSA DECLARADA",
        "receita média anual de uma empresa operante do ICP",
        [{"nome": "ticket", "valor": "R$ " + _num(bu["ticket"])}],
        "",
        R.brl(bu["ticket"]),
        racional=bu["premissas"]["racional_ticket"],
        explicacao=("Quanto um concorrente típico fatura por ano — premissa declarada, com as referências que a sustentam."),
    )
    m_sam_bu = mem.registrar(
        "SAM bottom-up",
        "DERIVADO",
        "SAM bottom-up = empresas operantes × ticket médio anual",
        [{"nome": "operantes", "valor": R.inteiro(bu["n_operantes"]),
          "ref": m_oper},
         {"nome": "ticket", "valor": "R$ " + _num(bu["ticket"]), "ref": m_ticket}],
        "{} × {}".format(R.inteiro(bu["n_operantes"]), _num(bu["ticket"])),
        R.brl(bu["sam"]),
        explicacao=("O mercado local medido contando quem já está nele: número de concorrentes reais × quanto cada um fatura."),
    )

    if m_icp_end:
        frase_icp = (
            f"o recorte de ICP resulta em <b>{R.inteiro(contagem['n_icp'])}</b> "
            f"empresas cadastradas nas cidades do estudo;{mem.ref(m_icp)} "
            f"ponderando cada cidade pelo fator de acesso (seção 3b), o "
            f"<b>ICP endereçável</b> é <b>{R.inteiro(bu['n_icp'])}</b> "
            f"concorrentes-equivalentes.{mem.ref(m_icp_end)}"
        )
    else:
        frase_icp = (
            f"o recorte de ICP resulta em <b>{R.inteiro(bu['n_icp'])}</b> "
            f"empresas cadastradas.{mem.ref(m_icp)}"
        )
    blocos_bu = [
        f"<p>O universo do CNAE na região tem <b>{R.inteiro(contagem['universo_empresas'])}</b> "
        f"empresas ativas ({R.inteiro(contagem['universo_estabelecimentos'])} estabelecimentos, "
        f"contando filiais); {frase_icp} Aplicando a premissa de atividade efetiva de "
        f"{R.pct(bu['taxa_atividade'], 0)}, chega-se a <b>{R.inteiro(bu['n_operantes'])}</b> "
        f"empresas-alvo operantes.{mem.ref(m_oper)} Com ticket médio anual de {R.brl(bu['ticket'])}, o SAM "
        f"bottom-up é <b>{R.brl(bu['sam'])}</b>.{mem.ref(m_sam_bu)}</p>",
        nota_secundaria,
    ]
    if funil_mun:
        desc_cnae = {c["codigo"]: c["descricao"] for c in config["cnaes"]}
        cidades_ord = sorted(funil_mun.items(), key=lambda kv: -kv[1]["universo"])
        # (a) composição por CNAE × cidade — o universo NÃO é "lojas da
        # linha-âncora": abre o que cada cidade realmente tem em cada linha
        linhas_comp = []
        for mun, f in cidades_ord:
            for cn, pc in sorted(f["por_cnae"].items(),
                                 key=lambda kv: -kv[1]["universo"]):
                linhas_comp.append((
                    mun, "{} — {}".format(cn, desc_cnae.get(cn, "")),
                    R.inteiro(pc["universo"]), R.inteiro(pc["mei"])))
        blocos_bu.append(
            "<p><b>Composição da concorrência por cidade e atividade</b> — o "
            "universo soma as empresas ativas de TODAS as linhas do estudo, "
            "inclusive MEIs (borracharias, lava-jatos, mecânicas de bairro); a "
            "abertura abaixo evita ler o total como lojas da linha-âncora:"
            f"{mem.ref(m_comp)}</p>"
        )
        blocos_bu.append(R.tabela(
            ["Cidade", "Atividade (CNAE principal)", "Empresas ativas",
             "das quais MEI"],
            linhas_comp,
        ))
        # (b) funil bottom-up por cidade + consolidação ponderada
        tem_fator = icp_enderecavel is not None
        linhas_funil = []
        for mun, f in sorted(funil_mun.items(), key=lambda kv: -kv[1]["icp"]):
            fat = (fatores_mun.get(mun, {"base": 1.0})["base"]
                   if tem_fator else None)
            linhas_funil.append((
                mun, R.inteiro(f["universo"]), R.inteiro(f["icp"]),
                R.inteiro(f["icp_simples"]),
                R.pct(fat, 0) if fat is not None else "—",
                _dec(f["icp"] * fat, 1) if fat is not None else "—"))
        tot_uni = sum(f["universo"] for _, f in cidades_ord)
        tot_icp = sum(f["icp"] for _, f in cidades_ord)
        tot_sim = sum(f["icp_simples"] for _, f in cidades_ord)
        linhas_funil.append((
            "CONSOLIDADO", R.inteiro(tot_uni), R.inteiro(tot_icp),
            R.inteiro(tot_sim), "ponderado",
            "<b>{}</b>".format(R.inteiro(round(icp_enderecavel)))
            if tem_fator else "—"))
        blocos_bu.append(
            "<p><b>Funil bottom-up por cidade:</b> universo → ICP (porte e "
            "idade) → optantes do Simples no ICP (proxy de operação"
            + (", taxa medida de {}".format(R.pct(tot_sim / tot_icp, 1))
               if tot_icp else "")
            + ")"
            + (" → ICP endereçável pelo fator de acesso — a última coluna é o "
               "que alimenta o SAM" if tem_fator else "")
            + f".{mem.ref(m_funil_v)}</p>"
        )
        blocos_bu.append(R.tabela(
            ["Cidade", "Universo (todas as linhas)", "ICP (ME/EPP, 2+ anos)",
             "das quais no Simples", "Fator de acesso (base)",
             "ICP endereçável"],
            linhas_funil,
        ))
    blocos_bu += [
        R.grafico_barras_h(
            sorted(contagem["por_porte"].items(), key=lambda kv: -kv[1]),
            "empresas ativas",
        ),
        f'<p class="premissas">Premissas: {bu["premissas"]["icp"]}. '
        f'Ticket: {bu["premissas"]["racional_ticket"]}.{mem.ref(m_ticket)} '
        f'Atividade efetiva: {bu["premissas"]["racional_atividade"]}{mem.ref(m_taxa)}</p>',
        R.selo_fonte(prov_cnpj),
    ]
    if contagem.get("por_regime"):
        blocos_bu.append(
            "<p><b>Estrutura tributária</b> (dado público distingue MEI e Simples; "
            "Lucro Presumido × Lucro Real é sigilo fiscal e aparece agrupado como "
            "&quot;Fora do Simples&quot; — proxy por porte em docs/metodologia-v3.md):</p>"
        )
        rotulos_regime = {"MEI": "MEI", "SIMPLES": "Simples",
                          "FORA_SIMPLES": "Fora do Simples"}
        blocos_bu.append(R.grafico_barras_h(
            sorted(((rotulos_regime.get(k, k), v) for k, v in contagem["por_regime"].items()),
                   key=lambda kv: -kv[1]),
            "empresas ativas",
            esq=140,
        ))
    if dist_redes:
        ordem = ["1", "2-5", "6+"]
        total_emp_r = sum(e for e, _ in dist_redes.values())
        est_redes = sum(est for f, (_, est) in dist_redes.items() if f != "1")
        total_est_r = sum(est for _, est in dist_redes.values())
        blocos_bu.append(
            f"<p><b>Redes e filiais (força dos players):</b> filiais localizadas na região "
            f"contam como cobertura do mercado local, mesmo com sede fora dela. "
            f"{R.pct(est_redes / total_est_r)} dos estabelecimentos pertencem a empresas "
            "com mais de uma unidade na região:</p>"
        )
        blocos_bu.append(R.grafico_barras_h(
            [(f"{f} unid.", dist_redes[f][0]) for f in ordem if f in dist_redes],
            "empresas",
            esq=110,
        ))
        blocos_bu.append(R.tabela(
            ["Unidades na região", "Empresas", "Estabelecimentos"],
            [(f, R.inteiro(dist_redes[f][0]), R.inteiro(dist_redes[f][1]))
             for f in ordem if f in dist_redes],
        ))
    if cempre:
        ano_c, qtd_c, prov_c = cempre
        cfg_val = config["bottomup_validacao"]
        m_cempre = mem.registrar(
            "Validação cruzada — CEMPRE (IBGE)",
            "DADO",
            "comparação de ordem de grandeza: operantes do bottom-up vs "
            "contagem oficial do CEMPRE (escopos declarados podem diferir)",
            [{"nome": "operantes (bottom-up)",
              "valor": R.inteiro(bu["n_operantes"]), "ref": m_oper},
             {"nome": "CEMPRE {} — classe {}".format(
                 ano_c, cfg_val.get("rotulo_classe", "CNAE do setor")),
              "valor": R.inteiro(qtd_c),
              "fonte": cfg_val["citacao"], "url": prov_c.get("url")},
             {"nome": "tabela navegável",
              "valor": "SIDRA {}".format(cfg_val["agregado"]),
              "url": "https://sidra.ibge.gov.br/tabela/{}".format(
                  cfg_val["agregado"])}],
            "{} (medido) vs {} (CEMPRE)".format(
                R.inteiro(bu["n_operantes"]), R.inteiro(qtd_c)),
            "referência de ordem de grandeza",
            racional=cfg_val.get(
                "escopo_texto", "em " + config["regiao"]["nome"]),
            provs=[prov_c],
            explicacao=("Conferência com uma contagem oficial independente do IBGE — os números não precisam bater, mas precisam fazer sentido juntos."),
        )
        blocos_bu.append(
            f"<p><b>Validação cruzada (fonte oficial independente):</b> o CEMPRE do IBGE "
            f"registra <b>{R.inteiro(qtd_c)}</b> empresas da classe "
            f"{config['bottomup_validacao'].get('rotulo_classe', 'CNAE do setor')} "
            f"{config['bottomup_validacao'].get('escopo_texto', 'em ' + config['regiao']['nome'])} "
            f"({ano_c}). A contagem do CEMPRE segue metodologia "
            "própria (empresas, não estabelecimentos, e cobertura parcial de MEIs), servindo "
            "como referência de ordem de grandeza para o recorte formal (ME/EPP) usado no "
            f"bottom-up.{mem.ref(m_cempre)}</p>"
        )
        blocos_bu.append(R.selo_fonte(prov_c))
    s.append(secao("5. Tamanho de mercado — bottom-up (censo CNPJ)", *blocos_bu))

    cen = bu["cenarios"]
    blocos_anc = []
    if informal:
        labor_share = config.get("labor_share", 0.55)
        formal_labor = informal["n_formal"] * 3724.24 if False else None
        rend_formal = None
        # rendimento formal vem do CSV da PNAD (linha FORMAL)
        import csv as _csv
        for l in _csv.DictReader(open(pnad.arquivo(config), encoding="utf-8")):
            if l["uf"] == config["regiao"]["sigla"] and l["categoria"] == "FORMAL":
                rend_formal = float(l["rendimento_medio_mensal"])
        if rend_formal:
            mercado_labor = informal["n_formal"] * rend_formal * 12 / labor_share
            m_labor = mem.registrar(
                "Âncora labor-input (PNAD)",
                "DADO × PREMISSA",
                "mercado formal total = trabalhadores formais × rendimento médio "
                "mensal × 12 ÷ participação do trabalho na receita",
                [{"nome": "trabalhadores formais",
                  "valor": R.inteiro(informal["n_formal"]),
                  "fonte": informal["proveniencia"].get("fonte"),
                  "url": informal["proveniencia"].get("url")},
                 {"nome": "rendimento médio mensal",
                  "valor": "R$ " + _num(rend_formal),
                  "fonte": "PNAD Contínua (consulta F), categoria FORMAL"},
                 {"nome": "participação do trabalho (labor share)",
                  "valor": R.pct(labor_share, 0) + " [premissa]"}],
                "{} × {} × 12 ÷ {}".format(
                    R.inteiro(informal["n_formal"]), _num(rend_formal),
                    R.pct(labor_share, 0)),
                R.brl(mercado_labor),
                provs=[informal["proveniencia"]],
                sql_ref="CONSULTA F (PNAD)",
                explicacao=("Estima o mercado pelo lado dos salários: trabalhadores × renda ÷ fatia do trabalho na receita — enxerga também o que o CNPJ não mostra."),
            )
            blocos_anc.append(
                "<p><b>Diagnóstico por três âncoras independentes</b> (setores intensivos em "
                "MEI, como beleza, são subcapturados pelo universo da PAS — a âncora "
                "trabalhista dimensiona o mercado formal TOTAL):</p>"
            )
            blocos_anc.append(R.tabela(
                ["Âncora", "O que mede", "Valor (SP/ano)"],
                [
                    ("Top-down PAS", "receita formal do universo de pesquisa do IBGE "
                     "(≈ empresas do CEMPRE) — PISO do segmento corporativo",
                     R.brl(td["sam"]) + mem.ref(m_sam_td)),
                    ("Bottom-up CNPJ", "empresas ME/EPP operantes × ticket "
                     "(exclui MEI)", R.brl(bu["sam"]) + mem.ref(m_sam_bu)),
                    ("Labor-input (PNAD)", f"{R.inteiro(informal['n_formal'])} trabalhadores "
                     f"formais × rendimento × 12 ÷ participação do trabalho "
                     f"({R.pct(labor_share, 0)} [premissa]) — mercado formal TOTAL, "
                     "inclusive MEI", R.brl(mercado_labor) + mem.ref(m_labor)),
                ],
            ))
            if not tri["convergente"] and mercado_labor > td["sam"] * 3:
                blocos_anc.append(
                    "<p>Leitura: a âncora trabalhista é múltiplas vezes maior que o top-down "
                    "da PAS — indício forte de que a PAS cobre apenas a fatia corporativa "
                    "deste setor. Para setores assim, o top-down preferencial é o lado da "
                    "demanda (POF) ou o labor-input; o valor da PAS deve ser lido como piso, "
                    "não como o mercado.</p>"
                )
    if demanda:
        cfg_d = config["topdown_demanda"]
        ipca_pontos, prov_ipca = demanda["ipca_pof"]
        fator_ipca = 1.0
        for _, v in ipca_pontos:
            fator_ipca *= 1 + v / 100
        ano_pof4 = str(demanda["ano_pof"])[:4]
        ano_dom, n_dom, prov_dom = demanda["domicilios"]
        mercado_demanda = (demanda["despesa_mensal_familia"] * 12 * n_dom * fator_ipca)
        m_pof = mem.registrar(
            "Âncora de demanda (POF × domicílios × IPCA)",
            "DADO",
            "demanda anual = despesa média mensal familiar × 12 × domicílios × "
            "fator IPCA acumulado desde a POF",
            [{"nome": "despesa mensal familiar (POF {})".format(demanda["ano_pof"]),
              "valor": "R$ " + _dec(demanda["despesa_mensal_familia"], 2),
              "fonte": cfg_d["citacao"],
              "url": demanda["provs"][0].get("url") if demanda["provs"] else None},
             {"nome": "domicílios (Censo {})".format(ano_dom),
              "valor": R.inteiro(n_dom),
              "fonte": cfg_d["domicilios"]["citacao"],
              "url": prov_dom.get("url")},
             {"nome": "fator IPCA ({} meses desde jan/{})".format(
                 len(ipca_pontos), ano_pof4),
              "valor": _dec(fator_ipca, 2),
              "fonte": "produto de (1 + variação mensal ÷ 100), BCB SGS 433",
              "url": prov_ipca.get("url")}],
            "{} × 12 × {} × {}".format(
                _dec(demanda["despesa_mensal_familia"], 2), _num(n_dom),
                _dec(fator_ipca, 2)),
            R.brl(mercado_demanda),
            racional=cfg_d["nota_regional"],
            provs=demanda["provs"] + [prov_dom, prov_ipca],
            explicacao=("Quanto as famílias declaram gastar com o setor, vezes o número de casas da região, corrigido pela inflação até hoje."),
        )
        blocos_anc.append(
            f"<p><b>Âncora de demanda (POF):</b> despesa média mensal familiar com o setor de "
            f"{R.brl(demanda['despesa_mensal_familia'])} (POF {demanda['ano_pof']}) × "
            f"{R.inteiro(n_dom)} domicílios (Censo {ano_dom}) × 12, corrigida pelo IPCA "
            f"acumulado desde jan/{ano_pof4} "
            f"(fator {fator_ipca:.2f}, {len(ipca_pontos)} meses) "
            f"= <b>{R.brl(mercado_demanda)}</b>/ano.{mem.ref(m_pof)} O lado da demanda "
            "enxerga o mercado "
            "inteiro (formal + informal), mas a POF tende a subdeclarar despesas pessoais — "
            "ler como piso da demanda. "
            f"Nota regional: {cfg_d['nota_regional']}.</p>"
        )
        for prov_d in demanda["provs"]:
            blocos_anc.append(R.selo_fonte(prov_d))
        blocos_anc.append(R.selo_fonte(prov_dom))
        blocos_anc.append(R.selo_fonte(prov_ipca))
    m_dl = None
    if demanda_linhas and demanda_linhas["total"]:
        entradas_dl = []
        for l in demanda_linhas["linhas"]:
            if l["mercado"] is None:
                entradas_dl.append({
                    "nome": l["nome"],
                    "valor": "não dimensionada (sem parâmetro de frequência "
                             "com fonte — a levantar com a empresa)"})
            elif l["qtd_ano"] is not None:
                entradas_dl.append({
                    "nome": l["nome"],
                    "valor": "{} veíc. × {}/ano = {} {} × R$ {} = {}".format(
                        _num(l["base_qtd"]), _dec(l["frequencia_ano"], 1),
                        _num(l["qtd_ano"]), l.get("unidade", "un."),
                        _num(l["preco_medio_brl"]), R.brl(l["mercado"])),
                    "fonte": l.get("racional_frequencia", "")})
            else:
                entradas_dl.append({
                    "nome": l["nome"],
                    "valor": "{} veíc. × R$ {}/veíc./ano = {}".format(
                        _num(l["base_qtd"]),
                        _dec(l["valor_anual_por_veiculo"], 2),
                        R.brl(l["mercado"])),
                    "fonte": l.get("racional_frequencia", "")})
        m_dl = mem.registrar(
            "Âncora de demanda por linha de negócio",
            "DADO × PREMISSA",
            "mercado da linha = base atendível ponderada × frequência anual "
            "de uso × preço médio (frequências e preços = premissas "
            "declaradas, cada uma com sua fonte)",
            entradas_dl,
            "soma das linhas dimensionadas (detalhe na seção 7b)",
            R.brl(demanda_linhas["total"]) + "/ano",
            racional=("Método incorporado do plano de negócio da empresa "
                      "(dimensionamento por linha da analista), formalizado "
                      "sobre a frota oficial ponderada pelos fatores de "
                      "acesso; frequências e preços a validar com a empresa"),
            explicacao=("Para cada serviço, contamos quantos veículos podem "
                        "usar, quantas vezes por ano em média e a que preço. "
                        "A soma é quanto os moradores da área tendem a GASTAR "
                        "por ano nessas linhas — a demanda. Ela é maior que o "
                        "SAM bottom-up porque este mede só a receita dos "
                        "concorrentes formais (ME/EPP) da área: a diferença é "
                        "atendida por MEIs e informais, por lojas de fora da "
                        "área, ou é espaço real de expansão."),
        )
        blocos_anc.append(
            "<p><b>Âncora de demanda por linha de negócio:</b> os moradores da "
            f"área tendem a gastar <b>{R.brl(demanda_linhas['total'])}</b>/ano "
            "nas linhas do estudo (frota atendível × frequência × preço — "
            f"tabela completa na seção 7b).{mem.ref(m_dl)} O SAM bottom-up "
            f"({R.brl(bu['sam'])}) mede só a receita dos concorrentes FORMAIS "
            "do perfil-alvo — a diferença entre demanda e oferta formal local "
            "é atendida por MEIs/informais e por lojas de fora da área, ou "
            "indica espaço de expansão.</p>"
        )
    # ---- memória de cálculo: SAM central, triangulação, SOM e sensibilidade --
    if usa_bu_central:
        m_sam_central = mem.registrar(
            "SAM central do estudo",
            "DERIVADO",
            "SAM central = SAM bottom-up ({})".format(detalhe_sam),
            [{"nome": "SAM bottom-up (central)", "valor": R.brl(bu["sam"]),
              "ref": m_sam_bu},
             {"nome": "SAM top-down (referência)", "valor": R.brl(td["sam"]),
              "ref": m_sam_td}],
            "",
            R.brl(sam_central),
            racional=config.get("racional_sam_central", ""),
            explicacao=("O número oficial do estudo para o tamanho do mercado local, e por que este caminho de cálculo foi o escolhido."),
        )
    else:
        m_sam_central = mem.registrar(
            "SAM central do estudo",
            "DERIVADO",
            "SAM central = média simples das duas metodologias",
            [{"nome": "SAM top-down", "valor": R.brl(td["sam"]), "ref": m_sam_td},
             {"nome": "SAM bottom-up", "valor": R.brl(bu["sam"]), "ref": m_sam_bu}],
            "({} + {}) ÷ 2".format(_num(td["sam"]), _num(bu["sam"])),
            R.brl(sam_central),
            explicacao=("O número oficial do estudo para o tamanho do mercado local: a média dos dois caminhos de cálculo."),
        )
    tri_maior = max(td["sam"], bu["sam"])
    tri_menor = min(td["sam"], bu["sam"])
    m_tri = mem.registrar(
        "Triangulação das metodologias",
        "DERIVADO",
        "divergência = (maior − menor) ÷ maior",
        [{"nome": "SAM top-down", "valor": R.brl(td["sam"]), "ref": m_sam_td},
         {"nome": "SAM bottom-up", "valor": R.brl(bu["sam"]), "ref": m_sam_bu}],
        "({} − {}) ÷ {}".format(_num(tri_maior), _num(tri_menor), _num(tri_maior)),
        R.pct(tri["divergencia"]),
        explicacao=("Quanto os dois jeitos independentes de calcular divergem entre si — quanto menor, mais confiável a estimativa."),
    )
    m_som = mem.registrar(
        "SOM por cenário de captura ({} anos)".format(bu["horizonte_anos"]),
        "PREMISSA DECLARADA",
        "SOM = SAM bottom-up × taxa de captura do cenário",
        [{"nome": "SAM bottom-up", "valor": R.brl(bu["sam"]), "ref": m_sam_bu}]
        + [{"nome": "cenário " + nome,
            "valor": "{} × {} = {}".format(_num(bu["sam"]), R.pct(c["taxa"]),
                                           R.brl(c["som"]))}
           for nome, c in cen.items()],
        "por cenário (acima)",
        R.brl(som_base) + " (cenário-base)",
        racional=config["captura"].get("racional", ""),
        explicacao=("A meta de receita: que fatia do mercado a empresa captura em cada cenário, do pessimista ao otimista."),
    )
    m_sens = mem.registrar(
        "Matriz de sensibilidade do SAM bottom-up",
        "DERIVADO",
        "célula = round(ICP × taxa da linha) × ticket da coluna",
        [{"nome": "ICP", "valor": R.inteiro(bu["n_icp"]), "ref": m_icp},
         {"nome": "grade de taxas de atividade",
          "valor": ", ".join(R.pct(x, 0) for x in sens["taxas"])},
         {"nome": "grade de tickets",
          "valor": ", ".join("R$ " + _num(x) for x in sens["tickets"])}],
        "grade completa na tabela da seção 6",
        "ver matriz",
        explicacao=("Mostra como o mercado muda se as duas premissas mais incertas (taxa de atividade e ticket) variarem — o intervalo honesto da estimativa."),
    )

    ressalva_demo = (
        " <b>Atenção:</b> o lado bottom-up ainda usa dados de demonstração — a "
        "leitura de convergência/divergência só vale após a carga real do CNPJ."
        if cnpj_demo else ""
    )
    s.append(secao(
        "6. Triangulação e cenários (TAM/SAM/SOM)",
        f"<p>{tri['leitura']}{mem.ref(m_tri)}{ressalva_demo}</p>",
        *blocos_anc,
        R.grafico_funil([
            ("TAM", td["tam"], f"Brasil, top-down, {td['ano_base']}"),
            ("SAM", sam_central,
             (config.get("rotulo_sam_funil",
                        "bottom-up ME/EPP; top-down PAS como piso (ver diagnóstico acima)")
              if usa_bu_central else
              f"média das metodologias (divergência {R.pct(tri['divergencia'])})"
              + ("" if tri["convergente"] else " — usar com cautela; ver diagnóstico acima"))),
            ("SOM", som_base,
             f"cenário-base: {R.pct(cen['base']['taxa'])} de captura em {bu['horizonte_anos']} anos"),
        ]),
        R.tabela(
            ["Cenário", "Taxa de captura", "SOM anual"],
            [(n.capitalize(), R.pct(c["taxa"]),
              R.brl(c["som"]) + (mem.ref(m_som) if n == "base" else ""))
             for n, c in cen.items()],
        ),
        "<p>Sensibilidade do SAM bottom-up às duas premissas mais incertas "
        "(taxa de atividade efetiva × ticket médio) — o valor usado no relatório "
        f"está no centro da matriz:{mem.ref(m_sens)}</p>",
        R.tabela(
            ["Taxa de atividade \\ Ticket"] + [R.brl(t) for t in sens["tickets"]],
            [
                [R.pct(taxa, 0)] + [R.brl(v) for v in linha]
                for taxa, linha in zip(sens["taxas"], sens["matriz"])
            ],
        ),
    ))

    # 7. Dinâmica do mercado
    regimes_din = {d["regime"] for d in din}
    tem_dim = regimes_din - {"TOTAL"} != set()
    def _serie_anual(filtro):
        agg = {}
        for d in din:
            if filtro(d):
                ab, fe = agg.get(d["ano"], (0, 0))
                agg[d["ano"]] = (ab + d["aberturas"], fe + d["fechamentos"])
        return sorted((a, ab, fe) for a, (ab, fe) in agg.items())
    if tem_dim:
        serie_foco = _serie_anual(lambda d: d["regime"] != "MEI")
        serie_mei = _serie_anual(lambda d: d["regime"] == "MEI")
    else:
        serie_foco = _serie_anual(lambda d: True)
        serie_mei = []
    anos_d = [a for a, _, _ in serie_foco]
    blocos_din = []
    if tem_dim:
        saldo = sum(ab - fe for _, ab, fe in serie_foco)
        leitura_saldo = (
            f"saldo líquido de <b>{'+' if saldo >= 0 else '−'}{R.inteiro(abs(saldo))}</b> no "
            "período — a base formal está em "
            + ("expansão" if saldo >= 0 else "contração (parte relevante tende a ser limpeza "
               "cadastral de empresas dormentes pela Receita"
               + (", coerente com a baixa adesão ao Simples observada na seção 5"
                  if config["icp"].get("taxa_atividade", 1.0) < 0.4 else "") + ")")
        )
        blocos_din.append(
            f"<p>Recorte relevante ao ICP (empresas <b>não-MEI</b>): entre {anos_d[0]} e "
            f"{anos_d[-1]}, foram {R.inteiro(sum(ab for _, ab, _ in serie_foco))} aberturas e "
            f"{R.inteiro(sum(fe for _, _, fe in serie_foco))} fechamentos/inaptidões — "
            f"{leitura_saldo}. O fluxo de MEIs "
            f"({R.inteiro(sum(ab for _, ab, _ in serie_mei))} aberturas no período) domina o "
            "setor, mas está fora do perfil de cliente-alvo e aparece apenas na tabela "
            "detalhada.</p>"
        )
    else:
        blocos_din.append(
            f"<p>Entre {anos_d[0]} e {anos_d[-1]}, o CNAE registrou "
            f"{R.inteiro(sum(ab for _, ab, _ in serie_foco))} aberturas na região, com saldo "
            "líquido positivo. Atenção: a maior parte dessas aberturas é de MEIs, que estão "
            "fora do ICP — a série separada por regime e porte (consulta B3) refina esta "
            "leitura.</p>"
        )
    blocos_din.append(R.grafico_barras_pares(
        anos_d, [ab for _, ab, _ in serie_foco], [fe for _, _, fe in serie_foco],
        ["Aberturas" + (" (não-MEI)" if tem_dim else ""),
         "Fechamentos" + (" (não-MEI)" if tem_dim else "")],
    ))
    if tem_dim:
        blocos_din.append(R.tabela(
            ["Ano", "Regime", "Porte", "Aberturas", "Fechamentos"],
            [(d["ano"], d["regime"], d["porte"], R.inteiro(d["aberturas"]),
              R.inteiro(d["fechamentos"])) for d in din],
        ))
    fes = [fe for _, _, fe in serie_foco]
    if len(fes) >= 3 and fes[-1] < 0.7 * (sum(fes[:-1]) / len(fes[:-1])):
        blocos_din.append(
            f"<p>Nota: os fechamentos de {anos_d[-1]} estão bem abaixo da média dos anos "
            "anteriores — provável atraso de registro de baixas no cadastro (o número tende a "
            "ser revisado para cima), e não melhora real do setor.</p>"
        )
    revisao = cnpj.fator_revisao(config.get("cnpj_prefixo", "cnpj"))
    if revisao:
        blocos_din.append(
            f"<p><b>Lag de baixas medido:</b> entre as extrações {revisao['de']} e "
            f"{revisao['para']}, os fechamentos de {revisao['ano']} foram revisados em "
            f"{revisao['fator'] - 1:+.1%} — fator aplicável como correção de leitura do "
            "último ano da série.</p>"
        )
    else:
        estado_vintage = (
            "o arquivamento de extrações (vintages) começa na primeira carga real"
            if cnpj_demo else
            f'a extração {config.get("cnpj_extracao", "atual").split(" ")[0]} está '
            "arquivada como base (dados/vintages/)"
        )
        blocos_din.append(
            f'<p class="premissas">Monitoramento do lag de baixas: {estado_vintage}; '
            "o fator de revisão dos fechamentos passa a ser medido a cada "
            "nova extração mensal. Referência externa de fluxo: Mapa de Empresas — boletim "
            "quadrimestral oficial de aberturas, baixas e tempo de baixa (Ministério do "
            "Empreendedorismo; não cobre MEI) · "
            "https://www.gov.br/empresas-e-negocios/pt-br/mapa-de-empresas</p>"
        )
    if config["regiao"].get("municipios"):
        blocos_din.append(
            '<p class="premissas">Nota de recorte: a consulta B3 (dinâmica) é '
            "agregada por área no BigQuery e não guarda a cidade — confirme que "
            "a lista de cidades da última execução confere com o recorte atual "
            "do estudo (consultas em dados/sql/).</p>"
        )
    blocos_din.append(R.selo_fonte(prov_cnpj))
    s.append(secao("7. Dinâmica do mercado-alvo", *blocos_din))

    # 7b. Dimensionamento por atividade (estudos multi-CNAE com mix de receita)
    if config.get("atividades"):
        sam_medio = sam_central
        # mix medido: com a demanda por linha, a participação de cada
        # atividade no SAM deixa de ser premissa e vira o mix MEDIDO
        mix_medido = None
        mercado_cnae = {}
        if demanda_linhas and demanda_linhas["total"]:
            for l in demanda_linhas["linhas"]:
                if l["mercado"]:
                    mercado_cnae[l["cnae"]] = (mercado_cnae.get(l["cnae"], 0)
                                               + l["mercado"])
            mix_medido = {cn: v / demanda_linhas["total"]
                          for cn, v in mercado_cnae.items()}
            for atv in config["atividades"]:
                if atv["cnae"] in mix_medido:
                    atv["participacao_sam"] = mix_medido[atv["cnae"]]
        expansao = None
        if config["icp"].get("peso_receita_secundaria") and conc_atividades:
            expansao = {
                "taxa_atividade": config["icp"].get("taxa_atividade", 1.0),
                "ticket": config["icp"]["ticket_medio_anual_brl"],
                "peso_secundaria": config["icp"]["peso_receita_secundaria"],
            }
        linhas_atv = sizing.por_atividade(sam_medio, som_base, config["atividades"],
                                          conc_atividades, expansao)
        entradas_atv = []
        for l in linhas_atv:
            v_atv = "{} × {} = {}".format(
                _num(sam_medio), R.pct(l["participacao_sam"], 0),
                R.brl(l["sam_atividade"]))
            if l["sam_expandido"]:
                v_atv += " ↔ expandido {}".format(R.brl(l["sam_expandido"]))
            entradas_atv.append({"nome": l["cnae"] + " — " + l["descricao"],
                                 "valor": v_atv, "ref": m_sam_central})
        if expansao:
            entradas_atv.append({
                "nome": "expansão por CNAE secundário (por atividade)",
                "valor": "+ empresas só-secundárias × {} × {} × {}".format(
                    R.pct(expansao["taxa_atividade"], 1),
                    "R$ " + _num(expansao["ticket"]),
                    R.pct(expansao["peso_secundaria"], 0)),
                "fonte": "contagens da consulta E (principal / só-secundária)"})
        m_atv = mem.registrar(
            "SAM por atividade e share implícito",
            "PREMISSA DECLARADA",
            "SAM da atividade = SAM central × participação da atividade; "
            "expandido = + (empresas só-secundárias × taxa de atividade × "
            "ticket × peso secundário); share implícito = receita-alvo ÷ SAM "
            "da atividade",
            entradas_atv,
            "por atividade (acima)",
            "ver tabela da seção 7b",
            racional=config.get("racional_atividades",
                                "pesos declarados no arquivo do setor"),
            sql_ref="CONSULTA E" if conc_atividades else None,
            explicacao=("Divide o mercado pelas linhas de negócio e testa se a meta da empresa é realista em cada uma."),
        )
        corpo_atv = [(
            "<p>Cada atividade é dimensionada como um mercado próprio; a receita-alvo é "
            "distribuída pelo mix do plano do cliente e o <b>share implícito</b> por "
            "atividade testa o realismo do plano (metodologia em docs/metodologia-v3.md). "
            "Concorrentes por atividade contam CNAE principal e secundário, sem dupla "
            "contagem."
            + (" O SAM é publicado como <b>faixa</b>: conservador (só CNAE principal) ↔ "
               "expandido (somando as empresas com o CNAE apenas como atividade "
               "secundária, ponderadas pelo mix de receita)." if expansao else "")
            + "</p>"
        )]
        if demanda_linhas:
            linhas_dl_tab = []
            for l in demanda_linhas["linhas"]:
                if l["mercado"] is None:
                    linhas_dl_tab.append((
                        l["nome"], _num(l["base_qtd"]), "—", "—", "—",
                        "não dimensionada (a levantar)", "—"))
                elif l["qtd_ano"] is not None:
                    linhas_dl_tab.append((
                        l["nome"], _num(l["base_qtd"]),
                        _dec(l["frequencia_ano"], 1) + "×/ano",
                        _num(l["qtd_ano"]) + " " + l.get("unidade", "un."),
                        "R$ " + _num(l["preco_medio_brl"]),
                        R.brl(l["mercado"]), R.pct(l["mix"], 1)))
                else:
                    linhas_dl_tab.append((
                        l["nome"], _num(l["base_qtd"]), "gasto/veíc.", "—",
                        "R$ " + _dec(l["valor_anual_por_veiculo"], 2) + "/ano",
                        R.brl(l["mercado"]), R.pct(l["mix"], 1)))
            linhas_dl_tab.append((
                "TOTAL (linhas dimensionadas)", "", "", "", "",
                "<b>" + R.brl(demanda_linhas["total"]) + "</b>", "100%"))
            corpo_atv.append(
                "<p><b>Mercado por linha de negócio (lado da demanda):</b> "
                "para cada linha, base atendível ponderada × frequência anual "
                "de uso × preço médio. Frequências e preços são premissas "
                "declaradas, cada uma com sua fonte — método incorporado do "
                "plano de negócio da empresa e formalizado com a frota "
                f"oficial.{mem.ref(m_dl)}</p>"
            )
            corpo_atv.append(R.tabela(
                ["Linha de negócio", "Base atendível (ponderada)",
                 "Frequência", "Volume/ano", "Preço médio [premissa]",
                 "Mercado/ano", "% do mix"],
                linhas_dl_tab,
            ))
        tem_exp = expansao and any(l["sam_expandido"] for l in linhas_atv)
        cab = ["Atividade", "Mix de receita",
               ("SAM (conservador ↔ expandido)" if tem_exp else "SAM da atividade"),
               "Receita-alvo (SOM)",
               ("Share implícito (cons. ↔ exp.)" if tem_exp else "Share implícito"),
               "Concorrentes (principal / +secundária)"]
        linhas_tab = []
        for l in linhas_atv:
            conc_txt = (
                f"{R.inteiro(l['concorrentes_principal'])} / +{R.inteiro(l['concorrentes_secundaria'])}"
                if l["concorrentes_principal"] is not None else "aguardando consulta E"
            )
            sam_txt = R.brl(l["sam_atividade"])
            share_txt = R.pct(l["share_implicito"], 2)
            if l["sam_expandido"]:
                sam_txt += f" ↔ {R.brl(l['sam_expandido'])}"
                share_txt += f" ↔ {R.pct(l['share_expandido'], 2)}"
            linhas_tab.append((
                f"{l['cnae']} — {l['descricao']}", R.pct(l["peso_receita"], 0),
                sam_txt, R.brl(l["receita_alvo"]), share_txt, conc_txt,
            ))
        corpo_atv.append(R.tabela(cab, linhas_tab))
        if config.get("nota_emprego_formal"):
            corpo_atv.append(
                f"<p><b>Dinâmica por atividade no emprego formal:</b> "
                f"{config['nota_emprego_formal']}.</p>"
            )
        # testes de realismo (método incorporado do plano da analista, com
        # dados oficiais): mercado médio por concorrente e receita/funcionário
        if mercado_cnae and funil_mun and icp_enderecavel is not None:
            icp_end_cnae = {}
            for mun2, f2 in funil_mun.items():
                fb2 = fatores_mun.get(mun2, {"base": 1.0})["base"]
                for cn2, pc2 in f2["por_cnae"].items():
                    icp_end_cnae[cn2] = (icp_end_cnae.get(cn2, 0)
                                         + pc2["icp"] * fb2)
            linhas_mm = []
            entradas_mm = []
            for cn2 in sorted(mercado_cnae, key=lambda c: -mercado_cnae[c]):
                icp_c = icp_end_cnae.get(cn2, 0)
                mm = mercado_cnae[cn2] / icp_c if icp_c else None
                mm_txt = (R.brl(mm) if mm
                          else "sem concorrente formal no ICP local")
                linhas_mm.append((cn2, R.brl(mercado_cnae[cn2]),
                                  _dec(icp_c, 1), mm_txt))
                entradas_mm.append({
                    "nome": cn2,
                    "valor": "{} ÷ {} = {}".format(
                        _num(mercado_cnae[cn2]), _dec(icp_c, 1), mm_txt),
                    "ref": m_dl})
            m_mm = mem.registrar(
                "Mercado médio por concorrente da linha (teste de realismo)",
                "DERIVADO",
                "mercado medido da linha ÷ concorrentes formais endereçáveis "
                "da linha",
                entradas_mm,
                "por linha (acima)",
                "comparar com o ticket premissado de "
                + R.brl(config["icp"]["ticket_medio_anual_brl"]),
                explicacao=("Se o mercado de cada linha fosse dividido em "
                            "partes iguais entre os concorrentes formais que "
                            "o disputam, quanto caberia a cada um. Onde esse "
                            "valor é muito maior que o ticket premissado, há "
                            "mais dinheiro por empresa (espaço, informalidade "
                            "ou vazamento para fora da área)."),
            )
            corpo_atv.append(
                "<p><b>Teste de realismo — mercado médio por concorrente:</b> "
                "o mercado medido de cada linha dividido pelos concorrentes "
                "formais endereçáveis da própria linha, para comparar com o "
                f"ticket premissado.{mem.ref(m_mm)}</p>"
            )
            corpo_atv.append(R.tabela(
                ["Atividade (CNAE)", "Mercado medido (demanda)",
                 "Concorrentes endereçáveis (ICP)",
                 "Mercado médio por concorrente"],
                linhas_mm,
            ))
        ei = config.get("empresa_info")
        if ei and ei.get("funcionarios_previstos"):
            fat_func = som_base / ei["funcionarios_previstos"] / 12
            m_ff = mem.registrar(
                "Faturamento por funcionário (teste de realismo da meta)",
                "DERIVADO",
                "faturamento/funcionário/mês = SOM do cenário-base ÷ "
                "funcionários previstos ÷ 12 meses",
                [{"nome": "SOM cenário-base", "valor": R.brl(som_base),
                  "ref": m_som},
                 {"nome": "funcionários previstos",
                  "valor": str(ei["funcionarios_previstos"]),
                  "fonte": ei.get("fonte", "plano de negócio (declarado)")}],
                "{} ÷ {} ÷ 12".format(_num(som_base),
                                      ei["funcionarios_previstos"]),
                "R$ " + _num(fat_func) + "/funcionário/mês",
                racional=ei.get("faixa_setorial_texto", ""),
                explicacao=("Divide a meta de receita pela equipe prevista. "
                            "Se o valor cair muito fora da faixa típica do "
                            "setor, ou a meta ou o quadro de pessoal está "
                            "desajustado."),
            )
            corpo_atv.append(
                f"<p><b>Teste de realismo — pessoal:</b> a meta do cenário-base "
                f"({R.brl(som_base)}/ano) dividida pelos "
                f"{ei['funcionarios_previstos']} funcionários previstos dá "
                f"<b>R$ {_num(fat_func)}/funcionário/mês</b>. "
                f"{ei.get('faixa_setorial_texto', '')}.{mem.ref(m_ff)}</p>"
            )
        corpo_atv.append(
            '<p class="premissas">'
            + ("Participação por atividade = MIX MEDIDO pela âncora de demanda "
               "por linha (tabela acima)" + mem.ref(m_dl) + "; "
               if mix_medido else
               "Premissa participacao_sam por atividade declarada no arquivo "
               "do setor; ")
            + 'share implícito = receita-alvo da atividade ÷ SAM da atividade.'
            + (f' Expansão por CNAE secundário: {config["icp"].get("racional_secundaria", "")}'
               if expansao else '')
            + mem.ref(m_atv) + '</p>'
        )
        s.append(secao("7b. Dimensionamento por atividade e projeção de receita", *corpo_atv))

    # 7c. Mercado informal (labor input method) — quando a consulta F existir
    if informal:
        fator = config.get("informalidade_fator_produtividade", 0.5)
        piso = informal["receita_informal_piso"]
        teto = piso / fator
        total_trab = informal["n_informal"] + informal["n_formal"]
        m_inf = mem.registrar(
            "Mercado informal (labor input method)",
            "DADO × PREMISSA",
            "piso = soma dos rendimentos anuais declarados dos informais; "
            "teto = piso ÷ fator de produtividade",
            [{"nome": "trabalhadores informais",
              "valor": R.inteiro(informal["n_informal"]),
              "fonte": informal["proveniencia"].get("fonte"),
              "url": informal["proveniencia"].get("url")},
             {"nome": "piso (rendimentos declarados × 12)",
              "valor": "R$ " + _num(piso)},
             {"nome": "fator de produtividade",
              "valor": R.pct(fator, 0) + " [premissa]"}],
            "teto = {} ÷ {}".format(_num(piso), R.pct(fator, 0)),
            "{} (piso) a {} (teto)".format(R.brl(piso), R.brl(teto)),
            provs=[informal["proveniencia"]],
            sql_ref="CONSULTA F (PNAD)",
            explicacao=("O tamanho do mercado invisível: quem trabalha no setor sem CNPJ. É dinheiro que circula, mas não aparece em nenhuma base formal."),
        )
        s.append(secao(
            "7c. Mercado informal (labor input method)",
            f"<p>Pela PNAD Contínua ({informal['referencia']}), o setor tem "
            f"<b>{R.inteiro(informal['n_informal'])}</b> trabalhadores informais (sem CNPJ/"
            f"carteira) e {R.inteiro(informal['n_formal'])} formais na região — "
            f"{R.pct(informal['n_informal']/total_trab)} de informalidade ocupacional. "
            f"Receita anual estimada do mercado informal: entre <b>{R.brl(piso)}</b> "
            f"(piso: soma dos rendimentos declarados) e <b>{R.brl(teto)}</b> (teto: piso ÷ "
            f"fator de produtividade {R.pct(fator, 0)} [premissa declarada]). Este valor é "
            f"ADICIONAL ao mercado formal dimensionado nas seções 4–6.{mem.ref(m_inf)}</p>",
            R.grafico_barras_h(
                [("Informais", informal["n_informal"]), ("Formais", informal["n_formal"])],
                "trabalhadores", esq=110,
            ),
            R.selo_fonte(informal["proveniencia"]),
        ))

    # 8. Limitações e fontes — a lista reflete o que já foi fechado com dado
    # (plano e benchmark de mercado: docs/plano-fechamento-lacunas.md)
    itens_lim = [
        "CNPJ ativo não significa empresa operante; a adesão ao Simples é usada como proxy "
        "MEDIDO de operação, mas o score multi-sinal (snapshots, presença viva, IE) da "
        "Onda 2 do plano de lacunas ainda não está ativo.",
        "A informalidade do setor não é capturada pela base CNPJ"
        + (" (dimensionada na seção 7c via PNAD Contínua)." if informal
           else " — mensurável via PNAD Contínua (consulta F)."),
    ]
    if regiao_dado:
        itens_lim.append(
            "As participações do top-down deixaram de ser premissas: segmento é DADO "
            "(PAS 2611) e região é triangulação de pesos públicos (seção 4) — a revisão "
            "com o cliente segue recomendada para recortes fora do padrão."
        )
    else:
        itens_lim.append(
            "As participações de segmento e região do top-down são premissas curadas por "
            "setor e devem ser revisadas com o cliente."
        )
    itens_lim.append(
        "Este protótipo não inclui share de varejo (Nielsen/Kantar) nem pesquisa primária "
        "— o caminho mapeado é alt-data (ICVA/Índice Stone) e survey embutido "
        "(plano de lacunas, Onda 3)."
    )
    if config["icp"].get("peso_receita_secundaria") and conc_atividades:
        itens_lim.append(
            "Empresas com o CNAE apenas como atividade secundária: publicadas como FAIXA "
            "na seção 7b (conservador ↔ expandido, ponderação pelo mix de receita "
            "[premissa declarada])."
        )
    else:
        itens_lim.append(
            "Empresas com o CNAE do setor apenas como atividade secundária não entram na "
            "contagem principal (faixa conservadora; ver nota na seção 5)."
        )
    itens_lim.append(
        "Fechamentos do último ano tendem a ser revisados para cima (atraso de registro "
        "de baixas)"
        + ("; o fator de revisão já é medido entre extrações arquivadas (seção 7)."
           if revisao else
           "; a medição do fator de revisão entre extrações mensais foi iniciada "
           "(dados/vintages/, seção 7).")
    )
    if config.get("cnpj_idade_matriz"):
        itens_lim.append(
            "Idade da empresa medida pelo estabelecimento matriz (consulta A4) — a faixa "
            "etária reflete a empresa, não cada filial."
        )
    else:
        itens_lim.append(
            "A faixa de idade é do estabelecimento; empresas com matriz e filiais de idades "
            "distintas podem aparecer em mais de uma faixa (efeito marginal — a consulta A4 "
            "corrige pela idade da matriz)."
        )
    itens_lim.append(
        "Lucro Presumido e Lucro Real não são distinguíveis em dados públicos (sigilo "
        "fiscal) — aparecem agrupados como Fora do Simples; abrir essa dimensão exige "
        "enriquecimento pago por CNPJ (inferência via NF-e/Sintegra de vendors), mapeado "
        "como add-on."
    )
    s.append(secao(
        "8. Limitações declaradas",
        "<ul>" + "".join(f"<li>{i}</li>" for i in itens_lim) + "</ul>",
    ))

    # Anexo — glossário: os termos do estudo em linguagem simples, para um
    # analista júnior ler o relatório inteiro sem tradutor
    glossario = [
        ("TAM", "o mercado inteiro do setor no Brasil, em R$/ano (Total "
         "Addressable Market)."),
        ("SAM", "a fatia do TAM que está na região e no segmento da empresa — "
         "o mercado que dá para disputar (Serviceable Addressable Market)."),
        ("SOM", "a fatia do SAM que a empresa consegue capturar no horizonte "
         "do plano — a meta de receita (Serviceable Obtainable Market)."),
        ("Top-down", "cálculo de cima para baixo: começa na receita nacional "
         "oficial e recorta por segmento e região."),
        ("Bottom-up", "cálculo de baixo para cima: conta os concorrentes um a "
         "um e multiplica pelo faturamento típico de cada um."),
        ("ICP", "o perfil de empresa contado no estudo (porte, tempo de vida, "
         "atividade) — Ideal Customer/Competitor Profile."),
        ("CNAE", "código oficial da atividade econômica de cada CNPJ (ex.: "
         "4530-7/05 = comércio varejista de pneus)."),
        ("MEI / ME / EPP", "portes de empresa: Microempreendedor Individual "
         "(fatura até R$ 81 mil/ano), Microempresa (até R$ 360 mil) e Empresa "
         "de Pequeno Porte (até R$ 4,8 mi)."),
        ("Simples Nacional", "regime simplificado de impostos; aderir a ele é "
         "o sinal usado no estudo de que a empresa opera de verdade."),
        ("Taxa de atividade", "de cada 100 CNPJs cadastrados com o perfil, "
         "quantos mostram sinal de operação real — cadastro ativo não "
         "significa negócio funcionando."),
        ("Ticket médio", "faturamento anual típico de um concorrente do "
         "perfil-alvo."),
        ("Fator de acesso", "fração do mercado de uma cidade que a loja "
         "consegue disputar: 100% na cidade-sede, menos nas vizinhas."),
        ("Frota atendível", "só os tipos de veículo que a empresa atende "
         "(decisão declarada do cliente)."),
        ("CAGR", "crescimento médio composto ao ano de uma série histórica."),
        ("Share implícito", "a fatia do mercado que a meta de receita "
         "representa — o teste de realismo do plano."),
        ("Selo cinza / laranja", "cinza = dado obtido ao vivo da fonte "
         "oficial no momento da geração; laranja = dado de demonstração, com "
         "o motivo declarado."),
    ]
    s.append('<section id="glossario"><h2>Anexo — Glossário: os termos do '
             "estudo em linguagem simples</h2>"
             + tabela_aberta(["Termo", "O que significa"], glossario)
             + "</section>")

    # Anexo — memória de cálculo: verbetes registrados ao longo do pipeline +
    # SQLs de reprodução das consultas BigQuery declarados no config do setor
    sql_blocos = []
    for caminho in config.get("sql_arquivos", []):
        arq_sql = RAIZ / caminho
        if arq_sql.exists():
            sql_blocos.append((arq_sql.name, caminho,
                               arq_sql.read_text(encoding="utf-8")))
    anexo = mem.render_anexo(sql_blocos)
    if anexo:
        s.append(anexo)

    meta = {
        "titulo": config["titulo"],
        "contexto": config["contexto"],
        "cnaes": ", ".join(f'{c["codigo"]} ({c["descricao"]})' for c in config["cnaes"]),
        "regiao": config["regiao"]["nome"],
        "gerado_em": time.strftime("%d/%m/%Y %H:%M UTC", time.gmtime()),
    }
    provs = [prov_ibge, prov_cnpj] + [prov for _, prov in series_macro]
    if cempre:
        provs.append(cempre[2])
    for p in regiao_pesos:
        if p["prov"]:
            provs.append(p["prov"])
    tem_demo = any(p["origem"] == "fixture" for p in provs)
    return R.montar(s, meta, tem_demo=tem_demo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setor", default="setores/estetica_sp.json")
    ap.add_argument("--modo", default="auto", choices=["auto", "live", "fixture"])
    ap.add_argument("--saida", default=None)
    args = ap.parse_args()

    config = json.loads((RAIZ / args.setor).read_text())
    html = gerar(config, args.modo)

    destino = Path(args.saida) if args.saida else RAIZ / "saida" / f"relatorio-{config['id']}.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    print(f"Relatório gerado: {destino}")


if __name__ == "__main__":
    main()
