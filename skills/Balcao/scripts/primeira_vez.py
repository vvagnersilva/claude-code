#!/usr/bin/env python3
"""Primeira vez do Balcao - grava a base de conhecimento e depois se autodestroi.

NAO e interativo. O Claude coleta as respostas com o dono, monta um JSON e chama:

    python3 scripts/primeira_vez.py --respostas /tmp/respostas_balcao.json
    (ou:  cat respostas.json | python3 scripts/primeira_vez.py --stdin)

O script entao:
  1. grava .balcao/config.json (motor) e .balcao/config.md (legivel)
  2. grava .balcao/base.md a partir das respostas (servicos, precos, horarios, politicas)
  3. semeia .balcao/faq.csv com as perguntas e respostas informadas
  4. cria .balcao/lacunas.csv vazio
  5. garante .balcao/ no .gitignore
  6. remove o bloco de Primeira vez do SKILL.md (entre os marcadores)
  7. se apaga (e apaga o exemplo de respostas), deixando a skill limpa
"""

import csv
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
DIR = os.path.join(PROJ, ".balcao")

CAMPOS_OBRIG = ["negocio", "horario"]


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
    os.makedirs(DIR, exist_ok=True)
    cfg = {
        "negocio": r["negocio"],
        "tipo": r.get("tipo", ""),
        "canal": r.get("canal", "WhatsApp"),
        "tom": r.get("tom", "cordial, claro e proximo"),
        "assinatura": r.get("assinatura", r["negocio"]),
        "fora_horario": r.get("fora_horario",
                              "No momento estamos fora do horario de atendimento. "
                              "Assim que abrirmos retornamos sua mensagem!"),
        "encaminhar_agendamento": r.get("encaminhar_agendamento", True),
    }
    with open(os.path.join(DIR, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    linhas = ["# Configuracao do Balcao", "",
              "Negocio: **%s**%s" % (cfg["negocio"], " (" + cfg["tipo"] + ")" if cfg["tipo"] else ""),
              "Canal preferido: %s" % cfg["canal"],
              "Tom das respostas: %s" % cfg["tom"],
              "Assinatura: %s" % cfg["assinatura"],
              "", "Mensagem fora do horario: " + cfg["fora_horario"], ""]
    with open(os.path.join(DIR, "config.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    return cfg


def gravar_base(r, cfg):
    """Monta a base de conhecimento legivel a partir das respostas."""
    L = ["# Base de conhecimento - %s" % cfg["negocio"], "",
         "Tudo que o Balcao usa para responder ao cliente. Mantenha atualizado:",
         "adicione aqui (ou pelo modo Base) tudo que voce responde com frequencia.", ""]

    if r.get("horario"):
        L += ["## Horario de funcionamento"]
        h = r["horario"]
        if isinstance(h, dict):
            for d in ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]:
                v = h.get(d)
                L.append("- %s: %s" % (d, v if v else "fechado"))
        else:
            L.append(str(h))
        L.append("")

    if r.get("endereco"):
        L += ["## Onde fica", r["endereco"], ""]

    if r.get("servicos"):
        L += ["## Servicos e precos"]
        for s in r["servicos"]:
            if isinstance(s, dict):
                preco = (" - R$ %s" % s["preco"]) if s.get("preco") else ""
                desc = (" - %s" % s["descricao"]) if s.get("descricao") else ""
                L.append("- **%s**%s%s" % (s.get("nome", "?"), preco, desc))
            else:
                L.append("- %s" % s)
        L.append("")

    if r.get("pagamento"):
        formas = r["pagamento"]
        L += ["## Formas de pagamento",
              ", ".join(formas) if isinstance(formas, list) else str(formas), ""]

    if r.get("politicas"):
        L += ["## Politicas (garantia, cancelamento, prazos)"]
        pol = r["politicas"]
        if isinstance(pol, list):
            for p in pol:
                L.append("- %s" % p)
        else:
            L.append(str(pol))
        L.append("")

    if r.get("nao_fazemos"):
        L += ["## O que NAO fazemos (seja honesto com o cliente)"]
        for x in r["nao_fazemos"]:
            L.append("- %s" % x)
        L.append("")

    with open(os.path.join(DIR, "base.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def semear_faq(r):
    cols = ["id", "pergunta", "resposta", "categoria", "tags", "vezes_perguntada"]
    linhas = []
    for i, qa in enumerate(r.get("faq", []), 1):
        linhas.append({
            "id": str(i),
            "pergunta": qa.get("pergunta", ""),
            "resposta": qa.get("resposta", ""),
            "categoria": qa.get("categoria", "geral"),
            "tags": qa.get("tags", ""),
            "vezes_perguntada": "1",
        })
    with open(os.path.join(DIR, "faq.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for l in linhas:
            w.writerow(l)
    # lacunas vazio
    with open(os.path.join(DIR, "lacunas.csv"), "w", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=["id", "pergunta", "cliente", "status"]).writeheader()
    return len(linhas)


def ajustar_gitignore():
    gi = os.path.join(PROJ, ".gitignore")
    linha = ".balcao/"
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
        nota = "> Balcao ja esta configurado para este projeto (veja `.balcao/base.md`).\n"
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
    cfg = gravar_config(r)
    gravar_base(r, cfg)
    n = semear_faq(r)
    ajustar_gitignore()
    limpar_skill_md()
    print("Balcao configurado! Base em .balcao/base.md, %d perguntas no banco (.balcao/faq.csv)." % n)
    print("Removendo os arquivos de primeira vez...")
    autodestruir()
    print("Pronto. A skill esta limpa e pronta para atender.")


if __name__ == "__main__":
    main()
