# Exemplo de diagnóstico (fictício)

Como uma conversa real com a Turbina costuma acontecer, do equilíbrio ao veredito.

## 1) O dono roda o equilíbrio

> "Meu ticket é R$ 500 e sobra uns 40% de cada venda."

```
$ python3 scripts/turbina.py equilibrio --ticket "R$ 500" --margem 40
ROAS de EQUILÍBRIO: 2,50x
CPA MÁXIMO (empata): R$ 200,00
CPA-ALVO saudável:   R$ 66,00
```

> Turbina: *"Traduzindo: cada venda te deixa R$ 200. Se você pagar mais que R$ 200
> por venda no anúncio, começa a ter prejuízo — esse é o teto. O ideal é mirar uns
> R$ 66 por venda pra sobrar bom lucro. Agora cola a exportação que eu te digo o que
> está dentro e o que está estourando."*

## 2) O dono cola a exportação do Gerenciador

Salvo em `.turbina/metricas.csv`:

```csv
Nome da campanha,Gasto,Impressões,Cliques no link,Resultados,Frequência
Conjunto A - Interesse frio,"R$ 450,00",30000,310,9,1.8
Conjunto B - Lookalike 1%,"R$ 620,00",41000,255,3,2.9
Conjunto C - Retargeting,"R$ 180,00",8000,190,12,3.2
Conjunto D - Aberto novo,"R$ 35,00",2500,20,0,1.1
Conjunto E - Video sem oferta,"R$ 300,00",50000,120,0,1.4
```

## 3) A Turbina diagnostica

```
$ python3 scripts/turbina.py diagnostico --arquivo .turbina/metricas.csv --cpa-alvo "R$ 66" --cpa-max "R$ 200"

🔴 MATAR — Conjunto B - Lookalike 1%
   CPA R$ 206,67 acima do máximo R$ 200,00 (paga p/ vender)
   ✔ pausar; realocar verba para o que converte abaixo do teto
   ⚠ frequência 2,90 subindo → prepare criativo novo

🔴 MATAR — Conjunto E - Video sem oferta
   gastou R$ 300,00 e 0 resultado (acima do custo de 1 venda)
   ✔ pausar; com 0 resultado o gargalo costuma ser oferta/página
   ⚠ CTR 0,24% baixo → criativo/gancho não para o dedo

🟢 ESCALAR — Conjunto A - Interesse frio
   CPA R$ 50,00 dentro/abaixo do alvo R$ 66,00
   ✔ subir verba ~20%/dia SEM resetar aprendizado; duplicar em público novo

🟢 ESCALAR — Conjunto C - Retargeting
   CPA R$ 15,00 dentro/abaixo do alvo R$ 66,00
   ⚠ frequência 3,20 subindo → prepare criativo novo

⚪ AGUARDAR — Conjunto D - Aberto novo
   gasto/resultado ainda baixo p/ decidir (fase de aprendizado)
   ✔ aguardar ~50 resultados ou 3-4 dias antes de mexer
```

## 4) A leitura que a Turbina faz junto do dono

> *"Resumo: mata o B e o E, escala o A e o C, e deixa o D quieto mais uns dias.*
> - *O **B** está estourando o teto por pouco (R$ 207 vs R$ 200) E com frequência
>   subindo — a fadiga de criativo pode ser a causa. Antes de matar de vez, vale
>   testar UM criativo novo nele; se não melhorar em 2 dias, pausa.*
> - *O **E** gastou R$ 300 e não vendeu nada, com CTR baixíssimo (0,24%): o vídeo não
>   para o dedo e não tem oferta clara. Pausa — e o problema aqui é o criativo/oferta,
>   não o público.*
> - *O **A** e o **C** estão ótimos: pode subir a verba deles ~20% a cada 2-3 dias.
>   O C é retargeting (público pequeno), a frequência 3,2 é meio esperada, mas já
>   deixa um criativo novo pronto.*
> - *O **D** mal gastou R$ 35: é cedo pra julgar, deixa juntar dado.*
>
> *Quer que eu monte a matriz do criativo novo pro B e mande pro Verbo escrever?"*

Repare: nenhum número foi inventado — tudo saiu do que o dono colou. E a Turbina só
**sugeriu**; quem pausa e escala no Gerenciador é o dono.
