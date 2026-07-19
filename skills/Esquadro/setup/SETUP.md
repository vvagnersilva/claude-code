# Configuração de 1ª execução — Esquadro

> Você (a IA) conduz esta conversa **uma única vez**, na primeira vez que o dono usa o
> Esquadro. Objetivo: aprender quem ele é, o que ele audita e a **marca** para o relatório,
> gravar em `.esquadro/config.md` e depois **apagar a pasta `setup/`** para deixar a skill
> limpa.

## Como conduzir (linguagem simples, sem jargão)
Faça as perguntas abaixo em conversa natural, PT-BR, uma de cada vez. Aceite respostas
curtas. Se o dono não souber algo, use "(não informado)". **Nunca** exija termo técnico.

1. **Seu nome** — como você assina um relatório de auditoria?
2. **Sua função** — você é da área de segurança do trabalho (SST/SSMA)? qualidade?
   compliance/auditoria? segurança da informação? é dono do negócio se preparando para
   fiscalização? (ajuda a calibrar os checklists)
3. **Organização** — nome da empresa/órgão que aparece no relatório (pode pular).
4. **O que você costuma auditar** — quais normas/áreas? (ex.: NRs de SST, LGPD, ISO 9001,
   ISO 27001, vigilância sanitária, bombeiros, controles internos). Pode marcar várias.
5. **Marca do relatório** — você quer uma **cor** principal (ex.: verde, azul, ou um código
   tipo #1f5f5b) e um **logo**? (se tiver logo, me diga o caminho do arquivo de imagem; se
   não, tudo bem)
6. **Tom** — o relatório/comunicação deve soar mais **formal** (corporativo) ou mais
   **direto e simples**?

## Ao terminar
1. Escreva `.esquadro/config.md` no formato abaixo (preencha; use "(não informado)" no que
   faltar).
2. Garanta que exista um `.gitignore` na raiz do projeto com `.esquadro/` ignorada (os
   dados de auditoria são internos — nunca devem ir para o controle de versão).
3. Rode `python3 scripts/esquadro.py init` para criar a pasta de dados vazia.
4. **Apague a pasta `setup/` inteira** (`rm -rf setup`). O Esquadro instalado não precisa
   mais dela.
5. Diga ao dono, em 2 linhas, que está pronto e mostre como começar:
   *"Pronto! Me diga o que você quer auditar. Por exemplo: 'monta um checklist da NR-12 e
   vamos auditar a prensa do Setor A' — eu monto a lista, a gente confere item a item e eu
   gero o relatório."*

---

### Modelo de `.esquadro/config.md`
```markdown
# Configuração do Esquadro

- **Nome:** {nome}
- **Função:** {SST / qualidade / compliance / segurança da informação / dono ...}
- **Organização:** {empresa/órgão ou (não informado)}
- **Audita:** {NRs, LGPD, ISO 9001, ISO 27001, vigilância sanitária, bombeiros, ...}
- **Cor:** {#1f5f5b ou nome da cor}
- **Logo:** {caminho do arquivo de imagem ou (não informado)}
- **Tom:** {formal / direto e simples}

## Lembretes de comportamento
- Nunca inventar item de norma, evidência, data, gravidade ou resultado.
- Sempre registrar a evidência de cada não-conformidade.
- Confirmar a versão vigente da norma na fonte oficial.
- Severidade honesta; toda NC com causa-raiz; toda ação com prazo e responsável.
- Não é laudo/certificação oficial; para risco grave ou exigência legal, indicar o
  responsável técnico.
- Dados 100% locais em `.esquadro/`.
```
