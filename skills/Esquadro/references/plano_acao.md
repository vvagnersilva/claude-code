# Plano de ação 5W2H

Toda não-conformidade precisa de um plano de ação **concreto, com responsável e prazo** —
senão o conserto não acontece. O formato **5W2H** garante que nada essencial falte.

| Sigla | Pergunta | O que registrar |
|-------|----------|-----------------|
| **What** (O quê) | O que será feito? | A ação, em verbo no infinitivo: "Instalar proteção fixa…" |
| **Why** (Por quê) | Por que fazer? | O risco/objetivo: liga a ação à causa-raiz |
| **Who** (Quem) | Quem é o responsável? | Uma pessoa ou função clara (não "a equipe") |
| **When** (Quando) | Até quando? | Uma data real (DD/MM/AAAA). Sem prazo, não é plano |
| **Where** (Onde) | Onde? | Local/setor/sistema onde a ação acontece |
| **How** (Como) | Como será feito? | O passo a passo ou método |
| **How much** (Quanto) | Quanto custa? | Custo estimado (R$), se houver — ajuda a aprovar |

O motor guarda tudo isso: `acao-add --nc <id> --oque "…" --porque "…" --quem "…"
--quando DD/MM/AAAA --onde "…" --como "…" --quanto "R$ …"`. O **O quê**, o **Quem** e o
**Quando** são o mínimo indispensável — sem prazo, o motor avisa "(sem prazo!)".

## Os três tipos de ação (use os três quando fizer sentido)
1. **Correção imediata** — apaga o incêndio agora (ex.: recolocar a proteção, destrancar a
   saída). Reduz o risco já.
2. **Ação corretiva** — ataca a **causa-raiz** para a NC **não voltar** (ex.: criar o passo
   de verificação no procedimento). É a mais importante.
3. **Ação preventiva** — evita que o mesmo problema apareça em **outros lugares** parecidos
   (ex.: conferir as proteções de todas as máquinas iguais, não só a auditada).

> Uma NC crítica geralmente precisa das três: contém o risco hoje, corrige a causa e
> previne a repetição em outros pontos.

## Boas práticas
- **Uma ação, um dono.** Responsabilidade dividida vira responsabilidade de ninguém.
- **Prazo realista, mas curto para crítica.** Crítica = imediato/interromper; maior = dias
  a poucas semanas; menor = médio prazo (ver `severidade.md`).
- **Verifique a eficácia depois.** Concluir a ação não basta — confirme que a NC não
  voltou (`acao-concluir --eficaz sim|nao`). Se voltou, a causa-raiz estava errada.
- **Acompanhe os prazos.** O motor marca 🔴 VENCIDO / 🟠 VENCE HOJE / 🟡 perto. Use
  `acoes --atrasadas` para cobrar o que passou.

## PDCA (o ciclo por trás disso)
- **P**lanejar: o checklist e o que auditar.
- **D**esenvolver: rodar a auditoria, registrar NCs.
- **C**hecar: o plano de ação foi executado? a NC sumiu?
- **A**gir: padronizar o que funcionou (vira procedimento/checklist) e reauditar.

O Esquadro cobre o ciclo todo: você audita, registra, planeja o conserto, acompanha e
emite o relatório — e na próxima auditoria confere se o que foi corrigido continua conforme.
