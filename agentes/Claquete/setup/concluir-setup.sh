#!/usr/bin/env bash
# Encerra o setup da Claquete: remove os arquivos de instalação depois que
# o .claquete/config.md já foi gravado. Roda só uma vez.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -f ".claquete/config.md" ]; then
  echo "ERRO: .claquete/config.md ainda não existe. Rode o setup antes de concluir."
  exit 1
fi

# Remove os arquivos usados apenas durante a instalação.
rm -f "SETUP.md"
rm -rf "setup"

echo "Setup concluído. Arquivos de instalação removidos."
echo "A Claquete está pronta: Pauteiro, Roteirista, Diretor de Arte, Otimizador, Produtor e Analista a postos. Ação!"
