# Farol 🔦

**O analista financeiro do seu negócio, dentro do Claude Code.**

Você manda suas vendas e gastos do jeito que tiver — planilha, CSV do banco,
anotação solta — e o Farol responde em português simples:

- **Quanto sobrou no mês** (e se isso é bom ou ruim)
- **Qual serviço ou cliente dá lucro de verdade** (nem sempre é o que mais vende)
- **Se a receita está crescendo ou caindo**
- **Quanto tempo o seu caixa aguenta**
- **Alertas** antes que o problema cresça
- **"Posso contratar? Vale comprar?"** — decisão com conta na mesa

Tudo roda na sua máquina. Seus números não saem do seu computador.

## Para quem é

Donos de negócio de serviço — clínicas, barbearias, agências, escritórios,
consultorias, lojas — que têm os números espalhados e nenhum analista para
olhá-los. Não precisa saber programar nem entender de finanças.

## Instalação

1. Baixe e descompacte o arquivo `Farol.zip`.
2. Copie a pasta `Farol` para dentro da pasta `.claude/skills/` do seu projeto
   (crie se não existir):

   ```
   seu-projeto/
   └── .claude/
       └── skills/
           └── Farol/
   ```

   Dica: para usar em qualquer projeto, copie para `~/.claude/skills/Farol`.
3. Abra o Claude Code nessa pasta e diga: **"Farol, analisa meus números"**.

## Primeira conversa

Na primeira vez, o Farol faz um papo rápido de 2 minutos: nome do negócio,
ramo, despesa fixa aproximada e seu objetivo. Ele cria a pasta local `.farol/`
(onde ficam seus lançamentos e configurações) e está pronto. Esse setup
acontece uma vez só.

## Frases do dia a dia

| Você diz | O Farol faz |
|----------|-------------|
| "Como está o negócio?" | Resumo com sinal verde/amarelo/vermelho |
| "Fecha o mês de maio" | Fechamento: entrou, saiu, sobrou, de onde e para onde |
| "O que dá mais lucro?" | Margem por serviço/categoria |
| "Quem são meus maiores clientes?" | Ranking com risco de concentração |
| "Estou crescendo ou caindo?" | Tendência dos últimos meses |
| "Tenho R$ 12 mil em caixa, aguento quanto tempo?" | Fôlego de caixa |
| "Tem algo errado?" | Alertas de atenção |
| "Posso contratar um assistente de R$ 2.500?" | Decisão com cenários e payback |
| "Toma essa planilha de vendas" | Importa e organiza no livro de lançamentos |

## Garantias

- **Nunca inventa número** — toda resposta sai dos seus lançamentos.
- **Dados 100% locais** — nada é enviado para internet.
- **Sem dependências** — usa só o Python que já vem no sistema. Sem conta,
  sem chave de API, sem mensalidade.
- **Você decide** — o Farol mostra a conta e recomenda; a decisão é sua.

## Requisitos

- Claude Code instalado
- Python 3 (já vem no macOS e na maioria dos Linux; no Windows, instale de python.org)

## Licença

MIT — veja o arquivo `LICENSE`.
