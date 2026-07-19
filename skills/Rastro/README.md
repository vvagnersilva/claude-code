# Rastro 🐛🔦

**Caça-bug metódico para quem constrói software com IA.** Em vez de chutar correção quando o
código quebra, o Rastro segue o *rastro* do erro até a causa-raiz — reproduzir, observar o
runtime real, achar o porquê, corrigir o mínimo, verificar e blindar contra regressão. Menos
tempo, menos bug novo e **muito menos token queimado** naquele loop em que cada conserto
quebra outra coisa.

> A Lei de Ferro: **não existe correção antes de investigar a causa-raiz.** Consertar o
> sintoma é falhar.

## O que ele faz (6 modos)
1. **Depurar** — o loop completo para um bug: pare/triagem → reproduzir → evidência → causa-raiz → uma hipótese → correção mínima → verificar → blindar.
2. **Reproduzir** — transforma "às vezes quebra" em passos fixos + um teste que a IA pode rodar.
3. **Causa-raiz** — 5 porquês, Portão da Causa-Raiz (o teste do paliativo), rastrear o fluxo de dados e a matriz ACH para bugs teimosos.
4. **Sair do loop** — o modo de emergência: nomeia o anti-padrão, roda o protocolo de resgate e aplica a regra das 3 quedas (3 correções falharam → é a arquitetura, não mais um patch).
5. **Blindar** — verificar de verdade, escrever a guarda de regressão, limpar a instrumentação de debug e explicar por que funciona.
6. **Diário** — registra cada bug resolvido (sintoma → causa-raiz → correção) para nunca depurar o mesmo problema duas vezes; `buscar` recupera "já vi esse erro antes?".

## Instalação
1. Descompacte o `Rastro.zip`.
2. Copie a pasta `Rastro` para dentro de `.claude/skills/` do seu projeto (ou de `~/.claude/skills/` para usar em todos os projetos):
   ```
   .claude/skills/Rastro/
   ```
3. Abra o Claude Code na pasta do seu projeto. Na primeira vez, peça algo como *"configura o Rastro"* — ele roda um setup de 1 minuto (linguagem, comando de teste, como rodar o app) e grava `.rastro/config.md` na raiz do projeto. Depois disso, a pasta de setup se autodestrói.

## Como usar
Você só **conversa**, em português. Exemplos do que dizer:
- *"tá dando erro 500 quando eu salvo o formulário, me ajuda a achar a causa"*
- *"o teste tal está falhando e não sei por quê"* (cole o erro)
- *"a IA ficou em loop tentando consertar esse bug, tá quebrando tudo — para o loop"*
- *"achei que era o cache, mas não resolveu; vamos investigar direito"*
- *"já vi esse erro antes?"* (consulta o diário)

Por baixo, o Claude roda o método e o motor local (`scripts/rastro.py`, só stdlib, offline)
guarda o diário de bugs. Você aprova a correção; o Rastro nunca conserta no escuro.

## As travas de ouro
- Nunca conserta sem reproduzir e entender a causa-raiz.
- Nunca chuta a partir do código-fonte — observa o valor real em execução.
- Uma mudança por vez, a menor possível; nunca empilha patch sobre patch.
- Nunca inventa dado/log/comportamento — só o que rodou de verdade.
- Toda instrumentação de debug é marcada e removida no fim.
- Toda correção termina com guarda de regressão + registro no diário.
- Dados 100% locais — nada sai do seu computador.

## Quando NÃO usar
Erro de sintaxe (o linter já disse), typo óbvio, "onde está X definido?" (é busca, não
depuração) ou funcionalidade que falta (é planejamento). Para esses, resolva direto.

## Requisitos
- Claude Code.
- Python 3 (só a biblioteca padrão — sem instalar nada, sem internet, sem chave de API).

## Licença
MIT. Uso livre.
