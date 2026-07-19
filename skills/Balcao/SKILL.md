---
name: balcao
description: >-
  Recepcao e atendimento inbound para negocios de servico (clinicas,
  barbearias, lojas, corretoras, concessionarias, escritorios, hospedagem).
  Use quando o usuario colar uma mensagem de cliente que chegou (WhatsApp,
  Instagram, e-mail) e quiser uma resposta pronta, consistente e no tom dele;
  quando quiser triar/priorizar varias mensagens; lidar com uma reclamacao;
  montar ou crescer a base de perguntas e respostas (FAQ) do negocio; criar
  respostas-padrao (saudacao, fora do horario, "vou verificar e retorno"); ou
  ver um resumo do que os clientes mais perguntam. O Balcao responde so com o
  que esta na base - nunca inventa preco, prazo ou politica.
---

# Balcao - a recepcao que responde seu cliente na hora e do seu jeito

O Balcao cuida da conversa de **quem ja chegou** ate o seu negocio: a duvida de
preco, o "voces fazem X?", o "que horas abre?", a reclamacao, o "como uso o que
comprei?". Ele guarda a **base de conhecimento** do negocio (servicos, precos,
horarios, formas de pagamento, politicas e um banco de perguntas e respostas) e
te entrega uma resposta pronta, **consistente e no seu tom**, para voce revisar
e enviar.

O motor (`scripts/balcao.py`, so Python padrao) faz a parte exata e chata:
busca a resposta certa na base, classifica (tria) a mensagem que chegou, registra
o que ainda nao tem resposta e mostra o que mais perguntam. O Claude escreve a
resposta humana. **Regra de ouro: o que nao esta na base nao se inventa** - se o
Balcao nao acha, ele pergunta a voce e guarda na base para a proxima.

Tudo fica em `.balcao/` na sua maquina (local, fora do controle de versao):
`base.md` (a base legivel), `faq.csv` (o banco de perguntas), `lacunas.csv`
(perguntas sem resposta ainda) e `config.md` (tom e identidade).

<!-- SETUP:START -->
## Primeira vez (configuracao) - faca antes de qualquer outra coisa

Se NAO existir `.balcao/config.json` no projeto, configure o Balcao antes de usar.
Pergunte ao dono (de forma natural, uma de cada vez ou via AskUserQuestion) e colete:

1. **Nome do negocio** e tipo (clinica, barbearia, loja, corretora, concessionaria,
   escritorio, hospedagem, outro).
2. **Horario de funcionamento** por dia (seg..dom).
3. **Endereco / ponto de referencia** (se atende presencial).
4. **Servicos e precos** - para cada um: nome, preco (se fixo) e uma descricao curta.
5. **Formas de pagamento** aceitas.
6. **Politicas** importantes (garantia, cancelamento, prazos de entrega/resposta).
7. **O que voces NAO fazem** (para ser honesto com o cliente, sem prometer demais).
8. **As perguntas que voce mais ouve** e a resposta certa de cada uma (o banco de FAQ
   inicial) - quanto mais, melhor o Balcao ja comeca.
9. **Tom** das respostas (ex.: caloroso e proximo / formal / descontraido), a
   **assinatura** e a mensagem padrao de **fora do horario**.

Monte um JSON de respostas (veja `respostas_exemplo.json` para o formato) e grave:

```bash
python3 scripts/primeira_vez.py --respostas /tmp/respostas_balcao.json
```

Esse script grava a config + a `base.md` + semeia o `faq.csv`, poe `.balcao/` no
`.gitignore` e **se apaga**, deixando a skill limpa. Rode uma vez so.

> Em sessao automatica (sem humano), o JSON de respostas pode vir pronto no pedido -
> escreva-o em `/tmp/respostas_balcao.json` e rode o comando acima sem AskUserQuestion.
<!-- SETUP:END -->

## Como trabalhar

