# Identidade visual e sonora: O Código Público

## Marca
- **Wordmark:** `{ O CÓDIGO PÚBLICO }`. As chaves `{ }` e a palavra "PÚBLICO" ficam em dourado, o resto em branco, tudo em Montserrat 900 e caixa alta. Componente: `<Wordmark/>`.
- **Handle:** `@ocodigopublico`.
- **Assinatura no vídeo:** uma pílula escura no topo (y≈70) com um círculo dourado `{}` e o handle. Fica presente do início até o encerramento.
- **Conceito:** "o código" são as regras do país (leis, impostos, decisões). A marca mostra como esse código público afeta a vida real, com mapas, números e história.

## Cores (`COR` em `src/base.ts`)
| Uso | Cor |
|---|---|
| Destaque / palavra-chave | ouro `#F5C542` |
| Texto | branco `#FFFFFF` |
| Brasil (glow) / positivo | verde `#7CFC6A` |
| Alerta / falha / riscado | vermelho `#FF4D4D` |
| Água / frio / EUA | azul `#6EC3FF` |
| Card de vidro | `rgba(8,10,14,0.70)` com blur de 18px, borda `rgba(255,255,255,0.14)` e raio de 24px |

Para os fundos das cenas sem mapa, use um gradiente radial com uma cor escura saturada no centro, indo até `#05070b`. Troque o matiz a cada cena: azul-marinho, terracota, petróleo, roxo, verde, ouro-escuro.

## Tipografia
- **Montserrat 900:** títulos, em caixa alta, com `letterSpacing: -1`. Palavras entre `*asteriscos*` ficam douradas (`<Titulo texto="O dinheiro *volta?*"/>`).
- **Montserrat 800:** rótulos e legendas.
- **Playfair Display 700/900, inclusive itálico:** só na quebra histórica.
- **Monospace:** só em nota fiscal e documentos.
- **Tamanhos no vertical:** título de cena 70–120 px, número de impacto 130–190 px, rótulo 22–40 px.

## Motion
- **Ritmo:** algum elemento novo entra a cada 2–3 s. Nada fica parado: o mapa tem deriva contínua, os fundos têm grade e partículas em movimento.
- **Entradas:** pop-in em spring (`<Pop/>`), títulos palavra por palavra subindo com easing back (`<Titulo/>`) e cards subindo com fade (`<Vidro/>`).
- **Câmera do mapa:** keyframes com easing inOut cubic e zoom interpolado em escala logarítmica. A abertura é sempre do mundo para o Brasil, e o fechamento é um zoom-out para o mundo.
- **Contadores:** sobem de 0 até o valor com easing out cubic em cerca de 2 s.
- **Rotas animadas:** moedas e linhas em arco quadrático entre cidades. Quando algo falha, a rota fica vermelha tracejada e piscando, com um ✕ e a moeda caindo.
- **Quebra histórica:** papel envelhecido, Ken Burns de 1,00 a 1,16, granulação mudando a cada frame, vinheta e leve flicker.

## Layout vertical (1080×1920)
- **Cenas com mapa:** o assunto geográfico fica na metade de cima (centro em y≈600) e os cards em `blocoMapa` (top 1040).
- **Cenas sem mapa:** conteúdo em `blocoCentro`, entre y 220 e 1400.
- **Legendas:** `bottom: 400` (a linha fica em y≈1450–1520), sempre em **uma linha só**, com no máximo cerca de 26 caracteres e 3–5 palavras. Fonte de 60 px, peso 800, branca com sombra. Números e palavras-chave ficam em dourado.
- **Zonas seguras:** nada importante abaixo de y 1560 nem acima de y 140, porque é onde ficam a interface do Reels/TikTok e o selo da marca.

## Som
- **Voz:** narração em pt-BR, 1,1×, com highpass em 80 Hz, +3 dB em 4 kHz, compressor 4:1 e loudnorm em −16 LUFS.
- **Trilha:** pulso investigativo em Ré menor, a 90 bpm, com volume em torno de 0,2. Abaixa na quebra histórica e para por cerca de 0,6 s antes da frase de virada.
- **Efeitos** (`public/sfx`): whoosh nos movimentos de câmera e trocas de cena, pop nos ícones, clique nos checks e contadores, moedas nas rotas, scratch na quebra de senso comum, carimbo em documentos, calculadora em contas, tique no calendário, hit nas revelações e riser antes de títulos.

## Capa (`src/Capa.tsx`)
- O fundo é o mapa do tema com glow, escurecido, com moedas ou ícones espalhados.
- A pílula dourada no topo traz o TEMA e o ANO.
- O **número gigante** em dourado tem 230 px.
- Abaixo, uma frase curta em branco.
- A **promessa** vai em faixas inclinadas a −3°: a primeira branca com texto preto, a segunda vermelha com texto branco.
- Fecha com uma pergunta-gancho ("Você está na lista?").
- Todo o texto fica no miolo 3:4 (y 240–1680).

## Encerramento (`<Encerramento/>`)
O fundo é ouro-escuro com grade e chaves gigantes `{ }`. Sobre ele vêm o wordmark, uma linha dourada e o handle. Depois aparecem dois botões com "toque" animado: **SIGA O PERFIL** (dourado) e **ENVIE PARA QUEM PRECISA SABER** (branco). Cada botão tem um clique no áudio.
