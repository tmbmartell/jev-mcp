#!/usr/bin/env bash
# designe-01 — prepara um projeto de Reel a partir de um vídeo.
# Uso: bash preparar.sh VIDEO.mp4 PASTA_DO_PROJETO [idioma=pt]
# Faz: copia o template, instala dependências, padroniza o vídeo (1080x1920, áudio -14 LUFS),
#      transcreve com tempo por palavra (words.json) e gera src/config.ts.
# Variáveis opcionais: WHISPER_MODEL (padrão "small"; "medium" é mais preciso e ~3x mais lento).
set -euo pipefail
SRC="$(readlink -f "$1")"; PROJ="$2"; LANG_CODE="${3:-pt}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="${WHISPER_MODEL:-small}"

mkdir -p "$PROJ"; PROJ="$(readlink -f "$PROJ")"
cp -rn "$SKILL_DIR/assets/template/." "$PROJ/"
cd "$PROJ"; mkdir -p public work

echo ">> dependências do Remotion"
[ -d node_modules/remotion ] || npm install --silent --no-audit --no-fund
cp node_modules/@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-{500,800}-normal.woff2 \
   node_modules/@fontsource/playfair-display/files/playfair-display-latin-{600,700}-italic.woff2 public/

echo ">> padronizando vídeo (pode levar alguns minutos)"
# Gira conforme os metadados do celular, preenche 9:16 cortando o excesso, normaliza o volume.
ffmpeg -v error -y -i "$SRC" \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,unsharp=5:5:0.4" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 30 \
  -af "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -movflags +faststart public/base.mp4
ffmpeg -v error -y -i public/base.mp4 -ac 1 -ar 16000 work/audio.wav
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 public/base.mp4)
printf '// Gerado por scripts/preparar.sh — duração do vídeo base e do cartão final.\nexport const VIDEO_SECONDS = %.2f;\nexport const END_SECONDS = 3;\n' "$(awk "BEGIN{print $DUR - 0.05}")" > src/config.ts

echo ">> Whisper"
VENV="$HOME/.cache/designe-01/venv"
[ -x "$VENV/bin/python" ] || { python3 -m venv "$VENV"; "$VENV/bin/pip" install -q faster-whisper; }
MODEL_ARG="$MODEL"
if ! "$VENV/bin/python" -c "from faster_whisper.utils import download_model as d; d('$MODEL')" >/dev/null 2>&1; then
  # Rede sem acesso ao Hugging Face: usa a cópia do Whisper small (CTranslate2 int8) publicada no npm em 4 partes,
  # conferindo o SHA-256 publicado junto. Só pesos/JSON — nenhum código é executado desses pacotes.
  MDIR="$HOME/.cache/designe-01/whisper-small"
  if [ ! -f "$MDIR/model.bin" ]; then
    echo "   Hugging Face bloqueado — baixando modelo small via npm"
    T=$(mktemp -d); mkdir -p "$MDIR"
    for i in 0 1 2 3; do (cd "$T" && npm pack -q "@skillninja/shortmovie-telop-model-p$i@1.0.0" >/dev/null && mkdir p$i && tar -xzf ./*p$i-*.tgz -C p$i); done
    P0="$T/p0/package"; cp "$P0"/{config.json,preprocessor_config.json,tokenizer.json,vocabulary.json} "$MDIR/"
    cat "$T"/p0/package/model.bin.part0 "$T"/p1/package/model.bin.part1 "$T"/p2/package/model.bin.part2 "$T"/p3/package/model.bin.part3 > "$MDIR/model.bin"
    [ "$(sha256sum "$MDIR/model.bin" | cut -d' ' -f1)" = "$(cat "$P0/model.sha256")" ] || { echo "SHA-256 não confere"; rm -rf "$MDIR"; exit 1; }
    rm -rf "$T"
  fi
  MODEL_ARG="$MDIR"
fi
"$VENV/bin/python" -I "$SKILL_DIR/scripts/transcrever.py" work/audio.wav work/words.json "$MODEL_ARG" "$LANG_CODE"
echo ">> pronto: $PROJ (duração $DUR s). Próximo: revisar transcrição, rodar legendas.py, escrever src/roteiro.tsx."
