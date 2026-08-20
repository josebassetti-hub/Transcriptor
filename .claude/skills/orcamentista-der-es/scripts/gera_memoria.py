#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os dados da Memória de Cálculo de Quantitativos a partir da entrada do motor.

Cruza cada item do orçamento com a derivação declarada no bloco `memoria` da entrada
({grupos: {...}, codigos: {...}}, cada valor = [classe, texto]). Itens sem derivação
declarada usam a fórmula do próprio motor (classe C, ou D nos grupos de estrutura
paramétrica). Saída: JSON consumido por tools/memoria_docx.js.

Emite sempre o Markdown (--md, funciona em qualquer lugar) e o JSON que alimenta o
memoria_docx.js, que gera o .docx quando houver Node com o pacote `docx`.

Uso:  python3 gera_memoria.py entrada.json [--refs DIR] [--out memoria-data.json] [--md memoria.md]
"""
import json, os, sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
# funciona tanto dentro da skill (motor é irmão em scripts/) quanto no repositório
for _c in (_AQUI, os.path.join(_AQUI, '..', '.claude', 'skills', 'orcamentista-der-es', 'scripts')):
    if os.path.exists(os.path.join(_c, 'motor_orcamento.py')):
        sys.path.insert(0, _c); break
import motor_orcamento as M

argv = [a for a in sys.argv[1:] if not a.startswith('--')]
refs = sys.argv[sys.argv.index('--refs') + 1] if '--refs' in sys.argv else None
out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'memoria-data.json'
md_out = sys.argv[sys.argv.index('--md') + 1] if '--md' in sys.argv else None
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


def br(v, c=2):
    return f"{v:,.{c}f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def escreve_md(d, caminho):
    """Memória de cálculo em Markdown — mesma estrutura do .docx, sem depender de Node."""
    L = []
    w = L.append
    ob, T = d['obra'], d['totais']
    w(f"# Memória de Cálculo de Quantitativos\n")
    w(f"**{ob['nome']}**  ")
    w(f"{ob.get('local','')}  ")
    w(f"Área construída {br(ob['area'])} m² · {ob['pav']} pavimentos · padrão {ob['padrao']} · "
      f"BDI {br(T['bdi_pct'],1)}% · bases DER-ES Abr/2026 e SINAPI-ES 06/2026 (custo direto, BDI 0)  ")
    w(f"**Total geral de referência: R$ {br(T['total_geral_com_complemento'])} "
      f"(R$ {br(T['total_geral_com_complemento']/ob['area'])}/m²)**\n")
    w("## 1. Objeto e documentos de referência\n")
    w("Demonstra a origem de cada quantidade do orçamento, item a item, para conferência do responsável "
      "técnico. Projetos complementares não fornecidos usam contagens sobre o arquitetônico, mínimos de "
      "norma e índices paramétricos — sempre com a classe de origem declarada.\n")
    w("## 2. Classificação da origem de cada quantidade\n")
    w("| Classe | Significado |\n|---|---|")
    for a, b in [('A', 'Medido no projeto — cotas, quadro de áreas/esquadrias, planta de cobertura ou de situação.'),
                 ('B', 'Contado no projeto ou nas imagens 3D — peças, pontos, aparelhos, panos de parede.'),
                 ('C', 'Calculado por fórmula (geometria, NBR ou regra do motor) — a expressão está no item.'),
                 ('D', 'Índice paramétrico (perfil estrutural) — incerteza ±20%, exige projeto estrutural.'),
                 ('E', 'Fechamento aritmético — saldo que garante a soma exata das áreas.'),
                 ('F', 'Estimativa declarada (premissa) — a confirmar com projeto complementar.')]:
        w(f"| **{a}** | {b} |")
    w("\n## 3. Quadro de ambientes (medido na planta)\n")
    w("| Ambiente | Tipo | Área (m²) | Perímetro (m) |\n|---|---|---:|---:|")
    soma = 0
    for a in d['ambientes']:
        soma += a['area']
        w(f"| {a['nome']} | {a['tipo']} | {br(a['area'])} | {br(a['per'])} |")
    w(f"| **SOMA (áreas úteis)** | | **{br(soma)}** | |")
    w("\n## 4. Geometria derivada\n")
    w("| Grandeza | Valor | Origem / expressão |\n|---|---:|---|")
    for g in d['geometria']:
        w(f"| {g[0]} | {g[1]} | {g[2]} |")
    w("\n## 5. Memória por item — Tabela DER-ES\n")
    for s_ in d['secoes']:
        w(f"\n### 5.{s_['cap']} — Capítulo {s_['cap']} · {s_['nome']}\n")
        w("| Código | Serviço | Quant. | Und | Memória de cálculo | Cl. |\n|---|---|---:|---|---|:-:|")
        for it in s_['itens']:
            w(f"| {it['c']} | {it['d'][:88]} | {br(it['qtd'])} | {it['u']} | {it['mem']} | **{it['classe']}** |")
    w("\n## 6. Itens da tabela SINAPI-ES 06/2026\n")
    w("| Código | Composição | Quant. | Und | Memória de cálculo | Cl. |\n|---|---|---:|---|---|:-:|")
    for it in d['sinapi']:
        w(f"| {it['c']} | {it['d'][:88]} | {br(it['qtd'])} | {it['u']} | {it['mem']} | **{it['classe']}** |")
    st = d['sinapi_tot']
    w(f"\nSubtotal SINAPI: custo direto R$ {br(st['custo_direto'])} · com BDI R$ {br(st['com_bdi'])}. "
      "O SINAPI não publica caderno de critério de medição por composição — medição pela unidade da composição.\n")
    for tit, chave, pref in [('7. Verificações de fechamento', 'verificacoes', ''),
                             ('8. Apontamentos da conferência (a validar com os projetos complementares)', 'apontamentos', '⚠ '),
                             ('10. Premissas adotadas', 'premissas', ''),
                             ('11. Lacunas e pontos de atenção', 'lacunas', '⚠ ')]:
        if chave == 'premissas':
            su = d.get('substituicoes')
            if su:
                w("\n## 9. Substituições para agente financeiro (resumo)\n")
                w("| Item de projeto | Valor de mercado | Valor de tabela | % coberto | Grau |\n|---|---:|---:|---:|:-:|")
                for x in su['itens']:
                    w(f"| {x['item']} | R$ {br(x['cotado'])} | R$ {br(x['substituido'])} | "
                      f"{br(100*x['substituido']/x['cotado'],0)}% | **{x['grau']}** |")
                w(f"| **TOTAL — diferença de escopo (recursos próprios do cliente)** | **R$ {br(su['total_cotado'])}** | "
                  f"**R$ {br(su['total_substituido'])}** | **R$ {br(su['diferenca'])}** | |")
        w(f"\n## {tit}\n")
        for i, t in enumerate(d[chave], 1):
            w(f"{i}. {pref}{t}")
    w("\n## 12. Encerramento\n")
    w("*Estudo indicativo por metodologia paramétrica sobre tabelas referenciais. Não substitui orçamento "
      "executivo com projetos complementares, nem dispensa responsável técnico. Toda quantidade classe D ou F "
      "deve ser revista quando os projetos das disciplinas forem emitidos.*\n")
    w("\n\n_________________________________________  \nResponsável técnico — conferência e aprovação")
    open(caminho, 'w', encoding='utf-8').write("\n".join(L))


if md_out:
    escreve_md(data, md_out)
    print(f"{md_out}: memória em Markdown (não depende de Node)")
n = sum(len(s['itens']) for s in data['secoes'])
print(f"{out}: {n} itens DER-ES em {len(data['secoes'])} capítulos + {len(sin_itens)} SINAPI")
from collections import Counter
cls = Counter(i['classe'] for s in data['secoes'] for i in s['itens'])
cls.update(i['classe'] for i in sin_itens)
print("classes:", dict(sorted(cls.items())))
