# Cashback Tributário — vídeo explicativo (estilo mapa + infográfico)

Vídeo de ~1min49s, 1920x1080, 30 fps, feito em [Remotion](https://remotion.dev).
Estilo: mapa de satélite escurecido, Brasil com contorno em glow, cards de vidro,
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

Tudo é sincronizado pelo `src/tempos.json`: trocou a voz, recalcula e o vídeo se reajusta.

## Trocar pela voz final (ElevenLabs ou gravação)
1. Grave/gere **um arquivo por trecho** (s01…s15, o texto está em `scripts/narracao.json`).
2. Salve como `public/voz/s01.wav`, `public/voz/s02.wav`…
3. Rode `python3 scripts/gerar_voz.py --so-tempos` (recalcula os tempos).
4. Rode `python3 scripts/gerar_sons.py` (ajusta a duração da trilha).

## Regerar do zero
```bash
npm i
pip install piper-tts numpy
# voz pt-BR: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium
python3 scripts/gerar_voz.py caminho/pt_BR-faber-medium.onnx
python3 scripts/gerar_sons.py
npx remotion studio         # editar/visualizar
npx remotion render CashbackTributario out/cashback-tributario.mp4
```

## Créditos
- Textura: NASA Blue Marble (domínio público), via three-globe.
- Fronteiras: Natural Earth (domínio público); estados: click_that_hood (Code for Germany).
- Fontes: Montserrat e Playfair Display (SIL OFL).
