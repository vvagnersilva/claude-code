# Primeira execução — configurar a Fachada

Este roteiro roda UMA vez, na primeira conversa. Ao terminar, ele se autodestrói.

## Passo a passo

### 1. Dê as boas-vindas (em uma linha)

> "Vamos montar o site do seu negócio. Primeiro preciso te conhecer — são só algumas perguntas rápidas."

### 2. Colete, em conversa natural (não como formulário):

1. **Nome do negócio**
2. **O que o negócio faz** (uma frase — detecte o arquétipo pela tabela de `references/entrevista.md`)
3. **Região atendida** (cidade/bairros, "cliente vem até mim" ou "online")
4. **Cliente ideal** (quem procura o negócio)
5. **Diferencial** (o que faz melhor que os concorrentes — ajude com exemplos se travar)
6. **WhatsApp do negócio** (com DDD — vira o botão principal do site)
7. **Telefone fixo, e-mail, endereço e horários** (o que existir)
8. **Tom de voz**: mais próximo ("você") ou mais formal ("o senhor/a senhora")?
9. **Materiais**: tem logo? fotos reais? cores da marca? (se sim, pedir para colocar em `fachada-site/imagens/`)

Se o usuário responder várias de uma vez, reconheça e não repita perguntas.

### 3. Grave a configuração

Crie `.fachada/config.md` no projeto com este formato:

```markdown
# Fachada — configuração do negócio
atualizado: [data de hoje]

## Negócio
- Nome: [nome]
- Ramo: [o que faz, uma frase]
- Arquétipo: [um dos 8 de references/entrevista.md]
- Região: [área atendida]
- Cliente ideal: [descrição curta]
- Diferencial: [o que o dono disse]

## Contato
- WhatsApp: [55 + DDD + número, só dígitos]
- Telefone: [se houver]
- E-mail: [se houver]
- Endereço: [se houver]
- Horários: [se houver]
- Instagram/redes: [se houver]

## Estilo
- Tom: [você | senhor(a)]
- Direção de design: [preencher no modo Montar]
- Cores da marca: [se existirem]
- Logo: [caminho em fachada-site/imagens/ ou "não tem"]

## Provas reais (só o confirmado pelo dono)
- Anos de mercado: [ ]
- Registro/certificação: [ ]
- Depoimentos disponíveis: [sim/não]
```

### 4. Proteja os dados

Adicione `.fachada/` ao `.gitignore` do projeto (crie o arquivo se não existir).

### 5. Autodestruição do setup

1. Apague a pasta `setup/` desta skill (`rm -rf` da pasta `setup/` dentro da pasta da skill Fachada).
2. Abra o `SKILL.md` da skill e remova a seção "## Setup de primeira execução" inteira.
3. Confirme para o usuário em uma linha: "Configuração salva. Vamos ao site."

### 6. Emende no fluxo normal

Siga direto para o modo **Entrevista** (só as perguntas do arquétipo que faltarem) e depois **Montar** — sem pedir permissão para continuar.
