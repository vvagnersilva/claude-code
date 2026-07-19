---
name: forja
description: >-
  Transforma a sua profissao + IA numa oferta de servico vendavel, com nome,
  publico certo, escopo, preco e plano de lancamento. Use quando a pessoa nao
  sabe O QUE vender com IA, para quem, por quanto, ou como comecar a ganhar
  dinheiro / criar uma renda extra com inteligencia artificial. Tambem quando
  ela tem uma ideia de servico de IA e quer validar, empacotar, precificar,
  montar uma pagina de oferta (one-pager) ou um plano de 30 dias para conseguir
  o primeiro cliente pagante. E o passo ANTES de prospectar.
---

# Forja - de "sei usar IA" para "tenho o que vender"

A Forja pega o que voce ja sabe fazer (sua profissao, sua experiencia) e a IA que
voce tem em maos e transforma isso numa **oferta concreta**: um servico com nome,
publico, escopo, preco e um plano simples para conseguir o primeiro cliente.

E a etapa que vem **antes** de sair prospectando. Primeiro voce decide o que vender
e por quanto (Forja). Depois voce vai atras dos clientes (isso e a Fisga). A Forja
resolve a pergunta que trava todo mundo no comeco:
"beleza, sei usar IA... mas o que eu vendo, para quem e quanto cobro?"

O motor (`scripts/forja.py`, so Python padrao) faz a parte deterministica: calcula
faixas de preco honestas e monta a pagina de oferta em HTML. Voce (Claude) faz a
parte humana: entrevistar, pesquisar, validar e escrever no tom da pessoa.

A configuracao fica em `.forja/config.md` - local, na maquina do usuario, fora do
controle de versao.

<!-- SETUP:START -->
## Primeira vez (configuracao) - faca antes de qualquer outra coisa

Se NAO existir o arquivo `.forja/config.json` no projeto, configure a Forja antes
de usar. Pergunte ao usuario (de forma natural, uma pergunta de cada vez ou via
AskUserQuestion) e colete:

1. **Quem e voce** - nome (pessoa ou negocio) e sua **profissao/experiencia atual**
   (ex: barbeiro, advogado, contador, gestor de trafego, dono de clinica).
2. **O que voce ja sabe fazer bem** - 2 ou 3 habilidades ou areas de forca.
3. **Que IA / ferramentas voce ja usa** (ex: Claude, ChatGPT, n8n, automacoes) -
   ou "nenhuma ainda".
4. **Quem voce poderia atender** - tem em mente algum tipo de cliente? (pode ser "nao sei ainda").
5. **Marca** - cor principal (hex, ex `#3b5bdb`), caminho do logo (opcional) e o
   **tom de voz** (ex: proximo e simples / formal / descontraido).
6. **Moeda** (padrao BRL) e **canais que voce ja tem** (WhatsApp, Instagram, rede de
   contatos, lista de clientes antigos...).

Depois monte um JSON de respostas (veja `respostas_exemplo.json` para o formato) e
grave a configuracao rodando:

```bash
python3 scripts/primeira_vez.py --respostas /tmp/respostas_forja.json
```

Esse script grava `.forja/config.json` + `.forja/config.md`, poe `.forja/` no
`.gitignore` e **se apaga**, deixando a skill limpa. Rode uma vez so.

> Em sessao automatica (sem humano), o JSON de respostas pode vir pronto no pedido -
> escreva-o em `/tmp/respostas_forja.json` e rode o comando acima sem usar AskUserQuestion.
<!-- SETUP:END -->

## Como trabalhar

1. Garanta que a config existe (senao, faca a Primeira vez acima).
2. Leia `.forja/config.md` para saber a profissao, as forcas, a marca e o tom.
3. Conduza pelos modos abaixo. Nao precisa fazer todos de uma vez - a jornada
   natural e: **Descobrir -> Validar -> Empacotar -> Precificar -> Apresentar -> Largada**.
4. Tudo que voce gerar (oferta, preco, plano) e para o dono **revisar e usar** - a
   Forja sugere e organiza; quem decide e age e a pessoa.

### Modos (combine conforme o pedido)

