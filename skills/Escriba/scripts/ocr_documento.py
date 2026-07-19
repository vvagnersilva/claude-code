# /// script
# requires-python = ">=3.10"
# dependencies = ["pytesseract", "pdf2image", "pillow"]
# ///
"""OCR de documento escaneado (PDF imagem) ou foto -> texto.

Uso:
    uv run ocr_documento.py documento.pdf --saida texto.txt
    uv run ocr_documento.py foto.jpg --idioma por

Requisitos de sistema (instalar uma vez):
    - Tesseract OCR  (mac: brew install tesseract tesseract-lang)
    - Poppler        (mac: brew install poppler)  -- so para PDF
O idioma padrao e portugues ("por").
"""
import argparse
import sys
from pathlib import Path

import pytesseract
from PIL import Image


def ocr_imagem(img: Image.Image, idioma: str) -> str:
    return pytesseract.image_to_string(img, lang=idioma)


def main() -> int:
    p = argparse.ArgumentParser(description="OCR de PDF escaneado ou imagem.")
    p.add_argument("entrada", type=Path, help="PDF escaneado ou imagem (png/jpg)")
    p.add_argument("--saida", type=Path, default=None, help="Arquivo .txt de saida")
    p.add_argument("--idioma", default="por", help="Idioma do Tesseract (padrao: por)")
    args = p.parse_args()

    if not args.entrada.exists():
        print(f"Arquivo nao encontrado: {args.entrada}", file=sys.stderr)
        return 1

    partes: list[str] = []
    if args.entrada.suffix.lower() == ".pdf":
        try:
            from pdf2image import convert_from_path
        except ImportError:
            print("pdf2image ausente. Rode com 'uv run' ou instale as dependencias.", file=sys.stderr)
            return 1
        paginas = convert_from_path(str(args.entrada))
        for i, pagina in enumerate(paginas, start=1):
            partes.append(f"--- pagina {i} ---\n{ocr_imagem(pagina, args.idioma)}")
    else:
        partes.append(ocr_imagem(Image.open(args.entrada), args.idioma))

    texto = "\n\n".join(partes).strip()
    saida = args.saida or args.entrada.with_suffix(".ocr.txt")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(texto, encoding="utf-8")
    print(f"OK: texto salvo em {saida} ({len(texto)} caracteres)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
