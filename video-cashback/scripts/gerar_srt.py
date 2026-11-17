"""Gera out/legendas.srt com os mesmos blocos (3–5 palavras) e tempos das legendas do vídeo (ver src/UI.tsx)."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = json.load(open(os.path.join(ROOT, "src/tempos.json")))

def quebrar(texto):
    palavras = texto.split()
    blocos, atual = [], []
    for i, w in enumerate(palavras):
        atual.append(w)
        fim = re.search(r"[.,:?!;]$", w) is not None
        resto = len(palavras) - i - 1
        if len(atual) >= 5 or (len(atual) >= 3 and fim) or (len(atual) >= 4 and resto != 1):
            blocos.append(atual); atual = []
    if atual:
        if len(atual) == 1 and blocos: blocos[-1] += atual
        else: blocos.append(atual)
    return blocos

def ts(s):
    ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"

linhas, n = [], 1
for s in t["segments"]:
    blocos = quebrar(s["text"])
    pesos = [len(" ".join(b)) + 4 for b in blocos]; soma = sum(pesos); acc = s["start"]
    for b, p in zip(blocos, pesos):
        d = p / soma * s["duration"]
        linhas.append(f"{n}\n{ts(acc)} --> {ts(acc + d)}\n{' '.join(b)}\n"); n += 1; acc += d
os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
open(os.path.join(ROOT, "out/legendas.srt"), "w", encoding="utf-8").write("\n".join(linhas))
print(n - 1, "blocos")
