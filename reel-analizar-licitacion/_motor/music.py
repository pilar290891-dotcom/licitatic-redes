# Música original para el reel (compuesta por código, sin muestras ni derechos de terceros)
import numpy as np, json, wave
from scipy.signal import butter, sosfilt
SR = 44100; BPM = 120; B = 60 / BPM
TL = json.load(open('timeline.json')); END = TL['END']
N = int(SR * END); rng = np.random.default_rng(3)
mus = np.zeros((N, 2)); sfx = np.zeros((N, 2)); duck = np.ones(N)

def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def add(buf, t, x, g=1.0, pan=0.0):
    i = int(t * SR); x = x[:max(0, N - i)]
    if i < 0 or len(x) == 0: return
    l, r = np.sqrt(0.5 - pan / 2), np.sqrt(0.5 + pan / 2)
    buf[i:i + len(x), 0] += x * g * l * 1.414; buf[i:i + len(x), 1] += x * g * r * 1.414
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; out = 0
    for k in range(1, 14): out = out + np.sin(2 * np.pi * f * (1 + det) * k * t) / k
    return out * 0.55

def kick():
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 46 + 110 * np.exp(-t / 0.035); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.16) + 0.25 * hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.004)
def clap():
    n = int(0.25 * SR); x = bp(rng.standard_normal(n), 900, 4200)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022): i = int(o * SR); e[i:] += env(n - i, 0.001, 0.012 if o < 0.02 else 0.09)
    return x * e * 0.8
def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR); return hp(rng.standard_normal(n), 7500) * env(n, 0.001, 0.07 if open_ else 0.014) * 0.5
def pluck(m, d=0.28):
    n = int(d * 1.6 * SR); t = np.arange(n) / SR; f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return x * env(n, 0.002, d * 0.45)
KICK, CLAP = kick(), clap()

# Progresión La m – Fa – Do – Sol (1 compás cada uno = 2 s)
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]
bars = int(np.ceil(END / (4 * B)))
def sec(t):
    if t < 6: return 'intro'
    if 24 <= t < 26: return 'break'
    if 40 <= t < 42: return 'build'
    if t >= 47: return 'outro'
    return 'main'
for bar in range(bars):
    t0 = bar * 4 * B; root, ch = PROG[bar % 4]
    # pad
    s_ = sec(t0); n = int(4 * B * SR)
    if t0 < END:
        pad = sum(saw(mtof(m), n, d) for m in ch for d in (-0.004, 0.004))
        pad = lp(pad, 1400 if s_ in ('main', 'outro') else 900) * env(n, 0.25, 6) * 0.05
        add(mus, t0, pad, 1.0 if s_ != 'build' else 0.6)
    for step in range(16):
        t = t0 + step * B / 4
        if t >= END: break
        s_ = sec(t)
        beat = step % 4 == 0
        kick_on = s_ in ('intro', 'main') or (s_ == 'outro' and t < 51) or (s_ == 'break' and t < 25)
        if beat and kick_on: add(mus, t, KICK, 0.9); duck[int(t*SR):int((t+0.18)*SR)] = np.linspace(0.35, 1, len(duck[int(t*SR):int((t+0.18)*SR)]))
        if step in (4, 12) and s_ in ('main',) or (step in (4, 12) and s_ == 'intro' and t > 2): add(mus, t, CLAP, 0.55, 0.05)
        if step % 4 == 2 and s_ in ('intro', 'main', 'outro'): add(mus, t, hat(True), 0.35, 0.2)
        if s_ == 'main' and step % 2 == 1: add(mus, t, hat(), 0.4, -0.25)
        # bajo: corcheas a contratiempo
        if step % 2 == 0 and s_ in ('intro', 'main') or (s_ == 'outro' and t < 51 and step % 4 == 2):
            nb = int(B / 2 * SR * 0.9); x = lp(saw(mtof(root - 12), nb), 500) * env(nb, 0.004, 0.12)
            add(mus, t + (B / 2 if step % 4 == 0 else 0) * 0, x, 0.42)
        # arpegio
        if s_ in ('main', 'outro', 'intro'):
            seq = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24][step % 4]
            if s_ == 'intro' and step % 2: continue
            add(mus, t, pluck(seq), 0.11, 0.35 if step % 2 else -0.35)
