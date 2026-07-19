# Fisco — Organizador Fiscal e Guia da Reforma Tributária

**O seu braço direito para impostos, em português de gente.** O Fisco tira o medo de
errar com o fisco: ele **explica** o que confunde (regime, DAS, obrigação, nota), monta o
**calendário** das suas obrigações e avisa o que vence, ajuda a **organizar** o que você
manda para o contador todo mês, compara regimes de forma **direcional** (Simples x
Presumido, Fator R) e explica a **Reforma Tributária** (IBS, CBS) e o que ela muda para o
seu negócio.

> O Fisco **não substitui o seu contador** e **nunca inventa** alíquota ou valor de imposto.
> Ele organiza, explica e prepara — a conta e a decisão oficial são do contador.
> **Isto não é parecer contábil.**

## Para quem é

Dono de pequeno negócio de serviço no Brasil (clínica, barbearia, agência, escritório,
consultoria, prestador, loja) que paga imposto e se perde nas regras — **e também** o
contador/consultor tributário que quer uma ferramenta para organizar prazos, comparar
regimes e explicar a Reforma para os clientes.

## Como instalar

1. Descompacte o arquivo `Fisco.zip`.
2. Copie a pasta `Fisco` para dentro de `.claude/skills/` no seu projeto (ou em
   `~/.claude/skills/` para deixar disponível em qualquer projeto). O caminho final fica:
   `.claude/skills/Fisco/`.
3. Abra o Claude Code na pasta do seu projeto. Pronto — a skill é reconhecida sozinha.

## Como usar (você só conversa, em português)

Na **primeira vez**, diga algo como *"configurar o Fisco"*. Ele faz uma conversa curta
(nome do negócio, atividade, regime, se tem funcionário), grava tudo numa pasta local
`.fisco/` e some com o assistente de configuração.

Depois, é só falar naturalmente:
- "Me explica como funciona o meu Simples."
- "Quando vence o meu DAS? Monta meu calendário fiscal."
- "O que eu preciso mandar pro contador esse mês?"
- "Simples ou Presumido, qual tende a valer mais a pena pra mim?"
- "O que essa Reforma Tributária muda pro meu negócio?"

Por baixo, o Claude roda um pequeno motor em Python (`scripts/fisco.py`, só biblioteca
padrão — sem internet, sem chave de API, sem senha de banco). Você não precisa digitar
nenhum comando: só conversa.

## O que ele faz (6 modos)

1. **Entender** — explica regime, DAS, obrigação acessória, Fator R, nota — em linguagem simples.
2. **Reforma** — o que muda com IBS/CBS e o que preparar (linha do tempo 2026–2033).
3. **Calendário** — cadastra suas obrigações e avisa o que está 🔴 vencido / 🟠 hoje / 🟡 perto.
4. **Organizar** — checklist do que mandar pro contador todo mês, sem esquecer nada.
5. **Regime** — Fator R + comparação direcional Simples x Presumido (com as alíquotas que você/o contador informam).
6. **Perguntar** — tira dúvida fiscal do dia a dia, sem inventar; o que depende do caso vai pro contador.

## O que esperar (as regras de ouro)

- **Nunca inventa** alíquota, valor de imposto ou prazo legal — na dúvida, pergunta ou manda confirmar.
- **Não é parecer contábil** — toda saída lembra de confirmar com o contador.
- **Explica em português de gente** — sem juridiquês.
- **A Reforma com datas reais**, mas sempre "confirme a regra vigente".
- **Sugere, você decide/envia.**
- **Dados 100% locais** em `.fisco/`, nada vai para a internet, nenhuma senha é pedida.

## Privacidade

Tudo o que você conversa e cadastra fica em `.fisco/` **no seu computador**. A skill não
manda nada para a internet e não pede nenhuma senha (nem de banco, nem da Receita). A pasta
`.fisco/` já vem no `.gitignore` para não ir parar em nenhum repositório.

## Licença

MIT — veja `LICENSE`. Use, adapte e compartilhe à vontade.
