# 📬 Carteiro — sua caixa de entrada sob controle

Uma skill de Claude Code em português que **tri­a suas mensagens, rascunha as
respostas no seu tom e não deixa ninguém sem retorno**. Para quem se afoga em
e-mail e mensagem e perde tempo (ou clientes) decidindo o que responder primeiro.

O Carteiro **não conecta na sua conta de e-mail**. Você **cola** as mensagens (ou
aponta um arquivo com elas) e ele trabalha em cima disso — tudo local, privado,
sem senha nenhuma.

## O que ele faz (6 modos)
1. **Triar** — cole a pilha de mensagens; ele separa em 🔴 responder hoje / 🟡 pode
   esperar / 🟢 só ler / ⛔ ignorar, com o resumo do que cada um quer.
2. **Responder** — rascunha cada resposta no seu tom, pronta pra você revisar e
   enviar. Nunca inventa: marca `[PREENCHER]` no que falta.
3. **Pendências (nada cai)** — registra quem está esperando sua resposta e conta os
   dias; avisa quem está há muito tempo sem retorno.
4. **Modelos** — guarda aquelas respostas que você repete toda semana, com
   variáveis pra personalizar.
5. **Limpar / Regras** — ajuda a zerar o ruído e criar regras simples pra caixa
   parar de encher.
6. **Painel** — a caixa num olhar: o que você deve, o que aguarda, quem está
   esperando há mais tempo.

## Instalar
1. Descompacte a pasta `Carteiro`.
2. Copie para a pasta de skills do seu Claude Code:
   - no projeto: `.claude/skills/Carteiro/`
   - ou global: `~/.claude/skills/Carteiro/`
3. Abra o Claude Code e diga algo como **"minha caixa de entrada está um caos, me
   ajuda a triar"**. Na primeira vez ele faz 5 perguntinhas rápidas e já começa.

## Requisitos
- Claude Code.
- Python 3 (já vem no Mac/Linux; no Windows, instale de python.org marcando "Add
  Python to PATH"). Nenhuma biblioteca extra — só o Python padrão.

## Privacidade
Tudo fica em `.carteiro/` na raiz do seu projeto: seu perfil, a fila de pendências
e seus modelos. Nada sai da sua máquina, nenhuma senha é pedida. Se usa Git, o
setup adiciona `.carteiro/` ao `.gitignore` pra manter tudo privado.

## Regras de ouro
- Nunca inventa um dado, preço ou data — marca `[PREENCHER]`.
- Sugere; **quem envia é você**.
- Seus dados são 100% locais.

## Licença
MIT — veja `LICENSE`. Feito para a comunidade **Maestros da IA**.
