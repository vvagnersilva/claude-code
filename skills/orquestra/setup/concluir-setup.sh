#!/usr/bin/env bash
# Encerra o setup da Orquestra: remove os arquivos de instalação depois que
# o .orquestra/config.md já foi gravado. Roda só uma vez.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -f ".orquestra/config.md" ]; then
  echo "ERRO: .orquestra/config.md ainda não existe. Rode o setup antes de concluir."
  exit 1
fi

# Remove os arquivos usados apenas durante a instalação.
rm -f "SETUP.md"
rm -rf "setup"

echo "Setup concluído. Arquivos de instalação removidos."
echo "A Orquestra está afinada e pronta para uso."
