#!/usr/bin/env python3
"""Primeira vez da Forja - grava a configuracao e depois se autodestroi.

NAO e interativo. O Claude coleta as respostas com o usuario, monta um JSON
de respostas e chama:

    python3 scripts/primeira_vez.py --respostas /caminho/respostas.json

ou passando o JSON por stdin:

    cat respostas.json | python3 scripts/primeira_vez.py --stdin

O script entao:
  1. grava .forja/config.json (lido pelo motor) e .forja/config.md (legivel)
  2. garante que .forja/ esteja no .gitignore
  3. remove o bloco de Primeira vez do SKILL.md (entre os marcadores)
  4. se apaga (e apaga o exemplo de respostas e a pasta setup), skill limpa
"""

import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ_SKILL = os.path.dirname(AQUI)            # pasta da skill (onde fica o SKILL.md)


def raiz_projeto():
    """Raiz do projeto do usuario, mesmo rodando de dentro de .claude/skills/forja."""
    cwd = os.path.abspath(os.getcwd())
    marcador = os.sep + ".claude" + os.sep
    if marcador in cwd + os.sep:
        return cwd.split(marcador)[0]
    d = cwd
    while True:
        if os.path.isdir(os.path.join(d, ".claude")) or os.path.isdir(os.path.join(d, ".git")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            return cwd
        d = pai


PROJ = raiz_projeto()
DIR_CFG = os.path.join(PROJ, ".forja")

CAMPOS_OBRIG = ["nome", "profissao"]


def carregar_respostas():
    if "--stdin" in sys.argv:
        return json.load(sys.stdin)
    if "--respostas" in sys.argv:
        caminho = sys.argv[sys.argv.index("--respostas") + 1]
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    print("Uso: primeira_vez.py --respostas arquivo.json  (ou --stdin)", file=sys.stderr)
    sys.exit(1)


def validar(r):
    faltando = [c for c in CAMPOS_OBRIG if not r.get(c)]
    if faltando:
        print("ERRO: faltam respostas: " + ", ".join(faltando), file=sys.stderr)
        sys.exit(1)


def gravar_config(r):
    os.makedirs(DIR_CFG, exist_ok=True)
    cfg = {
        "nome": r["nome"],
        "profissao": r["profissao"],
        "forcas": r.get("forcas", []),
        "ferramentas": r.get("ferramentas", []),
        "clientes_possiveis": r.get("clientes_possiveis", ""),
        "cor": r.get("cor", "#3b5bdb"),
        "logo": r.get("logo", ""),
        "tom": r.get("tom", "proximo e simples"),
        "moeda": r.get("moeda", "BRL"),
        "canais": r.get("canais", []),
    }
    with open(os.path.join(DIR_CFG, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    linhas = ["# Configuracao da Forja", "",
              "Nome: **%s**" % cfg["nome"],
              "Profissao / experiencia: %s" % cfg["profissao"],
              "Tom de voz: %s" % cfg["tom"],
              "Moeda: %s" % cfg["moeda"],
              "Cor da marca: %s" % cfg["cor"]]
    if cfg["logo"]:
        linhas.append("Logo: %s" % cfg["logo"])
    if cfg["forcas"]:
        linhas += ["", "## Forcas (o que faz bem)"] + ["- " + x for x in cfg["forcas"]]
    if cfg["ferramentas"]:
        linhas += ["", "## Ferramentas / IA que ja usa"] + ["- " + x for x in cfg["ferramentas"]]
    if cfg["clientes_possiveis"]:
        linhas += ["", "## Clientes possiveis", cfg["clientes_possiveis"]]
    if cfg["canais"]:
        linhas += ["", "## Canais que ja tem"] + ["- " + x for x in cfg["canais"]]
    linhas.append("")
    with open(os.path.join(DIR_CFG, "config.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))


def ajustar_gitignore():
    gi = os.path.join(PROJ, ".gitignore")
    linha = ".forja/"
    existentes = ""
    if os.path.exists(gi):
        with open(gi, encoding="utf-8") as f:
            existentes = f.read()
    if linha not in existentes:
        with open(gi, "a", encoding="utf-8") as f:
            if existentes and not existentes.endswith("\n"):
                f.write("\n")
            f.write(linha + "\n")


def limpar_skill_md():
    """Remove o bloco entre <!-- SETUP:START --> e <!-- SETUP:END -->."""
    caminho = os.path.join(RAIZ_SKILL, "SKILL.md")
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding="utf-8") as f:
        txt = f.read()
    ini, fim = "<!-- SETUP:START -->", "<!-- SETUP:END -->"
    if ini in txt and fim in txt:
        antes = txt.split(ini)[0]
        depois = txt.split(fim)[1]
        nota = ("> A Forja ja esta configurada para este projeto "
                "(veja `.forja/config.md`).\n")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(antes + nota + depois)


def autodestruir():
    p = os.path.join(RAIZ_SKILL, "respostas_exemplo.json")
    if os.path.exists(p):
        os.remove(p)
    pasta_setup = os.path.join(RAIZ_SKILL, "setup")
    if os.path.isdir(pasta_setup):
        shutil.rmtree(pasta_setup, ignore_errors=True)
    try:
        os.remove(os.path.abspath(__file__))
    except OSError:
        pass


def main():
    r = carregar_respostas()
    validar(r)
    gravar_config(r)
    ajustar_gitignore()
    limpar_skill_md()
    print("Forja configurada! Config em .forja/config.md.")
    print("Removendo os arquivos de primeira vez...")
    autodestruir()
    print("Pronto. A skill esta limpa e pronta para usar.")


if __name__ == "__main__":
    main()
