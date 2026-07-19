# Triagem — como separar a pilha

A meta: em poucos minutos a pessoa sabe **o que responder hoje** e ve que a maior
parte da caixa nao exigia acao nenhuma.

## As 4 faixas

| Faixa | Quando | O que fazer |
|-------|--------|-------------|
| 🔴 **Responder hoje** | Pergunta ou pedido direto ao dono; cliente esperando; algo com prazo; financeiro (boleto/fatura/pagamento); remetente importante (VIP); reclamacao | Rascunhar resposta + registrar pendencia |
| 🟡 **Pode esperar** | Precisa de resposta, mas nao e hoje; assunto sem urgencia; "quando puder" | Registrar pendencia, responder depois |
| 🟢 **Arquivar / so ler** | Confirmacao de pedido, comprovante, agenda, informativo que so se le | Ler e arquivar, sem resposta |
| ⛔ **Ignorar** | Divulgacao, promocao, newsletter que nao le, notificacao automatica, spam | Arquivar/apagar em bloco |

## Sinais que puxam pra 🔴 Responder hoje
- Vem de um **remetente importante** (lista de VIPs do config).
- **Linguagem de urgencia**: "urgente", "hoje", "prazo", "vence", "para ontem", "aguardo retorno".
- **Financeiro**: boleto, fatura, nota fiscal, pagamento, Pix, cobranca.
- **Pergunta/pedido direto**: "voce pode", "poderia", "me confirma", "qual", "quando", "?".
- **Reclamacao / insatisfacao / pedido de cancelamento** — sempre entra na frente.
- E uma **resposta dentro de uma conversa que o proprio dono comecou**.

## Sinais que puxam pra 🟢/⛔ (ruido)
- Remetente `no-reply`, `noreply`, `marketing@`, `news@`, `notificacao`.
- Assunto de divulgacao: "oferta", "desconto", "imperdivel", "webinar", "resumo semanal".
- Nao pede nada de voce; e so informativo ou promocional.

## Pista do motor (opcional, mas util)
Salve o texto da mensagem num arquivo temporario e peca a pista:
```bash
python3 ".../carteiro.py" classificar --remetente "fulano@x.com" --assunto "..." --corpo-arquivo /tmp/msg.txt
```
Ele devolve `categoria`, `confianca` (alta/media/baixa) e `motivos`.

**Gate de confianca:** se `confianca: baixa`, o motor esta dizendo "nao tenho sinais
fortes". Nesse caso NAO aceite a categoria no automatico — leia a mensagem e
decida, ou pergunte ao dono. O motor e uma pista, nao um juiz.

## Formato de apresentacao da fila
```
📬 Triagem — <data>
<N> mensagens · 🔴 <a> · 🟡 <b> · 🟢 <c> · ⛔ <d>

🔴 RESPONDER HOJE (<a>)
1. <Remetente> — <assunto>
   O que quer: <uma linha>
   → Sugerido: Responder / Agendar / Encaminhar pra <quem>

🟡 PODE ESPERAR (<b>)
2. ...

🟢 SO LER / ARQUIVAR (<c>)   — resumo em contagem, sem detalhar uma a uma
⛔ IGNORAR (<d>)             — resumo em contagem
```
Depois da fila, ofereca: "quer que eu rascunhe as respostas das 🔴?" e registre
cada 🔴 como pendencia (`pend-add`).
