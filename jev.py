#!/usr/bin/env python3
"""
Cliente Jev (System One) com duas rotas:

  rota "openrouter" (padrao) -> POST https://openrouter.ai/api/alpha/decisions
                                chave em /root/.secrets/openrouter.key
  rota "typesafe"            -> POST https://api.typesafe.ai/v1/systemone
                                chave em /root/.secrets/typesafe.key

Modelo: typesafe/jev-1.13  (OpenRouter)  |  jev-latest (TypeSafe direto)

IMPORTANTE: o Jev NAO usa /chat/completions. E um modelo de DECISOES:
state + questions tipadas -> answers com probabilidades e confianca.

Uso:
    python3 jev.py selftest
    python3 jev.py battery
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
SECRETS_DIR = os.environ.get("JEV_SECRETS_DIR") or os.path.join(HERMES_HOME, "secrets")


def _keyfiles(name):
    """Locais onde procurar a chave, do mais portavel ao local."""
    return [
        os.path.join(SECRETS_DIR, name),
        os.path.join("/root/.secrets", name),
    ]


ROUTES = {
    "openrouter": {
        "url": "https://openrouter.ai/api/alpha/decisions",
        "model": "typesafe/jev-1.13",
        "env_vars": ["OPENROUTER_API_KEY", "JEV_API_KEY"],
        "keyfiles": _keyfiles("openrouter.key"),
        "usd_per_input_token": 42.0 / 1e9,
    },
    "typesafe": {
        "url": "https://api.typesafe.ai/v1/systemone",
        "model": "jev-latest",
        "env_vars": ["TYPESAFE_API_KEY", "JEV_API_KEY"],
        "keyfiles": _keyfiles("typesafe.key"),
        "usd_per_input_token": 42.0 / 1e9,
    },
}
RETRYABLE = {429, 500, 502, 503, 529}
ROUTE = os.environ.get("JEV_ROUTE", "openrouter")


class JevConfigError(Exception):
    """Configuracao ausente ou invalida (chave, rota)."""


def load_key(cfg):
    """Resolve a chave: variavel de ambiente primeiro (time), arquivo depois (local)."""
    for var in cfg["env_vars"]:
        val = (os.environ.get(var) or "").strip()
        if val:
            return val
    for path in cfg["keyfiles"]:
        if os.path.exists(path):
            val = open(path).read().strip()
            if val:
                return val
    raise JevConfigError(
        "chave ausente. Defina " + " ou ".join(cfg["env_vars"])
        + " (recomendado para o time), ou crie um dos arquivos: "
        + ", ".join(cfg["keyfiles"])
    )


def ask(state, questions, route=None, retries=4, timeout=120, **extra):
    """Envia state + questions. Devolve (http_status, resposta_dict)."""
    r = route or ROUTE
    cfg = ROUTES[r]
    key = load_key(cfg)
    payload = {"model": cfg["model"], "state": state, "questions": questions}
    payload.update(extra)
    body = json.dumps(payload).encode()
    delay = 1.0
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            cfg["url"], data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "X-Title": "jev-client"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:500]
            if e.code in RETRYABLE and attempt < retries:
                w = e.headers.get("retry-after")
                time.sleep(float(w) if w else delay)
                delay *= 2
                continue
            return e.code, {"raw_error": detail}
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(delay); delay *= 2; continue
            return 0, {"raw_error": str(e)}
    return 0, {"raw_error": "retries esgotados"}


def validate(questions, answers):
    """Confere cada resposta contra o contrato da pergunta."""
    errs = []
    if not isinstance(answers, dict):
        return ["campo 'answers' ausente"]
    for qid, q in questions.items():
        a = answers.get(qid)
        if a is None:
            errs.append(f"{qid}: sem resposta"); continue
        t = q["type"]
        if a.get("type") != t:
            errs.append(f"{qid}: type '{a.get('type')}' != '{t}'"); continue
        if t == "noul":
            v = a.get("noul")
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1:
                errs.append(f"{qid}: noul invalido ({v!r})")
        elif t == "choice":
            if a.get("choice") not in q["criteria"]:
                errs.append(f"{qid}: choice '{a.get('choice')}' fora das opcoes")
            pr = a.get("probabilities") or {}
            if pr and abs(sum(pr.values()) - 1.0) > 0.02:
                errs.append(f"{qid}: probabilidades somam {sum(pr.values()):.3f}")
        elif t == "score":
            n = len(q["criteria"]); s = a.get("score")
            if not isinstance(s, (int, float)) or not -0.01 <= s <= n - 1 + 0.01:
                errs.append(f"{qid}: score {s!r} fora de 0..{n-1}")
            pr = a.get("probabilities") or {}
            if pr and abs(sum(pr.values()) - 1.0) > 0.02:
                errs.append(f"{qid}: probabilidades somam {sum(pr.values()):.3f}")
        else:
            errs.append(f"{qid}: tipo desconhecido '{t}'")
    return errs


def cost_of(resp, route=None):
    u = resp.get("usage") or {}
    if "cost" in u and u["cost"] is not None:
        return float(u["cost"])
    return u.get("input_tokens", 0) * ROUTES[route or ROUTE]["usd_per_input_token"]


# ---------------------------------------------------------------- perguntas
QUESTIONS = {
    "department": {
        "type": "choice",
        "instructions": "Qual equipe deve tratar esta mensagem?",
        "criteria": {
            "billing": "Pagamentos, faturas, reembolsos",
            "technical": "Bugs, indisponibilidade, integracoes",
            "sales": "Precos, upgrades, novas contas",
            "other": "Nada disso se aplica",
        },
    },
    "is_urgent": {
        "type": "noul",
        "instructions": "A mensagem expressa urgencia?",
        "criteria": {"true": "Explicitamente sensivel ao tempo", "false": "Sem urgencia"},
    },
    "frustration": {
        "type": "score",
        "instructions": "Qual o nivel de frustracao do cliente?",
        "criteria": ["Calmo", "Frustrado", "Muito irritado"],
    },
}

CASES = [
    ("Help! My payouts have been failing for 3 days. I'm losing sales. Please help ASAP.", "technical"),
    ("How much does the enterprise plan cost for 50 seats? We're evaluating vendors.", "sales"),
    ("I was charged twice this month. I need a refund for the duplicate charge.", "billing"),
    ("Just wanted to say the new dashboard looks lovely. Have a nice weekend!", "other"),
    ("The export button crashes the settings page in Safari. Works in Chrome. A few customers only use Safari.", "technical"),
    ("Can I upgrade from Pro to Business mid-cycle, and how is the proration handled?", "sales"),
]


def decide(ans):
    """Politica explicita em codigo, nunca no modelo."""
    dep = ans.get("department", {})
    urg = ans.get("is_urgent", {})
    fru = ans.get("frustration", {})
    c = dep.get("confidence", 0)
    rota = "REVISAO HUMANA" if c < 0.6 else f"FILA {str(dep.get('choice','?')).upper()}"
    if urg.get("noul", 0) > 0.7 and fru.get("score", 0) >= 1.5:
        rota += " + PRIORIDADE ALTA"
    return rota


def battery():
    print(f"Rota: {ROUTE} | endpoint: {ROUTES[ROUTE]['url']} | modelo: {ROUTES[ROUTE]['model']}")
    print(f"Bateria: {len(CASES)} casos, 1 chamada cada (3 perguntas em paralelo)\n")
    hit = valid = 0
    total = 0.0
    for text, expected in CASES:
        st, resp = ask(text, QUESTIONS)
        if st != 200:
            print(f"  ERRO HTTP {st}: {str(resp)[:140]}")
            print(f"     caso: {text[:60]}")
            continue
        errs = validate(QUESTIONS, resp.get("answers", {}))
        c = cost_of(resp)
        total += c
        if errs:
            print(f"  CONTRATO INVALIDO: {errs[0]}")
            print(f"     caso: {text[:60]}")
            continue
        valid += 1
        a = resp["answers"]
        ok = a["department"]["choice"] == expected
        hit += ok
        print(f"  {'OK ' if ok else 'DIF'} {a['department']['choice']:<10}"
              f" conf={a['department'].get('confidence',0):.2f}"
              f"  p_urg={a['is_urgent']['noul']:.2f}"
              f"  frust={a['frustration']['score']:.2f}"
              f"(c={a['frustration'].get('confidence',0):.2f})"
              f"  {'' if ok else 'esperado=' + expected}")
        print(f"      decisao: {decide(a)}")
        print(f"      modelo respondeu: {resp.get('model')} | custo US$ {c:.8f}")
    print("=" * 70)
    print(f"contrato OK: {valid}/{len(CASES)}   acerto de rotulo: {hit}/{len(CASES)}")
    print(f"CUSTO TOTAL: US$ {total:.8f}")


def selftest():
    state = CASES[0][0]
    st, resp = ask(state, QUESTIONS)
    print(f"POST {ROUTES[ROUTE]['url']}\nHTTP {st}")
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:1500])
    if st != 200:
        return 1
    errs = validate(QUESTIONS, resp.get("answers", {}))
    print("\nVALIDACAO:", "OK" if not errs else "FALHOU: " + "; ".join(errs))
    print("DECISAO:", decide(resp["answers"]))
    print(f"CUSTO: US$ {cost_of(resp):.8f}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    try:
        if cmd == "battery":
            battery(); sys.exit(0)
        sys.exit(selftest())
    except JevConfigError as e:
        print(f"ERRO DE CONFIGURACAO: {e}")
        sys.exit(2)
