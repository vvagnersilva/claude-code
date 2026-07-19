#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplauso — motor de reputacao e prova social (somente biblioteca padrao do Python).

Guarda tudo localmente na pasta .aplauso/ ao lado de onde o dono trabalha:
  .aplauso/config.md         -> negocio, tom, canais (criado no setup de 1a execucao)
  .aplauso/depoimentos.csv   -> banco de elogios/avaliacoes coletados
  .aplauso/indicacoes.csv    -> pedidos de indicacao e quem indicou

NUNCA inventa nota, depoimento ou cliente. Só registra o que o dono informa.
Tudo fica no computador do dono. Nada é enviado para a internet.

Uso (o Claude chama por baixo; o dono so conversa):
  python3 aplauso.py init
  python3 aplauso.py add-dep --cliente "Maria" --texto "Amei o resultado!" \
      --nota 5 --canal whatsapp --servico "Limpeza de pele" --consent sim
  python3 aplauso.py list-dep [--so-sem-consent] [--canal google]
  python3 aplauso.py pedir-dep --cliente "Joao" --servico "Corte" --canal google   # registra um PEDIDO pendente
  python3 aplauso.py marcar-recebido --id 3 --texto "..." --nota 5
  python3 aplauso.py add-ind --quem-indicou "Ana" --indicado "Clara" --status pedido
  python3 aplauso.py list-ind [--status pedido]
  python3 aplauso.py resumo
