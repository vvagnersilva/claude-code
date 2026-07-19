# Primeira conversa da Lupa (só na primeira vez)

Rode isto **uma única vez**, quando `.lupa/config.md` ainda não existir. É uma
conversa curta e leve para a Lupa te conhecer. Depois dela, a pasta `setup/`
se apaga sozinha.

## Como conduzir

Fale como um colega prestativo, não como um formulário. Faça as perguntas em
linguagem natural, uma de cada vez ou em pequenos blocos. Se o usuário já tiver
dado alguma informação no pedido inicial, **não pergunte de novo** — aproveite.

Colete:

1. **Como prefere ser chamado?** (primeiro nome ou apelido)
2. **Qual sua profissão ou área?** (ex.: advogado, contador, perito, engenheiro,
   corretor, gestor — serve para a Lupa usar exemplos e termos do seu mundo)
3. **Que tipos de documento você mais analisa?** (ex.: contratos de prestação de
   serviço, contratos bancários, laudos, relatórios contábeis, processos,
   propostas, NDAs)
4. **Nível de rigor:** prefere que a Lupa aponte **até o menor detalhe**
   (conservador) ou só **o que realmente importa** (equilibrado)?

> Nota de boas-vindas para dizer ao usuário: a Lupa lê o documento, mostra o
> trecho de tudo que aponta e **nunca inventa** — o que não estiver no texto, ela
> diz que não encontrou. Ela é apoio à leitura, não substitui o parecer de um
> profissional habilitado. E o documento fica **só na sua máquina**.

## O que gravar

Crie o arquivo **`.lupa/config.md`** na pasta atual com este conteúdo (preencha
com as respostas, mantendo os acentos):

```markdown
# Configuração da Lupa

- **Nome:** <como chamar>
- **Profissão/área:** <profissão>
- **Documentos mais analisados:** <lista>
- **Nível de rigor:** <conservador | equilibrado>

<!-- A Lupa lê estes ajustes no início de cada análise. Edite quando quiser. -->
```

Depois:

1. Se a pasta atual tiver um repositório git (existe `.git`), garanta que o
   arquivo **`.gitignore`** contenha a linha `.lupa/` (crie o `.gitignore` se não
   existir) — os documentos e dados do usuário são sigilosos e não devem ir para
   o controle de versão.
2. **Apague a pasta `setup/` inteira desta skill** — ela só serve para a primeira
   vez. (Remova `setup/PRIMEIRA_CONVERSA.md` e a pasta `setup/`.)
3. Confirme para o usuário em uma frase que está tudo pronto e mostre o que a Lupa
   sabe fazer (resumir, achar riscos, extrair prazos, comparar versões, responder
   perguntas do documento, conferir completude). Pergunte qual documento ele quer
   analisar primeiro.
