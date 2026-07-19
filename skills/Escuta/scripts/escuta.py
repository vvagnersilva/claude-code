#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Escuta - motor local da skill de reuniao/consulta/atendimento.

Tudo fica numa pasta local `.escuta/` ao lado de onde voce roda:
  .escuta/config.md                 -> preferencias do dono (criado no 1o uso)
  .escuta/clientes/<slug>.md        -> ficha/historico de cada cliente
  .escuta/pendencias.csv            -> lista de pendencias (tarefas) de todos os clientes

Sem dependencias externas: so a biblioteca padrao do Python 3.
O motor NUNCA inventa dados. Ele so guarda, lista e organiza o que voce manda.

Comandos:
  python3 escuta.py init
  python3 escuta.py cliente "Maria Souza"                 # cria/mostra a ficha
  python3 escuta.py clientes [--sumidos DIAS]             # lista clientes (e quem sumiu)
  python3 escuta.py registrar --cliente "Maria Souza" --resumo "texto"
  python3 escuta.py pendencia --cliente "Maria" --o-que "Enviar orcamento" [--quem "Eu"] [--prazo 20/06/2026]
  python3 escuta.py pendencias [--abertas|--atrasadas|--cliente "Maria"]
  python3 escuta.py concluir --id 3
  python3 escuta.py resumo

