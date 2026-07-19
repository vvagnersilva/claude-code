#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regua - motor de controle de recebiveis + regua de cobranca.

Somente biblioteca padrao do Python (stdlib). Sem pandas, sem rede, sem chave de API.
Le e escreve um unico livro local: .regua/recebimentos.csv

O motor faz APENAS a parte exata: cadastrar uma conta a receber, registrar
pagamentos (inclusive parcial), calcular dias de atraso, agrupar por faixa de
atraso (aging), dizer quem cobrar hoje pela regua, somar o que ha a receber,
a taxa de inadimplencia e o prazo medio de recebimento (DSO).

A redacao das mensagens de cobranca quem faz e a IA (com base no tom do dono).
O motor nao inventa numero nem manda mensagem - so organiza e calcula.

Uso (a IA chama por baixo; o dono so conversa):
  regua.py init
  regua.py add --cliente "Joao" --valor "R$ 1.500,00" --venc 10/06/2026 \
           [--servico "Mensalidade"] [--emitido 01/06/2026] [--obs "..."]
  regua.py pagar --id 3 --valor "R$ 500,00" [--data 12/06/2026]   # baixa parcial ou total
  regua.py quitar --id 3 [--data 12/06/2026]                      # quita o saldo restante
  regua.py cancelar --id 3 [--motivo "..."]
  regua.py editar --id 3 [--valor ..] [--venc ..] [--cliente ..] [--servico ..] [--obs ..]
  regua.py hoje [--data 24/06/2026]      # quem cobrar hoje pela regua (degraus)
  regua.py atrasados [--data ...]        # tudo vencido, ordenado do mais velho
  regua.py aging [--data ...]            # mapa por faixa de atraso
  regua.py cliente --nome "Joao" [--data ...]   # extrato de um cliente
  regua.py resumo [--data ...]           # painel geral (semaforo + indicadores)
  regua.py listar [--status aberto|pago|cancelado|todos]

Datas aceitas: DD/MM/AAAA, DD/MM/AA, DD/MM (assume ano corrente do --data), AAAA-MM-DD.
Dinheiro aceito: "R$ 1.234,56", "1.234,56", "1500", "1500.00", "R$ 1.890".
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

PASTA = ".regua"
LIVRO = os.path.join(PASTA, "recebimentos.csv")
CAMPOS = [
    "id", "cliente", "servico", "valor", "pago", "emitido", "vencimento",
    "status", "ultimo_contato", "degrau", "obs",
]
CENT = Decimal("0.01")

# Degraus da regua de cobranca (em dias relativos ao vencimento).
# Negativo = antes de vencer (lembrete amigavel). 0 = vence hoje. Positivo = atraso.
# Cada degrau tem um rotulo e um "tom" que a IA usa para calibrar a mensagem.
DEGRAUS = [
    (-3, "pre_vencimento", "lembrete gentil, ainda nao venceu"),
    (0,  "vence_hoje",     "aviso cordial de vencimento no dia"),
    (3,  "atraso_leve",    "lembrete leve, provavel esquecimento"),
    (7,  "atraso_1sem",    "cobranca firme e educada, oferece ajuda/2a via"),
    (15, "atraso_2sem",    "cobranca direta, propoe parcelamento/negociacao"),
    (30, "atraso_1mes",    "ultima tentativa amigavel antes de medidas formais"),
]


