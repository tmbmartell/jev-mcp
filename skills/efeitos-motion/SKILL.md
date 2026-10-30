---
name: efeitos-motion
description: Edita vídeos verticais (Reels, TikTok, Shorts) aplicando efeitos de motion design prontos — parede de vídeos, celular flutuando, zoom na palavra, checklist, órbita, capa de revista, fundo trocado, tela do Claude, mural de comentários, afasta e revela, recorte de papel — além de legenda palavra por palavra, título com lista numerada, contador, logo pop e DM com link. Use sempre que o usuário mandar um vídeo e pedir para "editar", "colocar efeito", "deixar viral", "pôr legenda", ou citar qualquer um desses efeitos pelo nome (ex.: "faz o recorte de papel no segundo 12", "coloca a órbita quando eu falar dos clientes", "troca o fundo", "põe aquele celular flutuando", "faz a capa de revista escrito CLAREZA"). Gera o vídeo final em MP4 com áudio original.
---

# Efeitos Motion

Kit de 16 efeitos de motion para vídeo vertical de "talking head" (pessoa falando para a câmera),
renderizados por `scripts/motion.py` (Python + Pillow + ffmpeg, com recorte de pessoa offline).

## Cardápio — como a pessoa pede

| # | Efeito (`tipo`) | Como pedir | O que acontece |
|---|---|---|---|
| 01 | `parede_videos` | "abre com a parede de vídeos" | Grade com vários vídeos; a câmera dá zoom até o vídeo principal ocupar a tela |
| 02 | `celular_flutuando` | "põe um celular flutuando mostrando X" | Mockup de celular entra de lado, flutua e balança |
| 03 | `zoom_palavra` | "dá um zoom quando eu falar *dinheiro*" | Punch-in rápido no rosto (opcional: palavra gigante na tela) |
| 04 | `checklist` | "faz um checklist com: grava, manda, posta" | Card escuro "TUDO QUE VOCÊ PRECISA · 0 de 3" marcando itens |
| 05 | `orbita` | "faz os vídeos girando em volta de mim" | Cards orbitam a pessoa, passando por trás e pela frente |
| 06 | `capa_revista` | "capa de revista escrito CLAREZA" | Palavra gigante em serifa no topo, com a cabeça na frente |
| 07 | `fundo_trocado` | "troca meu fundo por esta foto" | Recorta a pessoa e troca o fundo (imagem ou cor) |
| 08 | `tela_claude` | "mostra a tela do Claude editando" | Janela de chat: anexa o vídeo, digita o pedido, etapas ✓ |
| 09 | `mural_comentarios` | "faz o mural de comentários com estes:" | Comentários voam para a tela, fundo preto atrás da pessoa |
| 10 | `afasta_e_revela` | "afasta a câmera e revela o fundo" | O vídeo recua e revela fundo creme + bloco amarelo |
| 11 | `recorte_papel` | "recorte de papel com 50% e 'acabou de lançar'" | Adesivo com borda branca, rabiscos, letras de revista, etiqueta |
| + | `legenda` | "põe legenda" | Uma palavra por vez, serifa branca, no peito; palavras-chave em amarelo |
| + | `titulo_lista` | "título '11 efeitos que o Claude faz' com a lista" | Título grande + lista numerada em 2 colunas, item ativo em amarelo |
| + | `contador` | "card '0 cliques no mouse'" | Card com ícone de mouse e número que conta |
| + | `logo_pop` | "faz o logo do Claude aparecer" | Ícone redondo com pop + rótulo |
| + | `dm_link` | "fecha com a DM do link, palavra *editar*" | Campo de DM digitando a palavra + notificação "Aqui está o seu link" |

Parâmetros de cada efeito, valores padrão e dicas de tempo: **`references/efeitos.md`**.
Exemplo completo de plano: **`references/plano-exemplo.json`**.

## Fluxo de trabalho

1. **Preparar o ambiente** (uma vez por sessão):
   ```bash
   pip install pillow numpy ai-edge-litert   # ai-edge-litert só é usado nos efeitos que recortam a pessoa
   ffmpeg -version                            # precisa existir
   ```
