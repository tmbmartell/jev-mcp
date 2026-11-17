# Catálogo de cenas

O código de cada cena está em `assets/template/src/Cenas.tsx` (exemplo: vídeo do cashback tributário). Para um roteiro novo, **escolha o tipo de cena pelo papel da frase**, copie o padrão e troque textos, ícones e números.

Legenda: 🗺️ = com mapa (Brasil na metade de cima) · ⬛ = sem mapa (fundo próprio de `Fundos`) · 📜 = histórico

| Tipo | Quando usar | Exemplo no template |
|---|---|---|
| 🗺️ **Abertura mundo → país** | Sempre no gancho | câmera em `Mapa.tsx` + `C01` (ícone preso a uma cidade via `camera()`) |
| 🗺️ **Rota de dinheiro / fluxo** | Dinheiro, produtos ou pessoas indo e vindo | rotas `ida`/`volta` em `Mapa.tsx` (moedas em arco) |
| 🗺️ **Título sobre o mapa** | Virada ou promessa | `C02` |
| 🗺️ **Contador + estados acendendo** | Número de pessoas ou lugares atingidos | `C03` + `estOn` em `Mapa.tsx` |
| ⬛ **Comparação em barras** | Desigualdade, antes × depois, A × B | `C04` (barras verticais), `C07` (percentuais) |
| ⬛ **Documento riscado** | Quebra de senso comum ("não é X, é Y") | `C05` (nota fiscal, total riscado, linha que brilha) |
| ⬛ **Grade de ícones** | Lista de itens, serviços ou setores | `C06` (5 ícones com pop sincronizado à fala + número gigante) |
| 📜 **Quebra histórica** | A cada 30–45 s | `C08` (pergaminho, mapa a nanquim, Ken Burns, caixa com o dado histórico) |
| 🗺️ **Checklist** | Requisitos, critérios, passos | `C09` / `ItemCheck` |
| ⬛ **Card + objeto encaixando** | Ação que a pessoa precisa fazer | `C10` (CPF entrando na nota) |
| ⬛ **Linha do tempo vertical** | Datas, prazos, cronograma | `C11` |
| ⬛ **Conta / prova interna** | Escala de números (÷, ×) | `C12` (total → ÷ pessoas → resultado em card dourado) |
| 🗺️ **Desafio / rotas falhando** | Problemas, riscos, gargalos | `C13` + bloco `desafio` em `Mapa.tsx` |
| 🗺️ **Promessa ≠ entrega** | Contraste final com metáfora visual | `C14` (moedas caindo no prato) |
| 🗺️ **Pergunta final** | CTA de comentário, com zoom-out para o mundo | `C15` |
| ⬛ **Encerramento da marca** | **Sempre o último trecho** | `Encerramento` em `Marca.tsx` |

## Ícones disponíveis (`Icones.tsx`)
Carrinho, Moeda, CasaRetorno, Gota, Raio, Esgoto, Chama, Celular, Check, Engrenagem, Alerta, Prato, Pessoa, Calendario, IdCPF.

Precisa de outro? Desenhe-o como SVG flat no mesmo estilo: formas simples, 1–3 cores da paleta e `drop-shadow`. Use viewBox 0–100.

## Outros países e mapas
`scripts/gerar_geo.py` gera os caminhos SVG a partir de `public/countries.geojson` (Natural Earth) e `public/br-states.geojson`. Para destacar outro país, inclua o contorno dele no `geo.json`, mude `BR` e os keyframes de `keys()` em `Mapa.tsx`. Para EUA e outros países em comparação, use glow azul `#6EC3FF`.

## Regras de composição
- Alterne mapa e sem mapa, com no máximo três cenas de mapa seguidas.
- Sincronize os pops com as palavras: estime o tempo por proporção de caracteres dentro do trecho.
- Cada cena sem mapa ganha um fundo com cor e marca d'água próprias (`FUNDOS_A`, `FUNDOS_B` em `Cenas.tsx`). Agrupe cenas sem mapa consecutivas no mesmo `CamadaFundo`, para o mapa não "piscar" entre elas.