# redoble y subidas
def riser(t0, d, g=0.4):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); k = 2048
    for i in range(0, n, k):
        f = 400 + 7000 * (i / n) ** 2; seg = bp(x[i:i + k], f * 0.7, min(f * 1.4, 18000))
        out[i:i + len(seg)] = seg
    add(sfx, t0, out * np.linspace(0, 1, n) ** 2, g)
for i in range(16):
    t = 40 + 2 * (1 - (1 - i / 16) ** 1.0)
    add(mus, 40 + i * 0.125, CLAP, 0.25 + 0.35 * i / 16)
riser(40.0, 2.0, 0.35); riser(24.2, 1.8, 0.25); riser(4.6, 1.4, 0.2)
# impactos
def boom(t, g=1.0):
    n = int(1.4 * SR); tt = np.arange(n) / SR; f = 38 + 70 * np.exp(-tt / 0.08)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.5) + 0.3 * lp(rng.standard_normal(n), 2500) * np.exp(-tt / 0.15)
    add(sfx, t, x, g)
boom(0.0, 0.9); boom(TL['STAMP'], 1.0); boom(TL['CTA'], 0.5)
# acorde final
n = int(4 * SR); fin = sum(saw(mtof(m), n, d) for m in (45, 57, 60, 64, 69) for d in (-0.003, 0.003))
add(mus, 52.0, lp(fin, 1800) * env(n, 0.02, 1.2) * 0.05)
# efectos de pantalla
def whoosh(t, d=0.45, g=0.35):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); k = 1024
    for i in range(0, n, k):
        u = i / n; f = 300 + 3500 * np.sin(np.pi * u); seg = bp(x[i:i + k], f * 0.6, f * 1.5); out[i:i + len(seg)] = seg
    add(sfx, t, out * np.sin(np.pi * np.linspace(0, 1, n)) ** 2, g)
def marker(t, d):
    n = int(d * SR); x = bp(rng.standard_normal(n), 2200, 6500)
    tt = np.arange(n) / SR; am = 0.55 + 0.45 * np.sin(2 * np.pi * 9 * tt) ** 2
    add(sfx, t, x * am * np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.05) * 0.22, 1.0, 0.1)
def pop(t, f0=900, g=0.3):
    n = int(0.12 * SR); tt = np.arange(n) / SR; f = f0 * (1 - 0.4 * tt / 0.12)
    add(sfx, t, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.035), g)
for T in TL['ITEMS']:
    whoosh(T - 0.1); marker(T + 0.42, 0.85); pop(T + 0.5)
whoosh(TL['SWITCH'] - 0.05); pop(TL['SWITCH'] + 0.2, 700); pop(2.35, 800)
whoosh(TL['VERDICT'], 0.5, 0.4)
for i in range(8): pop(TL['VERDICT'] + 0.55 + 0.17 * i, 1000 + 90 * i, 0.22)
whoosh(TL['CTA'] - 0.4, 0.6, 0.45)
# pasar páginas (gancho)
t = 0.05
while t < 2.1:
    n = int(0.03 * SR); add(sfx, t, hp(rng.standard_normal(n), 2500) * env(n, 0.001, 0.008) * 0.25, 1.0, rng.uniform(-.4, .4))
    t += 0.16 * (1 - t / 2.4) + 0.025
# mezcla
mus *= duck[:, None] ** 0.8
mix = mus * 0.95 + sfx
fade = np.ones(N); fl = int(1.5 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
mix *= fade[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) ; mix = mix / np.max(np.abs(mix)) * 0.89
with wave.open('musica.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', mix.shape, np.sqrt(np.mean(mix**2)))