# --------------------------------------------------------------------------- #
# Parsers tolerantes (dinheiro e data no padrao brasileiro)
# --------------------------------------------------------------------------- #
def parse_dinheiro(txt) -> Decimal:
    """Converte texto BR de dinheiro para Decimal exato em centavos."""
    if txt is None:
        raise ValueError("valor vazio")
    if isinstance(txt, (int, float, Decimal)):
        return Decimal(str(txt)).quantize(CENT, ROUND_HALF_UP)
    s = str(txt).strip()
    if not s:
        raise ValueError("valor vazio")
    s = s.replace("R$", "").replace("r$", "").replace(" ", "").replace(" ", "")
    neg = s.startswith("-")
    s = s.lstrip("-+")
    if "," in s:
        # virgula = separador decimal BR; ponto = milhar
        s = s.replace(".", "").replace(",", ".")
    else:
        # sem virgula: ponto pode ser milhar (1.890) ou decimal (1500.00)
        if s.count(".") == 1:
            ip, dp = s.split(".")
            if len(dp) == 3 and len(ip) <= 3:
                s = ip + dp          # 1.890 -> 1890 (milhar)
            # senao mantem como decimal (1500.00)
        else:
            s = s.replace(".", "")   # 1.234.567 -> milhares
    try:
        val = Decimal(s)
    except InvalidOperation:
        raise ValueError(f"valor invalido: {txt!r}")
    if neg:
        val = -val
    return val.quantize(CENT, ROUND_HALF_UP)


def fmt_dinheiro(v: Decimal) -> str:
    v = Decimal(v).quantize(CENT, ROUND_HALF_UP)
    neg = v < 0
    v = abs(v)
    inteiro, dec = divmod(int(v * 100), 100)
    s = f"{inteiro:,}".replace(",", ".")
    return ("-" if neg else "") + f"R$ {s},{dec:02d}"


def parse_data(txt, ref: date | None = None) -> date:
    """Converte data BR/ISO para date. DD/MM assume o ano de ref (ou hoje)."""
    if txt is None or str(txt).strip() == "":
        raise ValueError("data vazia")
    if isinstance(txt, date):
        return txt
    s = str(txt).strip()
    base = ref or date.today()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    # DD/MM sem ano
    try:
        d, m = s.split("/")[:2]
        return date(base.year, int(m), int(d))
    except Exception:
        raise ValueError(f"data invalida: {txt!r} (use DD/MM/AAAA)")


def fmt_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def hoje_de(args) -> date:
    return parse_data(args.data) if getattr(args, "data", None) else date.today()


# --------------------------------------------------------------------------- #
# Persistencia
# --------------------------------------------------------------------------- #
def garantir_pasta():
    os.makedirs(PASTA, exist_ok=True)


