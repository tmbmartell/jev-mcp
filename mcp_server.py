#!/usr/bin/env python3
"""
Servidor MCP do Jev (TypeSafe System One).

Expõe o Jev como ferramenta de primeira classe para agentes (Hermes, Claude Code,
Cursor, qualquer cliente MCP). Sem o Jev como "chat": aqui ele devolve julgamentos
tipados (Noul = probabilidade de sim, Choice = escolha com distribuição,
Score = grau em níveis ordenados), sempre validados por regra antes de sair.

Rodar (stdio):
    python3 mcp_server.py

Registrar no Hermes:
    hermes mcp add jev --command python3 --args /caminho/mcp_server.py

Chave: OPENROUTER_API_KEY (recomendado) ou arquivo em $HERMES_HOME/secrets/openrouter.key
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.mcpserver import MCPServer  # noqa: E402

import jev as jm  # noqa: E402

INSTRUCTIONS = """\
Jev é um modelo de DECISÕES (System One), não de conversa: você envia um estado
(texto ou objeto) e um mapa de perguntas tipadas, e recebe respostas estruturadas
com probabilidade e confiança. Use quando precisar de julgamento semântico que o
código comum não faz: rotear, classificar, ranquear, verificar, extrair por seleção.

Três tipos de pergunta:
- noul   -> probabilidade de sim (0 a 1)
- choice -> uma opção de um conjunto fechado, com distribuição de probabilidade
- score  -> grau em níveis ordenados, com distribuição

Regras obrigatórias:
- noul exige "type" e "instructions". "criteria" é opcional ({true, false}).
- choice exige "criteria" como OBJETO: {opcao: descricao}.
- score exige "criteria" como ARRAY ORDENADO de descrições.

Regra de ouro: a política (limiares, pesos, escalonamento) fica no SEU código,
nunca na pergunta. Use a "confidence" devolvida para mandar casos incertos para
revisão humana. Confiança baixa é informação, não erro.
"""

server = MCPServer(
    name="jev",
    title="Jev (TypeSafe System One)",
    version="1.0.0",
    instructions=INSTRUCTIONS,
)


def _err(msg: str, **extra: Any) -> str:
    return json.dumps({"ok": False, "error": msg, **extra}, ensure_ascii=False)


@server.tool(
    name="jev_decisions",
    description=(
        "Faz um julgamento tipado com o Jev. Envie 'state' (o conteúdo a avaliar: "
        "texto, objeto ou lista) e 'questions' (mapa id -> pergunta tipada). "
        "Devolve as respostas com probabilidades e confiança, já validadas por regra. "
        "Tipos de pergunta: noul {type,instructions,criteria?}, "
        "choice {type,instructions,criteria:{opcao:descricao}}, "
        "score {type,instructions,criteria:[nivel0,nivel1,...]}. "
        "Várias perguntas na mesma chamada rodam em paralelo e não se influenciam."
    ),
)
def jev_decisions(
    state: Any,
    questions: dict[str, Any],
    route: str = "openrouter",
) -> str:
    if route not in jm.ROUTES:
        return _err(f"rota invalida: {route}", rotas=list(jm.ROUTES))
    if not isinstance(questions, dict) or not questions:
        return _err("'questions' deve ser um objeto nao vazio")

    # valida o formato antes de gastar chamada
    for qid, q in questions.items():
        if not isinstance(q, dict) or "type" not in q or "instructions" not in q:
            return _err(f"pergunta '{qid}': precisa de 'type' e 'instructions'")
        if q["type"] not in ("noul", "choice", "score"):
            return _err(f"pergunta '{qid}': type invalido '{q['type']}'")
        if q["type"] == "choice" and not isinstance(q.get("criteria"), dict):
            return _err(f"pergunta '{qid}': choice exige criteria como OBJETO "
                        "({opcao: descricao})")
        if q["type"] == "score" and not isinstance(q.get("criteria"), list):
            return _err(f"pergunta '{qid}': score exige criteria como ARRAY ordenado")

    try:
        status, resp = jm.ask(state, questions, route=route)
    except jm.JevConfigError as e:
        return _err(str(e), como_configurar=(
            "Defina a variavel OPENROUTER_API_KEY, ou crie o arquivo "
            f"{jm.ROUTES['openrouter']['keyfiles'][0]} com a chave."
        ))
    except Exception as e:  # rede, timeout, etc.
        return _err(f"falha na chamada: {e}")

    if status != 200:
        return _err(f"HTTP {status} do provedor", detalhe=resp)

    errs = jm.validate(questions, resp.get("answers", {}))
    u = resp.get("usage") or {}
    return json.dumps({
        "ok": not errs,
        "model": resp.get("model"),
        "provider": resp.get("provider"),
        "answers": resp.get("answers"),
        "validation": errs,
        "cost_usd": jm.cost_of(resp, route),
        "input_tokens": u.get("input_tokens"),
        "output_tokens": u.get("output_tokens"),
        "request_id": resp.get("id"),
    }, ensure_ascii=False)


@server.tool(
    name="jev_health",
    description=(
        "Verifica se o Jev está configurado e alcançável: informa qual rota e chave "
        "estão em uso, se a chave existe, e faz uma chamada real de teste. "
        "Use quando uma chamada ao Jev falhar, ou antes de depurar um fluxo."
    ),
)
def jev_health(route: str = "openrouter") -> str:
    if route not in jm.ROUTES:
        return _err(f"rota invalida: {route}", rotas=list(jm.ROUTES))
    cfg = jm.ROUTES[route]

    origem, tem_chave = None, False
    for var in cfg["env_vars"]:
        if (os.environ.get(var) or "").strip():
            origem, tem_chave = f"variavel {var}", True
            break
    if not tem_chave:
        for path in cfg["keyfiles"]:
            if os.path.exists(path) and open(path).read().strip():
                origem, tem_chave = f"arquivo {path}", True
                break

    info = {
        "rota": route,
        "endpoint": cfg["url"],
        "modelo": cfg["model"],
        "chave_configurada": tem_chave,
        "origem_da_chave": origem,
        "locais_procurados": cfg["keyfiles"],
        "variaveis_aceitas": cfg["env_vars"],
    }
    if not tem_chave:
        return json.dumps({"ok": False, "config": info,
                           "erro": "nenhuma chave encontrada"}, ensure_ascii=False)

    st, resp = jm.ask("Teste de conectividade.", {
        "ping": {"type": "noul", "instructions": "Este texto e um teste tecnico?"}
    }, route=route)
    if st != 200:
        return json.dumps({"ok": False, "config": info, "http_status": st,
                           "detalhe": resp}, ensure_ascii=False)
    return json.dumps({"ok": True, "config": info,
                       "modelo_respondeu": resp.get("model"),
                       "custo_teste_usd": jm.cost_of(resp, route)},
                      ensure_ascii=False)


if __name__ == "__main__":
    server.run(transport="stdio")
