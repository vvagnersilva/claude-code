# O que é uma receita (e o que cada campo significa)

Uma **receita** é o jeito de fazer uma tarefa, guardado para repetir sempre
igual. Ela NÃO guarda fatos nem dados do negócio — guarda o **método**. Os dados
entram na hora de rodar (a "entrada"). Cada receita vive em
`.bancada/receitas/<slug>.json` e tem estes campos:

| Campo | O que é | Exemplo |
|-------|---------|---------|
| **nome** | Como o dono chama a rotina | "Resposta de orçamento" |
| **faz** | Uma frase do que ela resolve | "Monta um orçamento a partir do pedido do cliente" |
| **gatilho** | Frases que disparam a receita | "faz um orçamento", "responde esse pedido" |
| **entrada** | O que o dono fornece na hora de rodar | "O e-mail/mensagem do cliente pedindo preço" |
| **passos** | O passo a passo a seguir, em ordem | 1. Identifique o que ele pediu · 2. Veja o que falta perguntar · 3. Monte 3 opções… |
| **saida** | Como o resultado tem que sair | "E-mail curto: saudação, 3 opções com preço, próximo passo, assinatura" |
| **tom** | O tom de voz e regras fixas | "Próximo e prestativo, sem ser informal demais; sempre ofereça uma call" |
| **exemplos** | 1+ par real de entrada→saída | (a melhor forma de ensinar o estilo) |

O motor ainda guarda sozinho: `criada_em`, `usos` (quantas vezes rodou) e
`ultimo_uso`.

## Como é uma boa receita

- **Os passos descrevem o MÉTODO, não os dados.** "Liste os itens que o cliente
  pediu" (bom) em vez de "O cliente pediu 3 camisas" (isso é dado, vem na
  entrada).
- **A saída é específica.** "3 parágrafos no máximo, com assinatura X" funciona
  melhor que "um texto bom".
- **O exemplo real vale por dez explicações.** Sempre que o dono tiver um, guarde.
- **A receita evolve.** Cada feedback de uso ("encurta", "sempre inclua Y") deve
  entrar na receita pelo modo Melhorar — assim ela fica cada vez mais a cara dele.

## O que uma receita NÃO é

- Não é um banco de dados do cliente (isso some — cada rodada usa a entrada da
  vez).
- Não é uma automação que dispara sozinha. A Bancada gera; o dono revisa e envia.
- Não é um robô que inventa números/fatos. Se a entrada não traz um dado que a
  receita precisa, a regra é **perguntar**, nunca chutar.
