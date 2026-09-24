#!/usr/bin/env python3
"""
Cliente Jev / TypeSafe (HTTP puro, sem dependencias externas).

Endpoint : POST https://api.typesafe.ai/v1/systemone
Chave    : /root/.secrets/typesafe.key  (ou env TYPESAFE_API_KEY)
Modelo   : jev-latest  ->  jev-1.13.0
Preco    : US$42/Btok = US$0,042 por milhao de tokens, cobrado SO na entrada.

Uso rapido:
    python3 typesafe.py selftest          # chamada real: noul + choice + score
    python3 typesafe.py ask '{"state": "...", "questions": {...}}'
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.typesafe.ai/v1/systemone"
KEY_FILE = "/root/.secrets/typesafe.key"
DEFAULT_MODEL = "jev-latest"
USD_PER_INPUT_TOKEN = 42.0 / 1e9  # US$42 por bilhao

RETRYABLE = {429, 500, 502, 503, 529}


def load_key():
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not key and os.path.exists(KEY_FILE):
        key = open(KEY_FILE).read().strip()
    if not key:
        print("ERRO: chave do TypeSafe nao encontrada.")
        print(f"Crie {KEY_FILE} (chmod 600) ou exporte TYPESAFE_API_KEY.")
        print("A chave sai em https://console.typesafe.ai/keys")
        sys.exit(2)
    return key


def systemone(state, questions, model=DEFAULT_MODEL, retries=4, timeout=120):
    """Envia state + questions[]. Devolve o corpo da resposta ja parseado."""
    key = load_key()
    body = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    delay = 1.0
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            API,
            data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            if e.code in RETRYABLE and attempt < retries:
                wait = e.headers.get("retry-after")
                time.sleep(float(wait) if wait else delay)
                delay *= 2
                continue
            return e.code, {"raw_error": detail}
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            return 0, {"raw_error": str(e)}
    return 0, {"raw_error": "retries esgotados"}


# ----------------------------------------------------------------------------
# Validacao por regra: o modelo interpreta, o codigo confere o contrato.
# ----------------------------------------------------------------------------
def validate(questions, answers):
    """Confere cada resposta contra o tipo da pergunta. Devolve lista de erros."""
    errs = []
    if not isinstance(answers, dict):
        return ["campo 'answers' ausente ou nao e objeto"]
    for qid, q in questions.items():
        a = answers.get(qid)
        if a is None:
            errs.append(f"{qid}: sem resposta")
            continue
        t = q["type"]
        if a.get("type") != t:
            errs.append(f"{qid}: type '{a.get('type')}' != pergunta '{t}'")
            continue
        if t == "noul":
            v = a.get("noul")
            if not isinstance(v, (int, float)) or not 0.0 <= v <= 1.0:
                errs.append(f"{qid}: noul invalido ({v!r})")
        elif t == "choice":
            opts = list(q["criteria"].keys())
            if a.get("choice") not in opts:
                errs.append(f"{qid}: choice '{a.get('choice')}' fora das opcoes")
            probs = a.get("probabilities") or {}
            if abs(sum(probs.values()) - 1.0) > 0.01:
                errs.append(f"{qid}: probabilidades nao somam 1 ({sum(probs.values()):.4f})")
        elif t == "score":
            levels = q["criteria"]
            s = a.get("score")
            if not isinstance(s, (int, float)) or not -0.01 <= s <= len(levels) - 1 + 0.01:
                errs.append(f"{qid}: score {s!r} fora de 0..{len(levels)-1}")
            probs = a.get("probabilities") or {}
            if abs(sum(probs.values()) - 1.0) > 0.01:
                errs.append(f"{qid}: probabilidades nao somam 1 ({sum(probs.values()):.4f})")
        else:
            errs.append(f"{qid}: tipo desconhecido '{t}'")
    return errs


# ----------------------------------------------------------------------------
def selftest():
    state = ("Hi, I've been trying to connect my Stripe account for 3 days and the "
             "integration keeps failing. I'm losing sales. Please help ASAP.")

    questions = {
        "department": {
            "type": "choice",
            "instructions": "Which team should handle this?",
            "criteria": {
                "billing": "Payments, invoicing, refunds",
                "technical": "Bugs, outages, integrations",
                "sales": "Pricing, upgrades, new accounts",
            },
        },
        "is_urgent": {
            "type": "noul",
            "instructions": "Does this message express urgency?",
            "criteria": {"true": "Explicitly time-sensitive", "false": "No urgency expressed"},
        },
        "frustration": {
            "type": "score",
            "instructions": "How frustrated is the customer?",
            "criteria": ["Calm", "Frustrated", "Very angry"],
        },
    }

    print(f"POST {API}")
    print(f"model={DEFAULT_MODEL} | {len(questions)} perguntas em UMA chamada (paralelas)\n")

    status, resp = systemone(state, questions)
    print(f"HTTP {status}")
    if status != 200:
        print(json.dumps(resp, indent=2)[:800])
        return 1

    print(f"model respondido: {resp.get('model')}")
    print("\nRESPOSTAS:")
    print(json.dumps(resp.get("answers"), indent=2, ensure_ascii=False))

    errs = validate(questions, resp.get("answers", {}))
    print("\nVALIDACAO:", "OK - contrato respeitado" if not errs else "FALHOU: " + "; ".join(errs))

    a = resp.get("answers", {})
    dep, urg, fru = a.get("department", {}), a.get("is_urgent", {}), a.get("frustration", {})
    if not errs:
        # Politica explicita em codigo, com limiar de confianca (confidence-gated routing)
        conf = dep.get("confidence", 0)
        if conf < 0.6:
            rota = "REVISAO HUMANA (confianca baixa no roteamento)"
        else:
            rota = f"FILA {dep.get('choice','?').upper()}"
        if urg.get("noul", 0) > 0.7 and fru.get("score", 0) >= 1.5:
            rota += " + PRIORIDADE ALTA"
        print(f"DECISAO (regra em codigo): {rota}")
        print(f"  confianca choice={conf}, p_urgencia={urg.get('noul')}, "
              f"frustracao={fru.get('score')} (conf {fru.get('confidence')})")

    u = resp.get("usage", {})
    inp, out = u.get("input_tokens", 0), u.get("output_tokens", 0)
    print(f"\nUSO: input={inp} tok, output={out} tok (saida nao e cobrada)")
    print(f"CUSTO: US$ {inp * USD_PER_INPUT_TOKEN:.8f}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest":
        sys.exit(selftest())
    elif cmd == "ask":
        payload = json.loads(sys.argv[2])
        st, rp = systemone(payload["state"], payload["questions"], payload.get("model", DEFAULT_MODEL))
        print(json.dumps({"status": st, "response": rp}, indent=2, ensure_ascii=False))
        sys.exit(0 if st == 200 else 1)
    else:
        print(__doc__)
        sys.exit(1)
