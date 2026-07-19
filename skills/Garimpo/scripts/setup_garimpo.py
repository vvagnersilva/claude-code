#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Garimpo — assistente de PRIMEIRA EXECUÇÃO (roda só uma vez).

A IA conversa com o dono (PT-BR, sem jargão), coleta as respostas e chama este
script para gravar .garimpo/config.md na RAIZ do projeto. Depois de gravar, o
script se AUTODESTROI (apaga a si mesmo e o marcador de setup). Sem internet.

Uso (a IA preenche com o que o dono respondeu):
  python3 setup_garimpo.py \
    --nome "Marina" \
    --negocio "Loja de roupas com e-commerce" \
    --dados "Exportações de vendas do Shopify, planilha de estoque" \
    --moeda "Real (R$)" \
    --formato-data "DD/MM/AAAA"
"""
import argparse
import os
import sys
from pathlib import Path


def _project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    cwd = Path.cwd().resolve()
    parts = cwd.parts
    if ".claude" in parts:
        idx = parts.index(".claude")
        if idx > 0:
            return Path(*parts[:idx])
    for p in [cwd, *cwd.parents]:
        if (p / ".git").is_dir() or (p / ".claude").is_dir():
            return p
    return cwd


BASE = _project_root() / ".garimpo"

CONFIG = """# Configuração do Garimpo

> Preenchido na primeira conversa. O Garimpo usa isto para entender seus dados e
> falar a sua língua. Pode editar quando quiser.

- **Nome:** {nome}
- **Negócio:** {negocio}
- **Tipos de dado que você costuma ter:** {dados}
- **Moeda:** {moeda}
- **Formato de data:** {formato}

---
_Seus dados e análises ficam só no seu computador (pasta `.garimpo/`, ignorada pelo Git)._
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", required=True)
    ap.add_argument("--negocio", required=True)
    ap.add_argument("--dados", default="Planilhas de vendas, clientes e gastos")
    ap.add_argument("--moeda", default="Real (R$)")
    ap.add_argument("--formato-data", dest="formato", default="DD/MM/AAAA")
    a = ap.parse_args()

    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "dados").mkdir(exist_ok=True)
    (BASE / "config.md").write_text(
        CONFIG.format(nome=a.nome.strip(), negocio=a.negocio.strip(),
                      dados=a.dados.strip(), moeda=a.moeda.strip(), formato=a.formato.strip()),
        encoding="utf-8")
    (BASE / ".gitignore").write_text("# dados locais do Garimpo — não versionar\n*\n!.gitignore\n",
                                     encoding="utf-8")

    print(f"✅ Pronto, {a.nome.strip().split()[0]}! Configuração salva em .garimpo/config.md")
    print("   Agora me mande uma planilha (CSV) e pergunte o que quiser sobre ela.")

    try:
        marker = Path(__file__).resolve().parent.parent / "PRIMEIRA_VEZ.md"
        if marker.exists():
            marker.unlink()
    except Exception:
        pass
    try:
        Path(__file__).resolve().unlink()
    except Exception:
        pass

if __name__ == "__main__":
    main()
