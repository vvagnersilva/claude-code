# Primeira conversa da Lavra (assistente de preparação — roda só uma vez)

Este roteiro roda **na primeiríssima vez** que a Lavra é usada num computador —
quando ainda não existe o arquivo `.lavra/config.json`. Ele coleta a identidade do
profissional (que vai no cabeçalho e no fecho de todo documento), grava a
configuração e depois **se apaga**, deixando a skill instalada limpa.

Conduza como uma conversa curta e acolhedora, em português, uma pergunta de cada vez.

## O que coletar

1. **Nome completo** — como deve aparecer na assinatura.
2. **Registro profissional / conselho** — ex.: CRM-SP 123456, CRO-RJ 0000, CREA/CAU,
   OAB/UF 00000, CRC-00/000000. (Se a pessoa não tiver um conselho — ex.: consultor —
   pergunte como quer se identificar: cargo, empresa, etc.)
3. **Área de atuação** — saúde, odontologia, engenharia/obra, jurídico, contábil,
   administrativo/público, consultoria, ou "outra: qual?".
4. **Cidade / UF** — para o local no fecho.
5. **Formato de saída preferido** — "Markdown" (texto simples) e/ou "HTML pronto para
   PDF" (para imprimir/salvar como PDF). Pode ser os dois.

## Como gravar

> ⚠️ **REGRA DE PATH (importante).** Rode o script **a partir da pasta do projeto**
> (a pasta onde o Claude Code está aberto) — **nunca** entre (`cd`) na pasta da skill.
> O script grava a pasta `.lavra/` no diretório atual, e ela precisa nascer **na raiz do
> projeto**, não dentro de `.claude/skills/`. Por isso, chame o script pelo **caminho
> completo de onde a skill está instalada** (`SKILL_DIR`), sem mudar de diretório:
> - Instalação no projeto → `SKILL_DIR = .claude/skills/Lavra`
> - Instalação global → `SKILL_DIR = ~/.claude/skills/Lavra`

Depois de coletar, chame o script (da raiz do projeto) para criar a estrutura e gravar
a configuração — troque `SKILL_DIR` pelo caminho real acima:

```bash
python3 SKILL_DIR/scripts/lavra.py init \
  --nome "<nome completo>" \
  --registro "<registro/conselho>" \
  --area "<area>" \
  --cidade-uf "<Cidade/UF>" \
  --saida "<markdown|html|ambos>"
```

Isso cria a pasta local `.lavra/` **na raiz do projeto**, com:
- `.lavra/config.json` — a identidade profissional.
- `.lavra/documentos/` — onde cada documento lavrado será salvo.
- `.lavra/modelos/` — onde os modelos próprios da pessoa ficam.

Confirme que `.lavra/config.json` foi criado **na raiz do projeto** (e não dentro de
`.claude/skills/Lavra/`). Se o Python não estiver disponível, crie `.lavra/config.json`
manualmente na raiz do projeto com os mesmos campos (`nome`, `registro`, `area`,
`cidade_uf`, `saida`).

## Autodestruição (obrigatória, ao final)

Assim que o `config.json` existir na raiz do projeto e você confirmar os dados com a
pessoa, **remova a pasta de setup da skill** para o pacote instalado ficar limpo — use
o mesmo `SKILL_DIR` de onde a skill está instalada:

```bash
rm -rf SKILL_DIR/setup
```

Confirme para a pessoa: "Pronto, Lavra configurada para {nome} — {registro}. Da
próxima vez é só me pedir um laudo, parecer ou relatório." E siga para o modo que ela
pedir (ou explique os modos: Lavrar, Revisar, Fechar, Modelos, Painel).

> Importante: a autodestruição apaga só a pasta `setup/`. Todo o resto da skill
> (SKILL.md, referências, modelos, script) permanece. A configuração fica em
> `.lavra/config.json`, que não é versionado (está no `.gitignore`).
