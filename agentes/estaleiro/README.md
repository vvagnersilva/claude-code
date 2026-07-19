# ⚓ Estaleiro — sua tripulação de engenharia no Claude Code

O **Estaleiro** é um time de 5 subagentes do Claude Code que trabalham como um estaleiro de verdade: cada tripulante tem uma função, e juntos eles planejam, constroem, testam, revisam e blindam o seu código — com contexto isolado por função, do jeito que dá mais qualidade.

Feito para quem **desenvolve software** e quer parar de pedir tudo num prompt só, ganhando um fluxo de trabalho com papéis separados.

## A tripulação

| Tripulante | Função | Quando entra |
|-----------|--------|--------------|
| 🧭 **Arquiteto** | Planeja antes de codar: mapeia arquivos, passos e trade-offs | "planeje", "como abordar", "antes de codar" |
| 🔨 **Construtor** | Implementa o código seguindo as convenções do projeto | "implemente", "code isso", "aplique o plano" |
| 🧪 **Testes** | Escreve/roda testes do que mudou, caminho feliz + bordas | "escreva os testes", "rode a suíte", "cubra com teste" |
| 🔍 **Revisor** | Revisa o diff antes do commit: correção, regressão, estilo | "revise", "code review", "antes de commitar" |
| 🛡️ **Sentinela** | Revisão de segurança: segredos, injection, OWASP, authz | "revisão de segurança", "isso é seguro", "antes do deploy" |

Cada um roda como um **subagente** (contexto próprio), então o trabalho de um não polui o do outro. Você conversa naturalmente com o Claude e a tripulação certa entra em cena — ou você chama pelo nome.

## Instalação

1. Descompacte a pasta `estaleiro/`.
2. Copie os agentes para o seu projeto (ou para o seu Claude Code global):
   - **Por projeto:** copie `.claude/agents/` para a raiz do seu projeto.
   - **Global (todos os projetos):** copie os arquivos de `.claude/agents/` para `~/.claude/agents/`.
3. Abra o Claude Code na raiz do projeto e rode o setup (recomendado):

   > **"Rode o setup do Estaleiro."**

   Ele pergunta as convenções do seu projeto (linguagem, comandos de teste/lint, padrões, zona proibida), grava em `.estaleiro/config.md` (ignorado pelo git) e remove sozinho os arquivos de instalação.

> Sem o setup também funciona — cada tripulante detecta a stack lendo os manifests do projeto. O setup só deixa tudo mais preciso.

## Fluxo recomendado (do plano ao deploy)

1. **Planeje** → *"Arquiteto, planeje como adicionar X."*
2. **Construa** → *"Construtor, implemente o plano."*
3. **Teste** → *"Testes, cubra o que mudou e rode a suíte."*
4. **Revise** → *"Revisor, olha o diff antes de eu commitar."*
5. **Blinde** → *"Sentinela, faça uma revisão de segurança."*

Você não precisa seguir tudo sempre — chame só quem o trabalho pede.

## Requisitos
- **Claude Code** instalado.
- Um projeto de código (qualquer linguagem). Os agentes se adaptam à sua stack.
- Nenhuma chave de API. O Estaleiro não precisa de credenciais para funcionar.

## Privacidade & segurança
- O `.estaleiro/config.md` guarda só convenções do seu projeto e fica **fora do git**.
- **Nunca** cole segredos (chaves, senhas) no config — os agentes não precisam disso.
- O Sentinela atua só em **defesa**: encontra e ajuda a fechar brechas no seu próprio código.

## Licença
MIT — use, modifique e distribua à vontade.

---
*Feito com ⚓ para a comunidade. Bons ventos e código limpo.*
