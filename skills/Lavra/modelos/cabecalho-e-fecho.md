# Cabeçalho, identificação e fecho (modo Fechar)

Blocos-padrão que emolduram o documento. Preencha o cabeçalho e o fecho com a
identidade que está em `.lavra/config.json`. Mantenha linguagem impessoal.

---

## Cabeçalho (topo do documento)

```
{NOME DO PROFISSIONAL}
{Título/Especialidade} — {Registro/Conselho: ex. CRM-SP 000000}
{Cidade}/{UF}
```

Se o profissional tiver um timbre/logo próprio, o HTML de saída deixa um espaço no
topo para ele colar depois — nunca invente um logo.

---

## Identificação do documento (logo abaixo do cabeçalho)

```
{TIPO DO DOCUMENTO EM CAIXA ALTA}          (ex.: LAUDO TÉCNICO)
Referência/Nº: {se houver}
Data de elaboração: {data}
Objeto/Interessado: {o que/quem}
```

---

## Fecho (fim do documento) — SEMPRE presente

```
Local e data: {Cidade}/{UF}, {data por extenso}.

Documento sob responsabilidade do profissional signatário.
Elaborado com apoio de ferramenta de redação assistida; deve ser revisado
integralmente pelo responsável antes da assinatura.


_______________________________________________
{NOME DO PROFISSIONAL}
{Registro/Conselho}
```

---

## Marca d'água de status

Enquanto o documento não for revisado e assinado pela pessoa, o topo leva a marca:

```
● RASCUNHO — revisar linha a linha antes de assinar ●
```

No modo Fechar, mantenha essa marca. Ela só deve ser retirada pela própria pessoa,
manualmente, no momento em que ela assumir o documento como final.

---

## Exportação HTML pronto-para-PDF

Quando a pessoa quiser um PDF, gere um HTML simples e limpo (fonte serifada para
corpo, títulos claros, margens A4, sem cor forte) que ela abre no navegador e usa
**Imprimir → Salvar como PDF**. Estruture o HTML assim:

- `<header>` com o cabeçalho + a marca de RASCUNHO.
- corpo com as seções na ordem da estrutura da área.
- `<footer>` com o fecho + linha de assinatura.

Não embuta imagens externas nem fontes da internet — só CSS inline e fontes do
sistema, para funcionar offline e imprimir igual em qualquer máquina.
