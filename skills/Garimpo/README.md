# Garimpo ⛏️ — seu analista de dados de bolso

Garimpar é separar o ouro do cascalho. É o que esta skill faz com as suas
planilhas: você manda um CSV e pergunta o que quiser, em português — *"qual produto
vende mais?"*, *"quantos clientes novos esse mês?"*, *"qual dia tem mais falta?"* —
e o Garimpo lê o arquivo, faz a conta certa e te explica de forma simples.

**Nunca inventa número.** Toda resposta vem de uma conta feita sobre o seu arquivo
real. Se o dado não está lá, ele te diz — não chuta.

## O que ele faz (6 modos)

1. **Conhecer** — abre a planilha e mostra o que tem (colunas, tipos, vazios) e
   sugere boas perguntas.
2. **Perguntar** — soma, conta, média, com filtros ("só os de SP").
3. **Ranking** — top/piores, com a concentração 80/20.
4. **Tendência** — como evolui por dia, semana ou mês.
5. **Cruzar** — uma coisa por outra (ex.: faturamento por produto × mês).
6. **Resumo** — um panorama dos números + alerta de qualidade dos dados.

Serve para qualquer tabela: vendas, clientes, estoque, agendamentos, leads,
exportações de anúncios, produção — não só finanças.

## Como instalar

1. Descompacte o arquivo `Garimpo.zip`.
2. Copie a pasta `Garimpo` para dentro de `.claude/skills/` no seu projeto (ou
   `~/.claude/skills/` para usar em qualquer projeto).
3. Abra o Claude Code nessa pasta e diga: **"Garimpo, analisa essa planilha"** (com
   o caminho do seu CSV). Na primeira vez ele faz um setup rápido.

Tem só Excel? Use **Arquivo → Salvar como → CSV** (um clique) — o Garimpo lê CSV.

Caminho final esperado:
```
.claude/skills/Garimpo/SKILL.md
```

## Privacidade

Tudo fica no seu computador. Seus dados e análises ficam na pasta `.garimpo/`
(ignorada pelo Git). Nada é enviado para fora.

## Requisitos

- Claude Code instalado.
- Python 3 (já vem no macOS e na maioria dos Linux) — sem bibliotecas extras, sem
  chave de API.

## Licença

MIT — use, adapte e compartilhe à vontade.
