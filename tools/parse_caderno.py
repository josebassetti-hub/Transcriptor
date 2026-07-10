#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_caderno.py — digere Cadernos Técnicos DER-ES (PDF) para data/regras-medicao.json.

Extrai por código de serviço: descrição, unidade, APLICAÇÃO, SERVIÇOS INCLUÍDOS NOS
PREÇOS, CRITÉRIO DE MEDIÇÃO e NORMAS — os campos que governam levantamento de
quantitativo e evitam dupla contagem no orçamento.

Uso:
  python3 tools/parse_caderno.py caderno1.pdf [caderno2.pdf ...]
  python3 tools/parse_caderno.py --dir pasta_com_pdfs/
Mescla no data/regras-medicao.json existente (atualiza códigos repetidos).
Requer poppler-utils (pdftotext).
"""
import argparse, glob, json, os, re, subprocess, sys

SECTIONS = [
    "DESCRIÇÃO TÉCNICA", "APLICAÇÃO", "MÉTODO DE EXECUÇÃO", "EQUIPAMENTOS",
    "SERVIÇOS INCLUÍDOS NOS PREÇOS", "CRITÉRIO DE MEDIÇÃO", "CRITÉRIOS DE MEDIÇÃO",
    "RECEBIMENTO", "NORMAS", "BIBLIOGRAFIA",
]
FURNITURE = re.compile(
    r"CADERNO TÉCNICO DE ESPECIFICAÇÃO|Folha:|Revisão:|^\s*\d/\d\s+\d+\s*$"
    r"|Departamento de Edificações e de Rodovias|27 3636-2000|Av\. Marechal Mascarenhas"
    r"|GOVERNO DO ESTADO|DO ESPÍRITO SANTO|^\s*DER[·\-‑]ES\s*$"
    r"|DEPARTAMENTO DE EDIFICAÇÕES E|DE RODOVIAS DO ESPÍRITO SANTO|^\s*Caderno Técnico\s*$")
UNITS = {"m", "m2", "m3", "und", "un", "pt", "cj", "kg", "l", "h", "mês", "ms", "par", "jg", "gl", "vb"}


def pdf_to_text(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"pdftotext falhou em {pdf}: {out.stderr[:200]}")
    return out.stdout


def clean_lines(text):
    return [ln.rstrip() for ln in text.splitlines() if not FURNITURE.search(ln)]


def parse_text(text):
    lines = clean_lines(text)
    caderno = next((l.strip() for l in lines[:10] if re.match(r"^\s*\d{2}\s*[–\-]", l)), "")
    # blocos: começam no cabeçalho "Código ... Descrição do serviço ... Und"
    starts = [i for i, l in enumerate(lines) if re.match(r"^\s*Código\s+Descrição do serviço\s+Und", l)]
    regras = {}
    for bi, start in enumerate(starts):
        end = starts[bi + 1] if bi + 1 < len(starts) else len(lines)
        block = lines[start:end]
        # ---- cabeçalho do serviço (até "Última atualização") ----
        head, body_start, atualizacao = [], 1, ""
        for j, l in enumerate(block[1:], start=1):
            m = re.search(r"Última atualização:\s*([\d/]+)", l)
            if m:
                atualizacao = m.group(1)
                body_start = j + 1
                break
            head.append(l)
        head_txt = " ".join(" ".join(head).split())
        mcode = re.search(r"\b(\d{6,8})\b", head_txt)
        if not mcode:
            continue
        code = mcode.group(1)
        desc = head_txt.replace(code, "", 1)
        # a coluna Und pode "vazar" para o meio do texto no layout multilinha —
        # pega o último token isolado que seja unidade conhecida e remove da descrição
        und = ""
        unit_tokens = [(m.start(), m.group(1)) for m in
                       re.finditer(r"(?:^|\s)(" + "|".join(sorted(UNITS, key=len, reverse=True)) + r")(?=\s|,|$)",
                                   desc, flags=re.IGNORECASE)]
        if unit_tokens:
            pos, und = unit_tokens[-1]
            desc = (desc[:pos] + " " + desc[pos + len(und) + 1:])
        desc = " ".join(desc.replace(" ,", ",").split()).strip(" -–")
        # ---- seções ----
        secs, cur = {}, None
        for l in block[body_start:]:
            s = l.strip()
            if s in SECTIONS:
                cur = "CRITÉRIO DE MEDIÇÃO" if s.startswith("CRITÉRIOS") else s
                secs[cur] = []
                continue
            if cur and s:
                secs[cur].append(s)

        def sec(name):
            return " ".join(" ".join(secs.get(name, [])).split()) or None

        normas = [n.strip() for n in secs.get("NORMAS", [])
                  if re.match(r"^(NBR|NR|ABNT|IT |Lei|Decreto|Portaria|IEC|ISO)", n.strip())]
        regras[code] = {
            "d": desc, "u": und, "caderno": caderno, "atualizacao": atualizacao,
            "aplicacao": sec("APLICAÇÃO"),
            "incluidos": sec("SERVIÇOS INCLUÍDOS NOS PREÇOS"),
            "criterio": sec("CRITÉRIO DE MEDIÇÃO"),
            "normas": normas or None,
        }
    return caderno, regras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="*")
    ap.add_argument("--dir", help="pasta com PDFs de cadernos")
    ap.add_argument("--out", default="data/regras-medicao.json")
    args = ap.parse_args()
    pdfs = list(args.pdfs)
    if args.dir:
        pdfs += sorted(glob.glob(os.path.join(args.dir, "*.pdf")))
    if not pdfs:
        sys.exit("nenhum PDF informado")

    merged = {"meta": {"fonte": "Cadernos Técnicos DER-ES", "cadernos": []}, "regras": {}}
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            merged = json.load(f)

    for pdf in pdfs:
        caderno, regras = parse_text(pdf_to_text(pdf))
        novos = sum(1 for c in regras if c not in merged["regras"])
        merged["regras"].update(regras)
        if caderno and caderno not in merged["meta"]["cadernos"]:
            merged["meta"]["cadernos"].append(caderno)
        sem_crit = [c for c, r in regras.items() if not r["criterio"]]
        print(f"{os.path.basename(pdf)}: {len(regras)} serviços ({novos} novos); sem critério: {sem_crit or 'nenhum'}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print(f"total no {args.out}: {len(merged['regras'])} serviços de {len(merged['meta']['cadernos'])} caderno(s)")


if __name__ == "__main__":
    main()
