---
name: rastro
description: >
  Depuração metódica de bugs para quem constrói software com IA — segue o RASTRO do
  erro até a causa-raiz em vez de chutar correção. Use SEMPRE que aparecer bug, erro,
  crash, teste falhando, comportamento estranho, "tá quebrado e não sei por quê", "a IA
  ficou em loop tentando consertar", "toda correção quebra outra coisa", 500/404/undefined/
  null/NaN/timeout/stack trace, ou quando estiver prestes a "achar que o problema é X" sem
  ter rodado nada. Também para PARAR o loop que queima tokens: reproduzir → observar o
  runtime real → achar a causa-raiz → correção mínima → verificar → blindar contra
  regressão → registrar no diário. Não conserta sem reproduzir e entender.
---

# Rastro — caça-bug metódico (siga o rastro até a origem)

Quem constrói com IA conhece a cena: o código quebra, você (ou o próprio Claude) começa
a **chutar correções**, mexe em coisa demais, cada conserto quebra outra coisa, e a
assinatura vai embora num loop sem fim. Rastro troca o chute pelo método: **nenhuma
correção antes de reproduzir o bug e achar a causa-raiz.** Menos tempo, menos tokens,
menos bug novo.

> **A Lei de Ferro:** NÃO EXISTE correção antes de investigar a causa-raiz. Consertar o
> sintoma é falhar. (Estudos de campo: método sistemático = 15-30 min e ~95% de acerto de
> primeira; chute aleatório = 2-3 h de sofrimento e ~40%. Projeto sem planejamento gasta
> 4-6× mais tokens.)

## Primeira vez? Faça o setup (1 minuto)
Se ainda **não existe** um arquivo `.rastro/config.md` na raiz do projeto, rode o setup
guiado **antes** de depurar: abra `setup/SETUP.md` nesta skill e siga os passos. Ele
pergunta o essencial (linguagem/stack, **o comando de rodar os testes**, o comando de
build/checagem de tipos, como rodar o app, onde ficam os logs, o tom) e grava
`.rastro/config.md` na raiz do projeto. Saber o "**teste que o Claude pode rodar**" é o
que faz o método inteiro funcionar. Depois de gravar, a pasta `setup/` se autodestrói.
Se o config já existe, pule o setup e vá direto ao modo pedido.

## As travas de ouro (valem em TODOS os modos)
1. **Nunca conserta sem reproduzir + entender a causa-raiz.** Sem reprodução, não há correção.
2. **Nunca chuta a partir do código-fonte.** O código diz o que *deveria* fazer; só o
   runtime diz o que ele *faz*. Observe o valor real (rode, log, breakpoint) — não teorize.
3. **Uma mudança por vez, a menor possível.** Nada de "já que estou aqui" — refatorar no
   meio do conserto cria bug novo.
4. **Nunca empilha correção sobre correção.** 2-3 tentativas falharam? Reverta TUDO, volte
   à investigação, e questione a arquitetura. Empilhar patch é o que queima tokens.
5. **Nunca inventa dado, log, erro ou comportamento.** Só o que rodou de verdade. Se não sabe, diga "não sei ainda" e investigue.
6. **Toda instrumentação de debug é marcada e removida no fim.** Nada de `console.log`/`print` esquecido no código.
7. **Toda correção termina com guarda de regressão + registro no diário** — para o mesmo bug nunca voltar nem ser re-investigado do zero.
8. **Dados 100% locais.** A IA depura e propõe; o dono aprova a correção. Sem enviar código pra fora.

## Antes de investigar: "já vi esse erro?" (economiza mais tokens que tudo)
No começo de QUALQUER bug, recupere o diário — o mesmo erro pode já estar resolvido:
```
python3 scripts/rastro.py buscar "<palavras do sintoma/erro>"
```
Se voltar um bug parecido com causa-raiz + correção, comece por ali. (Rode a partir da
raiz do projeto; o motor ancora `.rastro/` sozinho.)

## Os 6 modos

### 1. Depurar — o coração (o loop inteiro)
O caminho padrão para UM bug, do começo ao fim. Leia `references/loop.md` e conduza as fases,
**sem pular nenhuma**: **PARE/triagem** (severidade P0-P3, escopo pelo `git diff`) →
**Reproduzir** (ver o bug com os próprios olhos + um teste que dá pra rodar) → **Evidência**
(ler o erro inteiro, observar o runtime real, instrumentar o mínimo com marcador) →
**Causa-raiz** (5 porquês + Portão da Causa-Raiz) → **1 hipótese por vez** (matriz ACH se o
bug for teimoso/intermitente) → **Correção mínima** → **Verificar** → **Blindar** (limpar
instrumentação + guarda de regressão + registrar no diário). Anuncie ao dono em que fase está.

