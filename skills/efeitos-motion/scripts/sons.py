#!/usr/bin/env python3
"""Sons sintetizados para os vídeos: ambiente de fundo + efeitos curtos, mixados por baixo da voz.

Uso:
  python sons.py mix video.mp4 plano.json saida.mp4 [--ambiente cafe] [--volume-ambiente -30]
  python sons.py amostras pasta/          # gera um .wav de cada som para ouvir

Tudo é sintetizado aqui (numpy), sem arquivos de terceiros. Os efeitos são derivados do plano do
motion.py, com uma regra fixa por tipo de evento (o mesmo evento sempre soa igual):

  flash (troca de capítulo)        → "sopro"  : whoosh suave, de grave para agudo, esquerda→direita
  titulo_empilhado (cada palavra)  → "toque"  : batida de madeira curta e abafada
  destaque só com sans             → "toque"
  destaque com manuscrito          → "caneta" : rabisco de caneta no papel durante a escrita
  fim do vídeo                     → o ambiente sai em fade de 1,2 s

O ambiente ("cafe") é um pad quente estilo piano elétrico + chiado de vinil + ar de sala, que
abaixa sozinho quando a pessoa fala (sidechain) e volta nas pausas.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

SR = 48000
rng = np.random.default_rng(11)


# ---------------------------------------------------------------- utilidades

def filtro(x, lo=None, hi=None, sr=SR):
    """Passa-faixa suave no domínio da frequência (sem fase, sem scipy)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / sr)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    return np.fft.irfft(X * g, n)


def env(n, ataque, queda, sr=SR):
    t = np.arange(n) / sr
    a = np.clip(t / max(ataque, 1e-4), 0, 1)
    d = np.exp(-np.maximum(t - ataque, 0) / max(queda, 1e-4))
    return a * d


def db(v):
    return 10 ** (v / 20)


def estereo(m, pan=0.0):
    """pan: -1 esquerda … 1 direita (pode ser array)."""
    l = m * np.sqrt((1 - pan) / 2)
    r = m * np.sqrt((1 + pan) / 2)
    return np.stack([l, r], 1)


# ---------------------------------------------------------------- efeitos curtos

def sopro(dur=0.45):
    """Whoosh: ruído com filtro que sobe de 300 Hz a 3,5 kHz, cresce e some; viaja da esquerda pra direita."""
    n = int(dur * SR)
    ruido = rng.standard_normal(n)
    out = np.zeros(n)
    bloco = 1024
    for i in range(0, n, bloco // 2):  # filtro que varia no tempo, em blocos sobrepostos
        seg = ruido[i:i + bloco]
        if len(seg) < 32:
            break
        p = i / n
        fc = 300 * (3500 / 300) ** p
        y = filtro(seg * np.hanning(len(seg)), lo=fc * 0.5, hi=fc * 1.6)
        out[i:i + len(y)] += y
    t = np.linspace(0, 1, n)
    forma = np.sin(np.pi * t) ** 1.6 * (1 - 0.35 * t)
    out = out * forma
    out /= np.abs(out).max() + 1e-9
    return estereo(out * db(-6), pan=np.linspace(-0.6, 0.6, n))


def toque(dur=0.12):
    """Batida de madeira abafada: dois parciais curtos + clique."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 820 * t) * 0.7 + np.sin(2 * np.pi * 1730 * t) * 0.25) * np.exp(-t / 0.018)
    clique = filtro(rng.standard_normal(n), lo=2000, hi=7000) * np.exp(-t / 0.003) * 0.25
    s = filtro(s + clique, hi=4500)
    s /= np.abs(s).max() + 1e-9
    return estereo(s * db(-4))


def caneta(dur=0.6):
    """Rabisco de caneta no papel: ruído agudo com 'traços' irregulares (~13 por segundo)."""
    n = int(max(dur, 0.15) * SR)
    t = np.arange(n) / SR
    base = filtro(rng.standard_normal(n), lo=2200, hi=7500)
    tracos = 0.5 + 0.5 * np.sin(2 * np.pi * 13 * t + 2 * np.sin(2 * np.pi * 3.1 * t))
    tracos = tracos ** 3 * (0.6 + 0.4 * rng.random(n).cumsum() % 1)
    borda = np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    s = base * tracos * borda
    s /= np.abs(s).max() + 1e-9
    return estereo(s * db(-5), pan=0.15)


# ---------------------------------------------------------------- ambiente

NOTAS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(nota):
    nome, oit = nota[:-1], int(nota[-1])
    return 440 * 2 ** ((NOTAS[nome] + 12 * (oit + 1) - 69) / 12)


ACORDES = [["F2", "A3", "C4", "E4"], ["E2", "G3", "B3", "D4"],
           ["D2", "F3", "A3", "C4"], ["C2", "E3", "G3", "B3"]]  # Fmaj7 Em7 Dm7 Cmaj7


def cafe(dur):
    """Pad de piano elétrico (lo-fi) + vinil + ar de sala. Devolve estéreo normalizado a ~-6 dBFS de pico."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    pad = np.zeros((n, 2))
    passo = 4.0
    for k in range(int(dur / passo) + 1):
        ini = k * passo
        a, b = int(ini * SR), min(n, int((ini + passo + 1.2) * SR))
        if a >= n:
            break
        tt = t[a:b] - ini
        e = np.clip(tt / 0.9, 0, 1) * np.clip((passo + 1.2 - tt) / 1.2, 0, 1)
        for j, nota in enumerate(ACORDES[k % len(ACORDES)]):
            f = hz(nota)
            for desv, lado in ((-0.0012, -0.5), (0.0012, 0.5)):  # leve chorus
                ff = f * (1 + desv)
                v = (np.sin(2 * np.pi * ff * tt) + 0.28 * np.sin(4 * np.pi * ff * tt)
                     + 0.08 * np.sin(6 * np.pi * ff * tt))
                trem = 1 - 0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * tt + j))
                ganho = 0.55 if j == 0 else 0.32
                pad[a:b] += estereo(v * e * trem * ganho, pan=lado * 0.6)
    pad[:, 0] = filtro(pad[:, 0], lo=60, hi=1600)
    pad[:, 1] = filtro(pad[:, 1], lo=60, hi=1600)
    pad /= np.abs(pad).max() + 1e-9
    # vinil: estalinhos esparsos + chiado
    estalos = np.zeros(n)
    idx = rng.choice(n, size=int(dur * 6), replace=False)
    estalos[idx] = rng.standard_normal(len(idx)) * rng.random(len(idx)) ** 3
    estalos = filtro(estalos, lo=1500, hi=9000)
    estalos /= np.abs(estalos).max() + 1e-9
    chiado = filtro(rng.standard_normal(n), lo=3000, hi=10000)
    chiado /= np.abs(chiado).max() + 1e-9
    # ar de sala: ruído marrom bem grave
    ar = np.cumsum(rng.standard_normal(n))
    ar = filtro(ar - ar.mean(), lo=40, hi=400)
    ar /= np.abs(ar).max() + 1e-9
    mix = pad * db(-6) + estereo(estalos * db(-24) + chiado * db(-42) + ar * db(-26))
    fade = np.clip(t / 1.0, 0, 1) * np.clip((dur - t) / 1.2, 0, 1)
    mix *= fade[:, None]
    return mix / (np.abs(mix).max() + 1e-9) * db(-6)


