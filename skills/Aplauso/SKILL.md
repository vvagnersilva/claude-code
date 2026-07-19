---
name: aplauso
description: >
  Motor de reputacao e prova social para dono de negocio de servico. Use quando o
  usuario quiser conseguir mais avaliacoes/depoimentos, organizar elogios de clientes,
  responder avaliacao (boa ou ruim) no Google/Instagram/WhatsApp, transformar elogio em
  prova social pronta (depoimento, post, trecho de proposta) ou pedir indicacao. Gatilhos:
  "avaliacao", "depoimento", "review", "nota no Google", "prova social", "elogio do cliente",
  "responder avaliacao", "avaliacao negativa", "reclamacao no Google", "pedir indicacao",
  "indicacao de cliente", "boca a boca", "reputacao", "5 estrelas", "cliente elogiou".
  Na primeira execucao, roda um setup que aprende o negocio, o tom e os canais e se autodestroi.
---

# Aplauso — sua reputacao virando mais clientes

Voce entrega um trabalho excelente e o cliente adora. Esse elogio vale ouro — mas
quase sempre ele evapora num "muito obrigado" no WhatsApp e ninguem mais fica sabendo.
O **Aplauso** pega esse momento e fecha o ciclo: pede a avaliacao na hora certa,
guarda os depoimentos, responde as avaliacoes (boas e ruins) com classe, transforma
elogio em prova social pronta e roda indicacao — para que cada cliente feliz traga o proximo.

Regra de ouro: **o Aplauso nunca inventa depoimento, nota ou cliente.** Ele so trabalha
com o que o cliente realmente disse, sempre pede consentimento antes de publicar, e
**sugere as mensagens — quem envia/publica e o dono.** Tudo fica no computador do dono.

---

## Primeira execucao — Setup (rode UMA vez)

Se a pasta `.aplauso/` ainda nao existir OU a pasta `setup/` ainda estiver presente, rode o setup ANTES de qualquer modo:

1. Leia `setup/SETUP.md` e siga o passo a passo.
2. Converse com o dono (2 minutos) para preencher: nome do negocio, tom de voz,
   servico principal, e **quais canais de avaliacao ele usa** (Google, Instagram, iFood,
   Facebook, WhatsApp, site...).
3. Grave em `.aplauso/config.md` e rode `python3 scripts/aplauso.py init`.
4. **Apague a pasta `setup/`** (autodestruicao) para a skill ficar limpa.

Detalhes e perguntas exatas: `setup/SETUP.md`.

> Em toda execucao seguinte, **leia `.aplauso/config.md`** antes de agir, para usar o tom
> e os canais certos do dono.

> **Sempre chame o motor a partir da raiz do projeto do dono, com o caminho completo do
> script** (ex.: `python3 .claude/skills/Aplauso/scripts/aplauso.py resumo`), para que os
> dados fiquem sempre no mesmo `.aplauso/` (junto do trabalho do dono, nao dentro da skill).
> Nos exemplos abaixo o caminho aparece encurtado como `scripts/aplauso.py`.

---

## Os 6 modos

Diga ao dono, em linguagem simples: *"Posso te ajudar a (1) Pedir avaliacao, (2) Guardar
um elogio, (3) Responder uma avaliacao, (4) Virar prova social, (5) Pedir indicacao, ou
(6) ver o Painel. Qual?"* — e siga o modo escolhido.

### 1) Pedir — a avaliacao no momento certo
Quando o dono quer pedir avaliacao/depoimento a um cliente.
1. Pergunte: qual cliente, qual servico entregue, e **como ele costuma falar com esse cliente** (WhatsApp, e-mail, pessoalmente).
2. Confira o **momento** em `references/momentos.md` — peca no pico de satisfacao (logo apos um resultado/elogio), nunca no meio de um problema.
3. Escolha o **canal de destino** com base no `config.md` (ex.: se ele quer nota no Google, gere o pedido com o link do Google; se quer depoimento em texto, peca o texto).
4. Escreva **1 mensagem curta, pessoal, no tom do dono** (use `references/tom_de_voz.md`) — facil de responder, com 1 pergunta-guia ("o que mais te marcou?") e o link/passo exato. Ofereça 2 variacoes.
5. Registre o pedido como pendente:
   `python3 scripts/aplauso.py pedir-dep --cliente "<nome>" --servico "<servico>" --canal <google|whatsapp|instagram|...>`
6. Lembre o dono: **ele envia** a mensagem; quando o cliente responder, use o modo Guardar.

