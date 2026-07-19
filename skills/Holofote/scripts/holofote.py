#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Holofote - motor do estudio de conteudo.

A parte DETERMINISTICA do Holofote (o Claude escreve a parte humana - os temas,
os ganchos, as legendas, no tom do dono). Este motor so usa a biblioteca padrao
do Python (nada para instalar) e cuida do que precisa ser exato:

  - gerar o calendario editorial (datas reais respeitando a frequencia, com os
    pilares e os formatos rodando para nao ficar tudo igual);
  - registrar o que foi planejado e o que ja foi publicado;
  - avisar quando um tema parece repetir algo recente (anti-repeticao);
  - guardar o banco de ideias/ganchos;
  - mostrar um resumo (posts por pilar, taxa de execucao, proximos da fila).

Tudo vive em `.holofote/` na raiz do projeto:
  config.json / config.md  -> identidade, nicho, publico, tom, pilares, plataformas
  calendario.csv           -> id,data,pilar,tema,formato,plataforma,gancho,status,publicado_em
  banco.csv                -> id,tipo,texto,pilar,criado_em,usado_em

Comandos:
  init
  calendario --dias N [--inicio DATA] [--freq N]      (N = posts por semana; gera e PLANEJA)
  calendario --dias N ... --so-ver                    (so mostra a grade, nao grava)
  add --data DATA --pilar P --tema "..." --formato F --plataforma X [--gancho "..."] [--status planejado|feito]
  editar --id N [--tema "..."] [--gancho "..."] [--pilar P] [--formato F] [--plataforma X] [--data DATA]
  feito --id N [--data DATA]
  proximos [--n 5]
  checar --tema "..." [--pilar P] [--ignorar-id N]    (anti-repeticao: temas parecidos no calendario)
  banco-add --tipo ideia|gancho|tema --texto "..." [--pilar P]
  banco [--tipo T]
  usar-banco --id N [--em "Reels 12/06"]
  resumo
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
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
F_CONFIG = os.path.join(DIR, "config.json")
F_CAL = os.path.join(DIR, "calendario.csv")
F_BANCO = os.path.join(DIR, "banco.csv")

COLS_CAL = ["id", "data", "pilar", "tema", "formato", "plataforma", "gancho", "status", "publicado_em"]
COLS_BANCO = ["id", "tipo", "texto", "pilar", "criado_em", "usado_em"]

# formatos nativos que o motor sabe rodar no calendario (o Claude produz o conteudo)
FORMATOS_PADRAO = ["Reels", "Carrossel", "Post unico", "Stories", "Reels", "Carrossel"]

DIAS_PT = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]

STOP = set("""a o e de da do das dos um uma para por com sem que como nao sim em no na nos nas
ao aos seu sua seus suas meu minha se os as ja te tu eu ele ela isso este esta esse essa
mais menos muito pouco voce vc pra pro the to of and""".split())


# ---------- utilidades ----------

def hoje():
    return dt.date.today()


def parse_data(s):
    """Aceita YYYY-MM-DD ou DD/MM/YYYY (ou DD/MM, assume ano atual)."""
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    m = re.match(r"^(\d{1,2})/(\d{1,2})$", s)
    if m:
        return dt.date(hoje().year, int(m.group(2)), int(m.group(1)))
    raise SystemExit("ERRO: data invalida: %r (use AAAA-MM-DD ou DD/MM/AAAA)" % s)


def fmt_data(d):
    return d.strftime("%d/%m/%Y (%a)").replace("Mon", "seg").replace("Tue", "ter") \
        .replace("Wed", "qua").replace("Thu", "qui").replace("Fri", "sex") \
        .replace("Sat", "sab").replace("Sun", "dom")


def palavras(texto):
    t = re.sub(r"[^\wáàâãéêíóôõúüç]+", " ", (texto or "").lower(), flags=re.UNICODE)
    return [p for p in t.split() if len(p) > 2 and p not in STOP]


