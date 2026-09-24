#!/usr/bin/env bash
# Instalador do MCP do Jev (transporte stdio, execucao local).
# Idempotente: pode rodar varias vezes sem duplicar nada.
#
#   ./install.sh          instala e registra no agente Hermes
#   ./install.sh --check  so verifica o ambiente, nao muda nada
#
# O que ele faz:
#   1. confere o python e a versao minima
#   2. garante o pacote `mcp` no python do agente (e no python do sistema)
#   3. confere se a chave existe
#   4. registra o servidor no Hermes, sem perguntar nada (resp onde o prompt)
#   5. testa a conexao
#
# O que ele NAO faz: nao escreve a sua chave em lugar nenhum. Se faltar chave,
# ele explica e para.

set -uo pipefail

CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

OK="[ok]"; AVISO="[aviso]"; ERRO="[erro]"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER="$REPO_DIR/mcp_server.py"

echo "== Instalador do Jev MCP =="
echo "repositorio: $REPO_DIR"
echo

# ---- 1. python --------------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  PY3="$(command -v python3)"
  VER="$("$PY3" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
  echo "$OK python3 $VER em $PY3"
  case "$VER" in
    3.1[0-9]|3.[2-9][0-9]) : ;;
    *) echo "$ERRO precisa de Python 3.10 ou mais novo (achei $VER)"; exit 1 ;;
  esac
else
  echo "$ERRO python3 nao encontrado"; exit 1
fi

# ---- 2. o agente e o python dele -------------------------------------------
AGENTE=""
AGENT_PY=""
if command -v hermes >/dev/null 2>&1; then
  AGENTE="hermes"
  HERMES_BIN="$(command -v hermes)"
  REAL="$(readlink -f "$HERMES_BIN" 2>/dev/null || echo "$HERMES_BIN")"
  CAND="$(dirname "$REAL")/python"
  [ -x "$CAND" ] && AGENT_PY="$CAND"
  [ -z "$AGENT_PY" ] && AGENT_PY="$PY3"
  echo "$OK agente Hermes detectado"
else
  echo "$AVISO agente Hermes nao esta no PATH"
  echo "       sem ele, registre o servidor no seu cliente MCP (Claude Code, Cursor, etc)"
  echo "       veja INSTALL.md, secao 'outros clientes'"
fi

# ---- 3. pacote mcp ----------------------------------------------------------
# So e necessario no python que EXECUTA o servidor (o mesmo que registramos
# como --command). O python do sistema so importa se voce registrar com ele.
SERVER_PY="${AGENT_PY:-$PY3}"
if "$SERVER_PY" -c "import mcp" >/dev/null 2>&1; then
  echo "$OK pacote mcp presente em $SERVER_PY"
else
  echo "$AVISO pacote mcp FALTANDO em $SERVER_PY"
  if [ "$CHECK_ONLY" -eq 0 ]; then
    echo "       instalando..."
    if "$SERVER_PY" -m pip install --quiet --upgrade mcp; then
      echo "$OK instalado em $SERVER_PY"
    else
      echo "$ERRO falhou. Tente manualmente:"
      echo "       $SERVER_PY -m pip install mcp"
    fi
  fi
fi
if [ "$SERVER_PY" != "$PY3" ]; then
  echo "       (o python do sistema, $PY3, nao precisa do pacote: o servidor roda com $SERVER_PY)"
fi

# ---- 4. chave ---------------------------------------------------------------
tem_chave=0
local_chave=""
if [ -n "${OPENROUTER_API_KEY:-}" ] || [ -n "${JEV_API_KEY:-}" ]; then
  tem_chave=1; local_chave="variavel de ambiente"
else
  for F in "${HERMES_HOME:-$HOME/.hermes}/secrets/openrouter.key" "$HOME/.hermes/secrets/openrouter.key"; do
    if [ -s "$F" ]; then tem_chave=1; local_chave="$F"; break; fi
  done
fi

if [ "$tem_chave" -eq 1 ]; then
  echo "$OK chave encontrada ($local_chave)"
else
  echo "$AVISO chave NAO encontrada"
  echo "       escolha uma das duas formas:"
  echo "         export OPENROUTER_API_KEY=\"sk-or-v1-...\""
  echo "       ou"
  echo "         mkdir -p ~/.hermes/secrets && chmod 700 ~/.hermes/secrets"
  echo "         printf '%s' 'sk-or-v1-...' > ~/.hermes/secrets/openrouter.key"
  echo "         chmod 600 ~/.hermes/secrets/openrouter.key"
  echo "       pegue a chave em https://openrouter.ai/settings/keys"
fi

# ---- 5. registro no agente --------------------------------------------------
if [ "$AGENTE" = "hermes" ]; then
  if hermes mcp list 2>/dev/null | grep -q '^  jev '; then
    echo "$OK servidor 'jev' ja registrado (nada a fazer)"
  elif [ "$CHECK_ONLY" -eq 1 ]; then
    echo "$AVISO servidor 'jev' ainda nao registrado"
  else
    echo "       registrando no Hermes..."
    # o prompt "Enable all tools? [Y/n]" cancela silenciosamente sem TTY
    if printf 'Y\n' | hermes mcp add jev --command "$AGENT_PY" --args "$SERVER" >/tmp/jev-install.log 2>&1; then
      if grep -q "Saved" /tmp/jev-install.log; then
        echo "$OK registrado (2 ferramentas habilitadas)"
      else
        echo "$ERRO o registro nao confirmou. Saida:"
        sed 's/^/       /' /tmp/jev-install.log
      fi
    else
      echo "$ERRO falha ao registrar. Saida:"
      sed 's/^/       /' /tmp/jev-install.log
    fi
  fi
fi

# ---- 6. teste final --------------------------------------------------------
if [ "$AGENTE" = "hermes" ] && [ "$CHECK_ONLY" -eq 0 ] && [ "$tem_chave" -eq 1 ]; then
  echo
  echo "== Teste de conexao =="
  hermes mcp test jev 2>&1 | sed 's/^/  /'
fi

echo
echo "== Fim =="
if [ "$CHECK_ONLY" -eq 0 ]; then
  echo "As ferramentas aparecem para o agente depois de reiniciar a sessao."
  echo "Confira se a chave esta exposta no seu perfil de shell (ex.: ~/.bashrc)"
  echo "se preferiu usar a variavel de ambiente."
fi
