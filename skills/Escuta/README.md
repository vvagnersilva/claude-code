# Escuta 🎧 — o que aconteceu no atendimento vira a proxima acao

Voce atende cliente o dia todo — consulta, reuniao, visita, ligacao — e sai com a cabeca
cheia e anotacoes soltas. No fim do dia, esquece o que combinou, perde o follow-up e chega
no proximo encontro sem lembrar do historico.

A **Escuta** resolve isso. Voce cola suas anotacoes (ou uma transcricao que voce ja tem) e
ela transforma em:

- **Resumo limpo** do atendimento
- **Decisoes** que ficaram
- **Pendencias** com o que / quem / prazo
- **Follow-up pronto** no seu tom, pra voce colar no WhatsApp
- **Ficha por cliente** com todo o historico, pra voce chegar preparado na proxima

Tudo em portugues, **100% no seu computador**, e a Escuta **nunca inventa** nada — so
organiza o que voce escreveu. Ela sugere; quem fala com o cliente e sempre voce.

## Para quem e
Medicos, dentistas, advogados, peritos, corretores de imoveis e seguros, arquitetos,
consultores, fisioterapeutas, contadores — qualquer dono de negocio de servico que atende
gente e precisa nao deixar nada cair.

## O que ela faz (6 modos)
1. **Capturar** — anotacoes/transcricao viram resumo + decisoes + pendencias.
2. **Acompanhar** — escreve o follow-up no seu tom e sugere quando enviar.
3. **Ficha** — o historico completo de cada cliente.
4. **Preparar** — briefing de 1 minuto antes do proximo atendimento.
5. **Pendencias** — o que esta em aberto e o que esta atrasado hoje.
6. **Panorama** — visao geral + quem sumiu e merece um retorno.

## Instalacao
1. Baixe e descompacte o arquivo.
2. Copie a pasta `Escuta` para dentro de `.claude/skills/` do seu projeto
   (ou de `~/.claude/skills/` para usar em qualquer lugar). Deve ficar assim:
   ```
   .claude/skills/Escuta/SKILL.md
   ```
3. Abra o Claude Code nessa pasta e diga, por exemplo:
   *"Acabei de atender um cliente, quero organizar as anotacoes."*
   Na primeira vez, a Escuta faz uma configuracao rapida (2 min) e ja comeca.

## Requisitos
- [Claude Code](https://claude.com/claude-code)
- Python 3 (ja vem no Mac e no Linux; no Windows, instale de python.org)
- Nenhuma chave de API, nenhuma conta, nenhum dado na nuvem.

## Onde ficam seus dados
Tudo numa pasta `.escuta/` no seu computador:
- `.escuta/config.md` — suas preferencias
- `.escuta/clientes/<nome>.md` — a ficha de cada cliente
- `.escuta/pendencias.csv` — suas pendencias

Nada sai da sua maquina. Dados de cliente sao sensiveis — a Escuta os mantem locais e
nunca os coloca em mensagem ou post.

## Licenca
MIT — use, adapte e compartilhe livremente.
