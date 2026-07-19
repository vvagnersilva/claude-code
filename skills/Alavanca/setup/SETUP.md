# Primeira conversa — configurar a Alavanca (roda uma vez só)

Quando o membro usa a Alavanca pela **primeira vez** (ainda não existe o arquivo
`.alavanca/config.md` na pasta dele), conduza esta conversa curta ANTES de qualquer modo.
É rápida, em português, sem nenhum termo técnico. Faça uma pergunta de cada vez, em tom
acolhedor. Se a pessoa não souber responder algo, siga com um padrão razoável e diga que dá
pra ajustar depois.

## Perguntas (uma de cada vez)
1. **Como você quer ser chamado(a)?** (nome ou apelido)
2. **Qual é a sua profissão / o que você faz hoje?** (ex.: dentista, gestor de tráfego,
   contador, confeiteira)
3. **Qual conhecimento ou experiência sua as pessoas mais elogiam ou pedem ajuda?**
   (isso é a matéria-prima do produto)
4. **Você já tem algum público?** (lista de WhatsApp, seguidores, clientes antigos) —
   mais ou menos quantas pessoas você consegue avisar quando quiser?
5. **Quanto vale, hoje, a sua hora de trabalho (mais ou menos)?** (pra calcular preço; pode
   ser uma estimativa)
6. **Você prefere mensagens mais formais ou mais descontraídas?** (define o tom de voz)

## O que fazer com as respostas
Crie a pasta `.alavanca/` e escreva `.alavanca/config.md` com este conteúdo (preenchido):

```markdown
# Configuração da Alavanca
- nome: <resposta 1>
- profissao: <resposta 2>
- expertise_bruta: <resposta 3>
- publico_tamanho: <resposta 4, número aproximado>
- custo_hora: <resposta 5, em R$>
- tom_de_voz: <formal | descontraído, da resposta 6>
- criado_em: <data de hoje>
```

Garanta que exista um arquivo `.gitignore` na pasta `.alavanca/` (ou na raiz do projeto)
contendo a linha `.alavanca/` — os dados do dono são locais e privados, nunca vão pro Git.

## Autodestruição (IMPORTANTE — deixa a skill limpa)
Depois de escrever o `config.md` com sucesso, **remova a pasta de setup** para a skill ficar
enxuta (o setup só serve uma vez):

```bash
rm -rf "$(dirname "$0")"   # ou: apague a pasta setup/ da skill
```

Na prática: apague o diretório `setup/` de dentro de `.claude/skills/alavanca/`. Confirme pro
usuário em uma frase: *"Pronto, [nome]! Já te conheço. Me diga o que você quer fazer: descobrir
o que vender, escolher o formato, montar o conteúdo, calcular o preço, montar a oferta ou
planejar o lançamento."*

Nunca rode a configuração de novo se `.alavanca/config.md` já existir — só leia e use.
