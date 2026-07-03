"""Renderizador do relatório: HTML autocontido com gráficos SVG inline.

Princípios (da especificação, docs/especificacao-produto-mvp.md, seção 3):
- Todo número exibido vem do dicionário de dados calculados — o texto analítico
  é gerado por template determinístico neste protótipo (em produção, LLM com
  guard-rail: cada número do texto é validado contra o JSON antes de renderizar).
- Cada seção exibe o selo da fonte (com proveniência live/fixture).
- Se qualquer fixture foi usada, um aviso de DEMONSTRAÇÃO abre o relatório.

Paleta: instância de referência validada (dataviz) — série 1 azul, série 2 aqua
(com rótulos diretos, exigência do contraste), rampa ordinal azul para o funil.
"""

# --- paleta validada (light / dark) -----------------------------------------
CORES = {
    "s1": ("#2a78d6", "#3987e5"),
    "s2": ("#1baf7a", "#199e70"),
    "funil": [("#86b6ef", "#184f95"), ("#3987e5", "#2a78d6"), ("#1c5cab", "#86b6ef")],
}


def brl(v: float) -> str:
    if v >= 1e9:
        return f"R$ {v/1e9:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")
    if v >= 1e6:
        return f"R$ {v/1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def inteiro(v) -> str:
    return f"{int(v):,}".replace(",", ".")


def pct(v: float, casas=1) -> str:
    return f"{v*100:.{casas}f}%".replace(".", ",")


def selo_fonte(prov: dict) -> str:
    import html as _html
    demo = prov["origem"] == "fixture"
    classe = "fonte demo" if demo else "fonte"
    rotulo = "DEMONSTRAÇÃO — " if demo else ""
    motivo = (
        f' · motivo do fallback: {_html.escape(prov["motivo"])}'
        if demo and prov.get("motivo")
        else ""
    )
    return (
        f'<p class="{classe}">Fonte: {rotulo}{prov.get("fonte", "")} · '
        f'<a href="{prov["url"]}">{prov["url"]}</a> · consulta: {prov["consultado_em"]}{motivo}</p>'
    )


# --- gráficos SVG ------------------------------------------------------------

def _svg(w, h, corpo):
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'style="max-width:{w}px;display:block">{corpo}</svg>'
    )


def grafico_funil(itens):
    """Funil TAM/SAM/SOM: barras horizontais em rampa ordinal, rótulos diretos."""
    w, h, alt, gap, esq = 760, 190, 44, 14, 66
    max_v = max(v for _, v, _ in itens)
    corpo = []
    for i, (nome, valor, nota) in enumerate(itens):
        y = 10 + i * (alt + gap)
        larg = max(6, (w - esq - 200) * valor / max_v)
        cor = f"var(--funil-{i})"
        corpo.append(
            f'<text x="{esq-10}" y="{y+alt/2+5}" text-anchor="end" class="rotulo">{nome}</text>'
            f'<rect x="{esq}" y="{y}" width="{larg:.0f}" height="{alt}" rx="4" fill="{cor}">'
            f"<title>{nome}: {brl(valor)} — {nota}</title></rect>"
            f'<text x="{esq+larg+10:.0f}" y="{y+alt/2-3}" class="valor">{brl(valor)}</text>'
            f'<text x="{esq+larg+10:.0f}" y="{y+alt/2+15}" class="nota">{nota}</text>'
        )
    return _svg(w, h, "".join(corpo))


