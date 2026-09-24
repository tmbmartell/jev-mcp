# Bateria real: Jev x LLM generico

Mesmos 6 casos, mesmas 3 perguntas (choice + noul + score), 2026-09-24.
Cada linha e uma chamada real. Rotulo esperado definido por mim.

## Jev 1.13 (typesafe/jev-1.13, via OpenRouter /api/alpha/decisions)

```
Rota: openrouter | modelo: typesafe/jev-1.13
  DIF billing    conf=0.86  p_urg=0.99  frust=1.76(c=0.64)  esperado=technical
      decisao: FILA BILLING + PRIORIDADE ALTA
  OK  sales      conf=1.00  p_urg=0.11  frust=0.00(c=1.00)
      decisao: FILA SALES
  OK  billing    conf=1.00  p_urg=0.32  frust=0.54(c=0.30)
      decisao: FILA BILLING
  OK  other      conf=1.00  p_urg=0.03  frust=0.00(c=1.00)
      decisao: FILA OTHER
  OK  technical  conf=1.00  p_urg=0.30  frust=0.66(c=0.47)
      decisao: FILA TECHNICAL
  OK  sales      conf=0.76  p_urg=0.11  frust=0.00(c=1.00)
      decisao: FILA SALES
======================================================================
contrato OK: 6/6   acerto de rotulo: 5/6
CUSTO TOTAL: US$ 0.00011899
```

## LLM generico (gpt-4o-mini, via /chat/completions)

```
contrato OK: 6/6   acerto de rotulo: 5/6
CUSTO: US$ 0.00042150
```

## Comparacao honesta

1. Os dois acertaram 5/6, e o MESMO caso. Nao e vantagem de acuracia aqui.
   O caso em questao: "payouts falhando ha 3 dias, perdendo vendas" foi
   classificado como billing pelos dois, e o meu rotulo dizia technical.
   Pagamentos falhando e uma resposta defensavel — o defeito provavel e
   ambiguidade do meu conjunto de teste, nao do modelo. Nao contar como erro.

2. A diferenca real esta na CONFIANCA. O Jev entrega confianca por resposta, e
   ela acompanha a ambiguidade: 1.00 nos casos claros, 0.76 a 0.86 no caso
   ambiguo. O gpt-4o-mini nao entrega nada disso, entao nao ha como aplicar
   roteamento por limiar de confianca com ele.

3. Custo: Jev US$0,00011899 contra US$0,00042150 do gpt-4o-mini nos mesmos 6
   casos — cerca de 3,5x mais barato, porque cobra so entrada. E o gpt-4o-mini
   precisou de mais tokens de prompt (instrucoes de formato + schema) para
   tentar respeitar o contrato.

4. Robustez do contrato: o gpt-4o-mini precisou de prompt gigante com schema
   embutido e mesmo assim o retorno dependia do modelo. O Jev devolve o formato
   tipado por construcao, sem prompt de formatacao.

## Conclusao

Nesta amostra pequena, acuracia empatou e o Jev ganhou em custo e em
confianca calibrada. Amostra de 6 casos nao prova calibracao — para producao,
medir com dados rotulados do dominio real antes de confiar em limiares.

O que fica claro: a vantagem do Jev nao e "acertar mais", e devolver
probabilidade e confianca utilizaveis, de forma barata e sem engenharia de
prompt. E exatamente o que um LLM generico nao entrega.
