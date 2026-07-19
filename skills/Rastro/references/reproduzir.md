# Reproduzir — o portão de entrada

**Se você não consegue reproduzir, você não consegue consertar.** Reproduzir não é
burocracia: é o que transforma "às vezes quebra" em um alvo fixo que você pode atacar e,
depois, confirmar que morreu. Este é o portão — o modo Depurar não passa daqui sem ele.

## O objetivo
Sair de uma descrição vaga ("tá dando erro", "não funciona", "às vezes trava") para:
1. **Passos exatos** que disparam o bug de forma confiável.
2. **Uma checagem que o Claude pode rodar sozinho** (o comando de teste/build do config, ou
   uma verificação observável). Sem uma checagem que fecha o ciclo, o loop de correção nunca
   fecha — a IA fica adivinhando se resolveu.

## Passo a passo
1. **Colha o sintoma literal.** A mensagem de erro exata (copie o stack trace inteiro), o
   comportamento observado, ou um print da tela. Nada de paráfrase.
2. **Descubra o gatilho.** Pergunte ao dono (ou teste você mesmo): o que exatamente você fez
   antes do erro? Com qual entrada? Em qual tela/rota? Logado como quem?
3. **Reduza ao menor caso.** Vá cortando: acontece com qualquer entrada ou só com aquela?
   Em qualquer usuário ou só num? Sempre ou só depois de um passo anterior? O menor caso que
   ainda quebra é ouro — ele aponta a causa.
4. **Classifique:** é **consistente** (quebra toda vez com os mesmos passos) ou
   **intermitente** (só às vezes)? Intermitente cheira a tempo/concorrência/estado/cache/dado
   externo — anote isso, será evidência no modo Causa-raiz (matriz ACH).
5. **Estabeleça a checagem que dá pra rodar.** De preferência, nesta ordem:
   - o **comando de teste** do projeto (do `.rastro/config.md`) que exercita o cenário;
   - um **teste novo mínimo** que reproduz o bug (vira sua guarda de regressão depois);
   - o **comando de build / checagem de tipos** (se o bug é de compilação/tipo);
   - uma **verificação observável** (uma rota que devolve X, um valor no log, um print da tela para comparar).

## Se NÃO dá pra reproduzir
Não invente e **não conserte no escuro**. Em vez disso:
- Junte mais contexto: logs (`tail` antes de reproduzir), ambiente, versões, dado real de entrada.
- Peça ao dono os passos exatos e o dado que ele usou.
- Adicione instrumentação mínima marcada (`[RASTRO]`) para capturar o estado na próxima vez que acontecer.
- Só volte a propor correção quando conseguir ver o bug acontecer. "Não consigo reproduzir"
  é uma resposta honesta e útil — muito melhor que um chute que vira patch em cima de patch.

## Erros a evitar aqui
- **"Funciona na minha máquina."** Reproduza no ambiente onde falha, não no que é confortável.
- **Depurar em produção.** Reproduza local primeiro — risco de perder dado ou derrubar o serviço.
- **Confiar no resumo do erro.** Leia a saída inteira; a linha que importa costuma estar no meio do stack trace.
