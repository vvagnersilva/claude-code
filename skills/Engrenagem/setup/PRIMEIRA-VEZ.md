# Primeira vez com a Engrenagem (configuracao guiada)

Estas instrucoes sao para o Claude conduzir UMA conversa rapida de configuracao
na primeira vez que a pessoa usa a Engrenagem. Demora ~2 minutos.

## Quando rodar
Sempre que NAO existir o arquivo `.engrenagem/config.md` na raiz do projeto.
Se ele ja existir, pule tudo isto e va direto para o trabalho.

## Como conduzir
Fale como um consultor simpatico e direto, em PORTUGUES, sem jargao tecnico.
Faca UMA pergunta de cada vez. Aceite respostas curtas. Se a pessoa nao souber
um numero, ofereca uma estimativa razoavel e siga.

Colete:

1. **Sobre o negocio** — "Me conta em uma frase o que voce faz e qual o seu negocio."
   (ex.: "tenho uma clinica de fisioterapia", "sou contador", "tenho uma barbearia")

2. **Quanto vale 1 hora do seu tempo (custo_hora)** — "So pra eu calcular o quanto
   voce ganha automatizando: quanto vale, mais ou menos, 1 hora do seu tempo em reais?
   Se nao souber, eu chuto a partir do quanto voce fatura por mes."
   (Se a pessoa der o faturamento mensal, estime: faturamento / 160 horas. Guarde um numero.)

3. **Equipe** — "Voce toca sozinho ou tem equipe? Quantas pessoas?"

4. **Ferramentas que ja usa** — "Quais dessas voce ja usa hoje? WhatsApp Business,
   planilhas (Google Sheets/Excel), algum CRM, n8n/Make/Zapier, ou so o Claude mesmo?"

5. **Nivel tecnico** — "Numa escala simples: voce se vira sozinho montando coisas
   tecnicas (1 = nem pensar, prefiro o mais simples / 2 = me viro / 3 = manjo de codigo)?"
   (Isso calibra: nivel 1-2 = sugerir abordagens simples; nunca empurrar n8n para quem nao usa.)

6. **Tom das mensagens** — "Quando eu te ajudar a escrever mensagens pra cliente,
   prefere um tom mais formal ou mais proximo/informal?"

## Gravar a configuracao
Crie o arquivo `.engrenagem/config.md` com este conteudo (preenchido):

```markdown
# Configuracao da Engrenagem

negocio: <descricao em uma linha>
custo_hora: <numero em reais, so o numero>
equipe: <numero de pessoas>
ferramentas: <lista separada por virgula>
nivel_tecnico: <1, 2 ou 3>
tom: <formal | proximo>
```

> Importante: a linha `custo_hora:` precisa ter SO o numero (ex.: `custo_hora: 80`),
> porque o motor de ROI le esse valor.

Depois de gravar, confirme em uma frase: "Pronto, Engrenagem configurada. Bora
mapear onde o seu tempo esta indo?" e ja siga para o modo **Mapear**.

## Autodestruicao (importante)
Assim que o `.engrenagem/config.md` for gravado com sucesso, a configuracao acabou.
A skill deve **apagar a pasta `setup/`** inteira (este arquivo) para deixar a
instalacao limpa — ela so serve uma vez. Nunca rode esta configuracao de novo se
o `config.md` ja existir.

> Cuidado ao apagar: use o caminho da PROPRIA pasta da skill, nao um caminho
> relativo solto. O alvo e `<pasta-da-skill>/setup` (a pasta que contem este
> arquivo). Confirme com `ls` depois que so sobraram `SKILL.md`, `scripts/`,
> `references/`, `README.md` e `LICENSE` — e que `setup/` sumiu.
