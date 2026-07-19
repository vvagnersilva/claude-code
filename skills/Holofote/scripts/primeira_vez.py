#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Primeira vez do Holofote - grava o perfil de conteudo e depois se autodestroi.

NAO e interativo. O Claude conversa com o dono, monta um JSON com as respostas e chama:

    python3 scripts/primeira_vez.py --perfil /tmp/perfil_holofote.json
    (ou:  cat perfil.json | python3 scripts/primeira_vez.py --stdin)

O script entao:
  1. grava .holofote/config.json (motor) e .holofote/config.md (legivel)
  2. cria .holofote/calendario.csv e .holofote/banco.csv vazios
  3. semeia o banco com as ideias iniciais informadas (se houver)
  4. garante .holofote/ no .gitignore
  5. remove o bloco de Primeira vez do SKILL.md (entre os marcadores)
  6. se apaga (e apaga o exemplo de perfil), deixando a skill limpa
"""

import csv
import datetime as dt
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ_SKILL = os.path.dirname(AQUI)


def raiz_projeto():
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
DIR = os.path.join(PROJ, ".holofote")

PILARES_PADRAO = ["Educar", "Bastidores", "Prova social", "Oferta"]
CAMPOS_OBRIG = ["negocio", "nicho"]


def carregar_perfil():
    if "--stdin" in sys.argv:
        return json.load(sys.stdin)
    if "--perfil" in sys.argv:
        caminho = sys.argv[sys.argv.index("--perfil") + 1]
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    print("Uso: primeira_vez.py --perfil arquivo.json  (ou --stdin)", file=sys.stderr)
    sys.exit(1)


def validar(r):
    faltando = [c for c in CAMPOS_OBRIG if not r.get(c)]
    if faltando:
        print("ERRO: faltam respostas: " + ", ".join(faltando), file=sys.stderr)
        sys.exit(1)


def gravar_config(r):
    os.makedirs(DIR, exist_ok=True)
    cfg = {
        "negocio": r["negocio"],
        "nicho": r["nicho"],
        "publico": r.get("publico", ""),
        "tom": r.get("tom", "proximo, claro e sem jargao"),
        "pilares": r.get("pilares") or PILARES_PADRAO,
        "plataformas": r.get("plataformas") or ["Instagram"],
        "frequencia_semanal": int(r.get("frequencia_semanal", 3)),
        "assinatura": r.get("assinatura", r["negocio"]),
        "cta_padrao": r.get("cta_padrao", "Chama no direct/WhatsApp para saber mais."),
        "nao_falar": r.get("nao_falar", []),
    }
    with open(os.path.join(DIR, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    L = ["# Configuracao do Holofote", "",
         "Negocio: **%s**" % cfg["negocio"],
         "Nicho: %s" % cfg["nicho"],
         "Publico-alvo: %s" % (cfg["publico"] or "(definir)"),
         "Tom de voz: %s" % cfg["tom"],
         "Plataformas: %s" % ", ".join(cfg["plataformas"]),
         "Frequencia: %d posts por semana" % cfg["frequencia_semanal"],
         "Assinatura/perfil: %s" % cfg["assinatura"],
         "CTA padrao: %s" % cfg["cta_padrao"],
         "", "## Pilares de conteudo"]
    for p in cfg["pilares"]:
        L.append("- %s" % p)
    if cfg["nao_falar"]:
        L += ["", "## Assuntos/expressoes a evitar"]
        for x in cfg["nao_falar"]:
            L.append("- %s" % x)
    L.append("")
    with open(os.path.join(DIR, "config.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return cfg


def criar_csvs(r):
    cols_cal = ["id", "data", "pilar", "tema", "formato", "plataforma", "gancho", "status", "publicado_em"]
    with open(os.path.join(DIR, "calendario.csv"), "w", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=cols_cal).writeheader()

    cols_banco = ["id", "tipo", "texto", "pilar", "criado_em", "usado_em"]
    linhas = []
    hoje = dt.date.today().strftime("%Y-%m-%d")
    for i, ideia in enumerate(r.get("ideias_iniciais", []), 1):
        if isinstance(ideia, dict):
            txt, pil, tipo = ideia.get("texto", ""), ideia.get("pilar", ""), ideia.get("tipo", "ideia")
        else:
            txt, pil, tipo = str(ideia), "", "ideia"
        linhas.append({"id": str(i), "tipo": tipo, "texto": txt, "pilar": pil,
                       "criado_em": hoje, "usado_em": ""})
    with open(os.path.join(DIR, "banco.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols_banco)
        w.writeheader()
        for l in linhas:
            w.writerow(l)
    return len(linhas)


def ajustar_gitignore():
    gi = os.path.join(PROJ, ".gitignore")
    linha = ".holofote/"
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
    caminho = os.path.join(RAIZ_SKILL, "SKILL.md")
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding="utf-8") as f:
        txt = f.read()
    ini, fim = "<!-- SETUP:START -->", "<!-- SETUP:END -->"
    if ini in txt and fim in txt:
        antes = txt.split(ini)[0]
        depois = txt.split(fim)[1]
        nota = "> Holofote ja esta configurado para este projeto (veja `.holofote/config.md`).\n"
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(antes + nota + depois)


def autodestruir():
    for nome in ("perfil_exemplo.json",):
        p = os.path.join(RAIZ_SKILL, nome)
        if os.path.exists(p):
            os.remove(p)
    try:
        os.remove(os.path.abspath(__file__))
    except OSError:
        pass


def main():
    r = carregar_perfil()
    validar(r)
    cfg = gravar_config(r)
    n = criar_csvs(r)
    ajustar_gitignore()
    limpar_skill_md()
    print("Holofote configurado! Perfil em .holofote/config.md, %d pilares, %d ideias no banco."
          % (len(cfg["pilares"]), n))
    print("Removendo os arquivos de primeira vez...")
    autodestruir()
    print("Pronto. A skill esta limpa e pronta para criar conteudo.")


if __name__ == "__main__":
    main()
