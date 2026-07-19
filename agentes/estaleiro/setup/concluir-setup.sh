#!/usr/bin/env bash
# Encerra o setup do Estaleiro: remove os arquivos de instalação depois que
# o .estaleiro/config.md já foi gravado. Roda só uma vez.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -f ".estaleiro/config.md" ]; then
  echo "ERRO: .estaleiro/config.md ainda não existe. Rode o setup antes de concluir."
  exit 1
fi

# Remove os arquivos usados apenas durante a instalação.
rm -f "SETUP.md"
rm -rf "setup"

echo "Setup concluído. Arquivos de instalação removidos."
echo "O Estaleiro está montado: Arquiteto, Construtor, Testes, Revisor e Sentinela a postos."
