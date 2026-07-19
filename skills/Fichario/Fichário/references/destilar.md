# Como destilar (revisar para ficar mais afiado, não maior)

Toda base de conhecimento envelhece e incha. O Fichário tem uma rotina para o contrário: ficar **menor e mais confiante** com o tempo. A pergunta que guia tudo é uma só:

> **O que aqui ainda é verdade pra você?**

## Quando destilar
- Quando o dono pedir "revisar meu fichário", "limpar minhas anotações", "o que eu posso juntar".
- De vez em quando, sozinho: rode `revisar --dias 30` e ofereça uma destilada.

## O passo a passo
1. Rode `python3 "<...>/fichario.py" revisar --dias 30`. Ele lista:
   - **Cartões esquecidos** (não revisados há 30+ dias).
   - **Possíveis cartões repetidos** (pares muito parecidos).
2. Para cada **cartão esquecido**, pergunte ao dono: *"Isso ainda é verdade pra você? Quer manter, atualizar ou aposentar?"*
   - Mantém → `revisado --id <id>` (marca revisado hoje).
   - Mudou → `editar --id <id> --corpo-stdin` (corpo novo por stdin), depois `revisado`.
   - Não vale mais → `remover --id <id>`.
3. Para cada **par repetido**, proponha **fundir num só cartão mais nítido**:
   - Escreva um cartão novo que junte o melhor dos dois, nas palavras do dono.
   - Grave o novo (`guardar`), reconecte se precisar, e remova os dois antigos (`remover`).
4. Ao final, mostre o **placar da destilada**: quantos cartões foram mantidos, atualizados, fundidos e aposentados. O bom sinal é **menos cartões e mais clareza**.

## Promover ideia a regra (opcional, poderoso)
Se uma ideia se repete e o dono confirma que virou um princípio dele, deixe isso explícito no título/corpo: de "acho que responder rápido ajuda" para "**regra minha:** respondo todo cliente em até 1 hora". A base vai virando o manual de princípios do dono.

## Regra de ouro da destilada
Destilar **aumenta o sinal**, não o volume. Se ao final você tem **mais** cartões dizendo a mesma coisa, fez errado. O objetivo é uma base enxuta em que o dono confia.
