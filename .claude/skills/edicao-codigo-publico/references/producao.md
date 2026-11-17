# Produção técnica

## Pipeline
```bash
bash <skill>/scripts/novo_video.sh videos/<slug-do-tema>    # copia o template e instala dependências
cd videos/<slug-do-tema>
# 1. editar scripts/narracao.json (manter o último trecho = encerramento da marca)
# 2. voz + tempos (Piper offline; o script já aplica atempo 1.1)
python3 scripts/gerar_voz.py <modelo pt_BR-faber-medium.onnx>
# 3. trilha e efeitos (a trilha acompanha a duração)
python3 scripts/gerar_sons.py
# 4. editar src/Cenas.tsx, src/Mapa.tsx (keys, rotas), src/Video.tsx (CENAS, SFX) e src/Capa.tsx
npx tsc --noEmit
# 5. revisão por stills (um por cena)
npx remotion bundle --out-dir /tmp/bundle
npx remotion still /tmp/bundle CashbackTributario /tmp/f.jpg --frame=<n> --scale=0.4
# 6. finais
npx remotion render /tmp/bundle CashbackTributario out/video.mp4 --concurrency=4 --crf=20
npx remotion still /tmp/bundle Capa out/capa.png
python3 scripts/gerar_srt.py   # out/legendas.srt
```
A composição se chama `CashbackTributario` no template. Renomeie-a em `src/Root.tsx` para o slug do novo vídeo.

## Voz
- **Provisória:** Piper TTS (`pip install piper-tts`), com a voz `pt_BR-faber-medium` de huggingface.co/rhasspy/piper-voices (pt/pt_BR/faber/medium).
- **Final:** ElevenLabs ou gravação, com um arquivo por trecho em `public/voz/sNN.wav`. Depois rode `python3 scripts/gerar_voz.py --so-tempos`.
  - Atenção: o modo `--so-tempos` **não** acelera. Se a voz final vier em velocidade normal, aplique `ffmpeg -af atempo=1.1` em cada arquivo antes.
- Os tempos de tudo (cenas, legendas, efeitos) vêm de `src/tempos.json`. Nunca escreva tempos absolutos à mão: use `seg("sNN").start + offset`.

## Problemas de ambiente já conhecidos
- **Remotion não baixa o Chrome** (rede restrita): use `--browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell`. O `remotion.config.ts` do template já aponta para ele, e a variável `REMOTION_CHROME` pode sobrescrever.
- **Fontes:** são locais, em `public/fonts` (woff2 do @fontsource) e carregadas em `base.ts`. Não dependa do Google Fonts no render.
- **Emojis** não renderizam no Chrome headless sem fonte de emoji. Use setas e símbolos Unicode simples (↓ ✓ ✕ ≠ ≈).
- **Imagens de terceiros:** Wikimedia e NASA podem estar bloqueados. A textura de satélite (NASA Blue Marble, domínio público) já vem em `public/world.jpg`. Para B-roll histórico sem acesso a acervo, desenhe a cena (mapa a nanquim, documento, objetos) como no `C08`.
- **Render:** 100 s de vídeo levam de 10 a 15 min com concurrency 4. Rode em background.

## Checklist antes de entregar
- [ ] O último trecho é o encerramento "siga + compartilhe", e a assinatura fica visível do início ao fim
- [ ] Nenhuma legenda quebra em duas linhas nem cobre um card
- [ ] Nada importante abaixo de y 1560
- [ ] Números conferidos, e valores ilustrativos sinalizados
- [ ] Áudio com média em torno de −18 dB e pico abaixo de −0,5 dB (`ffmpeg -af volumedetect`)
- [ ] Os 4 arquivos entregues: vídeo, capa, .srt e texto do post (com o CTA e #ocodigopublico)