def grafico_linhas(series, unidade):
    """Linhas (2 séries máx.): legenda + rótulo direto no fim de cada série."""
    w, h, m_esq, m_dir, m_topo, m_base = 760, 260, 52, 130, 26, 34
    todos = [v for _, pontos in series for _, v in pontos]
    v_min, v_max = min(todos), max(todos)
    folga = (v_max - v_min) * 0.15 or 1
    v_min, v_max = v_min - folga, v_max + folga
    n = max(len(p) for _, p in series)
    def X(i):
        return m_esq + i * (w - m_esq - m_dir) / (n - 1)
    def Y(v):
        return m_topo + (v_max - v) * (h - m_topo - m_base) / (v_max - v_min)
    corpo = []
    for frac in (0, 0.5, 1):
        v = v_min + (v_max - v_min) * frac
        corpo.append(
            f'<line x1="{m_esq}" y1="{Y(v):.0f}" x2="{w-m_dir}" y2="{Y(v):.0f}" class="grade"/>'
            f'<text x="{m_esq-8}" y="{Y(v)+4:.0f}" text-anchor="end" class="nota">{v:.1f}</text>'
        )
    rotulos_x = series[0][1]
    for i in (0, len(rotulos_x) // 2, len(rotulos_x) - 1):
        corpo.append(
            f'<text x="{X(i):.0f}" y="{h-10}" text-anchor="middle" class="nota">{rotulos_x[i][0]}</text>'
        )
    for si, (nome, pontos) in enumerate(series):
        cor = f"var(--s{si+1})"
        d = " ".join(f'{"M" if i==0 else "L"}{X(i):.1f},{Y(v):.1f}' for i, (_, v) in enumerate(pontos))
        ux, uy = X(len(pontos) - 1), Y(pontos[-1][1])
        corpo.append(
            f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="2"/>'
            f'<circle cx="{ux:.1f}" cy="{uy:.1f}" r="4" fill="{cor}">'
            f"<title>{nome} — último: {pontos[-1][1]:.2f} {unidade}</title></circle>"
            f'<text x="{ux+9:.1f}" y="{uy+4:.1f}" class="rotulo" fill="{cor}">'
            f"{nome.split()[0]} {pontos[-1][1]:.2f}</text>"
        )
    return _svg(w, h, "".join(corpo))


def grafico_barras_pares(rotulos, serie_a, serie_b, nomes):
    """Barras agrupadas (2 séries) com espaçador de 2px e rótulos diretos."""
    w, h, m_esq, m_topo, m_base = 760, 250, 52, 30, 34
    v_max = max(serie_a + serie_b) * 1.18
    n = len(rotulos)
    grupo = (w - m_esq - 20) / n
    barra = min(46, (grupo - 18) / 2)
    def Y(v):
        return m_topo + (v_max - v) * (h - m_topo - m_base) / v_max
    corpo = [f'<line x1="{m_esq}" y1="{h-m_base}" x2="{w-20}" y2="{h-m_base}" class="eixo"/>']
    for i, rot in enumerate(rotulos):
        x0 = m_esq + i * grupo + (grupo - 2 * barra - 2) / 2
        for k, (v, cor_v) in enumerate(((serie_a[i], "var(--s1)"), (serie_b[i], "var(--s2)"))):
            x = x0 + k * (barra + 2)
            corpo.append(
                f'<rect x="{x:.0f}" y="{Y(v):.0f}" width="{barra:.0f}" height="{h-m_base-Y(v):.0f}"'
                f' rx="4" fill="{cor_v}"><title>{nomes[k]} {rot}: {inteiro(v)}</title></rect>'
                f'<text x="{x+barra/2:.0f}" y="{Y(v)-6:.0f}" text-anchor="middle" class="nota">'
                f"{inteiro(v)}</text>"
            )
        corpo.append(f'<text x="{x0+barra+1:.0f}" y="{h-12}" text-anchor="middle" class="nota">{rot}</text>')
    legenda = "".join(
        f'<g transform="translate({m_esq + 170*k},4)"><rect width="12" height="12" rx="3" fill="var(--s{k+1})"/>'
        f'<text x="18" y="11" class="nota">{nome}</text></g>'
        for k, nome in enumerate(nomes)
    )
    return _svg(w, h, legenda + "".join(corpo))


def grafico_barras_h(pares, titulo_valor):
    """Barras horizontais simples (1 série) com rótulos diretos."""
    w, alt, gap, esq = 760, 30, 10, 88
    h = 12 + len(pares) * (alt + gap)
    v_max = max(v for _, v in pares)
    corpo = []
    for i, (nome, v) in enumerate(pares):
        y = 6 + i * (alt + gap)
        larg = max(4, (w - esq - 120) * v / v_max)
        corpo.append(
            f'<text x="{esq-8}" y="{y+alt/2+5}" text-anchor="end" class="rotulo">{nome}</text>'
            f'<rect x="{esq}" y="{y}" width="{larg:.0f}" height="{alt}" rx="4" fill="var(--s1)">'
            f"<title>{nome}: {inteiro(v)} {titulo_valor}</title></rect>"
            f'<text x="{esq+larg+8:.0f}" y="{y+alt/2+5}" class="valor">{inteiro(v)}</text>'
        )
    return _svg(w, h, "".join(corpo))


def tabela(colunas, linhas):
    ths = "".join(f"<th>{c}</th>" for c in colunas)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return (
        "<details><summary>Ver dados em tabela</summary>"
        f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></details>'
    )


# --- redação (determinística no protótipo; LLM com guard-rail em produção) ---

def redigir_secao_llm(secao: str, dados_json: dict) -> str:
    """Ponto de integração com a Claude API em produção.

    O prompt recebe APENAS o JSON de dados calculados e instruções de citação;
    a saída passa pelo guard-rail: todo número presente no texto precisa existir
    no JSON, senão a seção é regerada. Neste protótipo a redação é feita por
    templates determinísticos nas funções de seção (mesma garantia, sem custo).
    """
    raise NotImplementedError("produção: chamada à Claude API com guard-rail anti-alucinação")


# --- montagem do HTML ---------------------------------------------------------

ESTILO = """
:root{--surface:#fcfcfb;--pagina:#f9f9f7;--ink:#0b0b0b;--ink2:#52514e;--mudo:#898781;
--grade:#e1e0d9;--eixo:#c3c2b7;--s1:#2a78d6;--s2:#1baf7a;
--funil-0:#86b6ef;--funil-1:#3987e5;--funil-2:#1c5cab;--borda:rgba(11,11,11,.1);
--demo-fundo:#fff7e6;--demo-borda:#eda100}
@media(prefers-color-scheme:dark){:root{--surface:#1a1a19;--pagina:#0d0d0d;--ink:#fff;
--ink2:#c3c2b7;--mudo:#898781;--grade:#2c2c2a;--eixo:#383835;--s1:#3987e5;--s2:#199e70;
--funil-0:#184f95;--funil-1:#2a78d6;--funil-2:#86b6ef;--borda:rgba(255,255,255,.1);
--demo-fundo:#33290d;--demo-borda:#c98500}}
*{box-sizing:border-box}body{margin:0;background:var(--pagina);color:var(--ink);
font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:900px;margin:0 auto;padding:32px 20px 64px}
section{background:var(--surface);border:1px solid var(--borda);border-radius:12px;
padding:24px 28px;margin:18px 0;overflow-x:auto}
h1{font-size:1.7rem;margin:.2rem 0}h2{font-size:1.15rem;margin:0 0 6px}
.sub{color:var(--ink2);margin:0 0 4px}.aviso-demo{background:var(--demo-fundo);
border:1px solid var(--demo-borda);border-radius:12px;padding:14px 20px;margin:18px 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:14px 0}
.kpi{border:1px solid var(--borda);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:1.5rem}.kpi span{color:var(--ink2);font-size:.82rem}
.fonte{color:var(--mudo);font-size:.78rem;margin:10px 0 0}
.fonte.demo{color:var(--demo-borda);font-weight:600}
.fonte a{color:inherit}
.rotulo{font-size:13px;fill:var(--ink2)}.valor{font-size:14px;font-weight:700;fill:var(--ink)}
.nota{font-size:12px;fill:var(--mudo)}.grade{stroke:var(--grade)}.eixo{stroke:var(--eixo)}
svg text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
table{border-collapse:collapse;margin:10px 0;font-size:.85rem;width:100%}
td,th{border-bottom:1px solid var(--grade);padding:6px 10px;text-align:left;
font-variant-numeric:tabular-nums}
details{margin-top:10px;color:var(--ink2)}summary{cursor:pointer;font-size:.85rem}
.premissas{font-size:.85rem;color:var(--ink2);border-left:3px solid var(--grade);
padding-left:12px;margin:12px 0 0}
footer{color:var(--mudo);font-size:.8rem;margin-top:28px}
"""


def montar(secoes: list, meta: dict, tem_demo: bool) -> str:
    aviso = (
        '<div class="aviso-demo"><b>Este relatório contém dados de demonstração.</b> '
        "Confira o selo de fonte no fim de cada seção: selo <b>cinza</b> = dado obtido ao "
        "vivo da fonte oficial no momento da geração; selo <b>laranja (DEMONSTRAÇÃO)</b> = "
        "valor ilustrativo de fixture. Para ligar as fontes reais que ainda faltam, siga "
        "o passo a passo em <code>prototype/README.md</code> (seção &quot;Ligando dados "
        "públicos reais&quot;) — comece rodando <code>python3 testar_fontes.py</code>.</div>"
        if tem_demo
        else ""
    )
    corpo = "".join(secoes)
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta['titulo']}</title><style>{ESTILO}</style></head>
<body><main>
<header><h1>{meta['titulo']}</h1>
<p class="sub">{meta['contexto']}</p>
<p class="sub">CNAEs: {meta['cnaes']} · Região: {meta['regiao']} · Gerado em {meta['gerado_em']}</p>
</header>
{aviso}
{corpo}
<footer>Protótipo técnico — pipeline: coleta (IBGE/Bacen/CNPJ) → cálculo → redação → render.
Metodologia e fontes: ver seção "Metodologia" e selos por seção.
Base conceitual: docs/pesquisa-mercado-ferramentas-analise.md.</footer>
</main></body></html>"""
