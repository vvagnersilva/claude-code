# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber", "openpyxl"]
# ///
"""Extrai tabelas de um PDF (com texto selecionavel) para XLSX.

Uso:
    uv run extrair_tabelas_pdf.py entrada.pdf --saida tabelas.xlsx

Se o PDF for escaneado (so imagem), nenhuma tabela sera encontrada — use
ocr_documento.py primeiro. Cada tabela detectada vira uma aba na planilha.
"""
import argparse
import sys
from pathlib import Path

import pdfplumber
from openpyxl import Workbook


def extrair(caminho_pdf: Path, caminho_saida: Path) -> int:
    wb = Workbook()
    wb.remove(wb.active)
    total = 0
    with pdfplumber.open(caminho_pdf) as pdf:
        for n_pagina, pagina in enumerate(pdf.pages, start=1):
            for n_tabela, tabela in enumerate(pagina.extract_tables() or [], start=1):
                if not tabela:
                    continue
                total += 1
                ws = wb.create_sheet(title=f"p{n_pagina}_t{n_tabela}"[:31])
                for linha in tabela:
                    ws.append(["" if c is None else c for c in linha])
    if total == 0:
        print("Nenhuma tabela encontrada. Se o PDF for escaneado, rode o OCR antes.")
        return 0
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho_saida)
    print(f"OK: {total} tabela(s) salvas em {caminho_saida}")
    return total


def main() -> int:
    p = argparse.ArgumentParser(description="Extrai tabelas de PDF para XLSX.")
    p.add_argument("pdf", type=Path, help="Arquivo PDF de entrada")
    p.add_argument("--saida", type=Path, default=None, help="Arquivo XLSX de saida")
    args = p.parse_args()
    if not args.pdf.exists():
        print(f"Arquivo nao encontrado: {args.pdf}", file=sys.stderr)
        return 1
    saida = args.saida or args.pdf.with_suffix(".tabelas.xlsx")
    extrair(args.pdf, saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
