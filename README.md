# Jev MCP — julgamento tipado para agentes

Servidor [MCP](https://modelcontextprotocol.io) que expõe o **Jev** (TypeSafe System One)
como ferramenta de primeira classe para agentes: Hermes, Claude Code, Cursor, ou
qualquer cliente MCP.

O Jev não é um modelo de conversa. É um modelo de **decisões**: você envia um estado
e um mapa de perguntas tipadas, e recebe respostas estruturadas com probabilidade e
confiança — que o seu código usa diretamente, sem `prompt` e `parse`.

## Por que usar

- **Roteamento e classificação** — escolher entre opções fechadas com distribuição de
  probabilidade, não só um rótulo.
- **Ranqueamento** — comparar itens com a mesma régua.
- **Verificação e guardrails** — checar se uma afirmação é sustentada pela fonte.
- **Confiança calibrada** — a resposta traz `confidence`, então caso incerto vai para
  revisão humana em vez de virar decisão silenciosa.

## Instalação

Requisitos: Python 3.10+ e o pacote `mcp`.

Passo a passo completo, com solução de problemas: **[INSTALL.md](INSTALL.md)**

Resumo para Hermes:

```bash
git clone https://github.com/tmbmartell/jev-mcp.git
cd jev-mcp
./scripts/install.sh          # confere, instala e registra
```

### Configurar a chave

A chave é do OpenRouter (o Jev é servido por lá no endpoint de decisions).

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Alternativa sem variável de ambiente (recomendada se o agente filtra o ambiente):

```bash
mkdir -p ~/.hermes/secrets && chmod 700 ~/.hermes/secrets
printf '%s' 'sk-or-v1-...' > ~/.hermes/secrets/openrouter.key
chmod 600 ~/.hermes/secrets/openrouter.key
```

Aceita também `JEV_API_KEY` como nome genérico.

> Rota direta do TypeSafe: defina `TYPESAFE_API_KEY` e passe `route: "typesafe"`.
> Requer conta própria em console.typesafe.ai.

### Claude Code / Claude Desktop

```json
{
  "mcpServers": {
    "jev": {
      "command": "python3",
      "args": ["/caminho/para/jev-mcp/mcp_server.py"],
      "env": { "OPENROUTER_API_KEY": "sk-or-v1-..." }
    }
  }
}
```

### Hermes

```bash
hermes mcp add jev --command python3 --args /caminho/para/jev-mcp/mcp_server.py
```

## Ferramentas expostas

| Ferramenta | Para que serve |
|---|---|
| `jev_decisions` | Faz o julgamento: recebe `state` + `questions`, devolve respostas validadas |
| `jev_health` | Diagnóstico: qual rota e chave estão em uso, e uma chamada real de teste |

## Os três tipos de pergunta

| Tipo | Resposta | Use quando |
|---|---|---|
| `noul` | `{noul: 0..1}` — probabilidade de sim | "Isto é urgente?", "É um bug?" |
| `choice` | `{choice, probabilities, confidence}` | Escolher uma entre opções definidas |
| `score` | `{score, legend, probabilities, confidence}` | Grau em níveis ordenados |

### Contratos (validados antes de gastar chamada)

```jsonc
// noul — criteria opcional
{ "type": "noul", "instructions": "Isto é um defeito?", "criteria": {"true": "...", "false": "..."} }

// choice — criteria OBRIGATÓRIO como objeto
{ "type": "choice", "instructions": "Qual equipe?", "criteria": { "billing": "Pagamentos", "technical": "Bugs" } }

// score — criteria OBRIGATÓRIO como array ordenado
{ "type": "score", "instructions": "Quão grave?", "criteria": ["Cosmético", "Com contorno", "Bloqueante"] }
```

## Exemplo

```jsonc
{
  "state": {
    "customer_tier": "enterprise",
    "ticket": "Meu checkout mostra tela branca depois que clico em Pagar. Já tentei dois navegadores."
  },
  "questions": {
    "e_bug":   { "type": "noul", "instructions": "É defeito de software?" },
    "equipe":  { "type": "choice", "instructions": "Qual equipe assume?",
                 "criteria": { "account": "Login e perfil",
                               "frontend": "Renderização e navegador",
                               "payments": "Checkout e pagamento" } },
    "urgencia": { "type": "score", "instructions": "Quão urgente?",
                  "criteria": ["Pode esperar", "Esta semana", "Bloqueando receita"] }
  }
}
```

Resposta real:

```json
{
  "ok": true,
  "model": "typesafe/jev-1.13-20260917",
  "answers": {
    "e_bug":    { "type": "noul", "noul": 0.95 },
    "equipe":   { "type": "choice", "choice": "payments",
                  "probabilities": { "payments": 0.92, "frontend": 0.08, "account": 0 },
                  "confidence": 0.87 },
    "urgencia": { "type": "score", "score": 2,
                  "legend": { "0": "Pode esperar", "1": "Esta semana", "2": "Bloqueando receita" },
                  "probabilities": { "0": 0, "1": 0, "2": 1 }, "confidence": 0.99 }
  },
  "validation": [],
  "cost_usd": 0.000018774
}
```

## Regra de ouro

**A política fica no seu código, nunca na pergunta.** Limiares, pesos, escalonamento
e o que fazer com confiança baixa são decisões suas:

```python
if ans["equipe"]["confidence"] < 0.6:
    mandar_para_revisao_humana(ticket)
elif ans["urgencia"]["score"] >= 2 and ans["urgencia"]["confidence"] > 0.8:
    escalar_imediatamente(ticket)
else:
    fila_normal(ans["equipe"]["choice"])
```

O Jev devolve julgamento. Quem decide é o seu código.

## Custo

- US$ 42 por bilhão de tokens = **US$ 0,042 por milhão**, cobrado **só na entrada**.
- Saída é grátis.
- Uma chamada com 3 perguntas custa cerca de **US$ 0,00002**.
  Mil chamadas ficam em torno de 2 centavos.

Cada resposta traz `cost_usd`, então dá para contabilizar por fluxo.

## Pegadinhas

1. **O Jev não funciona em `/chat/completions`.** Retorna 400. É modelo de decisões.
2. **Não apareça no catálogo.** Ele não está em `GET /api/v1/models` do OpenRouter
   (é modelo alpha do router de decisions). Varrer o catálogo não prova ausência.
3. **`/api/alpha/decisions` não tem `/v1`.**
4. **Perguntas independentes vão juntas.** Várias perguntas na mesma chamada rodam em
   paralelo e não se influenciam — e sai muito mais barato que chamadas separadas.
5. **`choice` e `score` têm `confidence`; `noul` não.** Para `noul`, use o próprio valor
   como medida: perto de 0,5 significa sim e não igualmente prováveis, não intensidade média.

## Arquivos

```
mcp_server.py         servidor MCP (stdio)  <- o que o time registra no agente
jev.py                cliente HTTP + validacao por regra + as duas rotas (base de tudo)
cli.py                CLI para uso em terminal
test_mcp_client.py    teste de ponta a ponta falando o protocolo MCP
examples/             exemplos de payload
inspect_openapi.py    utilitario: extrai os schemas do openapi.json do OpenRouter
```

Testar o servidor:

```bash
python3 test_mcp_client.py     # requer o pacote mcp
```

## Créditos

Jev e System One são da [TypeSafe](https://typesafe.ai). Documentação oficial:
https://docs.typesafe.ai
