#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
motor_orcamento.py — motor determinístico do Orçamentista DER-ES (port fiel do motor
JavaScript do orcamentista.html; mesma entrada ⇒ mesmos números do app).

Uso:
  python3 motor_orcamento.py entrada.json [--out orcamento.json] [--csv planilha.csv] [--refs DIR]
  python3 motor_orcamento.py --autoteste          # reproduz o orçamento dourado (casa 70 m²)
  python3 motor_orcamento.py --exemplo > entrada.json   # imprime uma entrada de exemplo

entrada.json (mesmo estado do app):
{
 "obra": {"nome":"...", "local":"...", "area":70, "pav":1, "padrao":"popular|medio|alto",
          "bdi":25, "redeEsgoto":true, "incluirEstrutura":true, "temLaje":true, "perExt":0,
          "semEle":true, "semHid":true, "semEst":true},
 "ambientes": [{"nome":"Sala","tipo":"sala","area":16,"per":16.5,"distQ":3,"distP":0}, ...],
 "med": {"quadroMedidor":12, "esgotoExterno":8, "escalaNota":""},
 "ov": {}, "extras": [], "precos": {}, "par": {}
}
Tipos de ambiente: sala, quarto, cozinha, banheiro, lavabo, area_servico, circulacao,
varanda, garagem, escritorio, despensa, outro.

