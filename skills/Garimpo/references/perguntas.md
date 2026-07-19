# Perguntas que valem a pena, por tipo de dado / profissão

Use para sugerir 3-4 perguntas boas depois do `perfil`, conforme o que a planilha
tem. Sempre adapte aos nomes reais das colunas.

## Vendas / comércio / e-commerce (planilha de pedidos)
- Quanto faturei no total e no mês? (`resumo` / `tendencia --periodo mes`)
- Quais os 10 produtos que mais e que menos vendem? (`ranking`)
- Qual o ticket médio por canal/loja? (`agrupar --op media`)
- Que dia da semana / mês vende mais? (`tendencia`)
- Concentração: quantos produtos fazem 80% da receita? (`ranking` → 80/20)
- Faturamento por categoria e por mês (`cruzar`)

## Clientes / CRM / leads
- Quantos clientes novos por mês? (`tendencia --op contagem`)
- De onde vêm os leads (origem)? (`agrupar --por origem --op contagem`)
- Quais clientes compram mais (top)? (`ranking`)
- Quantos leads viraram cliente, por canal? (`cruzar --linhas canal --colunas status`)

## Agendamentos / atendimento (clínica, salão, consultoria)
- Qual dia/horário tem mais falta (no-show)? (`agrupar --por dia_semana --onde "status = falta"`)
- Quantos atendimentos por profissional/mês? (`cruzar` ou `tendencia`)
- Taxa de retorno: quantos voltaram? (`valores`/`agrupar`)

## Estoque / produção
- O que está parado (giro baixo)? (`ranking --ordem` / `agrupar`)
- Quanto tenho parado em valor por categoria? (`agrupar --metrica valor --op soma`)
- Entradas e saídas por mês (`tendencia`)

## Marketing / tráfego pago (exportação de Meta/Google Ads)
- Qual campanha teve melhor custo por resultado? (`agrupar --op media`)
- Gasto por campanha e por mês (`cruzar`)
- Onde está indo a maior parte do investimento? (`ranking` → 80/20)

## Financeiro / gastos (quando for só explorar, não decidir)
- Maiores categorias de gasto (`ranking`)
- Despesa por fornecedor e por mês (`cruzar`)
> Para DECISÃO de dinheiro com cenários, margem e fôlego de caixa, indique o **Farol**.

## Regra de ouro ao sugerir
Só sugira perguntas que **as colunas da planilha realmente respondem**. Se não há
coluna de data, não prometa tendência. Se não há valor, foque em contagens.
