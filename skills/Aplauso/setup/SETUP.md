# Setup do Aplauso (primeira execucao — roda UMA vez)

Voce (Claude) esta guiando o dono pela configuracao inicial. Seja breve, caloroso e em PT-BR.
**Nao** peca nada tecnico. No fim, grave a config e apague esta pasta `setup/`.

## Passo 1 — Conversa de 2 minutos
Pergunte, de forma leve (uma de cada vez, aceite respostas curtas):

1. **Qual e o nome do seu negocio?** (ex.: "Clinica Sorria", "Studio Ana Cabelos")
2. **O que voce faz / seu servico principal?** (1 frase)
3. **Como voce fala com seus clientes?** Mais formal ("o senhor/a senhora") ou informal
   ("voce"), usa emoji? Se puder, cole 1 mensagem sua de verdade para eu pegar seu jeito.
4. **Onde voce quer receber avaliacoes?** Marque os que usa: Google, Instagram, Facebook,
   iFood, WhatsApp, site, outro. (Se tiver o link do Google Avaliacoes, me passa.)
5. **Tem alguma regra sua?** (ex.: "nunca usar emoji", "sempre assinar como Dra. Ana")

## Passo 2 — Gravar a configuracao
Crie/atualize o arquivo `.aplauso/config.md` (na pasta do dono) com o que ele respondeu.
Use exatamente este formato (preencha os valores):

```markdown
# Configuracao do Aplauso

- negocio: <nome do negocio>
- servico_principal: <servico>
- tom_de_voz: <formal/informal, emoji sim/nao, jeito do dono>
- exemplo_de_mensagem_do_dono: <cole aqui se ele deu um exemplo>
- canais_de_avaliacao: <ex.: google, instagram, whatsapp>
- link_google_avaliacao: <cole se tiver, senao deixe vazio>
- regras: <regras especificas que ele pediu>
```

Depois rode o motor para criar os arquivos de dados. **Importante:** rode a partir da
pasta de trabalho do dono (a raiz do projeto), NAO de dentro da pasta da skill — assim o
`.aplauso/` nasce junto do trabalho do dono. Use o caminho completo do script:
```bash
# a partir da raiz do projeto do dono:
python3 .claude/skills/Aplauso/scripts/aplauso.py init
```
(Em todos os modos, sempre chame o script com esse caminho completo, a partir da raiz do
projeto, para os dados ficarem sempre no mesmo `.aplauso/`.)

## Passo 3 — Autodestruicao (OBRIGATORIO)
Confirme que `.aplauso/config.md` existe e esta preenchido. Entao **apague a pasta `setup/`**
para a skill ficar limpa:
```bash
rm -rf setup
```

## Passo 4 — Primeiro valor
Diga ao dono: *"Pronto! Me conta um cliente que ficou feliz com seu trabalho ultimamente —
eu ja preparo o pedido de avaliacao perfeito para voce mandar."* E entre no modo **Pedir**.
