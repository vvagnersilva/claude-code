# Entrega — modelos de checklist (build, teste, handoff)

Use no modo **Entrega**. Monte o checklist com `planta.py tarefa-add` nas três
etapas. Adapte ao projeto — abaixo está o esqueleto que serve para a maioria das
automações de cliente. **IA sem gente que usa vira código morto**: teste e
treinamento NÃO são extra, são parte da entrega.

## Etapa BUILD (construir)
- [ ] Reunir os acessos e dados que o cliente precisa fornecer (lista do escopo).
- [ ] Montar o fluxo/automação principal (o que entrega o output).
- [ ] Preparar os modelos de mensagem/documento no **tom do cliente**.
- [ ] Tratar os casos de erro óbvios (dado faltando, fora do horário, duplicado).
- [ ] Documentar como funciona (pra não amarrar o cliente só a você / evitar lock-in).

## Etapa TESTE (testar com o real antes de subir)
- [ ] Rodar com **dados/casos reais** do cliente (não só exemplo).
- [ ] Conferir cada critério de aceite combinado (o output acontece? o número anda?).
- [ ] Testar o que dá errado: entrada incompleta, volume alto, exceção.
- [ ] Validar com 1 pessoa da equipe do cliente usando de verdade (piloto).
- [ ] Ajustar o que o teste mostrou antes de liberar pra todos.

## Etapa HANDOFF (colocar no ar + treinar + combinar suporte)
- [ ] Subir/ativar em produção com o cliente junto.
- [ ] **Treinar a equipe** que vai usar (passo a passo simples, na linguagem deles).
- [ ] Entregar um guia curto de uso + a quem recorrer quando travar.
- [ ] Combinar o **suporte e a melhoria contínua** (a recorrência da proposta).
- [ ] Marcar uma data para medir o resultado (a métrica andou? vira case/depoimento → Vitrine/Aplauso).

## Critérios de aceite (defina ANTES de construir)
Para cada projeto, escreva 3-5 frases objetivas do tipo "está pronto quando...":
- "Está pronto quando todo paciente do dia recebe o lembrete D-1 automaticamente."
- "Está pronto quando o relatório mensal sai sozinho até o dia 5."
- "Está pronto quando a recepção responde as 10 perguntas frequentes a partir da base."
Isso evita o "ficou faltando" no fim e protege contra escopo estourado.

## Regra de mudança (anti escopo estourado)
Pedido novo que não estava no escopo = **adendo separado** (novo item de escopo
com `--tipo dentro` numa nova fase, ou orçado à parte). Registre, não faça "de
graça por cima" — é o que corrói a margem.
