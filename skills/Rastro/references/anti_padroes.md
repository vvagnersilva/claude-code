# Os anti-padrões — o que parece produtivo mas queima tokens

Cada um destes *parece* que está avançando, mas está girando em falso. Reconheça, nomeie e
saia. A saída de todos é a mesma: voltar ao método (reproduzir → evidência → uma hipótese).

---

### 1. Chute aleatório ("homem bêbado")
**Como aparece:** mudar coisas ao acaso até o bug sumir.
**Por que falha:** mesmo que o bug pare, você não sabe por quê — e pode ter criado outro que só aparece em produção.
**Saída:** toda mudança precisa de uma hipótese. Uma mudança, um teste, de cada vez.

### 2. Visão de túnel ("poste de luz")
**Como aparece:** 30 min no mesmo arquivo porque você "tem certeza" que o bug está ali; ou procurar onde é confortável, não onde o bug está.
**Por que falha:** o sintoma aparece no arquivo A, mas a causa está no B/C ou na interação.
**Saída:** depois de 15 min sem progresso num lugar, pare. Rastreie o fluxo de dados do começo. "Isto é onde o bug ESTÁ ou onde eu SEI OLHAR?"

### 3. Cargo cult
**Como aparece:** copiar uma correção do Stack Overflow / de um bug antigo sem entender por que funciona.
**Por que falha:** pode atacar outra causa, funcionar hoje e quebrar amanhã, e você não sabe explicar.
**Saída:** antes de aplicar, termine a frase "isto corrige porque [mecanismo específico]". Não conseguiu terminar? Você ainda não entendeu.

### 4. Avalanche de prints
**Como aparece:** 30 `console.log`/`print` e sair rolando a saída.
**Por que falha:** barulho demais afoga o sinal; você lê log em vez de entender o código.
**Saída:** 2-3 logs focados nos pontos de decisão, cada um confirmando/refutando UMA hipótese. Marque com `[RASTRO]` e remova no fim.

### 5. Culpar o externo
**Como aparece:** "deve ser a biblioteca", "o framework tem bug", "a API mudou".
**Por que falha:** causa externa é real, mas rara. Começar culpando pula as causas mais prováveis: seu código, sua config, suas suposições.
**Saída:** assuma que o SEU código está errado primeiro. Só culpe o externo depois de verificar o seu E de confirmar que o externo não bate com a própria doc.

### 6. Consertar-antes-de-entender
**Como aparece:** já escrever a correção antes de entender o bug.
**Por que falha:** você conserta a sua suposição, não o bug. Costuma criar problema novo ou mascarar o real.
**Saída:** nenhuma mudança de código até responder "o que exatamente acontece, e por quê?". Evidência vem antes da correção.

### 7. Loop infinito
**Como aparece:** "só mais uma tentativa" repetido 10 vezes com a mesma abordagem.
**Por que falha:** se a abordagem não funcionou em 3 tentativas, a abordagem está errada — mais tentativas não ajudam.
**Saída:** depois de 3 falhas com a mesma estratégia, pare e troque de método (matriz ACH; ou regra das 3 quedas → questione a arquitetura).

### 8. Teorizar a partir do código-fonte
**Como aparece:** "olhando o código, acho que o problema é…" sem ter rodado nada.
**Por que falha:** o código diz o que *deveria* fazer; ~7 de 10 bugs têm causa invisível na leitura (ordem de inicialização, cache velho, null inesperado, tempo/concorrência).
**Saída:** rode e observe o valor real. `p variavel` / breakpoint / log. Observe primeiro, teorize depois.

---

## Bandeiras de que você está num anti-padrão
| Bandeira | Você provavelmente está em |
|---|---|
| "Deixa eu só tentar…" | Chute aleatório |
| "Funcionou pra outra pessoa" | Cargo cult |
| 10+ logs adicionados | Avalanche de prints |
| "Com certeza não é o meu código" | Culpar o externo |
| Mesmo arquivo aberto há 30+ min | Visão de túnel |
| 4ª tentativa com a mesma abordagem | Loop infinito |
| Escrevendo a correção antes de ler o código | Consertar-antes-de-entender |
| "Olhando o código, acho que…" | Teorizar do código-fonte |
