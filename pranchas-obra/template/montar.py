#!/usr/bin/env python3
"""
Monta uma prancha HTML a partir de um config JSON + template + SVG de desenho.

Uso:
    python3 montar.py config.json [-o saida.html]

Config (JSON):
{
  "template": "prancha.html",            // caminho relativo ao próprio config
  "saida": "minha-prancha.html",
  "desenho": {
    "svg": "base.svg",                   // SVG base (ex.: extraído do PDF via pdftocairo -svg)
    "recorte": [x, y, largura, altura],  // viewBox de recorte em pt (opcional)
    "camada_sob": "grade.svg",           // fragmento SVG inserido POR BAIXO da base (opcional)
    "camada_sobre": "simbolos.svg"       // fragmento SVG inserido POR CIMA da base (opcional)
  },
  "titulo_prancha": "PAGINAÇÃO PISO 2º ANDAR",
  "escala": "1/100",
  "legenda": { "titulo": "LEGENDA",
               "itens": [ {"texto": "PORCELANATO 90X90"},
                          {"simbolo": {"tipo": "quadrado", "cor": "#f3c"}, "texto": "PAINEL DE LED 28X28W"} ] },
  "notas": { "titulo": "GERAL", "texto": "INSTALAÇÃO DA PELE DE VIDRO\nINSTALAÇÃO DE PISOS" },
  "carimbo": { "titulo_bloco": "PROJETO DE REFORMA", "resp_nome": "...", "resp_reg": "...",
               "resp_sub": "...", "cliente": "...", "autor": "...", "endereco": "...",
               "data": "...", "area": "...", "prancha": "2/6" },
  "marca": "REPRODUÇÃO DIGITAL — NÃO SUBSTITUI PRANCHA ASSINADA PELO RESPONSÁVEL TÉCNICO"
}

Fragmentos de camada devem ser SVG parcial (ex.: "<defs>...</defs><g>...</g>"),
no MESMO sistema de coordenadas do SVG base (pt da página original).
"""
import json
import re
import sys
from pathlib import Path

ABRE_SVG = re.compile(r"<svg\b[^>]*>", re.S)


def le(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def monta_desenho(cfg: dict, base_dir: Path) -> str:
    svg = le(base_dir / cfg["svg"])
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)

    m = ABRE_SVG.search(svg)
    if not m:
        raise SystemExit(f"SVG sem tag <svg>: {cfg['svg']}")
    tag = m.group(0)

    if "recorte" in cfg:
        x, y, w, h = cfg["recorte"]
        tag_novo = re.sub(r'\bviewBox="[^"]*"', "", tag)
        tag_novo = re.sub(r'\bwidth="[^"]*"', "", tag_novo)
        tag_novo = re.sub(r'\bheight="[^"]*"', "", tag_novo)
        tag_novo = tag_novo.replace(
            "<svg",
            f'<svg viewBox="{x} {y} {w} {h}" preserveAspectRatio="xMidYMid meet"',
            1,
        )
        svg = svg[: m.start()] + tag_novo + svg[m.end():]
        tag = tag_novo

    if "camada_sob" in cfg:
        frag = le(base_dir / cfg["camada_sob"])
        i = svg.index(tag) + len(tag)
        svg = svg[:i] + "\n<!-- camada_sob -->\n" + frag + "\n" + svg[i:]

    if "camada_sobre" in cfg:
        frag = le(base_dir / cfg["camada_sobre"])
        i = svg.rindex("</svg>")
        svg = svg[:i] + "\n<!-- camada_sobre -->\n" + frag + "\n" + svg[i:]

    return svg


