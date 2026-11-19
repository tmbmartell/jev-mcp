---
name: time-lapse
description: Gera prompts de vídeo com efeito TIME-LAPSE (passagem acelerada do tempo com câmera estática). Use quando pedirem time-lapse, timelapse, pôr do sol acelerado, dia virando noite, abertura de vídeo de viagem ou passagem de tempo.
---

# TIME-LAPSE

**Use em:** abertura de vídeo de viagem ou passagem de tempo.

## O que é
Muitas horas comprimidas em poucos segundos: céu mudando de cor, nuvens correndo, luzes acendendo, movimento acelerado — tudo com **câmera estática**.

## Prompt base (referência)
```
Time-lapse from late afternoon to night: the sun sets behind Rio de Janeiro, clouds race across the sky, the sky turns orange then deep blue and the city lights turn on. Boats move on the bay. Static camera.
```

## Template
```
Time-lapse from {INÍCIO} to {FIM}: {EVENTO_PRINCIPAL} {LOCAL}, clouds race across the sky, the sky turns {COR_1} then {COR_2} and {MUDANÇA_FINAL}. {MOVIMENTO_SECUNDÁRIO}. Static camera.
```

## Variáveis
- **INÍCIO / FIM**: late afternoon → night, night → sunrise, morning → evening, winter → spring...
- **EVENTO_PRINCIPAL**: the sun sets behind / the sun rises over / fog rolls over...
- **LOCAL**: cidade, montanha, praia, deserto, monumento.
- **COR_1 / COR_2**: orange, pink, purple, deep blue...
- **MUDANÇA_FINAL**: city lights turn on, stars appear, streetlights flicker on...
- **MOVIMENTO_SECUNDÁRIO**: boats move on the bay, cars stream along the avenue, crowds flow...

## Como responder
1. Identifique local e janela de tempo desejada.
2. Entregue o prompt final **em inglês**, num bloco de código.
3. Ofereça uma variação (ex.: nascer do sol, ou noite estrelada).
4. Sempre termine com `Static camera.` — é o que segura o efeito.
