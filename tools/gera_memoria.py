#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os dados da Memória de Cálculo de Quantitativos a partir da entrada do motor.

Cruza cada item do orçamento com a derivação declarada no bloco `memoria` da entrada
({grupos: {...}, codigos: {...}}, cada valor = [classe, texto]). Itens sem derivação
declarada usam a fórmula do próprio motor (classe C, ou D nos grupos de estrutura
paramétrica). Saída: JSON consumido por tools/memoria_docx.js.

Uso:  python3 tools/gera_memoria.py entrada.json [--refs data] [--out memoria-data.json]
"""
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',
                                '.claude', 'skills', 'orcamentista-der-es', 'scripts'))
import motor_orcamento as M

argv = [a for a in sys.argv[1:] if not a.startswith('--')]
refs = sys.argv[sys.argv.index('--refs') + 1] if '--refs' in sys.argv else None
out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'memoria-data.json'
src = argv[0]

refs = M.find_refs(refs)
base, mapa, ind, reg = M.load_refs(refs)
ent = json.load(open(src, encoding='utf-8'))
S = M.def_state()
S['obra'].update(ent.get('obra', {}))
if ent.get('ambientes'): S['ambientes'] = ent['ambientes']
S['med'].update(ent.get('med') or {})
S['ov'] = ent.get('ov', {}); S['extras'] = ent.get('extras', [])
S['par'] = ent.get('par', {}); S['precos'] = ent.get('precos', {})
S['sinapi'] = ent.get('sinapi', []); S['complemento'] = ent.get('complemento', [])
S['substituicoes'] = ent.get('substituicoes', [])
m = M.Motor(S, base, mapa, ind, reg)
ctx, rows = m.calc_itens(); T = m.totais(rows)
oj = m.orcamento_json(ctx, rows, T)

MEM_G = (ent.get('memoria') or {}).get('grupos', {})
MEM_C = (ent.get('memoria') or {}).get('codigos', {})
REGN = reg.get('regras', {})
ESTRUT = {'escavacao_fund', 'fund_concreto', 'fund_forma', 'fund_armadura',
          'imperm_baldrame', 'super_concreto', 'super_forma', 'super_armadura'}

def item_mem(r):
    """(classe, texto) da memória de um item do motor."""
    if r['grupo'] in MEM_G:
        cl, tx = MEM_G[r['grupo']]
    elif r['manual'] and r['c'] in MEM_C:
        cl, tx = MEM_C[r['c']]
    elif r['grupo'] in ESTRUT:
        cl, tx = 'D', r['f'] + ' — índice paramétrico do perfil estrutural (±20%; sem projeto estrutural).'
    else:
        cl, tx = 'C', r['f']
    crit = (REGN.get(r['c']) or {}).get('criterio')
    return cl, tx, (crit or '')

secoes = {}
for r in rows:
    cl, tx, crit = item_mem(r)
    cap = r['cap']
    secoes.setdefault(cap, []).append({
        'c': r['c'], 'd': r['d'], 'qtd': r['qtd'], 'u': r['u'],
        'mem': tx, 'classe': cl, 'criterio': crit[:220]})
sin_itens = []
for it in oj.get('itens_sinapi', {}).get('itens', []):
    cl, tx = MEM_C.get(it['c'], ('F', it.get('obs', '')))
    sin_itens.append({'c': it['c'], 'd': it['d'], 'qtd': it['qtd'], 'u': it['u'],
                      'mem': tx, 'classe': cl, 'criterio': ''})

st = ctx['st']
data = {
  'obra': oj['obra'],
  'totais': oj['totais'],
  'sinapi_tot': oj.get('itens_sinapi', {}),
  'ambientes': S['ambientes'],
  'geometria': [
    ['Área construída declarada', f"{ctx['areaConstr']:.2f} m²", 'Carimbo/quadro de áreas do projeto executivo v02 (A)'],
    ['Pavimentos', str(ctx['pav']), 'Pranchas (A)'],
    ['Projeção por pavimento (footprint)', f"{ctx['footprint']:.2f} m²", 'Área construída ÷ nº de pavimentos (C)'],
    ['Soma das áreas úteis (17 ambientes)', f"{st['area']:.2f} m²", 'Quadro de ambientes medido na planta (A)'],
    ['Pé-direito', f"{ctx['pd']:.2f} m", 'Cortes do projeto (A)'],
    ['Perímetro externo', f"{ctx['perExt']:.2f} m", 'Planta baixa (A)'],
    ['Σ perímetros dos ambientes', f"{st['per']:.2f} m", 'Quadro de ambientes (A)'],
    ['Comprimento de paredes', f"{ctx['paredesLen']:.1f} m", '(Σ perímetros 493,70 + per. externo 135,00) ÷ 2 — cada parede separa 2 ambientes (C)'],
    ['Área bruta de paredes', f"{ctx['paredesM2']:.1f} m²", '314,40 m × pé-direito 4,70 m; vãos ≤ 2 m² não descontados (critério de medição) (C)'],
    ['Dist. medidor → quadro geral', f"{ctx['distQM']:.0f} m", 'Planta de situação (A)'],
    ['Dist. última caixa → rede de esgoto', f"{ctx['distEsgExt']:.0f} m", 'Planta de situação (A)'],
  ],
  'secoes': [{'cap': c, 'nome': base['capitulos'].get(c, ''), 'itens': secoes[c]}
             for c in sorted(secoes)],
  'sinapi': sin_itens,
  'verificacoes': [
    'Fechamento dos pisos: 1.600,51 (porcelanato treino) + 150,00 (vinílico) + 135,28 (porcelanato 60×60) = 1.885,79 m² = área construída — fecha exatamente.',
    'Lajes: obra de 2 pavimentos ⇒ 1 laje de entrepiso (942,89 m² pela projeção) — presente; topo em telha metálica, sem laje de cobertura (conforme imagens 3D).',
    'Hidráulica por peça: 28 pontos de AF = 15 lav + 11 bacias + 1 pia + 1 tanque; esgoto secundário 17 = 15 lav + 1 pia + 1 tanque; primário 11 = bacias; ralos 10 = chuveiros; mictórios pelo ponto próprio 140714 — sem dupla contagem.',
    'Climatização: 624.000 BTU ÷ 1.827,3 m² internos = 342 BTU/m² — dentro da faixa típica de academia no ES (300–400).',
    'Estrutura metálica da cobertura: (8.040 + 6.030) kg ÷ 1.005 m² = 14 kg/m² × R$ 12–13/kg ≈ R$ 178/m² — faixa de cobertura apoiada em pórtico (R$ 150–250/m²).',
    'Total geral R$ 4.973.643,43 (R$ 2.637,43/m²) — reproduzido pelo autoteste dourado do motor (16 checagens).',
  ],
  'apontamentos': [
    'PINTURA DO FORRO: os 2.100 m² de tinta cobrem as paredes; a pintura do forro de gesso (300 m²) não está explícita — acrescentar ~300 m² se o forro for pintado (impacto ≈ R$ 10 mil c/ BDI).',
    'ALIMENTADOR: lançado com o cabo do grupo padrão (10 mm²); com carga > 75 kW o projeto elétrico exigirá bitola maior — requantificar no projeto executivo de elétrica.',
    'HI-WALLS: os 5 splits pequenos não têm ponto de força dedicado (alimentação pelos circuitos de tomadas); se o projeto elétrico exigir ponto dedicado, acrescentar 5 × item 151806.',
    'ESCADA INTERNA: o take-off não tem ambiente de circulação vertical e a única escada orçada é a externa — se as pranchas previrem escada interna, acrescentar o concreto dela e descontar o vazio na laje de entrepiso.',
    'VÃO E SOBRECARGA DA LAJE: a DER-ES 040602 vence 3,5–4,3 m com 300 kg/m² (NBR 6120 p/ academia); vãos maiores entre pilares ou área de peso livre exigem laje maciça/nervurada e sobrecarga 400–500 kg/m² — validar com o projetista estrutural.',
  ],
  'premissas': oj['premissas'], 'lacunas': oj['lacunas'],
  'substituicoes': oj.get('substituicoes'),
}
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
n = sum(len(s['itens']) for s in data['secoes'])
print(f"{out}: {n} itens DER-ES em {len(data['secoes'])} capítulos + {len(sin_itens)} SINAPI")
from collections import Counter
cls = Counter(i['classe'] for s in data['secoes'] for i in s['itens'])
cls.update(i['classe'] for i in sin_itens)
print("classes:", dict(sorted(cls.items())))
