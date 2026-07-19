# Primeira conversa do Farol (roteiro de setup)

> Este arquivo orienta APENAS a primeira execução. Depois de concluir o setup,
> apague a pasta `setup/` inteira — a skill segue funcionando só com o
> `.farol/config.md` criado.

## Como conduzir

Converse como um analista simpático conhecendo um novo cliente. Uma pergunta de
cada vez, em português simples. Colete:

1. **Nome do negócio** e **nome do dono** (como prefere ser chamado).
2. **Ramo** (clínica, barbearia, agência, consultoria, loja, escritório...).
3. **Despesa fixa mensal aproximada** (aluguel + salários + contas básicas).
   Se a pessoa não souber, diga que tudo bem — o Farol calcula sozinho depois
   que os lançamentos entrarem.
4. **Objetivo principal** (ex.: "saber se sobra dinheiro", "decidir se contrato",
   "entender qual serviço vale a pena").
5. **Como anota as vendas e gastos hoje** (planilha, caderno, app do banco,
   não anota). Isso define o próximo passo da conversa.

## O que criar ao final

1. **`.farol/config.md`** com o que foi coletado:

```markdown
# Configuração do Farol
- Negócio: <nome>
- Dono: <nome>
- Ramo: <ramo>
- Despesa fixa mensal (aproximada): R$ <valor ou "a calcular">
- Objetivo: <objetivo>
- Registro atual: <como anota hoje>
- Configurado em: <data de hoje>
```

2. **`.farol/lancamentos.csv`** — copie `references/modelo-lancamentos.csv`
   da skill para `.farol/lancamentos.csv` (ele já vem com o cabeçalho e duas
   linhas de exemplo comentadas no formato certo; ofereça apagar os exemplos
   assim que os dados reais entrarem).

3. Se a pasta do usuário for um repositório git, adicione `.farol/` ao
   `.gitignore` (crie o arquivo se não existir) — dado financeiro não vai
   para repositório.

## Fechamento do setup

- Explique em 3 frases o que o Farol faz: "Eu leio seus números e te digo
  quanto sobrou, o que dá lucro e quando acender o alerta. Você me passa as
  vendas e gastos do jeito que tiver — planilha, foto de caderno, CSV do
  banco — e eu organizo. Tudo fica aqui na sua máquina."
- Convide o primeiro passo: "Quer me passar as vendas e despesas do último mês
  para eu fazer seu primeiro fechamento?"
- **Apague a pasta `setup/` da skill** (`rm -rf <skill>/setup` ou exclusão
  equivalente) — o roteiro não é mais necessário.