### 2. Reproduzir — o portão de entrada
Quando o bug ainda não é reproduzível de forma confiável. Leia `references/reproduzir.md`:
transforme "às vezes quebra" em "quebra quando eu faço X, Y, Z", e defina o **teste que o
Claude pode rodar** (comando de teste, build, ou uma checagem observável). Sem esse portão,
o modo Depurar não avança. Se não dá pra reproduzir, junte mais contexto — **não invente e
não conserte**.

### 3. Causa-raiz — cavar até a origem
As ferramentas para achar o PORQUÊ, não só o QUÊ. Leia `references/causa_raiz.md`: os **5
porquês**, o **Portão da Causa-Raiz** ("se eu remover minha correção, o bug volta? volta →
era só um paliativo; não volta → correção real"), **rastrear o fluxo de dados de trás pra
frente** (o bug está onde o dado PRIMEIRO fica errado, não onde o erro aparece), e a **matriz
ACH** (hipóteses concorrentes × evidências) para bug intermitente ou que resiste a 2+ tentativas.

### 4. Sair do loop — pare de queimar tokens
Quando você (ou a IA) está travado, girando em círculos, e cada conserto quebra outra coisa.
Leia `references/sair_do_loop.md` + `references/anti_padroes.md`: identifique **qual
anti-padrão** está rolando (chute aleatório, visão de túnel, cargo cult, avalanche de prints,
culpar o externo, consertar-antes-de-entender, loop infinito, teorizar do código), rode o
**protocolo de resgate** (pare → reverta TUDO → releia o erro do topo → separe fato de
hipótese → ataque UMA incógnita) e aplique a **regra das 3 quedas** (3 correções falharam →
o problema é a arquitetura, não mais um patch — pare e converse com o dono).

### 5. Blindar — verificar, travar a regressão e limpar
Depois que a correção parece funcionar. Leia `references/blindar.md`: a diferença entre
**Corrigido** e **Verificado** (rodou de verdade?), escrever a **guarda de regressão** (um
teste que FALHA antes e PASSA depois — testando o cenário da causa-raiz, não o sintoma),
**remover toda a instrumentação de debug** (o `git diff` final só pode conter a correção
intencional) e explicar **por que** a correção funciona (se não sabe explicar, não corrigiu).

### 6. Diário — a memória que compõe (motor `rastro.py`)
O registro persistente e local de cada bug resolvido, para **nunca depurar o mesmo problema
duas vezes**. Leia `references/diario.md`. Comandos (sempre a partir da raiz do projeto):
- `python3 scripts/rastro.py registrar --titulo "..." --sintoma "..." --causa "..." --correcao "..." --arquivos "a.js,b.py" --severidade P2 --status corrigido --tags "auth,token"`
- `python3 scripts/rastro.py buscar "token expira"`  → "já vi esse erro antes?"
- `python3 scripts/rastro.py listar [--status corrigido|verificado|aberto]`
- `python3 scripts/rastro.py ver <id>` · `status <id> verificado` · `stats` · `onde`
O `stats` ainda aponta **assuntos e arquivos recorrentes** (>=2 bugs) — sinal de dívida
técnica que vale refatorar. O motor é 100% offline, só stdlib, e ancora `.rastro/` na raiz
do projeto sozinho. A IA depura seguindo o método; o motor só guarda o exato.

## Quando NÃO usar (não gaste método à toa)
- Erro de sintaxe / de compilação → o linter já te disse onde é; corrija direto.
- Typo óbvio (nome de variável errado, operador trocado) visível na leitura → corrija direto.
- "Onde está X definido?" → é busca de código, não depuração de comportamento.
- Não é bug, é funcionalidade que falta → isso é planejamento, não depuração.

## Referências (carregue por necessidade, não todas de uma vez)
- `references/loop.md` — o loop completo das 8 fases (modo Depurar).
- `references/reproduzir.md` — estabelecer reprodução + o "teste que dá pra rodar".
- `references/causa_raiz.md` — 5 porquês, Portão da Causa-Raiz, rastrear fluxo, matriz ACH.
- `references/sair_do_loop.md` — protocolo de resgate + regra das 3 quedas.
- `references/anti_padroes.md` — os anti-padrões nomeados e como sair de cada um.
- `references/blindar.md` — verificação, guarda de regressão e limpeza.
- `references/diario.md` — como usar bem o diário de bugs.
