# Configuração de 1ª execução — Régua

> Você (a IA) conduz esta conversa **uma única vez**, na primeira vez que o dono usa a
> Régua. Objetivo: aprender o negócio e o **tom de cobrança** dele, gravar em
> `.regua/config.md` e depois **apagar a pasta `setup/`** para deixar a skill limpa.

## Como conduzir (linguagem simples, sem jargão)
Faça as perguntas abaixo em conversa natural, PT-BR, uma de cada vez. Aceite respostas
curtas. Se o dono não souber algo, use o padrão sugerido. **Nunca** peça termo técnico.

1. **Seu nome / nome do negócio** — como você quer assinar as cobranças?
2. **O que você cobra** — mensalidade, por serviço/job, ou os dois?
3. **Tom de voz na cobrança** — mais próximo e informal (com emoji) ou mais formal
   ("senhor(a)", sem emoji)? Dê um exemplo de como você costuma falar com cliente.
4. **Canal preferido** — WhatsApp (padrão), e-mail, SMS?
5. **Forma de pagamento que você manda** — Pix (chave?), boleto, link, transferência?
   (Não guarde a chave se o dono não quiser; pode deixar em branco.)
6. **Prazos da sua régua** — quer usar os padrões (lembrete 3 dias antes, no vencimento,
   e cobranças em +3, +7, +15 e +30 dias) ou ajustar?
7. **Encargos** — você cobra juros/multa por atraso? Se sim, quanto? (Se não, deixe em
   branco — a Régua **nunca** inventa encargo.)

## Ao terminar
1. Escreva `.regua/config.md` no formato abaixo (preencha com as respostas; use
   "(não informado)" no que faltar).
2. Garanta que existe um `.gitignore` na raiz do projeto com a pasta `.regua/` ignorada
   (a pasta guarda dados de cliente — nunca deve ir para o controle de versão).
3. Rode `python3 scripts/regua.py init` para criar o livro vazio.
4. **Apague a pasta `setup/` inteira** (`rm -rf setup`). A Régua instalada não precisa mais dela.
5. Diga ao dono, em 2 linhas, que está pronto e mostre como começar:
   *"Pronto! Pode me dizer quem te deve, tipo: 'o João me deve R$ 1.500, vence dia 10'."*

---

### Modelo de `.regua/config.md`
```markdown
# Configuração da Régua

- **Assino como:** {nome / negócio}
- **Cobro por:** {mensalidade / job / ambos}
- **Tom de voz:** {próximo+emoji / formal / ...} — exemplo: "{frase de exemplo do dono}"
- **Canal preferido:** {WhatsApp / e-mail / SMS}
- **Pagamento que envio:** {Pix: chave / boleto / link / transferência / (não informado)}
- **Régua (degraus em dias):** {-3, 0, +3, +7, +15, +30  ou os ajustados}
- **Encargos por atraso:** {juros/multa informados pelo dono / nenhum}

## Lembretes de comportamento
- Nunca inventar valor, data ou pagamento.
- A Régua sugere; quem envia é o dono (WhatsApp-first).
- Cobrar sempre com respeito; manter o cliente; oferecer saída.
- Dados ficam só em `.regua/`.
```
