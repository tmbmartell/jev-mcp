"""Sintetiza trilha investigativa e efeitos sonoros (sem dependência de bancos de áudio)."""
import numpy as np, wave, os, json
SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "public/sfx"); os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(7)
def save(name, x, stereo=False):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    with wave.open(os.path.join(out, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
def t(d): return np.arange(int(SR * d)) / SR
def lp(x, a):  # one-pole lowpass, a in (0,1) per sample (array or scalar)
    y = np.zeros_like(x); s = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
# whoosh: ruído filtrado com varredura
d = 0.7; tt = t(d); n = rng.standard_normal(len(tt))
sweep = 0.02 + 0.25 * np.sin(np.pi * tt / d) ** 2
env = np.sin(np.pi * tt / d) ** 1.5
save("whoosh.wav", lp(n, sweep) * env)
# whoosh grave (abertura)
d = 1.4; tt = t(d); n = rng.standard_normal(len(tt))
env = (tt / d) ** 2 * np.exp(-((tt - d * 0.8) ** 2) / 0.05) + np.exp(-((tt - 1.1) ** 2) / 0.02)
save("whoosh_grave.wav", lp(n, 0.01 + 0.06 * tt / d) * env + 0.6 * np.sin(2 * np.pi * 45 * tt) * env)
# pop: blip com queda de pitch
d = 0.12; tt = t(d); f = 900 * np.exp(-tt * 25) + 250
save("pop.wav", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40))
# moeda: parciais metálicos
d = 0.5; tt = t(d)
coin = sum(a * np.sin(2 * np.pi * fr * tt) for fr, a in [(2637, 1), (3951, .6), (5274, .35), (6200, .2)]) * np.exp(-tt * 9)
save("moeda.wav", coin)
# moedas em sequência
d = 1.2; seq = np.zeros(int(SR * d))
for k in range(7):
    st = int(SR * (k * 0.13 + rng.uniform(0, .03))); c = coin[: len(seq) - st] * rng.uniform(.5, 1)
    seq[st:st + len(c)] += c
save("moedas.wav", seq)
# clique (check / contador)
d = 0.05; tt = t(d)
save("clique.wav", rng.standard_normal(len(tt)) * np.exp(-tt * 300) + np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 200))
# carimbo
d = 0.35; tt = t(d)
save("carimbo.wav", lp(rng.standard_normal(len(tt)), 0.08) * np.exp(-tt * 30) * 3 + np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 18))
# record scratch
d = 0.45; tt = t(d); f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.5 * tt))
save("scratch.wav", (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + lp(rng.standard_normal(len(tt)), 0.3)) * np.exp(-tt * 4))
# rewind / tape stop
d = 0.8; tt = t(d); f = 600 * (1 - tt / d) ** 2 + 40
save("rewind.wav", np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - tt / d) + 0.3 * lp(rng.standard_normal(len(tt)), 0.2) * (1 - tt / d))
# impacto (hit)
d = 1.6; tt = t(d)
save("hit.wav", np.sin(2 * np.pi * (55 * np.exp(-tt * 2) + 35) * tt) * np.exp(-tt * 3) + 0.5 * lp(rng.standard_normal(len(tt)), 0.05) * np.exp(-tt * 6))
# riser
d = 1.2; tt = t(d)
save("riser.wav", lp(rng.standard_normal(len(tt)), 0.02 + 0.3 * (tt / d) ** 2) * (tt / d) ** 2 + 0.3 * np.sin(2 * np.pi * (200 + 600 * (tt / d) ** 2) * tt) * (tt / d) ** 3)
# calculadora (teclas)
d = 1.0; seq = np.zeros(int(SR * d)); tk = t(0.04)
key = np.sin(2 * np.pi * 2400 * tk) * np.exp(-tk * 120)
for k in range(8):
    st = int(SR * (k * 0.11)); seq[st:st + len(key)] += key
save("calculadora.wav", seq)
# tique-taque
d = 1.0; seq = np.zeros(int(SR * d)); tk = t(0.03)
for k in range(4):
    st = int(SR * k * 0.25); fr = 3000 if k % 2 == 0 else 2200
    seq[st:st + len(tk)] += np.sin(2 * np.pi * fr * tk) * np.exp(-tk * 200)
save("tique.wav", seq)

# ---- trilha: pulso investigativo em Ré menor, 90 bpm ----
tempos = json.load(open(os.path.join(ROOT, "src/tempos.json")))
D = tempos["total"] + 2; N = int(SR * D); tt = np.arange(N) / SR
beat = 60 / 90
mus = np.zeros((N, 2))
# drone grave (Ré) com leve batimento
drone = sum(np.sin(2 * np.pi * f * tt + p) for f, p in [(73.42, 0), (73.9, 1), (110.0, 2), (146.8, .5)])
drone *= 0.18 * (0.8 + 0.2 * np.sin(2 * np.pi * tt / 8))
mus += drone[:, None]
# pulso de baixo em colcheias seguindo a progressão Dm - Bb - Gm - A
prog = [73.42, 58.27, 49.0, 55.0]
pl = int(SR * beat / 2); pt = np.arange(pl) / SR
for i in range(int(D / (beat / 2))):
    st = i * pl
    if st + pl > N: break
    f = prog[(i // 16) % 4]
    env = np.exp(-pt * 9)
    note = (np.sin(2 * np.pi * f * pt) + 0.4 * np.sin(2 * np.pi * 2 * f * pt)) * env * (0.55 if i % 2 == 0 else 0.35)
    mus[st:st + pl] += note[:, None]
# pad agudo suave (arpejo lento)
arp = [293.66, 349.23, 440.0, 349.23]
al = int(SR * beat); at = np.arange(al) / SR
for i in range(int(D / beat)):
    st = i * al
    if st + al > N: break
    f = arp[i % 4] * (1 if (i // 16) % 2 == 0 else 0.944)
    note = np.sin(2 * np.pi * f * at) * np.exp(-at * 3) * 0.12
    pan = 0.5 + 0.4 * np.sin(i)
    mus[st:st + al, 0] += note * (1 - pan); mus[st:st + al, 1] += note * pan
# tique de hi-hat
hl = int(SR * 0.03); hn = rng.standard_normal(hl) * np.exp(-np.arange(hl) / SR * 150)
hn = hn - lp(hn, 0.3)
for i in range(int(D / (beat / 2))):
    st = int(i * SR * beat / 2) + int(SR * beat / 4)
    if st + hl < N: mus[st:st + hl] += (hn * 0.08)[:, None]
fade = np.minimum(1, np.minimum(tt / 2, (D - tt) / 3))
mus *= fade[:, None]
save("trilha.wav", mus)
print("ok", D)
