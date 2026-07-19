# Lupa 🔎

**A leitura atenta que enxerga o que passa batido.**

A Lupa é uma skill para o Claude Code que **lê e analisa documentos densos por
você** — contratos, laudos, relatórios técnicos e contábeis, processos, propostas
e termos. Em vez de você gastar uma hora lendo um contrato de 30 páginas, a Lupa
lê em segundos e te conta, em português claro, o que importa: o resumo, os riscos
(com o trecho citado), os prazos e obrigações, o que mudou entre duas versões, a
resposta a uma pergunta específica e o que está faltando.

Feita para quem passa o dia lendo coisa séria: **advogados, contadores, peritos,
engenheiros, corretores, gestores** — e qualquer pessoa que precisa entender um
documento sem deixar passar uma cláusula perigosa.

## O que ela faz (6 modos)

| Modo | Você diz | A Lupa faz |
|------|----------|------------|
| **Resumir** | "do que se trata esse documento?" | Resumo executivo: tipo, partes, vigência, objeto e os pontos principais |
| **Riscos** | "tem alguma pegadinha aqui?" | Lista os pontos de atenção em 🔴 Crítico / 🟡 Atenção / 🟢 OK, com o trecho e o porquê |
| **Prazos & Obrigações** | "o que isso me obriga, e até quando?" | Extrai datas e obrigações, ordena e alerta o que está vencido/perto |
| **Comparar** | "o que mudou entre essas duas versões?" | Mostra o que mudou e, principalmente, o que mudou que importa |
| **Perguntar** | "tem cláusula de multa? qual o valor?" | Responde só com base no texto, citando o trecho (e diz quando não acha) |
| **Conferir** | "esse documento está completo?" | Confere contra um checklist do tipo e aponta o que falta |

## As garantias da Lupa

- **Nunca inventa.** Tudo que ela afirma está no documento, com o trecho citado.
  O que não estiver no texto, ela diz: "não encontrei isso no documento".
- **Sempre mostra onde está** (cláusula, página, seção) para você conferir na fonte.
- **Mostra também o que está OK**, não só problema.
- **Não substitui um parecer profissional** — é uma leitura de apoio que adianta
  seu trabalho. Decisões sérias, confirme com o profissional habilitado.
- **Seus documentos ficam só na sua máquina.** Nada vai para a internet.

## Como instalar

1. Baixe e descompacte o arquivo `Lupa.zip`.
2. Copie a pasta `Lupa` para dentro de `.claude/skills/` do seu projeto, **ou**
   para `~/.claude/skills/` (para usar em qualquer pasta). O caminho final fica:
   `.claude/skills/Lupa/`
3. Abra o Claude Code nessa pasta e diga, por exemplo: **"analisa esse contrato
   pra mim"** (e aponte/cole o documento). A Lupa entra em ação sozinha.

## A primeira conversa

Na primeira vez, a Lupa faz uma conversa rápida para te conhecer (como te chamar,
sua profissão, os tipos de documento que você mais analisa e o nível de rigor) e
guarda isso em `.lupa/config.md` na sua pasta. Depois disso, é só pedir.

## Privacidade

Tudo que a Lupa lê e grava fica na pasta `.lupa/` do seu projeto, na sua máquina.
A skill nunca envia o documento para fora. Se sua pasta usa git, a Lupa adiciona
`.lupa/` ao `.gitignore` para seus documentos não irem para o controle de versão.

## Licença

MIT — use, adapte e compartilhe. Veja `LICENSE`.