def simbolo_html(simb) -> str:
    if not simb:
        return ""
    if isinstance(simb, str):  # SVG cru
        return simb
    tipo = simb.get("tipo", "quadrado")
    cor = simb.get("cor", "#fff")
    borda = simb.get("borda", "#000")
    if tipo == "quadrado":
        return (f'<svg width="10" height="10"><rect x="1" y="1" width="8" height="8" '
                f'fill="{cor}" stroke="{borda}" stroke-width="0.8"/></svg>')
    if tipo == "retangulo":
        return (f'<svg width="18" height="9"><rect x="1" y="1" width="16" height="7" '
                f'fill="{cor}" stroke="{borda}" stroke-width="0.8"/></svg>')
    if tipo == "circulo":
        return (f'<svg width="10" height="10"><circle cx="5" cy="5" r="3.6" '
                f'fill="{cor}" stroke="{borda}" stroke-width="0.8"/></svg>')
    if tipo == "linha":
        return (f'<svg width="18" height="6"><line x1="1" y1="3" x2="17" y2="3" '
                f'stroke="{cor}" stroke-width="1.6"/></svg>')
    if tipo == "spot":
        return ('<svg width="10" height="10"><path d="M5 1V9M1 5H9M2.2 2.2L7.8 7.8M7.8 2.2L2.2 7.8" '
                'stroke="#000" stroke-width="0.7"/></svg>')
    raise SystemExit(f"tipo de símbolo desconhecido: {tipo}")


def monta_legenda(cfg) -> str:
    if not cfg or not cfg.get("itens"):
        return ""
    linhas = []
    for item in cfg["itens"]:
        simb = simbolo_html(item.get("simbolo"))
        cel_simb = f'<td class="simb">{simb}</td>' if simb else '<td class="simb"></td>'
        linhas.append(f"<tr>{cel_simb}<td>{item['texto']}</td></tr>")
    titulo = cfg.get("titulo", "LEGENDA")
    return (f'<div class="quadro" style="min-width:52mm">'
            f'<div class="cab centro">{titulo}</div>'
            f"<table>{''.join(linhas)}</table></div>")


def monta_notas(cfg) -> str:
    if not cfg or not cfg.get("texto"):
        return ""
    titulo = cfg.get("titulo", "GERAL")
    return (f'<div class="quadro" style="max-width:80mm">'
            f'<div class="cab">{titulo}:</div>'
            f'<div class="notas">{cfg["texto"]}</div></div>')


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cfg_path = Path(sys.argv[1]).resolve()
    base_dir = cfg_path.parent
    cfg = json.loads(le(cfg_path))

    template = le((base_dir / cfg.get("template", "prancha.html")).resolve())
    carimbo = cfg.get("carimbo", {})
    tokens = {
        "DESENHO_HTML": monta_desenho(cfg["desenho"], base_dir),
        "TITULO_PRANCHA": cfg.get("titulo_prancha", ""),
        "ESCALA": cfg.get("escala", ""),
        "LEGENDA_HTML": monta_legenda(cfg.get("legenda")),
        "NOTAS_HTML": monta_notas(cfg.get("notas")),
        "TITULO_BLOCO": carimbo.get("titulo_bloco", "PROJETO DE REFORMA"),
        "RESP_NOME": carimbo.get("resp_nome", ""),
        "RESP_REG": carimbo.get("resp_reg", ""),
        "RESP_SUB": carimbo.get("resp_sub", ""),
        "CLIENTE": carimbo.get("cliente", ""),
        "AUTOR": carimbo.get("autor", ""),
        "ENDERECO": carimbo.get("endereco", ""),
        "DATA": carimbo.get("data", ""),
        "AREA": carimbo.get("area", ""),
        "PRANCHA": carimbo.get("prancha", ""),
        "MARCA": cfg.get("marca", ""),
    }
    html = template
    for chave, valor in tokens.items():
        html = html.replace("{{" + chave + "}}", valor)

    saida = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "-o" else cfg.get("saida")
    if not saida:
        raise SystemExit("defina 'saida' no config ou use -o")
    destino = (base_dir / saida).resolve()
    destino.write_text(html, encoding="utf-8")
    print(f"prancha montada: {destino}")


if __name__ == "__main__":
    main()
