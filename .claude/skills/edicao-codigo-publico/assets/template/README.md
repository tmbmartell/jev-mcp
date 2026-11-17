# Cashback Tributário — vídeo explicativo (estilo mapa + infográfico)

Vídeo **vertical 9:16** (1080x1920, 30 fps, ~1min40s), feito em [Remotion](https://remotion.dev).
Narração 1,1x mais rápida. Estilo: cenas de mapa de satélite (Brasil com glow) alternando com cenas
de fundo próprio (gradiente, grade técnica, marca d'água e partículas); cards de vidro,
ícones com pop-in, títulos Montserrat Black branco/dourado, legendas dinâmicas
e quebra histórica em sépia (1789, a Derrama).

## Estrutura
| Arquivo | O que faz |
|---|---|
| `scripts/narracao.json` | Roteiro por trecho: `text` (legenda) e `tts` (como a voz deve pronunciar) |
| `scripts/gerar_voz.py` | Gera a voz provisória (Piper, offline) e `src/tempos.json` |
| `scripts/gerar_sons.py` | Sintetiza trilha tensa e efeitos (whoosh, pop, moedas, clique...) |
| `scripts/gerar_geo.py` | Converte GeoJSON em contornos SVG alinhados à textura |
| `src/Mapa.tsx` | Mapa, câmera (zoom/pan) e rotas de moedas |
| `src/Cenas.tsx` | Uma cena de sobreposição por trecho (s01–s15) |
| `src/Video.tsx` | Timeline: cenas, legendas, voz, trilha e efeitos (lista `SFX`) |
| `src/Capa.tsx` | Capa vertical (composição `Capa`) |
| `scripts/gerar_srt.py` | Gera `out/legendas.srt` com os mesmos blocos/tempos da tela |

Tudo é sincronizado pelo `src/tempos.json`: trocou a voz, recalcula e o vídeo se reajusta.

## Trocar pela voz final (ElevenLabs ou gravação)
1. Grave/gere **um arquivo por trecho** (s01…s15, o texto está em `scripts/narracao.json`).
2. Salve como `public/voz/s01.wav`, `public/voz/s02.wav`…
3. Rode `python3 scripts/gerar_voz.py --so-tempos` (recalcula os tempos).
4. Rode `python3 scripts/gerar_sons.py` (ajusta a duração da trilha) e `python3 scripts/gerar_srt.py`.

## Regerar do zero
```bash
npm i
pip install piper-tts numpy
# voz pt-BR: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium
python3 scripts/gerar_voz.py caminho/pt_BR-faber-medium.onnx
python3 scripts/gerar_sons.py
npx remotion studio         # editar/visualizar
npx remotion render CashbackTributario out/cashback-tributario-vertical.mp4
npx remotion still Capa out/capa.png
python3 scripts/gerar_srt.py
```

## Créditos
- Textura: NASA Blue Marble (domínio público), via three-globe.
- Fronteiras: Natural Earth (domínio público); estados: click_that_hood (Code for Germany).
- Fontes: Montserrat e Playfair Display (SIL OFL).
