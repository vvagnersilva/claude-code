#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bancada — motor da bancada de rotinas do dono de negócio.

A Bancada deixa o dono ENSINAR uma tarefa repetitiva uma vez (conversando em
português) e guardar como uma "receita". Depois, toda vez que ele precisar, é
só pedir para "rodar" a receita com uma entrada nova — e a tarefa sai sempre no
mesmo padrão e no mesmo tom. Este motor cuida APENAS de guardar, listar, contar
uso e editar as receitas. Quem EXECUTA a tarefa (a parte inteligente) é a IA,
lendo a receita que este motor entrega. Usa SOMENTE a biblioteca padrão.

Nunca inventa nada: cada receita é exatamente o que o dono ensinou.

Onde ficam os dados (tudo local, na pasta do usuário):
    .bancada/config.md            -> configuração (criada na primeira conversa)
    .bancada/receitas/<slug>.json -> uma receita por arquivo (fonte da verdade)

Formato de uma receita (.json):
    {
      "slug": "resumo-reuniao",
      "nome": "Resumo de reunião",
      "faz": "Transforma minhas anotações soltas num resumo com decisões e pendências",
      "gatilho": ["resumo da reunião", "resume essa reunião"],
      "entrada": "As anotações que eu colo da reunião",
      "passos": ["Separe o que foi decidido", "Liste as pendências com responsável", "..."],
      "saida": "Um resumo curto com 3 blocos: Resumo, Decisões, Pendências",
      "tom": "Direto e profissional",
      "exemplos": [{"entrada": "...", "saida": "..."}],
      "criada_em": "2026-06-21",
      "usos": 0,
      "ultimo_uso": ""
    }

Comandos:
    python3 bancada.py nova --nome "..." --faz "..." [--gatilho "g1||g2"]
            [--entrada "..."] [--passos "p1||p2||p3"] [--saida "..."] [--tom "..."]
            [--exemplo-entrada "..."] [--exemplo-saida "..."]
    python3 bancada.py listar                 # todas as receitas da bancada
    python3 bancada.py ver --slug X           # mostra a receita (para a IA seguir)
    python3 bancada.py usar --slug X          # igual ao ver + conta +1 uso
    python3 bancada.py editar --slug X [--nome ...] [--faz ...] [--gatilho ...]
            [--entrada ...] [--passos ...] [--saida ...] [--tom ...]
            [--add-exemplo-entrada ...] [--add-exemplo-saida ...]
    python3 bancada.py remover --slug X
    python3 bancada.py stats                  # painel da bancada
Opções globais: --pasta <dir>   (padrão: .bancada)
                --formato json  (padrão: texto)
