#!/usr/bin/env python3
"""
Desenho de som do vídeo CIPREM (vinheta + 8 cenas), estilo trailer.

Gera public/audio/score.wav (estéreo, 48 kHz, 108.29 s) totalmente sintetizado:
sub drops, braams, risers, taikos, tiques, pads, shimmer, reversos, hits e silêncios,
posicionados segundo a segundo conforme o roteiro de som.

Uso:  python build_score.py [saida.wav]
Requer numpy e scipy.
"""
import sys, math, os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 108.29                 # vinheta 18.22 s + conteúdo 90 s + folga do último quadro
N = int(DUR * SR)
C0 = 18.22                   # início do conteúdo (fim da vinheta)
BEAT = 0.6                   # 100 BPM
rng = np.random.default_rng(20260904)

def c(t):                    # tempo do conteúdo -> tempo absoluto
    return C0 + t

# ------------------------------------------------------------------ utilidades
def t_axis(dur):
    return np.arange(int(dur * SR)) / SR

def env_adsr(n, a, d, s, r, total=None):
    """Envelope em amostras. a/d/r em segundos, s nível de sustain."""
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.zeros(n)
    i = 0
    k = min(a, n); e[:k] = np.linspace(0, 1, k, endpoint=False); i += k
    k = min(d, n - i); e[i:i + k] = np.linspace(1, s, k, endpoint=False); i += k
    k = max(0, n - i - r); e[i:i + k] = s; i += k
    k = n - i
    if k > 0: e[i:] = np.linspace(e[i - 1] if i > 0 else s, 0, k)
    return e

def exp_decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))

def sine(freq, dur, phase=0.0):
    t = t_axis(dur)
    return np.sin(2 * np.pi * freq * t + phase)

def sine_glide(f0, f1, dur, curve=1.0):
    t = t_axis(dur)
    x = (t / dur) ** curve
    f = f0 * (f1 / f0) ** x
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)

def saw(freq, dur, detune_cents=0.0):
    f = freq * 2 ** (detune_cents / 1200)
    t = t_axis(dur)
    return 2 * ((t * f) % 1.0) - 1

def noise(dur):
    return rng.standard_normal(int(dur * SR))

