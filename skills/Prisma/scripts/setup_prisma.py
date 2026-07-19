#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prisma — assistente de PRIMEIRA EXECUÇÃO (roda só uma vez).

A IA conversa com o dono (em português, sem jargão), coleta as respostas e
chama este script para gravar .prisma/config.md. Depois de gravar, o script
se AUTODESTROI (apaga a si mesmo e o marcador de setup) para a skill instalada
ficar limpa. Não acessa a internet.

Uso (a IA preenche com o que o dono respondeu):
  python3 setup_prisma.py \
    --nome "Ana" \
    --profissao "Dentista, dona de uma clínica" \
    --tom "Próximo e acolhedor, mas profissional" \
    --ferramentas "ChatGPT, Claude, Gemini" \
    --idioma "Português do Brasil"
"""
import argparse
import os
import sys
from pathlib import Path


def _project_root() -> Path:
    """Mesma lógica do prisma.py: grava o .prisma/ na RAIZ do projeto, não na
    pasta da skill, mesmo que este script seja chamado de dentro dela."""
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


BASE = _project_root() / ".prisma"

CONFIG_TEMPLATE = """# Configuração do Prisma

> Preenchido na primeira conversa. O Prisma usa isto para já deixar seus prompts
> com o seu contexto (quem você é, seu tom, suas ferramentas) sem você repetir
> tudo toda vez. Pode editar este arquivo quando quiser.

- **Nome:** {nome}
- **Profissão / negócio:** {profissao}
- **Tom de voz preferido:** {tom}
- **Ferramentas de IA que você usa:** {ferramentas}
- **Idioma das respostas:** {idioma}

---
_Estes dados ficam só no seu computador (pasta `.prisma/`, ignorada pelo Git)._
"""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nome", required=True)
    p.add_argument("--profissao", required=True)
    p.add_argument("--tom", default="Claro e profissional")
    p.add_argument("--ferramentas", default="ChatGPT, Claude")
    p.add_argument("--idioma", default="Português do Brasil")
    a = p.parse_args()

    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "biblioteca").mkdir(exist_ok=True)

    (BASE / "config.md").write_text(
        CONFIG_TEMPLATE.format(
            nome=a.nome.strip(), profissao=a.profissao.strip(),
            tom=a.tom.strip(), ferramentas=a.ferramentas.strip(),
            idioma=a.idioma.strip()),
        encoding="utf-8")

    # garante que os dados locais não vão pro Git
    gi = BASE / ".gitignore"
    gi.write_text("# dados locais do Prisma — não versionar\n*\n!.gitignore\n", encoding="utf-8")

    print(f"✅ Tudo pronto, {a.nome.strip().split()[0]}! Configuração salva em .prisma/config.md")
    print("   Agora é só pedir: «Prisma, cria um prompt para...» que eu monto pra você.")

    # ----- autodestruição dos arquivos de setup -----
    try:
        marker = Path(__file__).resolve().parent.parent / "PRIMEIRA_VEZ.md"
        if marker.exists():
            marker.unlink()
    except Exception:
        pass
    try:
        Path(__file__).resolve().unlink()  # apaga este próprio script
    except Exception:
        pass

if __name__ == "__main__":
    main()
