---
name: orquestra-propostas
description: Naipe de Propostas da Orquestra — propostas comerciais, orçamentos e follow-up de clientes para negócios de serviços. Use quando o usuário pedir uma proposta, orçamento, precificação de serviço, mensagem de follow-up, ou script de fechamento. Trabalha em PT-BR com o contexto do negócio em .orquestra/config.md.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
---

# Naipe de Propostas

Cria **propostas comerciais que fecham** e cuida do follow-up. Para profissionais e PMEs que vendem serviços e perdem negócio por proposta fraca ou por não dar sequência.

## Antes de começar
Leia `.orquestra/config.md` (nome, nicho, serviços, tom, persona). Use os serviços reais do negócio.

## O que entrega
1. **Proposta comercial** estruturada:
   - Abertura que mostra que entendeu a dor do cliente.
   - Escopo do serviço (o que está e o que NÃO está incluído).
   - Entregáveis e prazos.
   - Investimento (com opções/planos quando fizer sentido — ancoragem de 3 níveis funciona bem).
   - Prova (cases, garantia, diferencial) e próximo passo claro.
2. **Orçamento / precificação** — ajuda a precificar por valor, não só por hora. Sugere faixas e justifica.
3. **Follow-up** — sequência de 3 mensagens (curto prazo) para quem recebeu proposta e não respondeu, no tom do negócio, sem ser insistente.

## Como trabalhar
1. Reúna o essencial: qual serviço, para qual cliente, qual dor, qual orçamento aproximado. Use AskUserQuestion se faltar.
2. Gere a proposta em markdown limpo, pronta para virar PDF ou e-mail.
3. Ofereça as opções de investimento e o follow-up.

## Regras
- **Foco no valor para o cliente**, não em listar tarefas.
- **Escopo claro** para evitar trabalho fora do combinado.
- **Sem prometer o que o negócio não entrega.**
- Tom e nomes de serviço sempre conforme o `config.md`.
