"""Gera a trilha e os efeitos sonoros do vídeo institucional GTK em Python puro (sem numpy).

Uso: python3 scripts/gen-audio.py [pasta de saída = public/gtk/audio]
Saída: trilha.wav (90,05 s, estéreo) e SFX curtos (mono->estéreo), todos 44.1 kHz 16-bit.
"""
import math, os, random, struct, sys, wave
from array import array

SR = 44100
TWO_PI = 2 * math.pi
random.seed(7)

# ----------------------------------------------------------------- utilidades

def zeros(n):
    return array("d", bytes(8 * n))

def add(dst, src, at=0, gain=1.0):
    n = len(src)
    end = min(len(dst), at + n)
    for i in range(at, end):
        dst[i] += src[i - at] * gain

def env_adsr(n, a, d, s, r):
    out = zeros(n)
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    for i in range(n):
        if i < a_n:
            v = i / max(1, a_n)
        elif i < a_n + d_n:
            v = 1 - (1 - s) * (i - a_n) / max(1, d_n)
        elif i < n - r_n:
            v = s
        else:
            v = s * (n - i) / max(1, r_n)
        out[i] = v
    return out

def exp_decay(n, tau):
    out = zeros(n)
    k = -1.0 / (tau * SR)
    for i in range(n):
        out[i] = math.exp(k * i)
    return out

def sine(n, f0, f1=None, phase=0.0):
    out = zeros(n)
    ph = phase
    if f1 is None:
        inc = TWO_PI * f0 / SR
        for i in range(n):
            out[i] = math.sin(ph)
            ph += inc
    else:
        for i in range(n):
            t = i / n
            f = f0 * (f1 / f0) ** t  # glide exponencial
            out[i] = math.sin(ph)
            ph += TWO_PI * f / SR
    return out

def noise(n):
    out = zeros(n)
    for i in range(n):
        out[i] = random.uniform(-1, 1)
    return out

def lowpass(x, cutoff, cutoff_end=None):
    """Passa-baixa de 1 polo; cutoff pode variar linearmente."""
    out = zeros(len(x))
    y = 0.0
    n = len(x)
    for i in range(n):
        c = cutoff if cutoff_end is None else cutoff + (cutoff_end - cutoff) * i / n
        a = 1 - math.exp(-TWO_PI * c / SR)
        y += a * (x[i] - y)
        out[i] = y
    return out

def highpass(x, cutoff):
    lp = lowpass(x, cutoff)
    out = zeros(len(x))
    for i in range(len(x)):
        out[i] = x[i] - lp[i]
    return out

def mul(x, e):
    out = zeros(len(x))
    for i in range(len(x)):
        out[i] = x[i] * e[i]
    return out

def scale(x, g):
    out = zeros(len(x))
    for i in range(len(x)):
        out[i] = x[i] * g
    return out

def reverb(x, taps=((0.031, 0.5), (0.047, 0.4), (0.071, 0.35), (0.113, 0.3)), wet=0.35, fb=0.45):
    """Reverb simples: 4 combs paralelos com feedback + mistura."""
    n = len(x)
    out = zeros(n)
    bufs = []
    for delay, g in taps:
        d = int(delay * SR)
        bufs.append((d, g, zeros(d), [0]))
    for i in range(n):
        acc = 0.0
        for d, g, buf, pos in bufs:
            p = pos[0]
            v = buf[p]
            buf[p] = x[i] + v * fb
            pos[0] = (p + 1) % d
            acc += v * g
        out[i] = x[i] + acc * wet
    return out

def softclip(x, drive=1.0):
    out = zeros(len(x))
    for i in range(len(x)):
        out[i] = math.tanh(x[i] * drive)
    return out

def normalize(x, peak_db=-1.0):
    m = max(1e-9, max(abs(v) for v in x))
    g = 10 ** (peak_db / 20) / m
    return scale(x, g)

def write_wav(path, left, right=None, peak_db=-1.0):
    left = normalize(left, peak_db)
    right = left if right is None else normalize(right, peak_db)
    n = min(len(left), len(right))
    frames = array("h")
    for i in range(n):
        frames.append(int(max(-1, min(1, left[i])) * 32767))
        frames.append(int(max(-1, min(1, right[i])) * 32767))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(frames.tobytes())
    rms = math.sqrt(sum(v * v for v in left) / n)
    print(f"{os.path.basename(path):24s} {n / SR:6.2f}s  rms={20 * math.log10(max(rms, 1e-9)):6.1f} dBFS")

