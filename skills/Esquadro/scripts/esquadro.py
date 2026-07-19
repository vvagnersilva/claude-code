#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Esquadro - motor de auditoria & conformidade.

Somente biblioteca padrao do Python (stdlib). Sem rede, sem chave de API, sem
biblioteca externa. Le e escreve uma pasta local: .esquadro/ (na raiz do projeto).

A IA e quem CONVERSA: monta o checklist a partir da norma, conduz a auditoria,
classifica a severidade, escreve a causa-raiz e o plano de acao, e narra o
relatorio em PT-BR simples. O motor faz APENAS a parte exata: guardar
checklists, registrar a auditoria item a item, calcular o INDICE DE
CONFORMIDADE, guardar as nao-conformidades, guardar o plano de acao 5W2H,
contar prazos (VENCIDO/VENCE HOJE/PERTO) e montar o relatorio (texto/HTML).
O motor NAO inventa item de norma, evidencia, data nem severidade.

Estrutura de dados em .esquadro/ :
  config.md                  -> configuracao (git-ignored)
  checklists/<slug>.json     -> um checklist-modelo por norma/area
  auditorias/<id>.json       -> uma auditoria (escopo, norma, resultados, indice)
  ncs.csv                    -> nao-conformidades
  acoes.csv                  -> plano de acao 5W2H

Uso (a IA chama por baixo; o dono so conversa):
  esquadro.py init
  esquadro.py checklist-add --slug nr12 --titulo "NR-12 Maquinas" --norma "NR-12" \
              --area "SST" --itens-arquivo /tmp/itens.txt
  esquadro.py checklists
  esquadro.py checklist-ver --slug nr12
  esquadro.py auditoria-nova --titulo "Auditoria prensa setor A" --escopo "Setor A" \
              --area SST --norma "NR-12" --checklist nr12 [--auditor "Fulano"] [--data 29/06/2026]
  esquadro.py auditar --id 1 --item 3 --status nc --severidade maior \
              --evidencia "Sem protecao fixa no ponto de operacao"
  esquadro.py auditoria-ver --id 1
  esquadro.py fechar-auditoria --id 1
  esquadro.py ncs [--status abertas|tratadas] [--severidade critica|maior|menor|obs]
  esquadro.py nc-causa --id 2 --causa "Falta de procedimento de instalacao da protecao"
  esquadro.py acao-add --nc 2 --oque "Instalar protecao fixa" --porque "Risco de amputacao" \
              --quem "Manutencao" --quando 15/07/2026 [--onde "Setor A"] [--como "..."] [--quanto "R$ 800"]
  esquadro.py acoes [--abertas|--atrasadas]
  esquadro.py acao-status --id 1 --status andamento
  esquadro.py acao-concluir --id 1 [--eficaz sim|nao]
  esquadro.py painel
  esquadro.py relatorio --id 1
  esquadro.py relatorio-html --id 1 --saida /tmp/relatorio.html

