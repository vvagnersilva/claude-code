# Turbina — o copiloto de tráfego pago

**Turbina** é uma skill de Claude Code que ajuda quem coloca dinheiro em anúncio
(Meta/Instagram/Facebook Ads e Google Ads) a fazer esse dinheiro voltar — falando em
português simples, sem "achismo". Ela **planeja** a campanha, faz a **conta de verba e
de equilíbrio** a partir da sua margem, e principalmente **lê a exportação de métricas**
que você cola e diz, com o porquê, o que **matar, ajustar ou escalar**.

Para gestores de tráfego, agências e donos de negócio que rodam o próprio anúncio.

## O que ela faz (6 modos)

1. **Planejar** — a estrutura da campanha (objetivo, públicos frio/morno/quente, verba, nomenclatura).
2. **Verba & Equilíbrio** — o ROAS de equilíbrio e o CPA máximo que a sua margem permite + projeção de resultado do orçamento em 3 cenários.
3. **Diagnóstico** — você cola a exportação do Gerenciador e a Turbina classifica cada campanha/conjunto: 🔴 matar · 🟡 ajustar · 🟢 escalar · ⚪ aguardar, com motivo e próxima ação.
4. **Otimizar & Escalar** — onde está o gargalo (criativo? público? página?), como escalar sem quebrar o aprendizado, fadiga de criativo.
5. **Testar** — a matriz de teste A/B (ângulo × público × formato) com critério de vitória.
6. **Aprendizados & Painel** — a memória do que venceu/fracassou e o resumo do mês.

## Instalação

1. Descompacte o arquivo `Turbina.zip`.
2. Copie a pasta `Turbina` para dentro de `.claude/skills/` do seu projeto (ou de
   `~/.claude/skills/` para deixá-la disponível em qualquer projeto):
   ```
   .claude/skills/Turbina/
   ```
3. Abra o Claude Code nesse projeto. A skill é descoberta sozinha.

## Como usar

Fale naturalmente. Exemplos que acionam a Turbina:
- "monta a estrutura da minha campanha de anúncio"
- "quanto eu devo investir por dia?"
- "qual é o meu ROAS de equilíbrio?"
- "cola essa exportação e me diz o que pausar"  *(e cole a tabela do Gerenciador)*
- "por que meu anúncio gasta e não vende?"
- "quando posso escalar?"
- "meu criativo saturou?"

Na **primeira vez**, a Turbina faz uma preparação rápida (nome do negócio, plataforma,
ticket, margem, orçamento, tom) e guarda tudo localmente em `.turbina/config.md`.
Depois disso é só conversar.

## O motor de contas (offline)

O arquivo `scripts/turbina.py` roda **100% local, só com a biblioteca padrão do
Python 3** — não instala nada, não acessa a internet, não conecta na sua conta de
anúncios. Ele só faz a matemática (equilíbrio, projeção) e lê a tabela que você colou.

```bash
python3 scripts/turbina.py equilibrio --ticket "R$ 500" --margem 40
python3 scripts/turbina.py verba --orcamento "R$ 3.000" --cpl "R$ 25" --conv 20 --ticket "R$ 500"
python3 scripts/turbina.py diagnostico --arquivo .turbina/metricas.csv --cpa-alvo "R$ 66" --cpa-max "R$ 200"
```

## Princípios (o que a Turbina nunca faz)

- **Nunca inventa métrica** — só trabalha com o que você colou ou informou.
- **Nunca conecta na sua conta nem move verba** — ela sugere; quem clica no Gerenciador é você.
- **Nunca promete resultado** — projeção é hipótese a validar com os números reais.
- **Seus dados ficam na sua máquina** — tudo em `.turbina/`, nada sobe pra lugar nenhum.

## Requisitos

- Claude Code.
- Python 3 (já vem no macOS e na maioria dos Linux; nada mais a instalar).

## Licença

MIT — veja `LICENSE`. Feito para a comunidade **Maestria Academy / Maestros da IA**.
