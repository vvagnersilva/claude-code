#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lupa — motor local (só biblioteca padrão do Python).

A Lupa LÊ o documento com a própria IA. Este motor cuida só da parte mecânica
e exata, que não pode depender de "achismo":

  • prazos/obrigações  -> guarda, ordena por data, calcula dias que faltam,
                          marca VENCIDO / VENCE HOJE / PERTO.
  • comparar versões   -> diferença linha a linha entre dois arquivos de texto.

Tudo é gravado em ./.lupa/ na pasta atual. Nada vai para a internet.
Datas no padrão do Brasil: DD/MM/AAAA (também aceita DD/MM/AA, AAAA-MM-DD e
"31 de dezembro de 2026").

Uso:
  python3 lupa.py add-prazo --doc "Contrato X" --desc "Pagar 1ª parcela" --data 10/07/2026 [--quem "Empresa"] [--tipo prazo|obrigacao]
  python3 lupa.py prazos [--doc "Contrato X"] [--dias 30]
  python3 lupa.py concluir --id 3
  python3 lupa.py remover --id 3
  python3 lupa.py comparar --a versao1.txt --b versao2.txt
"""

import argparse
import csv
import datetime
import os
import re
import sys
import difflib

DIR = ".lupa"
PRAZOS = os.path.join(DIR, "prazos.csv")
CAMPOS = ["id", "doc", "tipo", "desc", "quem", "data", "status"]

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}


def hoje():
    return datetime.date.today()


def garante_dir():
    os.makedirs(DIR, exist_ok=True)
    if not os.path.exists(PRAZOS):
        with open(PRAZOS, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CAMPOS).writeheader()


def parse_data(txt):
    """Converte texto de data BR em datetime.date. Levanta ValueError se não der."""
    if not txt:
        raise ValueError("data vazia")
    t = txt.strip().lower()
    # 31 de dezembro de 2026  /  31 de dezembro 2026
    m = re.search(r"(\d{1,2})\s+de\s+([a-zç]+)\s+(?:de\s+)?(\d{4})", t)
    if m:
        d, mes, a = int(m.group(1)), m.group(2), int(m.group(3))
        if mes in MESES:
            return datetime.date(a, MESES[mes], d)
    # AAAA-MM-DD
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", t)
    if m:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # DD/MM/AAAA ou DD/MM/AA  (também aceita . ou - como separador)
    m = re.match(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})$", t)
    if m:
        d, mes, a = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if a < 100:
            a += 2000
        return datetime.date(a, mes, d)
    raise ValueError(f"não entendi a data: {txt!r} (use DD/MM/AAAA)")


def ler():
    garante_dir()
    with open(PRAZOS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def grava(linhas):
    with open(PRAZOS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for l in linhas:
            w.writerow({k: l.get(k, "") for k in CAMPOS})


def novo_id(linhas):
    ids = [int(l["id"]) for l in linhas if str(l.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


def cmd_add(a):
    try:
        d = parse_data(a.data)  # valida e normaliza
    except ValueError as e:
        print(f"Data não reconhecida ({e}). Use o formato DD/MM/AAAA, ex.: 31/12/2026.")
        sys.exit(1)
    linhas = ler()
    item = {
        "id": str(novo_id(linhas)),
        "doc": a.doc or "",
        "tipo": a.tipo or "prazo",
        "desc": a.desc,
        "quem": a.quem or "",
        "data": d.strftime("%d/%m/%Y"),
        "status": "aberto",
    }
    linhas.append(item)
    grava(linhas)
    print(f"OK — registrado #{item['id']}: {item['desc']} — {item['data']}")


def faixa(dias):
    if dias < 0:
        return "VENCIDO"
    if dias == 0:
        return "VENCE HOJE"
    if dias <= 7:
        return "PERTO"
    return "ok"


def cmd_prazos(a):
    linhas = [l for l in ler() if l.get("status") == "aberto"]
    if a.doc:
        alvo = a.doc.strip().lower()
        linhas = [l for l in linhas if alvo in (l.get("doc", "").lower())]
    hj = hoje()
    enriq = []
    for l in linhas:
        try:
            d = parse_data(l["data"])
        except ValueError:
            continue
        dias = (d - hj).days
        if a.dias is not None and dias > a.dias:
            continue
        enriq.append((dias, l))
    enriq.sort(key=lambda x: x[0])
    if not enriq:
        print("Nenhum prazo/obrigação em aberto" + (f" nos próximos {a.dias} dias." if a.dias is not None else "."))
        return
    print(f"PRAZOS E OBRIGAÇÕES EM ABERTO  (hoje: {hj.strftime('%d/%m/%Y')})\n")
    rotulo = {"VENCIDO": "🔴 VENCIDO", "VENCE HOJE": "🟠 VENCE HOJE",
              "PERTO": "🟡 PERTO", "ok": "🟢"}
    for dias, l in enriq:
        f = faixa(dias)
        if dias < 0:
            quando = f"há {abs(dias)} dia(s)"
        elif dias == 0:
            quando = "hoje"
        else:
            quando = f"em {dias} dia(s)"
        quem = f" — {l['quem']}" if l.get("quem") else ""
        doc = f"  [{l['doc']}]" if l.get("doc") else ""
        tipo = l.get("tipo", "prazo")
        print(f"  #{l['id']} {rotulo[f]:14} {l['data']} ({quando}) · {tipo}{doc}")
        print(f"       {l['desc']}{quem}")
    print(f"\nTotal: {len(enriq)} item(ns). Conclua com:  python3 lupa.py concluir --id N")


def cmd_concluir(a):
    linhas = ler()
    achou = False
    for l in linhas:
        if str(l.get("id")) == str(a.id):
            l["status"] = "concluido"
            achou = True
            print(f"OK — #{a.id} concluído: {l['desc']}")
    if not achou:
        print(f"Não achei o item #{a.id}.")
        sys.exit(1)
    grava(linhas)


def cmd_remover(a):
    linhas = ler()
    n = len(linhas)
    linhas = [l for l in linhas if str(l.get("id")) != str(a.id)]
    if len(linhas) == n:
        print(f"Não achei o item #{a.id}.")
        sys.exit(1)
    grava(linhas)
    print(f"OK — #{a.id} removido.")


def _le_texto(caminho):
    if not os.path.exists(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        sys.exit(1)
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def cmd_comparar(a):
    va = _le_texto(a.a)
    vb = _le_texto(a.b)
    add = rem = 0
    print(f"COMPARANDO\n  A (antiga): {a.a}\n  B (nova):   {a.b}\n")
    saida = []
    for linha in difflib.unified_diff(va, vb, lineterm="", n=1):
        if linha.startswith("+++") or linha.startswith("---"):
            continue
        if linha.startswith("@@"):
            saida.append("  …")
            continue
        if linha.startswith("+"):
            add += 1
            saida.append(f"  + (B) {linha[1:].strip()}")
        elif linha.startswith("-"):
            rem += 1
            saida.append(f"  - (A) {linha[1:].strip()}")
    if not saida:
        print("Os dois textos são idênticos.")
        return
    for s in saida[:400]:
        print(s)
    if len(saida) > 400:
        print(f"  … (+{len(saida) - 400} linhas de diferença)")
    print(f"\nResumo bruto: {add} adicionada(s) em B, {rem} removida(s) de A.")
    print("Peça à Lupa para resumir o que mudou que importa.")


def main():
    p = argparse.ArgumentParser(description="Motor local da Lupa.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add-prazo", help="registrar um prazo/obrigação")
    s.add_argument("--doc", default="")
    s.add_argument("--desc", required=True)
    s.add_argument("--data", required=True)
    s.add_argument("--quem", default="")
    s.add_argument("--tipo", default="prazo", choices=["prazo", "obrigacao"])
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("prazos", help="listar prazos/obrigações em aberto")
    s.add_argument("--doc", default="")
    s.add_argument("--dias", type=int, default=None)
    s.set_defaults(func=cmd_prazos)

    s = sub.add_parser("concluir", help="marcar item como concluído")
    s.add_argument("--id", required=True)
    s.set_defaults(func=cmd_concluir)

    s = sub.add_parser("remover", help="remover item")
    s.add_argument("--id", required=True)
    s.set_defaults(func=cmd_remover)

    s = sub.add_parser("comparar", help="diferença entre dois arquivos de texto")
    s.add_argument("--a", required=True)
    s.add_argument("--b", required=True)
    s.set_defaults(func=cmd_comparar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
