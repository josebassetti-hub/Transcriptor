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
from fontes import ibge, bcb, cnpj
from calculos import sizing
from relatorio import render as R

RAIZ = Path(__file__).resolve().parent


def secao(titulo, *blocos):
    return f"<section><h2>{titulo}</h2>" + "".join(blocos) + "</section>"


def gerar(config: dict, modo: str) -> str:
    cliente = ClienteHTTP(modo)

    # ---- collect -------------------------------------------------------------
    receita, prov_ibge = ibge.receita_setorial(cliente, config["topdown"])
    series_macro = [
        bcb.serie_sgs(cliente, s["codigo"], s["nome"], s["ultimos"])
        for s in config["series_bcb"]
    ]
    linhas_cnpj, prov_cnpj = cnpj.agregados(config, demo=(modo != "live"))
    contagem = cnpj.contar_icp(linhas_cnpj, config["icp"])
    din, _ = cnpj.dinamica(config, demo=(modo != "live"))

    # ---- compute -------------------------------------------------------------
    td = sizing.top_down(receita, config["topdown"])
    bu = sizing.bottom_up(contagem["n_icp"], config["icp"], config["captura"])
    tri = sizing.triangulacao(td["sam"], bu["sam"])
    som_base = bu["cenarios"]["base"]["som"]

    # ---- write + render ------------------------------------------------------
    s = []

    # 1. Sumário executivo
    kpis = "".join(
        f'<div class="kpi"><b>{v}</b><span>{k}</span></div>'
        for k, v in [
            (f"TAM Brasil ({td['ano_base']}, top-down)", R.brl(td["tam"])),
            ("SAM " + config["regiao"]["sigla"] + " (triangulado)", R.brl((td["sam"] + bu["sam"]) / 2)),
            (f"SOM base em {bu['horizonte_anos']} anos", R.brl(som_base)),
            ("Empresas-alvo (ICP, censo CNPJ)", R.inteiro(bu["n_icp"])),
            ("CAGR do mercado (série oficial)", R.pct(td["cagr"]) if td["cagr"] else "n/d"),
        ]
    )
    s.append(secao(
        "1. Sumário executivo",
        f'<div class="kpis">{kpis}</div>',
        "<p>O dimensionamento por duas metodologias independentes chega a valores "
        f"próximos (divergência de {R.pct(tri['divergencia'])}): "
        f"{R.brl(td['sam'])} pelo recorte top-down da receita setorial oficial e "
        f"{R.brl(bu['sam'])} pelo bottom-up sobre o censo de {R.inteiro(bu['n_icp'])} "
        f"empresas-alvo da base CNPJ. No cenário-base de captura "
        f"({R.pct(bu['cenarios']['base']['taxa'], 0)} em {bu['horizonte_anos']} anos), o "
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
    s.append(secao(
        "4. Tamanho de mercado — top-down",
        f"<p>A receita nacional do setor somou <b>{R.brl(td['tam'])}</b> em {td['ano_base']}"
        + (f", com CAGR de <b>{R.pct(td['cagr'])}</b> desde {anos[0]}" if td["cagr"] else "")
        + f". Aplicando a participação do segmento ({R.pct(td['premissas']['participacao_segmento'],0)}) "
        f"e da região ({R.pct(td['premissas']['participacao_regiao'],0)}), o SAM top-down de "
        f"{config['regiao']['nome']} é <b>{R.brl(td['sam'])}</b>.</p>",
        R.tabela(["Ano", "Receita (R$)"], [(a, R.brl(receita[a])) for a in anos]),
        f'<p class="premissas">Premissas: segmento — {td["premissas"]["racional_segmento"]}; '
        f'região — {td["premissas"]["racional_regiao"]}.</p>',
        R.selo_fonte(prov_ibge),
    ))

    s.append(secao(
        "5. Tamanho de mercado — bottom-up (censo CNPJ)",
        f"<p>O universo do CNAE na região tem <b>{R.inteiro(contagem['universo'])}</b> "
        f"estabelecimentos ativos; o recorte de ICP resulta em <b>{R.inteiro(bu['n_icp'])}</b> "
        f"empresas-alvo. Com ticket médio anual de {R.brl(bu['ticket'])}, o SAM bottom-up é "
        f"<b>{R.brl(bu['sam'])}</b>.</p>",
        R.grafico_barras_h(
            sorted(contagem["por_porte"].items(), key=lambda kv: -kv[1]),
            "estabelecimentos ativos",
        ),
        f'<p class="premissas">Premissas: {bu["premissas"]["icp"]}. '
        f'Ticket: {bu["premissas"]["racional_ticket"]}.</p>',
        R.selo_fonte(prov_cnpj),
    ))

    cen = bu["cenarios"]
    s.append(secao(
        "6. Triangulação e cenários (TAM/SAM/SOM)",
        f"<p>{tri['leitura']}</p>",
        R.grafico_funil([
            ("TAM", td["tam"], f"Brasil, top-down, {td['ano_base']}"),
            ("SAM", (td["sam"] + bu["sam"]) / 2,
             f"média das metodologias (divergência {R.pct(tri['divergencia'])})"),
            ("SOM", som_base,
             f"cenário-base: {R.pct(cen['base']['taxa'],0)} de captura em {bu['horizonte_anos']} anos"),
        ]),
        R.tabela(
            ["Cenário", "Taxa de captura", "SOM anual"],
            [(n.capitalize(), R.pct(c["taxa"], 0), R.brl(c["som"])) for n, c in cen.items()],
        ),
    ))

    # 7. Dinâmica do mercado
    anos_d = [a for a, _, _ in din]
    s.append(secao(
        "7. Dinâmica do mercado-alvo",
        f"<p>Entre {anos_d[0]} e {anos_d[-1]}, as aberturas anuais de estabelecimentos do CNAE "
        f"na região cresceram de {R.inteiro(din[0][1])} para {R.inteiro(din[-1][1])}, mantendo "
        "saldo líquido positivo em todos os anos — sinal de expansão da base de clientes "
        "potenciais do produto.</p>",
        R.grafico_barras_pares(
            anos_d, [a for _, a, _ in din], [f for _, _, f in din], ["Aberturas", "Fechamentos"]
        ),
        R.selo_fonte(prov_cnpj),
    ))

    # 8. Limitações e fontes
    s.append(secao(
        "8. Limitações declaradas",
        "<ul>"
        "<li>CNPJ ativo não significa empresa operante; o recorte por situação cadastral, idade "
        "e porte mitiga, mas não elimina, a superestimação do universo.</li>"
        "<li>A informalidade do setor não é capturada pela base CNPJ.</li>"
        "<li>As participações de segmento e região do top-down são premissas curadas por setor "
        "e devem ser revisadas com o cliente.</li>"
        "<li>Este protótipo não inclui share de varejo (Nielsen/Kantar) nem pesquisa primária.</li>"
        "</ul>",
    ))

    meta = {
        "titulo": config["titulo"],
        "contexto": config["contexto"],
        "cnaes": ", ".join(f'{c["codigo"]} ({c["descricao"]})' for c in config["cnaes"]),
        "regiao": config["regiao"]["nome"],
        "gerado_em": time.strftime("%d/%m/%Y %H:%M UTC", time.gmtime()),
    }
    provs = [prov_ibge, prov_cnpj] + [prov for _, prov in series_macro]
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
