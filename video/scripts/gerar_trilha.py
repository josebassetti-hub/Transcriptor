"""Gera a trilha do vídeo institucional (60 s, WAV 44.1 kHz estéreo), estilo propaganda.

Síntese em Python puro (sem dependências): 100 bpm, pad de acordes, arpejo de
16 avos, baixo pulsado, bumbo e chimbal sintetizados, riser antes do final e
impacto no logo. Progressão D - Bm - G - A. Livre de direitos autorais.

Estrutura (em segundos):
  0.0 - 4.8   intro: pad + impacto inicial
  4.8 - 10.8  build: entra arpejo e bumbo
 10.8 - 44.4  cheio: bumbo, chimbal, baixo, arpejo (impactos suaves em 10,8 s e 22,8 s)
 44.4 - 50.4  clímax: riser
 50.4 - 60.0  final: impacto + pad, fade-out

Uso: python3 scripts/gerar_trilha.py [saida.wav]
"""
import math
import struct
import sys
import wave

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BPM = 100
BEAT = 60.0 / BPM        # 0.6 s
BAR = BEAT * 4           # 2.4 s

T_BUILD, T_FULL, T_RISER, T_END = 4.8, 10.8, 44.4, 50.4
CHAPTER_HITS = [10.8, 22.8]  # impactos suaves nas aberturas de capítulo

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

CHORDS = [[50, 54, 57, 62], [47, 50, 54, 59], [43, 47, 50, 55], [45, 49, 52, 57]]
ARPS = [[62, 66, 69, 74], [59, 62, 66, 71], [55, 59, 62, 67], [57, 61, 64, 69]]

