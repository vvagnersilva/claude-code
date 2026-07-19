# Formatos de saída por modo

Modelos de como estruturar a resposta. Adapte ao documento real — nunca encaixe
informação que o texto não tem. Em todos: **cite o trecho e aponte onde está.**

## Modo Resumir

```
📄 RESUMO — <nome/tipo do documento>

Tipo: <contrato de prestação de serviço / laudo / proposta…>
Partes: <quem e quem>
Vigência: <início → fim, ou data do documento>
Objeto: <o que está sendo acordado/relatado, em 1 frase>

Pontos principais:
• <ponto 1 — claro e curto> (cláusula/seção X)
• <ponto 2> (…)
• <ponto 3> (…)
```

## Modo Riscos

```
🔎 ANÁLISE DE RISCOS — <documento>

🔴 CRÍTICO
• <título do risco>
   Trecho: "<citação do documento>" (cláusula/pág X)
   Por que importa: <explicação em PT-BR simples>
   Sugestão: <o que olhar / perguntar / negociar>

🟡 ATENÇÃO
• <título>  — Trecho: "…" (X) — Por que importa: … — Sugestão: …

🟢 REVISADO E DENTRO DO NORMAL
• <cláusula/aspecto> — padrão, sem problema.

⚠️ Esta é uma leitura de apoio, não um parecer oficial. Para decisões com peso
legal/financeiro, confirme com um profissional habilitado.
```

## Modo Prazos & Obrigações
Saída gerada pelo motor (`lupa.py prazos`) — uma linha por item, ordenada por
data, com 🔴 VENCIDO / 🟠 VENCE HOJE / 🟡 PERTO e a contagem de dias. Depois da
lista, destaque em uma frase os 1–3 itens mais urgentes.

## Modo Comparar

```
🔀 O QUE MUDOU — <documento> (versão antiga → nova)

Mudanças que importam:
• <mudança 1 com peso> — antes: "<trecho A>" · agora: "<trecho B>"
• <mudança 2> — …

Mudanças menores: <resumo em 1 linha, ou "só formatação/redação">
```
(Use o `lupa.py comparar` para a diferença linha a linha e traduza o que importa.)

## Modo Perguntar

```
Pergunta: <a pergunta do usuário>
Resposta: <resposta direta, baseada só no texto>
Onde está: "<trecho citado>" (cláusula/pág X)
```
Se não estiver no documento:
```
Resposta: Não encontrei isso no documento. <opcional: o que mais perto disso
o documento traz, sem deduzir o resto.>
```

## Modo Conferir

```
✅ CONFERÊNCIA DE COMPLETUDE — <documento> (tipo: <…>)

✅ Presente: <itens ok, em lista curta>
⚠️ Incompleto: <item> — <o que está vago/faltando detalhe>
❌ Ausente: <item esperado que não aparece>

Antes de assinar/usar, resolva: <os ⚠️ e ❌ em ordem de importância>
```
