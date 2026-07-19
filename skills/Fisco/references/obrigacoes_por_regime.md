# Obrigações-padrão por regime — para montar o calendário (guia da IA)

Use esta lista para **sugerir** as obrigações a cadastrar no calendário (modo 3) conforme
o regime do dono. Estas são as obrigações mais comuns — **não é lista fechada** e prazos
podem mudar (feriado, regra municipal, mudança de norma). **Sempre** diga ao dono para
**confirmar prazos e a lista completa com o contador**. Cadastre com o motor:

```
python3 scripts/fisco.py add --obrig "<nome>" --freq <mensal|bimestral|trimestral|anual|unico> [--dia N | --data DD/MM] --cat <categoria>
```

Não invente vencimentos além dos consagrados abaixo; quando não tiver certeza do dia,
cadastre e escreva na `--obs` "confirmar dia com o contador".

---

## MEI

- **DAS-MEI** — valor fixo mensal. `--freq mensal --dia 20 --cat Imposto`
  (obs: valor fixo, não é % do faturamento; confirmar o dia com o contador).
- **DASN-SIMEI** — declaração anual do MEI, costuma vencer **31/05**.
  `--freq anual --data 31/05 --cat Declaracao`

## Simples Nacional

- **DAS Simples Nacional** — guia mensal. `--freq mensal --dia 20 --cat Imposto`
- **DEFIS** — declaração anual do Simples, costuma vencer **31/03**.
  `--freq anual --data 31/03 --cat Declaracao`
- Se tem funcionário: **FGTS** e **INSS/DCTFWeb** mensais, e envio do **eSocial/folha** —
  cadastre como mensais e confirme os dias com o contador. `--cat Trabalhista`

## Lucro Presumido

- **PIS** e **COFINS** — mensais. `--freq mensal --cat Imposto` (obs: confirmar dia)
- **ISS** — municipal, mensal (dia varia por cidade). `--freq mensal --cat Imposto`
  (obs: confirmar o dia na prefeitura/contador)
- **IRPJ e CSLL** — apuração **trimestral**. `--freq trimestral --data <1ª data> --cat Imposto`
- **DCTF** — obrigação acessória (mensal/conforme regra). `--cat Declaracao`
- Se tem funcionário: **FGTS**, **INSS/DCTFWeb**, **eSocial** mensais. `--cat Trabalhista`

## Lucro Real

- Semelhante ao Presumido em PIS/COFINS/ISS/folha, **+** apuração de **IRPJ/CSLL** (mensal
  por estimativa ou trimestral) e **EFD-Contribuições/ECD/ECF**. É o regime mais pesado em
  obrigação acessória — **peça a lista exata ao contador** e cadastre o que ele indicar.

---

## Reforma Tributária (todos os regimes do regime regular)

- A partir de **agosto/2026**: preencher os **campos de IBS/CBS na nota fiscal** vira
  obrigatório para o regime regular. Cadastre um lembrete:
  `--obrig "Conferir campos IBS/CBS na nota (Reforma)" --freq unico --data 01/08/2026 --cat Reforma`
  (obs: confirmar com o contador se o seu emissor já está adaptado).

---

## Como você (IA) deve conduzir

1. Depois do setup, **ofereça** cadastrar as obrigações-padrão do regime do dono ("quer que
   eu já monte seu calendário com o DAS e a declaração anual?").
2. Cadastre só o que se aplica; para os dias que variam (ISS, folha), use a `--obs` pedindo
   confirmação com o contador.
3. Depois, rode `python3 scripts/fisco.py agenda --dias 60` e leia em voz simples o que vem
   primeiro.
4. **O calendário começa olhando pra frente.** Uma obrigação recém-cadastrada mostra a
   **próxima** ocorrência (não acusa atraso de um mês passado que o Fisco não tem como saber
   se você pagou). Quando o dono paga/entrega uma competência, use `concluir --id N` — a
   partir daí, se um vencimento passar sem baixa, o motor marca 🔴 vencida sozinho. Se o dono
   disser que **já está atrasado** em algo, registre e oriente falar com o contador — não
   invente o atraso.
5. **Sempre** feche: "essa é a lista comum do seu regime; confirme com o contador se falta
   alguma coisa específica do seu caso".
