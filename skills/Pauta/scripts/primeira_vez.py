#!/usr/bin/env python3
"""Primeira vez do Pauta - grava a configuracao e depois se autodestroi.

NAO e interativo. O Claude coleta as respostas com o usuario, monta um JSON
de respostas e chama:

    python3 scripts/primeira_vez.py --respostas /caminho/respostas.json

ou passando o JSON por stdin:

    cat respostas.json | python3 scripts/primeira_vez.py --stdin

O script entao:
  1. grava .pauta/config.json (lido pelo motor) e .pauta/config.md (legivel)
  2. cria .pauta/agenda.csv vazia
  3. garante que .pauta/ esteja no .gitignore
  4. remove o bloco de Primeira vez do SKILL.md (entre os marcadores)
  5. se apaga (e apaga o exemplo de respostas), deixando a skill limpa
"""

import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ_SKILL = os.path.dirname(AQUI)           # pasta da skill (onde fica o SKILL.md)


def raiz_projeto():
    """Raiz do projeto do usuario, mesmo rodando de dentro de .claude/skills/pauta."""
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


PROJ = raiz_projeto()                         # projeto do usuario
DIR_CFG = os.path.join(PROJ, ".pauta")

CAMPOS_OBRIG = ["negocio", "servicos", "horario"]


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
        "negocio": r["negocio"],
        "tipo": r.get("tipo", ""),
        "profissionais": r.get("profissionais", []),
        "servicos": r["servicos"],
        "horario": r["horario"],
        "intervalo": r.get("intervalo", ""),
        "granularidade_min": r.get("granularidade_min", 30),
        "canal": r.get("canal", "WhatsApp"),
        "tom": r.get("tom", "profissional e cordial"),
        "assinatura": r.get("assinatura", r["negocio"]),
        "antecedencia_remarcacao_horas": r.get("antecedencia_remarcacao_horas", 24),
        "lembrete_dias": r.get("lembrete_dias", [2, 1]),
    }
    with open(os.path.join(DIR_CFG, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    linhas = ["# Configuracao do Pauta", "",
              "Negocio: **%s**%s" % (cfg["negocio"], " (" + cfg["tipo"] + ")" if cfg["tipo"] else ""),
              "Canal preferido: %s" % cfg["canal"],
              "Tom das mensagens: %s" % cfg["tom"],
              "Assinatura: %s" % cfg["assinatura"], ""]
    if cfg["profissionais"]:
        linhas.append("Profissionais: " + ", ".join(cfg["profissionais"]))
    linhas += ["", "## Servicos"]
    for s in cfg["servicos"]:
        linhas.append("- %s - %dmin - R$%s - retorno em %s dias" % (
            s["nome"], s.get("duracao_min", 30), s.get("preco", "?"),
            s.get("retorno_dias", "-")))
    linhas += ["", "## Horario de funcionamento"]
    for d in ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]:
        j = cfg["horario"].get(d, [])
        linhas.append("- %s: %s" % (d, ", ".join(j) if j else "fechado"))
    if cfg["intervalo"]:
        linhas.append("- intervalo: " + cfg["intervalo"])
    linhas += ["", "Lembretes: D-%s." % ", D-".join(str(x) for x in cfg["lembrete_dias"]),
               "Remarcacao com %dh de antecedencia." % cfg["antecedencia_remarcacao_horas"], ""]
    with open(os.path.join(DIR_CFG, "config.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))


def criar_agenda():
    agenda = os.path.join(DIR_CFG, "agenda.csv")
    if not os.path.exists(agenda):
        cols = ["id", "cliente", "telefone", "servico", "profissional",
                "data", "hora", "duracao_min", "status", "valor", "obs"]
        with open(agenda, "w", encoding="utf-8") as f:
            f.write(",".join(cols) + "\n")


def ajustar_gitignore():
    gi = os.path.join(PROJ, ".gitignore")
    linha = ".pauta/"
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
        nota = ("> Pauta ja esta configurada para este projeto "
                "(veja `.pauta/config.md`).\n")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(antes + nota + depois)


def autodestruir():
    for nome in ("respostas_exemplo.json",):
        p = os.path.join(RAIZ_SKILL, nome)
        if os.path.exists(p):
            os.remove(p)
    try:
        os.remove(os.path.abspath(__file__))
    except OSError:
        pass


def main():
    r = carregar_respostas()
    validar(r)
    gravar_config(r)
    criar_agenda()
    ajustar_gitignore()
    limpar_skill_md()
    print("Pauta configurada! Config em .pauta/config.md e agenda em .pauta/agenda.csv.")
    print("Removendo os arquivos de primeira vez...")
    autodestruir()
    print("Pronto. A skill esta limpa e pronta para o dia a dia.")


if __name__ == "__main__":
    main()
