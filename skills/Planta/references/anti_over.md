# Anti-over-engineering + placar de complexidade

A maior armadilha de quem entrega automação é **construir tecnologia bonita em
vez de resolver o problema**. Ninguém liga pro seu fluxo de 47 passos — o cliente
liga pro **número que vai mudar**. Use este arquivo no **Desenhar** e no **Escopo**.

## Teste da automação mínima viável (rode antes de fechar o desenho)
Responda honestamente para cada item da solução:

1. **Isso move o output/métrica?** Se não move o número combinado, **corte**.
2. **Resolve com o que o cliente já tem?** Se planilha + WhatsApp + formulário
   entregam, **não** proponha n8n, banco, app ou IA dedicada.
3. **O cliente vai conseguir usar/manter?** Se depende de algo que só você
   entende, ou de adoção heroica da equipe, **simplifique** ou faça **piloto**.
4. **Dá pra entregar a primeira versão em poucas semanas?** Se não, fatie: entrega
   o pedaço que já dá ganho primeiro (vitória rápida), o resto vira fase 2.
5. **Estou somando isto porque o cliente precisa, ou porque é legal de fazer?**
   Se é "legal de fazer", vai para **fora do escopo**.

> Regra de ouro: **comece pelo output, não pela ferramenta.** A ferramenta é a
> última decisão, não a primeira.

## Sinais de over-engineering (corte na hora)
- Mais de uma ferramenta nova que o cliente nunca usou, logo de cara.
- "Já que estamos aqui, dá pra também..." — isso é fase 2 ou fora do escopo.
- Integração complexa para um volume pequeno (10 itens/mês não pedem API).
- IA cara (RAG, agente) onde uma FAQ + base resolveria.
- Painel/dashboard que ninguém pediu nem vai abrir.

## Placar de complexidade (para o Escopo)
Classifique cada item do escopo como **simples / moderado / complexo** olhando 4
fatores. Quanto mais fatores "altos", mais complexo (e mais horas/risco):

| Fator | Simples | Moderado | Complexo |
|------|---------|----------|----------|
| **Prontidão dos dados** | já organizados/exportáveis | precisam limpar | espalhados/sujos/sem acesso |
| **Superfície de integração** | nenhuma (1 ferramenta) | 2 ferramentas conhecidas | várias / API instável / sistema fechado |
| **Risco se errar** | baixo (interno) | médio | alto (dinheiro, cliente final, legal) |
| **Distância da produção** | roda já | precisa de testes | precisa de homologação/aprovações |

- Use a classificação pra dar horas honestas e pra explicar o preço ao cliente.
- Um item **complexo** isolado costuma pedir **fase própria** e mais testes.

## ROI gate (antes de propor)
- Se o ganho (horas × custo-hora do cliente) **não** cobre o investimento em um
  prazo razoável, ou só fecha com adoção perfeita, **proponha um piloto menor**
  com uma meta clara de sucesso antes do projeto grande. Honestidade vende mais
  que promessa.
