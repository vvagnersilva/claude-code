# Configuração de 1ª execução da Âncora (roteiro para a IA)

Este arquivo só existe até a Âncora ser configurada. Conduza uma **conversa curta e leve** em
PT-BR (o dono NÃO é técnico), grave o resultado em `.ancora/config.md` e **apague a pasta `setup/`**
no final. Não cadastre nenhum cliente ainda — o setup só prepara o terreno; a carteira vem depois,
no modo Carteira.

## Como conduzir (uma pergunta de cada vez, tom acolhedor)

1. **Boas-vindas** — explique em uma frase: "A Âncora é o seu assistente de retenção: ela cuida da
   sua carteira de clientes recorrentes pra ninguém cancelar por descuido — te avisa quem está em
   risco, quem renova em breve e quem já pode crescer com você."

2. **Nome e negócio** — "Como você se chama? E o que o seu negócio faz?" (ex.: agência de tráfego,
   clínica, consultoria, contabilidade, escritório, prestador de serviço).

3. **Como você cobra os clientes recorrentes** — "Seus clientes pagam por mês, por trimestre ou por
   ano, na maioria?" (Guarde o ciclo padrão: mensal / trimestral / anual — só o mais comum; cada
   cliente pode ter o seu depois.)

4. **Canal preferido de contato** — "Quando você fala com cliente, é mais por **WhatsApp** ou
   **e-mail**?" (As mensagens que eu sugerir vão sair no jeito desse canal.)

5. **Tom de voz** — "Você fala com cliente de um jeito mais **formal**, mais **próximo/informal** ou
   **bem descontraído**?" (Para eu escrever as mensagens do seu jeito.)

6. **Lembrete honesto** — diga: "Eu **nunca invento** número, resultado ou sinal — sempre te
   pergunto. As contas (saúde, renovação, se vale salvar) são feitas por um motor exato. Seus dados
   ficam **só no seu computador**, numa pasta `.ancora/`. E eu **sugiro** as mensagens — quem manda
   é você. Combinado?"

## Ao final — escreva `.ancora/config.md` (crie a pasta `.ancora/` se não existir)

```markdown
# Configuração da Âncora

- **Dono (como chamar):** <nome>
- **Negócio:** <o que faz>
- **Ciclo padrão:** <mensal | trimestral | anual>
- **Canal preferido:** <whatsapp | email>
- **Tom de voz:** <formal | próximo | descontraído>
- **Configurado em:** <DD/MM/AAAA>

## Observações
- A Âncora nunca inventa número/resultado/sinal — sempre pergunta.
- As contas (saúde, radar de renovação, EV do resgate, painel) são feitas pelo motor `ancora.py`.
- Dados 100% locais em `.ancora/`. Nada vai para a internet.
- A Âncora sugere as mensagens; quem envia é o dono (WhatsApp na frente).
- Só expande cliente saudável; no resgate, se não vale a pena, deixa ir com dignidade.
```

## Depois de escrever o config, execute nesta ordem
1. `python3 scripts/ancora.py init`
2. Garanta o `.gitignore` (a pasta `.ancora/` não pode ir para o Git):
   - se houver `.gitignore` na raiz do projeto, garanta a linha `.ancora/`;
   - se não houver, crie um com `.ancora/`.
3. **Apague a pasta `setup/`** desta skill — a Âncora instalada fica limpa. (`rm -rf setup`)

## Primeiro valor entregue (faça já)
Convide o dono a montar a **carteira** agora, no modo **Carteira**: "me conta 2 ou 3 clientes fixos
seus — nome, o que você faz pra cada um, quanto cobra e quando renova — que eu já monto o seu painel
de retenção." Cadastre com `cliente-add`, rode uma avaliação de **saúde** de cada um e mostre o
**painel** (`painel`). Ver a carteira inteira com semáforo, MRR e quem renova primeiro é o momento
"uau" da Âncora.
