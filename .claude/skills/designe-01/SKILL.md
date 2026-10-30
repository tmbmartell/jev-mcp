---
name: designe-01
description: Edita vídeos de fala para a câmera (Reels, TikTok, Shorts, vídeo de WhatsApp) no estilo editorial "designe-01" — legenda palavra por palavra com palavras-chave em itálico rosa, fundo ameixa com magenta, vídeo que se transforma em card e em bolinha, capítulos numerados e cenas de gráfico animado — usando Whisper + Remotion e entregando um .mp4 vertical pronto. Use sempre que a pessoa mandar um vídeo dela falando e pedir para editar, legendar, "deixar bonito", "deixar profissional", "fazer igual da última vez", "no meu modelo", "no designe-01", ou quiser transformar uma gravação em Reel, mesmo que não cite Remotion, Whisper ou o nome da skill.
---

# designe-01 — Reel editorial a partir de um vídeo de fala

Transforma uma gravação de alguém falando para a câmera num Reel vertical (1080x1920) com cara de revista: poucas cores, duas fontes, muita repetição. O visual vem de um sistema fixo; o que muda em cada vídeo é só o **roteiro de cenas**, escrito a partir da transcrição.

Por que funciona: a legenda sincronizada segura a atenção sem som; as cenas de gráfico quebram o rosto falando a cada 10–20 s; e a consistência de cor e fonte faz o vídeo parecer "de marca", não "de app de efeito".

## O que tem na skill

- `assets/template/` — projeto Remotion pronto. Você só edita `src/roteiro.tsx` (e, se quiser, a lista de palavras-chave).
  - `src/pecas.tsx` — layouts (`FULL`, `CARD`, `CIRCLE`, `END`) e cenas prontas (`Title`, `Feed`, `Compare`, `Stairs`, `Stack`, `Chips`, `Punch`, `End`).
  - `src/kit.tsx` — o motor (janela do vídeo que se transforma, legendas, selos). Não precisa mexer.
  - `src/theme.ts` — cores e fontes do designe-01.
  - `src/roteiro.tsx` — **exemplo real** do primeiro vídeo feito com a skill. Leia antes de escrever um novo: é o melhor guia de ritmo.
- `scripts/preparar.sh` — copia o template, padroniza o vídeo, transcreve com tempo por palavra.
- `scripts/legendas.py` — gera `src/captions.json` (blocos de 1–3 palavras + palavras-chave).
- `scripts/renderizar.sh` — quadros de teste (`stills`) ou vídeo final (`final`).
- `references/design-system.md` — regras visuais e catálogo das cenas com quando usar cada uma. Leia ao escrever o roteiro.

Requisitos: `ffmpeg`, Node 18+, Python 3.10+, um Chromium (o script acha o do Playwright em `/opt/pw-browsers` sozinho; senão o Remotion baixa o dele).

## Passo a passo

### 1. Preparar e transcrever
```bash
bash <skill>/scripts/preparar.sh VIDEO.mp4 <pasta-do-projeto> pt
```
Leva alguns minutos (o vídeo é refeito em 1080x1920 com volume no padrão de -14 LUFS). Vídeo horizontal é cortado no centro para 9:16 — avise a pessoa, porque pode cortar gente da cena. O script imprime a transcrição com tempos; ela também fica em `work/words.json`.

Se o Hugging Face estiver bloqueado na rede, o script usa sozinho uma cópia do Whisper small publicada no npm, conferindo o checksum. Se nem isso funcionar, peça para a pessoa gerar o JSON no AutoSubs (`autosubs video.mp4 -o transcript.json`) e adapte.

### 2. Revisar a transcrição
O Whisper erra nomes próprios, gírias e palavras abafadas. Leia a transcrição inteira procurando frases que não fazem sentido e corrija com um `work/ajustes.json` (formato no topo de `scripts/legendas.py`). Corrija só o que tiver confiança; **o que for dúvida, liste para a pessoa no final** em vez de inventar — legenda errada com cara de certa é pior que pergunta.

```bash
python3 <skill>/scripts/legendas.py work/words.json src/captions.json work/ajustes.json
```
Confira a saída: palavras-chave aparecem em MAIÚSCULAS. O ideal é ~1 a cada 2–3 blocos. Se tiver demais ou de menos, ajuste `"chaves"` no ajustes.json ou a lista `KEY` no script.

### 3. Escrever o roteiro (`src/roteiro.tsx`)
Esta é a parte criativa — onde está o valor. Divida a fala em blocos de ideia e escolha, para cada um, um layout e (às vezes) uma cena de gráfico. Leia `references/design-system.md` para o catálogo e as regras. Resumo do ritmo que deu certo:

- Abra em `FULL(1)` — o rosto vende o gancho nos primeiros segundos.
- Alterne `FULL(1)` e `FULL(1.14)` entre blocos: o corte seco com zoom dá ritmo sem efeito nenhum.
- A cada 10–20 s, uma cena com `CARD` (frase de impacto em cima) ou `CIRCLE` (gráfico ocupando a tela, rosto na bolinha).
- 3–4 capítulos numerados (`["01", "o caos"]`) marcam a estrutura do argumento.
- Use **selos** (`badge`) nas cenas de tela cheia para destacar uma expressão no instante exato em que é dita.
- Quando a pessoa repete uma estrutura ("ainda dá tempo de… de… de…") use `Stack` com os tempos de cada repetição e `hideCaps: true`.
- Termine com `END` + `End(...)` (CTA) depois do fim do vídeo.

Os tempos (`s`, `e`) vêm de `work/words.json`. Cenas devem cobrir de 0 até `VIDEO_SECONDS + END_SECONDS` sem buracos, em ordem. O texto das cenas é **seu resumo da ideia**, curto (2–5 palavras na frase grande), em minúsculas, no tom da pessoa — não transcreva a fala.

### 4. Conferir com quadros de teste
```bash
bash <skill>/scripts/renderizar.sh <pasta-do-projeto> stills 3 24 57 70 86 122 135 160
```
Escolha segundos no meio de cada cena especial e olhe `work/stills/contato.jpg`. Procure: texto encostando na bolinha do rosto, rótulos cortados na borda, legenda ilegível sobre fundo claro, títulos em mais de 2 linhas. Corrija e gere de novo só os quadros afetados. Isso custa segundos; descobrir o erro depois do render completo custa 15–20 minutos.

### 5. Renderizar e entregar
```bash
bash <skill>/scripts/renderizar.sh <pasta-do-projeto> final reel_final.mp4
```
Um vídeo de 3 min leva ~15–20 min em 4 núcleos — rode em segundo plano. Depois: confira duração e que tem áudio (`ffprobe`), monte um contato de ~12 quadros do resultado e olhe, e entregue o .mp4.

Na mensagem de entrega, diga em linguagem simples: o que foi feito (legenda, capítulos, quais cenas), **a lista de correções de transcrição que você fez e as dúvidas que deixou**, e limitações (ex.: vídeo de WhatsApp vem em baixa resolução — peça o original do celular da próxima vez). Ofereça ajustes concretos (cor, frase, cortar trecho, colocar @ no final).

## Personalização
- **@ / nome da marca**: passe no `End(kicker, big, sub)` — por exemplo `End("não fica pra trás", "segue a gente", "@perfil")`.
- **Cores e fontes**: só mude se a pessoa pedir; o designe-01 é justamente esse visual. Se pedir outro, crie uma variante em vez de sobrescrever.
- **Duração do cartão final**: `END_SECONDS` em `src/config.ts`.
