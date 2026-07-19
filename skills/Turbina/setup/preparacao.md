# Preparação da Turbina (primeira execução)

> Este roteiro só roda **uma vez**. No fim, grava `.turbina/config.md` e **apaga a
> pasta `setup/`** para o repositório instalado ficar limpo.

Conduza como uma conversa em PT-BR, **uma pergunta por vez**, tom leve. Não peça nada
técnico. Se o dono não souber um número (ex.: margem), explique com um exemplo simples
e ajude a estimar — mas **registre que é estimativa**, nunca invente um valor "bonito".

## Perguntas (nesta ordem)

1. **Como você quer ser chamado e qual é o negócio?** (nome + o que vende / nicho)
2. **Você roda anúncio em qual plataforma?** (Meta = Instagram/Facebook · Google · os dois · ainda não comecei)
3. **Qual é o objetivo do anúncio, no geral?**
   - conversa/mensagem (WhatsApp, Direct)
   - lead (formulário, cadastro)
   - venda direta no site/checkout
   - agendamento
   - visita/tráfego pro site
4. **Quanto vale, em média, uma venda pra você?** (ticket médio — ex.: R$ 500)
5. **De cada venda dessas, quanto SOBRA depois dos custos?** (margem — em % ou em R$)
   - Explique: "se você vende por R$ 500 e o custo do que entregou é R$ 300, sobra
     R$ 200 = margem de 40%." Esse número é a base de tudo (o equilíbrio nasce dele).
6. **Quanto você costuma investir em anúncio?** (por dia OU por mês — ex.: R$ 50/dia)
7. **Onde a venda acontece depois do clique?** (WhatsApp / Direct / site / loja física)
8. **Como é o seu jeito de falar com o cliente?** (informal e próximo · profissional e
   direto · técnico · caloroso) — para as mensagens saírem no seu tom.

## O que gravar em `.turbina/config.md`

Crie a pasta `.turbina/` na **raiz do projeto** (onde o dono está usando o Claude Code)
e escreva o arquivo `config.md` com o conteúdo abaixo, preenchido com as respostas.
Se algum valor for estimativa, marque com `(estimado)`.

```markdown
# Config da Turbina

- Dono / negócio: <nome> — <nicho/o que vende>
- Plataforma principal: <Meta | Google | ambos | ainda não>
- Objetivo típico: <mensagem | lead | venda no site | agendamento | tráfego>
- Ticket médio: R$ <valor>
- Margem por venda: <pct>%  (= R$ <valor>)   <(estimado) se for o caso>
- Orçamento habitual: R$ <valor> por <dia|mês>
- Onde a venda acontece: <WhatsApp | Direct | site | loja>
- Tom de voz: <descrição curta>

## Equilíbrio (calculado)
- ROAS de equilíbrio: <preencher rodando: turbina.py equilibrio ...>
- CPA máximo (teto): R$ <preencher>
- CPA-alvo saudável: R$ <preencher>
```

Depois de escrever o config, **rode o cálculo de equilíbrio** com o ticket e a margem
informados e preencha as três últimas linhas:

```bash
python3 scripts/turbina.py equilibrio --ticket "R$ <ticket>" --margem <margem>
```

## Garanta que os dados fiquem fora do controle de versão

Se existir um `.gitignore` na raiz, garanta que ele contenha a linha `.turbina/`
(crie o `.gitignore` com essa linha se não existir). Os dados do dono são privados.

## Autodestruição (obrigatória no fim)

Quando o `config.md` estiver gravado e o equilíbrio preenchido, **apague a pasta de
setup** para o repositório instalado ficar limpo:

```bash
rm -rf setup
```

Confirme para o dono: *"Pronto! Sua Turbina está configurada. Da próxima vez é só
falar comigo — 'monta minha campanha', 'quanto invisto', ou cola a exportação de
métricas que eu te digo o que matar e o que escalar."*