1. Garanta que a base existe (senao, faca a Primeira vez acima).
2. Leia `.balcao/config.md` (tom, assinatura, fora do horario) e use a base como
   **unica fonte de verdade**.
3. Para a parte deterministica use o motor; para a resposta final use os modelos de
   `references/modelos_respostas.md`, sempre no tom do dono.
4. Toda resposta que voce gerar e para o dono **revisar e enviar** - nunca diga que
   enviou. O Balcao **sugere**, quem responde e o dono.
5. **Nunca invente.** Se a base nao cobre, registre a lacuna, escreva uma resposta
   honesta de "ja te confirmo isso" e peca a resposta certa ao dono para guardar.

### Modos (combine conforme o pedido)

**1. Responder** - o dono colou uma mensagem de cliente e quer a resposta.
- Triagem: `python3 scripts/balcao.py triar "texto do cliente"` (categoria + urgencia).
- Busque a resposta: `python3 scripts/balcao.py buscar "texto do cliente"`.
- Se achou no FAQ/base -> escreva a resposta no tom do dono, personalizada.
  Marque que foi usada: `python3 scripts/balcao.py usar --id N` (conta as mais pedidas).
- Se **nao** achou -> NAO invente. Registre `python3 scripts/balcao.py lacuna --pergunta "..."`,
  escreva uma resposta-ponte ("otima pergunta, ja confirmo certinho e te respondo")
  e pergunte ao dono a resposta para guardar na base depois.

**2. Triar** - chegaram varias mensagens de uma vez.
- Para cada uma rode `triar` e ordene por urgencia (reclamacao e "urgente" vem primeiro).
- Entregue ao dono a fila priorizada: o que responder agora, o que pode esperar.

**3. Reclamacao** - cliente insatisfeito (urgencia alta).
- Acolha primeiro, peca desculpa pelo transtorno, mostre o proximo passo concreto.
  Nunca discuta nem culpe o cliente. Use o modelo de reclamacao no tom do dono.
- Se virar caso serio (juridico, reembolso), sinalize ao dono para entrar pessoalmente.

**4. Base / FAQ** - montar e crescer a base de conhecimento.
- Adicionar resposta: `python3 scripts/balcao.py add --pergunta "..." --resposta "..." --categoria "preco"`.
- Ver o banco: `python3 scripts/balcao.py faq [--categoria preco]`.
- Ver/abrir lacunas: `python3 scripts/balcao.py lacunas` ; resolver: `... resolver --idl N`.
- Editar fatos longos (precos, horarios, politicas): mexa direto em `.balcao/base.md`.

**5. Respostas-padrao** - gerar os modelos reutilizaveis no tom do dono.
- Crie e guarde no FAQ: saudacao, fora do horario, "vou verificar e ja retorno",
  agradecimento/pos-venda, pedido de avaliacao. Use `add` para deixar prontas.

**6. Resumo** - `python3 scripts/balcao.py resumo` mostra as perguntas mais frequentes
(candidatas a resposta-padrao/automacao), as lacunas a preencher e a distribuicao por
categoria - o raio-x do seu atendimento.

## Regras de ouro
- **Nunca invente** preco, prazo, politica ou endereco - tudo vem da base. Sem base, pergunta.
- **Consistencia** - a mesma pergunta recebe sempre a mesma resposta correta.
- **No tom do dono** - leia `config.md`; humano e curto, nada de robo.
- **Acolha reclamacao** - desculpa + solucao, nunca discussao.
- **Agendamento nao e aqui** - se for marcar horario, encaminhe para a agenda (ex.: skill Pauta).
- O Balcao **sugere**; quem envia e o dono.

## Inputs / Outputs
- **Entra**: mensagens de clientes coladas pelo dono e as perguntas/respostas da base.
- **Sai**: respostas prontas no tom da marca (para revisar e enviar), base atualizada,
  fila triada e o resumo do que mais perguntam. Dados em `.balcao/`.

## Dependencias
- Python 3 (biblioteca padrao apenas - sem instalar nada).
