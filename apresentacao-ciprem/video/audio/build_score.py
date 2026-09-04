#!/usr/bin/env python3
"""
Desenho de som do vídeo CIPREM (vinheta + 8 cenas), versão 2: mais suave e numa grade única.

Gera public/audio/score.wav (estéreo, 48 kHz, 108.29 s) totalmente sintetizado.

Grade rítmica: 120 BPM, batida 0,5 s, compasso 2,0 s, ancorada no início do conteúdo (18,22 s).
Todas as cenas começam em cabeça de compasso (compassos 0, 4, 8, 13, 21, 28, 33, 40), então
os hits de cena caem sempre na pulsação que já está tocando.

Uso:  python build_score.py [saida.wav]
Requer numpy e scipy.
"""
import sys, math, os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 108.29
N = int(DUR * SR)
C0 = 18.22                   # início do conteúdo
BEAT = 0.5                   # 120 BPM
BAR = 2.0
rng = np.random.default_rng(20260904)

def bar(n, beat=0.0):        # cabeça do compasso n do conteúdo (+ deslocamento em batidas)
    return C0 + n * BAR + beat * BEAT

def c(t):                    # segundo do conteúdo -> tempo absoluto
    return C0 + t

# ------------------------------------------------------------------ utilidades
def t_axis(dur):
    return np.arange(int(dur * SR)) / SR

def env_adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.zeros(n); i = 0
    k = min(a, n); e[:k] = np.linspace(0, 1, k, endpoint=False) ** 1.5; i += k
    k = min(d, n - i); e[i:i + k] = np.linspace(1, s, k, endpoint=False); i += k
    k = max(0, n - i - r); e[i:i + k] = s; i += k
    k = n - i
    if k > 0: e[i:] = np.linspace(e[i - 1] if i > 0 else s, 0, k) ** 1.0
    return e

def exp_decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))

def soft_attack(n, ms):
    k = int(ms / 1000 * SR)
    e = np.ones(n); e[:k] = np.linspace(0, 1, k) ** 2
    return e

def sine(freq, dur, phase=0.0):
    return np.sin(2 * np.pi * freq * t_axis(dur) + phase)

def sine_glide(f0, f1, dur, curve=1.0):
    t = t_axis(dur); x = (t / dur) ** curve
    f = f0 * (f1 / f0) ** x
    return np.sin(2 * np.pi * np.cumsum(f) / SR)

def saw(freq, dur, detune_cents=0.0):
    f = freq * 2 ** (detune_cents / 1200)
    return 2 * ((t_axis(dur) * f) % 1.0) - 1

def noise(dur):
    return rng.standard_normal(int(dur * SR))

def brown(dur):
    x = np.cumsum(rng.standard_normal(int(dur * SR)))
    x -= np.convolve(x, np.ones(2000) / 2000, mode="same")
    return x / (np.abs(x).max() + 1e-9)

def lp(sig, fc, order=2):
    fc = float(np.clip(fc, 20, SR / 2 - 100))
    return sosfilt(butter(order, fc, btype="low", fs=SR, output="sos"), sig)

def hp(sig, fc, order=2):
    fc = float(np.clip(fc, 20, SR / 2 - 100))
    return sosfilt(butter(order, fc, btype="high", fs=SR, output="sos"), sig)

def bp(sig, f1, f2, order=2):
    f1 = float(np.clip(f1, 20, SR / 2 - 200)); f2 = float(np.clip(f2, f1 + 10, SR / 2 - 100))
    return sosfilt(butter(order, [f1, f2], btype="band", fs=SR, output="sos"), sig)

