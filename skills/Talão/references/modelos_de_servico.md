# Como itemizar por tipo de serviço

Guia rápido para não esquecer nada ao montar o orçamento. Para cada tipo, lance os
itens nos quatro grupos: **material**, **mao_de_obra**, **servico**, **custo**.
Pergunte sempre quantidade, unidade e valor unitário — nunca preencha sozinho.

## Instalação / HVAC / ar-condicionado / refrigeração
- **Material**: equipamento (splits, condensadora), tubulação de cobre + isolamento
  (use `--coef` 1.05–1.15 pra sobra), cabos, suportes, dreno, fluido, fixação.
- **Mão de obra**: horas de instalação × valor-hora do técnico; aplique coeficiente
  maior em altura/acesso difícil.
- **Custo**: deslocamento, vácuo/carga, descarte do equipamento antigo, ART/laudo
  se houver.
- Lembre da **manutenção preventiva** como serviço recorrente (orçamento separado).

## Obra / reforma / construção
- **Material**: por etapa (alvenaria, hidráulica, elétrica, acabamento) com
  coeficiente de perda real (azulejo quebra, tinta sobra).
- **Mão de obra**: por equipe/diária ou por m²; some o tempo de mestre/encarregado.
- **Custo**: caçamba/entulho, aluguel de equipamento, andaime, transporte de
  material, taxas/alvará.
- Não caia no "m² × tabela": adicione **fator de dificuldade** via coeficiente.

## Edição de vídeo / audiovisual
- **Mao_de_obra**: horas de edição por vídeo × valor-hora; trate revisões extras
  como item à parte (evita refação infinita de graça).
- **Servico**: pacotes (ex.: "10 Reels editados"), trilha/licença, motion/legendas.
- **Custo**: armazenamento, banco de mídia, software, transferência de arquivos.

## Marketing / tráfego / design / consultoria
- **Servico**: o entregável (campanha, criativos, gestão mensal, diagnóstico) —
  geralmente por pacote ou mensal (use `--parcelas` ou orçamentos recorrentes).
- **Mao_de_obra**: horas de estratégia/atendimento quando cobradas à parte.
- **Custo**: ferramentas (não confunda com a **verba de anúncio**, que é do
  cliente e fica fora do seu orçamento — deixe isso explícito nas observações).

## Manutenção / assistência técnica
- **Material**: peças trocadas (com coeficiente se houver perda).
- **Mao_de_obra**: hora técnica × tempo; visita técnica mínima como item.
- **Custo**: deslocamento, diagnóstico, garantia do serviço (mencione o prazo nas
  observações).

## Eventos / fotografia / serviços por dia
- **Servico**: a diária/pacote principal.
- **Mao_de_obra**: equipe extra, horas de pós-produção.
- **Custo**: deslocamento, alimentação, locação de equipamento, seguro.

## Dicas universais
- Sempre inclua **deslocamento** e **tempo de planejamento/compra** como `custo` ou
  `mao_de_obra` — é tempo real que quase ninguém cobra.
- Use **observações** (`--obs` no `novo`/`editar`) para deixar claro o que está
  **fora** do orçamento (ex.: "não inclui alvenaria", "verba de anúncio à parte").
- Quando o trabalho tem fases, faça itens por fase para o cliente entender o que
  paga em cada etapa.
