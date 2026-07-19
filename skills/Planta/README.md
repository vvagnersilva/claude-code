# Planta 📐 — a planta do projeto antes de construir

**Planta** é uma skill de Claude Code para quem **entrega automação e IA para
clientes** — agência, consultor ou freelancer de IA. Ela pega um cliente real e
te leva do **briefing** até a **entrega**, com tudo organizado e na sua máquina.

Você fecha um cliente e trava em "como escopo, desenho, orço e entrego isso sem me
enrolar?". A Planta resolve exatamente esse miolo.

## O que ela faz (7 modos)

1. **Briefing** — entrevista de levantamento: o processo do cliente, a dor, as
   ferramentas que ele já tem, o volume e o resultado que ele quer.
2. **Mapear** — mapa do processo atual, gargalos e a métrica a mover (de X para Y).
3. **Desenhar** — o blueprint da **automação mínima viável**, casada com o que o
   cliente já usa (sem over-engineering).
4. **Escopo** — esforço, prazo, fases e complexidade, com **o que está dentro ×
   o que está fora** (trava o escopo).
5. **ROI & Investimento** — quanto o cliente economiza, o piso de investimento e
   o payback. Sem preço mágico.
6. **Proposta** — proposta comercial de uma página (HTML → PDF), com a sua marca,
   na língua do cliente.
7. **Entrega** — checklist de build, teste real e handoff (com treinamento).

## Como instalar

1. Baixe e descompacte o arquivo.
2. Copie a pasta `Planta` para dentro de `.claude/skills/` do seu projeto
   (ou de `~/.claude/skills/` para usar em qualquer projeto):

   ```
   .claude/skills/Planta/
   ```
3. Abra o Claude Code nessa pasta.

## Como usar

Na **primeira vez**, a Planta faz uma conversa rápida de configuração (seu nome,
agência, cor da marca, seu custo-hora, ferramentas, tom de voz) e guarda em
`.planta/config.md`. Depois disso é só conversar:

- *"Fechei um cliente, uma clínica que perde paciente por falta de confirmação. Me
  ajuda a fazer o briefing."*
- *"Mapeia o processo desse cliente e me mostra os gargalos."*
- *"Desenha a solução mais simples pra isso."*
- *"Escopa o projeto e me diz o prazo."*
- *"Qual o ROI? Como justifico o preço?"*
- *"Monta a proposta pra eu mandar pro cliente."*
- *"Monta o checklist de entrega."*

Você fala em português normal. A Planta desenha, calcula e escreve; **você fala
com o cliente, fecha o preço e constrói**.

## O que esperar (regras de ouro)

- **Nunca inventa** o processo, os números ou as ferramentas do cliente — o que é
  suposição aparece marcado como `[CONFIRMAR]`.
- **Nunca orça antes de descobrir** — primeiro o briefing e o mapa, depois o preço.
- **Sempre a solução mais simples que resolve** — nada de complexidade à toa.
- **Trava o escopo** (dentro × fora) pra você não estourar margem.
- **Você decide e entrega** — a Planta é o plano, não a obra.
- **Dados 100% locais** — tudo fica na pasta `.planta/` da sua máquina.

## Privacidade

A Planta não usa nenhuma conta, chave de API ou serviço externo. Tudo roda na sua
máquina e os dados dos seus clientes ficam só com você.

## Licença

MIT — use, adapte e compartilhe.
