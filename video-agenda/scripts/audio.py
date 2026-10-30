"""Sintetiza a trilha de efeitos (notificação, tique do relógio, whoosh...) a partir de events.json."""
import json, sys, wave
import numpy as np

SR, DUR = 44100, 30.0
events = json.load(open(sys.argv[1]))
out = np.zeros(int(SR * DUR) + SR)
rng = np.random.default_rng(3)

def env(n, k):
    return np.exp(-np.arange(n) / SR * k)

def sine(f, d, a, k=12, f2=None):
    n = int(SR * d); tt = np.arange(n) / SR
    fr = f if f2 is None else f * (f2 / f) ** (tt / d)
    return a * np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, k)

def noise(d, a, k=30, smooth=1):
    n = int(SR * d); x = rng.uniform(-1, 1, n)
    if smooth > 1: x = np.convolve(x, np.ones(smooth) / smooth, 'same')
    return a * x * env(n, k)

def whoosh():
    n = int(SR * .32); x = rng.uniform(-1, 1, n)
    x = np.convolve(x, np.ones(12) / 12, 'same')
    return .9 * x * np.sin(np.pi * np.arange(n) / n) ** 2

def ping():
    a = sine(1318, .14, .32, 25); b = sine(1760, .5, .32, 8)
    s = np.zeros(len(b) + int(SR * .09)); s[:len(a)] += a; s[int(SR * .09):] += b
    return s

def mix(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o

SOUNDS = {
    'tick': lambda: mix(noise(.025, .35, 200), sine(3200, .02, .12, 300)),
    'type': lambda: noise(.03, .4, 150, 2),
    'ping': ping,
    'pop': lambda: sine(400, .09, .45, 30, 950),
    'thud': lambda: mix(sine(110, .35, .9, 10, 45), noise(.12, .35, 40, 6)),
    'low': lambda: sine(220, .45, .3, 6, 160),
    'ding': lambda: mix(sine(1046, 1.0, .3, 4), sine(2093, 1.0, .1, 7)),
    'drop': lambda: sine(1300, .4, .18, 6, 300),
    'whoosh': whoosh,
}
for t, kind in events:
    s = SOUNDS[kind](); i = int(t * SR)
    out[i:i + len(s)] += s[:len(out) - i]
out = out[:int(SR * DUR)]
out = np.tanh(out * 1.1) * .85
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())
