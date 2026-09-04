"""Gera a trilha instrumental do vídeo institucional (60 s, WAV 44.1 kHz estéreo).

Síntese aditiva em Python puro (sem dependências): pad de acordes sustentados,
arpejo suave de "piano elétrico" e um baixo discreto. Progressão em Ré maior,
andamento calmo, fade-in de 1,5 s e fade-out nos últimos 4 s. Sem direitos autorais.

Uso: python3 scripts/gerar_trilha.py [saida.wav]
"""
import math
import struct
import sys
import wave

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BPM = 72
BEAT = 60.0 / BPM          # 0.833 s
BAR = BEAT * 4             # 3.333 s -> 18 compassos em 60 s

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# Progressão (D maior): D  - Bm - G - A  (I - vi - IV - V), 2 compassos cada
# notas MIDI: D3=50, F#3=54, A3=57, B3=59, G3=55, C#4=61, E4=64
CHORDS = [
    [50, 54, 57, 62],  # D
    [47, 50, 54, 59],  # Bm
    [43, 47, 50, 55],  # G
    [45, 49, 52, 57],  # A
]
ARP_PATTERNS = [
    [62, 66, 69, 74, 69, 66],  # D
    [59, 62, 66, 71, 66, 62],  # Bm
    [55, 59, 62, 67, 62, 59],  # G
    [57, 61, 64, 69, 64, 61],  # A
]

def chord_at(t):
    bar = int(t // BAR)
    idx = (bar // 2) % 4
    return idx

def env_ad(t, a, d):
    if t < 0:
        return 0.0
    if t < a:
        return t / a
    return math.exp(-(t - a) / d)

# Pré-cálculo dos eventos de arpejo (nota, tempo de início)
arp_events = []
t = 0.0
step = BEAT / 2  # colcheia
i = 0
while t < DUR:
    idx = chord_at(t)
    pat = ARP_PATTERNS[idx]
    note = pat[i % len(pat)]
    arp_events.append((midi(note), t))
    t += step
    i += 1

def render():
    out = []
    # tabela de eventos ativos para eficiência
    ev_i = 0
    active = []
    for n in range(N):
        t = n / SR
        # --- pad ---
        idx = chord_at(t)
        # crossfade entre acordes nos limites
        pad = 0.0
        for k, note in enumerate(CHORDS[idx]):
            f = midi(note)
            # duas ondas levemente desafinadas + sub-harmônico suave
            pad += (math.sin(2 * math.pi * f * t) + 0.6 * math.sin(2 * math.pi * f * 1.003 * t + 0.3)
                    + 0.25 * math.sin(2 * math.pi * f * 2 * t)) / 4
        # envelope de compasso: cresce e decai suavemente a cada 2 compassos
        ph = (t % (2 * BAR)) / (2 * BAR)
        pad_env = 0.55 + 0.45 * math.sin(math.pi * ph)
        pad *= 0.11 * pad_env
        # tremolo lento
        pad *= 1 + 0.08 * math.sin(2 * math.pi * 0.25 * t)

        # --- baixo ---
        root = midi(CHORDS[idx][0] - 12)
        bass = math.sin(2 * math.pi * root * t) * 0.10
        bass *= 0.6 + 0.4 * math.sin(math.pi * ((t % BAR) / BAR))

        # --- arpejo ---
        while ev_i < len(arp_events) and arp_events[ev_i][1] <= t:
            active.append(arp_events[ev_i])
            ev_i += 1
        active = [e for e in active if t - e[1] < 2.5]
        arp = 0.0
        for f, t0 in active:
            dt = t - t0
            e = env_ad(dt, 0.008, 0.55)
            arp += e * (math.sin(2 * math.pi * f * dt) + 0.35 * math.sin(2 * math.pi * 2 * f * dt)
                        + 0.12 * math.sin(2 * math.pi * 3 * f * dt))
        arp *= 0.075

        s = pad + bass + arp
        # fades
        if t < 1.5:
            s *= t / 1.5
        if t > DUR - 4.0:
            s *= max(0.0, (DUR - t) / 4.0)
        # estéreo: pad levemente aberto, arpejo alternando
        l = s + 0.02 * math.sin(2 * math.pi * 0.11 * t) * arp
        r = s - 0.02 * math.sin(2 * math.pi * 0.11 * t) * arp
        out.append((max(-1, min(1, l)), max(-1, min(1, r))))
    return out

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "public/trilha.wav"
    samples = render()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for l, r in samples:
            frames += struct.pack("<hh", int(l * 32000), int(r * 32000))
        w.writeframes(bytes(frames))
    print("ok", path, len(samples) / SR, "s")

if __name__ == "__main__":
    main()
