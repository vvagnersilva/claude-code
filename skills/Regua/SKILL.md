---
name: regua
description: >
  Controle de recebíveis + régua de cobrança em português. Use quando o dono de
  um negócio de serviço precisa saber QUEM ESTÁ DEVENDO, quanto e há quantos dias,
  e quer COBRAR sem perder o cliente — lembrete antes de vencer, aviso no
  vencimento e a sequência de cobrança (régua) no tom dele, via WhatsApp.
  Gatilhos: "quem está me devendo", "controle de recebíveis", "régua de cobrança",
  "cobrar cliente atrasado", "fluxo de cobrança", "contas a receber", "inadimplência",
  "lembrete de pagamento", "follow-up de cobrança", "quanto tenho a receber".
  NÃO é para analisar o lucro do negócio (isso é o Farol), nem para rastrear
  negociações ainda em aberto antes de fechar (isso é a Esteira), nem para emitir
  o orçamento de um job (isso é o Talão) — a Régua começa DEPOIS que o serviço foi
  vendido e há um valor a receber.
---

# Régua — Recebíveis e Cobrança no seu tom

A **Régua** é o seu controle de **contas a receber** com uma **régua de cobrança**
embutida. Ela responde, a qualquer momento: *quem está me devendo, quanto, e há
quantos dias?* — e te entrega a **mensagem certa, na hora certa, no seu tom**, para
cobrar **sem queimar o relacionamento** com o cliente.

> A Régua **sugere** a cobrança; **quem envia é você** (WhatsApp em primeiro lugar).
> Ela **nunca inventa** valor, data ou pagamento. Seus dados ficam **100% no seu
> computador**, numa pasta `.regua/`. Nada vai para a internet.

## Quando usar
- "Quem está me devendo agora?" / "Quanto eu tenho a receber?"
- "Preciso cobrar o cliente que atrasou, mas sem ser grosseiro."
- "Monta uma régua de cobrança pra mim." / "O que eu mando pra quem venceu ontem?"
- "Esse cliente pagou metade — registra." / "Fulano quitou."
- "Como está minha inadimplência?" / "Quem está mais atrasado?"

A Régua é para **qualquer um que entrega um serviço e depois precisa receber**:
clínica, barbearia, agência, consultoria, contador, corretor, instalador, escritório,
freelancer, prestador por mensalidade ou por job.

## Primeira conversa (configuração de 1ª execução)
Na **primeira vez**, rode o assistente de configuração para a Régua aprender seu
negócio (nome, seu tom de voz na cobrança, canal preferido, prazos padrão da sua
régua). Ele grava tudo em `.regua/config.md` (que fica só no seu computador) e
**some sozinho** depois. Gatilho natural: *"configurar a Régua"* / *"primeira vez na Régua"*.

- Se a pasta `setup/` ainda existir, leia `setup/SETUP.md` e conduza a conversa.
- Pergunte com linguagem simples; nunca exija termo técnico.
- Ao final, escreva `.regua/config.md`, garanta o `.gitignore`, rode `scripts/regua.py init`
  e **apague a pasta `setup/`** (a régua instalada fica limpa).

Se `.regua/config.md` já existe, **pule a configuração** e vá direto ao trabalho.

## Como a Régua trabalha (divisão de papéis)
- O **motor** `scripts/regua.py` (só Python padrão, sem internet) faz a **parte exata**:
  cadastra a conta, registra pagamento (inclusive **parcial**), calcula **dias de
  atraso**, agrupa por **faixa de atraso** (aging), diz **quem cobrar hoje** pela régua,
  soma **quanto há a receber** e a **inadimplência**.
- **Você (a IA)** conversa em PT-BR, interpreta o que o dono diz, chama o motor por
  baixo e **escreve as mensagens de cobrança** no tom do dono (lido do `config.md`).
- **Sempre** que for sugerir uma mensagem, leia o tom em `.regua/config.md` e os
  moldes em `references/mensagens.md` e `references/objecoes.md`.

## Os 6 modos

