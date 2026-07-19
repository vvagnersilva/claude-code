#!/usr/bin/env bash
# Conclui o setup da Fisga: grava o perfil/oferta do usuario em .fisga/config.md (na raiz
# do projeto, ignorado pelo git) e remove os arquivos de instalacao (auto-destruicao).
#
# Uso (o Claude preenche os valores a partir das respostas do usuario):
#   bash concluir-setup.sh \
#     --nome "Maria" --oferta "Agendamento automatico no WhatsApp" \
#     --diferencial "Implanto em 7 dias sem mexer no sistema atual" \
#     --nicho "clinicas odontologicas" --porte "pequeno/medio" --regiao "Sao Paulo, SP" \
#     --ticket "R$ 1.500 a R$ 4.000" --canais "whatsapp,instagram" --tom "cordial"
set -euo pipefail

NOME="" ; OFERTA="" ; DIFERENCIAL="" ; NICHO="" ; PORTE="" ; REGIAO="" ; TICKET="" ; CANAIS="whatsapp" ; TOM="cordial"
while [ $# -gt 0 ]; do
  case "$1" in
    --nome) NOME="$2"; shift 2;;
    --oferta) OFERTA="$2"; shift 2;;
    --diferencial) DIFERENCIAL="$2"; shift 2;;
    --nicho) NICHO="$2"; shift 2;;
    --porte) PORTE="$2"; shift 2;;
    --regiao) REGIAO="$2"; shift 2;;
    --ticket) TICKET="$2"; shift 2;;
    --canais) CANAIS="$2"; shift 2;;
    --tom) TOM="$2"; shift 2;;
    *) echo "Flag desconhecida: $1" >&2; exit 1;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "./.fisga"
cat > "./.fisga/config.md" <<EOF
# Config da Fisga
Quem voce e e o que voce vende. Editavel a qualquer momento. Ignorado pelo git.

- nome: ${NOME}
- oferta_principal: ${OFERTA}
- diferencial: ${DIFERENCIAL}
- nicho_alvo: ${NICHO}
- porte_cliente: ${PORTE}
- regiao: ${REGIAO}
- ticket_medio: ${TICKET}
- canais_preferidos: ${CANAIS}   # whatsapp | instagram | email | linkedin
- tom_de_voz: ${TOM}             # informal | cordial | direto | formal

## Perfil de Cliente Ideal (ICP)
Refine aqui conforme aprende quem responde melhor:
- ramo: ${NICHO}
- porte: ${PORTE}
- regiao: ${REGIAO}
- dor_gatilho: (preencha: a urgencia que faz esse cliente procurar voce)
- ticket: ${TICKET}
EOF

echo "OK: perfil gravado em ./.fisga/config.md"

# Auto-destruicao dos arquivos de instalacao
rm -f "$SKILL_DIR/SETUP.md"
rm -rf "$SKILL_DIR/setup"
echo "OK: arquivos de instalacao removidos. A Fisga esta pronta."