AMBIENTES = {"cafe": cafe}


# ---------------------------------------------------------------- plano → sons

def eventos_do_plano(plano):
    """Regra fixa por tipo de evento: o mesmo tipo de evento sempre soa igual."""
    ev = []
    for e in plano.get("efeitos", []):
        tp = e["tipo"]
        if tp == "flash":
            ev.append(("sopro", e["inicio"] - 0.22, None))  # o pico do sopro cai no pico do flash
        elif tp == "titulo_empilhado":
            for p in e["palavras"]:
                ev.append(("toque", p[1], None))
        elif tp == "destaque":
            if e.get("script"):
                dur = len(e["script"]) / e.get("letras_por_s", 20)
                ev.append(("caneta", e["inicio"], dur))
            else:
                ev.append(("toque", e["inicio"], None))
    return ev


def mixar(video, plano, saida, ambiente="cafe", vol_amb=-30.0, vol_sfx=-20.0):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]))
    n = int(dur * SR)
    sfx = np.zeros((n, 2))
    gera = {"sopro": sopro, "toque": toque, "caneta": caneta}
    for nome, t0, d in eventos_do_plano(plano):
        s = gera[nome](d) if d else gera[nome]()
        a = int(max(0, t0) * SR)
        b = min(n, a + len(s))
        if a < n:
            sfx[a:b] += s[:b - a]
    tmp = os.path.splitext(saida)[0]
    escrever(tmp + "_sfx.wav", sfx * db(vol_sfx + 6))
    filtros = []
    entradas = ["-i", video, "-i", tmp + "_sfx.wav"]
    if ambiente:
        escrever(tmp + "_amb.wav", AMBIENTES[ambiente](dur) * db(vol_amb + 6))
        entradas += ["-i", tmp + "_amb.wav"]
        # o ambiente abaixa ~8 dB quando há voz (sidechain) e volta nas pausas
        filtros.append("[0:a]asplit=2[voz][chave];"
                       "[2:a][chave]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=450[amb];"
                       "[voz][1:a][amb]amix=inputs=3:normalize=0:duration=first[mix]")
    else:
        filtros.append("[0:a][1:a]amix=inputs=2:normalize=0:duration=first[mix]")
    filtros.append("[mix]alimiter=limit=0.89:level=false[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", saida],
                   check=True)
    for f in (tmp + "_sfx.wav", tmp + "_amb.wav"):
        if os.path.exists(f):
            os.remove(f)
    print("Pronto:", saida)


def escrever(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", path],
                   input=pcm, check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=["mix", "amostras"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--ambiente", default="cafe", help="cafe ou nenhum")
    ap.add_argument("--volume-ambiente", type=float, default=-30.0, help="dB relativos (padrão -30)")
    ap.add_argument("--volume-efeitos", type=float, default=-20.0, help="dB relativos (padrão -20)")
    a = ap.parse_args()
    if a.acao == "amostras":
        pasta = a.args[0] if a.args else "amostras"
        os.makedirs(pasta, exist_ok=True)
        for nome, s in (("sopro", sopro()), ("toque", toque()), ("caneta", caneta(0.7)), ("cafe", cafe(12))):
            escrever(os.path.join(pasta, nome + ".wav"), s)
        print("Amostras em", pasta)
        sys.exit(0)
    video, plano_path, saida = a.args
    with open(plano_path, encoding="utf-8") as f:
        plano = json.load(f)
    amb = None if a.ambiente == "nenhum" else a.ambiente
    mixar(video, plano, saida, amb, a.volume_ambiente, a.volume_efeitos)
