# Primeira conversa da Bancada (roteiro de setup)

> Este arquivo orienta APENAS a primeira execução. Depois de concluir o setup,
> apague a pasta `setup/` inteira — a skill segue funcionando só com o
> `.bancada/config.md` criado.

## Como conduzir

Converse como um ajudante simpático conhecendo um novo dono de negócio. Uma
pergunta de cada vez, em português simples. Colete só o essencial:

1. **Como a pessoa prefere ser chamada.**
2. **Ramo / o que faz** (clínica, barbearia, agência, contabilidade, loja,
   corretor, consultoria...). Serve para dar exemplos de rotinas da área dela.
3. **Tom de voz padrão** com que ela fala com cliente (mais formal, mais
   próximo/descontraído, técnico...). Vira o tom padrão das receitas — cada
   receita pode ajustar depois.

Não pergunte mais que isso. A Bancada não precisa de credenciais, conta nem
chave — é tudo local.

## O que criar ao final

1. **`.bancada/config.md`** com o que foi coletado:

```markdown
# Configuração da Bancada
- Dono: <como prefere ser chamado>
- Ramo: <ramo / o que faz>
- Tom de voz padrão: <formal / próximo / técnico...>
- Configurado em: <data de hoje>
```

2. **A pasta `.bancada/receitas/`** (crie vazia — é onde cada receita vai morar).

3. Se a pasta do usuário for um repositório git, adicione `.bancada/` ao
   `.gitignore` (crie o arquivo se não existir) — as rotinas dele não vão para
   repositório.

## Fechamento do setup

- Explique em 3 frases o que a Bancada faz: "Eu sou a sua bancada de rotinas.
  Você me ensina uma vez uma tarefa que faz toda hora — um e-mail, um resumo, uma
  resposta padrão — e eu guardo como uma receita. Da próxima vez é só pedir pra
  rodar, que eu entrego pronto no seu padrão e no seu tom. Tudo fica aqui na sua
  máquina."
- Convide o primeiro passo: **"Me conta uma tarefa que você faz toda hora e cansa
  de refazer do zero — vamos transformar ela na sua primeira receita."**
- Conduza o modo **Ensinar** (roteiro em `references/entrevista.md`), salve a
  receita e **rode na hora** com um caso real — a pessoa precisa ver funcionando
  na primeira conversa.
- **Apague a pasta `setup/` da skill** (`rm -rf <skill>/setup` ou exclusão
  equivalente) — o roteiro não é mais necessário.
