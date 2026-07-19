#!/usr/bin/env python3
"""Pauta - motor de agenda para negocios de servico.

So usa a biblioteca padrao do Python. Cuida da parte deterministica:
guarda a agenda num CSV, detecta conflito de horario, sugere horarios
livres, e responde quem precisa de confirmacao, quem deve voltar e quem
sumiu (para reativacao). As MENSAGENS sao escritas pelo proprio Claude,
no tom do dono, usando os modelos em references/modelos_mensagens.md.
"""

import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------- caminhos
def raiz_projeto():
    """Acha a raiz do projeto do usuario, mesmo que o script seja rodado de
    dentro de .claude/skills/pauta. Assim a agenda fica sempre no mesmo lugar."""
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


RAIZ = raiz_projeto()
DIR_CFG = os.path.join(RAIZ, ".pauta")
CONFIG_JSON = os.path.join(DIR_CFG, "config.json")
AGENDA = os.path.join(DIR_CFG, "agenda.csv")

COLUNAS = ["id", "cliente", "telefone", "servico", "profissional",
           "data", "hora", "duracao_min", "status", "valor", "obs"]

DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
ATIVOS = {"agendado", "confirmado"}          # ocupam horario
HISTORICO = {"atendido", "faltou"}           # ja aconteceram


# ---------------------------------------------------------------- utilidades
def erro(msg):
    print("ERRO: " + msg, file=sys.stderr)
    sys.exit(1)


def carregar_config():
    if not os.path.exists(CONFIG_JSON):
        erro("Pauta ainda nao foi configurada. Rode a Primeira vez (veja o SKILL.md).")
    with open(CONFIG_JSON, encoding="utf-8") as f:
        return json.load(f)