"""

import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from datetime import date

PASTA_PADRAO = ".bancada"
SEP = "||"  # separador para listas passadas na linha de comando


# ---------------------------------------------------------------- utilidades

def _hoje():
    return date.today().isoformat()


def _norm(s):
    """minúsculas e sem acento, para gerar slug e comparar."""
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _slugify(nome):
    base = _norm(nome)
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or "receita"


def _dir_receitas(pasta):
    return os.path.join(pasta, "receitas")


def _caminho(pasta, slug):
    return os.path.join(_dir_receitas(pasta), slug + ".json")


def _slug_unico(pasta, nome):
    """gera um slug que ainda não existe (acrescenta -2, -3... se preciso)."""
    base = _slugify(nome)
    slug = base
    n = 2
    while os.path.exists(_caminho(pasta, slug)):
        slug = "{}-{}".format(base, n)
        n += 1
    return slug


def _split(valor):
    if not valor:
        return []
    return [p.strip() for p in valor.split(SEP) if p.strip()]


def _carregar(pasta, slug):
    caminho = _caminho(pasta, slug)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _salvar(pasta, receita):
    os.makedirs(_dir_receitas(pasta), exist_ok=True)
    caminho = _caminho(pasta, receita["slug"])
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(receita, f, ensure_ascii=False, indent=2)
    return caminho


def _todas(pasta):
    arquivos = sorted(glob.glob(os.path.join(_dir_receitas(pasta), "*.json")))
    receitas = []
    for a in arquivos:
        try:
            with open(a, encoding="utf-8") as f:
                receitas.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    return receitas


def _erro(msg):
    print("ERRO: " + msg)
    sys.exit(1)


# ---------------------------------------------------------------- renderização

def _render_receita(r):
    """desenha a receita como texto claro para a IA seguir ao executar."""
    linhas = []
    linhas.append("RECEITA: {}".format(r["nome"]))
    linhas.append("(slug: {})".format(r["slug"]))
    linhas.append("")
    linhas.append("O que faz: {}".format(r.get("faz", "")))
    gat = r.get("gatilho", [])
    if gat:
        linhas.append("Gatilhos: " + " / ".join('"{}"'.format(g) for g in gat))
    if r.get("entrada"):
        linhas.append("Entrada esperada: {}".format(r["entrada"]))
    if r.get("saida"):
        linhas.append("Formato de saída: {}".format(r["saida"]))
    if r.get("tom"):
        linhas.append("Tom / regras: {}".format(r["tom"]))
    passos = r.get("passos", [])
    if passos:
        linhas.append("")
        linhas.append("Passos a seguir:")
        for i, p in enumerate(passos, 1):
            linhas.append("  {}. {}".format(i, p))
    exemplos = r.get("exemplos", [])
    if exemplos:
        linhas.append("")
        linhas.append("Exemplos de referência:")
        for i, ex in enumerate(exemplos, 1):
            linhas.append("  Exemplo {} — entrada:".format(i))
            linhas.append("    {}".format(ex.get("entrada", "").replace("\n", "\n    ")))
            linhas.append("  Exemplo {} — saída:".format(i))
            linhas.append("    {}".format(ex.get("saida", "").replace("\n", "\n    ")))
    linhas.append("")
    linhas.append("Usos até agora: {} | Último uso: {}".format(
        r.get("usos", 0), r.get("ultimo_uso") or "nunca"))
    return "\n".join(linhas)


# ---------------------------------------------------------------- comandos

def cmd_nova(args):
    pasta = args.pasta
    if not args.nome:
        _erro("a receita precisa de um --nome.")
    slug = _slug_unico(pasta, args.nome)
    receita = {
        "slug": slug,
        "nome": args.nome.strip(),
        "faz": (args.faz or "").strip(),
        "gatilho": _split(args.gatilho),
        "entrada": (args.entrada or "").strip(),
        "passos": _split(args.passos),
        "saida": (args.saida or "").strip(),
        "tom": (args.tom or "").strip(),
        "exemplos": [],
        "criada_em": _hoje(),
        "usos": 0,
        "ultimo_uso": "",
    }
    if args.exemplo_entrada or args.exemplo_saida:
        receita["exemplos"].append({
            "entrada": (args.exemplo_entrada or "").strip(),
            "saida": (args.exemplo_saida or "").strip(),
        })
    caminho = _salvar(pasta, receita)
    if args.formato == "json":
        print(json.dumps(receita, ensure_ascii=False, indent=2))
    else:
        print("Receita criada: {}  (slug: {})".format(receita["nome"], slug))
        print("Arquivo: {}".format(caminho))
    return slug


def cmd_listar(args):
    receitas = _todas(args.pasta)
    if args.formato == "json":
        print(json.dumps(receitas, ensure_ascii=False, indent=2))
        return
    if not receitas:
        print("A bancada ainda está vazia. Ensine a primeira rotina com o modo Ensinar.")
        return
    print("Sua bancada tem {} receita(s):".format(len(receitas)))
    print("")
    for r in receitas:
        gat = r.get("gatilho", [])
        gat_txt = (' — dispara com: "{}"'.format(gat[0])) if gat else ""
        print("• {}  (slug: {})".format(r["nome"], r["slug"]))
        if r.get("faz"):
            print("    {}".format(r["faz"]))
        print("    usos: {}{}".format(r.get("usos", 0), gat_txt))


def cmd_ver(args, contar=False):
    r = _carregar(args.pasta, args.slug)
    if r is None:
        _erro('não encontrei a receita "{}". Use "listar" para ver os slugs.'.format(args.slug))
    if contar:
        r["usos"] = int(r.get("usos", 0)) + 1
        r["ultimo_uso"] = _hoje()
        _salvar(args.pasta, r)
    if args.formato == "json":
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(_render_receita(r))


def cmd_editar(args):
    r = _carregar(args.pasta, args.slug)
    if r is None:
        _erro('não encontrei a receita "{}".'.format(args.slug))
    if args.nome:
        r["nome"] = args.nome.strip()
    if args.faz is not None:
        r["faz"] = args.faz.strip()
    if args.gatilho is not None:
        r["gatilho"] = _split(args.gatilho)
    if args.entrada is not None:
        r["entrada"] = args.entrada.strip()
    if args.passos is not None:
        r["passos"] = _split(args.passos)
    if args.saida is not None:
        r["saida"] = args.saida.strip()
    if args.tom is not None:
        r["tom"] = args.tom.strip()
    if args.add_exemplo_entrada or args.add_exemplo_saida:
        r.setdefault("exemplos", []).append({
            "entrada": (args.add_exemplo_entrada or "").strip(),
            "saida": (args.add_exemplo_saida or "").strip(),
        })
    _salvar(args.pasta, r)
    if args.formato == "json":
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("Receita atualizada: {}  (slug: {})".format(r["nome"], r["slug"]))


def cmd_remover(args):
    caminho = _caminho(args.pasta, args.slug)
    if not os.path.exists(caminho):
        _erro('não encontrei a receita "{}".'.format(args.slug))
    os.remove(caminho)
    print('Receita "{}" removida da bancada.'.format(args.slug))


def cmd_stats(args):
    receitas = _todas(args.pasta)
    total = len(receitas)
    usos_total = sum(int(r.get("usos", 0)) for r in receitas)
    mais_usadas = sorted(receitas, key=lambda r: int(r.get("usos", 0)), reverse=True)[:5]
    nunca = [r for r in receitas if int(r.get("usos", 0)) == 0]
    if args.formato == "json":
        print(json.dumps({
            "total": total,
            "usos_total": usos_total,
            "mais_usadas": [{"slug": r["slug"], "nome": r["nome"], "usos": int(r.get("usos", 0))} for r in mais_usadas],
            "nunca_usadas": [r["slug"] for r in nunca],
        }, ensure_ascii=False, indent=2))
        return
    print("Painel da Bancada")
    print("-----------------")
    print("Receitas guardadas: {}".format(total))
    print("Vezes que você usou a bancada: {}".format(usos_total))
    if mais_usadas and usos_total > 0:
        print("")
        print("Mais usadas:")
        for r in mais_usadas:
            if int(r.get("usos", 0)) > 0:
                print("  • {} — {} uso(s)".format(r["nome"], r.get("usos", 0)))
    if nunca:
        print("")
        print("Ainda não usou ({}): {}".format(
            len(nunca), ", ".join(r["nome"] for r in nunca)))


# ---------------------------------------------------------------- CLI

def construir_parser():
    p = argparse.ArgumentParser(description="Bancada — motor da bancada de rotinas.")
    p.add_argument("--pasta", default=PASTA_PADRAO, help="pasta de dados (padrão: .bancada)")
    p.add_argument("--formato", default="texto", choices=["texto", "json"])
    sub = p.add_subparsers(dest="comando", required=True)

    n = sub.add_parser("nova", help="cria uma nova receita")
    n.add_argument("--nome", required=True)
    n.add_argument("--faz", default="")
    n.add_argument("--gatilho", default="")
    n.add_argument("--entrada", default="")
    n.add_argument("--passos", default="")
    n.add_argument("--saida", default="")
    n.add_argument("--tom", default="")
    n.add_argument("--exemplo-entrada", dest="exemplo_entrada", default="")
    n.add_argument("--exemplo-saida", dest="exemplo_saida", default="")

    sub.add_parser("listar", help="lista todas as receitas")

    v = sub.add_parser("ver", help="mostra uma receita")
    v.add_argument("--slug", required=True)

    u = sub.add_parser("usar", help="mostra uma receita e conta +1 uso")
    u.add_argument("--slug", required=True)

    e = sub.add_parser("editar", help="edita uma receita existente")
    e.add_argument("--slug", required=True)
    e.add_argument("--nome", default=None)
    e.add_argument("--faz", default=None)
    e.add_argument("--gatilho", default=None)
    e.add_argument("--entrada", default=None)
    e.add_argument("--passos", default=None)
    e.add_argument("--saida", default=None)
    e.add_argument("--tom", default=None)
    e.add_argument("--add-exemplo-entrada", dest="add_exemplo_entrada", default="")
    e.add_argument("--add-exemplo-saida", dest="add_exemplo_saida", default="")

    r = sub.add_parser("remover", help="apaga uma receita")
    r.add_argument("--slug", required=True)

    sub.add_parser("stats", help="painel da bancada")
    return p


def main(argv=None):
    args = construir_parser().parse_args(argv)
    if args.comando == "nova":
        cmd_nova(args)
    elif args.comando == "listar":
        cmd_listar(args)
    elif args.comando == "ver":
        cmd_ver(args, contar=False)
    elif args.comando == "usar":
        cmd_ver(args, contar=True)
    elif args.comando == "editar":
        cmd_editar(args)
    elif args.comando == "remover":
        cmd_remover(args)
    elif args.comando == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
