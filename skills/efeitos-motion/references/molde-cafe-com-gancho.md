# Molde "Café com Gancho"

Estilo minimalista: só voz, texto amarelo-manteiga que aparece no número/conceito, ~50% de tela limpa.
Guia visual completo: https://claude.ai/artifact/CbPpoo7UkdJBPBGy4uZzRV

## Receita
1. `preparar.py`: corte TODAS as pausas > 0,22 s (detecção por energia no áudio limpo, folga de 0,08 s),
   depois acelere até ~175 palavras/min (ex.: 155 ppm → `--velocidade 1.15`). Sem trilha, sem efeito sonoro, -14 LUFS.
2. Abertura: `titulo_empilhado` com a frase-gancho (3–5 palavras), cada palavra no instante em que é dita, até o fim da frase.
3. Corpo: `destaque` a cada número/conceito, 3–5 s cada, máx. 5 palavras, números em algarismo, ~8–10 por minuto,
   sempre com tela limpa (≥ 1 s) entre um e outro.
   - `linhas` (sans) = o fato. `script` (manuscrito) = o conceito/adjetivo. `sub` = complemento pequeno.
   - Entra na palavra-gatilho (±0,15 s); sai no começo da frase seguinte.
4. `legenda` com `"fonte": "lora", "tamanho": 26, "corte_seco": true`, branca.
5. Zonas: peito (y ≈ 0.57–0.69) para quase tudo; topo (0.16–0.26) só se houver espaço acima da cabeça.
   Fundo claro (parede branca/cinza) → `"sombra": true` em tudo, senão o amarelo some.
