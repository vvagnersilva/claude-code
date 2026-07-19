# Banco de Automacoes — ideias por tipo de tarefa

Use isto no modo **Planejar** para sugerir a abordagem certa para cada processo.
Cada bloco traz: o que e, a abordagem mais simples primeiro, e o "pulo do gato".
Sempre prefira a abordagem MAIS SIMPLES que resolve — nao mande o dono montar
um robo de n8n se um modelo de mensagem pronto ja resolve 80%.

## Escada de abordagens (da mais simples para a mais complexa)
1. **Modelo pronto** — uma mensagem/texto/checklist padrao que o dono so copia e cola. Zero ferramenta.
2. **Claude na hora** — o dono cola o dado e pede o resultado (resumo, resposta, planilha). Sem montar nada.
3. **Planilha com formula** — Google Sheets/Excel faz a conta sozinho.
4. **Formulario** — Google Forms/Tally captura e organiza sem digitar.
5. **Automacao com gatilho** — n8n / Make / Zapier liga uma coisa na outra (ex.: chegou mensagem -> grava na planilha).
6. **Sistema sob medida** — so quando o ganho justifica; geralmente e um projeto.

> Regra de ouro: 60-70% das tarefas repetitivas de um negocio de servico sao
> resolvidas nos niveis 1 a 3. Comece sempre por baixo.

---

## As primeiras automacoes mais comuns (e que mais devolvem tempo)

### 1. Atendimento inicial no WhatsApp
- **O que e:** saudacao, horario de funcionamento, FAQ e triagem antes de chamar uma pessoa.
- **Mais simples:** mensagem de ausencia + um menu de respostas rapidas salvo no WhatsApp Business.
- **Pulo do gato:** so depois que o volume cresce vale um bot (n8n + WhatsApp). Antes disso, modelo pronto resolve.

### 2. Agendamento + confirmacao de horario
- **O que e:** marcar, confirmar e remarcar compromissos.
- **Mais simples:** link de agenda (Google Calendar / Calendly) + mensagem-modelo de confirmacao.
- **Ganho tipico:** confirmar na vespera derruba muito o no-show.

### 3. Lembrete de compromisso
- **O que e:** aviso 2 dias antes e confirmacao na vespera.
- **Mais simples:** modelo de mensagem + alarme. Depois, automatizar pelo gatilho da agenda.

### 4. Follow-up de orcamento/proposta
- **O que e:** cobrar resposta de quem recebeu um orcamento e sumiu.
- **Mais simples:** 3 modelos de mensagem (dia 1, dia 3, dia 7) que o dono dispara.
- **Pulo do gato:** uma planilha que marca a data do orcamento e avisa quem esta "vencendo".

### 5. Captura e qualificacao de lead
- **O que e:** organizar quem chega e separar quente/morno/frio.
- **Mais simples:** Google Forms -> planilha. Claude le e classifica em lote.

### 6. Regua de cobranca
- **O que e:** lembrar vencimento e reduzir inadimplencia.
- **Mais simples:** modelos de mensagem (antes, no dia, depois) + planilha de vencimentos.

### 7. Emissao de boleto/fatura recorrente
- **O que e:** gerar cobranca todo mes para os mesmos clientes.
- **Abordagem:** quase sempre ja existe no proprio sistema de pagamento — ative a recorrencia antes de montar qualquer coisa.

### 8. Extracao de dados de nota/recibo/PDF
- **O que e:** tirar numero, data, valor de documentos e jogar na planilha.
- **Mais simples:** o dono cola/anexa e o Claude extrai e organiza (sem inventar — sempre confere).
- **Combina com a skill Escriba**, se o dono tiver.

### 9. Triagem e rascunho de e-mail
- **O que e:** separar o que importa e ja deixar a resposta pronta no tom do dono.
- **Mais simples:** Claude le a caixa colada e devolve rascunhos. Dono so revisa e envia.

### 10. Relatorios automaticos
- **O que e:** fluxo de caixa, contas a receber/pagar, resumo de vendas.
- **Mais simples:** planilha com formula. Para mostrar bonito ao cliente/chefe, combina com a skill **Vitrine**.

### 11. Pos-atendimento / pedido de avaliacao
- **O que e:** agradecer e pedir feedback/avaliacao depois do servico.
- **Mais simples:** modelo de mensagem disparado no fim do atendimento.

### 12. Repurpose de conteudo
- **O que e:** transformar 1 conteudo em varios (post, legenda, e-mail).
- **Mais simples:** Claude na hora — cola o conteudo, pede as versoes.

---

## Como escolher a abordagem no modo Planejar
Para o processo escolhido, pergunte-se nesta ordem:
1. Da pra resolver com um **modelo pronto** que o dono so copia? Se sim, entregue o modelo.
2. Da pra **o Claude fazer na hora** com o dado colado? Se sim, ensine a frase exata.
3. Precisa **guardar/organizar dado**? Planilha ou formulario.
4. Precisa **ligar uma coisa na outra sem o dono no meio**? Ai sim, automacao com gatilho (n8n/Make/Zapier) — e avise que isso e um pequeno projeto.

Calibre pela ferramenta e nivel tecnico que estao no `config.md`: se o dono e
nao-tecnico e nao usa n8n, NAO mande montar n8n — fique nos niveis 1 a 4.