"""

import argparse, csv, os, sys, datetime

ROOT = ".aplauso"
DEP = os.path.join(ROOT, "depoimentos.csv")
IND = os.path.join(ROOT, "indicacoes.csv")
CFG = os.path.join(ROOT, "config.md")

DEP_COLS = ["id", "data", "cliente", "servico", "canal", "nota", "texto",
            "consent", "status", "obs"]
IND_COLS = ["id", "data", "quem_indicou", "indicado", "status", "recompensa", "obs"]

CANAIS = ["google", "whatsapp", "instagram", "facebook", "ifood", "site",
          "email", "indicacao", "outro"]
# status de depoimento: pendente (pedido feito, sem resposta) | recebido | publicado
# status de indicacao: pedido | indicou | virou_cliente | recompensado


def hoje():
    # data local AAAA-MM-DD, sem depender de relogio externo
    return datetime.date.today().isoformat()


def br(d):
    # AAAA-MM-DD -> DD/MM/AAAA
    try:
        y, m, dd = d.split("-")
        return f"{dd}/{m}/{y}"
    except Exception:
        return d


def garante(path, cols):
    os.makedirs(ROOT, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(cols)


def ler(path, cols):
    garante(path, cols)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def proximo_id(linhas):
    ids = [int(l["id"]) for l in linhas if l.get("id", "").isdigit()]
    return (max(ids) + 1) if ids else 1


def escreve(path, cols, linhas):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for l in linhas:
            w.writerow({c: l.get(c, "") for c in cols})


# ---------------- comandos ----------------

def cmd_init(a):
    garante(DEP, DEP_COLS)
    garante(IND, IND_COLS)
    if not os.path.exists(CFG):
        with open(CFG, "w", encoding="utf-8") as f:
            f.write("# Configuracao do Aplauso\n\n"
                    "Preencha na primeira conversa (o Aplauso te guia):\n\n"
                    "- negocio:\n- tom_de_voz:\n- servico_principal:\n"
                    "- canais_de_avaliacao:\n")
    print("OK: pasta .aplauso/ pronta (depoimentos.csv, indicacoes.csv, config.md).")


def cmd_add_dep(a):
    linhas = ler(DEP, DEP_COLS)
    nid = proximo_id(linhas)
    nota = (a.nota or "").strip()
    if nota and nota not in ("1", "2", "3", "4", "5"):
        print("AVISO: nota deve ser de 1 a 5 (deixei em branco).")
        nota = ""
    canal = (a.canal or "outro").lower()
    if canal not in CANAIS:
        canal = "outro"
    consent = "sim" if (a.consent or "").lower().startswith("s") else "nao"
    linhas.append({
        "id": nid, "data": hoje(), "cliente": a.cliente or "",
        "servico": a.servico or "", "canal": canal, "nota": nota,
        "texto": (a.texto or "").replace("\n", " ").strip(),
        "consent": consent, "status": "recebido", "obs": a.obs or "",
    })
    escreve(DEP, DEP_COLS, linhas)
    aviso = "" if consent == "sim" else "  (PEDIR consentimento antes de publicar!)"
    print(f"OK: depoimento #{nid} de {a.cliente or 'cliente'} salvo "
          f"[nota={nota or '-'} canal={canal} consent={consent}].{aviso}")


def cmd_pedir_dep(a):
    """Registra um PEDIDO de depoimento ainda sem resposta (status pendente)."""
    linhas = ler(DEP, DEP_COLS)
    nid = proximo_id(linhas)
    canal = (a.canal or "outro").lower()
    if canal not in CANAIS:
        canal = "outro"
    linhas.append({
        "id": nid, "data": hoje(), "cliente": a.cliente or "",
        "servico": a.servico or "", "canal": canal, "nota": "",
        "texto": "", "consent": "nao", "status": "pendente", "obs": a.obs or "",
    })
    escreve(DEP, DEP_COLS, linhas)
    print(f"OK: pedido #{nid} para {a.cliente or 'cliente'} marcado como PENDENTE "
          f"(canal {canal}). Use marcar-recebido quando o cliente responder.")


def cmd_marcar_recebido(a):
    linhas = ler(DEP, DEP_COLS)
    achou = False
    for l in linhas:
        if l["id"] == str(a.id):
            l["status"] = "recebido"
            if a.texto:
                l["texto"] = a.texto.replace("\n", " ").strip()
            if a.nota and a.nota in ("1", "2", "3", "4", "5"):
                l["nota"] = a.nota
            if a.consent:
                l["consent"] = "sim" if a.consent.lower().startswith("s") else "nao"
            achou = True
    if not achou:
        print(f"ERRO: pedido #{a.id} nao encontrado."); sys.exit(1)
    escreve(DEP, DEP_COLS, linhas)
    print(f"OK: pedido #{a.id} marcado como RECEBIDO.")


def cmd_list_dep(a):
    linhas = ler(DEP, DEP_COLS)
    if a.so_sem_consent:
        linhas = [l for l in linhas if l["consent"] != "sim" and l["status"] == "recebido"]
    if a.canal:
        linhas = [l for l in linhas if l["canal"] == a.canal.lower()]
    if a.pendentes:
        linhas = [l for l in linhas if l["status"] == "pendente"]
    if not linhas:
        print("(nenhum depoimento com esse filtro ainda)"); return
    for l in linhas:
        estrela = ("★" * int(l["nota"])) if l["nota"].isdigit() else "—"
        print(f"#{l['id']} {br(l['data'])} | {l['cliente'] or '-'} "
              f"| {l['canal']} | {estrela} | {l['status']} "
              f"| consent={l['consent']}")
        if l["texto"]:
            print(f'      "{l["texto"][:160]}"')


def cmd_add_ind(a):
    linhas = ler(IND, IND_COLS)
    nid = proximo_id(linhas)
    status = (a.status or "pedido").lower()
    linhas.append({
        "id": nid, "data": hoje(), "quem_indicou": a.quem_indicou or "",
        "indicado": a.indicado or "", "status": status,
        "recompensa": a.recompensa or "", "obs": a.obs or "",
    })
    escreve(IND, IND_COLS, linhas)
    print(f"OK: indicacao #{nid} registrada "
          f"({a.quem_indicou or '?'} -> {a.indicado or '?'}, status {status}).")


def cmd_set_ind(a):
    linhas = ler(IND, IND_COLS)
    achou = False
    for l in linhas:
        if l["id"] == str(a.id):
            if a.status:
                l["status"] = a.status.lower()
            if a.recompensa:
                l["recompensa"] = a.recompensa
            achou = True
    if not achou:
        print(f"ERRO: indicacao #{a.id} nao encontrada."); sys.exit(1)
    escreve(IND, IND_COLS, linhas)
    print(f"OK: indicacao #{a.id} atualizada.")


def cmd_list_ind(a):
    linhas = ler(IND, IND_COLS)
    if a.status:
        linhas = [l for l in linhas if l["status"] == a.status.lower()]
    if not linhas:
        print("(nenhuma indicacao com esse filtro ainda)"); return
    for l in linhas:
        print(f"#{l['id']} {br(l['data'])} | {l['quem_indicou'] or '-'} "
              f"-> {l['indicado'] or '-'} | {l['status']} "
              f"| recompensa={l['recompensa'] or '-'}")


def cmd_resumo(a):
    deps = ler(DEP, DEP_COLS)
    inds = ler(IND, IND_COLS)
    recebidos = [d for d in deps if d["status"] in ("recebido", "publicado")]
    pendentes = [d for d in deps if d["status"] == "pendente"]
    sem_consent = [d for d in recebidos if d["consent"] != "sim"]
    notas = [int(d["nota"]) for d in recebidos if d["nota"].isdigit()]
    media = (sum(notas) / len(notas)) if notas else 0

    print("=" * 48)
    print("  PAINEL DO APLAUSO")
    print("=" * 48)
    print(f"Depoimentos recebidos : {len(recebidos)}")
    print(f"Pedidos pendentes     : {len(pendentes)}")
    if notas:
        print(f"Nota media            : {media:.1f}  ({'★'*round(media)})  "
              f"de {len(notas)} avaliacoes com nota")
    # distribuicao por nota
    if notas:
        print("Distribuicao          :", end=" ")
        for n in (5, 4, 3, 2, 1):
            c = notas.count(n)
            if c:
                print(f"{n}★={c}", end="  ")
        print()
    # por canal
    canais = {}
    for d in recebidos:
        canais[d["canal"]] = canais.get(d["canal"], 0) + 1
    if canais:
        print("Por canal             :",
              "  ".join(f"{k}={v}" for k, v in sorted(canais.items(), key=lambda x: -x[1])))
    if sem_consent:
        print(f"\n[!] {len(sem_consent)} depoimento(s) SEM consentimento para publicar "
              f"(IDs: {', '.join(d['id'] for d in sem_consent)}) -> peca permissao antes.")
    if pendentes:
        nomes = ", ".join(f"#{d['id']} {d['cliente'] or '?'}" for d in pendentes[:8])
        print(f"\n[->] Pedidos aguardando resposta: {nomes}")
    # indicacoes
    ped = [i for i in inds if i["status"] == "pedido"]
    virou = [i for i in inds if i["status"] == "virou_cliente"]
    print(f"\nIndicacoes            : {len(inds)} no total | "
          f"{len(ped)} aguardando | {len(virou)} viraram cliente")
    if len(recebidos) == 0 and len(pendentes) == 0:
        print("\nComece pelo modo Pedir: escolha 1 cliente feliz e peca a 1a avaliacao.")
    print("=" * 48)


def main():
    p = argparse.ArgumentParser(description="Motor do Aplauso (reputacao e prova social).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)

    s = sub.add_parser("add-dep"); s.set_defaults(func=cmd_add_dep)
    s.add_argument("--cliente"); s.add_argument("--texto")
    s.add_argument("--nota"); s.add_argument("--canal")
    s.add_argument("--servico"); s.add_argument("--consent")
    s.add_argument("--obs")

    s = sub.add_parser("pedir-dep"); s.set_defaults(func=cmd_pedir_dep)
    s.add_argument("--cliente"); s.add_argument("--servico")
    s.add_argument("--canal"); s.add_argument("--obs")

    s = sub.add_parser("marcar-recebido"); s.set_defaults(func=cmd_marcar_recebido)
    s.add_argument("--id", required=True); s.add_argument("--texto")
    s.add_argument("--nota"); s.add_argument("--consent")

    s = sub.add_parser("list-dep"); s.set_defaults(func=cmd_list_dep)
    s.add_argument("--so-sem-consent", action="store_true", dest="so_sem_consent")
    s.add_argument("--canal"); s.add_argument("--pendentes", action="store_true")

    s = sub.add_parser("add-ind"); s.set_defaults(func=cmd_add_ind)
    s.add_argument("--quem-indicou", dest="quem_indicou")
    s.add_argument("--indicado"); s.add_argument("--status")
    s.add_argument("--recompensa"); s.add_argument("--obs")

    s = sub.add_parser("set-ind"); s.set_defaults(func=cmd_set_ind)
    s.add_argument("--id", required=True); s.add_argument("--status")
    s.add_argument("--recompensa")

    s = sub.add_parser("list-ind"); s.set_defaults(func=cmd_list_ind)
    s.add_argument("--status")

    sub.add_parser("resumo").set_defaults(func=cmd_resumo)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