def chord_idx(t):
    return int(t // BAR) % 4

# ruído determinístico (LCG)
_seed = 12345
def noise():
    global _seed
    _seed = (_seed * 1103515245 + 12345) & 0x7FFFFFFF
    return (_seed / 0x7FFFFFFF) * 2 - 1

def env(dt, a, d):
    if dt < 0:
        return 0.0
    if dt < a:
        return dt / a
    return math.exp(-(dt - a) / d)

def section_gain(t):
    """ganho por camada: (arp, kick, hat, bass)"""
    if t < T_BUILD:
        return (0.0, 0.0, 0.0, 0.0)
    if t < T_FULL:
        x = (t - T_BUILD) / (T_FULL - T_BUILD)
        return (0.6 + 0.4 * x, 0.7, 0.0, 0.5 + 0.5 * x)
    if t < T_END:
        return (1.0, 1.0, 1.0, 1.0)
    return (0.0, 0.0, 0.0, 0.0)

# eventos
arp_events = []
t = 0.0
i = 0
while t < T_END:
    idx = chord_idx(t)
    pat = ARPS[idx]
    seq = [pat[0], pat[1], pat[2], pat[3], pat[2], pat[1], pat[3], pat[0]]
    arp_events.append((midi(seq[i % 8]), t))
    t += BEAT / 4
    i += 1

kick_events = []
t = 0.0
while t < T_END:
    kick_events.append(t)
    t += BEAT
hat_events = []
t = BEAT / 2
while t < T_END:
    hat_events.append(t)
    t += BEAT / 2
impacts = [0.0, T_END]

def render():
    out = []
    ai = ki = hi = 0
    arp_active, kick_active, hat_active = [], [], []
    hp_prev_in = 0.0
    hp_prev_out = 0.0
    for n in range(N):
        t = n / SR
        g_arp, g_kick, g_hat, g_bass = section_gain(t)
        idx = chord_idx(t)

        # pad
        pad = 0.0
        for note in CHORDS[idx]:
            f = midi(note)
            pad += (math.sin(2 * math.pi * f * t) + 0.5 * math.sin(2 * math.pi * f * 1.004 * t + 0.4)
                    + 0.2 * math.sin(2 * math.pi * f * 2 * t)) / 4
        ph = (t % BAR) / BAR
        pad *= 0.10 * (0.6 + 0.4 * math.sin(math.pi * ph))
        if t >= T_END:
            pad *= 1.3

        # baixo: pulsado em colcheias
        root = midi(CHORDS[idx][0] - 12)
        bph = (t % (BEAT / 2)) / (BEAT / 2)
        bass = math.sin(2 * math.pi * root * t) * 0.16 * math.exp(-bph * 2.2) * g_bass
        bass += 0.04 * math.sin(2 * math.pi * root * 2 * t) * math.exp(-bph * 3) * g_bass

        # arpejo
        while ai < len(arp_events) and arp_events[ai][1] <= t:
            arp_active.append(arp_events[ai]); ai += 1
        arp_active = [e for e in arp_active if t - e[1] < 0.8]
        arp = 0.0
        for f, t0 in arp_active:
            dt = t - t0
            e = env(dt, 0.004, 0.16)
            arp += e * (math.sin(2 * math.pi * f * dt) + 0.4 * math.sin(2 * math.pi * 2 * f * dt))
        arp *= 0.07 * g_arp

        # bumbo
        while ki < len(kick_events) and kick_events[ki] <= t:
            kick_active.append(kick_events[ki]); ki += 1
        kick_active = [e for e in kick_active if t - e < 0.4]
        kick = 0.0
        for t0 in kick_active:
            dt = t - t0
            fk = 48 + 110 * math.exp(-dt * 28)
            kick += math.sin(2 * math.pi * fk * dt) * math.exp(-dt * 9)
        kick *= 0.42 * g_kick

        # chimbal
        while hi < len(hat_events) and hat_events[hi] <= t:
            hat_active.append(hat_events[hi]); hi += 1
        hat_active = [e for e in hat_active if t - e < 0.08]
        hat = 0.0
        if hat_active:
            nz = noise()
            for t0 in hat_active:
                dt = t - t0
                hat += nz * math.exp(-dt * 70)
        # passa-altas simples
        hp = hat - hp_prev_in + 0.95 * hp_prev_out
        hp_prev_in, hp_prev_out = hat, hp
        hat = hp * 0.10 * g_hat

        # riser (ruído filtrado subindo) antes do final
        riser = 0.0
        if T_RISER <= t < T_END:
            x = (t - T_RISER) / (T_END - T_RISER)
            riser = noise() * 0.12 * x * x
            riser += 0.05 * x * math.sin(2 * math.pi * (200 + 600 * x) * t)

        # impactos
        imp = 0.0
        for t0 in impacts:
            dt = t - t0
            if 0 <= dt < 2.0:
                imp += math.sin(2 * math.pi * (40 + 60 * math.exp(-dt * 6)) * dt) * math.exp(-dt * 2.2) * 0.45
                imp += noise() * math.exp(-dt * 12) * 0.12

        for t0 in CHAPTER_HITS:
            dt = t - t0
            if 0 <= dt < 1.2:
                imp += math.sin(2 * math.pi * (45 + 50 * math.exp(-dt * 7)) * dt) * math.exp(-dt * 3.5) * 0.28
                imp += noise() * math.exp(-dt * 16) * 0.07

        s = pad + bass + arp + kick + hat + riser + imp
        if t < 0.3:
            s *= t / 0.3
        if t > DUR - 4.0:
            s *= max(0.0, (DUR - t) / 4.0)
        # soft clip
        s = math.tanh(s * 1.4) / 1.4
        pan = 0.03 * math.sin(2 * math.pi * 0.13 * t)
        out.append((max(-1, min(1, s + pan * arp)), max(-1, min(1, s - pan * arp))))
    return out

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "public/trilha.wav"
    samples = render()
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        frames = bytearray()
        for l, r in samples:
            frames += struct.pack("<hh", int(l * 31000), int(r * 31000))
        w.writeframes(bytes(frames))
    print("ok", path, len(samples) / SR, "s")

if __name__ == "__main__":
    main()
