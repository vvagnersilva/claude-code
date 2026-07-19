# Como extrair: do texto solto ao registro limpo

A entrada e sempre TEXTO que o dono cola ou aponta: anotacoes soltas, bullets, ou uma
transcricao que ele ja tem. Pode vir baguncado, abreviado, com nome de gente no meio.
Seu trabalho e organizar **somente o que esta ali** em quatro blocos. Nunca complete
lacunas com suposicao.

## Regra mestra (inegociavel)
> So reflita o que esta no texto. Seja objetivo. Nao adicione opiniao, diagnostico,
> valor ou prazo que o dono nao escreveu. O que faltar fica marcado como "nao definido".

## Os quatro blocos

**1. Resumo** (2–5 linhas)
O que aconteceu no atendimento, em linguagem simples. Sem jargao novo, sem floreio.

**2. Decisoes**
O que ficou *decidido* (nao o que foi *cogitado*). Uma por linha. Se algo ficou em aberto,
liste em "Pontos de atencao", nao aqui.

**3. Pendencias** (o que vira tarefa)
Para cada acao combinada, extraia tres campos — e so preencha os que existem no texto:
- **O que** — a tarefa (verbo no inicio: "Enviar orcamento", "Confirmar exame").
- **Quem** — responsavel: o dono ("Eu") ou o cliente. Se nao der pra saber, deixe vazio.
- **Prazo** — data DD/MM/AAAA. "semana que vem", "ate sexta" -> peca a data exata ao dono
  antes de gravar; nao chute.

**4. Pontos de atencao**
Observacoes que ajudam no proximo encontro: preferencias ("prefere ser chamado de Dr."),
contexto pessoal relevante, restricoes, o que ficou *sem* definir.

## Exemplo

Anotacao colada pelo dono:
> "consulta joao, dor no joelho direito ha 3 semanas, pediu pra ver se da pra fazer a noite
> pq trabalha. falei q mando os horarios. ele vai mandar o exame antigo. retorno em 15 dias"

Vira:
```
Cliente: Joao  |  Data: <perguntar/confirmar>

Resumo
Joao relatou dor no joelho direito ha 3 semanas. Prefere atendimento no periodo da noite
porque trabalha durante o dia. Retorno previsto em 15 dias.

Decisoes
- Atendimento sera no periodo da noite.
- Retorno em 15 dias.

Pendencias
- [Eu] Enviar os horarios disponiveis a noite — prazo: <perguntar>
- [Joao] Enviar o exame antigo — prazo: nao definido

Pontos de atencao
- Trabalha de dia; so consegue a noite.
- "15 dias" e "retorno": confirmar a data exata com o dono antes de gravar.
```

Depois de o dono confirmar/ajustar, grave com os comandos do SKILL.md (registrar + pendencia).
Nunca grave antes do "ok" dele.
