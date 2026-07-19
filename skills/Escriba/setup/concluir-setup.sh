#!/usr/bin/env bash
# Conclui o setup do Escriba: grava as preferencias em .escriba/config.md (na raiz do
# projeto, ignorado pelo git) e remove os arquivos de instalacao (auto-destruicao).
#
# Uso (o Claude preenche os valores a partir das respostas do usuario):
#   bash concluir-setup.sh \
#     --nome "Maria" --empresa "Clinica X" --pasta "./trabalho" \
#     --formato-tabela xlsx --formato-doc docx --tom cordial --idioma pt-BR
set -euo pipefail

NOME="" ; EMPRESA="" ; PASTA="." ; FMT_TAB="xlsx" ; FMT_DOC="docx" ; TOM="cordial" ; IDIOMA="pt-BR"
while [ $# -gt 0 ]; do
  case "$1" in
    --nome) NOME="$2"; shift 2;;
    --empresa) EMPRESA="$2"; shift 2;;
    --pasta) PASTA="$2"; shift 2;;
    --formato-tabela) FMT_TAB="$2"; shift 2;;
    --formato-doc) FMT_DOC="$2"; shift 2;;
    --tom) TOM="$2"; shift 2;;
    --idioma) IDIOMA="$2"; shift 2;;
    *) echo "Flag desconhecida: $1" >&2; exit 1;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "./.escriba/modelos"
cat > "./.escriba/config.md" <<EOF
# Config do Escriba
Preferencias do usuario. Editavel a qualquer momento. Ignorado pelo git.

- nome: ${NOME}
- empresa: ${EMPRESA}
- pasta_de_trabalho: ${PASTA}
- formato_tabela_padrao: ${FMT_TAB}   # xlsx | csv
- formato_documento_padrao: ${FMT_DOC} # docx | md
- tom_das_respostas: ${TOM}            # formal | cordial | direto
- idioma_de_saida: ${IDIOMA}

## Modelos salvos
Coloque modelos de resposta/e-mail recorrentes em .escriba/modelos/ (um arquivo por modelo).
EOF

echo "OK: preferencias gravadas em ./.escriba/config.md"

# Auto-destruicao dos arquivos de instalacao
rm -f "$SKILL_DIR/SETUP.md"
rm -rf "$SKILL_DIR/setup"
echo "OK: arquivos de instalacao removidos. O Escriba esta pronto."
