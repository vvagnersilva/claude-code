# Fichário — seu segundo cérebro 🧠🗂️

O **Fichário** é uma skill de Claude Code que vira o seu **segundo cérebro**: você joga o que aprendeu — uma ideia, uma anotação de aula, um trecho de vídeo, um insight, um método — e ele transforma em **cartões** (uma ideia por cartão, nas suas palavras), liga aos cartões parecidos e, depois, responde às suas perguntas usando **só o que você guardou**, sempre dizendo de qual cartão veio. **Nunca inventa.**

Conversa 100% em **português**, sem jargão, e guarda tudo **no seu computador** (nada vai para a internet).

## O que ele faz (6 modos)
1. **Guardar** — você manda um texto/ideia; ele quebra em cartões de uma ideia cada e liga aos parecidos.
2. **Conectar** — sugere e cria ligações entre cartões, tecendo sua rede de conhecimento.
3. **Buscar / Perguntar** — "o que eu já sei sobre X?"; ele responde só com seus cartões, citando cada um.
4. **Destilar** — revisa o que envelheceu e junta os repetidos: a base fica **mais afiada, não maior**.
5. **Mapa** — agrupa tudo que você sabe sobre um assunto.
6. **Painel** — mostra seu segundo cérebro crescendo (quantos cartões, ligações, assuntos).

## Como instalar
1. Baixe e descompacte o arquivo.
2. Copie a pasta `Fichário` para dentro de `.claude/skills/` do seu projeto (ou de `~/.claude/skills/` para usar em qualquer projeto).
3. Abra o Claude Code e diga algo como **"guarda essa ideia: ..."** ou **"monta meu segundo cérebro"**. A skill ativa sozinha.

## Primeira conversa
Na primeira vez, o Fichário faz 3-4 perguntas rápidas (nome, sua área, os assuntos que você estuda, o tom que prefere), guarda isso e já começa. Depois é só conversar.

## Privacidade
Tudo fica em `.fichario/` no seu projeto — cartões em markdown, no seu disco. Nada é enviado para fora. Se você usa git, a pasta `.fichario/` já está no `.gitignore`.

## Para quem é
Qualquer pessoa que aprende e não quer esquecer: quem está estudando IA, profissionais que querem estruturar a própria metodologia, donos de negócio que guardam decisões e aprendizados, criadores com banco de ideias, e iniciantes que só querem um lugar em português para não perder o que descobrem.

## Requisitos
- Claude Code instalado.
- Python 3 (já vem no macOS/Linux) — o motor usa só a biblioteca padrão, sem instalar nada.

## Licença
MIT. Síntese própria; ideias de referência de repositórios open-source (MIT) foram estudadas e reescritas do zero — nenhum código de terceiros foi copiado.
