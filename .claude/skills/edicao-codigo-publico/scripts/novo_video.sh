#!/usr/bin/env bash
# Cria um novo projeto de vídeo "O Código Público" a partir do template.
# Uso: bash novo_video.sh <pasta-destino>
set -euo pipefail
DEST="${1:?informe a pasta destino}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
  echo "A pasta $DEST já existe e não está vazia." >&2; exit 1
fi
mkdir -p "$DEST"
cp -r "$SKILL_DIR/assets/template/." "$DEST/"
cd "$DEST"
npm install --silent
echo "Projeto criado em $DEST"
echo "Próximo passo: editar scripts/narracao.json e rodar scripts/gerar_voz.py (ver references/producao.md)."
