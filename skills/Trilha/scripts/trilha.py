#!/usr/bin/env python3
"""
Trilha — motor local do seu professor particular de IA.

Cuida da papelada (missões, status, progresso, ofensiva de dias seguidos) de um
jeito sempre consistente, pra que o tutor nunca precise inventar número. Só usa a
biblioteca padrão do Python — não instala nada, não acessa a internet.

Os dados ficam em `.trilha/` na raiz do projeto da pessoa:
  - config.md     -> perfil (profissão, nível, objetivo, tom...)  [criado no setup]
  - missoes.csv   -> a trilha: id, ordem, titulo, modulo, status, data_conclusao
"""

import argparse
import csv
import os
import sys
from datetime import date, datetime, timedelta

DADOS = ".trilha"
MISSOES = os.path.join(DADOS, "missoes.csv")
CAMPOS = ["id", "ordem", "titulo", "modulo", "status", "data_conclusao"]


# ----------------------------------------------------------------------------- util
def _garante_pasta():
    os.makedirs(DADOS, exist_ok=True)
    if not os.path.exists(MISSOES):
        with open(MISSOES, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CAMPOS).writeheader()


def _ler():
    _garante_pasta()
    with open(MISSOES, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _gravar(linhas):
    with open(MISSOES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for l in linhas:
            w.writerow({k: l.get(k, "") for k in CAMPOS})


def _proximo_id(linhas):
    return str(max([int(l["id"]) for l in linhas], default=0) + 1)


def _proxima_ordem(linhas):
    return max([int(l["ordem"]) for l in linhas], default=0) + 1


def _ordenar(linhas):
    return sorted(linhas, key=lambda l: int(l["ordem"]))


# --------------------------------------------------------------------------- comandos
def cmd_add(args):
    linhas = _ler()
    ordem = args.ordem if args.ordem is not None else _proxima_ordem(linhas)
    nova = {
        "id": _proximo_id(linhas),
        "ordem": str(ordem),
        "titulo": args.titulo.strip(),
        "modulo": (args.modulo or "").strip(),
        "status": "a_fazer",
        "data_conclusao": "",
    }
    linhas.append(nova)
    _gravar(linhas)
    print(f"+ Missão #{nova['id']} adicionada: {nova['titulo']}")


def cmd_proxima(_args):
    linhas = _ordenar(_ler())
    pend = [l for l in linhas if l["status"] != "feita"]
    if not pend:
        if linhas:
            print("TRILHA_COMPLETA")
        else:
            print("TRILHA_VAZIA")
        return
    m = pend[0]
    print(f"#{m['id']} | {m['modulo']} | {m['titulo']}")


def cmd_concluir(args):
    linhas = _ler()
    achou = False
    for l in linhas:
        if l["id"] == str(args.id):
            l["status"] = "feita"
            l["data_conclusao"] = date.today().isoformat()
            achou = True
            break
    if not achou:
        print(f"! Não achei a missão #{args.id}.")
        sys.exit(1)
    _gravar(linhas)
    print(f"✓ Missão #{args.id} concluída. Mandou bem!")


def _ofensiva(linhas):
    """Dias seguidos (até hoje ou ontem) com pelo menos 1 missão concluída."""
    dias = set()
    for l in linhas:
        d = l.get("data_conclusao", "")
        if d:
            try:
                dias.add(datetime.strptime(d, "%Y-%m-%d").date())
            except ValueError:
                pass
    if not dias:
        return 0
    hoje = date.today()
    # a ofensiva pode terminar hoje ou ontem (não quebrou ainda)
    if hoje in dias:
        ref = hoje
    elif (hoje - timedelta(days=1)) in dias:
        ref = hoje - timedelta(days=1)
    else:
        return 0
    n = 0
    while ref in dias:
        n += 1
        ref -= timedelta(days=1)
    return n


def cmd_progresso(_args):
    linhas = _ordenar(_ler())
    total = len(linhas)
    feitas = sum(1 for l in linhas if l["status"] == "feita")
    pct = round(feitas * 100 / total) if total else 0
    barra_cheia = round(pct / 10)
    barra = "█" * barra_cheia + "░" * (10 - barra_cheia)
    print(f"PROGRESSO: {feitas}/{total} missões ({pct}%)  [{barra}]")
    print(f"OFENSIVA: {_ofensiva(linhas)} dia(s) seguido(s)")
    pend = [l for l in linhas if l["status"] != "feita"]
    if pend:
        print(f"PROXIMA: #{pend[0]['id']} | {pend[0]['modulo']} | {pend[0]['titulo']}")
    elif total:
        print("PROXIMA: — trilha concluída! 🎉")
    else:
        print("PROXIMA: — trilha ainda não montada.")
    # módulos dominados (todos as missões do módulo feitas)
    mods = {}
    for l in linhas:
        mods.setdefault(l["modulo"], []).append(l["status"] == "feita")
    dominados = [m for m, st in mods.items() if m and all(st)]
    if dominados:
        print("DOMINADOS: " + ", ".join(dominados))


def cmd_listar(_args):
    linhas = _ordenar(_ler())
    if not linhas:
        print("(trilha vazia — monte a trilha primeiro)")
        return
    mod_atual = None
    for l in linhas:
        if l["modulo"] != mod_atual:
            mod_atual = l["modulo"]
            print(f"\n== {mod_atual or 'Sem módulo'} ==")
        marca = "✓" if l["status"] == "feita" else "·"
        data = f"  ({l['data_conclusao']})" if l["data_conclusao"] else ""
        print(f"  [{marca}] #{l['id']} {l['titulo']}{data}")


def cmd_limpar(_args):
    """Apaga só as missões (mantém o config/perfil)."""
    _gravar([])
    print("Trilha zerada. O perfil em .trilha/config.md foi mantido.")


# -------------------------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description="Motor local da skill Trilha.")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="adiciona uma missão à trilha")
    a.add_argument("--titulo", required=True)
    a.add_argument("--modulo", default="")
    a.add_argument("--ordem", type=int, default=None)
    a.set_defaults(func=cmd_add)

    sub.add_parser("proxima", help="mostra a próxima missão a fazer").set_defaults(func=cmd_proxima)

    c = sub.add_parser("concluir", help="marca uma missão como feita (data = hoje)")
    c.add_argument("--id", required=True)
    c.set_defaults(func=cmd_concluir)

    sub.add_parser("progresso", help="percentual, ofensiva e próxima missão").set_defaults(func=cmd_progresso)
    sub.add_parser("listar", help="lista todas as missões por módulo").set_defaults(func=cmd_listar)
    sub.add_parser("limpar", help="zera as missões (mantém o perfil)").set_defaults(func=cmd_limpar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