def carregar_config():
    if not os.path.exists(F_CONFIG):
        raise SystemExit("Holofote ainda nao foi configurado. Faca a Primeira vez "
                         "(scripts/primeira_vez.py) antes de usar o motor.")
    with open(F_CONFIG, encoding="utf-8") as f:
        return json.load(f)


def ler_csv(caminho, cols):
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def escrever_csv(caminho, cols, linhas):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for l in linhas:
            w.writerow({c: l.get(c, "") for c in cols})


def proximo_id(linhas):
    n = 0
    for l in linhas:
        try:
            n = max(n, int(l.get("id", 0)))
        except (TypeError, ValueError):
            pass
    return str(n + 1)


# ---------- comandos ----------

def cmd_init(args):
    os.makedirs(DIR, exist_ok=True)
    if not os.path.exists(F_CAL):
        escrever_csv(F_CAL, COLS_CAL, [])
    if not os.path.exists(F_BANCO):
        escrever_csv(F_BANCO, COLS_BANCO, [])
    print("Holofote pronto em %s" % DIR)


def datas_de_publicacao(inicio, dias, por_semana):
    """Distribui `por_semana` posts ao longo da janela de `dias` dias, de forma
    regular. Os dias da semana de publicacao sao ancorados no dia de `inicio`,
    entao o 1o post cai SEMPRE na data de inicio (ex.: inicio numa terca, 3/semana
    -> ter, qui, sab)."""
    por_semana = max(1, min(7, por_semana))
    # ancora os dias-alvo no weekday do inicio e espalha uniformemente pela semana
    base = inicio.weekday()
    passo = 7.0 / por_semana
    dias_semana_alvo = sorted({(base + int(round(i * passo))) % 7 for i in range(por_semana)})
    datas = []
    d = inicio
    fim = inicio + dt.timedelta(days=dias - 1)
    while d <= fim:
        if d.weekday() in dias_semana_alvo:
            datas.append(d)
        d += dt.timedelta(days=1)
    return datas


def cmd_calendario(args):
    cfg = carregar_config()
    pilares = cfg.get("pilares") or ["Educar", "Bastidores", "Prova social", "Oferta"]
    plataformas = cfg.get("plataformas") or ["Instagram"]
    inicio = parse_data(args.inicio) if args.inicio else hoje()
    freq = args.freq or cfg.get("frequencia_semanal") or 3
    datas = datas_de_publicacao(inicio, args.dias, int(freq))

    cal = ler_csv(F_CAL, COLS_CAL)
    grade = []
    for i, d in enumerate(datas):
        grade.append({
            "data": d.strftime("%Y-%m-%d"),
            "pilar": pilares[i % len(pilares)],
            "formato": FORMATOS_PADRAO[i % len(FORMATOS_PADRAO)],
            "plataforma": plataformas[i % len(plataformas)],
        })

    print("Grade editorial - %d posts em %d dias (%s/semana), comecando %s"
          % (len(grade), args.dias, freq, fmt_data(inicio)))
    print("Pilares em rotacao: " + " | ".join(pilares))
    print("-" * 64)
    for g in grade:
        d = dt.datetime.strptime(g["data"], "%Y-%m-%d").date()
        print("%s  | %-14s | %-10s | %s" % (fmt_data(d), g["pilar"], g["formato"], g["plataforma"]))
    print("-" * 64)

    if args.so_ver:
        print("(so visualizacao - nada gravado. O Claude preenche tema + gancho de cada dia")
        print(" e grava com: holofote.py add ...)")
        return

    # grava como planejado (tema/gancho ficam vazios para o Claude preencher depois)
    ja = {(l["data"], l["pilar"], l["formato"]) for l in cal}
    novos = 0
    for g in grade:
        chave = (g["data"], g["pilar"], g["formato"])
        if chave in ja:
            continue
        cal.append({
            "id": proximo_id(cal), "data": g["data"], "pilar": g["pilar"],
            "tema": "", "formato": g["formato"], "plataforma": g["plataforma"],
            "gancho": "", "status": "planejado", "publicado_em": "",
        })
        novos += 1
    escrever_csv(F_CAL, COLS_CAL, cal)
    print("Gravados %d slots planejados no calendario. Agora o Claude define o tema e o" % novos)
    print("gancho de cada um (modo Calendario/Criar) e atualiza com 'add' ou editando a peca.")


