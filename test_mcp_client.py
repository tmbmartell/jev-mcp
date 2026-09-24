#!/usr/bin/env python3
"""
Teste real do servidor MCP do Jev, falando o protocolo MCP por stdio.

Roda com o python do Hermes (que tem o pacote mcp):
    /usr/local/lib/hermes-agent/venv/bin/python test_mcp_client.py
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER], env=dict(os.environ))
    print(f"subindo: {sys.executable} {SERVER}\n")

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print("1) initialize OK")
            print(f"   servidor: {init.server_info.name} v{init.server_info.version}")
            print(f"   instructions recebidas: {bool(init.instructions)} "
                  f"({len(init.instructions or '')} chars)\n")

            tools = await session.list_tools()
            print(f"2) tools/list -> {len(tools.tools)} ferramenta(s)")
            for t in tools.tools:
                props = list((t.input_schema or {}).get("properties", {}).keys())
                print(f"   - {t.name}  args={props}")
            print()

            print("3) tools/call jev_health")
            r = await session.call_tool("jev_health", {})
            print("   " + r.content[0].text[:600] + "\n")

            print("4) tools/call jev_decisions (chamada REAL ao Jev)")
            r = await session.call_tool("jev_decisions", {
                "state": ("Cliente: Joao. Plano enterprise. "
                          "Ticket: 'Meu checkout mostra tela branca depois que clico em Pagar. "
                          "Ja tentei dois navegadores.'"),
                "questions": {
                    "e_bug": {"type": "noul",
                              "instructions": "O cliente esta relatando um defeito de software?"},
                    "equipe": {"type": "choice",
                               "instructions": "Qual equipe deve assumir este ticket?",
                               "criteria": {"account": "Login, permissoes ou perfil.",
                                            "frontend": "Renderizacao, layout ou navegador.",
                                            "payments": "Checkout, cobranca ou pagamento."}},
                    "urgencia": {"type": "score",
                                 "instructions": "Quao urgente e este ticket?",
                                 "criteria": ["Pode esperar a proxima versao",
                                              "Deveria ser corrigido esta semana",
                                              "Bloqueando receita agora"]},
                },
            })
            print("   " + r.content[0].text + "\n")

            print("5) tools/call com pergunta invalida (score com criteria de objeto)")
            r = await session.call_tool("jev_decisions", {
                "state": "teste",
                "questions": {"x": {"type": "score", "instructions": "q?",
                                    "criteria": {"0": "a", "1": "b"}}},
            })
            print("   " + r.content[0].text + "\n")

            print("6) ferramenta inexistente")
            r = await session.call_tool("nao_existe", {})
            if r.isError:
                print(f"   recusado como esperado (isError=True): "
                      f"{r.content[0].text[:80]}")
            else:
                print("   FALHA: deveria ter retornado erro")

    print("\nTESTE COMPLETO OK")


if __name__ == "__main__":
    asyncio.run(main())
