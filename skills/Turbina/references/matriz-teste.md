# Matriz de teste — criativos e públicos com método

Guia para o modo **Testar**. Ideia central: anúncio bom se **descobre testando**, não
adivinhando. A Turbina cuida da *estrutura* do teste e da leitura do resultado; a
*escrita* das variações (copy, gancho, roteiro) vai pro **Verbo**.

## A regra número 1: uma variável por vez

Se você troca criativo **e** público **e** oferta no mesmo teste, e o CPA melhora,
você não sabe o que causou — e não consegue repetir. Isole:
- Testando **criativo**? Mesmo público, mesma oferta, só o criativo muda.
- Testando **público**? Mesmo criativo, só o público muda.
- Testando **oferta/página**? Mesmo criativo e público, só o destino muda.

## Montando a matriz

Liste as hipóteses como combinações de três eixos e escolha UM eixo pra variar por vez:

```
ÂNGULO (a promessa/dor)   ×   PÚBLICO   ×   FORMATO
- dor "erra X há anos"        - lookalike    - vídeo curto
- prova social                - interesse    - imagem única
- oferta/benefício direto     - aberto       - carrossel
- comparação/antes-depois     - retargeting  - depoimento
```

Exemplo de rodada 1 (variando **ângulo**, público e formato fixos):
| Anúncio | Ângulo | Público | Formato |
|---|---|---|---|
| A1 | dor "erra X há anos" | Lookalike 1% | vídeo curto |
| A2 | prova social | Lookalike 1% | vídeo curto |
| A3 | oferta direta | Lookalike 1% | vídeo curto |

O vencedor de ângulo passa pra rodada 2 (agora variando **formato**), e assim por diante.

## Quantas variações, quanta verba, por quanto tempo

- **3–4 variações por rodada** é o ponto ideal pra começar (o suficiente pra achar um
  vencedor sem estilhaçar a verba).
- Cada variação precisa de verba pra **sair do aprendizado**: mire ~**50 resultados**
  acumulados antes de julgar, ou **3–4 dias**, o que vier primeiro.
- Se o orçamento não paga isso em 4 variações ao mesmo tempo, teste **menos por vez**.

## Critério de vitória e corte antecipado

Defina ANTES de subir o teste (senão você julga no sentimento):
- **Vitória:** CPA ≤ alvo (ou ROAS ≥ equilíbrio × 1,5) com volume mínimo.
- **Corte antecipado:** se uma variação já gastou **~2× o CPA-alvo sem 1 resultado**,
  ela quase certamente não vira — pode cortar antes de queimar mais. (Isso é o que a
  Turbina marca como 🔴 no diagnóstico.)
- **Empate técnico:** diferença pequena de CPA com pouco dado não é vitória — deixe
  rodar mais ou rode de novo. Não promova ruído a "vencedor".

## Depois do teste

1. Rode o **Diagnóstico** na exportação pra ver o veredito de cada variação.
2. **Guarde o aprendizado** (modo Aprendizados): qual ângulo/público/formato venceu e
   qual fracassou. Isso alimenta a próxima campanha:
   `python3 scripts/turbina.py aprendizado --tipo venceu --o-que "ângulo prova social" --publico "Lookalike 1%" --resultado "CPA R$ 48"`
3. **Escale o vencedor** com as regras de `regras-otimizacao.md` (subida ~20%, escala
   horizontal, proteger o campeão).
4. Comece a próxima rodada variando o **próximo eixo**.

## Handoff pro Verbo (escrita das variações)

A Turbina define **o que testar** (ângulos, quantos, critério). Para **escrever** cada
gancho/headline/roteiro de criativo, encaminhe pro **Verbo** com o contexto:
- o ângulo/promessa de cada variação,
- o público (pra quem é),
- o tom de voz do dono (do `config.md`),
- o formato (vídeo/imagem/carrossel) e onde vai rodar.

O Verbo devolve o texto; a Turbina monta a matriz, lê o resultado e decide o próximo passo.
