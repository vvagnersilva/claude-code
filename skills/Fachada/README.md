# Fachada

**O site profissional do seu negócio — feito conversando, sem cara de IA.**

A Fachada é uma skill de Claude Code que transforma uma conversa em português num site de uma página pronto para publicar: ela entrevista você sobre o seu negócio, propõe direções de design com personalidade (nada de template genérico), monta um único arquivo HTML com botão de WhatsApp, SEO local e dados estruturados, passa uma vistoria técnica de qualidade e ensina a colocar no ar de graça em 2 minutos.

## Para quem é

- Dono de negócio de serviço que não tem site (ou tem um que envergonha): clínica, barbearia, escritório, oficina, restaurante, estúdio.
- Profissional liberal que quer presença própria além do Instagram.
- Quem faz site para clientes (agências, freelancers) e quer acelerar a entrega de páginas de negócio local.

Nenhum conhecimento técnico é necessário — você só conversa.

## Instalação

1. Baixe e descompacte o arquivo `.zip`.
2. Copie a pasta `Fachada` para dentro da pasta `.claude/skills/` do seu projeto (crie a estrutura se não existir):

```
seu-projeto/
└── .claude/
    └── skills/
        └── Fachada/
            ├── SKILL.md
            ├── README.md
            ├── LICENSE
            ├── references/
            ├── scripts/
            └── setup/
```

3. Abra o Claude Code na pasta do projeto (`claude`) e diga:

> **"Quero criar um site para o meu negócio"**

Na primeira conversa a Fachada faz o setup (pergunta os dados do negócio e grava a configuração local). Depois disso, é direto ao ponto.

## O que dizer no dia a dia

| Você diz | O que acontece |
|---|---|
| "Quero um site para minha barbearia" | Entrevista rápida → escolha do estilo → site montado |
| "Troca a cor do botão" / "muda esse texto" | Ajuste pontual mantendo o design coerente |
| "Confere se tá tudo certo" | Vistoria técnica completa com relatório em português |
| "Como coloco no ar?" | Guia de publicação passo a passo (Netlify Drop, hospedagem própria, GitHub Pages) |
| "Já tenho site, quero um novo" | Renovação: aproveita os fatos, joga fora o visual datado |

## O que você recebe

- `fachada-site/index.html` — o site inteiro num arquivo só (CSS e JS embutidos), pronto para qualquer hospedagem.
- Botão flutuante de WhatsApp, telefone clicável, endereço linkado no mapa.
- SEO local: título e descrição certos, dados estruturados (JSON-LD), cartão bonito quando o link é compartilhado.
- Design com direção de arte nomeada — 8 estilos que fogem dos clichês de site feito por IA.

## Garantias (as regras de ouro)

- **Nunca inventa** depoimento, número, certificação ou foto. Se não existe, não entra.
- **Tudo local**: seus dados ficam em `.fachada/` na sua máquina; nada é enviado a lugar nenhum.
- **Quem publica é você**: a skill prepara e ensina; o site só vai ao ar pelas suas mãos.

## Requisitos

- [Claude Code](https://claude.com/claude-code) instalado.
- Python 3 (já vem no macOS e na maioria dos Linux; no Windows, instalar de python.org) — usado só pela vistoria técnica. Sem Python, tudo funciona exceto o relatório automático.

## Licença

MIT — use, adapte e compartilhe à vontade.
