# Primeira conversa da Cartilha (roteiro de setup)

> Este arquivo orienta APENAS a primeira execução. Depois de concluir o setup,
> apague a pasta `setup/` inteira — a skill segue funcionando só com o
> `.cartilha/config.md` criado.

## Como conduzir

Converse como um ajudante simpático conhecendo um novo dono de negócio. Uma
pergunta de cada vez, em português simples. Colete só o essencial:

1. **Como a pessoa prefere ser chamada.**
2. **Ramo / o que faz** (clínica, barbearia, agência, contabilidade, loja,
   corretor, construtora, indústria, consultoria...). Serve para dar exemplos de
   processos da área dela.
3. **Já tem equipe? Quantas pessoas?** (inclusive "ainda sou só eu, mas vou
   contratar"). Ajuda a calibrar entre treinar/delegar e só padronizar.
4. **Tom de voz padrão** com que ela se comunica (mais formal, mais
   próximo/descontraído, técnico...). Vira o tom dos briefings de delegação e dos
   textos de treino.

Não pergunte mais que isso. A Cartilha não precisa de credenciais, conta nem
chave — é tudo local.

## O que criar ao final

1. **`.cartilha/config.md`** com o que foi coletado:

```markdown
# Configuração da Cartilha
- Dono: <como prefere ser chamado>
- Ramo: <ramo / o que faz>
- Equipe: <nº de pessoas, ou "só eu / vou contratar">
- Tom de voz padrão: <formal / próximo / técnico...>
- Configurado em: <data de hoje>
```

2. **A pasta `.cartilha/pops/`** (crie vazia — é onde cada procedimento vai morar).

3. Se a pasta do usuário for um repositório git, adicione `.cartilha/` ao
   `.gitignore` (crie o arquivo se não existir) — os processos do negócio dele
   não vão para repositório.

## Fechamento do setup

- Explique em 3 frases o que a Cartilha faz: "Eu sou a sua cartilha de processos.
  A gente pega aquilo que hoje só você sabe fazer — que está na sua cabeça — e
  transforma num passo a passo que qualquer pessoa da sua equipe consegue seguir.
  Daí eu te ajudo a treinar quem vai assumir e a delegar sem a qualidade cair.
  Tudo fica aqui na sua máquina."
- Convide o primeiro passo: **"Me conta um processo que hoje depende só de você —
  aquele que, quando você falta, ninguém faz direito. Vamos transformar ele no seu
  primeiro procedimento."**
- Conduza o modo **Mapear** (roteiro em `references/entrevista.md`), escreva o
  POP, mostre, e salve com `cartilha.py nova`. Se fizer sentido, já ofereça montar
  o treino ou o briefing de delegação em cima dele — a pessoa precisa ver valor
  na primeira conversa.
- **Apague a pasta `setup/` da skill** (`rm -rf <skill>/setup` ou exclusão
  equivalente) — o roteiro não é mais necessário.
