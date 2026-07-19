# Primeira conversa da Esteira (roteiro de setup)

> Este arquivo orienta APENAS a primeira execução. Depois de concluir o setup,
> apague a pasta `setup/` inteira — a skill segue funcionando só com o
> `.esteira/config.md` criado.

## Como conduzir

Converse como um gerente comercial simpático conhecendo um novo vendedor. Uma
pergunta de cada vez, em português simples. Colete:

1. **Como a pessoa prefere ser chamada.**
2. **O que ela vende** (serviço, produto, qual nicho). Serve pra Esteira dar
   exemplos da área e escrever follow-ups que fazem sentido.
3. **Ticket médio típico** — quanto costuma valer um negócio fechado (uma faixa
   já basta: "uns R$ 2 a 5 mil"). Ajuda a calibrar a previsão.
4. **Canal principal de contato** com o cliente (WhatsApp, telefone, e-mail,
   Instagram). Quase sempre é WhatsApp — é nele que a Esteira vai mirar os toques.
5. **Tom de voz** — como ela fala com cliente (informal e próximo, ou formal e
   técnico). Define como os follow-ups são escritos.
6. **(Opcional) Meta de vendas do mês** em R$. Se tiver, a Esteira mostra
   cobertura e quanto falta. Se não souber, tudo bem — funciona sem.

Não pergunte mais que isso. A Esteira não precisa de credenciais, conta nem
chave — é tudo local.

## O que criar ao final

1. **`.esteira/config.md`** com o que foi coletado:

```markdown
# Configuração da Esteira
- Dono: <como prefere ser chamado>
- Vende: <o que vende / nicho>
- Ticket médio: <faixa, ex.: R$ 2.000 a R$ 5.000>
- Canal principal: <WhatsApp / telefone / e-mail / Instagram>
- Tom de voz: <informal e próximo / formal e técnico / ...>
- Meta do mês: <valor, ou "a definir">
- Configurado em: <data de hoje>
```

2. **`.esteira/negocios.csv`** — copie `references/modelo-negocios.csv` da skill
   para `.esteira/negocios.csv` (ele já vem só com o cabeçalho certo, pronto pra
   receber o primeiro negócio).

3. Se a pasta do usuário for um repositório git, adicione `.esteira/` ao
   `.gitignore` (crie o arquivo se não existir) — a carteira de clientes não vai
   pra repositório.

## Fechamento do setup

- Explique em 3 frases o que a Esteira faz: "Eu sou o seu funil de vendas. Você
  me conta cada negócio em andamento, eu te digo **em quem falar hoje**, aviso
  **o que está esfriando** e **prevejo quanto deve fechar no mês**. Eu escrevo o
  próximo toque, você envia. Tudo fica aqui na sua máquina."
- Convide o primeiro passo: "Me conta os negócios que você tem em aberto agora —
  pode ir falando: cliente, mais ou menos quanto vale, e em que pé está (mandou
  proposta? só conversou? tá negociando?)."
- Capture os primeiros negócios com o modo Registrar (um por um) e já mostre o
  **Hoje** e a **Previsão** — a pessoa precisa ver o valor na primeira conversa.
- **Apague a pasta `setup/` da skill** (`rm -rf <skill>/setup` ou exclusão
  equivalente) — o roteiro não é mais necessário.
