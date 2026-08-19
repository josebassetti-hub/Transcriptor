#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GTK v4 — portfólio ampliado: 9 blocos (vedação/estrutural/canaleta em 9, 14 e 19) + paver 6 e 8 cm.

Deriva, com memória aberta:
  1. capacidade por SKU (peças/turno) a partir da tabela da proposta Gervasi REV00;
  2. cesta de produtos por tipo de obra (física da alvenaria: 12,5 blocos/m², cinta a cada 13 fiadas);
  3. mix de receita = cesta x preço, dentro da divisão já auditada 45% vedação / 30% estrutural / 25% paver;
  4. escala única até o teto de EPP (LC 123/2006) de R$ 4.800.000, adotando R$ 4.791.000;
  5. custo variável por SKU a partir do volume de concreto e do teor de cimento (base auditada do bloco 14).
Nada aqui é percentual arbitrado: cada número sai de uma conta que o analista pode refazer.
"""

# ────────────────────────── 1. capacidade (proposta Gervasi REV00, 12/05/2026) ──────────────────────────
# bandeja 700x550 (útil 630x520); 2.000 bandejas/turno de 8 h; fator de utilização 87,75% (da própria tabela)
BANDEJA = {"b14": 4, "b19": 3, "b9": 6}          # peças por bandeja (tabela da proposta)
TURNO_BANDEJAS = 2000
FATOR = 0.8775                                    # 7020 / (4 x 2000) — extraído da própria tabela
CAP_PAVER_H6 = 530.0                              # m²/turno (linha "Pavimento H6" da proposta)
FATOR_H8 = 0.88                                   # PREMISSA declarada: ciclo ~15% maior (33% mais concreto)
CAP_PAVER_H8 = round(CAP_PAVER_H6 * FATOR_H8)     # a substituir pelo dado oficial da Gervasi

def cap_bloco(fam):                               # canaleta usa a mesma pegada da bandeja do bloco irmão
    return round(BANDEJA[fam] * TURNO_BANDEJAS * FATOR)

# ────────────────────────── 2. geometria e concreto por peça ──────────────────────────
# volume de concreto (m³/peça) — bloco 14 é o valor auditado do estudo (5,4 m³/h ÷ 1.000 pç/h);
# os demais saem da geometria com as espessuras de parede da NBR 6136:2016 (25/32 mm classe A-B, 18 mm classe C)
# Como todos os moldes serão construídos na espessura estrutural (25 mm transversal, 32 mm longitudinal no
# bloco de 19), o bloco de vedação sai com a mesma geometria do estrutural — consome um pouco mais de concreto
# que um bloco de parede fina, e é esse o preço de não comprar dois jogos de moldes.
# Canaleta = fundo de 5 cm + duas paredes de 14 cm de altura (19 − 5), na espessura do bloco irmão.
VOL = {"b14v": 0.0054, "b14e": 0.0054, "can14": 0.0055,
       "b9v": 0.0043,  "b9e": 0.0043,  "can9": 0.0045,
       "b19v": 0.0065, "b19e": 0.0065, "can19": 0.0072,
       "pav6": 0.0620, "pav8": 0.0820}            # paver em m³ por m² (inclui 3% de junta)
# teor de cimento (kg/m³) por classe — vedação fbk 3-4; estrutural fbk 6-8; paver 35 e 50 MPa
CIM = {"b14v": 185, "b14e": 260, "can14": 260,
       "b9v": 185,  "b9e": 260,  "can9": 260,
       "b19v": 185, "b19e": 260, "can19": 260,
       "pav6": 330, "pav8": 400}

# ────────────────────────── 3. SKUs: descrição, unidade, preço e capacidade ──────────────────────────
# PREÇO DE VENDA POSTO-FÁBRICA = insumo SINAPI-ES 06/2026 (MATERIAL, sem serviço de assentamento) x 0,825.
# O fator de 0,825 (-17,5%) é o centro da faixa de 10 a 25% declarada no §6.4 e corresponde ao mix de canais
# do cap. 8 (balcão a preço cheio, revenda -25 a -35%, construtora/volume -10 a -20%).
# ATENÇÃO: usa-se o INSUMO, nunca a composição. Exemplo do erro que isso evita — paver 20x10 e=6 natural:
#   insumo 36155 = R$ 69,97/m² (só o material)  x  composição 92397 = R$ 89,91/m² (pavimento executado,
#   com areia, assentamento, compactação e mão de obra). A diferença não pode entrar num preço de fábrica.
SINAPI_ES = {                       # código: (preço do insumo, descrição da referência)
    "b14v":  (4.16,  "651 — bloco de vedação de concreto 14x19x39 (classe C)"),
    "b14e":  (5.05,  "34573 — bloco estrutural 14x19x39 fbk 8 MPa"),
    "can14": (5.35,  "38597 — canaleta estrutural 14x19x39 fbk 4,5 MPa"),
    "b9v":   (3.33,  "650 — bloco de vedação de concreto 9x19x39 (classe C)"),
    "b9e":   (3.30,  "25071 — bloco estrutural 9x19x39 fbk 4,5 MPa"),
    "can9":  (3.61,  "derivado: 38597 x (658/659) = 5,35 x 0,675 — não há insumo de canaleta 9x19x39"),
    "b19v":  (5.16,  "654 — bloco de vedação de concreto 19x19x39 (classe C)"),
    "b19e":  (6.63,  "34580 — bloco estrutural 19x19x39 fbk 8 MPa"),
    "can19": (6.41,  "derivado: 38597 x (660/659) = 5,35 x 1,198 — não há insumo de canaleta 19x19x39"),
    "pav6":  (69.97, "36155 — piso intertravado 20x10, e=6 cm, 35 MPa, cor natural"),
    "pav8":  (79.80, "36170 — piso intertravado 20x10, e=8 cm, 35 MPa, cor natural"),
}
DESCONTO_CANAL = 0.825
def preco(k): return round(SINAPI_ES[k][0] * DESCONTO_CANAL, 2)
# Ressalvas registradas: (i) o SINAPI-ES precifica o bloco estrutural de 9 praticamente igual ao de vedação
# (3,30 x 3,33) — o plano não assume prêmio de resistência nessa linha; (ii) não existe insumo de 8 cm/50 MPa
# na tabela do ES: adota-se o de 8 cm/35 MPa, o que é conservador (o prêmio de tráfego pesado fica como
# upside não computado); (iii) as canaletas de 9 e 19 em 39 cm não têm insumo e são derivadas pela razão
# entre as canaletas de 19 cm das mesmas larguras.
SKU = [
    # chave    descrição                                          un    preço        capacidade/turno
    ("b14v",  "Bloco de concreto 14x19x39 - vedação",             "UND", preco("b14v"),  cap_bloco("b14")),
    ("b14e",  "Bloco de concreto 14x19x39 - estrutural",          "UND", preco("b14e"),  cap_bloco("b14")),
    ("can14", "Canaleta de concreto 14x19x39",                    "UND", preco("can14"), cap_bloco("b14")),
    ("b9v",   "Bloco de concreto 9x19x39 - vedação",              "UND", preco("b9v"),   cap_bloco("b9")),
    ("b9e",   "Bloco de concreto 9x19x39 - estrutural",           "UND", preco("b9e"),   cap_bloco("b9")),
    ("can9",  "Canaleta de concreto 9x19x39",                     "UND", preco("can9"),  cap_bloco("b9")),
    ("b19v",  "Bloco de concreto 19x19x39 - vedação",             "UND", preco("b19v"),  cap_bloco("b19")),
    ("b19e",  "Bloco de concreto 19x19x39 - estrutural",          "UND", preco("b19e"),  cap_bloco("b19")),
    ("can19", "Canaleta de concreto 19x19x39",                    "UND", preco("can19"), cap_bloco("b19")),
    ("pav6",  "Piso intertravado (paver) 6 cm - 35 MPa",          "M2",  preco("pav6"),  CAP_PAVER_H6),
    ("pav8",  "Piso intertravado (paver) 8 cm - 50 MPa",          "M2",  preco("pav8"),  CAP_PAVER_H8),
]
for _k, *_ in SKU:
    assert preco(_k) < SINAPI_ES[_k][0], f"preço de venda de {_k} não pode superar o insumo SINAPI"
PV  = {k: pv for k, _, _, pv, _ in SKU}
CAP = {k: c for k, _, _, _, c in SKU}
DESC = {k: d for k, d, _, _, _ in SKU}
UN  = {k: u for k, _, u, _, _ in SKU}

# ────────────────────────── 4. cesta de produtos por tipo de obra (peças por 1.000) ──────────────────────────
# Obra de vedação: paredes externas em bloco 14, divisórias em bloco 9, canaleta só em verga/contraverga (~2,5%).
# Obra estrutural: cinta de amarração = 1 fiada a cada 13 (pé-direito 2,60 m ÷ 0,20 m) = 7,7%, + vergas ≈ 9,5%.
CESTA = {
    "vedacao":    {"b14v": 630, "b9v": 330, "b19v": 15, "can14": 18, "can9": 7},
    "estrutural": {"b14e": 700, "b19e": 130, "b9e": 75, "can14": 70, "can19": 15, "can9": 10},
}
for nome, c in CESTA.items():
    assert sum(c.values()) == 1000, f"cesta {nome} deve somar 1.000 peças"

# Pavimentação: espessura definida pelo tráfego (NBR 9781 — 6 cm pedestre/veículo leve; 8 cm tráfego pesado)
PAV_CANAL = {"publica": 0.60, "privada": 0.40}          # peso dos canais na demanda de pavimento (cap. 8 do estudo)
PAV_ESPESSURA = {"publica": {"pav8": 0.85, "pav6": 0.15},   # ruas e calçamento rural x passeios da mesma obra
                 "privada": {"pav8": 0.25, "pav6": 0.75}}   # pátios/acessos de caminhão x calçadas e condomínios

# divisão de receita por bloco de mercado — mantida do estudo auditado (§5.4)
BLOCO_MERCADO = {"vedacao": 0.45, "estrutural": 0.30, "paver": 0.25}

# ────────────────────────── 5. mix de receita derivado ──────────────────────────
def mix_receita():
    """% da receita de cada SKU, derivada das cestas e dos preços."""
    share = {k: 0.0 for k, *_ in SKU}
    for bloco in ("vedacao", "estrutural"):
        cesta = CESTA[bloco]
        rec = {k: q * PV[k] for k, q in cesta.items()}
        tot = sum(rec.values())
        for k, v in rec.items():
            share[k] += BLOCO_MERCADO[bloco] * v / tot
    # paver: área por espessura -> receita por espessura
    area = {"pav6": 0.0, "pav8": 0.0}
    for canal, peso in PAV_CANAL.items():
        for esp, f in PAV_ESPESSURA[canal].items():
            area[esp] += peso * f
    rec_pav = {k: area[k] * PV[k] for k in area}
    tot_pav = sum(rec_pav.values())
    for k, v in rec_pav.items():
        share[k] += BLOCO_MERCADO["paver"] * v / tot_pav
    return share, area

SHARE, AREA_PAV = mix_receita()
assert abs(sum(SHARE.values()) - 1) < 1e-9

# ────────────────────────── 6. escala até o teto de EPP ──────────────────────────
TETO_EPP = 4_800_000.0
RECEITA_REGIME = 4_791_000.0                       # margem de folga de R$ 9.000 para o teto
REC = {1: 2_750_000.0, 2: 3_850_000.0, 3: RECEITA_REGIME}

def receita_sku(total): return {k: total * SHARE[k] for k in SHARE}
def qtd_sku(total):     return {k: receita_sku(total)[k] / PV[k] for k in SHARE}
def dias_sku(total):    return {k: qtd_sku(total)[k] / CAP[k] for k in SHARE}

# ────────────────────────── 7. cascata de OEE (dias efetivos/ano, 1 turno) ──────────────────────────
OEE = [("Dias úteis do calendário nacional", 252),
       ("(-) Feriados municipais de São Mateus e ponto facultativo", -3),
       ("(-) Manutenção preventiva programada", -16),
       ("(-) Trocas de molde do mix (≈10/mês x 20 min, 8 moldes)", -5),
       ("(-) Parada anual de revisão (dezembro)", -3),
       ("(-) Paradas não programadas (6%)", -14),
       ("(-) Perda por refugo/quebra (2%)", -4)]
DIAS_EFETIVOS = sum(v for _, v in OEE)

# ────────────────────────── 8. custo variável industrial por SKU ──────────────────────────
# base auditada (bloco 14 vedação = R$ 1,85): cimento R$ 0,55/kg; agregados R$ 165/m³; aditivo R$ 0,04/kg de
# cimento; energia R$ 0,04 por peça de 4 por bandeja; MO direta R$ 1.454/dia; manutenção+diesel R$ 22,2/m³.
P_CIM, P_AGREG, P_ADIT, MO_DIA, MANUT_M3 = 0.55, 165.0, 0.04, 1454.0, 22.2
ENERGIA_BANDEJA = 0.16                              # R$ 0,04 x 4 peças

def pecas_por_bandeja(k):
    if k.startswith("pav"): return 0.3              # m² por bandeja
    fam = "b14" if "14" in k else ("b9" if "9" in k else "b19")
    return BANDEJA[fam]

def custo_variavel(k):
    cim_kg = VOL[k] * CIM[k]
    c_cim   = cim_kg * P_CIM
    c_agreg = VOL[k] * P_AGREG
    c_adit  = cim_kg * P_ADIT
    c_ener  = ENERGIA_BANDEJA / pecas_por_bandeja(k)
    c_mo    = MO_DIA / CAP[k]
    c_manut = VOL[k] * MANUT_M3
    return dict(cimento=c_cim, agregados=c_agreg, aditivo=c_adit, energia=c_ener,
                mo=c_mo, manutencao=c_manut, total=c_cim + c_agreg + c_adit + c_ener + c_mo + c_manut)

TRIB, FRETE = 0.15, 0.045                           # DAS no topo da faixa + frete médio (premissas do estudo)
def margem_contribuicao(k):
    cv = custo_variavel(k)["total"]
    mc = PV[k] * (1 - TRIB - FRETE) - cv
    return mc, mc / PV[k]

# ────────────────────────── 9. relatório de conferência ──────────────────────────
if __name__ == "__main__":
    def br(v, d=2): return f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    print("=" * 118)
    print("CAPACIDADE E MIX — GTK v4 (11 SKUs)".center(118))
    print("=" * 118)
    print(f"{'SKU':<42} {'un':>4} {'preço':>8} {'cap/turno':>10} {'% receita':>10} "
          f"{'receita R$':>14} {'quantidade':>12} {'dias':>6}")
    r, q, d = receita_sku(REC[3]), qtd_sku(REC[3]), dias_sku(REC[3])
    for k, desc, un, pv, cap in SKU:
        print(f"{desc:<42} {un:>4} {br(pv):>8} {br(cap,0):>10} {br(SHARE[k]*100):>9}% "
              f"{br(r[k],0):>14} {br(q[k],0):>12} {d[k]:>6.1f}")
    print("-" * 118)
    print(f"{'TOTAL':<42} {'':>4} {'':>8} {'':>10} {br(sum(SHARE.values())*100):>9}% "
          f"{br(sum(r.values()),0):>14} {'':>12} {sum(d.values()):>6.1f}")
    print(f"\nCascata de OEE:")
    for nome, v in OEE: print(f"   {nome:<62} {v:>+5}")
    print(f"   {'= DIAS EFETIVOS POR ANO (1 turno)':<62} {DIAS_EFETIVOS:>5}")
    print(f"\nUtilização no regime: {sum(d.values()):.1f} de {DIAS_EFETIVOS} dias = "
          f"{sum(d.values())/DIAS_EFETIVOS*100:.1f}%   |   receita máxima da planta: "
          f"R$ {br(REC[3]/sum(d.values())*DIAS_EFETIVOS,0)}")
    print(f"\nPaver — área por espessura: 6 cm {AREA_PAV['pav6']*100:.0f}% e 8 cm {AREA_PAV['pav8']*100:.0f}%; "
          f"em receita: 6 cm {SHARE['pav6']/(SHARE['pav6']+SHARE['pav8'])*100:.1f}% e "
          f"8 cm {SHARE['pav8']/(SHARE['pav6']+SHARE['pav8'])*100:.1f}%")
    print("\n" + "=" * 118)
    print(f"{'CUSTO VARIÁVEL E MARGEM DE CONTRIBUIÇÃO':^118}")
    print("=" * 118)
    print(f"{'SKU':<42} {'cimento':>8} {'agreg.':>8} {'energia':>8} {'MO':>8} {'manut.':>8} "
          f"{'CV total':>9} {'MC R$':>9} {'MC %':>7}")
    mc_pond = 0.0
    for k, desc, un, pv, cap in SKU:
        c = custo_variavel(k); mc, pct = margem_contribuicao(k)
        mc_pond += SHARE[k] * pct
        print(f"{desc:<42} {br(c['cimento']):>8} {br(c['agregados']):>8} {br(c['energia']):>8} "
              f"{br(c['mo']):>8} {br(c['manutencao']):>8} {br(c['total']):>9} {br(mc):>9} {br(pct*100,1):>6}%")
    print("-" * 118)
    print(f"Margem de contribuição média ponderada pelo mix: {br(mc_pond*100,1)}%")
    print(f"Custo variável industrial médio: {br((1-TRIB-FRETE-mc_pond)*100,1)}% da receita")
