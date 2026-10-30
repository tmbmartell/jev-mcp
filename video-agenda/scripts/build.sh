#!/usr/bin/env bash
# Gera video-agenda/out/reels_v<N>.mp4 (1080x1920, 30fps, 30s) — uso: scripts/build.sh 1|2
set -e
cd "$(dirname "$0")/.."
V=$1; TMP=$(mktemp -d "${TMPDIR:-/tmp}/reels.XXXX")
node scripts/render.js "$V" "$TMP"
python3 scripts/audio.py "$TMP/events.json" "$TMP/fx.wav"
mkdir -p out
ffmpeg -loglevel error -y -framerate 30 -i "$TMP/f%04d.jpg" -i "$TMP/fx.wav" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "out/reels_v$V.mp4"
rm -rf "$TMP"
echo "ok out/reels_v$V.mp4"
