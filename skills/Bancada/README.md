# Bancada — ensine uma vez, use sempre

A **Bancada** é uma skill para Claude Code que transforma as suas tarefas
repetitivas em **receitas** reutilizáveis. Você ensina uma tarefa **uma vez**
(conversando, em português) e a Bancada repete sempre no mesmo padrão e no seu
tom — sem você precisar reexplicar do zero, sem código e sem montar fluxo no n8n.

Com o tempo você acumula uma **bancada de rotinas próprias**: as suas
ferramentas, feitas sob medida para o seu negócio.

## Para quem é

Donos de negócio de serviço e profissionais que fazem **a mesma tarefa toda
hora** — o mesmo tipo de e-mail, o mesmo resumo, a mesma resposta padrão, a mesma
formatação — e cansam de explicar tudo de novo cada vez. Não precisa saber
programar.

## O que ela faz

- **Ensinar** — você descreve uma tarefa que repete sempre; a Bancada guarda como
  uma receita (entrada, passos, formato de saída, tom, exemplos).
- **Rodar** — você cola uma entrada nova e pede para rodar; a tarefa sai pronta no
  seu padrão.
- **Listar** — veja todas as rotinas que você já ensinou.
- **Melhorar** — todo feedback ("encurta", "sempre inclua minha assinatura") entra
  na receita; ela fica cada vez mais a sua cara.
- **Editar / Remover** — ajuste ou apague uma receita quando quiser.
- **Painel** — veja quantas receitas tem e quais você mais usa, e peça sugestões
  de novas rotinas para botar na bancada.

## Como instalar

1. Baixe e descompacte o arquivo `Bancada.zip`.
2. Copie a pasta `Bancada` para dentro de `.claude/skills/` do seu projeto (ou
   para `~/.claude/skills/Bancada` para usar em qualquer lugar). O caminho final
   fica assim:

   ```
   .claude/skills/Bancada/
   ├── SKILL.md
   ├── scripts/bancada.py
   ├── references/
   └── setup/
   ```

3. Abra o Claude Code nessa pasta. Na primeira vez, é só dizer algo como
   **"quero ensinar uma rotina pra você"** — a Bancada faz uma conversa rápida de
   configuração e já cria a sua primeira receita.

## Como usar (você só conversa)

Você nunca digita comando nem código — só fala em português. Exemplos:

- "Tem uma coisa que eu faço toda semana, queria te ensinar." → modo **Ensinar**
- "Roda minha receita de resposta de orçamento com esse pedido aqui: …" → **Rodar**
- "Quais rotinas você já sabe fazer pra mim?" → **Listar**
- "Ficou ótimo, mas da próxima já põe minha assinatura." → **Melhorar**

Por baixo, a Bancada usa um pequeno programa em Python (já incluso, só biblioteca
padrão) para guardar e organizar as receitas. Você só conversa.

## Privacidade

Tudo fica na **sua** máquina, na pasta `.bancada/` do seu projeto. Nada é enviado
para fora, nenhuma conta, nenhuma chave de API, nenhuma internet necessária. A
Bancada **gera** o resultado; quem revisa e envia é sempre você.

## Requisitos

- Claude Code instalado.
- Python 3 (já vem no macOS e na maioria dos sistemas). Nada mais para instalar.

## Licença

MIT — veja o arquivo `LICENSE`.
