"""Motor financeiro BNB/FNE — porte fiel do runSim()/xirr() de index.html.

O simulador HTML é a FONTE DA VERDADE (validado 100% contra a planilha oficial do BNB,
10/10 cenários). Este módulo é um porte linha a linha para Python; a paridade é garantida
por tests/test_financeiro.py contra os mesmos valores-ouro do autoteste do simulador.

Convenções (idênticas ao original):
  - juros pro-rata em dias úteis / 252 (calendário de feriados BNB 2017–2060);
  - taxaSem = taxa sem bônus de adimplência; taxaCom = com bônus;
  - datas como datetime.date; dinheiro em float com arredondamento r2 (2 casas).
"""
import json
import math
import os
from calendar import monthrange
from datetime import date, timedelta

_AQUI = os.path.dirname(os.path.abspath(__file__))
FERIADOS = {}  # date -> cfg (1 = feriado que não ajusta vencimento, 2 = ajusta)
for _y, _m, _d, _cfg in json.load(open(os.path.join(_AQUI, "feriados_bnb.json"))):
    FERIADOS[date(_y, _m, _d)] = _cfg

PERIOD_M = {"MENSAL": 1, "BIMESTRAL": 2, "TRIMESTRAL": 3, "SEMESTRAL": 6, "ANUAL": 12}


# ---------- utilidades de data (semântica do JS) ----------

def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def hol_cfg(d: date) -> int:
    return FERIADOS.get(d, 0)


def network_days(s: date, e: date) -> int:
    if not s or not e or s > e:
        return 0
    c, cur = 0, s
    while cur <= e:
        if not is_weekend(cur) and not hol_cfg(cur):
            c += 1
        cur += timedelta(days=1)
    return c


def aj_flag(d: date) -> int:
    if is_weekend(d):
        return 2
    if hol_cfg(d) == 2:
        return 2
    return 1


def am_days(p: date, c: date) -> int:
    if not p or not c or c <= p:
        return 0
    nd = network_days(p, c)
    return nd if aj_flag(c) == 2 else nd - 1


def edate(d: date, m: int) -> date:
    y = d.year + (d.month - 1 + m) // 12
    mo = (d.month - 1 + m) % 12 + 1
    return date(y, mo, min(d.day, monthrange(y, mo)[1]))


def eomonth(d: date, m: int) -> date:
    y = d.year + (d.month - 1 + m) // 12
    mo = (d.month - 1 + m) % 12 + 1
    return date(y, mo, monthrange(y, mo)[1])


def js_set_date(d: date, day_num: int) -> date:
    """Equivale a new Date(d).setDate(day_num) do JS (transborda mês se preciso)."""
    return date(d.year, d.month, 1) + timedelta(days=day_num - 1)


# ---------- arredondamentos do original ----------

def r2(v: float) -> float:
    if v >= 0:
        return math.floor((v + 1e-12) * 100 + 0.5) / 100
    return -math.floor((-v + 1e-12) * 100 + 0.5) / 100


def r6(v: float) -> float:
    return math.floor((v + 1e-15) * 1e6 + 0.5) / 1e6


# ---------- TIR não periódica (Newton, como no original) ----------

def xirr(cfs, dts, guess=0.1):
    if not cfs:
        return 0.0
    d0 = dts[0]
    diffs = [(d - d0).days / 365.0 for d in dts]
    rate = guess
    for _ in range(300):
        f = df = 0.0
        for cf, t in zip(cfs, diffs):
            base = 1 + rate
            if base <= 0:
                continue
            f += cf / base ** t
            df -= t * cf / base ** (t + 1)
        if abs(df) < 1e-14:
            break
        nr = rate - f / df
        if abs(nr - rate) < 1e-13:
            return nr
        rate = nr
        if not math.isfinite(rate) or rate < -0.99:
            rate = guess * 0.5
    return rate


# ---------- motor principal ----------

