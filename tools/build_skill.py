#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_skill.py — sincroniza as referências da skill a partir de data/ e gera o zip
para upload no claude.ai (Configurações → Capacidades → Skills → carregar skill).

Rodar sempre que a tabela DER-ES ou os cadernos forem atualizados:
  python3 tools/build_skill.py
Saída: dist/orcamentista-der-es.zip (pasta orcamentista-der-es/ na raiz do zip).
"""
import json, os, shutil, subprocess, sys, zipfile

SKILL = ".claude/skills/orcamentista-der-es"
REFS = [
    ("data/base-der-es.json", "base-der-es.json"),
    ("data/mapa-padroes.json", "mapa-padroes.json"),
    ("data/indices-estimativa.json", "indices-estimativa.json"),
    ("data/regras-medicao.json", "regras-medicao.json"),
    ("data/base-sinapi-es-skill.json", "base-sinapi-es.json"),
    ("data/sinapi-decomposicoes.json", "sinapi-decomposicoes.json"),
    ("data/exemplo-comercial.json", "exemplo-comercial.json"),
    ("data/insumos.json", "insumos-der-es.json"),
    ("data/composicoes-resumo.json", "composicoes-der-es.json"),
    ("METODOLOGIA.md", "METODOLOGIA.md"),
    ("COBERTURA.md", "COBERTURA.md"),
]


def main():
    refdir = os.path.join(SKILL, "references")
    os.makedirs(refdir, exist_ok=True)
    for src, dst in REFS:
        if not os.path.exists(src):
            sys.exit(f"faltando {src}")
        shutil.copyfile(src, os.path.join(refdir, dst))
        print(f"ref: {dst} ({os.path.getsize(src)/1024:.0f} KB)")

    # exemplo de entrada gerado pelo próprio motor (fonte única de verdade)
    ex = subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "motor_orcamento.py"),
                         "--exemplo"], capture_output=True, text=True)
    if ex.returncode != 0:
        sys.exit("motor --exemplo falhou: " + ex.stderr[:200])
    with open(os.path.join(refdir, "exemplo-entrada.json"), "w", encoding="utf-8") as f:
        f.write(ex.stdout)

    # geradores de entrega viajam junto com a skill
    for src in ("tools/gera_excel.py", "tools/gera_memoria.py", "tools/memoria_docx.js"):
        shutil.copyfile(src, os.path.join(SKILL, "scripts", os.path.basename(src)))
        print("script:", os.path.basename(src))

    # autoteste obrigatório antes de empacotar
    at = subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "motor_orcamento.py"),
                         "--autoteste", "--refs", refdir], capture_output=True, text=True)
    print(at.stdout.strip().splitlines()[-1])
    if at.returncode != 0:
        sys.exit("AUTOTESTE FALHOU — zip não gerado:\n" + at.stdout)

    # o SKILL.md não pode citar um dourado diferente do que o motor trava
    import re
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
        md = f.read()
    sys.path.insert(0, os.path.join(SKILL, "scripts"))
    import motor_orcamento as _m
    for rotulo, valor in [("residencial", _m.GOLD_CUSTO_DIRETO),
                          ("comercial", _m.GOLD_COMERCIAL["geral"])]:
        br = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if br not in md:
            sys.exit(f"SKILL.md não cita o dourado {rotulo} atual (R$ {br}) — atualize o texto")
    print("dourados citados no SKILL.md conferem com o motor")

    # valida frontmatter
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
        head = f.read().split("---")[1]
    name = next(l.split(":", 1)[1].strip() for l in head.splitlines() if l.startswith("name:"))
    desc = next(l.split(":", 1)[1].strip() for l in head.splitlines() if l.startswith("description:"))
    assert len(name) <= 64 and len(desc) <= 1024, "frontmatter fora dos limites"
    print(f"frontmatter ok: name={name!r} ({len(name)}), description ({len(desc)} chars)")

    os.makedirs("dist", exist_ok=True)
    zpath = "dist/orcamentista-der-es.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(SKILL):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fn in sorted(files):
                if fn.endswith((".pyc", ".pyo")):
                    continue
                full = os.path.join(root, fn)
                rel = os.path.join("orcamentista-der-es", os.path.relpath(full, SKILL))
                z.write(full, rel)
    print(f"zip: {zpath} ({os.path.getsize(zpath)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
