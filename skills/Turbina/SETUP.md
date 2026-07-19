# Preparação (primeira execução)

A Turbina faz uma **preparação rápida** na primeira vez que você usa — só uma conversa
em português, nada técnico. Ela pergunta:

- qual é o seu negócio / nicho;
- em qual plataforma você anuncia (Meta / Google / os dois);
- qual o objetivo típico do anúncio (mensagem, lead, venda, agendamento);
- **quanto vale uma venda** (ticket médio) e **quanto sobra dela** (margem);
- quanto você costuma investir (por dia ou por mês);
- onde a venda acontece (WhatsApp, Direct, site);
- o seu jeito de falar com o cliente.

Com isso, ela calcula o seu **ponto de equilíbrio** (o CPA máximo e o ROAS mínimo que
a sua margem permite) e guarda tudo em `.turbina/config.md`, na raiz do seu projeto.

Esses dados ficam **só na sua máquina** e fora do controle de versão (a Turbina
garante a linha `.turbina/` no seu `.gitignore`).

Depois que a preparação termina, os arquivos de setup se **apagam sozinhos** — o que
fica é a skill limpa e o seu `config.md`. A partir daí, é só conversar:

> "monta minha campanha" · "quanto invisto?" · "cola essa exportação e me diz o que matar"

Para refazer a preparação do zero, apague a pasta `.turbina/` e chame a Turbina de novo.
