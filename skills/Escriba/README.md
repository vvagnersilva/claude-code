# 🖋️ Escriba — seu back-office no Claude Code

O **Escriba** é uma skill do Claude Code que toma conta do trabalho repetitivo de **papelada e
dados** — aquele que come horas e enche de erro quando feito na mão. Você joga os arquivos
bagunçados; o Escriba **lê, extrai, organiza e escreve**, e devolve uma entrega pronta.

Feito para **donos de negócio e profissionais não-técnicos** (clínicas, escritórios,
imobiliárias, importadoras, peritos, financeiro, agro) que querem reduzir trabalho manual
**sem programar e sem contratar mais gente**.

## O que ele faz (4 modos)

| Modo | Você pede algo como… | Recebe de volta |
|------|----------------------|-----------------|
| **Extrair** | "tira os dados desses PDFs", "transforma essas notas em planilha" | Planilha limpa (Excel/CSV) com os dados organizados |
| **Organizar planilha** | "essa planilha tá uma bagunça", "tira os duplicados, padroniza" | Planilha limpa, sem erros, num arquivo novo |
| **Relatório / Laudo** | "faz um relatório desses arquivos", "monta um laudo a partir disso" | Documento Word (ou Markdown) bem estruturado |
| **Responder** | "responde esses pedidos", "redige a resposta padrão" | Respostas prontas, no seu tom, pra copiar e enviar |

Funciona com PDF (inclusive **escaneado/foto**, via OCR), imagens, Excel e CSV.

## Instalação

1. Descompacte a pasta `escriba/`.
2. Copie para o seu Claude Code:
   - **Por projeto:** coloque em `SEU_PROJETO/.claude/skills/escriba/`.
   - **Global (todos os projetos):** coloque em `~/.claude/skills/escriba/`.
3. Abra o Claude Code e (opcional, recomendado) rode o setup uma vez:

   > **"Rode o setup do Escriba."**

   Ele pergunta seu nome/empresa, pasta de trabalho, formatos preferidos e tom, grava em
   `.escriba/config.md` (ignorado pelo git) e **some sozinho** com os arquivos de instalação.
   Sem o setup também funciona — o Escriba usa bons padrões e pergunta só o necessário na hora.

## Pré-requisitos

- **Claude Code** instalado.
- **uv** (recomendado) para rodar os scripts sem instalar nada à mão — o `uv run` resolve as
  dependências sozinho. Sem `uv`, dá pra usar `python3` instalando as bibliotecas indicadas no
  topo de cada script.
- Só para OCR de documentos escaneados/fotos: **Tesseract** e **Poppler** no sistema
  (no Mac: `brew install tesseract tesseract-lang poppler`).

## Como usar (exemplos)

- *"Escriba, extrai os dados dessas 12 notas fiscais em PDF pra uma planilha com Data, Fornecedor, Valor e Nº da NF."*
- *"Essa planilha de clientes tá uma bagunça — diagnostica e me devolve limpa."*
- *"Monta um relatório a partir desses 5 documentos, formato Word, para a diretoria."*
- *"Redige a resposta padrão pra esses 8 pedidos de orçamento, tom cordial."*

## Princípios

- **Nunca inventa dados** — só sai o que está nos seus arquivos; lacunas são sinalizadas.
- **Nunca sobrescreve o original** — sempre salva como arquivo novo.
- **Confirma antes de processar lotes grandes** e mostra o resultado pra você validar.

## Licença

MIT — use, adapte e compartilhe à vontade.