Os textos longos (itens de checklist, evidencia, "como") podem entrar por
--itens-arquivo (um item por linha) para nunca quebrar com aspas/quebras.
"""
from __future__ import annotations

import argparse
import csv
import html as _html
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime


# ----------------------------------------------------------------------------
# Localizacao da raiz do projeto (.esquadro na raiz, nao dentro da skill)
# ----------------------------------------------------------------------------
def achar_raiz():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".esquadro")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".claude")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return os.getcwd()


RAIZ = achar_raiz()
BASE = os.path.join(RAIZ, ".esquadro")
DIR_CHECK = os.path.join(BASE, "checklists")
DIR_AUD = os.path.join(BASE, "auditorias")
ARQ_NCS = os.path.join(BASE, "ncs.csv")
ARQ_ACOES = os.path.join(BASE, "acoes.csv")

COLS_NCS = ["id", "auditoria_id", "item", "descricao", "severidade",
            "causa_raiz", "evidencia", "status", "criado"]
COLS_ACOES = ["id", "nc_id", "oque", "porque", "quem", "quando", "onde",
              "como", "quanto", "status", "criado", "concluido_em", "eficaz"]

SEVERIDADES = {
    "critica": ("🔴", "Crítica", 3),
    "maior":   ("🟡", "Maior", 2),
    "menor":   ("🟢", "Menor", 1),
    "obs":     ("🔵", "Observação", 0),
}
STATUS_ITEM = {
    "conforme":  ("✅", "Conforme"),
    "nc":        ("❌", "Não conforme"),
    "parcial":   ("⚠️", "Parcial"),
    "na":        ("➖", "Não se aplica"),
    "pendente":  ("⬜", "Pendente"),
}
STATUS_ACAO = {
    "aberta":    "Aberta",
    "andamento": "Em andamento",
    "concluida": "Concluída",
}


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def slugify(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    txt = txt.lower()
    txt = re.sub(r"[^a-z0-9]+", "-", txt).strip("-")
    return txt or "item"


def hoje() -> date:
    return date.today()


def parse_data(s: str):
    """Aceita DD/MM/AAAA, DD/MM/AA, DD/MM (ano atual) e AAAA-MM-DD."""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    m = re.match(r"^(\d{1,2})/(\d{1,2})$", s)
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        try:
            return date(hoje().year, mo, d)
        except ValueError:
            return None
    return None


def fmt_data(d) -> str:
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return "(sem data)"


def garantir_base():
    os.makedirs(DIR_CHECK, exist_ok=True)
    os.makedirs(DIR_AUD, exist_ok=True)
    for arq, cols in ((ARQ_NCS, COLS_NCS), (ARQ_ACOES, COLS_ACOES)):
        if not os.path.exists(arq):
            with open(arq, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(cols)


def ler_csv(arq, cols):
    if not os.path.exists(arq):
        return []
    with open(arq, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def escrever_csv(arq, cols, linhas):
    with open(arq, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for ln in linhas:
            w.writerow({c: ln.get(c, "") for c in cols})


def proximo_id(linhas):
    mx = 0
    for ln in linhas:
        try:
            mx = max(mx, int(ln.get("id", 0)))
        except (ValueError, TypeError):
            pass
    return mx + 1


def erro(msg):
    print("ERRO: " + msg, file=sys.stderr)
    sys.exit(1)


# ----------------------------------------------------------------------------
# init
# ----------------------------------------------------------------------------
def cmd_init(args):
    garantir_base()
    print("Esquadro pronto. Pasta de dados: " + BASE)
    print("  checklists/  auditorias/  ncs.csv  acoes.csv")


# ----------------------------------------------------------------------------
# CHECKLISTS
# ----------------------------------------------------------------------------
def _carregar_itens(args):
    """Le itens de --itens-arquivo (um por linha).
    Formato por linha:  [*]Texto do item [:: criterio de conformidade]
      *  no inicio  -> item obrigatorio (peso maior)
      ::            -> separa o criterio do que conta como conforme
    Linhas vazias ou comecando com # sao ignoradas.
    """
    itens = []
    caminho = getattr(args, "itens_arquivo", None)
    if not caminho:
        return itens
    if not os.path.exists(caminho):
        erro("arquivo de itens nao encontrado: " + caminho)
    with open(caminho, encoding="utf-8") as f:
        n = 0
        for linha in f:
            linha = linha.rstrip("\n").strip()
            if not linha or linha.startswith("#"):
                continue
            obrig = False
            if linha.startswith("*"):
                obrig = True
                linha = linha[1:].strip()
            criterio = ""
            if "::" in linha:
                texto, criterio = linha.split("::", 1)
                texto, criterio = texto.strip(), criterio.strip()
            else:
                texto = linha
            n += 1
            itens.append({"n": n, "texto": texto, "criterio": criterio,
                          "obrigatorio": obrig})
    return itens


def cmd_checklist_add(args):
    garantir_base()
    slug = slugify(args.slug or args.titulo)
    itens = _carregar_itens(args)
    if not itens:
        erro("nenhum item lido. Passe --itens-arquivo com um item por linha.")
    dados = {
        "slug": slug,
        "titulo": args.titulo,
        "norma": args.norma or "",
        "area": args.area or "",
        "criado": hoje().isoformat(),
        "itens": itens,
    }
    with open(os.path.join(DIR_CHECK, slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Checklist '{args.titulo}' salvo ({len(itens)} itens) [slug: {slug}]")


def _ler_checklist(slug):
    caminho = os.path.join(DIR_CHECK, slug + ".json")
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def cmd_checklists(args):
    garantir_base()
    arqs = sorted(f for f in os.listdir(DIR_CHECK) if f.endswith(".json")) \
        if os.path.isdir(DIR_CHECK) else []
    if not arqs:
        print("Nenhum checklist guardado. Crie um com checklist-add.")
        return
    print(f"=== Checklists ({len(arqs)}) ===")
    for a in arqs:
        d = _ler_checklist(a[:-5])
        if d:
            ob = sum(1 for i in d["itens"] if i.get("obrigatorio"))
            print(f"- [{d['slug']}] {d['titulo']} — {d.get('norma') or 's/ norma'} "
                  f"| {len(d['itens'])} itens ({ob} obrigatórios) | área: {d.get('area') or '-'}")


def cmd_checklist_ver(args):
    d = _ler_checklist(slugify(args.slug))
    if not d:
        erro("checklist nao encontrado: " + args.slug)
    print(f"=== {d['titulo']} ===")
    print(f"Norma: {d.get('norma') or '-'} | Área: {d.get('area') or '-'} | "
          f"{len(d['itens'])} itens")
    for i in d["itens"]:
        mark = "★" if i.get("obrigatorio") else " "
        print(f" {mark}{i['n']:>3}. {i['texto']}")
        if i.get("criterio"):
            print(f"       conforme se: {i['criterio']}")


# ----------------------------------------------------------------------------
# AUDITORIAS
# ----------------------------------------------------------------------------
def _ler_auditoria(aid):
    caminho = os.path.join(DIR_AUD, str(aid) + ".json")
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _salvar_auditoria(d):
    with open(os.path.join(DIR_AUD, str(d["id"]) + ".json"), "w",
              encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def _proximo_id_auditoria():
    if not os.path.isdir(DIR_AUD):
        return 1
    ids = []
    for a in os.listdir(DIR_AUD):
        if a.endswith(".json"):
            try:
                ids.append(int(a[:-5]))
            except ValueError:
                pass
    return (max(ids) + 1) if ids else 1


def _calc_indice(resultados):
    """Indice de conformidade = (conforme + 0.5*parcial) / aplicaveis * 100.
    Aplicaveis = todos menos 'na' e 'pendente'."""
    conf = parc = nc = 0
    for r in resultados:
        s = r.get("status")
        if s == "conforme":
            conf += 1
        elif s == "parcial":
            parc += 1
        elif s == "nc":
            nc += 1
    aplic = conf + parc + nc
    if aplic == 0:
        return None, conf, parc, nc, aplic
    idx = (conf + 0.5 * parc) / aplic * 100
    return round(idx, 1), conf, parc, nc, aplic


def cmd_auditoria_nova(args):
    garantir_base()
    itens = []
    if args.checklist:
        d = _ler_checklist(slugify(args.checklist))
        if not d:
            erro("checklist nao encontrado: " + args.checklist)
        for i in d["itens"]:
            itens.append({"n": i["n"], "texto": i["texto"],
                          "criterio": i.get("criterio", ""),
                          "obrigatorio": i.get("obrigatorio", False),
                          "status": "pendente", "evidencia": "",
                          "severidade": ""})
    aid = _proximo_id_auditoria()
    data = parse_data(args.data) if args.data else hoje()
    if args.data and not data:
        erro("data invalida: " + args.data)
    dados = {
        "id": aid,
        "titulo": args.titulo,
        "escopo": args.escopo or "",
        "area": args.area or (d.get("area") if args.checklist else "") or "",
        "norma": args.norma or (d.get("norma") if args.checklist else "") or "",
        "checklist": slugify(args.checklist) if args.checklist else "",
        "auditor": args.auditor or "",
        "data": data.isoformat(),
        "fechada": False,
        "resultados": itens,
    }
    _salvar_auditoria(dados)
    print(f"Auditoria #{aid} criada: {args.titulo}")
    if itens:
        print(f"  {len(itens)} itens carregados do checklist '{args.checklist}'. "
              f"Use 'auditar --id {aid} --item N --status ...' para avaliar cada um.")
    else:
        print("  Sem checklist. Registre não-conformidades direto com nc-add "
              f"--auditoria {aid}.")


def cmd_auditar(args):
    garantir_base()
    d = _ler_auditoria(args.id)
    if not d:
        erro("auditoria nao encontrada: #" + str(args.id))
    if d.get("fechada"):
        erro("auditoria #%s ja esta fechada. Reabra editando o arquivo se preciso."
             % args.id)
    status = args.status
    if status not in STATUS_ITEM or status == "pendente":
        erro("status invalido. Use: conforme | nc | parcial | na")
    alvo = None
    for r in d["resultados"]:
        if r["n"] == args.item:
            alvo = r
            break
    if alvo is None:
        erro("item %s nao existe nesta auditoria." % args.item)
    alvo["status"] = status
    if args.evidencia:
        alvo["evidencia"] = args.evidencia
    if args.severidade:
        if args.severidade not in SEVERIDADES:
            erro("severidade invalida. Use: critica | maior | menor | obs")
        alvo["severidade"] = args.severidade
    # cria/atualiza NC automatica para itens nc/parcial
    if status in ("nc", "parcial"):
        sev = args.severidade or alvo.get("severidade") or \
            ("maior" if alvo.get("obrigatorio") else "menor")
        alvo["severidade"] = sev
        _sync_nc_de_item(d, alvo, sev)
    _salvar_auditoria(d)
    ic = STATUS_ITEM[status]
    print(f"Item {args.item} → {ic[0]} {ic[1]}"
          + (f" ({SEVERIDADES[alvo['severidade']][1]})" if alvo.get("severidade") else ""))
    idx, conf, parc, nc, aplic = _calc_indice(d["resultados"])
    pend = sum(1 for r in d["resultados"] if r["status"] == "pendente")
    if idx is not None:
        print(f"  Índice parcial de conformidade: {idx}%  "
              f"(✅{conf} ⚠️{parc} ❌{nc} de {aplic} aplicáveis; {pend} pendentes)")


def _sync_nc_de_item(auditoria, item, sev):
    """Garante uma NC ligada a (auditoria,item). Cria se nao existir."""
    ncs = ler_csv(ARQ_NCS, COLS_NCS)
    chave_aud = str(auditoria["id"])
    for n in ncs:
        if n.get("auditoria_id") == chave_aud and n.get("item") == str(item["n"]):
            n["severidade"] = sev
            if item.get("evidencia"):
                n["evidencia"] = item["evidencia"]
            escrever_csv(ARQ_NCS, COLS_NCS, ncs)
            return
    nid = proximo_id(ncs)
    ncs.append({
        "id": nid, "auditoria_id": chave_aud, "item": str(item["n"]),
        "descricao": item["texto"], "severidade": sev, "causa_raiz": "",
        "evidencia": item.get("evidencia", ""), "status": "aberta",
        "criado": hoje().isoformat(),
    })
    escrever_csv(ARQ_NCS, COLS_NCS, ncs)


def cmd_auditoria_ver(args):
    d = _ler_auditoria(args.id)
    if not d:
        erro("auditoria nao encontrada: #" + str(args.id))
    idx, conf, parc, nc, aplic = _calc_indice(d["resultados"])
    print(f"=== Auditoria #{d['id']}: {d['titulo']} {'[FECHADA]' if d.get('fechada') else ''}")
    print(f"Escopo: {d.get('escopo') or '-'} | Área: {d.get('area') or '-'} | "
          f"Norma: {d.get('norma') or '-'}")
    print(f"Data: {fmt_data(parse_data_iso(d.get('data')))} | "
          f"Auditor: {d.get('auditor') or '-'}")
    if idx is not None:
        print(f"Índice de conformidade: {idx}%  (✅{conf} ⚠️{parc} ❌{nc} "
              f"de {aplic} aplicáveis)")
    if d["resultados"]:
        print("\nItens:")
        for r in d["resultados"]:
            ic = STATUS_ITEM.get(r["status"], ("?", r["status"]))
            sev = f" {SEVERIDADES[r['severidade']][0]}" if r.get("severidade") else ""
            print(f" {ic[0]}{sev} {r['n']:>3}. {r['texto']}")
            if r.get("evidencia"):
                print(f"        evidência: {r['evidencia']}")


def parse_data_iso(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return parse_data(s)


def cmd_auditorias(args):
    garantir_base()
    if not os.path.isdir(DIR_AUD):
        print("Nenhuma auditoria.")
        return
    ids = sorted(int(a[:-5]) for a in os.listdir(DIR_AUD) if a.endswith(".json"))
    if not ids:
        print("Nenhuma auditoria ainda. Crie uma com auditoria-nova.")
        return
    print(f"=== Auditorias ({len(ids)}) ===")
    for i in ids:
        d = _ler_auditoria(i)
        idx, conf, parc, nc, aplic = _calc_indice(d["resultados"])
        tag = "FECHADA" if d.get("fechada") else "aberta"
        si = f"{idx}%" if idx is not None else "sem itens avaliados"
        print(f"#{d['id']} [{tag}] {d['titulo']} — {d.get('norma') or '-'} | "
              f"conformidade: {si} | ❌{nc} NC")


def cmd_fechar_auditoria(args):
    d = _ler_auditoria(args.id)
    if not d:
        erro("auditoria nao encontrada: #" + str(args.id))
    pend = [r for r in d["resultados"] if r["status"] == "pendente"]
    if pend and not args.forcar:
        erro(f"{len(pend)} item(ns) ainda pendente(s). Avalie todos ou use --forcar.")
    d["fechada"] = True
    idx, conf, parc, nc, aplic = _calc_indice(d["resultados"])
    d["indice_final"] = idx
    _salvar_auditoria(d)
    print(f"Auditoria #{d['id']} fechada. Índice final de conformidade: "
          f"{idx if idx is not None else '-'}%  (❌{nc} não-conformidades)")


# ----------------------------------------------------------------------------
# NAO-CONFORMIDADES
# ----------------------------------------------------------------------------
def cmd_nc_add(args):
    garantir_base()
    if args.severidade not in SEVERIDADES:
        erro("severidade invalida. Use: critica | maior | menor | obs")
    ncs = ler_csv(ARQ_NCS, COLS_NCS)
    nid = proximo_id(ncs)
    ncs.append({
        "id": nid,
        "auditoria_id": str(args.auditoria) if args.auditoria else "",
        "item": str(args.item) if args.item else "",
        "descricao": args.descricao,
        "severidade": args.severidade,
        "causa_raiz": args.causa or "",
        "evidencia": args.evidencia or "",
        "status": "aberta",
        "criado": hoje().isoformat(),
    })
    escrever_csv(ARQ_NCS, COLS_NCS, ncs)
    sv = SEVERIDADES[args.severidade]
    print(f"NC #{nid} registrada {sv[0]} {sv[1]}: {args.descricao}")


def cmd_nc_causa(args):
    ncs = ler_csv(ARQ_NCS, COLS_NCS)
    alvo = next((n for n in ncs if n["id"] == str(args.id)), None)
    if not alvo:
        erro("NC nao encontrada: #" + str(args.id))
    alvo["causa_raiz"] = args.causa
    escrever_csv(ARQ_NCS, COLS_NCS, ncs)
    print(f"Causa-raiz da NC #{args.id} registrada.")


def _acoes_por_nc(nc_id):
    return [a for a in ler_csv(ARQ_ACOES, COLS_ACOES) if a.get("nc_id") == str(nc_id)]


def cmd_ncs(args):
    garantir_base()
    ncs = ler_csv(ARQ_NCS, COLS_NCS)
    if args.status == "abertas":
        ncs = [n for n in ncs if n.get("status") != "tratada"]
    elif args.status == "tratadas":
        ncs = [n for n in ncs if n.get("status") == "tratada"]
    if args.severidade:
        ncs = [n for n in ncs if n.get("severidade") == args.severidade]
    if not ncs:
        print("Nenhuma não-conformidade nesse filtro.")
        return
    ordem = {"critica": 0, "maior": 1, "menor": 2, "obs": 3}
    ncs.sort(key=lambda n: ordem.get(n.get("severidade"), 9))
    print(f"=== Não-conformidades ({len(ncs)}) ===")
    for n in ncs:
        sv = SEVERIDADES.get(n.get("severidade"), ("?", n.get("severidade"), 0))
        ref = f"aud#{n['auditoria_id']}/item {n['item']}" if n.get("auditoria_id") else "avulsa"
        nac = len(_acoes_por_nc(n["id"]))
        print(f"{sv[0]} NC#{n['id']} [{sv[1]}] {n['descricao']}  ({ref})"
              f"  — {nac} ação(ões) | {n.get('status')}")
        if n.get("causa_raiz"):
            print(f"     causa-raiz: {n['causa_raiz']}")
        if n.get("evidencia"):
            print(f"     evidência: {n['evidencia']}")


# ----------------------------------------------------------------------------
# PLANO DE ACAO (5W2H)
# ----------------------------------------------------------------------------
def cmd_acao_add(args):
    garantir_base()
    ncs = ler_csv(ARQ_NCS, COLS_NCS)
    if not any(n["id"] == str(args.nc) for n in ncs):
        erro("NC #%s nao existe. Crie a NC antes da acao." % args.nc)
    quando = parse_data(args.quando) if args.quando else None
    if args.quando and not quando:
        erro("data --quando invalida: " + args.quando)
    acoes = ler_csv(ARQ_ACOES, COLS_ACOES)
    aid = proximo_id(acoes)
    acoes.append({
        "id": aid, "nc_id": str(args.nc),
        "oque": args.oque, "porque": args.porque or "",
        "quem": args.quem or "", "quando": quando.isoformat() if quando else "",
        "onde": args.onde or "", "como": args.como or "",
        "quanto": args.quanto or "", "status": "aberta",
        "criado": hoje().isoformat(), "concluido_em": "", "eficaz": "",
    })
    escrever_csv(ARQ_ACOES, COLS_ACOES, acoes)
    print(f"Ação #{aid} criada para a NC #{args.nc}: {args.oque}"
          + (f" (prazo {fmt_data(quando)})" if quando else " (sem prazo!)"))


def _flag_prazo(quando_iso):
    d = parse_data_iso(quando_iso)
    if not d:
        return "", None
    delta = (d - hoje()).days
    if delta < 0:
        return "🔴 VENCIDO", delta
    if delta == 0:
        return "🟠 VENCE HOJE", delta
    if delta <= 3:
        return f"🟡 vence em {delta}d", delta
    return f"em {delta}d", delta


def cmd_acoes(args):
    garantir_base()
    acoes = ler_csv(ARQ_ACOES, COLS_ACOES)
    if args.abertas:
        acoes = [a for a in acoes if a.get("status") != "concluida"]
    if args.atrasadas:
        novos = []
        for a in acoes:
            if a.get("status") == "concluida":
                continue
            _, delta = _flag_prazo(a.get("quando"))
            if delta is not None and delta < 0:
                novos.append(a)
        acoes = novos
    if not acoes:
        print("Nenhuma ação nesse filtro.")
        return
    # ordena por prazo (sem data por ultimo)
    def chave(a):
        d = parse_data_iso(a.get("quando"))
        return (d is None, d or date.max)
    acoes.sort(key=chave)
    print(f"=== Plano de ação ({len(acoes)}) ===")
    for a in acoes:
        flag, _ = _flag_prazo(a.get("quando"))
        st = STATUS_ACAO.get(a.get("status"), a.get("status"))
        prazo = fmt_data(parse_data_iso(a.get("quando"))) if a.get("quando") else "sem prazo"
        print(f"Ação#{a['id']} (NC#{a['nc_id']}) — {a['oque']}")
        print(f"    quem: {a.get('quem') or '-'} | prazo: {prazo} {flag} | {st}"
              + (f" | custo: {a['quanto']}" if a.get("quanto") else ""))


def cmd_acao_status(args):
    acoes = ler_csv(ARQ_ACOES, COLS_ACOES)
    alvo = next((a for a in acoes if a["id"] == str(args.id)), None)
    if not alvo:
        erro("ação nao encontrada: #" + str(args.id))
    if args.status not in STATUS_ACAO:
        erro("status invalido. Use: aberta | andamento | concluida")
    alvo["status"] = args.status
    if args.status == "concluida" and not alvo.get("concluido_em"):
        alvo["concluido_em"] = hoje().isoformat()
    escrever_csv(ARQ_ACOES, COLS_ACOES, acoes)
    print(f"Ação #{args.id} → {STATUS_ACAO[args.status]}")
    _talvez_tratar_nc(alvo["nc_id"])


def cmd_acao_concluir(args):
    acoes = ler_csv(ARQ_ACOES, COLS_ACOES)
    alvo = next((a for a in acoes if a["id"] == str(args.id)), None)
    if not alvo:
        erro("ação nao encontrada: #" + str(args.id))
    alvo["status"] = "concluida"
    alvo["concluido_em"] = hoje().isoformat()
    if args.eficaz:
        alvo["eficaz"] = args.eficaz
    escrever_csv(ARQ_ACOES, COLS_ACOES, acoes)
    print(f"Ação #{args.id} concluída em {fmt_data(hoje())}"
          + (f" | eficácia verificada: {args.eficaz}" if args.eficaz else
             " | (verifique a eficácia depois com --eficaz sim|nao)"))
    _talvez_tratar_nc(alvo["nc_id"])


def _talvez_tratar_nc(nc_id):
    """Se todas as acoes da NC estao concluidas, marca a NC como tratada."""
    acoes = _acoes_por_nc(nc_id)
    if acoes and all(a.get("status") == "concluida" for a in acoes):
        ncs = ler_csv(ARQ_NCS, COLS_NCS)
        for n in ncs:
            if n["id"] == str(nc_id) and n.get("status") != "tratada":
                n["status"] = "tratada"
                escrever_csv(ARQ_NCS, COLS_NCS, ncs)
                print(f"  → NC #{nc_id} marcada como TRATADA (todas as ações concluídas).")
                return


# ----------------------------------------------------------------------------
# PAINEL
# ----------------------------------------------------------------------------
def cmd_painel(args):
    garantir_base()
    ids = sorted(int(a[:-5]) for a in os.listdir(DIR_AUD) if a.endswith(".json")) \
        if os.path.isdir(DIR_AUD) else []
    ncs = ler_csv(ARQ_NCS, COLS_NCS)
    acoes = ler_csv(ARQ_ACOES, COLS_ACOES)
    print("=== Painel Esquadro ===")
    print(f"Auditorias: {len(ids)}")
    indices = []
    for i in ids:
        d = _ler_auditoria(i)
        idx, *_ = _calc_indice(d["resultados"])
        if idx is not None:
            indices.append(idx)
    if indices:
        print(f"  Índice médio de conformidade: {round(sum(indices)/len(indices),1)}%")
    abertas = [n for n in ncs if n.get("status") != "tratada"]
    porsev = {}
    for n in abertas:
        porsev[n.get("severidade")] = porsev.get(n.get("severidade"), 0) + 1
    print(f"NCs abertas: {len(abertas)}")
    for sev in ("critica", "maior", "menor", "obs"):
        if porsev.get(sev):
            s = SEVERIDADES[sev]
            print(f"  {s[0]} {s[1]}: {porsev[sev]}")
    ac_abertas = [a for a in acoes if a.get("status") != "concluida"]
    atrasadas = [a for a in ac_abertas
                 if (_flag_prazo(a.get("quando"))[1] or 0) < 0 and a.get("quando")]
    print(f"Ações abertas: {len(ac_abertas)}  |  atrasadas: {len(atrasadas)}")
    if atrasadas:
        print("  ⚠️ Ações vencidas:")
        for a in atrasadas[:8]:
            print(f"     Ação#{a['id']} (NC#{a['nc_id']}) {a['oque']} — "
                  f"venceu {fmt_data(parse_data_iso(a.get('quando')))}")


# ----------------------------------------------------------------------------
# RELATORIO
# ----------------------------------------------------------------------------
def _ler_config():
    """Le .esquadro/config.md em pares simples 'rotulo: valor'.

    Aceita os formatos de Markdown que o SETUP.md grava, incluindo o ':' DENTRO
    do negrito ('- **Rotulo:** valor'), '- **Rotulo**: valor' e '- Rotulo: valor'.
    A estrategia: remove o marcador de lista e TODO negrito (** / __) antes de
    separar no primeiro ':' — assim o '**' de fechamento nunca entra no valor.
    """
    caminho = os.path.join(BASE, "config.md")
    cfg = {}
    if not os.path.exists(caminho):
        return cfg
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            linha = re.sub(r"^[-*]\s+", "", linha)          # marcador de lista
            linha = linha.replace("**", "").replace("__", "")  # negrito markdown
            m = re.match(r"^(.+?)\s*[:：]\s*(.+)$", linha)
            if m:
                cfg[slugify(m.group(1))] = m.group(2).strip()
    return cfg


def _dados_relatorio(aid):
    d = _ler_auditoria(aid)
    if not d:
        erro("auditoria nao encontrada: #" + str(aid))
    idx, conf, parc, nc, aplic = _calc_indice(d["resultados"])
    ncs = [n for n in ler_csv(ARQ_NCS, COLS_NCS)
           if n.get("auditoria_id") == str(aid)]
    acoes = ler_csv(ARQ_ACOES, COLS_ACOES)
    return d, idx, conf, parc, nc, aplic, ncs, acoes


def cmd_relatorio(args):
    d, idx, conf, parc, nc, aplic, ncs, acoes = _dados_relatorio(args.id)
    print(f"RELATÓRIO DE AUDITORIA #{d['id']}")
    print("=" * 48)
    print(f"Título: {d['titulo']}")
    print(f"Escopo: {d.get('escopo') or '-'}")
    print(f"Norma/Padrão: {d.get('norma') or '-'}")
    print(f"Área: {d.get('area') or '-'}")
    print(f"Data: {fmt_data(parse_data_iso(d.get('data')))}")
    print(f"Auditor: {d.get('auditor') or '-'}")
    print(f"Situação: {'FECHADA' if d.get('fechada') else 'em andamento'}")
    print("-" * 48)
    if idx is not None:
        print(f"ÍNDICE DE CONFORMIDADE: {idx}%")
        print(f"  ✅ Conformes: {conf}   ⚠️ Parciais: {parc}   "
              f"❌ Não conformes: {nc}   (de {aplic} aplicáveis)")
    print("-" * 48)
    print("NÃO-CONFORMIDADES:")
    if not ncs:
        print("  Nenhuma. Tudo conforme no escopo avaliado.")
    for n in sorted(ncs, key=lambda x: {"critica":0,"maior":1,"menor":2,"obs":3}
                    .get(x.get("severidade"), 9)):
        sv = SEVERIDADES.get(n.get("severidade"), ("?", "?", 0))
        print(f"  {sv[0]} NC#{n['id']} [{sv[1]}] {n['descricao']}")
        if n.get("evidencia"):
            print(f"       evidência: {n['evidencia']}")
        if n.get("causa_raiz"):
            print(f"       causa-raiz: {n['causa_raiz']}")
        for a in acoes:
            if a.get("nc_id") == n["id"]:
                prazo = fmt_data(parse_data_iso(a.get("quando"))) if a.get("quando") else "sem prazo"
                print(f"       → ação: {a['oque']} | {a.get('quem') or '-'} | "
                      f"{prazo} | {STATUS_ACAO.get(a.get('status'), a.get('status'))}")


def _esc(s):
    return _html.escape(str(s or ""))


def cmd_relatorio_html(args):
    d, idx, conf, parc, nc, aplic, ncs, acoes = _dados_relatorio(args.id)
    cfg = _ler_config()
    org = cfg.get("organizacao") or cfg.get("organizacao-orgao") or cfg.get("empresa") or ""
    autor = cfg.get("nome") or d.get("auditor") or ""
    cor = cfg.get("cor") or cfg.get("cor-da-marca") or "#1f5f5b"
    logo = cfg.get("logo") or ""
    # ignora placeholders de "vazio" gravados pelo setup (nao renderiza img quebrada)
    if logo.strip().lower().lstrip("(").rstrip(")") in ("nao informado", "não informado",
                                                        "", "-", "n/a", "sem logo"):
        logo = ""
    ncs_ord = sorted(ncs, key=lambda x: {"critica":0,"maior":1,"menor":2,"obs":3}
                     .get(x.get("severidade"), 9))

    def bloco_nc(n):
        sv = SEVERIDADES.get(n.get("severidade"), ("?", "?", 0))
        acs = [a for a in acoes if a.get("nc_id") == n["id"]]
        linhas_ac = ""
        for a in acs:
            prazo = fmt_data(parse_data_iso(a.get("quando"))) if a.get("quando") else "sem prazo"
            linhas_ac += (f"<tr><td>{_esc(a['oque'])}</td><td>{_esc(a.get('quem') or '-')}</td>"
                          f"<td>{_esc(prazo)}</td><td>{_esc(STATUS_ACAO.get(a.get('status'),a.get('status')))}</td></tr>")
        tab_ac = (f"<table class='ac'><thead><tr><th>O quê</th><th>Quem</th>"
                  f"<th>Quando</th><th>Status</th></tr></thead><tbody>{linhas_ac}</tbody></table>"
                  if acs else "<p class='semac'>Sem plano de ação registrado.</p>")
        return (f"<div class='nc sev-{n.get('severidade')}'>"
                f"<div class='nctit'>{sv[0]} <strong>NC#{_esc(n['id'])}</strong> "
                f"<span class='badge'>{_esc(sv[1])}</span></div>"
                f"<p class='ncdesc'>{_esc(n['descricao'])}</p>"
                + (f"<p class='evid'><b>Evidência:</b> {_esc(n['evidencia'])}</p>" if n.get('evidencia') else "")
                + (f"<p class='causa'><b>Causa-raiz:</b> {_esc(n['causa_raiz'])}</p>" if n.get('causa_raiz') else "")
                + tab_ac + "</div>")

    ncs_html = "".join(bloco_nc(n) for n in ncs_ord) or \
        "<p class='ok'>Nenhuma não-conformidade no escopo avaliado. Tudo conforme. ✅</p>"
    idx_txt = f"{idx}%" if idx is not None else "—"
    logo_html = (f"<img src='{_esc(logo)}' class='logo' alt='logo'>" if logo else "")
    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório de Auditoria #{_esc(d['id'])}</title>
<style>
  :root {{ --cor: {_esc(cor)}; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
         color: #1c2321; margin: 0; background: #f4f3ee; }}
  .pg {{ max-width: 820px; margin: 0 auto; background: #fff; padding: 40px 48px; }}
  header {{ border-bottom: 3px solid var(--cor); padding-bottom: 16px; margin-bottom: 24px;
           display: flex; align-items: center; gap: 16px; }}
  .logo {{ height: 52px; }}
  h1 {{ font-size: 22px; margin: 0; color: var(--cor); }}
  .org {{ color: #5a6661; font-size: 13px; margin-top: 2px; }}
  .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 24px;
           font-size: 13px; margin-bottom: 24px; }}
  .meta b {{ color: #5a6661; font-weight: 600; }}
  .kpi {{ display: flex; gap: 14px; margin: 18px 0 26px; }}
  .kpi .card {{ flex: 1; border: 1px solid #e4e2da; border-radius: 10px;
               padding: 14px; text-align: center; }}
  .kpi .big {{ font-size: 28px; font-weight: 700; color: var(--cor); }}
  .kpi .lbl {{ font-size: 11px; color: #5a6661; text-transform: uppercase;
              letter-spacing: .04em; }}
  h2 {{ font-size: 15px; color: var(--cor); border-bottom: 1px solid #e4e2da;
       padding-bottom: 6px; margin: 28px 0 14px; }}
  .nc {{ border: 1px solid #e4e2da; border-left: 5px solid #bbb; border-radius: 8px;
        padding: 12px 16px; margin-bottom: 12px; }}
  .nc.sev-critica {{ border-left-color: #d33; }}
  .nc.sev-maior {{ border-left-color: #e0a900; }}
  .nc.sev-menor {{ border-left-color: #3a9; }}
  .nc.sev-obs {{ border-left-color: #58c; }}
  .nctit {{ font-size: 14px; }}
  .badge {{ font-size: 11px; background: #f0efe8; padding: 2px 8px; border-radius: 20px;
           color: #5a6661; }}
  .ncdesc {{ margin: 6px 0; font-weight: 600; }}
  .evid, .causa {{ font-size: 12.5px; color: #3c4441; margin: 3px 0; }}
  table.ac {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12.5px; }}
  table.ac th {{ text-align: left; background: #f7f6f1; padding: 5px 8px;
               border: 1px solid #e4e2da; }}
  table.ac td {{ padding: 5px 8px; border: 1px solid #e4e2da; }}
  .semac {{ font-size: 12px; color: #9a9a90; font-style: italic; }}
  .ok {{ background: #eef6ee; border: 1px solid #cfe6cf; border-radius: 8px;
        padding: 16px; color: #2c5e2c; }}
  footer {{ margin-top: 36px; border-top: 1px solid #e4e2da; padding-top: 12px;
           font-size: 11px; color: #8a8a80; }}
  @media print {{ body {{ background: #fff; }} .pg {{ max-width: none; padding: 0; }} }}
</style></head>
<body><div class="pg">
  <header>{logo_html}<div><h1>Relatório de Auditoria</h1>
    <div class="org">{_esc(org)}</div></div></header>
  <div class="meta">
    <div><b>Título:</b> {_esc(d['titulo'])}</div>
    <div><b>Norma/Padrão:</b> {_esc(d.get('norma') or '-')}</div>
    <div><b>Escopo:</b> {_esc(d.get('escopo') or '-')}</div>
    <div><b>Área:</b> {_esc(d.get('area') or '-')}</div>
    <div><b>Data:</b> {_esc(fmt_data(parse_data_iso(d.get('data'))))}</div>
    <div><b>Auditor(a):</b> {_esc(autor or '-')}</div>
  </div>
  <div class="kpi">
    <div class="card"><div class="big">{_esc(idx_txt)}</div><div class="lbl">Conformidade</div></div>
    <div class="card"><div class="big">{conf}</div><div class="lbl">Conformes</div></div>
    <div class="card"><div class="big">{parc}</div><div class="lbl">Parciais</div></div>
    <div class="card"><div class="big">{nc}</div><div class="lbl">Não conformes</div></div>
  </div>
  <h2>Não-conformidades e plano de ação</h2>
  {ncs_html}
  <footer>Relatório gerado pelo Esquadro a partir de dados locais. Documento de
  gestão interna; não substitui parecer/laudo técnico ou jurídico oficial.</footer>
</div></body></html>"""
    saida = args.saida or os.path.join(BASE, f"relatorio-auditoria-{d['id']}.html")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print("Relatório HTML gerado: " + saida)
    print("Abra no navegador e use Imprimir → Salvar como PDF para o documento final.")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(description="Esquadro - auditoria & conformidade")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init")

    s = sub.add_parser("checklist-add")
    s.add_argument("--slug")
    s.add_argument("--titulo", required=True)
    s.add_argument("--norma")
    s.add_argument("--area")
    s.add_argument("--itens-arquivo", dest="itens_arquivo")

    sub.add_parser("checklists")

    s = sub.add_parser("checklist-ver")
    s.add_argument("--slug", required=True)

    s = sub.add_parser("auditoria-nova")
    s.add_argument("--titulo", required=True)
    s.add_argument("--escopo")
    s.add_argument("--area")
    s.add_argument("--norma")
    s.add_argument("--checklist")
    s.add_argument("--auditor")
    s.add_argument("--data")

    s = sub.add_parser("auditar")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--item", type=int, required=True)
    s.add_argument("--status", required=True)
    s.add_argument("--evidencia")
    s.add_argument("--severidade")

    s = sub.add_parser("auditoria-ver")
    s.add_argument("--id", type=int, required=True)

    sub.add_parser("auditorias")

    s = sub.add_parser("fechar-auditoria")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--forcar", action="store_true")

    s = sub.add_parser("nc-add")
    s.add_argument("--auditoria")
    s.add_argument("--item")
    s.add_argument("--descricao", required=True)
    s.add_argument("--severidade", required=True)
    s.add_argument("--causa")
    s.add_argument("--evidencia")

    s = sub.add_parser("nc-causa")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--causa", required=True)

    s = sub.add_parser("ncs")
    s.add_argument("--status", choices=["abertas", "tratadas"])
    s.add_argument("--severidade", choices=list(SEVERIDADES.keys()))

    s = sub.add_parser("acao-add")
    s.add_argument("--nc", type=int, required=True)
    s.add_argument("--oque", required=True)
    s.add_argument("--porque")
    s.add_argument("--quem")
    s.add_argument("--quando")
    s.add_argument("--onde")
    s.add_argument("--como")
    s.add_argument("--quanto")

    s = sub.add_parser("acoes")
    s.add_argument("--abertas", action="store_true")
    s.add_argument("--atrasadas", action="store_true")

    s = sub.add_parser("acao-status")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--status", required=True)

    s = sub.add_parser("acao-concluir")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--eficaz", choices=["sim", "nao"])

    sub.add_parser("painel")

    s = sub.add_parser("relatorio")
    s.add_argument("--id", type=int, required=True)

    s = sub.add_parser("relatorio-html")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--saida")

    return p


DISPATCH = {
    "init": cmd_init,
    "checklist-add": cmd_checklist_add,
    "checklists": cmd_checklists,
    "checklist-ver": cmd_checklist_ver,
    "auditoria-nova": cmd_auditoria_nova,
    "auditar": cmd_auditar,
    "auditoria-ver": cmd_auditoria_ver,
    "auditorias": cmd_auditorias,
    "fechar-auditoria": cmd_fechar_auditoria,
    "nc-add": cmd_nc_add,
    "nc-causa": cmd_nc_causa,
    "ncs": cmd_ncs,
    "acao-add": cmd_acao_add,
    "acoes": cmd_acoes,
    "acao-status": cmd_acao_status,
    "acao-concluir": cmd_acao_concluir,
    "painel": cmd_painel,
    "relatorio": cmd_relatorio,
    "relatorio-html": cmd_relatorio_html,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.cmd:
        build_parser().print_help()
        return
    DISPATCH[args.cmd](args)


if __name__ == "__main__":
    main()
