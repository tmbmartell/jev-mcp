# Referência dos efeitos

Todos os efeitos aceitam `tipo`, `inicio` e `fim` (segundos). Posições `x`/`y` são frações da tela
(0 = esquerda/topo, 1 = direita/base). `tamanho` multiplica o tamanho padrão. Cores aceitam nome
(`amarelo`, `creme`, `vermelho`, `azul`, `laranja`, `verde`, `branco`, `preto`) ou hex (`"#FF0066"`).

Marcados com ✂ recortam a pessoa (precisam de `ai-edge-litert`).

---

## 01 · `parede_videos`
Abertura: grade de vídeos que dá zoom até o vídeo principal.
| parâmetro | padrão | |
|---|---|---|
| `midias` | quadros do próprio vídeo, com tons diferentes | lista de vídeos/imagens para os outros quadros |
| `duracao_zoom` | 60% do efeito (máx. 1,2 s) | o zoom acontece no fim do efeito |
| `escala_inicial` | 0.34 | tamanho do vídeo principal no começo (0.34 ≈ 3 colunas) |

Duração boa: 2–3 s, logo no início.

## 02 · `celular_flutuando`
| parâmetro | padrão | |
|---|---|---|
| `midia` | tela gerada | imagem ou vídeo para a tela do celular |
| `titulo` / `subtitulo` | "Edição Viral" / "por Claude" | texto da tela gerada |
| `cor_tela` | `#6B3FD1` | cor do degradê da tela gerada |
| `lado` | `direita` | `direita` ou `esquerda` |
| `x`, `y` | 0.3, 0.55 | `x` = distância do centro |

Duração boa: 2–4 s.

## 03 · `zoom_palavra`
| parâmetro | padrão | |
|---|---|---|
| `zoom` | 1.25 | 1.15 sutil · 1.4 forte |
| `centro` | [0.5, 0.36] | ponto do zoom (normalmente o rosto) |
| `palavra` | — | se tiver, aparece gigante no centro |
| `cor`, `y` | amarelo, 0.5 | da palavra |

Duração boa: 0,8–1,5 s, começando ~0,1 s antes da palavra.

## 04 · `checklist`
| parâmetro | padrão | |
|---|---|---|
| `itens` | ["Grava o vídeo", "Manda pro Claude", "Posta"] | 2–5 itens |
| `titulo` | "TUDO QUE VOCÊ PRECISA" | |
| `intervalo` | distribuído | segundos entre itens |
| `cor_check` | amarelo | |
| `riscar` | false | deixa o item cinza quando marcado |
| `y` | 0.6 | |

## 05 · `orbita` ✂
| parâmetro | padrão | |
|---|---|---|
| `midias` | quadros do próprio vídeo | imagens/vídeos dos cards |
| `quantidade` | 6 | |
| `raio` | 0.42 | fração da largura |
| `velocidade` | 0.9 | radianos/s |
| `centro` | [0.5, 0.66] | altura do "anel" (peito/mãos) |
| `tamanho` | 1.0 | |

## 06 · `capa_revista` ✂
| parâmetro | padrão | |
|---|---|---|
| `palavra` | "EDIÇÃO" | curta, maiúscula (encolhe sozinha se não couber) |
| `subtitulo` | — | linha pequena embaixo |
| `atras_da_pessoa` | true | cabeça passa na frente da palavra |
| `cor`, `y`, `tamanho` | branco, 0.085, 1.0 | |

## 07 · `fundo_trocado` ✂
| parâmetro | padrão | |
|---|---|---|
| `fundo` | `#111111` | caminho de imagem **ou** cor |
| `desfoque` | 0 | desfoca a imagem de fundo (ex.: 6) |
| `transicao` | 0.25 | fade de entrada/saída em segundos |

## 08 · `tela_claude`
| parâmetro | padrão | |
|---|---|---|
| `mensagem` | "Acabei de gravar esse vídeo. Edita para mim." | digitada letra a letra |
| `arquivo` | "meu-video.mp4" | chip de anexo |
| `passos` | ["Cortei as pausas", "Legenda e efeitos no lugar", "Postado no Instagram"] | |
| `destacar_ultimo` | true | último passo vira pílula verde |
| `velocidade_digitacao` | 28 | caracteres/s |
| `nome`, `y` | "Claude", 0.04 | |

Duração boa: 4–6 s (precisa de tempo para digitar).

## 09 · `mural_comentarios` (✂ se `fundo_escuro`)
| parâmetro | padrão | |
|---|---|---|
| `comentarios` | 1 de exemplo | lista de `{"usuario", "texto", "rodape"?, "cor_avatar"?}` — até 8 |
| `fundo_escuro` | true | fundo preto atrás da pessoa |
| `intervalo` | 0.25 | segundos entre um comentário e outro |

## 10 · `afasta_e_revela` (✂ no modo `recorte`)
| parâmetro | padrão | |
|---|---|---|
| `modo` | `recorte` | `recorte` (pessoa solta com contorno) ou `card` (o vídeo vira um card) |
| `escala` | 0.72 | quanto encolhe |
| `fundo` | creme | cor revelada |
| `bloco` | true | bloco amarelo atrás |
| `duracao`, `duracao_volta` | 0.8, 0.5 | ida e volta |

## 11 · `recorte_papel` ✂
| parâmetro | padrão | |
|---|---|---|
| `letras` | — | ex.: "50%", "100%", "NOVO" — cada caractere numa caixinha de revista |
| `pos_letras` | [0.3, 0.52] | |
| `circulo` | true | círculo vermelho desenhado em volta da primeira letra |
| `etiqueta` / `etiqueta_em` / `pos_etiqueta` | — / início+1 s / [0.73, 0.525] | pílula amarela |
| `fundo`, `cor_bloco`, `borda` | creme, amarelo, 9 | |

Tem "tremidinha" de stop-motion (8 qps) de propósito.

---

## `legenda`
| parâmetro | padrão | |
|---|---|---|
| `palavras` | — | `[["Tudo", 3.2], ["que", 3.45], ...]` — tempo em que cada palavra começa |
| `texto` | — | alternativa sem tempos: distribui entre `inicio` e `fim` |
| `destaques` | [] | palavras que ficam amarelas |
| `tamanho`, `y`, `cor` | 34, 0.475, branco | |

Gerar `palavras` com Whisper, se disponível:
```python
from faster_whisper import WhisperModel
segs, _ = WhisperModel("small").transcribe("video.mp4", word_timestamps=True, language="pt")
palavras = [[w.word.strip(), round(w.start, 2)] for s in segs for w in s.words]
```

## `titulo_lista`
| parâmetro | padrão | |
|---|---|---|
| `titulo` | ["11 efeitos", "que o Claude faz"] | linhas |
| `destaque` | "11" | palavra do título em amarelo |
| `itens` | [] | lista numerada (divide em 2 colunas) |
| `ativo` | — | índice fixo **ou** `[[indice, segundo], ...]` para ir trocando |
| `y`, `tamanho` | 0.045, 54 | |

## `contador`
`de` (0), `ate` (0), `sufixo` (""), `rotulo` ("cliques no mouse"), `duracao_contagem` (1.0), `y` (0.2).

## `logo_pop`
`imagem` (opcional, PNG do logo), `cor` (laranja), `rotulo` ("Claude"), `x` (0.5), `y` (0.17).

## `dm_link`
`palavra` ("editar"), `mensagem` ("Aqui está o seu link"), `remetente` ("voce · direct"),
`atraso_notificacao` (0.6), `y` (0.86).
