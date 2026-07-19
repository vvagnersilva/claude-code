# Régua — Recebíveis e Cobrança no seu tom

Uma skill para **Claude Code** que organiza suas **contas a receber** e te ajuda a
**cobrar sem perder o cliente**. Você conversa em português; a Régua controla quem te
deve, quanto e há quantos dias, e te entrega a **mensagem certa, na hora certa, no seu
tom** — você só envia (WhatsApp em primeiro lugar).

> Seus dados ficam **100% no seu computador**, numa pasta `.regua/`. Nada vai para a
> internet. A Régua **nunca inventa** valor ou pagamento, e **nunca envia** nada por
> você — ela sugere, você decide e manda.

## O que ela faz
- **Controle de recebíveis:** quem está devendo, quanto, vencimento e dias de atraso.
- **Régua de cobrança:** a sequência de mensagens (lembrete antes de vencer → vencimento
  → +3 → +7 → +15 → +30 dias) no seu tom, com saída digna em cada degrau.
- **Mapa por faixa de atraso** (a vencer / 1-30 / 31-60 / 61-90 / 90+) e **painel** com
  semáforo, total a receber, vencido x em dia e inadimplência.
- **Pagamentos parciais e quitação**, extrato por cliente, e respostas prontas para as
  objeções mais comuns ("tá difícil esse mês", "já paguei", "pago semana que vem").

## Para quem é
Qualquer pessoa que **entrega um serviço e depois precisa receber**: clínicas,
barbearias, salões, agências, consultorias, contadores, corretores, instaladores,
escritórios e freelancers — por mensalidade ou por job. **Não precisa saber programar.**

## Como instalar
1. Baixe e **descompacte** o arquivo `Regua.zip`.
2. Copie a pasta `Regua` para dentro de `.claude/skills/` no seu projeto
   (ou em `~/.claude/skills/Regua` para usar em qualquer pasta).
3. Abra o **Claude Code** nesse projeto.

Estrutura final:
```
.claude/skills/Regua/
├── SKILL.md
├── README.md
├── scripts/regua.py
├── references/
│   ├── mensagens.md
│   └── objecoes.md
└── setup/SETUP.md   (some sozinho depois da 1ª configuração)
```

## Como usar (você só conversa)
**Primeira vez** — diga: **"configurar a Régua"**. Ela faz algumas perguntas (seu nome,
seu tom, prazos) e prepara tudo.

**No dia a dia**, fale naturalmente:
- "O João me deve R$ 1.500, vence dia 10."
- "Quem está me devendo?" / "Quanto tenho a receber?"
- "Quem eu cobro hoje?" → ela te dá a mensagem pronta no seu tom, você manda no WhatsApp.
- "A Maria pagou metade." / "O cliente da consultoria quitou."
- "O cliente disse que tá difícil esse mês, o que respondo?"
- "Como está minha inadimplência?"

A Régua chama o motorzinho dela por baixo dos panos — você nunca digita comando.

## Privacidade e limites
- Tudo local em `.regua/` (incluído no `.gitignore`). Nenhuma chave de API, nenhum envio externo.
- Sem juros/multa inventados — só os que **você** informar.
- **Não é cobrança jurídica.** Para protesto/negativação/ação, procure um contador/advogado.
  A Régua cuida da conversa amigável de cobrança.

## Licença
MIT. Use, adapte e compartilhe.
