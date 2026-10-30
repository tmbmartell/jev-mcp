#!/usr/bin/env bash
# designe-01 — renderiza quadros de teste ou o vídeo final.
# Uso: bash renderizar.sh PASTA_DO_PROJETO stills 3 24 57 ...   (segundos; gera work/stills/contato.jpg)
#      bash renderizar.sh PASTA_DO_PROJETO final [saida.mp4]
set -euo pipefail
PROJ="$(readlink -f "$1")"; MODE="$2"; shift 2; cd "$PROJ"
BROWSER=()
for b in /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell /opt/pw-browsers/chromium; do
  [ -x "$b" ] && { BROWSER=(--browser-executable="$b"); break; }
done
if [ "$MODE" = stills ]; then
  mkdir -p work/stills; rm -f work/stills/*.png; ins=()
  for s in "$@"; do
    fr=$(awk "BEGIN{printf \"%d\", $s*30 + 0.5}")
    npx remotion still src/index.ts Reel "work/stills/$(printf '%07.2f' "$s").png" --frame="$fr" --scale=0.5 "${BROWSER[@]}" --log=error
  done
  for p in work/stills/*.png; do ins+=(-i "$p"); done
  n=${#ins[@]}; n=$((n/2))
  ffmpeg -v error -y "${ins[@]}" -filter_complex "hstack=inputs=$n,scale=$((n*270)):-1" work/stills/contato.jpg 2>/dev/null \
    || cp "$(ls work/stills/*.png | head -1)" work/stills/contato.jpg
  echo "work/stills/contato.jpg"
else
  OUT="${1:-reel_final.mp4}"
  npx remotion render src/index.ts Reel work/render.mp4 --concurrency="$(nproc)" --crf=20 "${BROWSER[@]}" --log=error
  # cópia mais leve para mandar por WhatsApp / subir no Instagram
  ffmpeg -v error -y -i work/render.mp4 -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart "$OUT"
  ls -la "$OUT"
fi
