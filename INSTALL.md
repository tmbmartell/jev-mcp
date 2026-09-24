# Instalação

Guia para colocar o Jev MCP para funcionar na sua máquina.

Tempo estimado: 3 minutos.

## Requisitos

- Python 3.10 ou mais novo
- Uma chave do OpenRouter (https://openrouter.ai/settings/keys)
- Um cliente MCP: Hermes, Claude Code, Cursor, ou qualquer outro

## Atalho: script de instalação

Para Hermes, há um script que faz tudo e não duplica nada se você rodar mais de uma vez:

```bash
git clone https://github.com/tmbmartell/jev-mcp.git
cd jev-mcp
./scripts/install.sh
```

Ele confere Python, instala o pacote `mcp` no lugar certo, verifica a chave e registra
o servidor. Para só inspecionar o ambiente sem mudar nada:

```bash
./scripts/install.sh --check
```

Se preferir entender cada passo, siga o manual abaixo.

## Manual

### 1. Clonar

```bash
git clone https://github.com/tmbmartell/jev-mcp.git
cd jev-mcp
```

### 2. Instalar o pacote mcp

O servidor é escrito com o SDK oficial do MCP, então esse pacote é obrigatório.

```bash
python3 -m pip install mcp
```

**Atenção:** se você usa Hermes, o pacote precisa estar no Python que executa o
servidor. No passo 4, o `--command` aponta para o Python do próprio Hermes, então
instale nele:

```bash
# descobrir o python do Hermes
readlink -f "$(command -v hermes)"     # ex.: /usr/local/lib/hermes-agent/venv/bin/hermes
# instalar nesse mesmo ambiente
/usr/local/lib/hermes-agent/venv/bin/python -m pip install mcp
```

Esse é o erro mais comum. Sem o pacote no ambiente do agente, o registro conecta,
lista as ferramentas e parece funcionar — mas o agente não descobre nada no início
da sessão, e as ferramentas simplesmente não aparecem.

### 3. Configurar a chave

Escolha uma das duas formas.

**Forma A — variável de ambiente** (mais simples, mas precisa valer no shell do agente)

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Para não repetir toda vez, coloque a linha no seu `~/.bashrc` ou `~/.zshrc`.
Aceita também o nome genérico `JEV_API_KEY`.

**Forma B — arquivo de segredo** (não depende do ambiente; melhor se o agente filtra variáveis)

```bash
mkdir -p ~/.hermes/secrets && chmod 700 ~/.hermes/secrets
printf '%s' 'sk-or-v1-...' > ~/.hermes/secrets/openrouter.key
chmod 600 ~/.hermes/secrets/openrouter.key
```

O arquivo fica fora de qualquer repositório e é lido só pelo servidor.

### 4. Registrar no agente

**Hermes:**

```bash
printf 'Y\n' | hermes mcp add jev \
  --command /usr/local/lib/hermes-agent/venv/bin/python \
  --args /caminho/para/jev-mcp/mcp_server.py
```

O `printf 'Y\n'` responde o prompt `Enable all tools? [Y/n]`. Sem esse empurrãozinho,
em contexto sem terminal interativo o registro cancela em silêncio e nada é salvo.
No seu terminal normal o prompt aparece e você responde `Y` na mão.

O `--command` deve ser um interpretador que tenha o pacote `mcp` (passo 2).

**Outros clientes** (Claude Code, Claude Desktop, Cursor, etc): acrescente ao arquivo
de configuração de MCP do seu cliente:

```json
{
  "mcpServers": {
    "jev": {
      "command": "/usr/local/lib/hermes-agent/venv/bin/python",
      "args": ["/caminho/para/jev-mcp/mcp_server.py"],
      "env": { "OPENROUTER_API_KEY": "sk-or-v1-..." }
    }
  }
}
```

## Verificar

```bash
hermes mcp list     # deve mostrar 'jev' com status enabled
hermes mcp test jev # deve conectar e listar 2 ferramentas
```

Depois de reiniciar a sessão do agente, estas ferramentas ficam disponíveis:

| Ferramenta | Para que serve |
|---|---|
| `jev_decisions` | Faz o julgamento tipado |
| `jev_health` | Diagnóstico da configuração e chamada real de teste |

Se algo parecer errado, peça ao agente para chamar `jev_health`: ele diz qual rota e
qual chave estão em uso, e faz uma chamada de verdade para confirmar.

## Solução de problemas

**As ferramentas não aparecem para o agente**
O pacote `mcp` está faltando no Python do agente (passo 2). Instale nele e reinicie.
Note que `hermes mcp test jev` pode passar mesmo assim, porque o teste sobe o servidor
direto. Testar e funcionar são coisas diferentes aqui.

**"chave ausente" ou erro 401**
A chave não chegou ao servidor. Se usou variável de ambiente, confirme que ela vale no
shell de onde o agente foi iniciado (variável exportada só num terminal não vale em
outro). Se usou arquivo, confira o caminho e a permissão de leitura.

**Erro 429 ou 529**
Limite de uso ou sobrecarga do provedor. O cliente já tenta de novo com espera
progressiva; se persistir, reduza o volume ou tente mais tarde.

**"choice exige criteria como OBJETO"**
Erro de formato na pergunta, apontado antes de gastar chamada. `choice` usa objeto
(`{opcao: descricao}`) e `score` usa array ordenado. Veja o README.

## Custo

Cobrança por token de entrada, saída grátis: US$ 0,042 por milhão, o que dá cerca de
US$ 0,00002 por chamada com 3 perguntas. Mil chamadas ficam em torno de 2 centavos.
Cada resposta traz `cost_usd`, então dá para medir o gasto por fluxo.

Para time: o ideal é uma chave própria por pessoa, ou uma chave compartilhada com
limite de gasto configurado no painel do OpenRouter. Não versione chave em repositório.