Datas no formato brasileiro DD/MM/AAAA. "hoje" e calculado pelo relogio do computador.
"""

import sys, os, csv, re, argparse, unicodedata
from datetime import datetime, date

BASE = ".escuta"
CLIENTES_DIR = os.path.join(BASE, "clientes")
PEND_CSV = os.path.join(BASE, "pendencias.csv")
CONFIG = os.path.join(BASE, "config.md")
PEND_FIELDS = ["id", "cliente", "o_que", "quem", "prazo", "status", "criada_em", "concluida_em"]


# ----------------------------- utilidades -----------------------------

def hoje():
    return date.today()


def slugify(nome):
    t = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "cliente"


def parse_data(s):
    """Aceita DD/MM/AAAA, DD/MM/AA, DD-MM-AAAA. Devolve date ou None."""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def fmt_data(d):
    return d.strftime("%d/%m/%Y") if isinstance(d, date) else (d or "")


def garantir_estrutura():
    os.makedirs(CLIENTES_DIR, exist_ok=True)
    if not os.path.exists(PEND_CSV):
        with open(PEND_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=PEND_FIELDS).writeheader()


def ler_pendencias():
    if not os.path.exists(PEND_CSV):
        return []
    with open(PEND_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escrever_pendencias(linhas):
    with open(PEND_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PEND_FIELDS)
        w.writeheader()
        for l in linhas:
            w.writerow({k: l.get(k, "") for k in PEND_FIELDS})


def proximo_id(linhas):
    ids = [int(l["id"]) for l in linhas if str(l.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


def ficha_path(nome):
    return os.path.join(CLIENTES_DIR, slugify(nome) + ".md")


def nome_em_ficha(nome):
    """Le o nome 'oficial' gravado na ficha, se existir, senao usa o informado."""
    p = ficha_path(nome)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            primeira = f.readline().strip()
        m = re.match(r"#\s*(.+)", primeira)
        if m:
            return m.group(1).strip()
    return nome


# ----------------------------- comandos -----------------------------

def cmd_init(_):
    garantir_estrutura()
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            f.write("# Configuracao da Escuta\n\n"
                    "Preencha no primeiro uso (a skill faz isso com voce):\n"
                    "- Dono: \n- Tipo de atendimento: \n- Tom de voz: \n"
                    "- Canal de follow-up: \n- Observacoes: \n")
    print("OK - pasta .escuta/ pronta.")


def cmd_cliente(args):
    garantir_estrutura()
    p = ficha_path(args.nome)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write(f"# {args.nome}\n\n")
            f.write("## Observacoes\n(preferencias, contexto, como prefere ser tratado)\n\n")
            f.write("## Historico de encontros\n\n")
        print(f"Ficha criada: {p}")
    else:
        print(f"Ficha de {nome_em_ficha(args.nome)}:\n")
        with open(p, encoding="utf-8") as f:
            print(f.read())
    # pendencias abertas desse cliente
    abertas = [l for l in ler_pendencias()
               if slugify(l["cliente"]) == slugify(args.nome) and l["status"] == "aberta"]
    if abertas:
        print("\nPendencias abertas:")
        for l in abertas:
            print(f"  [#{l['id']}] {l['o_que']}"
                  + (f" (resp.: {l['quem']})" if l['quem'] else "")
                  + (f" - prazo {l['prazo']}" if l['prazo'] else ""))


def cmd_clientes(args):
    garantir_estrutura()
    arquivos = sorted(f for f in os.listdir(CLIENTES_DIR) if f.endswith(".md"))
    if not arquivos:
        print("Nenhum cliente ainda. Use: cliente \"Nome\"")
        return
    print(f"{len(arquivos)} cliente(s):\n")
    for a in arquivos:
        p = os.path.join(CLIENTES_DIR, a)
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        nome = re.match(r"#\s*(.+)", txt).group(1).strip() if re.match(r"#\s*(.+)", txt) else a
        # ultimo encontro = ultima data DD/MM/AAAA encontrada no historico
        datas = [parse_data(d) for d in re.findall(r"\d{2}/\d{2}/\d{4}", txt)]
        datas = [d for d in datas if d]
        ultimo = max(datas) if datas else None
        linha = f"  - {nome}"
        if ultimo:
            dias = (hoje() - ultimo).days
            linha += f"  (ultimo registro: {fmt_data(ultimo)}, ha {dias} dia(s))"
        else:
            linha += "  (sem encontro registrado)"
        if args.sumidos and ultimo and (hoje() - ultimo).days >= args.sumidos:
            linha += "  << SUMIDO"
        if args.sumidos and not ultimo:
            pass
        print(linha)


def cmd_registrar(args):
    garantir_estrutura()
    p = ficha_path(args.cliente)
    if not os.path.exists(p):
        cmd_cliente(argparse.Namespace(nome=args.cliente))
    data = parse_data(args.data) if args.data else hoje()
    bloco = f"\n### {fmt_data(data)}\n{args.resumo.strip()}\n"
    with open(p, "a", encoding="utf-8") as f:
        f.write(bloco)
    print(f"Encontro registrado na ficha de {nome_em_ficha(args.cliente)} ({fmt_data(data)}).")


def cmd_pendencia(args):
    garantir_estrutura()
    linhas = ler_pendencias()
    nid = proximo_id(linhas)
    prazo = parse_data(args.prazo) if args.prazo else None
    linhas.append({
        "id": str(nid), "cliente": args.cliente, "o_que": args.o_que,
        "quem": args.quem or "", "prazo": fmt_data(prazo) if prazo else "",
        "status": "aberta", "criada_em": fmt_data(hoje()), "concluida_em": "",
    })
    escrever_pendencias(linhas)
    print(f"Pendencia #{nid} criada para {args.cliente}: {args.o_que}"
          + (f" (prazo {fmt_data(prazo)})" if prazo else ""))


def cmd_pendencias(args):
    garantir_estrutura()
    linhas = ler_pendencias()
    if args.cliente:
        linhas = [l for l in linhas if slugify(l["cliente"]) == slugify(args.cliente)]
    if args.abertas or args.atrasadas:
        linhas = [l for l in linhas if l["status"] == "aberta"]
    if args.atrasadas:
        def atrasada(l):
            d = parse_data(l["prazo"])
            return d is not None and d < hoje()
        linhas = [l for l in linhas if atrasada(l)]
    if not linhas:
        print("Nada por aqui.")
        return
    # ordena: atrasadas primeiro, depois por prazo
    def chave(l):
        d = parse_data(l["prazo"])
        return (0 if d else 1, d or date.max)
    for l in sorted(linhas, key=chave):
        d = parse_data(l["prazo"])
        flag = ""
        if l["status"] == "aberta" and d and d < hoje():
            flag = f"  << ATRASADA ({(hoje()-d).days} dia(s))"
        elif l["status"] == "aberta" and d and d == hoje():
            flag = "  << VENCE HOJE"
        marca = "[x]" if l["status"] != "aberta" else "[ ]"
        print(f"{marca} #{l['id']} {l['cliente']}: {l['o_que']}"
              + (f" (resp.: {l['quem']})" if l['quem'] else "")
              + (f" - prazo {l['prazo']}" if l['prazo'] else "")
              + flag)


def cmd_concluir(args):
    garantir_estrutura()
    linhas = ler_pendencias()
    achou = False
    for l in linhas:
        if str(l["id"]) == str(args.id):
            l["status"] = "concluida"
            l["concluida_em"] = fmt_data(hoje())
            achou = True
            print(f"Pendencia #{l['id']} concluida: {l['o_que']}")
    if not achou:
        print(f"Nao achei a pendencia #{args.id}.")
        return
    escrever_pendencias(linhas)


def cmd_resumo(args):
    garantir_estrutura()
    pend = ler_pendencias()
    abertas = [l for l in pend if l["status"] == "aberta"]
    atrasadas = [l for l in abertas if (parse_data(l["prazo"]) and parse_data(l["prazo"]) < hoje())]
    hoje_vence = [l for l in abertas if (parse_data(l["prazo"]) and parse_data(l["prazo"]) == hoje())]
    clientes = [f for f in os.listdir(CLIENTES_DIR) if f.endswith(".md")] if os.path.isdir(CLIENTES_DIR) else []
    print("=== Panorama Escuta ===")
    print(f"Clientes com ficha: {len(clientes)}")
    print(f"Pendencias abertas: {len(abertas)}  |  atrasadas: {len(atrasadas)}  |  vencem hoje: {len(hoje_vence)}")
    if atrasadas:
        print("\nAtrasadas (resolver primeiro):")
        for l in sorted(atrasadas, key=lambda x: parse_data(x["prazo"])):
            print(f"  #{l['id']} {l['cliente']}: {l['o_que']} - prazo {l['prazo']}")
    if hoje_vence:
        print("\nVencem hoje:")
        for l in hoje_vence:
            print(f"  #{l['id']} {l['cliente']}: {l['o_que']}")


def main():
    p = argparse.ArgumentParser(description="Motor local da Escuta (reuniao/consulta/atendimento).")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init")

    c = sub.add_parser("cliente"); c.add_argument("nome")
    cs = sub.add_parser("clientes"); cs.add_argument("--sumidos", type=int, default=0)

    r = sub.add_parser("registrar")
    r.add_argument("--cliente", required=True); r.add_argument("--resumo", required=True)
    r.add_argument("--data")

    pe = sub.add_parser("pendencia")
    pe.add_argument("--cliente", required=True); pe.add_argument("--o-que", dest="o_que", required=True)
    pe.add_argument("--quem"); pe.add_argument("--prazo")

    ps = sub.add_parser("pendencias")
    ps.add_argument("--abertas", action="store_true"); ps.add_argument("--atrasadas", action="store_true")
    ps.add_argument("--cliente")

    cc = sub.add_parser("concluir"); cc.add_argument("--id", required=True)

    sub.add_parser("resumo")

    args = p.parse_args()
    fn = {
        "init": cmd_init, "cliente": cmd_cliente, "clientes": cmd_clientes,
        "registrar": cmd_registrar, "pendencia": cmd_pendencia,
        "pendencias": cmd_pendencias, "concluir": cmd_concluir, "resumo": cmd_resumo,
    }.get(args.cmd)
    if not fn:
        p.print_help(); sys.exit(1)
    fn(args)


if __name__ == "__main__":
    main()
