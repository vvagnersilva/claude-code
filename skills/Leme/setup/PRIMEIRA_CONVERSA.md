# Primeira conversa do Leme (roteiro de setup)

> Este arquivo orienta APENAS a primeira execução. Depois de concluir o setup,
> apague a pasta `setup/` inteira — a skill segue funcionando só com o
> `.leme/config.md` criado.

## Como conduzir

Converse como um assistente pessoal simpático conhecendo um novo chefe. Uma
pergunta de cada vez, em português simples. Colete:

1. **Como a pessoa prefere ser chamada.**
2. **Ramo / o que faz** (clínica, barbearia, agência, consultoria, loja,
   corretor, contador...). Serve para o Leme dar exemplos da área dela.
3. **Como ela organiza as tarefas hoje** (na cabeça, no caderno, num app, em
   bilhetinhos, não organiza). Isso define o tom da próxima conversa.
4. **(Opcional) Os "projetos"/áreas que ela usa** para agrupar tarefas — ex.:
   Comercial, Financeiro, Pessoal, Equipe. Se não souber, tudo bem: o Leme
   funciona sem isso e os projetos vão surgindo no uso.

Não pergunte mais que isso. O Leme não precisa de credenciais, conta nem chave —
é tudo local.

## O que criar ao final

1. **`.leme/config.md`** com o que foi coletado:

```markdown
# Configuração do Leme
- Dono: <como prefere ser chamado>
- Ramo: <ramo / o que faz>
- Organiza hoje: <na cabeça / caderno / app / não organiza>
- Projetos/áreas: <lista, ou "a definir">
- Configurado em: <data de hoje>
```

2. **`.leme/tarefas.csv`** — copie `references/modelo-tarefas.csv` da skill para
   `.leme/tarefas.csv` (ele já vem só com o cabeçalho certo, pronto para receber
   a primeira tarefa).

3. Se a pasta do usuário for um repositório git, adicione `.leme/` ao
   `.gitignore` (crie o arquivo se não existir) — a lista pessoal não vai para
   repositório.

## Fechamento do setup

- Explique em 3 frases o que o Leme faz: "Eu sou o seu assistente de tarefas.
  Você me joga tudo que está na cabeça, eu te digo as 3 coisas que importam
  hoje e por quê, e não deixo nada cair. Uma vez por semana a gente revisa
  junto. Tudo fica aqui na sua máquina."
- Convide o primeiro passo: "Me conta tudo que você precisa fazer essa semana —
  pode jogar tudo de uma vez que eu organizo."
- Capture as primeiras tarefas com o modo Capturar (uma por uma) e já mostre o
  **Hoje** com as 3 escolhidas — a pessoa precisa ver o valor na primeira conversa.
- **Apague a pasta `setup/` da skill** (`rm -rf <skill>/setup` ou exclusão
  equivalente) — o roteiro não é mais necessário.