def run_sim(p: dict) -> dict:
    """Porte fiel de runSim(). Espera:
    data0 (date), valor (float), dia (int|None), taxaSem, taxaCom (frações a.a.),
    prazoAmort, carencia (meses), periodPrinc, periodCar, parcelasIguais (bool),
    reembolso (dict seq->valor), desembolsos ([{data: date, valor: float}]),
    custos ([{nome, valor}]).
    """
    C4, valor = p["data0"], p["valor"]
    dia = p.get("dia") or (28 if C4.day >= 29 else C4.day)
    ts, tc = p["taxaSem"], p["taxaCom"]
    prazo, car = p["prazoAmort"], p["carencia"]
    prazo_total = prazo + car
    pp = p.get("periodPrinc", "MENSAL")
    pc = p.get("periodCar", "TRIMESTRAL")
    iguais = p["parcelasIguais"]
    reemb = p.get("reembolso", {})

    # Data-base (P15)
    if C4.day <= dia:
        ld = monthrange(C4.year, C4.month)[1]
        base = date(C4.year, C4.month, min(dia, ld))
    else:
        nx = edate(C4, 1)
        ld = monthrange(nx.year, nx.month)[1]
        base = date(nx.year, nx.month, min(dia, ld))

    # 1ª prestação, vencimento, quantidade
    if pp == "PARCELA ÚNICA":
        data1a, qtd_prest = edate(base, prazo_total), 1
    else:
        pm = PERIOD_M.get(pp, 1)
        data1a = edate(base, car + pm)
        qtd_prest = prazo // pm
    venc = edate(base, prazo_total)
    D7 = qtd_prest
    K9 = r2(valor / D7)
    J4 = edate(data1a, -1)

    # CÁLCULO DESEMB
    cd = []
    for dd in p["desembolsos"]:
        if not (dd.get("valor", 0) > 0 and dd.get("data")):
            continue
        B, C = dd["data"], dd["valor"]
        if B > venc:
            continue
        D = B.day
        eom0 = eomonth(B, 0)
        if D == dia:
            F = B
        else:
            cand = js_set_date(B, B.day + (dia - D))
            F = eom0 if cand > eom0 else cand
        AD = (F - B).days
        eom1 = eomonth(B, 1)
        W_ = date(eom1.year, eom1.month, min(dia, eom1.day))
        Xd = eom1 if W_ > eom1 else W_
        G = F if AD > 0 else Xd
        H = B if F == B else G
        I = 0
        if B <= venc:
            nd = network_days(B, H)
            I = nd if aj_flag(H) == 2 else nd - 1
            if H == B and aj_flag(H) != 2:
                I = 0
        Pv = r2((r6((1 + ts) ** (I / 252)) - 1) * C) if I > 0 else 0.0
        Qv = r2((r6((1 + tc) ** (I / 252)) - 1) * C) if I > 0 else 0.0
        if B == C4:
            AE = C
        elif B == venc:
            AE = C
        elif D == dia:
            AE = 0
        else:
            AE = C
        cd.append({"B": B, "C": C, "H": H, "I": I, "P": Pv, "Q": Qv, "AE": AE})

    def sum_cd(campo, dt):
        return sum(x[campo] for x in cd if x["H"] == dt)

    # MEMÓRIA DE CÁLCULO
    O = Pb = Q = R = S = 0.0
    X = valor
    AOp = AUp = 0
    prev = C4
    tot_j = tot_k = tot_l = 0.0
    total_desemb_alloc = sum(x["C"] for x in cd)
    cum_desemb = 0.0
    rows = []
    for m in range(prazo_total + 1):
        Cd = base if m == 0 else edate(base, m)
        AM = am_days(prev, Cd) if Cd > prev else 0
        Dm, Em, Fm = sum_cd("C", Cd), sum_cd("P", Cd), sum_cd("Q", Cd)
        Gm = r2((r6((1 + ts) ** (AM / 252)) - 1) * R) + Em
        Hm = r2((r6((1 + tc) ** (AM / 252)) - 1) * S) + Fm
        AT = 1 if Cd == data1a else 0
        if AOp + 1 > D7:
            AO = 0
        elif AT == 1:
            AO = 1
        elif AOp > 0:
            AO = AOp + 1
        else:
            AO = 0
        AU = AO
        Bm = AU if AU != AUp else 0
        Im = 0.0
        if not iguais and 0 < Bm <= D7:
            Im = reemb.get(Bm, 0.0)
        if Cd > venc or Bm == 0:
            T = 0.0
        elif Cd == venc:
            T = X
        elif iguais:
            T = K9
        elif Im > 0:
            T = Im
        else:
            T = X / ((D7 + 1) - Bm)
        Wm = T / X if (T != 0 and X != 0) else 0.0
        Um = sum_cd("AE", Cd)
        Jm = (Q + Um) if Cd == venc else r2((Q + Um) * Wm)
        BB = 0
        if pc != "NENHUMA":
            gate = (Cd <= J4) and (AU == 0)
            div = PERIOD_M.get(pc, 3)
            BB = 1 if (gate and m % div == 0) else 0
        if data1a > Cd:
            Km, Lm = (O + Gm) * BB, (Pb + Hm) * BB
        elif Jm == 0:
            Km = Lm = 0.0
        else:
            Km, Lm = O + Gm, Pb + Hm
        O = O + Gm - Km
        Pb = Pb + Hm - Lm
        Q = Q + Dm - Jm
        R = O + Q
        S = Pb + Q
        if T > 0:
            X = X - T
        if Jm > 0:
            tot_j += Jm
        if Km > 0:
            tot_k += Km
        if Lm > 0:
            tot_l += Lm
        rows.append({
            "mes": m, "seq": Bm, "data": Cd, "disbValor": Dm, "amd": AM,
            "juroMensalSem": Gm, "juroPagoSem": Km, "juroPagoCom": Lm,
            "principal": Jm, "totalSem": Jm + Km, "totalCom": Jm + Lm,
            "bonus": Km - Lm, "saldoPrinc": max(Q, 0.0),
            "isGrace": Cd < data1a and m > 0, "isAmort": Cd >= data1a,
        })
        prev, AOp, AUp = Cd, AO, AU
        cum_desemb += Dm
        if Q <= 0.01 and Cd >= data1a and cum_desemb >= total_desemb_alloc - 0.01:
            break

    # CET (Anexo CET da planilha): desembolsos (+) nas datas reais, custos (−) na 1ª
    # data de desembolso, prestações (−) em todas as datas com pagamento.
    custos_total = sum(c["valor"] for c in p.get("custos", []))

    def build_flow(campo):
        fm = {}

        def add_f(d, v):
            fm[d] = fm.get(d, 0.0) + v

        vd = [{"data": dd["data"], "valor": dd["valor"]} for dd in p["desembolsos"]
              if dd.get("valor", 0) > 0 and dd.get("data") and dd["data"] <= venc]
        for item in vd:
            add_f(item["data"], item["valor"])
        if vd:
            fd = min(item["data"] for item in vd)
            add_f(fd, -custos_total)
        for s_ in rows:
            if s_[campo] > 0.001:
                add_f(s_["data"], -s_[campo])
        keys = sorted(fm)
        return [fm[k] for k in keys], keys

    cfs_sem, dts_sem = build_flow("totalSem")
    cet_anual = xirr(cfs_sem, dts_sem, 0.1) if len(cfs_sem) > 2 else 0.0
    cfs_com, dts_com = build_flow("totalCom")
    cet_anual_bonus = xirr(cfs_com, dts_com, 0.1) if len(cfs_com) > 2 else 0.0

    amort_rows = [s_ for s_ in rows if s_["principal"] > 0.001]
    return {
        "rows": rows, "cd": cd, "qtdPrest": D7, "data1a": data1a, "venc": venc,
        "base": base, "dia": dia,
        "totalJurosSem": round(tot_k * 100) / 100,
        "totalJurosCom": round(tot_l * 100) / 100,
        "totalPrincipal": round(tot_j * 100) / 100,
        "totalBonus": round((tot_k - tot_l) * 100) / 100,
        "mediaPrestCom": (sum(s_["totalCom"] for s_ in amort_rows) / len(amort_rows))
                         if amort_rows else 0.0,
        "cetAnual": cet_anual,
        "cetMensal": (1 + cet_anual) ** (1 / 12) - 1,
        "cetAnualComBonus": cet_anual_bonus,
        "cetMensalComBonus": (1 + cet_anual_bonus) ** (1 / 12) - 1,
        "custosTotal": custos_total,
    }