def carregar() -> list[dict]:
    if not os.path.exists(LIVRO):
        return []
    with open(LIVRO, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for r in linhas:
        for c in CAMPOS:
            r.setdefault(c, "")
    return linhas


def salvar(linhas: list[dict]):
    garantir_pasta()
    with open(LIVRO, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for r in linhas:
            w.writerow({c: r.get(c, "") for c in CAMPOS})


def proximo_id(linhas) -> int:
    ids = [int(r["id"]) for r in linhas if str(r.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


def achar(linhas, _id):
    for r in linhas:
        if str(r.get("id")) == str(_id):
            return r
    return None


# --------------------------------------------------------------------------- #
# Calculos
# --------------------------------------------------------------------------- #
def saldo(r) -> Decimal:
    val = parse_dinheiro(r.get("valor") or 0)
    pago = parse_dinheiro(r.get("pago") or 0)
    s = val - pago
    return s if s > 0 else Decimal("0.00")


def dias_atraso(r, ref: date) -> int:
    venc = parse_data(r["vencimento"], ref)
    return (ref - venc).days


def faixa(dias: int) -> str:
    if dias <= 0:
        return "a_vencer"
    if dias <= 30:
        return "1-30"
    if dias <= 60:
        return "31-60"
    if dias <= 90:
        return "61-90"
    return "90+"


FAIXA_ORDEM = ["a_vencer", "1-30", "31-60", "61-90", "90+"]
FAIXA_ROTULO = {
    "a_vencer": "A vencer (em dia)",
    "1-30": "Atraso 1-30 dias",
    "31-60": "Atraso 31-60 dias",
    "61-90": "Atraso 61-90 dias",
    "90+": "Atraso +90 dias (critico)",
}


def abertos(linhas):
    return [r for r in linhas if r.get("status") == "aberto" and saldo(r) > 0]


def degrau_devido(dias: int):
    """Retorna o degrau da regua que essa conta atingiu hoje (o mais avancado <= dias)."""
    atual = None
    for off, chave, tom in DEGRAUS:
        if dias >= off:
            atual = (off, chave, tom)
    return atual


# --------------------------------------------------------------------------- #
# Comandos
# --------------------------------------------------------------------------- #
def cmd_init(args):
    garantir_pasta()
    if not os.path.exists(LIVRO):
        salvar([])
    print(f"OK - livro pronto em {LIVRO}")


def cmd_add(args):
    linhas = carregar()
    ref = date.today()
    val = parse_dinheiro(args.valor)
    if val <= 0:
        print("ERRO: valor deve ser maior que zero.")
        sys.exit(1)
    venc = parse_data(args.venc, ref)
    emitido = parse_data(args.emitido, ref) if args.emitido else ref
    novo = {
        "id": str(proximo_id(linhas)),
        "cliente": args.cliente.strip(),
        "servico": (args.servico or "").strip(),
        "valor": str(val),
        "pago": "0.00",
        "emitido": fmt_data(emitido),
        "vencimento": fmt_data(venc),
        "status": "aberto",
        "ultimo_contato": "",
        "degrau": "",
        "obs": (args.obs or "").strip(),
    }
    linhas.append(novo)
    salvar(linhas)
    print(f"OK - conta #{novo['id']} | {novo['cliente']} | {fmt_dinheiro(val)} | vence {novo['vencimento']}")


def cmd_pagar(args):
    linhas = carregar()
    r = achar(linhas, args.id)
    if not r:
        print(f"ERRO: conta #{args.id} nao encontrada.")
        sys.exit(1)
    val = parse_dinheiro(args.valor)
    pago = parse_dinheiro(r.get("pago") or 0) + val
    total = parse_dinheiro(r.get("valor") or 0)
    if pago >= total:
        pago = total
        r["status"] = "pago"
    r["pago"] = str(pago.quantize(CENT, ROUND_HALF_UP))
    quando = parse_data(args.data) if args.data else date.today()
    r["obs"] = (r.get("obs", "") + f" | pgto {fmt_dinheiro(val)} em {fmt_data(quando)}").strip(" |")
    salvar(linhas)
    rest = saldo(r)
    if r["status"] == "pago":
        print(f"OK - conta #{r['id']} QUITADA ({r['cliente']}).")
    else:
        print(f"OK - baixa parcial em #{r['id']}. Pago {fmt_dinheiro(pago)} de {fmt_dinheiro(total)}. Saldo {fmt_dinheiro(rest)}.")


def cmd_quitar(args):
    linhas = carregar()
    r = achar(linhas, args.id)
    if not r:
        print(f"ERRO: conta #{args.id} nao encontrada.")
        sys.exit(1)
    total = parse_dinheiro(r.get("valor") or 0)
    r["pago"] = str(total)
    r["status"] = "pago"
    quando = parse_data(args.data) if args.data else date.today()
    r["obs"] = (r.get("obs", "") + f" | quitado em {fmt_data(quando)}").strip(" |")
    salvar(linhas)
    print(f"OK - conta #{r['id']} QUITADA ({r['cliente']}).")


def cmd_cancelar(args):
    linhas = carregar()
    r = achar(linhas, args.id)
    if not r:
        print(f"ERRO: conta #{args.id} nao encontrada.")
        sys.exit(1)
    r["status"] = "cancelado"
    if args.motivo:
        r["obs"] = (r.get("obs", "") + f" | cancelado: {args.motivo}").strip(" |")
    salvar(linhas)
    print(f"OK - conta #{r['id']} cancelada.")


def cmd_editar(args):
    linhas = carregar()
    r = achar(linhas, args.id)
    if not r:
        print(f"ERRO: conta #{args.id} nao encontrada.")
        sys.exit(1)
    if args.valor:
        r["valor"] = str(parse_dinheiro(args.valor))
    if args.venc:
        r["vencimento"] = fmt_data(parse_data(args.venc))
    if args.cliente:
        r["cliente"] = args.cliente.strip()
    if args.servico is not None:
        r["servico"] = args.servico.strip()
    if args.obs is not None:
        r["obs"] = args.obs.strip()
    salvar(linhas)
    print(f"OK - conta #{r['id']} atualizada.")


def _registrar_contato(linhas, r, ref, chave):
    r["ultimo_contato"] = fmt_data(ref)
    r["degrau"] = chave
    salvar(linhas)


def cmd_hoje(args):
    ref = hoje_de(args)
    linhas = carregar()
    ab = abertos(linhas)
    fila = []
    for r in ab:
        dias = dias_atraso(r, ref)
        deg = degrau_devido(dias)
        if not deg:
            continue
        off, chave, tom = deg
        # ja cobrado nesse mesmo degrau? pula (evita spam no mesmo estagio)
        if r.get("degrau") == chave and r.get("ultimo_contato") == fmt_data(ref):
            continue
        ja = r.get("degrau") == chave
        fila.append((dias, r, off, chave, tom, ja))
    # ordena: mais atrasado primeiro, depois maior valor
    fila.sort(key=lambda x: (-x[0], -float(saldo(x[1]))))
    if not fila:
        print(f"Nenhuma cobranca para hoje ({fmt_data(ref)}). Tudo em dia. ")
        return
    print(f"=== COBRAR HOJE ({fmt_data(ref)}) - {len(fila)} conta(s) ===\n")
    for dias, r, off, chave, tom, ja in fila:
        sinal = "venceu ha %d dia(s)" % dias if dias > 0 else (
            "vence hoje" if dias == 0 else "vence em %d dia(s)" % (-dias))
        marca = " [ja no mesmo degrau - reforco]" if ja else ""
        print(f"#{r['id']} {r['cliente']} - {fmt_dinheiro(saldo(r))}  ({sinal})")
        print(f"   degrau: {chave} -> tom: {tom}{marca}")
        if r.get("servico"):
            print(f"   ref: {r['servico']} | venc {r['vencimento']}")
    print("\n(Para marcar que cobrou: regua.py marcar --id N)")


def cmd_marcar(args):
    """Marca que o dono enviou a cobranca de uma conta hoje (avanca o degrau)."""
    ref = hoje_de(args)
    linhas = carregar()
    r = achar(linhas, args.id)
    if not r:
        print(f"ERRO: conta #{args.id} nao encontrada.")
        sys.exit(1)
    dias = dias_atraso(r, ref)
    deg = degrau_devido(dias)
    chave = deg[1] if deg else "contato"
    _registrar_contato(linhas, r, ref, chave)
    print(f"OK - cobranca de #{r['id']} registrada em {fmt_data(ref)} (degrau {chave}).")


def cmd_atrasados(args):
    ref = hoje_de(args)
    linhas = carregar()
    venc = [(dias_atraso(r, ref), r) for r in abertos(linhas)]
    venc = [(d, r) for d, r in venc if d > 0]
    venc.sort(key=lambda x: -x[0])
    if not venc:
        print(f"Nenhuma conta vencida em {fmt_data(ref)}. ")
        return
    tot = sum((saldo(r) for _, r in venc), Decimal("0.00"))
    print(f"=== ATRASADOS ({fmt_data(ref)}) - {len(venc)} conta(s) | {fmt_dinheiro(tot)} ===\n")
    for d, r in venc:
        print(f"#{r['id']} {r['cliente']:<22} {fmt_dinheiro(saldo(r)):>14}  ha {d} dia(s)  [{faixa(d)}]  venc {r['vencimento']}")


def cmd_aging(args):
    ref = hoje_de(args)
    linhas = carregar()
    grupos = {k: [] for k in FAIXA_ORDEM}
    for r in abertos(linhas):
        d = dias_atraso(r, ref)
        grupos[faixa(d)].append(r)
    print(f"=== MAPA DE RECEBIVEIS POR FAIXA ({fmt_data(ref)}) ===\n")
    total = Decimal("0.00")
    for k in FAIXA_ORDEM:
        itens = grupos[k]
        sub = sum((saldo(r) for r in itens), Decimal("0.00"))
        total += sub
        if itens:
            print(f"{FAIXA_ROTULO[k]:<28} {len(itens):>2} conta(s)  {fmt_dinheiro(sub):>14}")
    print("-" * 56)
    print(f"{'TOTAL A RECEBER':<28} {'':>2}            {fmt_dinheiro(total):>14}")
    venc_tot = sum((saldo(r) for r in abertos(linhas) if dias_atraso(r, ref) > 0), Decimal("0.00"))
    if total > 0:
        pct = (venc_tot / total * 100).quantize(Decimal("0.1"))
        print(f"\nEm atraso: {fmt_dinheiro(venc_tot)} ({pct}% do total a receber)")


def cmd_cliente(args):
    ref = hoje_de(args)
    linhas = carregar()
    nome = args.nome.strip().lower()
    do_cli = [r for r in linhas if nome in r.get("cliente", "").lower()]
    if not do_cli:
        print(f"Nenhuma conta para '{args.nome}'.")
        return
    print(f"=== EXTRATO: {args.nome} ({fmt_data(ref)}) ===\n")
    aberto_tot = Decimal("0.00")
    for r in do_cli:
        s = saldo(r)
        if r["status"] == "aberto" and s > 0:
            d = dias_atraso(r, ref)
            sit = f"ABERTO - {('atraso %d d' % d) if d > 0 else ('vence em %d d' % -d) if d < 0 else 'vence hoje'}"
            aberto_tot += s
        elif r["status"] == "pago":
            sit = "PAGO"
        else:
            sit = "CANCELADO"
        print(f"#{r['id']} {r.get('servico') or 'servico'} | {fmt_dinheiro(parse_dinheiro(r['valor']))} | venc {r['vencimento']} | {sit}")
    print("-" * 50)
    print(f"Em aberto deste cliente: {fmt_dinheiro(aberto_tot)}")


def cmd_resumo(args):
    ref = hoje_de(args)
    linhas = carregar()
    ab = abertos(linhas)
    total = sum((saldo(r) for r in ab), Decimal("0.00"))
    venc = [(dias_atraso(r, ref), r) for r in ab]
    em_atraso = [(d, r) for d, r in venc if d > 0]
    val_atraso = sum((saldo(r) for _, r in em_atraso), Decimal("0.00"))
    a_vencer = total - val_atraso
    # recebido = TUDO que ja foi pago, incluindo baixas parciais (campo "pago" de qualquer conta)
    quitadas = [r for r in linhas if r.get("status") == "pago"]
    recebido = sum((parse_dinheiro(r.get("pago") or 0) for r in linhas
                    if r.get("status") != "cancelado"), Decimal("0.00"))
    # taxa de inadimplencia = valor vencido / (valor vencido + recebido) -> proxy simples
    base = val_atraso + recebido
    inad = (val_atraso / base * 100).quantize(Decimal("0.1")) if base > 0 else Decimal("0.0")
    # semaforo
    if total == 0:
        farol = "VERDE - nada a receber em aberto"
    elif val_atraso == 0:
        farol = "VERDE - tudo em dia, nada vencido"
    elif (val_atraso / total) <= Decimal("0.2"):
        farol = "AMARELO - pouca coisa vencida, fique de olho"
    else:
        farol = "VERMELHO - muito valor vencido, priorize cobranca"
    print(f"=== PAINEL REGUA ({fmt_data(ref)}) ===\n")
    print(f"Semaforo: {farol}\n")
    print(f"A receber (em aberto) : {fmt_dinheiro(total)}  ({len(ab)} conta(s))")
    print(f"  - em dia (a vencer) : {fmt_dinheiro(a_vencer)}")
    print(f"  - vencido           : {fmt_dinheiro(val_atraso)}  ({len(em_atraso)} conta(s))")
    print(f"Ja recebido (inc. parciais): {fmt_dinheiro(recebido)}  ({len(quitadas)} conta(s) quitada(s))")
    print(f"Inadimplencia (proxy) : {inad}%")
    # mais velho
    if em_atraso:
        em_atraso.sort(key=lambda x: -x[0])
        d, r = em_atraso[0]
        print(f"\nMais antigo vencido   : #{r['id']} {r['cliente']} - {fmt_dinheiro(saldo(r))} (ha {d} dias)")
    # quantos cobrar hoje
    hoje_fila = 0
    for r in ab:
        deg = degrau_devido(dias_atraso(r, ref))
        if deg:
            hoje_fila += 1
    print(f"Contas para cobrar hoje: {hoje_fila}  (rode: regua.py hoje)")


def cmd_listar(args):
    linhas = carregar()
    filtro = (args.status or "aberto")
    if filtro != "todos":
        linhas = [r for r in linhas if r.get("status") == filtro]
    if not linhas:
        print(f"Nenhuma conta com status '{filtro}'.")
        return
    print(f"=== CONTAS ({filtro}) - {len(linhas)} ===\n")
    for r in linhas:
        print(f"#{r['id']:<3} {r['cliente']:<22} {fmt_dinheiro(parse_dinheiro(r.get('valor') or 0)):>14} "
              f"| pago {fmt_dinheiro(parse_dinheiro(r.get('pago') or 0)):>12} | venc {r['vencimento']} | {r['status']}")


# --------------------------------------------------------------------------- #
def build_parser():
    p = argparse.ArgumentParser(description="Regua - recebiveis + regua de cobranca (stdlib).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    a = sub.add_parser("add")
    a.add_argument("--cliente", required=True)
    a.add_argument("--valor", required=True)
    a.add_argument("--venc", required=True)
    a.add_argument("--servico", default="")
    a.add_argument("--emitido", default="")
    a.add_argument("--obs", default="")

    pg = sub.add_parser("pagar")
    pg.add_argument("--id", required=True)
    pg.add_argument("--valor", required=True)
    pg.add_argument("--data", default="")

    q = sub.add_parser("quitar")
    q.add_argument("--id", required=True)
    q.add_argument("--data", default="")

    c = sub.add_parser("cancelar")
    c.add_argument("--id", required=True)
    c.add_argument("--motivo", default="")

    e = sub.add_parser("editar")
    e.add_argument("--id", required=True)
    e.add_argument("--valor", default="")
    e.add_argument("--venc", default="")
    e.add_argument("--cliente", default="")
    e.add_argument("--servico", default=None)
    e.add_argument("--obs", default=None)

    for nome in ("hoje", "atrasados", "aging", "resumo"):
        s = sub.add_parser(nome)
        s.add_argument("--data", default="")

    m = sub.add_parser("marcar")
    m.add_argument("--id", required=True)
    m.add_argument("--data", default="")

    cl = sub.add_parser("cliente")
    cl.add_argument("--nome", required=True)
    cl.add_argument("--data", default="")

    ls = sub.add_parser("listar")
    ls.add_argument("--status", default="aberto",
                    choices=["aberto", "pago", "cancelado", "todos"])
    return p


CMDS = {
    "init": cmd_init, "add": cmd_add, "pagar": cmd_pagar, "quitar": cmd_quitar,
    "cancelar": cmd_cancelar, "editar": cmd_editar, "hoje": cmd_hoje,
    "marcar": cmd_marcar, "atrasados": cmd_atrasados, "aging": cmd_aging,
    "cliente": cmd_cliente, "resumo": cmd_resumo, "listar": cmd_listar,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        CMDS[args.cmd](args)
    except ValueError as ex:
        print(f"ERRO: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