def haas(x, ms=12.0, g=0.85):
    """Cria canal direito com pequeno atraso para largura estéreo."""
    d = int(ms / 1000 * SR)
    r = zeros(len(x))
    for i in range(d, len(x)):
        r[i] = x[i - d] * g + x[i] * (1 - g)
    return r

# ----------------------------------------------------------------- instrumentos

def note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)

def pad_note(n, hz, detune=0.4, harmonics=5, amp=1.0):
    """Pad: 2 vozes desafinadas, harmônicos 1/n (dente de serra suave)."""
    out = zeros(n)
    for voice in (-1, 1):
        f = hz * 2 ** (voice * detune / 1200)
        ph = random.random() * TWO_PI
        inc = TWO_PI * f / SR
        for i in range(n):
            s = 0.0
            p = ph
            for h in range(1, harmonics + 1):
                s += math.sin(p * h) / h
            out[i] += s
            ph += inc
    return scale(out, amp / (2 * 2.3))

def pluck(n, hz, amp=1.0, tau=0.18):
    out = zeros(n)
    ph = 0.0
    inc = TWO_PI * hz / SR
    k = -1.0 / (tau * SR)
    for i in range(n):
        e = math.exp(k * i)
        out[i] = (math.sin(ph) + 0.5 * math.sin(2 * ph) * e + 0.25 * math.sin(3 * ph) * e) * e
        ph += inc
    return scale(out, amp / 1.6)

def kick(n=None, amp=1.0):
    n = n or int(0.35 * SR)
    body = mul(sine(n, 160, 42), exp_decay(n, 0.12))
    click = mul(noise(int(0.01 * SR)), exp_decay(int(0.01 * SR), 0.003))
    out = zeros(n)
    add(out, body)
    add(out, click, 0, 0.4)
    return scale(softclip(out, 1.6), amp)

def hat(n=None, amp=1.0, tau=0.03):
    n = n or int(0.08 * SR)
    return scale(mul(highpass(noise(n), 6000), exp_decay(n, tau)), amp)

def sub_note(n, hz, amp=1.0):
    return scale(mul(sine(n, hz), env_adsr(n, 0.01, 0.1, 0.8, 0.15)), amp)

# ----------------------------------------------------------------- trilha

BPM = 95
BEAT = 60.0 / BPM
BAR = 4 * BEAT
DURATION = 90.1

# Progressão (MIDI): Dm  Bb  F  C  — tríades com raiz grave
CHORDS = [
    (62, [62, 65, 69]),  # Dm
    (58, [58, 62, 65]),  # Bb
    (65, [65, 69, 72]),  # F
    (60, [60, 64, 67]),  # C
]

def section(t):
    """Intensidade por trecho do vídeo (segundos)."""
    if t < 6:   return "intro"
    if t < 26:  return "build"
    if t < 58:  return "drive"
    if t < 78:  return "climax"
    if t < 84:  return "light"
    return "outro"

