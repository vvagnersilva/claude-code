# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "openpyxl"]
# ///
"""Diagnostica e limpa uma planilha bagunçada (XLSX ou CSV).

Uso:
    uv run limpar_planilha.py dados.xlsx --diagnosticar
    uv run limpar_planilha.py dados.csv --saida limpo.xlsx

--diagnosticar  : so mostra um relatorio (colunas, tipos, vazios, duplicados) sem alterar nada.
Sem --diagnosticar: aplica limpezas seguras (remove linhas/colunas 100% vazias, tira espacos
das pontas dos textos, remove linhas duplicadas) e salva como NOVO arquivo. O original nunca
e sobrescrito. Limpezas que dependem de decisao (converter tipos, normalizar categorias) ficam
para o Claude aplicar conforme combinado com o usuario.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


def carregar(caminho: Path) -> pd.DataFrame:
    if caminho.suffix.lower() in {".csv", ".tsv"}:
        sep = "\t" if caminho.suffix.lower() == ".tsv" else None
        return pd.read_csv(caminho, sep=sep, engine="python")
    return pd.read_excel(caminho)


def diagnostico(df: pd.DataFrame) -> str:
    linhas = [f"Dimensoes: {df.shape[0]} linhas x {df.shape[1]} colunas", "", "Colunas:"]
    for col in df.columns:
        vazios = int(df[col].isna().sum())
        linhas.append(f"  - {col!r}: tipo={df[col].dtype}, vazios={vazios}")
    linhas.append("")
    linhas.append(f"Linhas totalmente vazias: {int(df.isna().all(axis=1).sum())}")
    linhas.append(f"Colunas totalmente vazias: {int(df.isna().all(axis=0).sum())}")
    linhas.append(f"Linhas duplicadas: {int(df.duplicated().sum())}")
    return "\n".join(linhas)


def limpar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    mudancas: list[str] = []
    antes = df.shape
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    if df.shape != antes:
        mudancas.append(f"Removidas linhas/colunas vazias: {antes} -> {df.shape}")
    for col in df.columns:
        df[col] = df[col].map(lambda v: v.strip() if isinstance(v, str) else v)
    mudancas.append("Espacos das pontas dos textos removidos")
    dups = int(df.duplicated().sum())
    if dups:
        df = df.drop_duplicates()
        mudancas.append(f"Removidas {dups} linha(s) duplicada(s)")
    return df, mudancas


def main() -> int:
    p = argparse.ArgumentParser(description="Diagnostica/limpa planilha.")
    p.add_argument("entrada", type=Path, help="Planilha XLSX/CSV de entrada")
    p.add_argument("--diagnosticar", action="store_true", help="So mostra o diagnostico")
    p.add_argument("--saida", type=Path, default=None, help="Arquivo XLSX de saida")
    args = p.parse_args()

    if not args.entrada.exists():
        print(f"Arquivo nao encontrado: {args.entrada}", file=sys.stderr)
        return 1

    df = carregar(args.entrada)
    print(diagnostico(df))

    if args.diagnosticar:
        return 0

    df_limpo, mudancas = limpar(df)
    saida = args.saida or args.entrada.with_suffix(".limpo.xlsx")
    saida.parent.mkdir(parents=True, exist_ok=True)
    df_limpo.to_excel(saida, index=False)
    print("\nLimpezas aplicadas:")
    for m in mudancas:
        print(f"  - {m}")
    print(f"\nOK: salvo em {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
