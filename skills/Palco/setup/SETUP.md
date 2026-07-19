# Primeira conversa do Palco (configuração inicial)

Este arquivo guia a **primeira execução**. Quando o dono usar o Palco pela primeira
vez (ou disser "configurar Palco"), conduza esta conversa curta em PT-BR, grave as
respostas em `.palco/config.md` e, ao final, **apague a pasta `setup/`** para que a
skill instalada fique limpa.

## Como conduzir (tom leve, sem jargão)
Faça uma pergunta de cada vez. Se a pessoa não souber algo, registre como "(a definir)"
e siga — nada aqui é obrigatório para começar.

1. **Seu nome e o nome do negócio/empresa** — aparece no rodapé dos slides e no contato.
2. **Para quem você costuma apresentar?** — cliente, diretoria/board, equipe, plateia/palestra.
   (Ajuda a sugerir a estrutura certa depois.)
3. **Tom de voz** — mais formal ("o senhor", corporativo) ou mais próximo ("você", direto)?
4. **Cor da marca** — tem uma cor principal? Pode ser o nome ("azul", "verde") ou o código hex
   (ex.: `#1F6FEB`). Se não tiver, deixe em branco que eu uso a cor do tema.
5. **Logo** — você tem um arquivo de logo (PNG/JPG)? Se sim, me diga o caminho dele; pode ser
   adicionado depois.
6. **Tema visual preferido** — mostre as 5 opções de `references/temas.md` em uma frase cada
   (executivo, consultoria, criativo, técnico, claro) e pergunte qual combina mais. Padrão: `executivo`.
7. **Contato no rodapé** — e-mail/telefone/site que pode aparecer na capa e no encerramento.

## Gravar o config
Crie o arquivo `.palco/config.md` (na raiz do projeto do dono) com este conteúdo,
preenchido com as respostas:

```markdown
# Configuração do Palco
- nome: <nome da pessoa>
- empresa: <nome do negócio>
- publico_tipico: <cliente | board | equipe | plateia>
- tom_de_voz: <formal | proximo>
- cor_marca: <#hex ou nome ou "(a definir)">
- logo: <caminho do arquivo ou "(a definir)">
- tema_padrao: <executivo | consultoria | criativo | tecnico | claro>
- rodape: <contato>
```

Garanta que `.palco/` está no `.gitignore` (os dados são do dono, ficam locais).

## Autodestruição (importante)
Depois de gravar o `.palco/config.md` com sucesso:
1. Confirme para o dono: "Pronto! Configurei o Palco. Quer montar sua primeira apresentação?"
2. **Apague a pasta `setup/` inteira** desta skill (ela só serve para a 1ª vez).
3. A partir daí, sempre leia `.palco/config.md` no início de cada uso para aplicar marca,
   tema e tom automaticamente.
