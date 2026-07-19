# Catálogo de soluções (blocos de automação comuns) e quando cada um cabe

Use isto no modo **Desenhar**. Cada bloco resolve um problema comum. Escolha o
**mais simples que entrega o output** e que **casa com a ferramenta que o cliente
já tem**. Quase tudo abaixo resolve com WhatsApp + planilha + formulário; só suba
o nível (n8n/Make/sistema/IA dedicada) quando o volume ou a integração realmente
exigir.

> Para cada bloco: o que faz · quando cabe · ferramenta mais simples · quando
> subir o nível · onde fica o humano.

## 1. Lembrete e confirmação (anti-falta)
- **Faz:** avisa o cliente antes do compromisso e confirma presença.
- **Cabe quando:** negócio de hora marcada com no-show (clínica, salão, consultoria).
- **Mais simples:** mensagem-modelo no tom do negócio + lista do dia em planilha;
  o atendente dispara. Sobe o nível só com agenda integrada e volume alto.
- **Humano:** quem manda/confirma pode ser pessoa até o volume justificar automatizar o envio.

## 2. Captação e qualificação de lead
- **Faz:** recebe o interessado, faz 2-4 perguntas e organiza quem é quente/morno/frio.
- **Cabe quando:** entra lead por Instagram/site/anúncio e ninguém tria.
- **Mais simples:** formulário (Google Forms/typebot) → planilha; resposta-modelo automática.
- **Subir:** só com muitos leads/dia e necessidade de roteamento.

## 3. Resposta automática / atendimento da recepção (FAQ)
- **Faz:** responde as perguntas repetidas a partir de uma base, no tom do negócio.
- **Cabe quando:** o mesmo punhado de perguntas chega o dia todo.
- **Mais simples:** base de perguntas/respostas + resposta sugerida; pessoa revisa e envia.
- **Regra:** **nunca inventar resposta** — sem base, marca lacuna e dá resposta-ponte.

## 4. Organização e limpeza de dados (planilha)
- **Faz:** junta/limpa/padroniza dados que chegam bagunçados (PDF, foto, várias planilhas).
- **Cabe quando:** o cliente perde tempo copiando/colando e arrumando planilha.
- **Mais simples:** extração + planilha padronizada; nada de banco de dados se uma planilha resolve.

## 5. Relatório recorrente
- **Faz:** transforma dados crus num relatório/painel claro toda semana/mês.
- **Cabe quando:** alguém monta o mesmo relatório à mão sempre.
- **Mais simples:** modelo de relatório + planilha → documento/HTML. Sobe só se a fonte for múltipla e viva.

## 6. Follow-up / cobrança de retorno
- **Faz:** lembra de retomar contato com quem parou de responder (orçamento parado, cliente sumido).
- **Cabe quando:** dinheiro vaza por falta de follow-up.
- **Mais simples:** lista + cadência de mensagens-modelo; a pessoa envia.

## 7. Geração de documento padrão
- **Faz:** preenche contrato/proposta/laudo a partir de um modelo + dados do caso.
- **Cabe quando:** documentos repetitivos com poucos campos variáveis.
- **Mais simples:** modelo com campos → preenchimento; revisão humana sempre.

## 8. Triagem/encaminhamento de mensagens
- **Faz:** classifica o que chega (urgente, reclamação, dúvida) e prioriza.
- **Cabe quando:** muita mensagem misturada e o importante se perde.

## 9. Integração entre ferramentas (quando REALMENTE precisa)
- **Faz:** liga sistema A ao B (site → CRM, formulário → planilha → WhatsApp) sem cópia manual.
- **Cabe quando:** o cliente já usa esses sistemas, o volume é real e a cópia manual erra/atrasa.
- **Ferramenta:** aí sim n8n/Make/Zapier ou API. **Marque como complexo** no escopo.
- **Cuidado:** não amarre o cliente a uma ferramenta só (lock-in). Documente como funciona.

## 10. Assistente com IA sobre os dados do cliente (RAG)
- **Faz:** responde perguntas sobre os documentos/base do próprio cliente.
- **Cabe quando:** há volume grande de documento e perguntas recorrentes que uma FAQ não cobre.
- **Cuidado:** é o mais caro/complexo. Só proponha quando o ganho justifica; senão, FAQ + base resolve.

---

## Como montar o desenho (estado futuro)
1. Pegue o **output** e a **métrica** do Mapear.
2. Escolha 1-2 blocos acima que entregam esse output — **o mínimo que resolve**.
3. Descreva o **fluxo passo a passo**: o que dispara, o que acontece, o que sai.
4. Marque o que é **automático** e o que **continua humano** (e por quê).
5. Liste os **limites honestos** (o que NÃO faz) e o que o cliente precisa fornecer
   (acessos, base, aprovação).
6. Rode o teste anti-over-engineering (`anti_over.md`) antes de fechar.
