# Engenharia de roteiro (retenção)

## Fórmula (adapte ao texto recebido, não force)
1. **Gancho (0–8 s):** uma pergunta ou um contraste que toque o bolso ou a vida do espectador. Visual: zoom do mundo até o lugar do tema.
2. **Virada (8–12 s):** a promessa ou a tese ("parte desse dinheiro pode voltar"). Visual: título grande.
3. **Dado de impacto:** o número principal, com contador animado.
4. **Quebra de senso comum:** desfaz a leitura óbvia ("não é a compra que volta, é o imposto"). Visual: algo riscado em vermelho e uma frase de duas linhas.
5. **Blocos de causa e consequência:** quanto, quem, quando e como, cada bloco em uma cena diferente.
6. **Quebra histórica (a cada 30–45 s):** um episódio que ecoe o tema. Exemplos: Derrama de 1789 para impostos, Lei de Terras de 1850 para propriedade, Revolta da Vacina de 1904 para saúde pública, Plano Real de 1994 para inflação.
7. **Prova interna:** uma conta simples que dê escala ao número (total ÷ pessoas ÷ meses). Mostre a fórmula na tela.
8. **Plot twist / desafio:** o obstáculo real ("uma coisa é prometer, outra é entregar").
9. **Pergunta aberta:** uma pergunta que gere comentários. Visual: zoom-out e o selo "COMENTA AÍ ↓".
10. **Encerramento da marca (sempre):** "Siga o Código Público e compartilhe este vídeo com alguém que precisa saber disso."

## Divisão em trechos (`scripts/narracao.json`)
- Um trecho por ideia, com 3–11 s de fala. Cada trecho vira uma cena (`s01`, `s02`…).
- `text` é exatamente o que aparece na legenda: números em algarismos, siglas, `R$`.
- `tts` é como a voz deve falar. Escreva por extenso:
  - anos: "2027" → "dois mil e vinte e sete"
  - porcentagens: "100%" → "cem por cento"
  - dinheiro: "R$ 10 bilhões" → "dez bilhões de reais"
  - siglas soletradas: CBS → "cê bê ésse", CPF → "cê pê éfe", IBS → "i bê ésse", INSS → "i ene ésse ésse"
  - estrangeirismos: "cashback" → "quéchbéc"
- Use vírgulas e reticências no `tts` para criar pausas dramáticas antes das viradas ("Pois agora... parte desse dinheiro").
- Frases curtas e conversacionais, uma ideia por frase.

## Tom da marca
Crítico sem ser panfletário, didático e com um toque de ironia. Por exemplo, em "1/5 = 20%. Coincidência?", ironia aparece numa nota de tela, nunca em ataque pessoal. Mostre a regra (o "código") e o efeito real na vida das pessoas, e deixe a conclusão para o espectador por meio da pergunta final.

## Inserções sugeridas
Sugira no máximo duas linhas novas por roteiro: a prova interna e a quebra histórica. Marque-as como sugestão no plano de edição. Fatos históricos e números precisam estar corretos; na dúvida, não insira.