Saídas: resumo + planilha por capítulo no stdout; --out grava orcamento.json compatível
com o import do orcamentista.html; --csv grava planilha para Excel.
"""
import argparse, csv, io, json, math, os, sys

# ---------- localização das referências (data/ do repo ou references/ da skill) ----------
def find_refs(explicit=None):
    here = os.path.dirname(os.path.abspath(__file__))
    cands = ([explicit] if explicit else []) + [
        os.path.join(here, "..", "references"),
        os.path.join(here, "..", "..", "..", "..", "data"),  # repo: .claude/skills/x/scripts → data/
        "data", "references", ".",
    ]
    for c in cands:
        if c and os.path.exists(os.path.join(c, "base-der-es.json")):
            return os.path.abspath(c)
    sys.exit("referências não encontradas (base-der-es.json) — use --refs DIR")


def load_refs(refs):
    def rd(name, default=None):
        p = os.path.join(refs, name)
        if not os.path.exists(p):
            if default is not None:
                return default
            sys.exit(f"faltando {p}")
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    base = rd("base-der-es.json")
    mapa = rd("mapa-padroes.json")
    ind = rd("indices-estimativa.json")
    reg = rd("regras-medicao.json", {"regras": {}})

    # SINAPI é opcional: quando presente, permite orçar o que a DER-ES não cobre
    sin = rd("base-sinapi-es.json")
    if sin:
        base["_sinapi"] = sin
    return base, mapa, ind, reg


def jsround(v):        # Math.round do JS (meio para cima em positivos)
    return math.floor(v + 0.5)

def rnd1(v): return jsround(v * 10) / 10.0
def rnd2(v): return jsround(v * 100) / 100.0

def fmt(v):
    s = f"{v:,.2f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")

def fmt1(v):
    s = f"{v:,.1f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# ---------- estado padrão (idêntico ao defState()/demoAmbientes() do app) ----------
def demo_ambientes():
    return [
        {"nome": "Sala",            "tipo": "sala",         "area": 16,  "per": 16.5, "distQ": 3, "distP": 0},
        {"nome": "Cozinha",         "tipo": "cozinha",      "area": 9,   "per": 12,   "distQ": 2, "distP": 3},
        {"nome": "Quarto 1",        "tipo": "quarto",       "area": 12,  "per": 14,   "distQ": 6, "distP": 0},
        {"nome": "Quarto 2",        "tipo": "quarto",       "area": 9,   "per": 12,   "distQ": 9, "distP": 0},
        {"nome": "Banheiro",        "tipo": "banheiro",     "area": 3.5, "per": 7.6,  "distQ": 8, "distP": 1.5},
        {"nome": "Área de serviço", "tipo": "area_servico", "area": 4,   "per": 8.2,  "distQ": 4, "distP": 2},
        {"nome": "Circulação",      "tipo": "circulacao",   "area": 2.5, "per": 6.6,  "distQ": 5, "distP": 0},
    ]

def def_state():
    return {
        "obra": {"nome": "Residência exemplo 70 m²", "local": "Vitória - ES", "area": 70, "pav": 1,
                 "padrao": "medio", "bdi": 25, "redeEsgoto": True, "incluirEstrutura": True,
                 "temLaje": True, "perExt": 0, "semEle": True, "semHid": True, "semEst": True},
        "ambientes": demo_ambientes(),
        "med": {"quadroMedidor": 12, "esgotoExterno": 8, "escalaNota": ""},
        "ov": {}, "extras": [], "precos": {}, "par": {},
        "sinapi": [], "complemento": [], "substituicoes": [],
    }


class Motor:
    def __init__(self, S, base, mapa, ind, reg):
        self.S = S
        self.BASE, self.MAPA, self.IND, self.REG = base, mapa, ind, reg
        self.SVC = {s["c"]: s for s in base["servicos"]}
        self.CAPS = base.get("capitulos", {})
        self.P = ind["parametros"]; self.AMB = ind["ambientes"]
        self.CIRC = ind["circuitos"]
        # perfil estrutural: residencial (padrão) ou comercial — muda os índices paramétricos
        est = ind["estrutura_indices"]
        perfil = (S["obra"].get("perfilEstrutural") or "residencial").lower()
        self.perfilEst = perfil if perfil in est.get("perfis", {}) else "residencial"
        self.EST = {**est, **est.get("perfis", {}).get(self.perfilEst, {})}
        self.SIN = {c["c"]: c for c in (base.get("_sinapi") or {}).get("composicoes", [])}

    def par(self, k):
        v = self.S.get("par", {}).get(k)
        return float(v) if v not in (None, "") else self.P[k]

    # ---- ambStats (port fiel) ----
    def amb_stats(self):
        P = self.P
        a = dict(area=0.0, per=0.0, luz=0, int_=0, tug=0, chuveiros=0, bacias=0, lavatorios=0,
                 pias=0, tanques=0, ralos=0, registros=0, zonasMolhadas=0, ptAgua=0, ptEsgSec=0,
                 janelasM2=0.0, portasInt=0, cxGordura=0, rodape=0.0, molhadaM2=0.0,
                 distQextra=0.0, ramaisM=0.0, coletorM=0.0, nAmb=len(self.S["ambientes"]))
        for m in self.S["ambientes"]:
            t = self.AMB.get(m.get("tipo"), self.AMB["outro"])
            area = float(m.get("area") or 0)
            per = float(m.get("per") or 0) or (4 * math.sqrt(area))
            a["area"] += area; a["per"] += per
            a["luz"] += t["luz"]; a["int_"] += t["int"]
            a["tug"] += max(t["tug_min"], math.ceil(per / t["tug_por_perimetro"])) if t["tug_por_perimetro"] > 0 else t["tug_min"]
            a["chuveiros"] += t.get("chuveiro", 0); a["bacias"] += t.get("bacia", 0)
            a["lavatorios"] += t.get("lavatorio", 0); a["pias"] += t.get("pia", 0)
            a["tanques"] += t.get("tanque", 0); a["ralos"] += t.get("ralo", 0)
            a["registros"] += t.get("registro", 0)
            if t.get("cx_gordura"):
                a["cxGordura"] = 1
            if t.get("molhado"):
                a["zonasMolhadas"] += 1
                a["ramaisM"] += float(m.get("distP") or 0) or P["dist_default_ramal_hidraulico_m"]
            if m.get("tipo") in ("banheiro", "lavabo"):
                a["coletorM"] += float(m.get("distP") or 0) or 4
                a["molhadaM2"] += per * P["altura_revest_parede_molhada_m"]
            if m.get("tipo") in ("cozinha", "area_servico"):
                a["molhadaM2"] += min(per * 0.45, 6) * P["altura_meia_parede_cozinha_m"]
            if m.get("tipo") in ("sala", "quarto", "escritorio"):
                a["janelasM2"] += area / 6
            if m.get("tipo") in ("banheiro", "lavabo", "area_servico", "cozinha"):
                a["janelasM2"] += 1.2 if m.get("tipo") == "cozinha" else 0.6
            if m.get("tipo") in ("quarto", "banheiro", "lavabo", "escritorio", "despensa"):
                a["portasInt"] += 1
            if not t.get("molhado"):
                a["rodape"] += max(per - P["largura_porta_padrao_m"], 0)
            dq = float(m.get("distQ") or 0)
            if dq > P["raio_cobertura_ponto_eletrico_m"]:
                a["distQextra"] += dq - P["raio_cobertura_ponto_eletrico_m"]
        a["ptAgua"] = a["lavatorios"] + a["pias"] + a["tanques"] + a["bacias"]
        a["ptEsgSec"] = a["lavatorios"] + a["pias"] + a["tanques"]
        a["registros"] += 1
        return a

    # ---- buildCtx (port fiel) ----
    def build_ctx(self):
        S, P, CIRC = self.S, self.P, self.CIRC
        st = self.amb_stats()
        pd = self.par("pe_direito_m")
        area_constr = float(S["obra"].get("area") or 0) or rnd1(st["area"] * 1.25)
        pav = max(1, int(S["obra"].get("pav") or 1))
        footprint = area_constr / pav
        per_ext = float(S["obra"].get("perExt") or 0) or rnd1(4 * math.sqrt(footprint))
        paredes_len = rnd1((st["per"] + per_ext) / 2)
        paredes_m2 = rnd1(paredes_len * pd)
        n_colunas = max(1, math.ceil(st["zonasMolhadas"] / 2))
        circuitos = (math.ceil(st["area"] / CIRC["iluminacao_area_max_m2"])
                     + math.ceil(st["area"] / CIRC["tug_area_max_m2"])
                     + CIRC["circuito_dedicado_cozinha_as"] + st["chuveiros"] + CIRC["reserva"])
        vaos_verga = st["portasInt"] + 2 + jsround(st["janelasM2"] / 1.5)
        return dict(st=st, pd=pd, areaConstr=area_constr, pav=pav, footprint=footprint,
                    perExt=per_ext, paredesLen=paredes_len, paredesM2=paredes_m2,
                    nColunas=n_colunas, circuitos=circuitos,
                    vaosVerga=vaos_verga,
                    distQM=float(S["med"].get("quadroMedidor") or 0) or P["dist_default_quadro_medidor_m"],
                    distEsgExt=float(S["med"].get("esgotoExterno") or 0) or P["dist_default_esgoto_externo_m"])

    # ---- REGRAS (port fiel, mesmas fórmulas e arredondamentos) ----
    def regras(self):
        S, P, EST, CIRC, IND = self.S, self.P, self.EST, self.CIRC, self.IND
        def R(q, f): return {"q": q, "f": f}
        return {
            "area_construida": lambda c: R(c["areaConstr"], f"área construída {fmt1(c['areaConstr'])} m²"),
            "vol_escavacao_baldrame": (
                (lambda c: R(rnd2(c["footprint"] * EST["fundacao_escavacao_m3_por_m2"]), f"projeção {fmt1(c['footprint'])} m² × {EST['fundacao_escavacao_m3_por_m2']} m³/m² (cavas de sapata)"))
                if EST.get("base_fundacao") == "area" else
                (lambda c: R(rnd2(c["paredesLen"] * EST["baldrame_escavacao_m3_por_m"]), f"{fmt1(c['paredesLen'])} m de paredes × {EST['baldrame_escavacao_m3_por_m']} m³/m"))),
            "vol_concreto_fundacao": (
                (lambda c: R(rnd2(c["footprint"] * EST["fundacao_vol_m3_por_m2"]), f"projeção {fmt1(c['footprint'])} m² × {EST['fundacao_vol_m3_por_m2']} m³/m² (sapatas isoladas)"))
                if EST.get("base_fundacao") == "area" else
                (lambda c: R(rnd2(c["paredesLen"] * EST["baldrame_vol_m3_por_m"]), f"{fmt1(c['paredesLen'])} m × {EST['baldrame_vol_m3_por_m']} m³/m (baldrame)"))),
            "area_forma_fundacao": (
                (lambda c: R(rnd1(c["footprint"] * EST["fundacao_vol_m3_por_m2"] * EST["fundacao_forma_m2_por_m3"]), f"{fmt(c['footprint'] * EST['fundacao_vol_m3_por_m2'])} m³ × {EST['fundacao_forma_m2_por_m3']} m²/m³"))
                if EST.get("base_fundacao") == "area" else
                (lambda c: R(rnd1(c["paredesLen"] * EST["baldrame_forma_m2_por_m"]), f"{fmt1(c['paredesLen'])} m × {EST['baldrame_forma_m2_por_m']} m²/m"))),
            "peso_aco_fundacao": (
                (lambda c: R(rnd1(c["footprint"] * EST["fundacao_vol_m3_por_m2"] * EST["fundacao_aco_kg_por_m3"]), f"{fmt(c['footprint'] * EST['fundacao_vol_m3_por_m2'])} m³ × {EST['fundacao_aco_kg_por_m3']} kg/m³"))
                if EST.get("base_fundacao") == "area" else
                (lambda c: R(rnd1(c["paredesLen"] * EST["baldrame_vol_m3_por_m"] * EST["aco_kg_por_m3"]), f"{fmt(c['paredesLen'] * EST['baldrame_vol_m3_por_m'])} m³ × {EST['aco_kg_por_m3']} kg/m³"))),
            "peso_estrutura_metalica": lambda c: R(
                rnd1(c["footprint"] * P["fator_beiral_telhado"] * self.par("kg_estrutura_metalica_por_m2")) if S["obra"].get("coberturaMetalica") else 0,
                f"projeção horizontal {fmt1(c['footprint'])} m² × beiral {P['fator_beiral_telhado']} × {fmt(self.par('kg_estrutura_metalica_por_m2'))} kg/m² (DER 200738 é medido por PESO)"),
            "area_baldrame": lambda c: R(rnd1(c["paredesLen"] * 0.5), f"{fmt1(c['paredesLen'])} m × 0,5 m (2 faces+topo)"),
            "vol_concreto_super": lambda c: R(rnd2(c["areaConstr"] * EST["super_vol_m3_por_m2"]), f"{fmt1(c['areaConstr'])} m² × {EST['super_vol_m3_por_m2']} m³/m² (pilares/cintas)"),
            "area_forma_super": lambda c: R(rnd1(c["areaConstr"] * EST["super_vol_m3_por_m2"] * EST["forma_m2_por_m3"]), f"{fmt(c['areaConstr'] * EST['super_vol_m3_por_m2'])} m³ × {EST['forma_m2_por_m3']} m²/m³"),
            "peso_aco_super": lambda c: R(rnd1(c["areaConstr"] * EST["super_vol_m3_por_m2"] * EST["aco_kg_por_m3"]), f"{fmt(c['areaConstr'] * EST['super_vol_m3_por_m2'])} m³ × {EST['aco_kg_por_m3']} kg/m³"),
            "area_laje": lambda c: R(rnd1(c["st"]["area"]) if S["obra"].get("temLaje") else 0, f"área interna {fmt1(c['st']['area'])} m²" if S["obra"].get("temLaje") else "sem laje (premissa)"),
            "area_paredes_bruta": lambda c: R(c["paredesM2"], f"(Σper amb {fmt1(c['st']['per'])} + per ext {fmt1(c['perExt'])})/2 × pé-dir {c['pd']} m — vãos ≤2m² não descontados"),
            "comp_vergas": lambda c: R(rnd1(c["vaosVerga"] * (P["largura_porta_padrao_m"] + P["comp_verga_por_vao_m"])), f"{c['vaosVerga']} vãos × ({P['largura_porta_padrao_m']}+{P['comp_verga_por_vao_m']}) m"),
            "area_revestimento_total": lambda c: R(rnd1(c["paredesM2"] * 2), f"{fmt1(c['paredesM2'])} m² × 2 faces (chapisco)"),
            "area_revestimento_pintura": lambda c: R(rnd1(max(c["paredesM2"] * 2 - c["st"]["molhadaM2"], 0)), f"2 faces {fmt1(c['paredesM2'] * 2)} − azulejadas {fmt1(c['st']['molhadaM2'])} m²"),
            "area_parede_molhada": lambda c: R(rnd1(c["st"]["molhadaM2"]), f"banheiros: per×{P['altura_revest_parede_molhada_m']}m; coz/AS: bancada×{P['altura_meia_parede_cozinha_m']}m"),
            "area_forro": lambda c: R(0 if S["obra"]["padrao"] == "popular" else rnd1(c["st"]["area"]), "popular: sem forro (premissa)" if S["obra"]["padrao"] == "popular" else f"área interna {fmt1(c['st']['area'])} m²"),
            "area_piso_terreo": lambda c: R(rnd1(c["st"]["area"] / c["pav"]), f"área interna térreo {fmt1(c['st']['area'] / c['pav'])} m²"),
            "area_piso_total": lambda c: R(rnd1(c["st"]["area"]), f"área interna {fmt1(c['st']['area'])} m²"),
            "comp_rodape": lambda c: R(rnd1(c["st"]["rodape"]), "Σ perímetros secos − portas"),
            "comp_soleiras": lambda c: R(rnd1((c["st"]["zonasMolhadas"] + 2) * P["largura_porta_padrao_m"]), f"{c['st']['zonasMolhadas'] + 2} transições × {P['largura_porta_padrao_m']} m"),
            "comp_peitoril": lambda c: R(rnd1(c["st"]["janelasM2"] / 1.2), "Σ larguras de janelas (h média 1,2 m)"),
            "area_telhado": lambda c: R(rnd1(c["footprint"] * P["fator_beiral_telhado"]), f"projeção horizontal {fmt1(c['footprint'])} m² × beiral {P['fator_beiral_telhado']} (critério DER 0901/0902: inclinação embutida na composição)"),
            "qtd_portas_internas": lambda c: R(c["st"]["portasInt"], "contagem por ambiente (quartos, banheiros, etc.)"),
            "qtd_portas_todas": lambda c: R(c["st"]["portasInt"] + 2, f"{c['st']['portasInt']} internas + 2 externas"),
            "comp_alizar": lambda c: R(rnd1((c["st"]["portasInt"] + 2) * (2 * P["altura_porta_padrao_m"] + P["largura_porta_padrao_m"]) * 2), f"{c['st']['portasInt'] + 2} portas × {fmt1(2 * P['altura_porta_padrao_m'] + P['largura_porta_padrao_m'])} m × 2 faces"),
            "area_janelas": lambda c: R(rnd1(c["st"]["janelasM2"]), "1/6 do piso (permanência) + fixos banheiros/serviço"),
            "area_pintura_total": lambda c: (lambda forro: R(rnd1(max(c["paredesM2"] * 2 - c["st"]["molhadaM2"], 0) + forro), f"paredes pintáveis + forro {fmt1(forro)} m²"))(0 if S["obra"]["padrao"] == "popular" else c["st"]["area"]),
            "area_pintura_interna": lambda c: R(rnd1(max(c["paredesM2"] * 2 - c["st"]["molhadaM2"] - c["perExt"] * c["pd"], 0)), "faces internas pintáveis (p/ massa)"),
            "qtd_pt_agua": lambda c: R(c["st"]["ptAgua"], f"lavat {c['st']['lavatorios']} + pias {c['st']['pias']} + tanques {c['st']['tanques']} + bacias {c['st']['bacias']}"),
            "qtd_pt_chuveiro": lambda c: R(c["st"]["chuveiros"], f"{c['st']['chuveiros']} banheiro(s) com chuveiro"),
            "qtd_bacias": lambda c: R(c["st"]["bacias"], f"{c['st']['bacias']} bacia(s)"),
            "qtd_pt_esgoto_sec": lambda c: R(c["st"]["ptEsgSec"] + c["st"]["ralos"], f"peças secundárias {c['st']['ptEsgSec']} + ralos {c['st']['ralos']}"),
            "qtd_ralos": lambda c: R(c["st"]["ralos"], "1/banheiro + 1/área de serviço"),
            "comp_tubo_prumada": lambda c: R(rnd1(c["nColunas"] * (c["pd"] + 2) * 2), f"{c['nColunas']} coluna(s) × ({c['pd']}+2) m × 2"),
            "comp_tubo_ramal": lambda c: R(rnd1(c["st"]["ramaisM"] * P["fator_rota_hidraulica"]), f"Σ dist. prumada→ambiente {fmt1(c['st']['ramaisM'])} m × {P['fator_rota_hidraulica']}"),
            "comp_esgoto_coletor": lambda c: R(rnd1(c["st"]["coletorM"] * P["fator_rota_esgoto"]), f"Σ banheiro→caixa {fmt1(c['st']['coletorM'])} m × {P['fator_rota_esgoto']}"),
            "comp_esgoto_ramal": lambda c: R(rnd1((c["st"]["ptEsgSec"] + c["st"]["ralos"]) * IND["hidraulica"]["esgoto_ramal50_m_por_ponto_sec"]), f"{c['st']['ptEsgSec'] + c['st']['ralos']} pontos × {IND['hidraulica']['esgoto_ramal50_m_por_ponto_sec']} m"),
            "comp_esgoto_externo": lambda c: R(rnd1(c["distEsgExt"]), f"última caixa→rede/fossa {fmt1(c['distEsgExt'])} m (medido/premissa)"),
            "qtd_caixas_inspecao": lambda c: R(c["st"]["zonasMolhadas"] + math.ceil(c["distEsgExt"] / 12), f"{c['st']['zonasMolhadas']} zonas + 1/12m externo"),
            "qtd_caixa_gordura": lambda c: R(c["st"]["cxGordura"], "cozinha"),
            "qtd_fossa": lambda c: R(0 if S["obra"].get("redeEsgoto") else 1, "há rede pública" if S["obra"].get("redeEsgoto") else "sem rede pública: 1 conjunto"),
            "qtd_lavatorios": lambda c: R(c["st"]["lavatorios"], "banheiros + lavabos"),
            "qtd_pias_cozinha": lambda c: R(c["st"]["pias"], "cozinhas"),
            "qtd_tanques": lambda c: R(c["st"]["tanques"], "áreas de serviço"),
            "qtd_registros": lambda c: R(c["st"]["registros"], "1/amb molhado (banheiro 2) + 1 geral"),
            "qtd_pt_luz": lambda c: R(c["st"]["luz"], f"1 ponto de teto por ambiente ({c['st']['nAmb']} amb)"),
            "qtd_pt_tomada": lambda c: R(c["st"]["tug"], "NBR 5410: max(mín, per/passo) por ambiente"),
            "qtd_pt_interruptor": lambda c: R(c["st"]["int_"], "1 por ambiente (conjugado c/ tomada)"),
            "qtd_circuitos": lambda c: R(c["circuitos"], f"ilum ⌈{c['st']['area']:.0f}/75⌉ + TUG ⌈{c['st']['area']:.0f}/60⌉ + coz/AS + {c['st']['chuveiros']} chuv + reserva"),
            "comp_alimentador": lambda c: R(rnd1(3 * c["distQM"] * P["fator_rota_eletrica"]), f"3 × {fmt1(c['distQM'])} m × {P['fator_rota_eletrica']}"),
            "comp_alimentador_duto": lambda c: R(rnd1(c["distQM"] * P["fator_rota_eletrica"]), f"{fmt1(c['distQM'])} m × {P['fator_rota_eletrica']}"),
            "area_bancada_banheiro": lambda c: R(rnd2(0.6 * (c["st"]["bacias"] - sum(1 for m in S["ambientes"] if m.get("tipo") == "lavabo"))), "0,6 m² × banheiros"),
            "unitario": lambda c: R(1, "1 por obra"),
        }

    ESTRUTURA_GRUPOS = ["escavacao_fund", "fund_concreto", "fund_forma", "fund_armadura",
                        "imperm_baldrame", "super_concreto", "super_forma", "super_armadura", "laje"]

    def preco_de(self, c):
        s = self.SVC.get(c)
        if not s:
            return 0.0
        p = self.S.get("precos", {}).get(c)
        return float(p) if p is not None else s["p"]

    # ---- calcItens (port fiel, mesma ordem) ----
    def calc_itens(self):
        S = self.S
        c = self.build_ctx()
        REGRAS = self.regras()
        rows = []
        for g in self.MAPA["grupos"]:
            if g.get("condicional") == "sem_rede_esgoto" and S["obra"].get("redeEsgoto"):
                continue
            if g.get("condicional") == "cobertura_metalica" and not S["obra"].get("coberturaMetalica"):
                continue
            # com cobertura metálica, a estrutura de madeira sai de cena
            if g["id"] == "cobertura_estrutura" and S["obra"].get("coberturaMetalica"):
                continue
            if S["obra"].get("incluirEstrutura") is False and g["id"] in self.ESTRUTURA_GRUPOS:
                continue
            ov = S.get("ov", {}).get(g["id"], {})
            code = ov.get("c") if "c" in ov else g["itens"].get(S["obra"]["padrao"])
            if code in (None, ""):
                continue
            r = REGRAS[g["regra"]](c) if g["regra"] in REGRAS else {"q": 0, "f": "?"}
            qtd = float(ov["qtd"]) if ov.get("qtd") not in (None, "") else r["q"]
            if not qtd > 0:
                continue
            for cd in str(code).split("+"):
                s = self.SVC.get(cd)
                if not s:
                    continue
                rows.append({"grupo": g["id"], "nome": g["nome"], "c": cd, "d": s["d"], "u": s["u"],
                             "qtd": qtd, "pu": self.preco_de(cd),
                             "f": r["f"] + (" (ajustado manualmente)" if ov.get("qtd") not in (None, "") else ""),
                             "cap": cd[:2], "manual": False})
        # extras dinâmicos (cabo/eletroduto p/ ambientes afastados)
        if c["st"]["distQextra"] > 0:
            m = rnd1(c["st"]["distQextra"] * self.P["fator_rota_eletrica"])
            for grupo, nome, cd, qtd, f in [
                ("cabo_extra", "Cabo 2,5mm² extra (ambientes afastados do quadro)",
                 self.CIRC["cabo_por_bitola_codigo"]["2.5"], rnd1(m * 3),
                 f"3 × Σ(dist−{self.P['raio_cobertura_ponto_eletrico_m']}m) {fmt1(c['st']['distQextra'])} m × {self.P['fator_rota_eletrica']}"),
                ("duto_extra", "Eletroduto 3/4\" extra (idem)", "151126", m,
                 f"Σ(dist−{self.P['raio_cobertura_ponto_eletrico_m']}m) × {self.P['fator_rota_eletrica']}"),
            ]:
                s = self.SVC.get(cd)
                if s:
                    rows.append({"grupo": grupo, "nome": nome, "c": cd, "d": s["d"], "u": s["u"],
                                 "qtd": qtd, "pu": self.preco_de(cd), "f": f, "cap": cd[:2], "manual": False})
        for i, x in enumerate(S.get("extras", [])):
            s = self.SVC.get(x.get("c"))
            if not s or not float(x.get("qtd") or 0) > 0:
                continue
            rows.append({"grupo": f"extra{i}", "nome": "Item adicional", "c": x["c"], "d": s["d"], "u": s["u"],
                         "qtd": float(x["qtd"]), "pu": self.preco_de(x["c"]),
                         "f": x.get("obs") or "incluído manualmente", "cap": x["c"][:2], "manual": True})
        # anti-dupla-contagem: extra que repete código já gerado pelo mapa de padrões
        do_mapa = {r["c"] for r in rows if not r["manual"]}
        self.dup = sorted({r["c"] for r in rows if r["manual"] and r["c"] in do_mapa})
        for r in rows:
            r["total"] = r["qtd"] * r["pu"]
        return c, rows

    def totais(self, rows):
        cd = sum(r["total"] for r in rows)
        bdi = float(self.S["obra"].get("bdi") or 0) / 100
        return {"cd": cd, "bdi": bdi, "comBdi": cd * (1 + bdi)}

    def premissas(self, ctx):
        S, P, PT = self.S, self.P, self.IND["premissas_texto"]
        p = [PT["padrao"], PT["escala"]]
        if S["obra"].get("semEle"): p.append(PT["sem_projeto_eletrico"])
        if S["obra"].get("semHid"): p.append(PT["sem_projeto_hidraulico"])
        if S["obra"].get("semEst") and S["obra"].get("incluirEstrutura"): p.append(PT["sem_projeto_estrutural"])
        if S["obra"]["padrao"] == "popular":
            p.append("Padrão popular: sem forro de gesso e sem emassamento (pintura direto no reboco selado).")
        p.append(f"Pé-direito adotado: {self.par('pe_direito_m')} m. Portas {P['largura_porta_padrao_m']}×{P['altura_porta_padrao_m']} m. Vãos ≤ 2 m² não descontados da alvenaria (critério de medição).")
        p.append("Esgoto lançado em rede pública existente." if S["obra"].get("redeEsgoto")
                 else "Sem rede pública de esgoto: previsto conjunto fossa séptica + filtro anaeróbio.")
        if not S["obra"].get("incluirEstrutura"):
            p.append("Estrutura EXCLUÍDA do orçamento a pedido (será orçada com projeto estrutural).")
        p.append(f"BDI aplicado: {fmt1(float(S['obra'].get('bdi') or 0))}% sobre o custo direto da tabela DER-ES (tabela publicada com BDI 0).")
        return p

    def lacunas(self):
        S = self.S
        l = []
        if S["obra"].get("semEle"): l.append("Projeto elétrico não fornecido — pontos por mínimos NBR 5410 e distâncias medidas/estimadas.")
        if S["obra"].get("semHid"): l.append("Projeto hidrossanitário não fornecido — traçados estimados pela escala.")
        if S["obra"].get("semEst"): l.append("Projeto estrutural não fornecido — estrutura por índices paramétricos (±20%).")
        if not S["med"].get("escalaNota"): l.append("Planta sem calibração de escala registrada — distâncias digitadas/premissa.")
        pav = int(S["obra"].get("pav") or 1)
        if pav > 1 and S["obra"].get("incluirEstrutura"):
            l.append(f"CONFERIR AS LAJES: a obra tem {pav} pavimentos, logo {pav - 1} laje(s) de entrepiso "
                     f"+ a de cobertura (se não for telhado). Confira também o vazio da escada (desconta "
                     f"área) e lajes de áreas técnicas/barrilete, que o motor não deduz sozinho.")
        for c in getattr(self, "dup", []):
            sv = self.SVC.get(c, {})
            l.append(f"CONFERIR: o código {c} ({sv.get('d','')[:56]}) aparece duas vezes — como item do mapa "
                     f"de padrões E como item extra. Se as duas quantidades têm finalidades distintas "
                     f"(ex.: pontos de ambiente + pontos de bebedouro), está correto; se não, é dupla contagem.")
        return l

    # ---- itens fora da tabela DER-ES ----
    def bloco_sinapi(self):
        """Itens precificados pelo SINAPI (mesma natureza: custo direto, BDI 0)."""
        itens = []
        for x in self.S.get("sinapi", []):
            c = self.SIN.get(str(x.get("c")))
            q = float(x.get("qtd") or 0)
            if not c or not q > 0:
                continue
            itens.append({"c": c["c"], "d": c["d"], "u": c["u"], "qtd": q, "pu": c["p"],
                          "total": rnd2(q * c["p"]), "obs": x.get("obs", ""), "grau": x.get("grau", "")})
        cd = rnd2(sum(i["total"] for i in itens))
        bdi = float(self.S["obra"].get("bdi") or 0) / 100
        return {"fonte": (self.BASE.get("_sinapi") or {}).get("meta", {}).get("fonte", "SINAPI"),
                "referencia": (self.BASE.get("_sinapi") or {}).get("meta", {}).get("referencia", ""),
                "itens": itens, "custo_direto": cd, "com_bdi": rnd2(cd * (1 + bdi))}

    def bloco_complemento(self):
        """Itens sem código de tabela — só admissíveis quando o cliente NÃO exige tabela referencial."""
        itens = []
        for x in self.S.get("complemento", []):
            q, pu = float(x.get("qtd") or 0), float(x.get("pu") or 0)
            if not (q > 0 and pu > 0):
                continue
            mo = float(x.get("mo_oficial") or 0)
            itens.append({"descricao": x.get("descricao", ""), "qtd": q, "und": x.get("und", ""),
                          "pu": pu, "total": rnd2(q * pu),
                          "fonte": x.get("fonte", "Cotação de mercado"),
                          "mo_oficial": mo, "material_cotar": rnd2(pu - mo), "obs": x.get("obs", "")})
        cd = rnd2(sum(i["total"] for i in itens))
        bdi = float(self.S["obra"].get("bdi") or 0) / 100
        return {"nota": self.S.get("complementoNota") or
                ("Nenhum item por cotação: todos os serviços têm código de tabela referencial."
                 if not itens else
                 "Itens sem equivalente publicado nas tabelas — exigem cotação de mercado."),
                "itens": itens, "custo_direto": cd, "com_bdi": rnd2(cd * (1 + bdi)),
                "mo_oficial_total": rnd2(sum(i["qtd"] * i["mo_oficial"] for i in itens))}

    def bloco_substituicoes(self):
        """Item de projeto → serviço de tabela adotado, com grau de similaridade e diferença de escopo."""
        subs = self.S.get("substituicoes", [])
        if not subs:
            return None
        out = []
        for x in subs:
            comps = []
            for cp in x.get("componentes", []):
                tab = (cp.get("tabela") or "DER-ES").upper()
                fonte = self.SVC if tab.startswith("DER") else self.SIN
                sv = fonte.get(str(cp.get("c")))
                if not sv:
                    continue
                q = float(cp.get("qtd") or 0)
                comps.append({"tabela": "DER-ES" if tab.startswith("DER") else "SINAPI-ES",
                              "c": sv["c"], "d": sv["d"], "u": sv["u"], "qtd": q,
                              "pu": sv["p"], "total": rnd2(q * sv["p"])})
            sub = rnd2(sum(c["total"] for c in comps))
            cot = float(x.get("cotado") or 0)
            out.append({"item": x.get("item", ""), "cotado": cot, "substituido": sub,
                        "grau": x.get("grau", ""), "justificativa": x.get("justificativa", ""),
                        "componentes": comps})
        tc = rnd2(sum(o["cotado"] for o in out)); ts = rnd2(sum(o["substituido"] for o in out))
        return {"nota": SUBST_NOTA, "itens": out, "total_cotado": tc,
                "total_substituido": ts, "diferenca": rnd2(tc - ts)}

    # ---- saídas ----
    def orcamento_json(self, ctx, rows, T):
        S = self.S
        sin = self.bloco_sinapi(); compl = self.bloco_complemento()
        subs = self.bloco_substituicoes()
        geral = rnd2(T["comBdi"] + sin["com_bdi"] + compl["com_bdi"])
        extra = {}
        if sin["itens"]:
            extra["itens_sinapi"] = sin
        if subs:
            extra["substituicoes"] = subs
        return {
            "app": "orcamentista-der-es", "versao": 1,
            "obra": {**S["obra"], "data_base": self.BASE["meta"].get("data_base")},
            "ambientes": S["ambientes"], "medicoes": S["med"], "parametros": S.get("par", {}),
            "itens": [{"grupo": r["grupo"], "c": r["c"], "d": r["d"], "u": r["u"], "qtd": r["qtd"],
                       "pu": r["pu"], "total": r["total"], "formula": r["f"], "manual": r["manual"]} for r in rows],
            "overrides": S.get("ov", {}), "extras": S.get("extras", []), "precos": S.get("precos", {}),
            "totais": {"custo_direto": T["cd"], "bdi_pct": float(S["obra"].get("bdi") or 0),
                       "total": T["comBdi"], "total_geral_com_complemento": geral},
            "complemento_a_cotar": compl,
            **extra,
            "premissas": self.premissas(ctx), "lacunas": self.lacunas(),
        }

    def planilha_txt(self, rows, T):
        out = io.StringIO()
        por_cap = {}
        for r in rows:
            por_cap.setdefault(r["cap"], []).append(r)
        w = out.write
        w(f"{'CÓD.':8} {'ESPECIFICAÇÃO':62} {'UND':4} {'QTD':>10} {'PU c/BDI':>12} {'TOTAL':>14}\n")
        for cap in sorted(por_cap):
            rs = sorted(por_cap[cap], key=lambda r: r["c"])
            st = sum(r["total"] for r in rs) * (1 + T["bdi"])
            w(f"\n== {cap} — {self.CAPS.get(cap, '')[:70]}  (R$ {fmt(st)})\n")
            for r in rs:
                w(f"{r['c']:8} {r['d'][:62]:62} {r['u']:4} {fmt(r['qtd']):>10} {fmt(r['pu'] * (1 + T['bdi'])):>12} {fmt(r['total'] * (1 + T['bdi'])):>14}\n")
        w(f"\n{'TOTAL GERAL':88} {'R$':>12} {fmt(T['comBdi']):>14}\n")
        return out.getvalue()

    def memorial_txt(self, ctx, rows):
        out = io.StringIO(); w = out.write
        w("PREMISSAS:\n")
        for p in self.premissas(ctx):
            w(f" • {p}\n")
        lac = self.lacunas()
        if lac:
            w("\nLACUNAS:\n")
            for l in lac:
                w(f" ⚠ {l}\n")
        w("\nMEMÓRIA DE CÁLCULO:\n")
        REGN = self.REG.get("regras", {})
        for r in rows:
            crit = (REGN.get(r["c"]) or {}).get("criterio")
            w(f" [{r['c']}] {r['d'][:70]}\n")
            w(f"    qtd: {fmt(r['qtd'])} {r['u']} ← {r['f']}\n")
            if crit:
                w(f"    critério de medição (Caderno Técnico): {crit[:180]}\n")
        return out.getvalue()

    def csv_str(self, rows, T):
        out = io.StringIO()
        wr = csv.writer(out, delimiter=";")
        wr.writerow(["codigo", "descricao", "und", "qtd", "pu_sem_bdi", "pu_com_bdi", "total_com_bdi"])
        for r in rows:
            wr.writerow([r["c"], r["d"], r["u"], f"{r['qtd']}".replace(".", ","),
                         f"{r['pu']:.2f}".replace(".", ","), f"{r['pu'] * (1 + T['bdi']):.2f}".replace(".", ","),
                         f"{r['total'] * (1 + T['bdi']):.2f}".replace(".", ",")])
        wr.writerow(["", "", "", "", "", "TOTAL", f"{T['comBdi']:.2f}".replace(".", ",")])
        return out.getvalue()


SUBST_NOTA = (
    "O agente financeiro só aceita itens com código de tabela referencial. Cada item que seria cotação "
    "de mercado foi substituído pelo serviço mais próximo com preço publicado (DER-ES ou SINAPI), com o "
    "grau de similaridade declarado. GRAU ALTO: mesma função e mesmo sistema construtivo, troca sem "
    "impacto técnico relevante. GRAU MÉDIO: mesma função, material ou sistema diferente — exige aceite "
    "do projetista. GRAU BAIXO: apenas analogia funcional; o serviço de tabela NÃO reproduz o "
    "especificado. A diferença entre o valor de projeto e o valor de tabela é escopo que o cliente "
    "cobrirá com recursos próprios — declare-a sempre.")

GOLD_CUSTO_DIRETO = 175142.06  # casa exemplo 70 m², padrão médio, BDI 25% — idêntico ao app
# (telhado medido por projeção horizontal conforme critério DER 0901/0902 desde 07/2026)

# 2º dourado: obra COMERCIAL em alvenaria (academia 1.886 m², 2 pav.) — trava perfil estrutural
# comercial, itens SINAPI (inclusive a estrutura leve de cobertura) e substituições com grau.
GOLD_COMERCIAL = {"cd_der": 3107406.58, "cd_sinapi": 871508.17, "geral": 4973643.43,
                  "n_der": 108, "n_sinapi": 12, "dif_escopo": 471461.00}


def autoteste(refs):
    base, mapa, ind, reg = load_refs(refs)
    m = Motor(def_state(), base, mapa, ind, reg)
    st = m.amb_stats()
    ctx, rows = m.calc_itens()
    T = m.totais(rows)
    checks = [
        ("nº de serviços na base", len(base["servicos"]), 1340),
        ("preço 140701 (pt água fria)", m.SVC["140701"]["p"], 112.49),
        ("preço 151801 (pt luz teto)", m.SVC["151801"]["p"], 238.03),
        ("pontos de luz (7 amb)", st["luz"], 7),
        ("tomadas NBR 5410", st["tug"], 19),
        ("bacias", st["bacias"], 1),
        ("zonas molhadas", st["zonasMolhadas"], 3),
        ("custo direto DOURADO", round(T["cd"], 2), GOLD_CUSTO_DIRETO),
    ]
    # ---- 2º dourado: obra comercial ----
    exc = os.path.join(refs, "exemplo-comercial.json")
    if os.path.exists(exc):
        with open(exc, encoding="utf-8") as f:
            ent = json.load(f)
        S2 = def_state()
        S2["obra"].update(ent["obra"]); S2["ambientes"] = ent["ambientes"]
        S2["med"].update(ent.get("med", {})); S2["ov"] = ent.get("ov", {})
        S2["extras"] = ent.get("extras", []); S2["par"] = ent.get("par", {})
        S2["sinapi"] = ent.get("sinapi", []); S2["complemento"] = ent.get("complemento", [])
        S2["substituicoes"] = ent.get("substituicoes", [])
        m2 = Motor(S2, base, mapa, ind, reg)
        c2, r2 = m2.calc_itens(); T2 = m2.totais(r2)
        oj2 = m2.orcamento_json(c2, r2, T2)
        G = GOLD_COMERCIAL
        checks += [
            ("[comercial] itens DER-ES", len(r2), G["n_der"]),
            ("[comercial] itens SINAPI", len(oj2.get("itens_sinapi", {}).get("itens", [])), G["n_sinapi"]),
            ("[comercial] itens por cotação", len(oj2["complemento_a_cotar"]["itens"]), 0),
            ("[comercial] custo direto DER-ES", round(T2["cd"], 2), G["cd_der"]),
            ("[comercial] custo direto SINAPI", oj2["itens_sinapi"]["custo_direto"], G["cd_sinapi"]),
            ("[comercial] diferença de escopo", oj2["substituicoes"]["diferenca"], G["dif_escopo"]),
            ("[comercial] TOTAL GERAL", oj2["totais"]["total_geral_com_complemento"], G["geral"]),
        ]

    ok = True
    for nome, got, want in checks:
        passed = abs(got - want) < 0.011
        ok &= passed
        print(f"{'✅' if passed else '❌'} {nome}: {got}" + ("" if passed else f" (esperado {want})"))
    for r in rows:
        if not (r["qtd"] > 0 and r["pu"] > 0):
            ok = False
            print(f"❌ item degenerado: {r['c']} qtd={r['qtd']} pu={r['pu']}")
    print(("AUTOTESTE OK — motor idêntico ao app (" if ok else "AUTOTESTE FALHOU (")
          + f"custo direto R$ {fmt(T['cd'])}, total c/ BDI R$ {fmt(T['comBdi'])})")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", nargs="?")
    ap.add_argument("--out"); ap.add_argument("--csv"); ap.add_argument("--refs")
    ap.add_argument("--autoteste", action="store_true")
    ap.add_argument("--exemplo", action="store_true")
    a = ap.parse_args()
    if a.exemplo:
        print(json.dumps(def_state(), ensure_ascii=False, indent=1)); return 0
    refs = find_refs(a.refs)
    if a.autoteste:
        return autoteste(refs)
    if not a.entrada:
        ap.error("informe entrada.json (ou --autoteste / --exemplo)")
    base, mapa, ind, reg = load_refs(refs)
    with open(a.entrada, encoding="utf-8") as f:
        ent = json.load(f)
    S = def_state()
    S["obra"].update(ent.get("obra", {}))
    if ent.get("ambientes"): S["ambientes"] = ent["ambientes"]
    S["med"].update(ent.get("med") or ent.get("medicoes") or {})
    S["ov"] = ent.get("ov") or ent.get("overrides") or {}
    S["extras"] = ent.get("extras", []); S["precos"] = ent.get("precos", {}); S["par"] = ent.get("par") or ent.get("parametros") or {}
    # itens fora da tabela DER-ES
    S["sinapi"] = ent.get("sinapi", [])
    S["complemento"] = ent.get("complemento", [])
    S["complementoNota"] = ent.get("complementoNota")
    S["substituicoes"] = ent.get("substituicoes", [])
    m = Motor(S, base, mapa, ind, reg)
    ctx, rows = m.calc_itens()
    T = m.totais(rows)
    m2 = float(S["obra"].get("area") or 1) or 1
    print(f"OBRA: {S['obra']['nome']} · {S['obra'].get('local','')} · padrão {S['obra']['padrao']} · {fmt1(m2)} m²")
    sinb = m.bloco_sinapi(); cpl = m.bloco_complemento()
    geral = T["comBdi"] + sinb["com_bdi"] + cpl["com_bdi"]
    print(f"CUSTO DIRETO R$ {fmt(T['cd'])}  |  BDI {fmt1(T['bdi']*100)}% R$ {fmt(T['cd']*T['bdi'])}  |  DER-ES c/ BDI R$ {fmt(T['comBdi'])}")
    if sinb["itens"]:
        print(f"SINAPI: {len(sinb['itens'])} itens  |  c/ BDI R$ {fmt(sinb['com_bdi'])}")
    if cpl["itens"]:
        print(f"COTAÇÃO DE MERCADO: {len(cpl['itens'])} itens  |  c/ BDI R$ {fmt(cpl['com_bdi'])}  ⚠ não aceito por agente financeiro")
    else:
        print("COTAÇÃO DE MERCADO: nenhum item — orçamento 100% em tabela referencial ✅")
    print(f"TOTAL GERAL R$ {fmt(geral)}  |  R$/m² {fmt(geral/m2)}")
    sb = m.bloco_substituicoes()
    if sb:
        print(f"SUBSTITUIÇÕES: {len(sb['itens'])} itens · projeto R$ {fmt(sb['total_cotado'])} → tabela R$ {fmt(sb['total_substituido'])} · DIFERENÇA DE ESCOPO R$ {fmt(sb['diferenca'])} (recursos próprios do cliente)")
    print()
    print(m.planilha_txt(rows, T))
    print(m.memorial_txt(ctx, rows))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(m.orcamento_json(ctx, rows, T), f, ensure_ascii=False, indent=1)
        print(f"[orcamento.json gravado em {a.out} — abre no orcamentista.html via Importar JSON]")
    if a.csv:
        with open(a.csv, "w", encoding="utf-8") as f:
            f.write("﻿" + m.csv_str(rows, T))
        print(f"[planilha CSV gravada em {a.csv}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
