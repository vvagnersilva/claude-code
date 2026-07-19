# Estrutura e tom do relatório de auditoria

O relatório é o **documento que registra a auditoria** — vale como prova do que foi
conferido, do que estava conforme e do que precisa ser corrigido. Gere com `relatorio`
(texto) ou `relatorio-html` (com a marca do usuário, vira PDF imprimindo).

## Estrutura (na ordem)
1. **Cabeçalho** — título da auditoria, organização, marca/logo.
2. **Identificação** — escopo (o que foi auditado), norma/padrão de referência, área, data,
   auditor(a).
3. **Índice de conformidade** — o número-chave (% de conformes entre os aplicáveis) +
   contagem de conformes / parciais / não conformes. Dá a foto em um olhar.
4. **Não-conformidades** — uma a uma, da mais grave para a menos grave, cada uma com:
   - severidade (🔴/🟡/🟢/🔵), descrição objetiva, **evidência**, **causa-raiz** e o
     **plano de ação** (o quê, quem, quando, status).
5. **Pontos conformes / positivos** — registre o que está em ordem (não é só lista de
   problemas; isso dá equilíbrio e crédito ao que funciona).
6. **Conclusão** — leitura geral honesta: o nível de conformidade, os riscos prioritários,
   o prazo de reauditoria sugerido.
7. **Ressalva** — o relatório é de **gestão interna**; não substitui laudo/parecer/
   certificação oficial. Para risco grave ou exigência legal, indicar o responsável técnico.

## Tom
- **Factual e objetivo.** Descreva o que foi observado, não opiniões ("a porta de
  emergência estava trancada às 14h", não "a segurança é uma bagunça").
- **Sem dramatizar nem suavizar.** A severidade já comunica a gravidade.
- **Construtivo.** Cada problema vem com o caminho do conserto (a ação), não só a crítica.
- **PT-BR claro**, sem jargão desnecessário — quem lê pode não ser da área técnica.

## Como eu (a IA) escrevo a conclusão
Eu uso os números reais do motor (índice, contagem de NCs por severidade) e escrevo 2-4
frases: a foto geral, o(s) risco(s) prioritário(s) (as críticas/maiores), e a recomendação
de prazo para reauditar. Nunca invento número — só leio o que está registrado. Se algo
ficou pendente de confirmar, deixo explícito como **[CONFIRMAR]**.
