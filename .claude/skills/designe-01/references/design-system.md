# designe-01 — sistema visual e catálogo de cenas

## Identidade
| Token | Valor | Uso |
|---|---|---|
| `bg1` / `bg2` | `#12061A` / `#2B0A30` | fundo ameixa em degradê radial (canto superior esquerdo mais claro) |
| `magenta` | `#FF2E8A` | destaque: borda do vídeo, selos, números de capítulo, barra/degrau "quente" |
| `pink` | `#FFB3D6` | frases grandes em serifa e palavras-chave da legenda |
| `cream` | `#FFF4EC` | texto comum |
| brilho | magenta 22% | mancha difusa no canto inferior direito |

Fontes (duas, nunca mais):
- **Plus Jakarta Sans 800** — kickers, legendas comuns, etiquetas. Fala "explicação".
- **Playfair Display 700 itálico** — frase grande, palavra-chave, números. Fala "emoção / ênfase".

A graça está no contraste: frase curta sem serifa em cima ("a grande maioria") + frase serifada itálica grande embaixo ("não se atualiza").

## Canvas e áreas (1080x1920)
- Legenda: tela cheia em y=1360; com `CIRCLE` em 1560; com `CARD` em 1650 (abaixo do card).
- `CIRCLE`: bolinha 220px em x=790, y=130 → títulos com `top >= 400`; gráficos entre 700 e 1450.
- `CARD`: x=130, y=600, 820x1000 → títulos entre `top` 190 e 430 (no máximo 2 linhas).
- Capítulo: canto superior esquerdo (top 150). Selo: centro, top 210.

## Layouts do vídeo
| Layout | Quando usar |
|---|---|
| `FULL(1)` / `FULL(1.14)` | fala principal. Alterne os dois em blocos seguidos: corte seco com zoom = ritmo |
| `CARD` | frase de impacto que resume o que está sendo dito; o rosto continua presente |
| `CIRCLE` | ideia que fica melhor desenhada que falada; o gráfico domina, o rosto vira assinatura |
| `END` | cartão final depois do vídeo acabar (rosto congelado no centro) |

Entre layouts diferentes a janela do vídeo se transforma com mola (sem você fazer nada). Entre dois `FULL` é corte seco.

## Cenas prontas (`src/pecas.tsx`)
| Cena | Layout | Serve para | Assinatura |
|---|---|---|---|
| `Title` | CARD | resumir a frase-chave do trecho | `Title(capítulo\|null, kicker, frase, tamanho?)` |
| `Feed` | CIRCLE | excesso, caos, "muita coisa", lista de exemplos | `Feed(cap, kicker, frase, itens[≤10], destaques[])` |
| `Compare` | CIRCLE | "A vs B", "você vs outros", antes/depois | `Compare(kicker, frase, a, b, selo, iguais?)` |
| `Stairs` | CIRCLE | níveis, progresso, distância, "todo mundo no mesmo lugar" (`crowd`) | `Stairs(cap, kicker, frase, baixo, topo, crowd?, sub?)` |
| `Stack` | CIRCLE + `hideCaps` | repetição retórica / lista falada com tempos | `Stack(cap, kicker, frase, [{s, t}])` |
| `Chips` | CIRCLE | enumeração falada + "o novo item" em destaque | `Chips(kicker, frase, [{s, t}]≤4, destaque)` |
| `Punch` | CARD | fechamento: título + tarja magenta que entra num tempo exato | `Punch(kicker, frase, tarja, tempo)` |
| `End` | END + `hideCaps` | CTA final | `End(kicker, frase, sub?)` |

Selos (`badge` numa cena `FULL`): `{ s, e, kicker, word }` — `word` sai em serifa magenta. Use para a expressão que a pessoa enfatiza na voz ("de graça", "acorda!"). 1–2 por cena no máximo, 2–5 s cada.

## Se nenhuma cena servir
Crie uma nova em `pecas.tsx` seguindo o padrão: fábrica que recebe textos e devolve `({ t0 }) => …`, entra com `useEnter`/`spring`, só usa tokens de `theme.ts`, as duas fontes e formas simples (pílulas, barras, círculos, sublinhado magenta). Ícones e emojis destoam do estilo — prefira tipografia e geometria.

## Ritmo de referência (vídeo de 3 min)
~22 cenas: 11 de tela cheia, 4 `CARD`, 6 `CIRCLE`, 1 `END`; 4 capítulos; 9 selos. Nenhum trecho de rosto em tela cheia passa de ~18 s sem selo ou troca de layout.
