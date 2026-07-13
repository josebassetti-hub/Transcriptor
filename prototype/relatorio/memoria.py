"""Memória de cálculo: registrador de verbetes auditáveis + anexo HTML.

Cada número-chave do relatório ganha um verbete registrado NO MOMENTO do
cálculo, com a fórmula simbólica, as entradas (valor + fonte + link), a
substituição numérica exata e o resultado. Como os verbetes saem das mesmas
variáveis que alimentam as seções, relatório e memória nunca divergem.

Objetivo: um analista externo verifica qualquer número sem depender do autor —
o link da consulta exata na API oficial, a página navegável da tabela no SIDRA
e o SQL reproduzível do BigQuery ficam no próprio anexo.
"""

import html as _html

from . import render as R


def _tabela(colunas, linhas):
    """Tabela sempre visível (a de render.py abre recolhida em <details>)."""
    ths = "".join("<th>{}</th>".format(c) for c in colunas)
    trs = "".join(
        "<tr>" + "".join("<td>{}</td>".format(c) for c in l) + "</tr>" for l in linhas
    )
    return "<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(ths, trs)


def _celula_fonte(entrada):
    partes = []
    if entrada.get("ref"):
        partes.append('<a href="#mem-{0}">{0}</a>'.format(entrada["ref"]))
    if entrada.get("fonte"):
        partes.append(entrada["fonte"])
    if entrada.get("url"):
        partes.append('<a href="{0}">{0}</a>'.format(entrada["url"]))
    return " · ".join(partes) or "—"


class Memoria:
    def __init__(self):
        self.verbetes = []

    def registrar(self, titulo, classificacao, formula, entradas, calculo,
                  resultado, racional="", provs=None, sql_ref=None,
                  explicacao=""):
        """Registra um verbete e retorna seu código ("M1", "M2", ...).

        classificacao: "DADO" | "DADO-PROXY" | "PREMISSA DECLARADA" |
                       "DERIVADO" (só combina verbetes anteriores) ou
                       combinação declarada ("DADO × PREMISSA")
        formula:   string simbólica ("SAM = TAM × fração × chave")
        entradas:  lista de dicts {nome, valor (string já formatada),
                   fonte (opc.), url (opc.), ref (código de outro verbete, opc.)}
        calculo:   substituição numérica exata em texto ("" quando o verbete é
                   um valor único, sem operação)
        resultado: string formatada do número final (igual à das seções)
        provs:     proveniências exibidas como selos (render.selo_fonte)
        sql_ref:   rótulo da consulta reproduzível no bloco de SQLs do anexo
        explicacao: a mesma conta em português corrente, sem jargão — para um
                   analista júnior entender o que o número significa
        """
        codigo = "M{}".format(len(self.verbetes) + 1)
        self.verbetes.append({
            "codigo": codigo, "titulo": titulo, "classificacao": classificacao,
            "formula": formula, "entradas": entradas, "calculo": calculo,
            "resultado": resultado, "racional": racional,
            "provs": provs or [], "sql_ref": sql_ref,
            "explicacao": explicacao,
        })
        return codigo

    def ref(self, codigo):
        """Citação sobrescrita "(memória: M4)" para usar no texto das seções."""
        return (' <a class="memref" href="#mem-{0}">(memória: {0})</a>'
                .format(codigo))

    def render_anexo(self, sql_blocos=None):
        """HTML da seção "Anexo — Memória de cálculo"; "" se não há verbetes.

        sql_blocos: lista de tuplas (rotulo, caminho_relativo, conteudo_sql).
        """
        if not self.verbetes:
            return ""
        blocos = [
            "<p>Auditoria completa do estudo: cada número-chave tem um verbete "
            "com a fórmula, as entradas (com fonte e link), a substituição "
            "numérica exata e o resultado — gerados pelo mesmo cálculo que "
            "produziu as seções, portanto nunca divergem delas. Como verificar: "
            "os links de API abrem a consulta exata na fonte oficial (resposta "
            "em JSON); os links de tabela abrem a página navegável do SIDRA; os "
            "dados do BigQuery (Base dos Dados) têm o SQL exato reproduzível no "
            "fim do anexo. Classificação de cada verbete: <b>DADO</b> (medido "
            "na fonte), <b>DADO-PROXY</b> (medido, com viés declarado), "
            "<b>PREMISSA DECLARADA</b> (escolha do estudo, com racional) ou "
            "<b>DERIVADO</b> (só combina verbetes anteriores).</p>"
        ]
        for v in self.verbetes:
            blocos.append('<div class="memoria" id="mem-{}">'.format(v["codigo"]))
            blocos.append(
                '<h3>{} — {} <span class="classif">{}</span></h3>'.format(
                    v["codigo"], v["titulo"], v["classificacao"])
            )
            blocos.append('<p class="formula">{}</p>'.format(v["formula"]))
            if v["entradas"]:
                blocos.append(_tabela(
                    ["Entrada", "Valor", "Fonte / verificação"],
                    [(e.get("nome", ""), e.get("valor", ""), _celula_fonte(e))
                     for e in v["entradas"]],
                ))
            if v["calculo"]:
                blocos.append(
                    '<p>Cálculo: <span class="formula">{}</span> = <b>{}</b></p>'
                    .format(v["calculo"], v["resultado"])
                )
            else:
                blocos.append("<p>Valor: <b>{}</b></p>".format(v["resultado"]))
            if v.get("explicacao"):
                blocos.append(
                    '<p class="explicacao"><b>Em palavras:</b> {}</p>'
                    .format(v["explicacao"])
                )
            if v["racional"]:
                blocos.append('<p class="premissas">{}</p>'.format(v["racional"]))
            for p in v["provs"]:
                blocos.append(R.selo_fonte(p))
            if v["sql_ref"]:
                blocos.append(
                    '<p class="fonte">Reprodução: {} — <a href="#sql-anexo">SQL '
                    "no fim deste anexo</a>.</p>".format(v["sql_ref"])
                )
            blocos.append("</div>")
        if sql_blocos:
            blocos.append(
                '<h3 id="sql-anexo">Reprodução das consultas BigQuery '
                "(Base dos Dados)</h3>"
                "<p>As consultas abaixo são exatamente as que geraram os dados "
                "de CNPJ, frota e RAIS deste estudo. Para reproduzir: abra "
                '<a href="https://console.cloud.google.com/bigquery">'
                "console.cloud.google.com/bigquery</a>, cole a consulta e "
                "execute (projeto público <code>basedosdados</code>).</p>"
            )
            for rotulo, caminho, conteudo in sql_blocos:
                blocos.append(
                    "<details><summary>SQL — {} (arquivo {})</summary>"
                    "<pre>{}</pre></details>".format(
                        rotulo, caminho, _html.escape(conteudo))
                )
        return ("<section id=\"memoria-calculo\"><h2>Anexo — Memória de cálculo"
                "</h2>" + "".join(blocos) + "</section>")
