# Orquestra

**Seu time de agentes de IA para tocar um negócio de serviços, dentro do Claude Code.**

Você é o maestro. A Orquestra é o seu time de especialistas que já conhece o seu negócio e executa o trabalho do dia a dia: anúncios, conteúdo, propostas e documentos. Tudo em português, pensado para donos de agência, clínica, escritório e consultoria que querem fazer mais sem precisar contratar uma equipe inteira.

## Os quatro naipes

| Naipe | O que faz | Como chamar |
|-------|-----------|-------------|
| **Maestro** | Rege o time, monta o plano e delega | "configurar Orquestra", "Maestro, preciso de um plano" |
| **Tráfego** | Google/Meta Ads, públicos, SEO local | "cria uma campanha pra [serviço]" |
| **Conteúdo** | Textos no seu tom, sem "cara de IA" | "escreve um post sobre...", "deixa esse texto mais humano" |
| **Propostas** | Propostas, orçamentos, follow-up | "monta uma proposta pra esse cliente" |
| **Documentos** | Contratos, minutas, revisão | "faz um contrato de prestação de serviço" |

## Instalação

1. Baixe e **descompacte** a pasta `orquestra/`.
2. Abra a pasta no **Claude Code**.
3. Digite **"configurar Orquestra"** e responda às perguntas sobre o seu negócio.
4. Pronto. O seu time já está afinado e conhece o seu contexto.

> Quer usar os naipes em outro projeto? Copie a pasta `.claude/skills/` da Orquestra para dentro do seu projeto (ou para `~/.claude/skills/` para deixar disponível em tudo).

## Como funciona o setup

Na primeira execução, o Maestro faz uma rápida entrevista (nome do negócio, nicho, serviços, tom de voz, cliente ideal, região) e salva tudo em `.orquestra/config.md`. Esse arquivo é **privado** e fica fora do controle de versão (veja `.gitignore`). Depois do setup, os arquivos de instalação (`SETUP.md` e `setup/`) são removidos automaticamente — o repositório fica limpo.

**Não é preciso nenhuma chave de API para começar.** O núcleo funciona out-of-the-box.

## Privacidade e segurança

- Suas respostas de setup ficam só em `.orquestra/`, ignorado pelo git.
- Nenhuma chave ou segredo é guardado fora dessa pasta.
- As skills não fazem chamadas escondidas para serviços externos — leia os arquivos em `.claude/skills/`, são markdown legível.

## Estrutura

```
orquestra/
├── .claude/skills/
│   ├── orquestra-maestro/      # orquestrador + setup + plano
│   ├── orquestra-trafego/      # anúncios e aquisição
│   ├── orquestra-conteudo/     # conteúdo + humanização
│   ├── orquestra-propostas/    # propostas e follow-up
│   └── orquestra-documentos/   # contratos e revisão
├── exemplos/config.exemplo.md  # modelo do config
├── SETUP.md                    # guia de primeira execução (some após o setup)
├── setup/                      # arquivos de instalação (somem após o setup)
└── README.md
```

## Licença

MIT. Use, adapte e compartilhe à vontade.
