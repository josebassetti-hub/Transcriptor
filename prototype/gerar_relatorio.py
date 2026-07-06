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
from fontes import ibge, bcb, cnpj, pnad
from calculos import sizing
from relatorio import render as R

RAIZ = Path(__file__).resolve().parent


def secao(titulo, *blocos):
    return f"<section><h2>{titulo}</h2>" + "".join(blocos) + "</section>"


def gerar(config: dict, modo: str) -> str:
    cliente = ClienteHTTP(modo)

    # ---- collect -------------------------------------------------------------
    receita, prov_ibge = ibge.receita_setorial(cliente, config["topdown"])
    prov_segmento = None
    if config["topdown"].get("segmento_dado"):
        # a fração do segmento vem da PAS 2611 (dado), substituindo a premissa
        fracao, ano_frac, prov_segmento = ibge.fracao_segmento(
            cliente, config["topdown"]["segmento_dado"])
        config["topdown"]["participacao_segmento"] = fracao
        config["topdown"]["racional_segmento"] = (
            f"DADO (PAS Tab. 2611, {ano_frac}): receita de cabeleireiros/tratamento de beleza "
            f"÷ receita de serviços pessoais = {fracao:.1%}"
        )
    series_macro = [
        bcb.serie_sgs(cliente, s["codigo"], s["nome"], s["ultimos"])
        for s in config["series_bcb"]
    ]
    # os CSVs de CNPJ passam a contar como dado real quando o usuário os
    # substitui pelos agregados da Base dos Dados e marca cnpj_origem: "real"
    cnpj_demo = config.get("cnpj_origem", "demo") != "real"
    linhas_cnpj, prov_cnpj = cnpj.agregados(config, demo=cnpj_demo)
    contagem = cnpj.contar_icp(linhas_cnpj, config["icp"])
    din, _ = cnpj.dinamica(config, demo=cnpj_demo)
    cempre = None
    if config.get("bottomup_validacao"):
        cempre = ibge.contagem_empresas(cliente, config["bottomup_validacao"])
    # região: de premissa única para triangulação de pesos públicos (mediana)
    regiao_pesos = []
    rm = config["topdown"].get("regiao_medida")
    if rm:
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

    # ---- compute -------------------------------------------------------------
    td = sizing.top_down(receita, config["topdown"])
    bu = sizing.bottom_up(contagem["n_icp"], config["icp"], config["captura"])
    tri = sizing.triangulacao(td["sam"], bu["sam"])
    sens = sizing.sensibilidade(bu["n_icp"])
    som_base = bu["cenarios"]["base"]["som"]
    usa_bu_central = config.get("sam_central") == "bottom_up"
    sam_central = bu["sam"] if usa_bu_central else (td["sam"] + bu["sam"]) / 2
    rotulo_sam = ("SAM " + config["regiao"]["sigla"]
                  + (" (bottom-up; PAS = piso)" if usa_bu_central else " (triangulado)"))

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
    ))

    # 2. Metodologia
    s.append(secao(
        "2. Escopo e metodologia",
        "<p>Dupla metodologia com triangulação, no padrão descrito na pesquisa de mercado: "
        "<b>top-down</b> (receita setorial oficial → participação do segmento → participação da "
        "região) e <b>bottom-up</b> (nº de empresas-alvo do censo CNPJ × ticket médio anual × "
        "taxa de captura por cenário). Toda fonte é citada no selo da respectiva seção; a "
        "extração da base CNPJ usada é a de <b>" + config["cnpj_extracao"] + "</b>.</p>",
        '<p class="premissas">ICP: ' + config["icp"]["descricao"] + "</p>",
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

    # 4-6. Tamanho de mercado
    anos = sorted(receita)
    regiao_dado = len(regiao_pesos) >= 2
    blocos_td = [
        f"<p>A receita nacional do setor somou <b>{R.brl(td['tam'])}</b> em {td['ano_base']}"
        + (f", com CAGR de <b>{R.pct(td['cagr'])}</b> desde {anos[0]}" if td["cagr"] else "")
        + f". Aplicando a participação do segmento ({R.pct(td['premissas']['participacao_segmento'],0)}) "
        f"e da região ({R.pct(td['premissas']['participacao_regiao'],0)}), o SAM top-down de "
        f"{config['regiao']['nome']} é <b>{R.brl(td['sam'])}</b>.</p>",
        R.tabela(["Ano", "Receita (R$)"], [(a, R.brl(receita[a])) for a in anos]),
        f'<p class="premissas">{"Segmento (DADO oficial)" if prov_segmento else "Premissas: segmento"} — '
        f'{td["premissas"]["racional_segmento"]}; '
        f'região ({"DADO triangulado" if regiao_dado else "premissa"}) — '
        f'{td["premissas"]["racional_regiao"]}.</p>',
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
    blocos_bu = [
        f"<p>O universo do CNAE na região tem <b>{R.inteiro(contagem['universo_empresas'])}</b> "
        f"empresas ativas ({R.inteiro(contagem['universo_estabelecimentos'])} estabelecimentos, "
        f"contando filiais); o recorte de ICP resulta em <b>{R.inteiro(bu['n_icp'])}</b> "
        f"empresas cadastradas. Aplicando a premissa de atividade efetiva de "
        f"{R.pct(bu['taxa_atividade'], 0)}, chega-se a <b>{R.inteiro(bu['n_operantes'])}</b> "
        f"empresas-alvo operantes. Com ticket médio anual de {R.brl(bu['ticket'])}, o SAM "
        f"bottom-up é <b>{R.brl(bu['sam'])}</b>.</p>",
        nota_secundaria,
        R.grafico_barras_h(
            sorted(contagem["por_porte"].items(), key=lambda kv: -kv[1]),
            "empresas ativas",
        ),
        f'<p class="premissas">Premissas: {bu["premissas"]["icp"]}. '
        f'Ticket: {bu["premissas"]["racional_ticket"]}. '
        f'Atividade efetiva: {bu["premissas"]["racional_atividade"]}</p>',
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
        blocos_bu.append(
            f"<p><b>Validação cruzada (fonte oficial independente):</b> o CEMPRE do IBGE "
            f"registra <b>{R.inteiro(qtd_c)}</b> empresas da classe 96.02-5 em "
            f"{config['regiao']['nome']} ({ano_c}). A contagem do CEMPRE segue metodologia "
            "própria (empresas, não estabelecimentos, e cobertura parcial de MEIs), servindo "
            "como referência de ordem de grandeza para o recorte formal (ME/EPP) usado no "
            "bottom-up.</p>"
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
        from fontes.pnad import ARQ as _ARQ
        for l in _csv.DictReader(open(_ARQ, encoding="utf-8")):
            if l["uf"] == config["regiao"]["sigla"] and l["categoria"] == "FORMAL":
                rend_formal = float(l["rendimento_medio_mensal"])
        if rend_formal:
            mercado_labor = informal["n_formal"] * rend_formal * 12 / labor_share
            blocos_anc.append(
                "<p><b>Diagnóstico por três âncoras independentes</b> (setores intensivos em "
                "MEI, como beleza, são subcapturados pelo universo da PAS — a âncora "
                "trabalhista dimensiona o mercado formal TOTAL):</p>"
            )
            blocos_anc.append(R.tabela(
                ["Âncora", "O que mede", "Valor (SP/ano)"],
                [
                    ("Top-down PAS", "receita formal do universo de pesquisa do IBGE "
                     "(≈ empresas do CEMPRE) — PISO do segmento corporativo", R.brl(td["sam"])),
                    ("Bottom-up CNPJ", "empresas ME/EPP operantes × ticket "
                     "(exclui MEI)", R.brl(bu["sam"])),
                    ("Labor-input (PNAD)", f"{R.inteiro(informal['n_formal'])} trabalhadores "
                     f"formais × rendimento × 12 ÷ participação do trabalho "
                     f"({R.pct(labor_share, 0)} [premissa]) — mercado formal TOTAL, "
                     "inclusive MEI", R.brl(mercado_labor)),
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
        blocos_anc.append(
            f"<p><b>Âncora de demanda (POF):</b> despesa média mensal familiar com o setor de "
            f"{R.brl(demanda['despesa_mensal_familia'])} (POF {demanda['ano_pof']}) × "
            f"{R.inteiro(n_dom)} domicílios (Censo {ano_dom}) × 12, corrigida pelo IPCA "
            f"acumulado desde jan/{ano_pof4} "
            f"(fator {fator_ipca:.2f}, {len(ipca_pontos)} meses) "
            f"= <b>{R.brl(mercado_demanda)}</b>/ano. O lado da demanda enxerga o mercado "
            "inteiro (formal + informal), mas a POF tende a subdeclarar despesas pessoais — "
            "ler como piso da demanda. "
            f"Nota regional: {cfg_d['nota_regional']}.</p>"
        )
        for prov_d in demanda["provs"]:
            blocos_anc.append(R.selo_fonte(prov_d))
        blocos_anc.append(R.selo_fonte(prov_dom))
        blocos_anc.append(R.selo_fonte(prov_ipca))
    s.append(secao(
        "6. Triangulação e cenários (TAM/SAM/SOM)",
        f"<p>{tri['leitura']}</p>",
        *blocos_anc,
        R.grafico_funil([
            ("TAM", td["tam"], f"Brasil, top-down, {td['ano_base']}"),
            ("SAM", sam_central,
             ("bottom-up ME/EPP; top-down PAS como piso (ver diagnóstico acima)"
              if usa_bu_central else
              f"média das metodologias (divergência {R.pct(tri['divergencia'])})"
              + ("" if tri["convergente"] else " — usar com cautela; ver diagnóstico acima"))),
            ("SOM", som_base,
             f"cenário-base: {R.pct(cen['base']['taxa'])} de captura em {bu['horizonte_anos']} anos"),
        ]),
        R.tabela(
            ["Cenário", "Taxa de captura", "SOM anual"],
            [(n.capitalize(), R.pct(c["taxa"]), R.brl(c["som"])) for n, c in cen.items()],
        ),
        "<p>Sensibilidade do SAM bottom-up às duas premissas mais incertas "
        "(taxa de atividade efetiva × ticket médio) — o valor usado no relatório "
        "está no centro da matriz:</p>",
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
               "cadastral de empresas dormentes pela Receita, coerente com a baixa adesão ao "
               "Simples observada na seção 5)")
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
    revisao = cnpj.fator_revisao()
    if revisao:
        blocos_din.append(
            f"<p><b>Lag de baixas medido:</b> entre as extrações {revisao['de']} e "
            f"{revisao['para']}, os fechamentos de {revisao['ano']} foram revisados em "
            f"{revisao['fator'] - 1:+.1%} — fator aplicável como correção de leitura do "
            "último ano da série.</p>"
        )
    else:
        blocos_din.append(
            '<p class="premissas">Monitoramento do lag de baixas: a extração '
            f'{config.get("cnpj_extracao", "atual")[:7]} está arquivada como base '
            "(dados/vintages/); o fator de revisão dos fechamentos passa a ser medido a cada "
            "nova extração mensal. Referência externa de fluxo: Mapa de Empresas — boletim "
            "quadrimestral oficial de aberturas, baixas e tempo de baixa (Ministério do "
            "Empreendedorismo; não cobre MEI) · "
            "https://www.gov.br/empresas-e-negocios/pt-br/mapa-de-empresas</p>"
        )
    blocos_din.append(R.selo_fonte(prov_cnpj))
    s.append(secao("7. Dinâmica do mercado-alvo", *blocos_din))

    # 7b. Dimensionamento por atividade (estudos multi-CNAE com mix de receita)
    if config.get("atividades"):
        sam_medio = sam_central
        expansao = None
        if config["icp"].get("peso_receita_secundaria") and conc_atividades:
            expansao = {
                "taxa_atividade": config["icp"].get("taxa_atividade", 1.0),
                "ticket": config["icp"]["ticket_medio_anual_brl"],
                "peso_secundaria": config["icp"]["peso_receita_secundaria"],
            }
        linhas_atv = sizing.por_atividade(sam_medio, som_base, config["atividades"],
                                          conc_atividades, expansao)
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
        corpo_atv.append(
            '<p class="premissas">Premissa participacao_sam por atividade declarada no '
            'arquivo do setor; share implícito = receita-alvo da atividade ÷ SAM da '
            'atividade.'
            + (f' Expansão por CNAE secundário: {config["icp"].get("racional_secundaria", "")}'
               if expansao else '')
            + '</p>'
        )
        s.append(secao("7b. Dimensionamento por atividade e projeção de receita", *corpo_atv))

    # 7c. Mercado informal (labor input method) — quando a consulta F existir
    if informal:
        fator = config.get("informalidade_fator_produtividade", 0.5)
        piso = informal["receita_informal_piso"]
        teto = piso / fator
        total_trab = informal["n_informal"] + informal["n_formal"]
        s.append(secao(
            "7c. Mercado informal (labor input method)",
            f"<p>Pela PNAD Contínua ({informal['referencia']}), o setor tem "
            f"<b>{R.inteiro(informal['n_informal'])}</b> trabalhadores informais (sem CNPJ/"
            f"carteira) e {R.inteiro(informal['n_formal'])} formais na região — "
            f"{R.pct(informal['n_informal']/total_trab)} de informalidade ocupacional. "
            f"Receita anual estimada do mercado informal: entre <b>{R.brl(piso)}</b> "
            f"(piso: soma dos rendimentos declarados) e <b>{R.brl(teto)}</b> (teto: piso ÷ "
            f"fator de produtividade {R.pct(fator, 0)} [premissa declarada]). Este valor é "
            "ADICIONAL ao mercado formal dimensionado nas seções 4–6.</p>",
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