def ler_agenda():
    if not os.path.exists(AGENDA):
        return []
    with open(AGENDA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def gravar_agenda(linhas):
    os.makedirs(DIR_CFG, exist_ok=True)
    with open(AGENDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        for ln in linhas:
            w.writerow({c: ln.get(c, "") for c in COLUNAS})


def proximo_id(linhas):
    ids = [int(l["id"]) for l in linhas if str(l.get("id", "")).isdigit()]
    return str(max(ids) + 1) if ids else "1"


def parse_data(txt):
    """Aceita ISO (2026-06-10), hoje, amanha, ontem, +Nd e nomes de dia."""
    if not txt:
        return None
    t = txt.strip().lower()
    hoje = date.today()
    if t in ("hoje",):
        return hoje
    if t in ("amanha", "amanhã"):
        return hoje + timedelta(days=1)
    if t in ("ontem",):
        return hoje - timedelta(days=1)
    if t.startswith("+") and t.endswith("d") and t[1:-1].isdigit():
        return hoje + timedelta(days=int(t[1:-1]))
    nomes = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "dom": 6}
    if t[:3] in nomes:
        alvo = nomes[t[:3]]
        d = hoje + timedelta(days=1)
        while d.weekday() != alvo:
            d += timedelta(days=1)
        return d
    try:
        return datetime.strptime(t, "%Y-%m-%d").date()
    except ValueError:
        erro("Data invalida: '%s'. Use AAAA-MM-DD, hoje, amanha ou +Nd." % txt)


def hm(txt):
    h, m = txt.split(":")
    return int(h) * 60 + int(m)


def para_hm(minutos):
    return "%02d:%02d" % (minutos // 60, minutos % 60)


def servico_cfg(cfg, nome):
    for s in cfg.get("servicos", []):
        if s["nome"].lower() == (nome or "").lower():
            return s
    return None


def janelas_do_dia(cfg, d):
    return cfg.get("horario", {}).get(DIAS[d.weekday()], []) or []


# ---------------------------------------------------------------- comandos
def cmd_init(args):
    if os.path.exists(AGENDA):
        print("agenda.csv ja existe em .pauta/")
        return
    gravar_agenda([])
    print("Criada .pauta/agenda.csv vazia.")


def _ocupados(linhas, d_iso, prof=None):
    """Intervalos (ini,fim) em minutos ocupados por status ativo no dia."""
    out = []
    for l in linhas:
        if l["data"] != d_iso or l["status"] not in ATIVOS:
            continue
        if prof and l.get("profissional", "") and l["profissional"].lower() != prof.lower():
            continue
        ini = hm(l["hora"])
        dur = int(l.get("duracao_min") or 0) or 30
        out.append((ini, ini + dur, l.get("profissional", "")))
    return out


def cmd_slots(args):
    cfg = carregar_config()
    linhas = ler_agenda()
    d = parse_data(args.data)
    janelas = janelas_do_dia(cfg, d)
    if not janelas:
        print("Fechado em %s (%s). Nenhum horario." % (d.isoformat(), DIAS[d.weekday()]))
        return
    sv = servico_cfg(cfg, args.servico) if args.servico else None
    dur = sv["duracao_min"] if sv else cfg.get("granularidade_min", 30)
    passo = cfg.get("granularidade_min", 30)
    intervalo = cfg.get("intervalo", "")
    iv = (hm(intervalo.split("-")[0]), hm(intervalo.split("-")[1])) if "-" in intervalo else None

    profs = [args.prof] if args.prof else (cfg.get("profissionais") or [""])
    print("Horarios livres em %s (%s)%s%s:" % (
        d.isoformat(), DIAS[d.weekday()],
        " | servico: " + sv["nome"] if sv else "",
        " | duracao: %dmin" % dur))
    achou = False
    for prof in profs:
        ocup = _ocupados(linhas, d.isoformat(), prof if prof else None)
        livres = []
        for jan in janelas:
            ini_j, fim_j = hm(jan.split("-")[0]), hm(jan.split("-")[1])
            t = ini_j
            while t + dur <= fim_j:
                fim = t + dur
                conflito = any(not (fim <= a or t >= b) for a, b, _ in ocup)
                no_intervalo = iv and not (fim <= iv[0] or t >= iv[1])
                if not conflito and not no_intervalo:
                    livres.append(para_hm(t))
                t += passo
        rotulo = ("  " + prof) if prof else "  (geral)"
        if livres:
            achou = True
            print("%s: %s" % (rotulo, ", ".join(livres)))
        else:
            print("%s: sem horario livre" % rotulo)
    if not achou:
        print("Nenhum horario livre. Sugira outro dia ou ofereca a lista de espera (encaixe).")


def cmd_add(args):
    cfg = carregar_config()
    linhas = ler_agenda()
    status = "espera" if args.espera else "agendado"
    sv = servico_cfg(cfg, args.servico)
    dur = args.duracao or (sv["duracao_min"] if sv else cfg.get("granularidade_min", 30))
    valor = args.valor or (sv.get("preco", "") if sv else "")
    if status != "espera":
        if not args.data or not args.hora:
            erro("Agendamento precisa de --data e --hora (ou use --espera).")
        d = parse_data(args.data)
        ini = hm(args.hora)
        for a, b, p in _ocupados(linhas, d.isoformat(), args.prof):
            if not (ini + dur <= a or ini >= b):
                print("AVISO: conflito com horario ocupado (%s-%s%s). Confirme antes de salvar." % (
                    para_hm(a), para_hm(b), " / " + p if p else ""))
        data_iso = d.isoformat()
    else:
        data_iso = parse_data(args.data).isoformat() if args.data else ""
    nid = proximo_id(linhas)
    linhas.append({
        "id": nid, "cliente": args.cliente, "telefone": args.tel or "",
        "servico": args.servico or "", "profissional": args.prof or "",
        "data": data_iso, "hora": args.hora or "", "duracao_min": str(dur),
        "status": status, "valor": str(valor), "obs": args.obs or "",
    })
    gravar_agenda(linhas)
    print("Salvo #%s: %s | %s | %s %s | %s" % (
        nid, args.cliente, args.servico or "-", data_iso or "(sem data)",
        args.hora or "", status))


def _achar(linhas, _id):
    for l in linhas:
        if l["id"] == str(_id):
            return l
    erro("Nao achei o agendamento #%s." % _id)


def cmd_cancel(args):
    linhas = ler_agenda()
    l = _achar(linhas, args.id)
    l["status"] = "cancelado"
    gravar_agenda(linhas)
    print("Cancelado #%s (%s). O horario voltou a ficar livre." % (args.id, l["cliente"]))


def cmd_remarcar(args):
    cfg = carregar_config()
    linhas = ler_agenda()
    l = _achar(linhas, args.id)
    d = parse_data(args.data)
    ini = hm(args.hora)
    dur = int(l.get("duracao_min") or 0) or cfg.get("granularidade_min", 30)
    for a, b, p in _ocupados(linhas, d.isoformat(), l.get("profissional")):
        if l["data"] == d.isoformat() and l["hora"] == args.hora:
            continue
        if not (ini + dur <= a or ini >= b):
            print("AVISO: conflito no novo horario (%s-%s). Confirme antes." % (para_hm(a), para_hm(b)))
    l["data"], l["hora"], l["status"] = d.isoformat(), args.hora, "agendado"
    gravar_agenda(linhas)
    print("Remarcado #%s (%s) para %s %s." % (args.id, l["cliente"], d.isoformat(), args.hora))


def cmd_status(args):
    validos = {"agendado", "confirmado", "atendido", "faltou", "cancelado", "espera"}
    if args.para not in validos:
        erro("Status invalido. Use: " + ", ".join(sorted(validos)))
    linhas = ler_agenda()
    l = _achar(linhas, args.id)
    l["status"] = args.para
    gravar_agenda(linhas)
    print("#%s (%s) agora esta: %s" % (args.id, l["cliente"], args.para))


def cmd_dia(args):
    linhas = ler_agenda()
    d = parse_data(args.data).isoformat()
    filtro = args.status.split(",") if args.status else None
    do_dia = [l for l in linhas if l["data"] == d and (not filtro or l["status"] in filtro)
              and l["status"] != "cancelado"]
    do_dia.sort(key=lambda l: l["hora"])
    if not do_dia:
        print("Nenhum agendamento em %s." % d)
        return
    print("Agendamentos em %s (%d):" % (d, len(do_dia)))
    for l in do_dia:
        print("  #%s %s | %s | %s | %s | tel %s | %s" % (
            l["id"], l["hora"], l["cliente"], l["servico"] or "-",
            l["profissional"] or "-", l["telefone"] or "-", l["status"]))


def cmd_retorno(args):
    cfg = carregar_config()
    linhas = ler_agenda()
    ref = parse_data(args.ate) if args.ate else date.today()
    futuros = {}   # (cliente,servico) -> tem agendamento futuro?
    ult = {}       # (cliente,servico) -> (data, linha) mais recente atendido
    for l in linhas:
        if not l["data"]:
            continue
        try:
            dl = datetime.strptime(l["data"], "%Y-%m-%d").date()
        except ValueError:
            continue
        chave = (l["cliente"].lower(), l["servico"].lower())
        if l["status"] in ATIVOS and dl >= date.today():
            futuros[chave] = True
        if l["status"] == "atendido":
            if chave not in ult or dl > ult[chave][0]:
                ult[chave] = (dl, l)
    pendentes = []
    for chave, (dl, l) in ult.items():
        sv = servico_cfg(cfg, l["servico"])
        if not sv or not sv.get("retorno_dias"):
            continue
        vencimento = dl + timedelta(days=int(sv["retorno_dias"]))
        if vencimento <= ref and not futuros.get(chave):
            pendentes.append((vencimento, l, dl))
    pendentes.sort(key=lambda x: x[0])
    if not pendentes:
        print("Ninguem vencido para retorno ate %s." % ref.isoformat())
        return
    print("Clientes para chamar de volta (retorno vencido ate %s):" % ref.isoformat())
    for venc, l, dl in pendentes:
        print("  %s | %s | ultima vez %s | venceu %s | tel %s" % (
            l["cliente"], l["servico"], dl.isoformat(), venc.isoformat(), l["telefone"] or "-"))


def cmd_reativar(args):
    linhas = ler_agenda()
    limite = date.today() - timedelta(days=args.dias)
    futuros, ult = set(), {}
    for l in linhas:
        if not l["data"]:
            continue
        try:
            dl = datetime.strptime(l["data"], "%Y-%m-%d").date()
        except ValueError:
            continue
        c = l["cliente"].lower()
        if l["status"] in ATIVOS and dl >= date.today():
            futuros.add(c)
        if l["status"] in HISTORICO:
            if c not in ult or dl > ult[c][0]:
                ult[c] = (dl, l)
    sumidos = [(dl, l) for c, (dl, l) in ult.items() if dl < limite and c not in futuros]
    sumidos.sort(key=lambda x: x[0])
    if not sumidos:
        print("Nenhum cliente parado ha mais de %d dias." % args.dias)
        return
    print("Clientes sumidos ha mais de %d dias (candidatos a reativacao):" % args.dias)
    for dl, l in sumidos:
        dias = (date.today() - dl).days
        print("  %s | ultima vez %s (%d dias) | %s | tel %s" % (
            l["cliente"], dl.isoformat(), dias, l["servico"] or "-", l["telefone"] or "-"))


def cmd_espera(args):
    linhas = ler_agenda()
    fila = [l for l in linhas if l["status"] == "espera"]
    if not fila:
        print("Lista de espera vazia.")
        return
    print("Lista de espera (%d):" % len(fila))
    for l in fila:
        print("  #%s %s | %s | quer: %s | tel %s | %s" % (
            l["id"], l["cliente"], l["servico"] or "-",
            l["data"] or "qualquer dia", l["telefone"] or "-", l["obs"] or ""))


def cmd_resumo(args):
    linhas = ler_agenda()
    cont = {}
    for l in linhas:
        cont[l["status"]] = cont.get(l["status"], 0) + 1
    atend = cont.get("atendido", 0)
    falt = cont.get("faltou", 0)
    base = atend + falt
    print("Resumo da agenda:")
    for s in ["agendado", "confirmado", "atendido", "faltou", "cancelado", "espera"]:
        print("  %-11s %d" % (s, cont.get(s, 0)))
    if base:
        print("  taxa de no-show: %.0f%% (%d de %d concluidos)" % (100 * falt / base, falt, base))


# ---------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description="Pauta - motor de agenda (so stdlib).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="cria a agenda vazia").set_defaults(func=cmd_init)

    s = sub.add_parser("slots", help="horarios livres num dia")
    s.add_argument("data"); s.add_argument("--prof"); s.add_argument("--servico")
    s.set_defaults(func=cmd_slots)

    s = sub.add_parser("add", help="adiciona agendamento ou espera")
    s.add_argument("--cliente", required=True); s.add_argument("--tel")
    s.add_argument("--servico"); s.add_argument("--prof")
    s.add_argument("--data"); s.add_argument("--hora")
    s.add_argument("--duracao", type=int); s.add_argument("--valor")
    s.add_argument("--obs"); s.add_argument("--espera", action="store_true")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("cancel", help="cancela um agendamento")
    s.add_argument("--id", required=True); s.set_defaults(func=cmd_cancel)

    s = sub.add_parser("remarcar", help="muda data/hora de um agendamento")
    s.add_argument("--id", required=True); s.add_argument("--data", required=True)
    s.add_argument("--hora", required=True); s.set_defaults(func=cmd_remarcar)

    s = sub.add_parser("status", help="muda o status (atendido/faltou/confirmado/...)")
    s.add_argument("--id", required=True); s.add_argument("--para", required=True)
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("dia", help="lista os agendamentos de um dia")
    s.add_argument("data"); s.add_argument("--status")
    s.set_defaults(func=cmd_dia)

    s = sub.add_parser("retorno", help="clientes vencidos para voltar")
    s.add_argument("--ate"); s.set_defaults(func=cmd_retorno)

    s = sub.add_parser("reativar", help="clientes sumidos (reativacao)")
    s.add_argument("--dias", type=int, default=60); s.set_defaults(func=cmd_reativar)

    sub.add_parser("espera", help="mostra a lista de espera").set_defaults(func=cmd_espera)
    sub.add_parser("resumo", help="contagem por status + no-show").set_defaults(func=cmd_resumo)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
