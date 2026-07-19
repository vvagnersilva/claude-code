# 🎣 Fisga — encontre e abra conversa com novos clientes

A **Fisga** é uma skill do Claude Code que cuida da parte mais difícil de vender um serviço:
**achar o cliente certo e abrir a conversa do jeito certo.** Ela pesquisa o prospect, descobre
o gancho real (por que ele precisaria de você *agora*) e escreve a mensagem de primeiro contato
que soa humana, específica e impossível de ignorar — sem virar spam.

Feita para **prestadores de serviço, consultores, agências e freelancers** que sabem entregar,
mas travam na hora de **conseguir cliente**. WhatsApp-first, em português, para quem não é técnico.

## O que ela faz (6 modos)

| Modo | Pra quê |
|------|---------|
| 🎯 **Mira** | Define seu cliente ideal — pra você parar de atirar pra todo lado |
| 🔎 **Investigar** | Pesquisa um prospect e monta um dossiê: o que faz, sinais de compra, dor, quem decide, gancho |
| ⚖️ **Qualificar** | Diz se o lead é 🔥 quente, 🙂 morno ou ❄️ frio — pra você gastar energia onde converte |
| ✍️ **Abordar** | Escreve a 1ª mensagem personalizada + a sequência de follow-up, no seu tom e no canal certo |
| 💬 **Responder** | Te dá a resposta certa pra cada objeção ("tá caro", "não tenho tempo", "já tenho alguém") |
| 📞 **Call** | Monta o roteiro da call de diagnóstico e te entrega o lead pronto pra proposta |

A Fisga **não** dispara mensagem em massa nem usa lista comprada. Toda abordagem é 1-a-1,
pesquisada e personalizada — e respeita sempre quem disse "não".

## Instalação

1. Descompacte a pasta `Fisga/`.
2. Copie para a pasta de skills do seu Claude Code:
   - **Por projeto:** copie a pasta `Fisga/` para `.claude/skills/fisga/` na raiz do seu projeto.
   - **Global (todos os projetos):** copie para `~/.claude/skills/fisga/`.
3. Abra o Claude Code e rode o setup (recomendado):

   > **"Rode o setup da Fisga."**

   Ele pergunta quem você é e o que você vende, grava em `.fisga/config.md` (ignorado pelo git) e
   remove sozinho os arquivos de instalação. Veja `SETUP.md`.

> Sem o setup também funciona — a Fisga só vai te perguntar nome, oferta e canal na hora.

## Como usar (exemplos do dia a dia)

- *"Pesquisa essa clínica pra mim: @nomedaclinica"* → dossiê com o gancho.
- *"Esse lead vale a pena?"* → nota quente/morno/frio.
- *"Escreve a abordagem no WhatsApp pra esse cliente."* → mensagem pronta + follow-up.
- *"Ele falou que tá caro, como respondo?"* → resposta no seu tom.
- *"Vou ter uma call amanhã, monta o roteiro."* → roteiro de diagnóstico.

## Onde a Fisga começa e termina

A Fisga é a **frente do funil**: ela encontra o prospect e abre a conversa. Quando o cliente
respondeu e topou conversar, o próximo passo (diagnóstico aprofundado + proposta comercial) é
outro trabalho. Se você tiver a skill/agentes **Bússola**, é ali que a coisa continua.

## Privacidade
Seu perfil e seus dados de prospects ficam em arquivos locais (`.fisga/`), na sua máquina,
ignorados pelo git. Nenhuma credencial sua sai do seu computador. Você usa suas próprias
ferramentas — a Fisga não exige nenhuma API paga.

---
Licença MIT. Feita pela **Maestria Academy** para a comunidade.
