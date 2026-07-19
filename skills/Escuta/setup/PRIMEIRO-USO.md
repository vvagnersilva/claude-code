# Primeiro uso da Escuta — configuracao guiada (2 minutos)

Voce (a IA) esta lendo isto porque ainda nao existe `.escuta/config.md`. Conduza uma
conversa curta e amigavel em portugues para configurar a Escuta para este dono. NAO faca
trabalho de atendimento ainda — primeiro configure.

## Passo 1 — Crie a estrutura
```bash
python3 scripts/escuta.py init
```

## Passo 2 — Faca estas perguntas (uma de cada vez, tom acolhedor)
1. **Como voce se chama?** (e, se quiser, o nome do seu negocio/clinica/escritorio)
2. **Que tipo de atendimento voce faz?** (ex.: consulta medica, sessao, reuniao de venda,
   visita a imovel, atendimento juridico, consultoria...) — e como voce chama quem atende
   (paciente, cliente, lead...).
3. **Qual o seu tom com o cliente?** (mais proximo e informal, ou mais formal e tecnico?
   usa emoji? como trata: voce, senhor(a), Dr(a), primeiro nome?)
4. **Por onde voce costuma fazer o follow-up?** (WhatsApp, e-mail, ligacao?)
5. **Tem alguma palavra/jargao do seu negocio** que eu devo (ou nao devo) usar com o cliente?

> Observacao: a Escuta trabalha a partir do TEXTO que voce cola (anotacoes ou uma
> transcricao que voce ja tem). Ela nao grava nem transcreve audio. Se voce so tiver o
> audio, e so colar aqui a transcricao depois.

## Passo 3 — Grave o config
Escreva as respostas em `.escuta/config.md` (UTF-8, com acentos), neste formato:

```markdown
# Configuracao da Escuta

- Dono: <nome> (<negocio>)
- Tipo de atendimento: <...> | chama o cliente de: <...>
- Tom de voz: <proximo/formal>, emoji: <sim/nao>, tratamento: <voce/senhor/Dr...>
- Canal de follow-up: <WhatsApp/e-mail/...>
- Jargao do negocio: <termos a usar / evitar>
- Observacoes: <qualquer detalhe util>
```

## Passo 4 — Autodestruicao do setup
Depois de gravar o config com sucesso, **apague a pasta de setup** para deixar a skill limpa:
```bash
rm -rf setup
```
Confirme ao dono: "Pronto! Escuta configurada. Da proxima vez que voce sair de um
atendimento, e so colar suas anotacoes aqui que eu organizo tudo." E siga para os modos
normais (SKILL.md).
