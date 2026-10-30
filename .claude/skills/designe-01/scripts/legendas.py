"""Gera src/captions.json (blocos de 1–3 palavras, palavras-chave marcadas) a partir de words.json.
Uso: python legendas.py words.json captions.json [ajustes.json]
ajustes.json (opcional):
  {"trocas": [{"de": "ar", "para": "IA", "em": 116.05}],   # "em" = segundo da palavra (±0.1); sem "em" troca todas
   "remover": [{"de": "amou,", "em": 119.49}],
   "chaves": ["tecnologia", "automação"]}                  # palavras-chave extras (minúsculas, sem pontuação)
"""
import json, re, sys

words = [dict(w) for s in json.load(open(sys.argv[1])) for w in s["words"]]
aj = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}

def hit(w, r): return w["w"] == r["de"] and ("em" not in r or abs(w["s"] - r["em"]) < 0.1)
words = [w for w in words if not any(hit(w, r) for r in aj.get("remover", []))]
for w in words:
    for r in aj.get("trocas", []):
        if hit(w, r): w["w"] = r["para"]; break
# "da tempo" -> "dá tempo" é erro clássico do Whisper em PT
for a, b in zip(words, words[1:]):
    if a["w"] == "da" and b["w"].startswith("tempo"): a["w"] = "dá"

# Palavras-chave padrão: substantivos/verbos de peso de conteúdo educativo. Ajuste por vídeo via "chaves".
KEY = {"tecnologia", "tecnológica", "atualizar", "atualiza", "novidade", "novidades", "atrasado", "escada", "diferença",
       "rápido", "aprender", "caminho", "graça", "perdido", "inteligência", "artificial", "degrau", "momento", "aproveita",
       "acorda", "automação", "automações", "fluente", "linguagem", "robô", "funcionário", "dinheiro", "resultado",
       "segredo", "erro", "nunca", "sempre", "grátis", "agora", "hoje", "mudar", "medo", "coragem"}
KEY |= set(aj.get("chaves", []))

def clean(t): return re.sub(r"[.,!…:;\"]", "", t)
chunks, cur = [], []
for w in words:
    if cur:
        prev = cur[-1]
        txt = " ".join(clean(x["w"]) for x in cur + [w])
        if len(cur) >= 3 or len(txt) > 17 or re.search(r"[.,?!…]$", prev["w"]) or w["s"] - prev["e"] > 0.3:
            chunks.append(cur); cur = []
    cur.append(w)
if cur: chunks.append(cur)

res = []
for n, c in enumerate(chunks):
    end = c[-1]["e"] + 0.35
    if n + 1 < len(chunks):
        nxt = chunks[n + 1][0]["s"]
        end = min(end if nxt - c[-1]["e"] > 0.6 else nxt, nxt)
    ws = []
    for w in c:
        t = clean(w["w"]).lower(); base = t.rstrip("?")
        ws.append({"t": "IA" if base == "ia" else t, "s": w["s"], "k": base in KEY})
    res.append({"s": c[0]["s"], "e": end, "w": ws})
json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False)
print(f"{len(res)} blocos de legenda")
print(" | ".join(" ".join(x["t"].upper() if x["k"] else x["t"] for x in r["w"]) for r in res))