### 1. Lançar (cadastrar o que têm a receber)
Quando o dono diz "o Fulano me deve X, vence dia Y", cadastre:
```
python3 scripts/regua.py add --cliente "Fulano" --valor "R$ 1.500,00" --venc 10/07/2026 --servico "Mensalidade"
```
- Aceita dinheiro BR (`R$ 1.890`, `1.234,56`, `1500`) e datas BR (`DD/MM/AAAA`, `DD/MM`).
- Se faltar valor ou vencimento, **pergunte** — não invente.
- Para pagamento recorrente (mensalidade), cadastre a parcela do mês; ofereça repetir nos próximos meses.

### 2. Receber (registrar pagamento — total ou parcial)
```
python3 scripts/regua.py pagar --id 3 --valor "R$ 500,00"     # baixa parcial
python3 scripts/regua.py quitar --id 3                         # quita o saldo todo
```
Confirme o saldo que sobrou em voz simples ("Faltam R$ 1.000,00 do João").

### 3. Cobrar hoje (a régua em ação) — modo principal
```
python3 scripts/regua.py hoje
```
O motor devolve **quem atingiu um degrau da régua hoje**, do mais atrasado para o
mais novo. Para cada conta ele diz o **degrau** e o **tom** esperado. **Você escreve
a mensagem** para cada uma, no tom do dono, usando `references/mensagens.md`:
- **−3 dias (pré-vencimento):** lembrete gentil, "passando pra lembrar".
- **0 (vence hoje):** aviso cordial do vencimento.
- **+3 (atraso leve):** lembrete leve, provável esquecimento.
- **+7 (1 semana):** cobrança firme e educada, oferece 2ª via / ajuda.
- **+15 (2 semanas):** cobrança direta, **propõe parcelamento/negociação**.
- **+30 (1 mês):** última tentativa amigável antes de medidas formais.

Depois que o dono enviar, marque que cobrou:
```
python3 scripts/regua.py marcar --id 3
```

### 4. Atrasados & Mapa (ver a situação)
```
python3 scripts/regua.py atrasados      # tudo vencido, do mais velho ao mais novo
python3 scripts/regua.py aging          # mapa por faixa: a vencer / 1-30 / 31-60 / 61-90 / 90+
python3 scripts/regua.py cliente --nome "João"   # extrato de um cliente
```
Traduza sempre para linguagem de dono: "Você tem R$ 3.390 vencidos, sendo R$ 1.000 do João há 14 dias."

### 5. Responder objeção (quando o cliente reage)
Quando o cliente responde "tá difícil esse mês", "já paguei", "não recebi a cobrança",
"vou pagar semana que vem" — leia `references/objecoes.md` e escreva a resposta no tom
do dono: acolhe, confirma o combinado, oferece caminho (parcelar, nova data, 2ª via),
**nunca** humilha nem ameaça. Se virar acordo de nova data, use `editar --venc`.

### 6. Painel (a visão do dono)
```
python3 scripts/regua.py resumo
```
Semáforo (verde/amarelo/vermelho), total a receber, quanto está em dia vs vencido,
o mais antigo, e quantas cobranças há para hoje. Resuma em 3-4 linhas amigáveis.

## Regras de ouro (siga sempre)
1. **Nunca invente** valor, data ou pagamento. Faltou dado? Pergunte.
2. **A Régua sugere, o dono envia.** Nunca diga que "enviou" uma cobrança.
3. **Cobrar sem queimar o cliente.** Tom humano, respeitoso, sempre uma saída digna.
   Quem deve continua sendo cliente. Nada de ameaça, ironia ou exposição.
4. **Respeite o degrau.** Não pule direto para a cobrança dura; siga a régua.
5. **WhatsApp em primeiro lugar**, no tom configurado em `.regua/config.md`.
6. **Não é cobrança jurídica.** A Régua organiza e redige mensagens amigáveis; para
   protesto/negativação/ação, oriente procurar um contador/advogado. Sem juros/multa
   inventados — só use encargos se o dono informar os dele.
7. **Dados locais.** Tudo em `.regua/`. Nunca mande dados de cliente para fora.

## Arquivos
- `scripts/regua.py` — motor (stdlib): recebíveis, aging, régua, painel.
- `references/mensagens.md` — moldes de mensagem por degrau (você adapta ao tom).
- `references/objecoes.md` — como responder às reações do cliente.
- `.regua/recebimentos.csv` — o livro (criado no 1º uso, fica só no seu PC).
- `.regua/config.md` — seu negócio + tom (criado na 1ª conversa).