def brown(dur):
    x = np.cumsum(rng.standard_normal(int(dur * SR)))
    x -= np.convolve(x, np.ones(2000) / 2000, mode="same")  # tira o passeio lento
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
    """Passa-baixas com corte variando no tempo (fc_curve com o mesmo tamanho de sig)."""
    out = np.zeros_like(sig)
    zi = None
    for i in range(0, len(sig), block):
        fc = float(np.clip(fc_curve[min(i + block // 2, len(sig) - 1)], 30, SR / 2 - 200))
        sos = butter(order, fc, btype="low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + block], zi = sosfilt(sos, sig[i:i + block], zi=zi)
    return out

def sweep_bp(sig, fc_curve, width=0.8, block=512):
    out = np.zeros_like(sig)
    zi = None
    for i in range(0, len(sig), block):
        fc = float(np.clip(fc_curve[min(i + block // 2, len(sig) - 1)], 60, SR / 2 - 400))
        sos = butter(2, [fc / (1 + width), min(fc * (1 + width), SR / 2 - 200)], btype="band", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + block], zi = sosfilt(sos, sig[i:i + block], zi=zi)
    return out

def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)

_ir_cache = {}
def reverb(sig, decay=2.0, mix=0.35, predelay=0.02):
    """Reverb por convolução com IR sintética estéreo. Retorna (L, R)."""
    key = round(decay, 2)
    if key not in _ir_cache:
        n = int(decay * 3 * SR)
        t = np.arange(n) / SR
        e = np.exp(-t / decay * 3)
        irl = rng.standard_normal(n) * e
        irr = rng.standard_normal(n) * e
        irl = lp(irl, 6000); irr = lp(irr, 6000)
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
        self.name = name
        self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, t, sig, gain=1.0, pan=0.0):
        if isinstance(sig, tuple):
            l, r = sig
        else:
            l, r = pan_lr(sig, pan)
        i = int(t * SR)
        if i >= N or i < 0: return
        k = min(len(l), N - i)
        self.L[i:i + k] += l[:k] * gain; self.R[i:i + k] += r[:k] * gain
    def stereo(self):
        return np.stack([self.L, self.R], axis=1)

# ------------------------------------------------------------------ notas
def hz(name):
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)

CH = {
    "Dm":  ["D3", "F3", "A3"],
    "Bb":  ["Bb2", "D3", "F3"],
    "F":   ["F3", "A3", "C4"],
    "C":   ["C3", "E3", "G3"],
    "Dm5": ["D3", "F3", "A3", "D4", "F4"],
    "Dmaj": ["D3", "F#3", "A3", "D4"],
    "Dmaj5": ["D3", "F#3", "A3", "D4", "F#4", "A4"],
    "Bbchoir": ["Bb2", "F3", "Bb3", "D4", "F4"],
    "Cchoir": ["C3", "G3", "C4", "E4", "G4"],
}
BASS = {"Dm": "D2", "Bb": "Bb1", "F": "F2", "C": "C2", "Dm5": "D2", "Dmaj": "D2", "Dmaj5": "D2", "Bbchoir": "Bb1", "Cchoir": "C2"}

# ------------------------------------------------------------------ instrumentos
def i_sub_drop(f0=55, f1=30, dur=2.5):
    s = sine_glide(f0, f1, dur, curve=0.6)
    return s * env_adsr(len(s), 0.01, 0.4, 0.7, 1.2)

def i_braam(f=36.71, dur=3.0, bright=1.0):
    n = int(dur * SR)
    voices = 0
    for cents in (-9, -4, 3, 8):
        voices = voices + saw(f, dur, cents) * 0.5 + saw(f * 2, dur, cents * 0.5) * 0.35
    t = np.arange(n) / SR
    fc = 150 + (1400 * bright) * (1 - np.exp(-t / 0.5))
    v = sweep_lp(voices, fc, order=2)
    v = softclip(v * 1.8, 1.6)
    v *= env_adsr(n, 0.25, 0.6, 0.75, 1.0)
    return reverb(v, decay=2.2, mix=0.3)

def i_hit(size=1.0, tail=2.5):
    dur = 0.6
    n = int(dur * SR)
    body = lp(noise(dur), 2500) * exp_decay(n, 0.12)
    thump = sine_glide(90, 45, dur) * exp_decay(n, 0.25)
    sub = sine(42, dur) * exp_decay(n, 0.5)
    x = body * 0.8 + thump * 1.2 + sub * 0.9 * size
    x = softclip(x, 1.4)
    return reverb(x, decay=tail, mix=0.45 if tail > 1 else 0.15)

def i_hit_dry():
    dur = 0.5; n = int(dur * SR)
    x = lp(noise(dur), 900) * exp_decay(n, 0.08) + sine_glide(70, 38, dur) * exp_decay(n, 0.3)
    return softclip(x, 1.3)

def i_riser(dur=3.0, f0=180, f1=2400, tone=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = t / dur
    fc = f0 * (f1 / f0) ** (x ** 1.4)
    nz = sweep_bp(noise(dur), fc, width=0.9)
    trem_rate = 4 + 26 * x ** 2
    trem = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * np.cumsum(trem_rate) / SR))
    e = (x ** 2.2) * 1.0
    out = nz * e * trem
    if tone:
        gl = sine_glide(f0 / 2, f1 / 4, dur, curve=1.5) * e * 0.5 * trem
        out = out + gl
    return out

def i_swell(dur=1.5, f1=3000, f2=9000):
    n = int(dur * SR)
    x = (np.arange(n) / n) ** 3
    return bp(noise(dur), f1, f2) * x

def i_reverse(dur=0.8, size=0.8):
    l, r = i_hit(size, tail=dur)
    l = l[: int(dur * SR)][::-1]; r = r[: int(dur * SR)][::-1]
    fade = np.linspace(0, 1, len(l)) ** 2
    return l * fade, r * fade

def i_taiko(low=True):
    dur = 0.7; n = int(dur * SR)
    f0, f1 = (130, 52) if low else (200, 90)
    x = sine_glide(f0, f1, dur, curve=0.5) * exp_decay(n, 0.22)
    x += lp(noise(dur), 1800) * exp_decay(n, 0.02) * 0.6
    x = softclip(x * 1.2, 1.2)
    return reverb(x, decay=0.9, mix=0.25)

def i_kick():
    dur = 0.4; n = int(dur * SR)
    x = sine_glide(160, 42, dur, curve=0.4) * exp_decay(n, 0.12)
    x += lp(noise(dur), 3000) * exp_decay(n, 0.008)
    return softclip(x * 1.3, 1.3)

def i_snare(gain=1.0):
    dur = 0.25; n = int(dur * SR)
    x = bp(noise(dur), 900, 5000) * exp_decay(n, 0.05) + sine(190, dur) * exp_decay(n, 0.03) * 0.6
    return x * gain

def i_hat(dur=0.05):
    n = int(dur * SR)
    return hp(noise(dur), 7000) * exp_decay(n, 0.012)

def i_tick(kind="clock"):
    if kind == "clock":
        dur = 0.06; n = int(dur * SR)
        return (sine(2100, dur) * 0.6 + hp(noise(dur), 3000) * 0.5) * exp_decay(n, 0.008)
    if kind == "glass":
        dur = 0.5; n = int(dur * SR)
        x = sine(3200, dur) * exp_decay(n, 0.09) + sine(3200 * 2.41, dur) * exp_decay(n, 0.05) * 0.4
        return reverb(x * 0.6, decay=1.0, mix=0.35)
    if kind == "metal":
        dur = 0.35; n = int(dur * SR)
        x = 0
        for k, a in ((1.0, 1), (1.83, 0.6), (2.71, 0.45), (3.96, 0.3)):
            x = x + sine(1500 * k, dur) * a
        x = x * exp_decay(n, 0.045) + hp(noise(dur), 5000) * exp_decay(n, 0.006)
        return reverb(x * 0.5, decay=0.8, mix=0.3)
    raise ValueError(kind)

def i_ping(freq, dur=1.4):
    n = int(dur * SR)
    x = sine(freq, dur) * exp_decay(n, 0.45) + sine(freq * 2.76, dur) * exp_decay(n, 0.12) * 0.35 + sine(freq * 5.4, dur) * exp_decay(n, 0.05) * 0.15
    return reverb(x * 0.7, decay=1.6, mix=0.4)

def i_piano(freq, dur=3.5, bright=1.0):
    n = int(dur * SR)
    x = 0
    for k in range(1, 7):
        x = x + sine(freq * k, dur) * (1 / k ** 1.3) * bright ** (k - 1) * exp_decay(n, 1.4 / k ** 0.8)
    x = x * (1 - np.exp(-np.arange(n) / (0.004 * SR)))
    return reverb(x * 0.8, decay=2.8, mix=0.4)

def i_pad(chord, dur, gain=1.0, fc0=900, fc1=None, attack=1.2, release=1.5, octave=0, vib=0.003):
    """Pad de cordas sintéticas: 2 serras detunadas + seno por voz, filtro com abertura lenta."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    L = np.zeros(n); R = np.zeros(n)
    for i, name in enumerate(chord):
        f = hz(name) * 2 ** octave
        v = 1 + vib * np.sin(2 * np.pi * (4.6 + 0.3 * i) * t + i)
        ph = 2 * np.pi * np.cumsum(f * v) / SR
        s = np.sin(ph) * 0.6
        left = saw(f, dur, -6 - 2 * i) * 0.35 + s
        right = saw(f, dur, 6 + 2 * i) * 0.35 + s
        L += left; R += right
    fc1 = fc1 or fc0 * 1.6
    fc = fc0 + (fc1 - fc0) * (1 - np.exp(-t / (dur * 0.5)))
    L = sweep_lp(L, fc); R = sweep_lp(R, fc)
    e = env_adsr(n, attack, 0.3, 0.9, release)
    L *= e; R *= e
    wl, _ = reverb(L, decay=2.4, mix=0.3); _, wr = reverb(R, decay=2.4, mix=0.3)
    return wl * gain / len(chord), wr * gain / len(chord)

def i_shimmer(chord, dur, gain=1.0):
    return i_pad(chord, dur, gain=gain, fc0=2500, fc1=4500, attack=1.5, release=2.0, octave=1, vib=0.004)

def i_bass(note, dur=0.28):
    n = int(dur * SR)
    f = hz(note)
    x = lp(saw(f, dur) * 0.7 + sine(f, dur) * 0.6, 260) * exp_decay(n, 0.11)
    return softclip(x * 1.4, 1.2)

def i_drone(freq, dur, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sine(freq, dur) + 0.5 * sine(freq * 2.002, dur) + 0.25 * sine(freq * 3.0, dur)
    x *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.17 * t)
    x *= env_adsr(n, 0.8, 0.1, 1.0, 1.0)
    return x * gain

def i_rumble(dur, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = lp(brown(dur), 110, order=2)
    x *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * t) * np.sin(2 * np.pi * 0.07 * t + 1)
    return x / (np.abs(x).max() + 1e-9) * gain

def i_whoosh(dur=0.6, f_peak=2500):
    n = int(dur * SR); t = np.arange(n) / SR
    x = t / dur
    fc = 300 + (f_peak - 300) * np.sin(np.pi * x) ** 1.5 + 200 * x
    nz = sweep_bp(noise(dur), fc, width=0.7)
    e = np.sin(np.pi * x) ** 2
    return nz * e

def i_heartbeat():
    """Dois batimentos surdos (lub-dub)."""
    dur = 0.5; n = int(dur * SR)
    a = sine_glide(80, 45, 0.25) * exp_decay(int(0.25 * SR), 0.07)
    b = sine_glide(70, 40, 0.25) * exp_decay(int(0.25 * SR), 0.06) * 0.7
    x = np.zeros(n); x[: len(a)] += a; x[int(0.17 * SR): int(0.17 * SR) + len(b)] += b
    return lp(x, 200)

# ------------------------------------------------------------------ stems
music = Stem("music"); perc = Stem("perc"); fx = Stem("fx"); amb = Stem("amb"); hits = Stem("hits")

def whoosh_pan(t, dur=0.6, gain=1.0, f_peak=2500):
    """Whoosh que cruza da esquerda para a direita, acompanhando o reveal dos textos."""
    w = i_whoosh(dur, f_peak)
    n = len(w); p = np.linspace(-0.8, 0.8, n)
    th = (p + 1) * np.pi / 4
    fx.add(t, (w * np.cos(th), w * np.sin(th)), gain)

def taiko_grid(t0, t1, pattern, gain=1.0, low=True):
    """pattern: lista de deslocamentos em batidas dentro de um compasso de 4 tempos."""
    bar = 4 * BEAT
    t = t0
    while t < t1 - 1e-6:
        for off in pattern:
            tt = t + off * BEAT
            if tt < t1:
                perc.add(tt, i_taiko(low), gain)
        t += bar

def grid(t0, t1, step, fn, gain=1.0, accent=None):
    t = t0; k = 0
    while t < t1 - 1e-6:
        g = gain * (accent(k) if accent else 1.0)
        perc.add(t, fn(), g)
        t += step; k += 1

# =========================================================== VINHETA (0 – 18.22)
amb.add(1.5, i_rumble(16.5, gain=1.0) * np.concatenate([np.linspace(0, 1, int(2 * SR)), np.ones(int(14.5 * SR))])[: int(16.5 * SR)], 0.032)
music.add(2.5, i_piano(hz("D2"), 4.0, bright=0.8), 0.28)
music.add(4.5, i_piano(hz("A2"), 4.0, bright=0.8), 0.24)
music.add(6.0, i_piano(hz("F3"), 4.0, bright=0.9), 0.22)
hits.add(6.6, i_reverse(0.9, 0.9), 0.55)
hits.add(7.5, i_braam(hz("D1"), 3.2, bright=0.8), 0.6)
music.add(7.5, i_shimmer(["D3", "A3", "D4"], 5.0, gain=0.8), 0.35)
amb.add(7.5, i_rumble(10.7, gain=1.0), 0.05)
music.add(9.0, i_pad(CH["Dm"], 3.5, gain=1.0, fc0=500, fc1=900, attack=0.8, release=0.6), 0.5)
grid(9.0, 12.0, BEAT, lambda: i_tick("clock"), gain=0.35)
hits.add(12.0, i_sub_drop(60, 28, 2.2), 0.8)
fx.add(12.0, i_tick("metal"), 0.9)
music.add(12.4, i_pad(CH["Dm"], 5.4, gain=0.5, fc0=400, fc1=700, attack=0.3, release=0.5), 0.35)
fx.add(12.5, i_riser(5.2, 150, 3200), 0.55)
# tiques dobrando de velocidade a cada 1,5 s
for a, b, step in ((12.5, 14.0, 0.6), (14.0, 15.5, 0.3), (15.5, 17.0, 0.15), (17.0, 17.75, 0.075)):
    grid(a, b, step, lambda: i_tick("clock"), gain=0.3)
# 17.8 – 18.22: silêncio (nada é colocado; o corte é feito no master)

# =========================================================== CENA 1 GANCHO (c 0–8)
hits.add(c(0.0), i_hit_dry(), 0.9)
music.add(c(0.1), i_drone(hz("D2"), 5.6, gain=1.0), 0.28)
for k in range(4):                                   # batimento a cada 1,2 s de 1,5 a 5,1 s
    perc.add(c(1.5 + k * 1.2), i_heartbeat(), 0.9)
for k in range(7):                                   # um tique por palavra (12 frames = 0,48 s)
    fx.add(c(1.5 + k * 0.48), i_tick("clock"), 0.28, pan=-0.5 + k * 0.17)
fx.add(c(4.8), i_swell(0.7, 2500, 8000), 0.45)
hits.add(c(5.5), i_braam(hz("D1"), 3.0, bright=1.1), 0.95)
hits.add(c(5.5), i_sub_drop(55, 30, 2.6), 0.9)
hits.add(c(5.5), i_hit(1.0, 3.0), 0.9)
music.add(c(5.6), i_drone(hz("D3"), 2.6, gain=1.0), 0.18)
grid(c(6.5), c(8.0), BEAT, lambda: i_tick("clock"), gain=0.3)

# =========================================================== CENA 2 DOR (c 8–16)
whoosh_pan(c(8.0), 0.6, 0.6)
music.add(c(8.0), i_pad(CH["Dm"], 8.2, gain=1.0, fc0=350, fc1=1400, attack=0.6, release=0.2), 0.42)
t = c(8.0); k = 0
while t < c(15.8):                                   # baixo em colcheias crescendo
    g = 10 ** ((-30 + 12 * (t - c(8.0)) / 8) / 20) * 3.2
    perc.add(t, i_bass("D1"), g); t += 0.3; k += 1
fx.add(c(8.5), i_tick("metal"), 0.6)
fx.add(c(8.5), i_swell(0.5, 3000, 8000), 0.3)
fx.add(c(12.0), i_tick("glass"), 0.5, pan=0.2)
fx.add(c(12.5), i_riser(3.5, 200, 3800), 0.75)
fx.add(c(12.5), i_swell(3.4, 3000, 9000), 0.5)
t = c(12.5)
while t < c(14.8):
    perc.add(t, i_taiko(True), 0.7); t += BEAT
t = c(14.8)
while t < c(15.95):
    perc.add(t, i_taiko(False), 0.65); t += 0.3
# c(16.0)–c(16.2): silêncio, feito no master

# =========================================================== CENA 3 SOLUÇÃO (c 16–26)
T3 = c(16.0)
hits.add(T3, i_hit(1.2, 3.2), 1.0)
hits.add(T3, i_braam(hz("D1"), 3.5, bright=1.2), 1.0)
hits.add(T3, i_sub_drop(55, 28, 3.0), 1.0)
fx.add(T3 - 0.9, i_reverse(0.9, 1.0), 0.6)
# tema principal: Dm (2 compassos) -> Bb (2) -> F (2) -> C (2), 2,4 s por compasso
prog = ["Dm", "Dm", "Bb", "Bb", "F", "F", "C", "C"]
for i, ch in enumerate(prog):
    t0 = T3 + i * 2.4
    if t0 >= c(26.0): break
    music.add(t0, i_pad(CH[ch], 2.6, gain=1.0, fc0=700, fc1=1900, attack=0.35, release=0.4), 0.5)
    music.add(t0, i_bass(BASS[ch], 1.2), 0.9)
taiko_grid(T3, c(26.0), [0, 2], gain=0.8)
grid(T3 + BEAT, c(26.0), 2 * BEAT, lambda: i_tick("metal"), gain=0.45)
music.add(c(17.5), i_shimmer(["D4", "A4", "D5"], 5.0, gain=0.7), 0.3)
fx.add(c(20.3), i_reverse(0.7, 0.8), 0.5)
hits.add(c(21.0), i_hit(0.8, 2.0), 0.8)
perc.add(c(21.0), i_taiko(True), 1.0); perc.add(c(21.15), i_taiko(True), 0.8)
fx.add(c(24.8), i_reverse(1.2, 0.9), 0.6)

# =========================================================== CENA 4 PRODUTOS (c 26–42)
T4 = c(26.0)
whoosh_pan(T4, 0.6, 0.7)
prog4 = ["Dm", "Bb", "Dm", "Bb", "F", "C", "Dm", "Bb"]
for i, ch in enumerate(prog4):
    t0 = T4 + i * 2.0
    swell_g = 0.22 + 0.16 * i / 7                                    # o pad cresce ao longo da cena
    music.add(t0, i_pad(CH[ch], 2.2, gain=0.9, fc0=700 + 120 * i, fc1=1600 + 200 * i, attack=0.25, release=0.3, octave=1), swell_g)
    music.add(t0, i_bass(BASS[ch], 0.9), 0.8)
    music.add(t0 + 1.0, i_bass(BASS[ch], 0.5), 0.6)
# padrão motor em duas metades: a primeira mais seca, um respiro sem bumbo em 32,4–33,6 e a segunda mais cheia
grid(T4, c(32.4), 2 * BEAT, i_kick, gain=0.8)                       # bumbo em 1 e 3
grid(c(33.6), c(40.5), 2 * BEAT, i_kick, gain=1.0)
taiko_grid(c(33.6), c(40.5), [1, 3], gain=0.6, low=False)           # taiko em 2 e 4 só na segunda metade
grid(T4, c(32.4), BEAT / 2, i_hat, gain=0.3, accent=lambda k: 1.0 if k % 2 == 0 else 0.5)
grid(c(33.6), c(40.5), BEAT / 4, i_hat, gain=0.32, accent=lambda k: 1.0 if k % 4 == 0 else (0.6 if k % 2 == 0 else 0.4))
for k in range(4):                                                  # virada de taiko no respiro
    perc.add(c(33.0 + 0.15 * k), i_taiko(False), 0.5 + 0.15 * k)
scale = ["D4", "E4", "F4", "G4", "A4", "Bb4", "C5"]
for k, note in enumerate(scale):                                   # um produto a cada 1,5 s
    tt = c(27.5 + 1.5 * k)
    fx.add(tt, i_tick("metal"), 0.7, pan=-0.6)
    music.add(tt, i_ping(hz(note)), 0.55, pan=-0.3)
for tt in (29.2, 32.4, 35.6, 38.8):                                 # cortes de plano
    whoosh_pan(c(tt), 0.5, 0.45, 3000)
fx.add(c(38.0), i_tick("glass"), 0.55, pan=0.3)
music.add(c(38.0), i_pad(CH["Dm5"], 4.0, gain=0.8, fc0=1200, fc1=3200, attack=0.4, release=0.6), 0.3)
fx.add(c(40.3), i_reverse(1.6, 1.0), 0.65)
t = c(40.4)
while t < c(41.9):                                                  # tercinas subindo
    perc.add(t, i_taiko(t < c(41.2)), 0.6 + 0.4 * (t - c(40.4)) / 1.5); t += BEAT / 3

# =========================================================== CENA 5 GRUPO (c 42–56)
T5 = c(42.0)
hits.add(T5, i_hit(1.0, 2.4), 0.95)
hits.add(T5, i_braam(hz("D1"), 2.2, bright=1.0), 0.7)
prog5 = ["Dm", "Dm", "Bb", "Bb", "F", "C", "Dm", "Dm", "Bb", "C", "Dm", "Dm"]
voices = 3
for i, ch in enumerate(prog5):
    t0 = T5 + i * 1.2
    chord = CH[ch]
    if t0 >= c(46.0): chord = chord + [chord[0].replace(chord[0][-1], str(int(chord[0][-1]) + 1))]
    if t0 >= c(51.0): chord = chord + [chord[1].replace(chord[1][-1], str(int(chord[1][-1]) + 1))]
    music.add(t0, i_pad(chord, 1.4, gain=1.0, fc0=800, fc1=2200, attack=0.2, release=0.3), 0.45)
    music.add(t0, i_bass(BASS[ch], 0.6), 0.9)
grid(T5, c(54.5), 2 * BEAT, i_kick, gain=1.0)
grid(T5 + BEAT, c(54.5), 2 * BEAT, lambda: i_snare(1.0), gain=0.55)
grid(T5, c(54.5), BEAT / 4, lambda: i_snare(0.35), gain=0.5, accent=lambda k: 1.0 if k % 4 == 0 else (0.7 if k % 2 == 0 else 0.45))
for tt in (44.8, 47.6, 50.4, 53.2):                                 # taiko em cada corte
    perc.add(c(tt), i_taiko(True), 1.0)
    whoosh_pan(c(tt), 0.45, 0.4, 2200)
music.add(c(43.5), i_shimmer(["D4", "A4", "F5"], 4.0, gain=0.7), 0.28)
for tt in (46.0, 51.0, 53.5):                                       # bullets
    whoosh_pan(c(tt), 0.5, 0.5, 2800)
    fx.add(c(tt) + 0.1, i_tick("glass"), 0.5, pan=0.5)
fx.add(c(54.3), i_swell(1.7, 2500, 9000), 0.6)
fx.add(c(54.5), i_riser(1.5, 300, 2500, tone=False), 0.5)

# =========================================================== CENA 6 OBRAS (c 56–66)
T6 = c(56.0)
hits.add(T6, i_hit(0.9, 2.0), 0.85)
grid(T6, c(62.4), BEAT, lambda: sine(46, 0.5) * exp_decay(int(0.5 * SR), 0.15), gain=0.8)   # pulso de sub em semínimas
music.add(T6, i_pad(CH["Bbchoir"], 3.4, gain=1.0, fc0=900, fc1=2600, attack=0.5, release=0.4), 0.5)
music.add(T6 + 3.2, i_pad(CH["Cchoir"], 3.6, gain=1.0, fc0=1000, fc1=2800, attack=0.4, release=0.4), 0.52)
music.add(T6, i_bass("Bb1", 1.5), 0.8); music.add(T6 + 3.2, i_bass("C2", 1.5), 0.8)
for k in range(3):
    fx.add(c(59.0 + 0.4 * k), i_tick("glass"), 0.5, pan=-0.5 + 0.5 * k)
fx.add(c(60.0), i_riser(2.5, 220, 4200), 0.85)
fx.add(c(60.0), i_swell(2.4, 3000, 10000), 0.55)
for a, b, step in ((60.0, 61.0, 0.3), (61.0, 61.8, 0.15), (61.8, 62.45, 0.075)):
    grid(c(a), c(b), step, lambda: i_tick("clock"), gain=0.35)
grid(c(60.0), c(62.4), BEAT / 2, lambda: i_taiko(False), gain=0.7)
hits.add(c(62.5), i_hit(1.1, 3.0), 1.0)
hits.add(c(62.5), i_sub_drop(55, 28, 2.8), 0.95)
music.add(c(62.6), i_pad(CH["Dm5"], 3.6, gain=1.0, fc0=1200, fc1=2000, attack=0.6, release=0.5), 0.45)
# 62.5–63.5: sem percussão (respiro); volta em meia intensidade
grid(c(63.6), c(65.6), 2 * BEAT, i_kick, gain=0.55)
grid(c(63.6), c(65.6), BEAT / 2, i_hat, gain=0.25)
fx.add(c(65.0), i_reverse(1.0, 0.9), 0.55)

# =========================================================== CENA 7 PARCERIA (c 66–80)
T7 = c(66.0)
hits.add(T7, i_hit(0.8, 2.6), 0.75)
for i in range(6):                                                  # Ré maior aberto, 2,4 s por compasso
    t0 = T7 + i * 2.4
    g = 1.0 if t0 < c(76.0) else 0.6
    music.add(t0, i_pad(CH["Dmaj5"] if i % 2 == 0 else CH["Dmaj"], 2.6, gain=1.0, fc0=1100, fc1=3000, attack=0.4, release=0.5), 0.42 * g)
    music.add(t0, i_bass("D2", 1.4), 0.7 * g)
music.add(T7, i_shimmer(["D4", "F#4", "A4", "D5"], 8.0, gain=0.9), 0.3)
grid(T7, c(76.0), 4 * BEAT, i_kick, gain=0.6)
grid(T7, c(76.0), BEAT / 2, i_hat, gain=0.2, accent=lambda k: 1.0 if k % 2 == 0 else 0.5)
whoosh_pan(c(68.5), 0.6, 0.35, 2000)
for k, (tt, note) in enumerate(((69.0, "D5"), (72.0, "F#5"), (75.0, "A5"))):
    whoosh_pan(c(tt), 0.5, 0.4, 2600)
    music.add(c(tt) + 0.05, i_ping(hz(note), 1.8), 0.55, pan=-0.5 + 0.5 * k)
# 79.5–80.0: silêncio no master

# =========================================================== CENA 8 FINAL (c 80–90)
T8 = c(80.0)
hits.add(T8, i_braam(hz("D1"), 4.0, bright=1.0), 0.9)
hits.add(T8, i_hit(1.2, 4.0), 1.0)
hits.add(T8, i_sub_drop(50, 30, 3.0), 0.8)
music.add(T8 + 0.2, i_shimmer(["D4", "F#4", "A4", "D5"], 8.5, gain=1.0), 0.32)
music.add(c(82.0), i_pad(CH["Dmaj5"], 8.0, gain=1.0, fc0=700, fc1=2400, attack=1.5, release=2.5), 0.45)
music.add(c(82.0), i_bass("D2", 2.0), 0.5)
fx.add(c(84.5), i_tick("glass"), 0.5, pan=0.0)
music.add(c(86.5), i_piano(hz("D5"), 3.5, bright=0.7), 0.5)
music.add(c(86.5), i_piano(hz("A4"), 3.5, bright=0.7), 0.3)

# ------------------------------------------------------------------ master
def rms_env(x, win=0.05):
    n = int(win * SR)
    k = np.ones(n) / n
    return np.sqrt(np.convolve(x ** 2, k, mode="same") + 1e-12)

def gain_curve(t_pts, g_pts):
    t = np.arange(N) / SR
    return np.interp(t, t_pts, g_pts)

M = music.stereo(); P = perc.stereo(); F = fx.stereo(); A = amb.stereo(); H = hits.stereo()

# ducking: música/percussão cedem 4 dB durante os hits grandes
duck = 1 - 0.37 * np.clip(rms_env(H.mean(axis=1)) / 0.25, 0, 1)
mix = (M * 1.0 + P * 0.9) * duck[:, None] + F * 0.9 + A * 1.0 + H * 1.0

# silêncios de impacto (cortes secos no master, com 5 ms de rampa)
def cut(mix, t0, t1):
    a, b = int(t0 * SR), int(t1 * SR); r = int(0.005 * SR)
    mix[a:b] = 0
    mix[a - r:a] *= np.linspace(1, 0, r)[:, None]
    mix[b:b + r] *= np.linspace(0, 1, r)[:, None]
for t0, t1 in ((17.8, C0), (c(16.0) - 0.2, c(16.0)), (c(79.5), c(80.0))):
    cut(mix, t0, t1)

# fades globais: silêncio até 1,5 s e fade final de 2,8 s
mix *= gain_curve([0, 1.5, 1.6, c(87.4), DUR], [0, 0, 1, 1, 0])[:, None]

# compressão leve (1.5:1 acima de -12 dBFS) + soft clip + normalização a -1 dBTP
e = rms_env(mix.mean(axis=1), 0.08)
thr = 10 ** (-12 / 20)
gr = np.where(e > thr, (thr / e) ** (1 / 3), 1.0)
mix *= gr[:, None]
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
mix *= (10 ** (-1 / 20)) / (np.abs(mix).max() + 1e-9)
mix *= 10 ** (-2.1 / 20)      # leva o programa de ~-12 para ~-14 LUFS (pico fica em ~-3 dBTP)

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "public", "audio", "score.wav")
wavfile.write(out, SR, (mix * 32767).astype(np.int16))

# relatório: RMS por segundo (anti-monotonia) e picos nos cues
sec_rms = [20 * math.log10(np.sqrt(np.mean(mix[i * SR:(i + 1) * SR] ** 2)) + 1e-9) for i in range(int(DUR))]
print(f"score.wav: {DUR} s, pico {20*math.log10(np.abs(mix).max()):.1f} dBFS, RMS médio {20*math.log10(np.sqrt(np.mean(mix**2))):.1f} dBFS")
print("RMS por segundo (dBFS):")
print(" ".join(f"{i}:{v:.0f}" for i, v in enumerate(sec_rms)))
