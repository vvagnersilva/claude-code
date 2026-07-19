# Sinais de saúde do cliente (como ler cada um)

A IA lê este guia para **avaliar a saúde de um cliente** conversando com o dono — nunca chutando.
Cada sinal vale **0, 1 ou 2** (quanto maior, mais saudável). O motor `ancora.py saude` transforma
os cinco sinais numa **nota de 0 a 100** e num **semáforo** (🟢🟡🔴) e mostra **o porquê**.

> Regra de ouro: **contexto vale mais que número.** Um cliente que contratou para uma entrega
> trimestral e some entre uma entrega e outra pode estar saudável. Um que contratou resultado
> semanal e sumiu há duas semanas, não. Sempre pergunte, nunca deduza sozinho.

## Os 5 sinais e como perguntar (sem jargão)

### 1. Pagamento — está em dia?
- **2** paga certinho, sem atraso.
- **1** atrasa de vez em quando, mas paga.
- **0** inadimplente / parou de pagar.
- Como perguntar: *"O [cliente] está pagando em dia?"*

### 2. Engajamento — ele participa?
Num negócio de serviço, "usar o produto" é **responder, mandar material, comparecer, dar retorno**.
- **2** responde rápido, participa das reuniões, manda o que você pede.
- **1** morno: responde devagar, às vezes some.
- **0** sumido: não responde, remarca sempre, não aparece.
- Como perguntar: *"Quando você chama o [cliente], ele responde e participa?"*

### 3. Satisfação — ele está contente?
- **2** elogia, indica, demonstra que gosta (ou deu nota alta numa pesquisa).
- **1** neutro: não reclama nem elogia.
- **0** reclamou, demonstrou insatisfação, deu nota baixa.
- Como perguntar: *"No último contato, ele parecia satisfeito ou incomodado com alguma coisa?"*

### 4. Resultado — ele está tendo o que comprou? (o sinal que mais pesa)
O cliente contratou por um **motivo**. Ele está chegando mais perto desse motivo?
- **2** claramente tendo resultado (vendeu mais, resolveu o problema, bateu a meta).
- **1** incerto: talvez, mas ninguém provou.
- **0** sem resultado percebido — e ele sabe disso.
- Como perguntar: *"O [cliente] está tendo resultado com o seu trabalho? Dá pra provar com um número?"*
- **Por que pesa mais:** "tá caro" quase sempre quer dizer "não me provaram valor". Resultado é o
  melhor antídoto contra o cancelamento.

### 5. Relacionamento — quem te contratou ainda está lá?
- **2** o decisor (quem assina/paga) está firme, presente e do seu lado.
- **1** trocou de contato, ou você não fala mais com quem decide.
- **0** o seu padrinho saiu da empresa / perdeu a força.
- Como perguntar: *"Você ainda fala com quem te contratou? Essa pessoa continua no comando?"*
- **Perigo silencioso:** cliente com **um só contato** é um ponto único de falha. Se ele sai, o
  contrato vai junto. Recomende ao dono ter **um segundo relacionamento** dentro do cliente.

## Ajustes automáticos que o motor aplica
- **Tempo sem contato:** 30+ dias tira 5 pontos; 60+ dias tira 10. Relacionamento esfria no silêncio.
- **Reclamação recente:** tira 10 pontos.
- **Travas de realidade:** se dois sinais graves estão zerados (inadimplente, decisor foi embora,
  sem resultado, insatisfeito), o semáforo vira 🔴 mesmo que a conta desse amarelo. Não deixamos um
  cliente perigoso parecer saudável.

## Detectores de padrão (o que a IA deve observar entre uma avaliação e outra)
- **Queda sem recuperação:** era 🟢, virou 🟡 e não voltou → trate como alerta.
- **Queda acelerada:** dois semáforos piores seguidos → aja agora, não espere a renovação.
- **Virada brusca:** de muito ativo para silêncio total → quase sempre é um problema não dito.
- **Padrinho calado:** o decisor parou de responder → risco de renovação, mesmo com o resto ok.

## Cadência de reavaliação
- 🟢 verde: reavalie **1x por mês** (rápido).
- 🟡 amarelo: **quinzenal**, com um plano escrito.
- 🔴 vermelho: **semanal** até virar de cor ou fechar a renovação.
