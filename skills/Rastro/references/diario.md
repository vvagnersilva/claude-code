# Diário de bugs — a memória que compõe

O diário é o que separa depurar duas vezes o mesmo problema de resolvê-lo uma vez e nunca
mais. É a maior economia de tokens de longo prazo do Rastro: em vez de a IA redescobrir do
zero um bug que você já matou há três semanas, ela **recupera** a causa-raiz e a correção em
segundos.

O motor é `scripts/rastro.py` — 100% offline, só stdlib, ancora a pasta `.rastro/` na raiz
do projeto sozinho. A IA depura seguindo o método; o motor só guarda o exato e recupera.

## O reflexo mais importante: buscar ANTES de investigar
No começo de todo bug, antes de qualquer investigação:
```
python3 scripts/rastro.py buscar "<palavras do sintoma ou da mensagem de erro>"
```
- Se voltar um bug parecido (**"JÁ VI ALGO PARECIDO"**), leia a causa-raiz e a correção dele
  e comece por ali — pode ser o mesmo bug ou um primo.
- Se voltar **"confiança baixa"** ou nada, provavelmente é novo — investigue do zero.

O `buscar` compara por sobreposição de palavras (sem acento, mantendo identificadores de
código como pistas) sobre título + sintoma + causa + tags + arquivos, com um portão de
confiança (match fraco não conta como "achei").

## Registrar (no fim de cada bug, no modo Blindar)
```
python3 scripts/rastro.py registrar \
  --titulo "..."        # curto, o nome do bug \
  --sintoma "..."       # o que aparecia / a mensagem de erro \
  --causa "..."         # a causa-raiz de verdade (não o sintoma) \
  --correcao "..."      # o que resolveu, na origem \
  --arquivos "a.js,b.py"  # arquivos tocados (vira sinal de recorrência) \
  --severidade P0|P1|P2|P3 \
  --status corrigido|verificado \
  --tags "auth,token"   # assuntos, viram sinal de recorrência
```
Escreva a **causa-raiz específica**, não "travou". "Trava porque `user` é null quando o
middleware não trata requisição sem login" é o que vai te salvar no futuro.

## Consultar e manter
- `listar [--status corrigido|verificado|aberto]` — todos os bugs, mais recentes primeiro.
- `ver <id>` — um bug inteiro (ex.: `ver 20260718-001`).
- `status <id> verificado` — promove de corrigido para verificado depois de rodar de verdade.
- `stats` — o painel: total, por severidade, por status, e **assuntos/arquivos recorrentes**.
- `onde` — mostra em qual pasta o `.rastro/` foi ancorado (útil se a recuperação vier vazia).

## O painel aponta dívida técnica
O `stats` marca **assuntos** (tags) e **arquivos** com **2 ou mais bugs** como recorrentes.
Um mesmo arquivo que quebra toda semana, ou um mesmo assunto ("auth", "parser") que volta,
não é azar — é candidato a **refatoração de causa-raiz estrutural**. O diário transforma
bugs individuais num mapa de onde o projeto está frágil.

## Privacidade
Tudo fica em `.rastro/` na raiz do seu projeto, no seu computador. Nada é enviado para fora.
O `.rastro/` é ignorado pelo git (o setup cuida disso) — seu histórico de bugs é seu.