def cmd_add(args):
    cal = ler_csv(F_CAL, COLS_CAL)
    data = parse_data(args.data).strftime("%Y-%m-%d") if args.data else ""
    pub = ""
    if args.status == "feito":
        pub = data or hoje().strftime("%Y-%m-%d")
    nova = {
        "id": proximo_id(cal),
        "data": data,
        "pilar": args.pilar or "",
        "tema": args.tema or "",
        "formato": args.formato or "",
        "plataforma": args.plataforma or "",
        "gancho": args.gancho or "",
        "status": args.status or "planejado",
        "publicado_em": pub,
    }
    cal.append(nova)
    escrever_csv(F_CAL, COLS_CAL, cal)
    print("Adicionado #%s: %s | %s | %s (%s)" % (nova["id"], nova.get("data", "?"),
          nova["pilar"], nova["tema"], nova["status"]))


def cmd_editar(args):
    """Preenche/atualiza campos de um slot JA EXISTENTE do calendario (sem duplicar)."""
    cal = ler_csv(F_CAL, COLS_CAL)
    for l in cal:
        if l["id"] == str(args.id):
            if args.tema is not None:
                l["tema"] = args.tema
            if args.gancho is not None:
                l["gancho"] = args.gancho
            if args.pilar is not None:
                l["pilar"] = args.pilar
            if args.formato is not None:
                l["formato"] = args.formato
            if args.plataforma is not None:
                l["plataforma"] = args.plataforma
            if args.data:
                l["data"] = parse_data(args.data).strftime("%Y-%m-%d")
            escrever_csv(F_CAL, COLS_CAL, cal)
            print("Atualizado #%s: %s | %s | %s" % (l["id"], l.get("data", "?"), l["pilar"], l["tema"]))
            return
    print("Nao achei o slot #%s no calendario." % args.id)


def cmd_feito(args):
    cal = ler_csv(F_CAL, COLS_CAL)
    achou = False
    for l in cal:
        if l["id"] == str(args.id):
            l["status"] = "feito"
            l["publicado_em"] = parse_data(args.data).strftime("%Y-%m-%d") if args.data else hoje().strftime("%Y-%m-%d")
            achou = True
            print("Marcado como publicado #%s: %s (%s)" % (l["id"], l["tema"] or l["pilar"], l["publicado_em"]))
    if not achou:
        print("Nao achei o item #%s no calendario." % args.id)
        return
    escrever_csv(F_CAL, COLS_CAL, cal)


def cmd_proximos(args):
    cal = ler_csv(F_CAL, COLS_CAL)
    pend = [l for l in cal if l.get("status") != "feito" and l.get("data")]
    pend.sort(key=lambda l: l["data"])
    pend = pend[: args.n]
    if not pend:
        print("Nenhum post planejado na fila. Gere um calendario (modo Calendario).")
        return
    print("Proximos %d posts planejados:" % len(pend))
    for l in pend:
        d = dt.datetime.strptime(l["data"], "%Y-%m-%d").date()
        tema = l["tema"] or "(tema a definir)"
        print("  #%s %s | %-12s | %-9s | %s" % (l["id"], fmt_data(d), l["pilar"], l["formato"], tema))