**1. Descobrir** - a pessoa nao sabe o que vender.
- Entreviste com base na config (profissao + forcas + ferramentas). Faca poucas
  perguntas certeiras, uma de cada vez.
- Proponha **3 a 5 ofertas candidatas** de servico de IA que combinam com ela.
  Para cada uma diga em 1 linha: o que e, para quem, e por que ela tem vantagem.
- Ranqueie por **encaixe** (usa as forcas dela), **demanda** (alguem paga por isso)
  e **facilidade de comecar**. Recomende uma e explique o porque.
- Use o guia `references/ofertas-exemplo.md` para inspirar por profissao.

**2. Validar** - a pessoa escolheu uma ideia e quer saber se vale a pena.
- Aplique a rubrica de `references/validacao.md`: sinal de demanda real (pesquise na
  web se possivel), quem ja faz isso (concorrentes), riscos, a **vantagem injusta**
  dela, e um **veredito honesto** (segue / ajusta / troca) com o motivo.
- Seja realista, nunca um "sim" automatico. Se for fraca, diga e proponha um ajuste.

**3. Empacotar** - transformar a ideia num produto claro.
- Defina: **nome** da oferta, **promessa** em 1 frase, **para quem** (cliente ideal),
  **a transformacao** (o que muda na vida do cliente), o que **inclui**, o que
  **NAO inclui** (escopo claro evita dor de cabeca), e o **formato** (projeto unico
  ou recorrente/mensalidade). Veja `references/ofertas-exemplo.md` para o padrao.

**4. Precificar** - quanto cobrar, sem chutar.
- Leia `references/precificacao.md`. Pegue da pessoa: quanto vale a hora dela, quantas
  horas o trabalho leva, e o **valor que a oferta gera para o cliente** (estimado).
- Rode: `python3 scripts/forja.py precos --custo-hora 80 --horas 20 --valor-cliente 8000`
  (acrescente `--recorrente` para mensalidade). Saem 3 faixas (basico/intermediario/premium).
- Explique cada faixa e oriente a ancorar o cliente na do meio. Justifique pelo
  **resultado**, nunca pelas horas.

**5. Apresentar** - a pagina de oferta (one-pager) para mandar ao cliente.
- Monte um JSON com os dados empacotados + as faixas + a marca (cor/logo da config).
- Rode: `python3 scripts/forja.py oferta --spec /tmp/oferta.json --saida oferta.html`
- Sai um HTML lindo, com a marca da pessoa, que abre no navegador e vira PDF ao
  imprimir. E o que ela manda no WhatsApp/e-mail para fechar.

**6. Largada** - plano de 30 dias para o primeiro cliente.
- Monte um plano simples, semana a semana, usando os **canais que a pessoa ja tem**
  (config): rede de contatos, clientes antigos, WhatsApp, 1 conteudo. Sem depender de
  trafego pago no inicio.
- De passos concretos e pequenos (o que fazer em cada semana, com uma meta clara).
- A partir daqui, quem quiser ir fundo em prospeccao e abordagem de clientes usa a
  skill **Fisga**.

## Regras de ouro
- **Nunca invente** demanda, numero de mercado ou preco "magico". Validacao e honesta;
  preco vem do motor + valor real.
- **Comece pelo que a pessoa ja tem** - profissao, forcas, rede de contatos. A primeira
  venda quase sempre vem de quem ja conhece voce.
- **Escopo claro** - sempre diga o que NAO esta incluido. Protege a pessoa.
- **Preco e sobre valor, nao sobre esforco** - justifique pelo resultado entregue.
- A Forja **organiza e sugere**; quem decide, precifica e vende e o dono.

## Inputs / Outputs
- **Entra**: a profissao/forcas da pessoa (config) e pedidos em linguagem natural
  ("o que eu vendo com IA?", "valida essa ideia", "quanto cobro?", "faz a pagina da oferta").
- **Sai**: ofertas candidatas ranqueadas, veredito de validacao, oferta empacotada,
  3 faixas de preco, uma pagina de oferta em HTML e um plano de 30 dias.

## Dependencias
- Python 3 (biblioteca padrao apenas - sem instalar nada).
