# Precificacao em linguagem simples

O objetivo aqui e parar de chutar preco. Voce vai ancorar em tres pontos e deixar o
motor calcular as faixas. Nunca cobre pelo esforco (horas) na hora de vender -
justifique pelo **resultado** que o cliente leva.

## Os tres pontos que definem um bom preco

1. **Piso (custo)** - quanto o trabalho realmente te custa.
   Conta simples: `quanto vale sua hora x quantas horas o trabalho leva`.
   Voce nunca cobra abaixo disso, senao trabalha de graca (ou no prejuizo).

2. **Referencia (mercado)** - quanto outros cobram por algo parecido.
   Serve para voce nao ficar absurdamente fora da realidade. Pesquise 2-3 concorrentes.

3. **Teto (valor)** - quanto a sua oferta faz o cliente ganhar ou economizar.
   Esse e o ponto mais importante e o mais esquecido. Se voce faz uma clinica faturar
   R$ 8.000 a mais por mes, cobrar R$ 1.500 e barato. Regra pratica: e justo cobrar
   uma fatia (~10% a 20%) do valor que voce gera.

O preco bom mora entre o piso e o teto, perto do valor - nao perto do custo.

## Como o motor calcula

```bash
python3 scripts/forja.py precos --custo-hora 80 --horas 20 --valor-cliente 8000
```

- `--custo-hora`  : quanto vale a sua hora (R$).
- `--horas`       : horas que o trabalho leva (se recorrente, horas por mes).
- `--valor-cliente`: o valor que a oferta gera para o cliente (R$).
- `--recorrente`  : use para mensalidade em vez de projeto unico.
- `--margem`      : multiplicador sobre o custo (padrao 2.5 - cobre impostos, ferramentas e lucro).

Saem 3 faixas:
- **Basico** - entrada acessivel, escopo enxuto.
- **Intermediario** - o mais vendido; ancore o cliente aqui.
- **Premium** - o maximo, para quem quer prioridade e mais entregas.

## A regra das 3 faixas (ancoragem)

Sempre ofereca tres. A maioria escolhe a do meio - e isso e otimo, porque e onde voce
quer que ela fique. O Basico faz a do meio parecer um bom negocio; o Premium faz a do
meio parecer barata. Tres opcoes vendem mais do que uma.

## Projeto unico x recorrente

- **Projeto unico**: bom para entregar algo com comeco, meio e fim (montar um sistema,
  criar um agente, organizar uma planilha). Recebe de uma vez (ou em 2-3 parcelas).
- **Recorrente (mensalidade)**: bom para algo continuo (manter um atendente de IA,
  acompanhar resultados todo mes). Da previsibilidade - e o que faz o negocio crescer
  de forma estavel. Sempre que der, tente transformar parte da oferta em recorrente.

## Erros comuns de preco (evite)

- **Cobrar barato por inseguranca.** Preco baixo nao traz mais cliente - traz cliente
  ruim e desvaloriza voce. Comece com um preco justo.
- **Cobrar por hora na frente do cliente.** Ele passa a contar suas horas. Cobre pelo
  pacote/resultado.
- **Esquecer impostos e ferramentas.** Por isso a margem padrao e 2.5x o custo.
- **Uma opcao so.** Sem comparacao, o cliente compara com "nao comprar". Da 3 faixas.
