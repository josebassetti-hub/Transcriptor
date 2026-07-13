#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_regras.py — consolida os JSONs extraídos dos Cadernos Técnicos (1 por caderno,
formato {arquivo, caderno, truncado, fichas:{codigo:{...}}}) no data/regras-medicao.json
e valida contra a base de preços.

Uso: python3 tools/merge_regras.py <dir_com_jsons> [--out data/regras-medicao.json]
"""
import argparse, glob, json, os, re, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--out", default="data/regras-medicao.json")
    ap.add_argument("--base", default="data/base-der-es.json")
    args = ap.parse_args()

    merged = {"meta": {"fonte": "Cadernos Técnicos DER-ES", "cadernos": []}, "regras": {}}
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            merged = json.load(f)

    problemas, truncados = [], []
    arquivos = sorted(glob.glob(os.path.join(args.dir, "*.json")))
    for path in arquivos:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            problemas.append(f"{os.path.basename(path)}: JSON inválido ({e})")
            continue
        fichas = data.get("fichas") or {}
        cad = data.get("caderno") or os.path.basename(path)
        if data.get("truncado"):
            truncados.append(f"{os.path.basename(path)} ({len(fichas)} fichas extraídas)")
        novos = atualizados = 0
        for cod, r in fichas.items():
            cod = str(cod).strip()
            if not re.fullmatch(r"\d{6,8}", cod):
                problemas.append(f"{os.path.basename(path)}: código estranho '{cod}'")
                continue
            if not isinstance(r, dict):
                continue
            r.setdefault("caderno", cad)
            if cod in merged["regras"]:
                atualizados += 1
            else:
                novos += 1
            merged["regras"][cod] = {
                "d": r.get("d"), "u": (r.get("u") or "").lower(), "caderno": r.get("caderno"),
                "atualizacao": r.get("atualizacao") or "",
                "aplicacao": r.get("aplicacao"), "incluidos": r.get("incluidos"),
                "criterio": r.get("criterio"), "normas": r.get("normas") or None,
            }
        if cad not in merged["meta"]["cadernos"]:
            merged["meta"]["cadernos"].append(cad)
        sem_crit = sum(1 for r in fichas.values() if isinstance(r, dict) and not r.get("criterio"))
        print(f"{os.path.basename(path)}: {len(fichas)} fichas ({novos} novas, {atualizados} atualizadas)"
              + (f", {sem_crit} sem critério" if sem_crit else ""))

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)

    # validação cruzada com a base de preços
    with open(args.base, encoding="utf-8") as f:
        base = json.load(f)
    precos = {s["c"] for s in base["servicos"]}
    regras = set(merged["regras"])
    sem_preco = sorted(regras - precos)
    caps_regras = {c[:2] for c in regras}
    caps_base = {s["c"][:2] for s in base["servicos"]}
    print("\n===== RESUMO =====")
    print(f"regras totais: {len(regras)} | serviços na base: {len(precos)}")
    print(f"serviços da base COM regra de caderno: {len(regras & precos)} ({len(regras & precos)/len(precos)*100:.0f}%)")
    print(f"códigos de caderno SEM preço na base (tabela evoluiu): {len(sem_preco)}")
    if sem_preco[:15]:
        print("  ex.:", ", ".join(sem_preco[:15]))
    print(f"capítulos com regras: {sorted(caps_regras)}")
    print(f"capítulos da base SEM nenhuma regra: {sorted(caps_base - caps_regras)}")
    if truncados:
        print("TRUNCADOS (reprocessar):", truncados)
    if problemas:
        print("PROBLEMAS:", problemas[:20])


if __name__ == "__main__":
    main()
