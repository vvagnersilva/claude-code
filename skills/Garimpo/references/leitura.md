# Como ler um resultado e explicar em PT-BR

O motor entrega o número certo. Seu trabalho é transformar isso numa resposta que
o dono entende e pode usar. Siga esta ordem.

## A estrutura de uma boa resposta
1. **Resposta direta primeiro.** "O produto que mais vendeu foi o Plano Anual:
   R$ 48.200." Sem rodeio.
2. **A leitura (1-2 frases).** O que aquilo significa. "Sozinho, ele puxa 38% do
   faturamento — uma boa parte do seu resultado depende de um único produto."
3. **A base.** Sempre diga de quantos registros saiu. "Isso é de 1.250 vendas no
   período da planilha."
4. **Um próximo passo, se couber.** "Quer ver como esse produto evolui mês a mês?"

## Traduzindo perguntas comuns em comandos
| A pessoa pergunta… | Comando |
|--------------------|---------|
| "quanto vendi no total?" | `agrupar ... --metrica valor --op soma` (sem `--por`) ou `resumo` |
| "quanto por [X]?" | `agrupar --por X --metrica valor --op soma` |
| "quantos [registros] de [Y]?" | `agrupar --por Y --op contagem` |
| "qual a média de [M] por [X]?" | `agrupar --por X --metrica M --op media` |
| "top N de [X]" / "quem mais/menos" | `ranking --por X --metrica M --top N` |
| "como evoluiu / por mês / tendência" | `tendencia --data D --metrica M --periodo mes` |
| "[A] por [B]" (duas dimensões) | `cruzar --linhas A --colunas B --metrica M` |
| "só os que [condição]" | adicione `--onde "coluna OP valor"` |
| "que valores tem na coluna X?" | `valores --coluna X` |
| "panorama / o que esses números dizem" | `resumo` |

## Sinais de dado sujo — avise SEMPRE que aparecerem
- **Muitos vazios numa coluna** (o `perfil`/`resumo` apontam) → o número pode estar
  subestimado; diga quantos ficaram de fora.
- **Datas que não leram** (a `tendencia` avisa quantas) → o período pode estar incompleto.
- **Mesma coisa escrita de formas diferentes** ("SP", "São Paulo", "sao paulo") →
  o agrupamento vai separar; sugira padronizar (ou use `valores` para mostrar).
- **Período incompleto** (o mês atual ainda não acabou) → não compare um mês pela
  metade com meses inteiros sem avisar.
- **Amostra pequena** (poucos registros num grupo) → uma média de 3 itens não é
  tendência; sinalize.

## O que NÃO fazer
- Não apresente porcentagem sem o número absoluto por trás.
- Não diga "cresceu/caiu" sem mostrar os dois períodos.
- Não use termo de estatística (mediana, desvio, correlação) sem explicar em uma
  frase simples — e só se a pessoa precisar.
- Não conclua causa ("vendeu mais por causa de X") a partir de uma planilha que só
  mostra o quê, não o porquê. Aponte o padrão; a causa é hipótese.
