# Âncora — Retenção de clientes recorrentes (Customer Success de bolso)

**Conquistar cliente novo custa de 5 a 7 vezes mais do que manter um que você já tem.** A Âncora é
o assistente que cuida da sua **carteira de clientes recorrentes** para ninguém cancelar por
descuido: mede a saúde de cada um, avisa quem está em risco, quem renova em breve, quem já pode
crescer com você — e não deixa ninguém ser esquecido.

Feita para **donos de negócio de serviço, agências, consultores, clínicas e freelancers** com
mensalidade/contrato — em português, sem jargão. Você **conversa**; a Âncora organiza e calcula.

## O que ela faz (7 modos)
1. **Carteira** — cadastra seus clientes fixos e mostra o retrato: quantos são, o MRR (receita
   recorrente/mês) e quem renova primeiro.
2. **Saúde** — dá uma **nota 0–100 e um semáforo 🟢🟡🔴** para cada cliente, a partir de 5 sinais
   simples (pagamento, engajamento, satisfação, resultado, relacionamento) — e explica o porquê.
3. **Renovação** — o radar: quem renova nos próximos dias, ordenado por **risco × valor**, com a
   receita em risco somada.
4. **Salvar** — o plano de resgate de quem está caindo, incluindo a conta fria **"vale a pena
   salvar?"** (retorno esperado × custo) e como **recuperar quem já cancelou**.
5. **Crescer** — oportunidades de vender mais para o mesmo cliente — **só em cliente saudável**.
6. **Toque** — quem está há muito tempo sem contato + o roteiro da reunião de resultado.
7. **Painel** — a foto da carteira: MRR, semáforos, receita em risco, churn do mês, expansão em
   aberto e as próximas ações.

## Como instalar
1. Baixe e descompacte esta pasta.
2. Copie a pasta **`Âncora`** para dentro de `.claude/skills/` no seu projeto
   (ou em `~/.claude/skills/` para usar em qualquer lugar). O caminho final fica assim:
   `.claude/skills/Âncora/SKILL.md`.
3. Abra o Claude Code nesse projeto.

## Como usar
- **Primeira conversa:** diga algo como *"quero organizar minha carteira de clientes"*. A Âncora
  faz um setup rápido (nome, negócio, ciclo de cobrança, canal, tom de voz), grava tudo numa pasta
  local `.ancora/` e **se limpa sozinha**.
- **No dia a dia:** fale naturalmente — *"como está o cliente Sorriso?"*, *"quem renova esse mês?"*,
  *"esse cliente quer cancelar, o que faço?"*, *"me mostra o painel da carteira"*. A Âncora escolhe
  o modo certo, faz as contas no motor e devolve em português claro.

## O que esperar
- **Nunca inventa** número, resultado ou sinal — sempre pergunta.
- **As contas são exatas** — nota de saúde, radar, EV do resgate e painel saem de um motor em
  Python (só biblioteca padrão, sem internet, sem instalar nada).
- **Seus dados ficam só no seu computador**, na pasta `.ancora/` (que não vai para o Git).
- **Ela sugere as mensagens; quem envia é você** — WhatsApp na frente.
- **Honesta:** se um cliente não vale mais o resgate, ela diz — em vez de te fazer queimar desconto.

## Requisitos
- Claude Code instalado.
- Python 3 (já vem no macOS e na maioria dos Linux) — a Âncora usa só a biblioteca padrão.

---
Feito com carinho pela **Maestria Academy** para a comunidade **Maestros da IA**. Licença MIT.
