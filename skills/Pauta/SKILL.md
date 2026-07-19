---
name: pauta
description: >-
  Agenda inteligente para negocios de servico (clinicas, barbearias, saloes,
  consultorios, restaurantes, consultorias). Use quando o usuario quiser
  organizar agendamentos, sugerir horarios livres, confirmar consultas do dia
  seguinte, reduzir faltas (no-show), remarcar ou cancelar, lembrar clientes de
  voltar (retorno) ou reativar clientes que sumiram. Tambem quando ele colar uma
  mensagem de cliente pedindo horario, ou pedir as mensagens de confirmacao,
  lembrete e reativacao no tom da marca dele.
---

# Pauta - sua agenda cheia e ninguem falta

Pauta cuida do ciclo do cliente recorrente: marcar, confirmar, lembrar, remarcar,
chamar de volta e reativar quem sumiu. O motor (`scripts/pauta.py`, so Python
padrao) faz a parte chata e deterministica - guarda a agenda, acha horario livre,
detecta conflito, calcula quem esta vencido para voltar e quem sumiu. Voce (Claude)
faz a parte humana: escrever as mensagens no tom do dono usando os modelos.

A agenda fica em `.pauta/agenda.csv` e a configuracao em `.pauta/config.json` -
tudo local, na maquina do usuario, fora do controle de versao.

<!-- SETUP:START -->
## Primeira vez (configuracao) - faca antes de qualquer outra coisa

Se NAO existir o arquivo `.pauta/config.json` no projeto, configure o Pauta antes
de usar. Pergunte ao usuario (de forma natural, uma pergunta de cada vez ou via
AskUserQuestion) e colete:

1. **Nome do negocio** e tipo (clinica, barbearia, salao, consultorio, restaurante, consultoria, outro).
2. **Profissionais** que atendem (lista de nomes; pode ser so um).
3. **Servicos** - para cada um: nome, duracao em minutos, preco, e de quantos em
   quantos dias o cliente costuma voltar (ex: corte 21, consulta 180, limpeza 180).
4. **Horario de funcionamento** por dia da semana (seg..dom), e o intervalo/almoco.
5. **Canal** preferido de contato (padrao WhatsApp) e o **tom** das mensagens
   (ex: caloroso e proximo / formal / descontraido) + a **assinatura**.
6. (Opcional) antecedencia minima para remarcar (horas) e em quantos dias antes
   mandar lembrete (padrao 2 e 1 dia antes).

Depois monte um JSON de respostas (veja `respostas_exemplo.json` para o formato)
e grave a configuracao rodando:

```bash
python3 scripts/primeira_vez.py --respostas /tmp/respostas_pauta.json
```

Esse script grava `.pauta/config.json` + `.pauta/config.md`, cria a agenda vazia,
poe `.pauta/` no `.gitignore` e **se apaga**, deixando a skill limpa. Rode uma vez so.

> Em sessao automatica (sem humano), o JSON de respostas pode vir pronto no
> pedido - escreva-o em `/tmp/respostas_pauta.json` e rode o comando acima sem
> usar AskUserQuestion.
<!-- SETUP:END -->

## Como trabalhar

1. Garanta que a config existe (senao, faca a Primeira vez acima).
2. Leia `.pauta/config.md` para saber tom, servicos, horarios e assinatura.
3. Use o motor para a parte deterministica; escreva as mensagens com os modelos de
   `references/modelos_mensagens.md`, sempre **personalizadas** (nome, servico,
   profissional, data, hora) e no tom da config.
4. Toda mensagem que voce gerar e para o dono **revisar e enviar** - nunca diga
   que enviou. O Pauta nao manda nada sozinho.

### Modos (combine conforme o pedido)

**1. Agendar** - cliente pediu horario (texto colado do WhatsApp, telefonema, etc.).
- Veja horarios livres: `python3 scripts/pauta.py slots AAAA-MM-DD --servico "Corte" [--prof Joao]`
  (aceita tambem `hoje`, `amanha`, `+3d`, `sab`).
- Ofereca 2-3 opcoes ao cliente. Quando ele escolher, salve:
  `python3 scripts/pauta.py add --cliente "Ana" --tel "5511..." --servico "Corte" --prof "Joao" --data AAAA-MM-DD --hora 14:00`
- Escreva a mensagem de confirmacao do agendamento.

**2. Confirmar (D-1) e Lembrar (D-2)** - reduz no-show ate ~40%.
- Liste os agendamentos do dia alvo: `python3 scripts/pauta.py dia amanha`
- Para cada um, gere a mensagem de lembrete/confirmacao (modelo correspondente).
- Quando o cliente responder "confirmo": `python3 scripts/pauta.py status --id N --para confirmado`.

**3. Remarcar / Cancelar.**
- Remarcar: `python3 scripts/pauta.py remarcar --id N --data AAAA-MM-DD --hora 15:30`
  (avisa se houver conflito). Cancelar: `python3 scripts/pauta.py cancel --id N`.
- Facilite ao maximo - ofereca novos horarios livres na hora (rode `slots`).

**4. Marcar presenca / falta** (depois do atendimento).
- `python3 scripts/pauta.py status --id N --para atendido` (ou `faltou`).
- Quem faltou vira candidato a reativacao.

**5. Retorno** - chamar de volta quem esta na hora de voltar.
- `python3 scripts/pauta.py retorno` (ou `--ate AAAA-MM-DD`). Para cada cliente
  vencido, escreva um convite gentil de retorno.

**6. Reativar** - clientes que sumiram.
- `python3 scripts/pauta.py reativar --dias 60`. Escreva uma mensagem de
  reativacao (com motivo de voltar; se fizer sentido, um incentivo).

**7. Encaixe / Lista de espera.**
- Adicione a espera: `python3 scripts/pauta.py add --cliente "Ana" --tel ... --servico ... --espera`.
- Veja a fila: `python3 scripts/pauta.py espera`. Quando abrir um buraco
  (cancelamento), rode `slots` e ofereca a quem esta esperando.

**8. Resumo** - `python3 scripts/pauta.py resumo` mostra contagem por status e a
taxa de no-show.

## Regras de ouro
- **Nunca invente** horario, preco ou dado de cliente - tudo vem da config/agenda.
- **Personalize sempre** - nome, servico, profissional, data e hora em toda mensagem.
- **WhatsApp-first, humano e curto** - nada de textao robotico.
- **Respeite o "nao"** - quem pediu para nao receber, nao recebe; sem spam.
- O Pauta **sugere**; quem envia e o dono.

## Inputs / Outputs
- **Entra**: pedidos do dono em linguagem natural (mensagens de cliente, "confirma
  a agenda de amanha", "quem sumiu?"). Dados ficam em `.pauta/agenda.csv`.
- **Sai**: horarios sugeridos, agenda atualizada e mensagens prontas (no tom da marca)
  para o dono revisar e enviar.

## Dependencias
- Python 3 (biblioteca padrao apenas - sem instalar nada).
