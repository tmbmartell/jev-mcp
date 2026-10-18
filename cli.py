#!/usr/bin/env python3
"""
CLI do Jev para uso dentro do Hermes.

Le um pedido em JSON (arquivo, argumento ou stdin) e imprime a resposta
normalizada em JSON, ja validada por regra.

Entrada:
{
  "state": "texto ou objeto ou lista",
  "questions": { "<id>": {"type":"noul|choice|score", ...} },
  "route": "openrouter" | "typesafe"      (opcional, padrao openrouter)
}

Saida (sempre JSON, uma linha por objeto):
{
  "ok": true,
  "route": "...", "model": "...", "provider": "...",
  "answers": {...},
  "validation": [],
  "cost_usd": 0.00002,
  "input_tokens": 412, "output_tokens": 73
}

Em erro: {"ok": false, "error": "..."} e exit 1.

Exemplos:
  jev '{"state":"quero cancelar","questions":{"reclamacao":{"type":"noul","instructions":"E uma reclamacao?"}}}'
  jev --file /tmp/pedido.json
  cat pedido.json | jev
  jev --help
"""
import json
import sys
import os

# O cliente HTTP vive no clone do servidor MCP. JEV_MCP_HOME aponta para o clone;
# sem ele, procura no diretório do próprio cli.py e no clone padrão.
for _cand in (os.environ.get("JEV_MCP_HOME"),
              os.path.dirname(os.path.abspath(__file__)),
              "/root/jev-mcp"):
    if _cand and os.path.exists(os.path.join(_cand, "jev.py")):
        sys.path.insert(0, _cand)
        break

import jev as jm  # noqa: E402


def emit(obj, code=0):
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if args[0] == "--file":
        if len(args) < 2:
            emit({"ok": False, "error": "--file exige um caminho"}, 1)
        raw = open(args[1]).read()
    elif args[0] == "-":
        raw = sys.stdin.read()
    elif args[0].strip().startswith("{"):
        raw = args[0]
    else:
        raw = sys.stdin.read()
        if not raw.strip():
            emit({"ok": False, "error": "entrada vazia ou argumento invalido"}, 1)

    try:
        payload = json.loads(raw)
    except Exception as e:
        emit({"ok": False, "error": f"JSON invalido: {e}"}, 1)

    state = payload.get("state")
    questions = payload.get("questions")
    if state is None or not isinstance(questions, dict) or not questions:
        emit({"ok": False, "error": "campos obrigatorios: state e questions (objeto nao vazio)"}, 1)

    route = payload.get("route", os.environ.get("JEV_ROUTE", "openrouter"))
    if route not in jm.ROUTES:
        emit({"ok": False, "error": f"rota invalida: {route} (use {list(jm.ROUTES)})"}, 1)

    # valida o formato das perguntas ANTES de gastar chamada
    for qid, q in questions.items():
        if not isinstance(q, dict) or "type" not in q or "instructions" not in q:
            emit({"ok": False, "error": f"pergunta '{qid}': precisa de type e instructions"}, 1)
        if q["type"] not in ("noul", "choice", "score"):
            emit({"ok": False, "error": f"pergunta '{qid}': type invalido '{q['type']}'"}, 1)
        if q["type"] == "choice" and not isinstance(q.get("criteria"), dict):
            emit({"ok": False, "error": f"pergunta '{qid}': choice exige criteria como OBJETO"}, 1)
        if q["type"] == "score" and not isinstance(q.get("criteria"), list):
            emit({"ok": False, "error": f"pergunta '{qid}': score exige criteria como ARRAY ordenado"}, 1)

    try:
        status, resp = jm.ask(state, questions, route=route)
    except jm.JevConfigError as e:
        emit({"ok": False, "error": str(e)}, 1)
    if status != 200:
        emit({"ok": False, "http_status": status, "error": resp}, 1)

    errs = jm.validate(questions, resp.get("answers", {}))
    u = resp.get("usage") or {}
    emit({
        "ok": not errs,
        "route": route,
        "model": resp.get("model"),
        "provider": resp.get("provider"),
        "answers": resp.get("answers"),
        "validation": errs,
        "cost_usd": jm.cost_of(resp, route),
        "input_tokens": u.get("input_tokens"),
        "output_tokens": u.get("output_tokens"),
        "request_id": resp.get("id"),
    }, 0 if not errs else 1)


if __name__ == "__main__":
    main()