def cmd_checar(args):
    """Anti-repeticao: acha posts JA NO CALENDARIO (planejados ou publicados) com
    tema parecido (sobreposicao de palavras). Use --ignorar-id N para nao comparar
    contra o proprio slot que voce esta preenchendo."""
    cal = ler_csv(F_CAL, COLS_CAL)
    alvo = set(palavras(args.tema))
    if args.pilar:
        alvo |= set(palavras(args.pilar))
    if not alvo:
        print("Informe um tema para checar.")
        return
    ignorar = str(args.ignorar_id) if args.ignorar_id else None
    achados = []
    for l in cal:
        if ignorar and l.get("id") == ignorar:
            continue
        base = set(palavras(l.get("tema", "")))
        if not base:
            continue
        inter = alvo & base
        if not inter:
            continue
        score = len(inter) / max(1, len(alvo))
        if score >= 0.34:
            achados.append((score, l))
    achados.sort(key=lambda x: -x[0])
    if not achados:
        print("OK - nenhum post parecido com %r encontrado. Tema livre." % args.tema)
        return
    print("ATENCAO - temas parecidos ja no calendario (evite repetir igual):")
    for score, l in achados[:5]:
        marca = "publicado %s" % l["publicado_em"] if l.get("status") == "feito" else "planejado %s" % l.get("data", "")
        print("  ~%d%% | #%s %s | %s [%s]" % (round(score * 100), l["id"], l["pilar"], l["tema"], marca))
    print("Sugestao: mude o angulo, o formato ou o pilar para nao soar repetido.")


def cmd_banco_add(args):
    banco = ler_csv(F_BANCO, COLS_BANCO)
    nova = {
        "id": proximo_id(banco),
        "tipo": args.tipo or "ideia",
        "texto": args.texto or "",
        "pilar": args.pilar or "",
        "criado_em": hoje().strftime("%Y-%m-%d"),
        "usado_em": "",
    }
    banco.append(nova)
    escrever_csv(F_BANCO, COLS_BANCO, banco)
    print("Guardado no banco #%s [%s]: %s" % (nova["id"], nova["tipo"], nova["texto"][:70]))


def cmd_banco(args):
    banco = ler_csv(F_BANCO, COLS_BANCO)
    if args.tipo:
        banco = [b for b in banco if b["tipo"] == args.tipo]
    livres = [b for b in banco if not b.get("usado_em")]
    if not banco:
        print("Banco vazio. Guarde ideias/ganchos com 'banco-add'.")
        return
    print("Banco de ideias (%d itens, %d ainda nao usados):" % (len(banco), len(livres)))
    for b in banco:
        marca = (" [usado em %s]" % b["usado_em"]) if b.get("usado_em") else ""
        pil = (" {%s}" % b["pilar"]) if b.get("pilar") else ""
        print("  #%s [%s]%s %s%s" % (b["id"], b["tipo"], pil, b["texto"][:80], marca))


def cmd_usar_banco(args):
    banco = ler_csv(F_BANCO, COLS_BANCO)
    for b in banco:
        if b["id"] == str(args.id):
            b["usado_em"] = args.em or hoje().strftime("%Y-%m-%d")
            escrever_csv(F_BANCO, COLS_BANCO, banco)
            print("Marcado como usado #%s: %s" % (b["id"], b["texto"][:60]))
            return
    print("Nao achei a ideia #%s no banco." % args.id)