def make_track():
    N = int(DURATION * SR)
    pad = zeros(N)
    bass = zeros(N)
    drums = zeros(N)
    arp = zeros(N)

    # PAD + SUB por compasso
    bar = 0
    t = 0.0
    while t < DURATION:
        sec = section(t)
        root, tones = CHORDS[bar % 4]
        n = int(BAR * SR) + int(0.4 * SR)
        at = int(t * SR)
        if sec == "outro":
            tones = [62, 66, 69, 74]  # D maior (final luminoso)
            n = int((DURATION - t) * SR)
        gain = {"intro": 0.35, "build": 0.55, "drive": 0.6, "climax": 0.85, "light": 0.5, "outro": 0.9}[sec]
        env = env_adsr(n, 0.25, 0.3, 0.85, 0.5 if sec != "outro" else 2.5)
        chord = zeros(n)
        for m in tones:
            add(chord, pad_note(n, note_hz(m - 12)), 0, 0.6)
            if sec in ("climax", "outro"):
                add(chord, pad_note(n, note_hz(m), harmonics=3), 0, 0.25)
        add(pad, mul(chord, env), at, gain)
        # sub grave
        sub_hz = note_hz(root - 24)
        if sec == "intro":
            add(bass, sub_note(n, sub_hz), at, 0.5)
        elif sec == "outro":
            add(bass, mul(sine(n, sub_hz), env_adsr(n, 0.05, 0.5, 0.9, 2.5)), at, 0.8)
        else:
            steps = 4 if sec in ("build", "light") else 8
            for k in range(steps):
                bt = t + k * BAR / steps
                bn = int(BAR / steps * SR)
                g = 0.9 if k % (steps // 4) == 0 else 0.55
                add(bass, sub_note(bn, sub_hz), int(bt * SR), 0.7 * g)
        if sec == "outro":
            break
        t += BAR
        bar += 1

    # BATERIA por batida
    k_wav = kick()
    h_wav = hat()
    h_open = hat(int(0.18 * SR), tau=0.09)
    b = 0
    while True:
        t = b * BEAT
        if t >= 84:
            break
        sec = section(t)
        at = int(t * SR)
        beat_in_bar = b % 4
        if sec in ("drive", "climax"):
            if sec == "climax" or beat_in_bar in (0, 2):
                add(drums, k_wav, at, 0.9 if beat_in_bar == 0 else 0.75)
            for e in range(2):
                add(drums, h_wav, at + int(e * BEAT / 2 * SR), 0.28 if e == 0 else 0.18)
            if sec == "climax":
                add(drums, h_open, at + int(BEAT / 2 * SR), 0.16)
        elif sec in ("build", "light"):
            for e in range(2):
                add(drums, h_wav, at + int(e * BEAT / 2 * SR), 0.16 if e == 0 else 0.1)
            if beat_in_bar == 0 and sec == "build" and t >= 16:
                add(drums, k_wav, at, 0.5)
        b += 1

    # ARPEJO (16 avos) a partir de 16 s
    s16 = BEAT / 4
    i16 = 0
    while True:
        t = 16 + i16 * s16
        if t >= 84:
            break
        sec = section(t)
        bar_idx = int(t // BAR) % 4
        _, tones = CHORDS[bar_idx]
        pattern = [0, 1, 2, 1, 0, 2, 1, 2]
        m = tones[pattern[i16 % 8] % 3] + (12 if sec == "climax" else 0)
        if sec == "climax" and i16 % 4 == 2:
            m += 12
        g = {"build": 0.22, "drive": 0.3, "climax": 0.38, "light": 0.2}.get(sec, 0.0)
        if i16 % 2 == 1:
            g *= 0.6
        if g > 0:
            add(arp, pluck(int(0.3 * SR), note_hz(m), tau=0.16), int(t * SR), g)
        i16 += 1

    # MIX
    mix = zeros(N)
    add(mix, reverb(pad, wet=0.45), 0, 1.0)
    add(mix, reverb(arp, wet=0.5), 0, 1.0)
    add(mix, bass, 0, 1.0)
    add(mix, drums, 0, 1.0)
    # fade final
    fade = int(1.6 * SR)
    for i in range(N - fade, N):
        mix[i] *= (N - i) / fade
    mix = softclip(mix, 1.15)
    return mix, haas(mix)

# ----------------------------------------------------------------- efeitos

def sfx_impact_concreto():
    n = int(0.9 * SR)
    body = mul(sine(n, 70, 34), exp_decay(n, 0.22))
    grit = mul(lowpass(noise(int(0.12 * SR)), 1800), exp_decay(int(0.12 * SR), 0.03))
    out = zeros(n); add(out, body); add(out, grit, 0, 0.7)
    return softclip(out, 1.8)

def sfx_impact_cine():
    n = int(2.2 * SR)
    body = mul(sine(n, 55, 28), exp_decay(n, 0.6))
    boom = mul(lowpass(noise(n), 300, 80), exp_decay(n, 0.35))
    out = zeros(n); add(out, body); add(out, boom, 0, 0.8)
    return reverb(softclip(out, 1.8), wet=0.4)

def sfx_whoosh(seconds=0.6, f0=300, f1=4000, reverse=False):
    n = int(seconds * SR)
    x = lowpass(noise(n), f0, f1) if not reverse else lowpass(noise(n), f1, f0)
    env = zeros(n)
    for i in range(n):
        t = i / n
        env[i] = math.sin(math.pi * t) ** 1.5
    return mul(x, env)

def sfx_riser(seconds=1.0):
    n = int(seconds * SR)
    x = zeros(n)
    add(x, lowpass(noise(n), 400, 6000), 0, 0.6)
    add(x, sine(n, 180, 1400), 0, 0.35)
    env = zeros(n)
    for i in range(n):
        env[i] = (i / n) ** 2
    return mul(x, env)

def sfx_tick():
    n = int(0.03 * SR)
    return mul(sine(n, 2400), exp_decay(n, 0.006))

def sfx_ding(base=880):
    n = int(1.2 * SR)
    out = zeros(n)
    for h, g, tau in ((1, 1.0, 0.5), (2.01, 0.5, 0.3), (3.0, 0.25, 0.2), (4.2, 0.12, 0.12)):
        add(out, mul(sine(n, base * h), exp_decay(n, tau)), 0, g)
    return reverb(out, wet=0.3)

def sfx_thud():
    n = int(0.25 * SR)
    return softclip(mul(sine(n, 140, 70), exp_decay(n, 0.05)), 1.5)

def sfx_pop():
    n = int(0.06 * SR)
    return mul(sine(n, 520, 240), exp_decay(n, 0.014))

def sfx_power_on():
    n = int(0.7 * SR)
    hum = mul(sine(n, 48, 55), env_adsr(n, 0.05, 0.1, 0.7, 0.3))
    click = mul(highpass(noise(int(0.02 * SR)), 2000), exp_decay(int(0.02 * SR), 0.004))
    rise = mul(sine(int(0.25 * SR), 300, 900), exp_decay(int(0.25 * SR), 0.12))
    out = zeros(n); add(out, hum, 0, 0.8); add(out, click, 0, 0.6); add(out, rise, 0, 0.25)
    return out

def sfx_shunk():
    n = int(0.6 * SR)
    hiss = mul(lowpass(noise(n), 5000, 800), exp_decay(n, 0.09))
    clank = zeros(n)
    for f, g in ((640, 1.0), (1290, 0.5), (2110, 0.3)):
        add(clank, mul(sine(n, f), exp_decay(n, 0.06)), int(0.06 * SR), g)
    thump = mul(sine(n, 110, 60), exp_decay(n, 0.08))
    out = zeros(n); add(out, hiss, 0, 0.6); add(out, clank, 0, 0.5); add(out, thump, int(0.05 * SR), 0.9)
    return softclip(out, 1.4)

def sfx_shimmer():
    n = int(1.4 * SR)
    out = zeros(n)
    for f in (1760, 2217, 2637, 3520):
        x = mul(sine(n, f), exp_decay(n, 0.5))
        trem = zeros(n)
        for i in range(n):
            trem[i] = 0.6 + 0.4 * math.sin(TWO_PI * 7 * i / SR)
        add(out, mul(x, trem), 0, 0.25)
    return reverb(out, wet=0.5)

def sfx_subdrop():
    n = int(1.4 * SR)
    return softclip(mul(sine(n, 90, 30), exp_decay(n, 0.5)), 1.6)

def main(out_dir="public/gtk/audio"):
    os.makedirs(out_dir, exist_ok=True)
    sfx = {
        "impact-concreto": sfx_impact_concreto,
        "impact-cine": sfx_impact_cine,
        "whoosh-curto": lambda: sfx_whoosh(0.5),
        "whoosh-longo": lambda: sfx_whoosh(2.8, 200, 2500),
        "whoosh-aereo": lambda: sfx_whoosh(4.5, 150, 1800),
        "riser": lambda: sfx_riser(1.1),
        "tick": sfx_tick,
        "ding": lambda: sfx_ding(880),
        "ding-grave": lambda: sfx_ding(440),
        "thud": sfx_thud,
        "pop": sfx_pop,
        "power-on": sfx_power_on,
        "shunk": sfx_shunk,
        "shimmer": sfx_shimmer,
        "subdrop": sfx_subdrop,
    }
    for name, fn in sfx.items():
        x = fn()
        write_wav(os.path.join(out_dir, f"{name}.wav"), x, haas(x, 6, 0.5), peak_db=-1.0)
    print("gerando trilha...")
    l, r = make_track()
    write_wav(os.path.join(out_dir, "trilha.wav"), l, r, peak_db=-1.0)

if __name__ == "__main__":
    main(*(sys.argv[1:2]))
