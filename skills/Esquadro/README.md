# Esquadro — auditoria & conformidade, no seu padrão

O **Esquadro** é o instrumento que confere se a realidade está **"no esquadro"** — dentro
da norma, da regra, do padrão. É um auditor de bolso, em português, que funciona dentro do
**Claude Code**: você conversa, ele monta o checklist da norma, conduz a auditoria item a
item, calcula o índice de conformidade, registra as não-conformidades com gravidade e
causa-raiz, monta o plano de ação 5W2H com prazo e responsável, acompanha o conserto e
emite o relatório de auditoria.

Feito para quem trabalha com **norma, risco e conformidade**: técnicos e gestores de
**SST/SSMA** (NRs), **qualidade** (ISO 9001), **compliance/auditoria/governança**,
**segurança da informação** (LGPD, ISO 27001) — e também donos de negócio que precisam
estar em dia com **fiscalização** (vigilância sanitária, bombeiros, boas práticas).

## O que ele faz (6 modos)
1. **Checklist** — monta a régua da norma (itens de verificação, obrigatórios e critério).
2. **Auditar** — confere item a item (conforme / não conforme / parcial / não se aplica) e
   calcula o índice de conformidade.
3. **Não-conformidade** — classifica a gravidade (🔴 crítica / 🟡 maior / 🟢 menor / 🔵
   observação) e encontra a causa-raiz (5 porquês).
4. **Plano de ação 5W2H** — o quê, por quê, quem, quando, onde, como, quanto, com prazo.
5. **Acompanhar (PDCA)** — andamento das ações, prazos atrasados, eficácia, painel geral.
6. **Relatório** — o documento da auditoria, em texto ou HTML com a sua marca (vira PDF).

## Princípios
- **Nunca inventa** item de norma, evidência, data ou gravidade — pergunta ou marca
  [CONFIRMAR].
- **Sempre mostra a evidência** e também o que está conforme.
- **Toda NC tem causa-raiz; toda ação tem prazo e responsável.**
- **Não é laudo nem certificação oficial** — para risco grave ou exigência legal, oriente o
  responsável técnico.
- **Seus dados ficam 100% no seu computador**, na pasta `.esquadro/`. Nada vai para a
  internet, nenhuma chave de API é necessária.

## Como instalar
1. Descompacte a pasta **`Esquadro`**.
2. Copie-a para a pasta de skills do seu projeto: `.claude/skills/Esquadro`
   (ou para `~/.claude/skills/Esquadro` para usar em qualquer projeto).
3. Abra o Claude Code nesse projeto.

## Como usar
Na primeira vez, é só dizer que quer usar o Esquadro — ele faz uma configuração rápida (seu
nome, o que você audita, a marca do relatório) e fica pronto. Depois, fale naturalmente:

- "Monta um checklist da NR-35 e vamos auditar o trabalho em altura."
- "Vou passar pela vigilância sanitária — me prepara um checklist."
- "Registra essa não-conformidade: a saída de emergência estava trancada."
- "Faz o plano de ação 5W2H pras não-conformidades."
- "Quais ações estão atrasadas?" / "Gera o relatório dessa auditoria com a minha marca."

Você nunca digita comando: o Esquadro traduz a sua conversa para o motor por baixo.

## Requisitos
- **Claude Code**
- **Python 3** (só a biblioteca padrão — nada para instalar)

## Privacidade
Tudo é local. A pasta `.esquadro/` (configuração, checklists, auditorias, não-conformidades
e plano de ação) nunca deve ir para o controle de versão — já vem no `.gitignore`.

---
Licença MIT — veja `LICENSE`.