def cmd_resumo(args):
    cfg = carregar_config()
    cal = ler_csv(F_CAL, COLS_CAL)
    banco = ler_csv(F_BANCO, COLS_BANCO)
    feitos = [l for l in cal if l.get("status") == "feito"]
    planej = [l for l in cal if l.get("status") != "feito"]

    print("=== Resumo Holofote - %s ===" % cfg.get("negocio", "seu negocio"))
    print("Nicho: %s | Tom: %s" % (cfg.get("nicho", "-"), cfg.get("tom", "-")))
    print("Plataformas: %s" % ", ".join(cfg.get("plataformas", []) or ["-"]))
    total = len(cal)
    if total:
        taxa = round(100 * len(feitos) / total)
        print("Execucao: %d publicados / %d no calendario (%d%%)" % (len(feitos), total, taxa))
    else:
        print("Calendario ainda vazio - gere um (modo Calendario).")

    # posts por pilar
    porpilar = {}
    for l in cal:
        porpilar[l.get("pilar", "?")] = porpilar.get(l.get("pilar", "?"), 0) + 1
    if porpilar:
        print("\nPor pilar:")
        for p in (cfg.get("pilares") or sorted(porpilar)):
            print("  - %-16s %d" % (p, porpilar.get(p, 0)))
        # pilares configurados sem nenhum post
        zerados = [p for p in (cfg.get("pilares") or []) if porpilar.get(p, 0) == 0]
        if zerados:
            print("  (sem conteudo ainda: %s)" % ", ".join(zerados))

    # proximos
    pend = sorted([l for l in planej if l.get("data")], key=lambda l: l["data"])[:3]
    if pend:
        print("\nProximos da fila:")
        for l in pend:
            d = dt.datetime.strptime(l["data"], "%Y-%m-%d").date()
            print("  #%s %s | %s | %s" % (l["id"], fmt_data(d), l["pilar"], l["tema"] or "(a definir)"))

    livres = [b for b in banco if not b.get("usado_em")]
    print("\nBanco de ideias: %d itens (%d ainda nao usados)." % (len(banco), len(livres)))


def main():
    p = argparse.ArgumentParser(prog="holofote.py", add_help=True)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init")

    c = sub.add_parser("calendario")
    c.add_argument("--dias", type=int, default=30)
    c.add_argument("--inicio", default="")
    c.add_argument("--freq", type=int, default=0, help="posts por semana")
    c.add_argument("--so-ver", action="store_true")

    a = sub.add_parser("add")
    a.add_argument("--data", default="")
    a.add_argument("--pilar", default="")
    a.add_argument("--tema", default="")
    a.add_argument("--formato", default="")
    a.add_argument("--plataforma", default="")
    a.add_argument("--gancho", default="")
    a.add_argument("--status", default="planejado")

    e = sub.add_parser("editar")
    e.add_argument("--id", required=True)
    e.add_argument("--tema", default=None)
    e.add_argument("--gancho", default=None)
    e.add_argument("--pilar", default=None)
    e.add_argument("--formato", default=None)
    e.add_argument("--plataforma", default=None)
    e.add_argument("--data", default="")

    f = sub.add_parser("feito")
    f.add_argument("--id", required=True)
    f.add_argument("--data", default="")

    pr = sub.add_parser("proximos")
    pr.add_argument("--n", type=int, default=5)

    ch = sub.add_parser("checar")
    ch.add_argument("--tema", required=True)
    ch.add_argument("--pilar", default="")
    ch.add_argument("--ignorar-id", dest="ignorar_id", default="")

    ba = sub.add_parser("banco-add")
    ba.add_argument("--tipo", default="ideia")
    ba.add_argument("--texto", required=True)
    ba.add_argument("--pilar", default="")

    b = sub.add_parser("banco")
    b.add_argument("--tipo", default="")

    u = sub.add_parser("usar-banco")
    u.add_argument("--id", required=True)
    u.add_argument("--em", default="")

    sub.add_parser("resumo")

    args = p.parse_args()
    cmds = {
        "init": cmd_init, "calendario": cmd_calendario, "add": cmd_add, "editar": cmd_editar,
        "feito": cmd_feito, "proximos": cmd_proximos, "checar": cmd_checar,
        "banco-add": cmd_banco_add, "banco": cmd_banco, "usar-banco": cmd_usar_banco,
        "resumo": cmd_resumo,
    }
    if not args.cmd:
        p.print_help()
        return
    cmds[args.cmd](args)


if __name__ == "__main__":
    main()