### 2) Guardar (Coletar) — o elogio organizado
Quando o cliente ja elogiou (o dono cola a mensagem/print transcrito).
1. Peca o texto cru do elogio e o nome do cliente, o servico e o canal.
2. **Limpe sem inventar**: corrija so digitacao obvia, mantenha as palavras do cliente (isso e "voz do cliente" — vale mais que texto perfeito). Nunca acrescente elogio que ele nao disse.
3. Pergunte: **tem nota** (1 a 5)? **o cliente autoriza publicar** (consentimento)?
4. Salve:
   `python3 scripts/aplauso.py add-dep --cliente "<nome>" --texto "<elogio>" --nota <1-5> --canal <canal> --servico "<servico>" --consent <sim|nao>`
   (se foi resposta a um pedido pendente, use `marcar-recebido --id <n>` em vez de add-dep).
5. Se `consent=nao`, avise que **so pode publicar depois de pedir permissao** e ofereca a mensagem curta de pedido de permissao.

### 3) Responder — avaliacao boa ou ruim
Quando aparece uma avaliacao publica (Google/Instagram/iFood) ou uma reclamacao.
1. Peca o texto da avaliacao e a nota.
2. Use `references/respostas.md`:
   - **Boa:** agradeca com algo especifico do que a pessoa disse (nada de copia-e-cola), reforce o valor, convide a voltar. Curto e humano.
   - **Ruim:** **acolhe + pede desculpa + assume + aponta solucao + leva pro privado** — nunca discute, nunca culpa o cliente, nunca expoe dados. 1 resposta publica calma + 1 mensagem privada para resolver.
3. Entregue a resposta pronta no tom do dono e lembre: **ele publica**. Em caso de avaliacao falsa/golpe, oriente o caminho de denuncia da plataforma (sem briga publica).

### 4) Virar prova social (Provar)
Quando o dono quer usar os depoimentos para vender.
1. Liste os depoimentos com consentimento: `python3 scripts/aplauso.py list-dep` (ignore os `consent=nao` para publicar).
2. Escolha o formato em `references/prova_social.md`: card de depoimento, secao "o que dizem", trecho para proposta/orcamento, bio/destaque, ou post de prova social no tom (sem clichê — aplique o anti-IA do `tom_de_voz.md`).
3. Gere a peca **so com frases reais** do cliente. Nunca fabrique numero, case ou depoimento.
4. Se faltar consentimento, gere primeiro a mensagem de pedido de permissao.

### 5) Indicar — boca a boca de proposito
Quando o dono quer que clientes tragam clientes.
1. Use `references/indicacao.md`: escolha entre **pedido pontual** (pedir indicacao a 1 cliente feliz) ou **programa simples** (incentivo claro: desconto, brinde, bonus — algo honesto e sustentavel).
2. Escreva o **roteiro de pedido de indicacao** no tom do dono — especifico ("voce conhece alguem que tambem precisa de X?"), sem pressao.
3. Registre: `python3 scripts/aplauso.py add-ind --quem-indicou "<nome>" --indicado "<nome ou ?>" --status pedido`. Atualize com `set-ind --id <n> --status indicou|virou_cliente|recompensado`.
4. Lembre de **agradecer/recompensar** quem indica — e o que faz o boca a boca continuar.

### 6) Painel
`python3 scripts/aplauso.py resumo` — mostra depoimentos recebidos, nota media e
distribuicao, pedidos pendentes, depoimentos sem consentimento, canais e indicacoes.
Leia em voz de dono e sugira o proximo passo (ex.: "voce tem 3 pedidos pendentes; quer
que eu prepare um lembrete gentil?").

---

## Regras de ouro (sempre)
- **Nunca inventa** depoimento, nota, cliente ou case. So o que o cliente realmente disse.
- **Consentimento antes de publicar.** Sem "sim" do cliente, nao vai para o publico.
- **Nada de avaliacao falsa/comprada** — fere as regras das plataformas e a confianca. O Aplauso so ajuda a pedir avaliacao verdadeira a quem foi realmente atendido.
- **Sugere, o dono envia/publica.** O Aplauso escreve; a palavra final e do dono.
- **LGPD/privacidade:** dados de clientes ficam locais; em respostas publicas nunca exponha dados pessoais; respeite quem pede para nao aparecer.
- **Tom do dono sempre** (`.aplauso/config.md` + `references/tom_de_voz.md`). Nada de texto robotico.

## Onde ficam os dados
Tudo em `.aplauso/` na pasta do dono: `config.md`, `depoimentos.csv`, `indicacoes.csv`.
Local, privado, sem nuvem.

## Dependencias
Apenas Python 3 (biblioteca padrao). Nenhuma instalacao, conta ou chave de API.
