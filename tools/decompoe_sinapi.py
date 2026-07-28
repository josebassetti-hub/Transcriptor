#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decompõe composições do SINAPI que não têm preço publicado na UF.

Algumas composições do SINAPI (pele de vidro, brises, fachada com placas insertadas…) são
publicadas com a estrutura completa — coeficientes de mão de obra e de material — mas SEM custo,
porque o IBGE não pesquisa o preço dos materiais específicos. A aba `Analítico` do
SINAPI_Referência traz esses coeficientes e marca cada item como COM PREÇO / SEM PREÇO.

Este script lê o Analítico, e para cada composição pedida separa:
  · a parcela que TEM preço na UF (mão de obra e insumos pesquisados) → custo oficial
  · a parcela SEM preço → lista exata do que precisa ser cotado, com o coeficiente

Assim uma cotação "R$ X/m² no chute" vira "R$ Y/m² de mão de obra oficial + N materiais a cotar".

Uso:  python3 tools/decompoe_sinapi.py <SINAPI_Referencia.xlsx> <cod> [<cod> …]
                                       [--uf ES] [--base data/base-sinapi-es.json] [--json saida.json]
"""
import json, sys
import openpyxl

FLAGS = {'--uf': 'ES', '--base': 'data/base-sinapi-es.json', '--json': None}
argv, i = [], 1
while i < len(sys.argv):
    a = sys.argv[i]
    if a in FLAGS:                      # consome a flag E o valor dela
        FLAGS[a] = sys.argv[i + 1]; i += 2
    else:
        argv.append(a); i += 1
uf = FLAGS['--uf'].upper(); basef = FLAGS['--base']; saida = FLAGS['--json']
src, alvos = argv[0], set(argv[1:])

base = json.load(open(basef, encoding='utf-8'))
PRECO = {c['c']: c for c in base['composicoes']}
PRECO_INS = {i['c']: i for i in base['insumos']}

wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
ws = wb['Analítico']
comp = {}
for row in ws.iter_rows(min_row=11, values_only=True):
    cod = str(row[1] or '').strip()
    if cod not in alvos:
        continue
    d = comp.setdefault(cod, {"descricao": "", "unidade": "", "itens": []})
    if not row[2]:                                   # linha-título da composição
        d["descricao"] = str(row[4] or '').strip()
        d["unidade"] = str(row[5] or '').strip()
        continue
    d["itens"].append({"tipo": str(row[2]).strip(), "c": str(row[3] or '').strip(),
                       "d": str(row[4] or '').strip(), "u": str(row[5] or '').strip(),
                       "coef": float(row[6] or 0), "situacao": str(row[7] or '').strip()})
wb.close()

out = {}
for cod in sorted(alvos):
    d = comp.get(cod)
    if not d:
        print(f"\n{cod}: não encontrado no Analítico"); continue
    com, sem = [], []
    for it in d['itens']:
        fonte = PRECO.get(it['c']) if it['tipo'] == 'COMPOSICAO' else PRECO_INS.get(it['c'])
        if fonte and fonte['p']:
            it = dict(it, pu=fonte['p'], total=round(it['coef'] * fonte['p'], 2))
            com.append(it)
        else:
            sem.append(it)
    parcial = round(sum(i['total'] for i in com), 2)
    out[cod] = {"descricao": d['descricao'], "unidade": d['unidade'],
                "custo_com_preco": parcial, "com_preco": com, "sem_preco": sem}
    print(f"\n{'='*100}\n{cod}  [{d['unidade']}]  {d['descricao'][:78]}")
    print(f"  ── parcela COM preço em {uf}: R$ {parcial:,.2f}".replace(',', '.'))
    for i in com:
        print(f"     {i['c']:>7} {i['d'][:52]:54} {i['coef']:>9.4f} {i['u']:>3} × R$ {i['pu']:>8,.2f} = R$ {i['total']:>9,.2f}".replace(',', '.'))
    print(f"  ── SEM preço ({len(sem)}) — a cotar:")
    for i in sem:
        print(f"     {i['c']:>7} {i['d'][:52]:54} {i['coef']:>9.4f} {i['u']:>3}   [{i['situacao']}]")

if saida:
    json.dump(out, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"\n→ {saida}")