def sweep_lp(sig, fc_curve, order=2, block=512):
    out = np.zeros_like(sig); zi = None
    for i in range(0, len(sig), block):
        fc = float(np.clip(fc_curve[min(i + block // 2, len(sig) - 1)], 30, SR / 2 - 200))
        sos = butter(order, fc, btype="low", fs=SR, output="sos")
        if zi is None: zi = np.zeros((sos.shape[0], 2))
        out[i:i + block], zi = sosfilt(sos, sig[i:i + block], zi=zi)
    return out

def sweep_bp(sig, fc_curve, width=0.8, block=512):
    out = np.zeros_like(sig); zi = None
    for i in range(0, len(sig), block):
        fc = float(np.clip(fc_curve[min(i + block // 2, len(sig) - 1)], 60, SR / 2 - 400))
        sos = butter(2, [fc / (1 + width), min(fc * (1 + width), SR / 2 - 200)], btype="band", fs=SR, output="sos")
        if zi is None: zi = np.zeros((sos.shape[0], 2))
        out[i:i + block], zi = sosfilt(sos, sig[i:i + block], zi=zi)
    return out

def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)

_ir_cache = {}
def reverb(sig, decay=2.0, mix=0.35, predelay=0.02, tone=5000):
    """Reverb por convolução com IR sintética estéreo (mais escura que a v1). Retorna (L, R)."""
    key = (round(decay, 2), tone)
    if key not in _ir_cache:
        n = int(decay * 3 * SR); t = np.arange(n) / SR
        e = np.exp(-t / decay * 3)
        irl = lp(rng.standard_normal(n) * e, tone); irr = lp(rng.standard_normal(n) * e, tone)
        pd = int(predelay * SR)
        irl = np.concatenate([np.zeros(pd), irl]); irr = np.concatenate([np.zeros(pd), irr])
        norm = np.sqrt(np.sum(irl ** 2))
        _ir_cache[key] = (irl / norm * 0.9, irr / norm * 0.9)
    irl, irr = _ir_cache[key]
    wl = fftconvolve(sig, irl)[: len(sig) + len(irl)]
    wr = fftconvolve(sig, irr)[: len(sig) + len(irr)]
    dry = np.concatenate([sig, np.zeros(len(wl) - len(sig))])
    return dry * (1 - mix) + wl * mix, dry * (1 - mix) + wr * mix

def pan_lr(sig, pan=0.0):
    th = (pan + 1) * np.pi / 4
    return sig * np.cos(th), sig * np.sin(th)

class Stem:
    def __init__(self, name):
        self.name = name; self.L = np.zeros(N); self.R = np.zeros(N); self.onsets = []
    def add(self, t, sig, gain=1.0, pan=0.0, onset=False):
        l, r = sig if isinstance(sig, tuple) else pan_lr(sig, pan)
        i = int(round(t * SR))
        if i >= N or i < 0: return
        k = min(len(l), N - i)
        self.L[i:i + k] += l[:k] * gain; self.R[i:i + k] += r[:k] * gain
        if onset: self.onsets.append(t)
    def stereo(self):
        return np.stack([self.L, self.R], axis=1)

# ------------------------------------------------------------------ notas
def hz(name):
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    return 440.0 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) + 1) - 69) / 12)

CH = {
    "Dm":   ["D3", "F3", "A3"],
    "Dm_hi": ["D4", "F4", "A4"],
    "Bb":   ["Bb2", "D3", "F3"],
    "F":    ["F3", "A3", "C4"],
    "C":    ["C3", "E3", "G3"],
    "Dm5":  ["D3", "F3", "A3", "D4", "F4"],
    "Bb5":  ["Bb2", "D3", "F3", "Bb3", "D4"],
    "F5":   ["F3", "A3", "C4", "F4", "A4"],
    "C5":   ["C3", "E3", "G3", "C4", "E4"],
    "Dmaj": ["D3", "F#3", "A3", "D4"],
    "Dmaj5": ["D3", "F#3", "A3", "D4", "F#4", "A4"],
    "Bbchoir": ["Bb2", "F3", "Bb3", "D4", "F4"],
    "Cchoir": ["C3", "G3", "C4", "E4", "G4"],
}
BASS = {"Dm": "D2", "Dm_hi": "D2", "Bb": "Bb1", "F": "F2", "C": "C2", "Dm5": "D2", "Bb5": "Bb1", "F5": "F2", "C5": "C2",
        "Dmaj": "D2", "Dmaj5": "D2", "Bbchoir": "Bb1", "Cchoir": "C2"}

# ------------------------------------------------------------------ instrumentos (v2: suaves)
def i_pad(chord, dur, gain=1.0, fc0=500, fc1=900, attack=0.35, release=0.5, octave=0, vib=0.0025, decay=3.0):
    """Cordas sintéticas macias: 5 serras em unison bem filtradas + seno; sem distorção; reverb longo."""
    n = int(dur * SR); t = np.arange(n) / SR
    L = np.zeros(n); R = np.zeros(n)
    for i, name in enumerate(chord):
        f = hz(name) * 2 ** octave
        v = 1 + vib * np.sin(2 * np.pi * (4.2 + 0.25 * i) * t + i)
        s = np.sin(2 * np.pi * np.cumsum(f * v) / SR) * 0.7
        uni_l = sum(saw(f, dur, d) for d in (-7, -3, 2)) * 0.12
        uni_r = sum(saw(f, dur, d) for d in (-2, 3, 7)) * 0.12
        L += uni_l + s; R += uni_r + s
    fc = fc0 + (fc1 - fc0) * (1 - np.exp(-t / max(0.3, dur * 0.5)))
    L = sweep_lp(L, fc, order=4); R = sweep_lp(R, fc, order=4)
    e = env_adsr(n, attack, 0.2, 0.92, release)
    L *= e; R *= e
    wl, _ = reverb(L, decay=decay, mix=0.4, tone=3500); _, wr = reverb(R, decay=decay, mix=0.4, tone=3500)
    return wl * gain / len(chord), wr * gain / len(chord)

def i_shimmer(chord, dur, gain=1.0):
    return i_pad(chord, dur, gain=gain, fc0=1200, fc1=2200, attack=1.2, release=1.5, octave=1, vib=0.003, decay=4.0)

def i_braam(f=36.71, dur=3.0):
    """Braam suave: serras detunadas com passa-baixas fechado (<= 800 Hz), ataque lento, sub por baixo."""
    n = int(dur * SR); t = np.arange(n) / SR
    v = sum(saw(f, dur, d) * 0.45 + saw(f * 2, dur, d * 0.5) * 0.25 for d in (-8, -3, 4, 9))
    fc = 120 + 680 * (1 - np.exp(-t / 0.6))
    v = sweep_lp(v, fc, order=4)
    v = softclip(v * 1.1, 1.1)
    v += sine(f, dur) * 0.9 + sine(f * 2, dur) * 0.3
    v *= env_adsr(n, 0.4, 0.5, 0.75, 1.2)
    return reverb(v, decay=2.5, mix=0.35, tone=2500)

def i_hit(size=1.0, tail=2.5):
    """Impacto: mais 'thump' grave, menos ruído; ataque de 8 ms; cauda de reverb escura."""
    dur = 0.7; n = int(dur * SR)
    body = lp(noise(dur), 1200) * exp_decay(n, 0.10) * 0.35
    thump = sine_glide(85, 42, dur, curve=0.6) * exp_decay(n, 0.28) * 1.2
    sub = sine(40, dur) * exp_decay(n, 0.55) * 0.9 * size
    x = (body + thump + sub) * soft_attack(n, 8)
    x = softclip(x, 1.15)
    return reverb(x, decay=tail, mix=0.45, tone=2500)

def i_hit_soft():
    dur = 0.5; n = int(dur * SR)
    x = lp(noise(dur), 600) * exp_decay(n, 0.07) * 0.4 + sine_glide(70, 38, dur) * exp_decay(n, 0.3)
    return reverb(x * soft_attack(n, 10), decay=1.2, mix=0.3, tone=2000)

def i_sub_drop(f0=55, f1=30, dur=2.5):
    s = sine_glide(f0, f1, dur, curve=0.6)
    return s * env_adsr(len(s), 0.03, 0.4, 0.7, 1.2)

def i_riser(dur=4.0, f0=150, f1=1800):
    """Riser suave: ruído com banda subindo (teto 2,5 kHz), tremolo senoidal acelerando, sem tom agudo."""
    n = int(dur * SR); t = np.arange(n) / SR; x = t / dur
    fc = np.minimum(f0 * (f1 / f0) ** (x ** 1.3), 2500)
    nz = sweep_bp(noise(dur), fc, width=1.0)
    rate = 3 + 14 * x ** 2
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    e = x ** 2.5
    out = lp(nz * e * trem, 2500)
    out += sine_glide(f0 / 3, f0, dur, curve=1.3) * e * 0.25   # tom grave subindo, discreto
    return reverb(out, decay=1.8, mix=0.3, tone=2500)

def i_swell(dur=1.5):
    n = int(dur * SR); x = (np.arange(n) / n) ** 3
    return lp(bp(noise(dur), 1500, 5000) * x, 4500)

def i_reverse(dur=0.8, size=0.8):
    l, r = i_hit(size, tail=dur)
    l = l[: int(dur * SR)][::-1]; r = r[: int(dur * SR)][::-1]
    fade = np.linspace(0, 1, len(l)) ** 2
    return l * fade, r * fade

def i_taiko(low=True, soft=False):
    """Taiko: pele grave com ataque de 4 ms, passa-baixas 1,2 kHz, sala curta."""
    dur = 0.8; n = int(dur * SR)
    f0, f1 = (120, 50) if low else (180, 85)
    x = sine_glide(f0, f1, dur, curve=0.5) * exp_decay(n, 0.26)
    x += lp(noise(dur), 900) * exp_decay(n, 0.025) * (0.25 if soft else 0.4)
    x = lp(x * soft_attack(n, 4), 1200)
    x = softclip(x * 1.1, 1.1)
    return reverb(x, decay=1.0, mix=0.3, tone=2000)

def i_shaker():
    dur = 0.12; n = int(dur * SR)
    return lp(bp(noise(dur), 2000, 5000) * exp_decay(n, 0.02) * soft_attack(n, 6), 5000)

def i_ping(freq, dur=1.8):
    """Sino/vidro suave, com reverb longo e sem parcial estridente."""
    n = int(dur * SR)
    x = sine(freq, dur) * exp_decay(n, 0.5) + sine(freq * 2.0, dur) * exp_decay(n, 0.18) * 0.25 + sine(freq * 2.76, dur) * exp_decay(n, 0.08) * 0.12
    x = lp(x * soft_attack(n, 3), 6000)
    return reverb(x * 0.6, decay=2.2, mix=0.45, tone=4000)

def i_piano(freq, dur=3.5, bright=0.8):
    n = int(dur * SR)
    x = 0
    for k in range(1, 7):
        x = x + sine(freq * k, dur) * (1 / k ** 1.4) * bright ** (k - 1) * exp_decay(n, 1.6 / k ** 0.8)
    x = lp(x * soft_attack(n, 5), 5000)
    return reverb(x * 0.8, decay=3.0, mix=0.4, tone=3500)

def i_bass(note, dur=0.8):
    n = int(dur * SR); f = hz(note)
    x = lp(saw(f, dur) * 0.5 + sine(f, dur) * 0.8, 220, order=4) * env_adsr(n, 0.02, 0.2, 0.6, 0.3)
    return x

def i_drone(freq, dur, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sine(freq, dur) + 0.4 * sine(freq * 2.001, dur) + 0.15 * sine(freq * 3.0, dur)
    x *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.15 * t)
    return x * env_adsr(n, 1.0, 0.1, 1.0, 1.2) * gain

def i_rumble(dur, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = lp(brown(dur), 100, order=2)
    x *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.21 * t) * np.sin(2 * np.pi * 0.06 * t + 1)
    return x / (np.abs(x).max() + 1e-9) * gain

def i_whoosh(dur=0.7, f_peak=1800):
    n = int(dur * SR); t = np.arange(n) / SR; x = t / dur
    fc = 250 + (f_peak - 250) * np.sin(np.pi * x) ** 1.5
    nz = lp(sweep_bp(noise(dur), fc, width=0.8), 2500)
    return nz * np.sin(np.pi * x) ** 2

def i_heartbeat():
    n = int(0.5 * SR)
    a = sine_glide(75, 42, 0.25) * exp_decay(int(0.25 * SR), 0.07)
    b = sine_glide(65, 38, 0.25) * exp_decay(int(0.25 * SR), 0.06) * 0.7
    x = np.zeros(n); x[: len(a)] += a; x[int(0.17 * SR): int(0.17 * SR) + len(b)] += b
    return lp(x, 160)

# ------------------------------------------------------------------ stems
music = Stem("music"); perc = Stem("perc"); fx = Stem("fx"); amb = Stem("amb"); hits = Stem("hits")

def whoosh_pan(t, gain=0.3, dur=0.7, f_peak=1800):
    w = i_whoosh(dur, f_peak); n = len(w)
    th = (np.linspace(-0.7, 0.7, n) + 1) * np.pi / 4
    fx.add(t, (w * np.cos(th), w * np.sin(th)), gain)

def motif(t, notes, gain=0.5, step=BEAT):
    for k, n in enumerate(notes):
        music.add(t + k * step, i_piano(hz(n), 3.5, 0.75), gain * (1 - 0.12 * k))

def fill(n_bar, gain=0.7):
    """Virada de 3 taikos no último tempo do compasso n, levando à cabeça do compasso seguinte."""
    for k, off in enumerate((3.0, 3.5, 3.75)):
        perc.add(bar(n_bar, off), i_taiko(low=(k == 0)), gain * (0.6 + 0.2 * k), onset=True)

# =========================================================== harmonia por compasso (45 compassos)
PROG = (["Dm"] * 3 + ["Dm_hi"]                          # cena 1  c0–3
        + ["Dm", "Bb", "Dm", "Bb"]                       # cena 2  c4–7
        + ["Dm5", "Dm5", "Bb5", "F5", "C5"]              # cena 3  c8–12
        + ["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "C"]   # cena 4  c13–20 (oitava acima)
        + ["Dm5", "Dm5", "Bb5", "F5", "C5", "Dm5", "Bb5"]  # cena 5  c21–27
        + ["Bbchoir", "Bbchoir", "Cchoir", "Cchoir", "Dm5"]  # cena 6  c28–32
        + ["Dmaj5", "Dmaj", "Dmaj5", "Dmaj", "Dmaj5", "Dmaj", "Dmaj"]  # cena 7  c33–39
        + ["Dmaj5"] * 5)                                 # cena 8  c40–44
assert len(PROG) == 45

def pad_gain(n):
    if n <= 3: return 0.30 + 0.03 * n
    if n <= 7: return 0.36 + 0.04 * (n - 4)
    if n <= 12: return 0.50
    if n <= 20: return 0.30 + 0.12 * (n - 13) / 7
    if n <= 27: return 0.48
    if n <= 32: return 0.50 if n != 31 else 0.42
    if n <= 39: return 0.46 if n < 38 else 0.30
    return 0.0                                           # cena 8 usa um pad longo próprio

for n_bar, ch in enumerate(PROG):
    g = pad_gain(n_bar)
    if g <= 0: continue
    octave = 1 if 13 <= n_bar <= 20 else 0
    fc0, fc1 = (450, 900) if n_bar < 8 else ((550, 1100) if n_bar < 33 else (600, 1200))
    if 4 <= n_bar <= 7:                                   # tensão da cena 2: filtro fecha
        fc0, fc1 = 380, 650
    music.add(bar(n_bar), i_pad(CH[ch], BAR + 0.5, gain=1.0, fc0=fc0, fc1=fc1, attack=0.35, release=0.5, octave=octave), g)
    if 4 <= n_bar <= 39 and n_bar not in (28, 29, 30, 31, 32):
        music.add(bar(n_bar), i_bass(BASS[ch], 1.0), 0.55 if n_bar >= 8 else 0.25 + 0.08 * (n_bar - 4))
        if 8 <= n_bar <= 27:
            music.add(bar(n_bar, 2), i_bass(BASS[ch], 0.7), 0.35)

# =========================================================== VINHETA (0 – 18.22)
amb.add(1.5, i_rumble(16.3) * np.concatenate([np.linspace(0, 1, int(2 * SR)), np.ones(int(14.3 * SR))])[: int(16.3 * SR)], 0.03)
motif(2.5, ["D2"], 0.34); motif(4.5, ["A2"], 0.30); motif(6.0, ["F3"], 0.28)
fx.add(6.6, i_reverse(0.9, 0.6), 0.35)
music.add(7.5, i_pad(CH["Dm"], 5.0, gain=1.0, fc0=450, fc1=800, attack=0.6, release=1.0), 0.42)
music.add(7.5, i_shimmer(["D3", "A3", "D4"], 5.0, gain=0.8), 0.22)
hits.add(7.5, i_hit_soft(), 0.5)
hits.add(12.0, i_sub_drop(55, 30, 2.0), 0.45)
music.add(12.0, i_ping(hz("D5")), 0.35)
music.add(12.3, i_pad(CH["Dm"], 5.5, gain=1.0, fc0=380, fc1=900, attack=0.4, release=0.4), 0.38)
fx.add(12.7, i_riser(5.0, 120, 1500), 0.32)
grid_t = 13.7
while grid_t < 17.6:                                     # taikos suaves acelerando (não são "tiques")
    perc.add(grid_t, i_taiko(False, soft=True), 0.3 + 0.25 * (grid_t - 13.7) / 4)
    grid_t += 1.0 if grid_t < 15.7 else 0.5
# 17.7 – 18.22: silêncio (feito no master)

# =========================================================== CENA 1 GANCHO (c0–3)
hits.add(bar(0), i_hit_soft(), 0.7, onset=True)
music.add(bar(0) + 0.1, i_drone(hz("D2"), 7.5), 0.22)
amb.add(bar(0), i_rumble(90.1), 0.016)                   # cola grave por todo o conteúdo
motif(bar(0), ["D3", "A3", "F4"], 0.28)
for t in (bar(0, 3), bar(1, 3), bar(2, 1)):              # batimento sob as palavras (na grade)
    perc.add(t, i_heartbeat(), 0.8, onset=True)
fx.add(c(4.9), i_swell(0.6), 0.25)
hits.add(c(5.5), i_braam(hz("D1"), 2.6), 0.55, onset=True)          # "ATÉ AGORA." = c2 tempo 4
hits.add(c(5.5), i_sub_drop(55, 30, 2.4), 0.6)
hits.add(c(5.5), i_hit(0.8, 2.5), 0.55)

# =========================================================== CENA 2 DOR (c4–7)
whoosh_pan(bar(4), 0.25)
hits.add(bar(4), i_hit_soft(), 0.45, onset=True)
motif(bar(4), ["D3", "A3", "F4"], 0.26)
fx.add(bar(6), i_riser(3.75, 150, 1600), 0.36)
for k in range(8):                                       # taikos em semínimas crescendo (c6–c7)
    perc.add(bar(6, k), i_taiko(True, soft=True), 0.35 + 0.05 * k, onset=True)
fill(7, 0.75)
# 33.97 – 34.22: silêncio (master)

# =========================================================== CENA 3 SOLUÇÃO (c8–12)
hits.add(bar(8), i_hit(1.1, 3.2), 0.85, onset=True)      # "CIPREM"
hits.add(bar(8), i_braam(hz("D1"), 3.5), 0.75)
hits.add(bar(8), i_sub_drop(55, 28, 3.0), 0.75)
fx.add(bar(8) - 0.9, i_reverse(0.9, 0.9), 0.4)
for n in range(8, 13):
    perc.add(bar(n), i_taiko(True), 0.7, onset=True)
    perc.add(bar(n, 2), i_taiko(False, soft=True), 0.35, onset=True)
music.add(bar(8) + 1.0, i_shimmer(["D4", "A4", "D5"], 6.0, gain=0.8), 0.22)
fx.add(bar(10, 2) - 0.6, i_reverse(0.6, 0.7), 0.3)
hits.add(bar(10, 2), i_hit(0.7, 2.0), 0.55, onset=True)  # "Brita produzida aqui" = c10 tempo 3
fill(12, 0.7)

# =========================================================== CENA 4 PRODUTOS (c13–20)
whoosh_pan(bar(13), 0.25)
hits.add(bar(13), i_hit_soft(), 0.4, onset=True)
for n in range(13, 21):
    if n == 17: continue                                 # respiro
    perc.add(bar(n), i_taiko(True), 0.6, onset=True)
    perc.add(bar(n, 2), i_taiko(False, soft=True), 0.4, onset=True)
scale = ["D4", "E4", "F4", "G4", "A4", "Bb4", "C5"]
for k, note in enumerate(scale):                         # produtos: 27,5 + 1,5k s (todos na grade)
    music.add(c(27.5 + 1.5 * k), i_ping(hz(note)), 0.4, pan=-0.3, onset=True)
for tt in (29.2, 32.4, 35.6, 38.8):                      # cortes de plano: só ar, sem ritmo
    whoosh_pan(c(tt), 0.14, 0.6, 1400)
music.add(c(38.0), i_ping(hz("D5")), 0.3, pan=0.3)
fill(20, 0.7)

# =========================================================== CENA 5 GRUPO (c21–27)
hits.add(bar(21), i_hit(0.9, 2.4), 0.65, onset=True)
for n in range(21, 28):
    perc.add(bar(n), i_taiko(True), 0.7, onset=True)
    perc.add(bar(n, 2), i_taiko(True, soft=True), 0.45, onset=True)
    if n < 27:
        for k in range(8):
            perc.add(bar(n, k * 0.5), i_shaker(), 0.16 if k % 2 == 0 else 0.09)
music.add(bar(21) + 1.5, i_shimmer(["D4", "A4", "F5"], 5.0, gain=0.7), 0.2)
for tt in (44.8, 47.6, 50.4, 53.2):                      # cortes de plano
    whoosh_pan(c(tt), 0.16, 0.6, 1400)
for tt in (46.0, 51.0, 53.5):                            # bullets (todos na grade)
    music.add(c(tt), i_ping(hz("A4")), 0.3, pan=0.4, onset=True)
fx.add(bar(27), i_swell(1.8), 0.3)
fill(27, 0.7)

# =========================================================== CENA 6 OBRAS (c28–32)
hits.add(bar(28), i_hit(0.8, 2.0), 0.55, onset=True)
music.add(bar(28), i_bass("Bb1", 3.9), 0.4); music.add(bar(30), i_bass("C2", 3.9), 0.4)
for n in range(28, 32):
    for k in range(4):
        t = bar(n, k)
        if c(62.5) <= t < c(63.5): continue              # 1 s sem pulso depois do hit
        perc.add(t, lp(sine(46, 0.45) * exp_decay(int(0.45 * SR), 0.14) * soft_attack(int(0.45 * SR), 6), 120), 0.55, onset=True)
for k in range(3):
    music.add(bar(29, 2 + k), i_ping(hz("A4")), 0.25, pan=-0.4 + 0.4 * k, onset=True)   # chips
fx.add(c(60.0), i_riser(2.5, 180, 2000), 0.36)
fx.add(c(60.0), i_swell(2.4), 0.25)
hits.add(c(62.5), i_hit(1.0, 3.0), 0.8, onset=True)      # "Quem constrói aqui" = c31 tempo 2
hits.add(c(62.5), i_sub_drop(55, 28, 2.8), 0.7)
music.add(c(62.6), i_shimmer(["D4", "A4", "D5"], 4.0, gain=0.8), 0.2)
fill(32, 0.45)

# =========================================================== CENA 7 PARCERIA (c33–39)
hits.add(bar(33), i_hit(0.7, 2.6), 0.5, onset=True)
motif(bar(33), ["D3", "A3", "F#4"], 0.3)
music.add(bar(33), i_shimmer(["D4", "F#4", "A4", "D5"], 9.0, gain=0.9), 0.22)
for n in range(33, 38):
    perc.add(bar(n), i_taiko(True, soft=True), 0.4, onset=True)
whoosh_pan(c(68.5), 0.2, 0.7, 1200)
for k, (tt, note) in enumerate(((69.0, "D5"), (72.0, "F#5"), (75.0, "A5"))):
    whoosh_pan(c(tt), 0.18, 0.6, 1400)
    music.add(c(tt), i_ping(hz(note), 2.0), 0.4, pan=-0.5 + 0.5 * k, onset=True)
# 97.72 – 98.22: silêncio (master)

# =========================================================== CENA 8 FINAL (c40–44)
hits.add(bar(40), i_braam(hz("D1"), 4.0), 0.7, onset=True)
hits.add(bar(40), i_hit(1.1, 4.0), 0.8)
hits.add(bar(40), i_sub_drop(50, 30, 3.0), 0.6)
motif(bar(40) + 0.4, ["D3", "A3", "F#4"], 0.3)
music.add(bar(40) + 0.3, i_shimmer(["D4", "F#4", "A4", "D5"], 9.0, gain=1.0), 0.24)
music.add(bar(41), i_pad(CH["Dmaj5"], 8.5, gain=1.0, fc0=500, fc1=1300, attack=1.5, release=2.5), 0.45)
music.add(bar(41), i_bass("D2", 2.5), 0.35)
music.add(c(84.5), i_ping(hz("D5")), 0.3, onset=True)                       # contatos
music.add(c(86.5), i_piano(hz("D5"), 3.5, 0.7), 0.4)                        # assinatura
music.add(c(86.5), i_piano(hz("A4"), 3.5, 0.7), 0.25)

# ------------------------------------------------------------------ master
def rms_env(x, win=0.05):
    n = int(win * SR)
    return np.sqrt(np.convolve(x ** 2, np.ones(n) / n, mode="same") + 1e-12)

def gain_curve(t_pts, g_pts):
    return np.interp(np.arange(N) / SR, t_pts, g_pts)

M = music.stereo(); P = perc.stereo(); F = fx.stereo(); A = amb.stereo(); H = hits.stereo()
duck = 1 - 0.30 * np.clip(rms_env(H.mean(axis=1)) / 0.2, 0, 1)      # música cede ~3 dB nos hits
mix = (M + P) * duck[:, None] + F + A + H

def cut(mix, t0, t1):
    a, b = int(t0 * SR), int(t1 * SR); r = int(0.008 * SR)
    mix[a:b] = 0
    mix[a - r:a] *= np.linspace(1, 0, r)[:, None]
    mix[b:b + r] *= np.linspace(0, 1, r)[:, None]
for t0, t1 in ((17.7, C0), (bar(8) - 0.25, bar(8)), (bar(40) - 0.5, bar(40))):
    cut(mix, t0, t1)

mix *= gain_curve([0, 1.5, 1.6, c(87.4), DUR], [0, 0, 1, 1, 0])[:, None]

# passa-baixas suave no master, compressão 1.5:1 acima de -14 dBFS, alvo -16 LUFS, pico <= -3 dBTP
mix = np.stack([lp(mix[:, 0], 9000), lp(mix[:, 1], 9000)], axis=1)
e = rms_env(mix.mean(axis=1), 0.08)
thr = 10 ** (-14 / 20)
mix *= np.where(e > thr, (thr / e) ** (1 / 3), 1.0)[:, None]
rms = np.sqrt(np.mean(mix ** 2))
mix *= 10 ** (-17.2 / 20) / rms                          # RMS -17.2 dBFS ~ -16 LUFS (medido na v1)
peak_lim = 10 ** (-3 / 20)
over = np.abs(mix) > peak_lim
if over.any():
    mix = np.where(over, np.sign(mix) * (peak_lim + (np.abs(mix) - peak_lim) * 0.15), mix)
mix = np.clip(mix, -0.99, 0.99)

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "public", "audio", "score.wav")
wavfile.write(out, SR, (mix * 32767).astype(np.int16))

# relatório
sec_rms = [20 * math.log10(np.sqrt(np.mean(mix[i * SR:(i + 1) * SR] ** 2)) + 1e-9) for i in range(int(DUR))]
print(f"score.wav: {DUR} s, pico {20*math.log10(np.abs(mix).max()):.1f} dBFS, RMS médio {20*math.log10(np.sqrt(np.mean(mix**2))):.1f} dBFS")
print("RMS por segundo (dBFS):", " ".join(f"{i}:{v:.0f}" for i, v in enumerate(sec_rms)))
ons = sorted(perc.onsets + hits.onsets + music.onsets)
off = [((t - C0) / BEAT) % 1 for t in ons if t >= C0]
off = [min(o, 1 - o) for o in off]
print(f"onsets no conteúdo: {len(off)}; fora da grade de 0,5 s (>10 ms): {sum(1 for o in off if o * BEAT > 0.01)}")
print("fronteiras de cena em cabeça de compasso:", all(abs(((C0 + s) - C0) / BAR - round(((C0 + s) - C0) / BAR)) < 1e-6 for s in (0, 8, 16, 26, 42, 56, 66, 80)))
