#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embed_data.py — injeta os JSON de data/ dentro do orcamentista.html (entre marcadores).
Rode após build_base.py / parse_caderno.py. Idempotente: substitui o conteúdo anterior.

Uso: python3 tools/embed_data.py [--app orcamentista.html] [--data data]
"""
import argparse, json, os, re, sys

BLOCOS = [
    ("BASE_DER", "base-der-es.json"),
    ("MAPA", "mapa-padroes.json"),
    ("INDICES", "indices-estimativa.json"),
    ("REGRAS_MED", "regras-medicao.json"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default="orcamentista.html")
    ap.add_argument("--data", default="data")
    args = ap.parse_args()

    with open(args.app, encoding="utf-8") as f:
        html = f.read()

    for marker, fname in BLOCOS:
        path = os.path.join(args.data, fname)
        if not os.path.exists(path):
            if marker == "REGRAS_MED":
                data = {"meta": {"cadernos": []}, "regras": {}}
            else:
                sys.exit(f"{path} não existe — rode build_base.py antes")
        else:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        blob = blob.replace("</", "<\\/")  # não fechar a tag <script>
        pat = re.compile(r"/\*" + marker + r"_START\*/.*?/\*" + marker + r"_END\*/", re.S)
        rep = f"/*{marker}_START*/const {marker}={blob};/*{marker}_END*/"
        if not pat.search(html):
            sys.exit(f"marcador {marker} não encontrado em {args.app}")
        html = pat.sub(lambda m: rep, html)
        print(f"{marker}: {len(blob)/1024:.0f} KB embutidos de {fname}")

    with open(args.app, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"ok: {args.app} → {os.path.getsize(args.app)/1024:.0f} KB")


if __name__ == "__main__":
    main()