2. **Entender o vídeo**: rode `ffprobe` para duração/resolução e extraia alguns quadros
   (`ffmpeg -ss T -i video.mp4 -frames:v 1 q.png`) para ver onde está o rosto, o que tem no fundo
   e onde há espaço livre na tela.
3. **Mapear o pedido em tempo**: cada efeito tem `inicio` e `fim` em segundos.
   - Se a pessoa disse "quando eu falar X" e há transcrição disponível (Whisper instalado ou legenda
     enviada por ela), use o tempo da palavra. Sem transcrição, pergunte o segundo aproximado ou
     estime e mostre um preview para ela confirmar.
   - Para `legenda`, prefira `palavras: [[palavra, segundo], ...]` com tempos reais; se só tiver o
     texto, use `texto` + `inicio`/`fim` (o script distribui as palavras pelo tamanho).
4. **Escrever o plano** `plano.json` ao lado do vídeo (caminhos relativos ao JSON). A ordem importa:
   - primeiro os que mexem no quadro inteiro: `parede_videos`, `zoom_palavra`, `fundo_trocado`,
     `recorte_papel`, `afasta_e_revela`;
   - depois os que dependem da pessoa recortada: `orbita`, `capa_revista`, `mural_comentarios`;
   - por último o que só desenha por cima: cards, títulos, `legenda` (sempre no fim, por cima de tudo).
5. **Conferir com preview antes de renderizar** (rápido, um PNG):
   ```bash
   python scripts/motion.py preview plano.json 12.5
   ```
   Olhe o PNG: texto cobrindo o rosto? card cortado na borda? Ajuste `y`, `x`, `tamanho`.
6. **Renderizar**:
   ```bash
   python scripts/motion.py render plano.json            # vídeo inteiro
   python scripts/motion.py render plano.json 10 20      # só um trecho, para testar
   ```
   ~1,5× o tempo real em CPU para 720×1280. Áudio original é mantido.
7. **Entregar** o MP4 e listar em uma tabela curta qual efeito entrou em qual segundo, para a pessoa
   pedir ajustes ("muda a órbita para 2 s depois", "legenda maior").

## Regras de estilo (o "jeito" desse kit)

- Tipografia: **Playfair Display Bold** (serifa de revista) para títulos, legenda e números;
  **Inter** para interface (chat, comentários, DM). Já vêm em `assets/fonts`.
- Paleta: amarelo `#F5D547` (destaque), creme `#EFEBE3` (papel), vermelho `#D2302C` e azul
  `#2E4BC6` (rabiscos), cards escuros translúcidos. Pode passar qualquer cor em hex.
- Um efeito "grande" (que muda o quadro todo) por vez; deixe 2–5 s de vídeo limpo entre eles.
  Efeito o tempo todo cansa — o contraste é o que faz cada um chamar atenção.
- Entradas rápidas (0,25–0,55 s) com leve "overshoot"; saídas mais curtas que entradas.
- Nada em cima do rosto. Faixa segura: deixe livres os 12% de baixo e os 8% de cima
  (interface do Instagram/TikTok).

## Quando algo não sai bem

- **Borda do recorte com "aura"/serrilhado**: o fundo tem cor parecida com a roupa/cabelo. Use
  `recorte_papel` (a borda branca disfarça) ou peça um vídeo com fundo mais contrastante.
- **Sem `ai-edge-litert`** (instalação bloqueada): os efeitos que recortam a pessoa param com aviso.
  Use os demais; `capa_revista` funciona com `"atras_da_pessoa": false` e `mural_comentarios`
  com `"fundo_escuro": false`.
- **Vídeo horizontal**: funciona, mas as posições padrão foram pensadas para 9:16.
- Para criar um efeito novo, siga o padrão do arquivo: uma função `@efeito("nome", "descrição")`
  que recebe `(canvas, t, ef, ctx)` e devolve o canvas.
