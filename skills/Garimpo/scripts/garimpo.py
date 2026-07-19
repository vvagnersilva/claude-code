#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Garimpo — motor de ANÁLISE de dados (somente biblioteca padrão do Python).

A IA conversa com o dono, entende a pergunta e chama este motor para fazer a
CONTA EXATA sobre o arquivo de dados (CSV/TSV). O motor NUNCA inventa número:
ele lê o arquivo real, calcula e devolve. A IA só interpreta e explica em PT-BR.

Aceita números no padrão brasileiro ("R$ 1.234,56", "1.234", "1234,5") e datas
DD/MM/AAAA, DD/MM/AA, DD-MM-AAAA e AAAA-MM-DD. Detecta o separador (vírgula,
ponto-e-vírgula ou tabulação) sozinho.

Comandos (a IA escolhe pela pergunta do dono):
  perfil   <arquivo>                       # conhece o arquivo: colunas, tipos, vazios, exemplos
  valores  <arquivo> --coluna C [--top N]  # valores distintos de uma coluna + contagem
  agrupar  <arquivo> --por A[,B] [--metrica M --op soma|media|contagem|min|max|distintos]
                     [--onde "C OP V" ...] [--top N] [--ordem desc|asc]
  ranking  <arquivo> --por A --metrica M [--op soma] [--top N]   # top + concentração 80/20
  tendencia<arquivo> --data D --periodo dia|semana|mes [--metrica M --op soma|contagem] [--onde ...]
  cruzar   <arquivo> --linhas A --colunas B [--metrica M --op soma|contagem]
  resumo   <arquivo>                       # números-chave + destaques/anomalias

OP de --onde: =  !=  >  <  >=  <=  contem   (ex.: --onde "cidade = Campinas" --onde "valor > 1000")
"""
import argparse
import csv
import io
import re
import sys
import unicodedata
from collections import defaultdict, Counter
from datetime import datetime, date
from pathlib import Path

# ----------------------------------------------------------------- utils texto

def _sa(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()

def parse_num(v):
    """Converte texto BR em float, ou None se não for número."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    if "/" in s or ":" in s:        # data (05/01/2026) ou hora — não é número
        return None
    s = re.sub(r"(?i)^\s*r\$\s*", "", s)
    s = s.replace("%", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]
    s = re.sub(r"[^\d,.\-]", "", s)
    if not s or s in ("-", ".", ","):
        return None
    if "," in s and "." in s:            # 1.234,56  -> ponto = milhar
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                        # 1234,56   -> vírgula decimal
        s = s.replace(",", ".")
    # só ponto: pode ser milhar (1.234) ou decimal (12.5) — heurística:
    elif s.count(".") == 1:
        intp, dec = s.split(".")
        if len(dec) == 3 and len(intp) <= 3 and intp.isdigit():
            s = intp + dec                # 1.234 -> 1234 (milhar)
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        n = float(s)
        return -n if neg else n
    except ValueError:
        return None

_DATE_FMTS = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]

def parse_date(v):
    if v is None:
        return None
    s = str(v).strip()[:19]
    if not s:
        return None
    s0 = s.split(" ")[0].split("T")[0]
    for f in _DATE_FMTS:
        try:
            return datetime.strptime(s0, f).date()
        except ValueError:
            continue
    return None

def fmt_num(n):
    """Float -> texto BR (1.234,56). Inteiros sem casas."""
    if n is None:
        return "—"
    if abs(n - round(n)) < 1e-9:
        s = f"{int(round(n)):,}".replace(",", ".")
    else:
        s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s

# ----------------------------------------------------------------- carga

def load(path):
    p = Path(path)
    if not p.exists():
        print(f"ERRO: não encontrei o arquivo «{path}».", file=sys.stderr); sys.exit(2)
    raw = p.read_text(encoding="utf-8-sig", errors="replace")
    sample = raw[:4096]
    delim = ","
    try:
        delim = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except Exception:
        # fallback: o que aparece mais na 1ª linha
        first = sample.splitlines()[0] if sample.splitlines() else ""
        delim = max([",", ";", "\t"], key=lambda d: first.count(d))
    rows = list(csv.reader(io.StringIO(raw), delimiter=delim))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        print("ERRO: arquivo vazio.", file=sys.stderr); sys.exit(2)
    header = [h.strip() for h in rows[0]]
    data = [dict(zip(header, r + [""] * (len(header) - len(r)))) for r in rows[1:]]
    return header, data

def resolve_col(header, name):
    """Acha a coluna real a partir de um nome aproximado (sem caso/acento)."""
    if name is None:
        return None
    t = _sa(name)
    for h in header:
        if _sa(h) == t:
            return h
    for h in header:
        if t and (t in _sa(h) or _sa(h) in t):
            return h
    print(f"ERRO: não achei a coluna «{name}». Colunas disponíveis: {', '.join(header)}",
          file=sys.stderr); sys.exit(2)

def col_is_numeric(data, col, thresh=0.8):
    vals = [d.get(col, "") for d in data if str(d.get(col, "")).strip()]
    if not vals:
        return False
    ok = sum(1 for v in vals if parse_num(v) is not None)
    return ok / len(vals) >= thresh

def col_is_date(data, col, thresh=0.7):
    vals = [d.get(col, "") for d in data if str(d.get(col, "")).strip()]
    if not vals:
        return False
    ok = sum(1 for v in vals if parse_date(v) is not None)
    return ok / len(vals) >= thresh

# ----------------------------------------------------------------- filtros

_OPS = ["!=", ">=", "<=", "=", ">", "<", " contem ", " contém "]

def parse_cond(header, expr):
    for op in _OPS:
        if op in expr:
            left, right = expr.split(op, 1)
            return resolve_col(header, left.strip()), op.strip(), right.strip()
    print(f"ERRO: condição inválida «{expr}». Use formato: coluna OP valor (OP = = != > < >= <= contem)",
          file=sys.stderr); sys.exit(2)

def apply_filters(data, conds):
    if not conds:
        return data
    out = []
    for d in data:
        keep = True
        for col, op, val in conds:
            cell = d.get(col, "")
            cn, vn = parse_num(cell), parse_num(val)
            if op in (">", "<", ">=", "<=") and cn is not None and vn is not None:
                if not ((op == ">" and cn > vn) or (op == "<" and cn < vn)
                        or (op == ">=" and cn >= vn) or (op == "<=" and cn <= vn)):
                    keep = False; break
            elif op in ("contem", "contém"):
                if _sa(val) not in _sa(cell):
                    keep = False; break
            elif op == "=":
                if cn is not None and vn is not None:
                    if abs(cn - vn) > 1e-9: keep = False; break
                elif _sa(cell) != _sa(val):
                    keep = False; break
            elif op == "!=":
                if cn is not None and vn is not None:
                    if abs(cn - vn) <= 1e-9: keep = False; break
                elif _sa(cell) == _sa(val):
                    keep = False; break
        if keep:
            out.append(d)
    return out

def aggregate(rows, metric_col, op):
    if op == "contagem":
        return float(len(rows))
    nums = [parse_num(d.get(metric_col, "")) for d in rows]
    nums = [n for n in nums if n is not None]
    if op == "distintos":
        return float(len({_sa(d.get(metric_col, "")) for d in rows if str(d.get(metric_col,"")).strip()}))
    if not nums:
        return None
    if op == "soma":  return sum(nums)
    if op == "media": return sum(nums) / len(nums)
    if op == "min":   return min(nums)
    if op == "max":   return max(nums)
    return None

# ----------------------------------------------------------------- comandos

def c_perfil(a):
    header, data = load(a.arquivo)
    print(f"📋 Arquivo: {Path(a.arquivo).name}")
    print(f"   Linhas (registros): {fmt_num(len(data))}   ·   Colunas: {len(header)}\n")
    print("Coluna | Tipo | Vazios | Valores únicos | Exemplos")
    print("-" * 64)
    for h in header:
        vals = [d.get(h, "") for d in data]
        nonempty = [v for v in vals if str(v).strip()]
        vazios = len(vals) - len(nonempty)
        if col_is_numeric(data, h):
            tipo = "número"
        elif col_is_date(data, h):
            tipo = "data"
        else:
            tipo = "texto"
        uniq = len({_sa(v) for v in nonempty})
        ex = ", ".join(list(dict.fromkeys([str(v).strip() for v in nonempty]))[:3])
        print(f"{h} | {tipo} | {vazios} | {uniq} | {ex[:50]}")
    print("\n💡 Pergunte coisas como: 'qual a soma de X por Y?', 'top 5 de Z', "
          "'quantos registros onde W?', 'como evolui por mês?'.")

def c_valores(a):
    header, data = load(a.arquivo)
    col = resolve_col(header, a.coluna)
    cnt = Counter(str(d.get(col, "")).strip() for d in data if str(d.get(col, "")).strip())
    print(f"Valores de «{col}» ({len(cnt)} distintos):\n")
    for val, n in cnt.most_common(a.top):
        print(f"  {val} — {fmt_num(n)}")

def c_agrupar(a):
    header, data = load(a.arquivo)
    conds = [parse_cond(header, e) for e in (a.onde or [])]
    rows = apply_filters(data, conds)
    cols = [resolve_col(header, c) for c in a.por.split(",")]
    metric = resolve_col(header, a.metrica) if a.metrica else None
    op = a.op or ("contagem" if not metric else "soma")
    groups = defaultdict(list)
    for d in rows:
        key = tuple(str(d.get(c, "")).strip() or "(vazio)" for c in cols)
        groups[key].append(d)
    res = [(k, aggregate(v, metric, op), len(v)) for k, v in groups.items()]
    res = [r for r in res if r[1] is not None]
    res.sort(key=lambda x: (x[1] is None, x[1]), reverse=(a.ordem != "asc"))
    if a.top:
        res = res[:a.top]
    label = f"{op}" + (f" de {metric}" if metric else " (nº de registros)")
    print(f"📊 {label}, por {', '.join(cols)}"
          + (f"  [filtro: {len(rows)} de {len(data)} registros]" if conds else "") + "\n")
    print(f"{' / '.join(cols)} | {label} | registros")
    print("-" * 52)
    for k, val, n in res:
        print(f"{' / '.join(k)} | {fmt_num(val)} | {n}")
    tot = aggregate(rows, metric, op) if op in ("soma", "contagem") else None
    if tot is not None:
        print(f"\nTotal geral ({op}): {fmt_num(tot)}  ·  registros analisados: {fmt_num(len(rows))}")

def c_ranking(a):
    header, data = load(a.arquivo)
    col = resolve_col(header, a.por)
    metric = resolve_col(header, a.metrica)
    op = a.op or "soma"
    groups = defaultdict(list)
    for d in data:
        groups[str(d.get(col, "")).strip() or "(vazio)"].append(d)
    res = [(k, aggregate(v, metric, op)) for k, v in groups.items()]
    res = [r for r in res if r[1] is not None]
    res.sort(key=lambda x: x[1], reverse=True)
    total = sum(v for _, v in res) or 1.0
    print(f"🏆 Ranking por «{col}» — {op} de «{metric}» (total: {fmt_num(total)})\n")
    acc = 0.0
    for i, (k, v) in enumerate(res[:a.top], 1):
        acc += v
        print(f"{i:>2}. {k} — {fmt_num(v)} ({v/total*100:.1f}%)  | acumulado {acc/total*100:.1f}%")
    # concentração 80/20
    acc2, n80 = 0.0, 0
    for _, v in res:
        acc2 += v; n80 += 1
        if acc2 / total >= 0.8:
            break
    print(f"\n📌 Concentração: {n80} de {len(res)} ({n80/len(res)*100:.0f}%) "
          f"itens somam ~80% do total.")

def _bucket(d, period):
    if period == "dia":   return d.isoformat()
    if period == "mes":   return f"{d.year}-{d.month:02d}"
    if period == "semana":
        iso = d.isocalendar()
        return f"{iso[0]}-S{iso[1]:02d}"
    return d.isoformat()

def c_tendencia(a):
    header, data = load(a.arquivo)
    conds = [parse_cond(header, e) for e in (a.onde or [])]
    rows = apply_filters(data, conds)
    dcol = resolve_col(header, a.data)
    metric = resolve_col(header, a.metrica) if a.metrica else None
    op = a.op or ("soma" if metric else "contagem")
    groups = defaultdict(list)
    ignored = 0
    for d in rows:
        dt = parse_date(d.get(dcol, ""))
        if dt is None:
            ignored += 1; continue
        groups[_bucket(dt, a.periodo)].append(d)
    series = sorted((k, aggregate(v, metric, op), len(v)) for k, v in groups.items())
    if not series:
        print("Não consegui ler datas válidas nessa coluna."); return
    label = f"{op}" + (f" de {metric}" if metric else " (registros)")
    print(f"📈 Tendência por {a.periodo} — {label}\n")
    mx = max((s[1] or 0) for s in series) or 1
    for k, val, n in series:
        bar = "█" * int(round((val or 0) / mx * 30))
        print(f"{k} | {bar} {fmt_num(val)}")
    if ignored:
        print(f"\n(Atenção: {ignored} registros sem data válida foram ignorados.)")

def c_cruzar(a):
    header, data = load(a.arquivo)
    rcol = resolve_col(header, a.linhas)
    ccol = resolve_col(header, a.colunas)
    metric = resolve_col(header, a.metrica) if a.metrica else None
    op = a.op or ("soma" if metric else "contagem")
    cells = defaultdict(list)
    rkeys, ckeys = set(), set()
    for d in data:
        rk = str(d.get(rcol, "")).strip() or "(vazio)"
        ck = str(d.get(ccol, "")).strip() or "(vazio)"
        cells[(rk, ck)].append(d); rkeys.add(rk); ckeys.add(ck)
    rkeys = sorted(rkeys); ckeys = sorted(ckeys)
    label = f"{op}" + (f" de {metric}" if metric else "")
    print(f"🔀 Cruzamento — {label}: linhas={rcol}, colunas={ccol}\n")
    print(f"{rcol} \\ {ccol} | " + " | ".join(ckeys) + " | TOTAL")
    print("-" * (20 + 12 * len(ckeys)))
    for rk in rkeys:
        rowvals, rowtot = [], 0.0
        for ck in ckeys:
            v = aggregate(cells.get((rk, ck), []), metric, op) or 0
            rowvals.append(fmt_num(v)); rowtot += v
        print(f"{rk} | " + " | ".join(rowvals) + f" | {fmt_num(rowtot)}")

def c_resumo(a):
    header, data = load(a.arquivo)
    print(f"🔎 Resumo de {Path(a.arquivo).name} — {fmt_num(len(data))} registros, {len(header)} colunas\n")
    num_cols = [h for h in header if col_is_numeric(data, h)]
    cat_cols = [h for h in header if not col_is_numeric(data, h) and not col_is_date(data, h)]
    if num_cols:
        print("Números:")
        for h in num_cols:
            nums = [parse_num(d.get(h, "")) for d in data]
            nums = [n for n in nums if n is not None]
            if nums:
                print(f"  · {h}: soma {fmt_num(sum(nums))} · média {fmt_num(sum(nums)/len(nums))} "
                      f"· mín {fmt_num(min(nums))} · máx {fmt_num(max(nums))}")
    if cat_cols:
        print("\nCategorias (valor mais comum):")
        for h in cat_cols[:6]:
            cnt = Counter(str(d.get(h, "")).strip() for d in data if str(d.get(h, "")).strip())
            if cnt:
                top, n = cnt.most_common(1)[0]
                print(f"  · {h}: {len(cnt)} valores distintos · mais comum «{top}» ({n}x)")
    # alerta de qualidade
    falhas = []
    for h in header:
        vazios = sum(1 for d in data if not str(d.get(h, "")).strip())
        if data and vazios / len(data) > 0.2:
            falhas.append(f"{h} ({vazios} vazios)")
    if falhas:
        print("\n⚠️ Qualidade: colunas com muitos vazios → " + "; ".join(falhas))

# ----------------------------------------------------------------- cli

def main():
    p = argparse.ArgumentParser(description="Motor de análise de dados do Garimpo.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("perfil"); s.add_argument("arquivo"); s.set_defaults(fn=c_perfil)

    s = sub.add_parser("valores"); s.add_argument("arquivo")
    s.add_argument("--coluna", required=True); s.add_argument("--top", type=int, default=20)
    s.set_defaults(fn=c_valores)

    s = sub.add_parser("agrupar"); s.add_argument("arquivo")
    s.add_argument("--por", required=True); s.add_argument("--metrica")
    s.add_argument("--op", choices=["soma","media","contagem","min","max","distintos"])
    s.add_argument("--onde", action="append"); s.add_argument("--top", type=int)
    s.add_argument("--ordem", choices=["desc","asc"], default="desc")
    s.set_defaults(fn=c_agrupar)

    s = sub.add_parser("ranking"); s.add_argument("arquivo")
    s.add_argument("--por", required=True); s.add_argument("--metrica", required=True)
    s.add_argument("--op", choices=["soma","media","contagem","min","max"], default="soma")
    s.add_argument("--top", type=int, default=10); s.set_defaults(fn=c_ranking)

    s = sub.add_parser("tendencia"); s.add_argument("arquivo")
    s.add_argument("--data", required=True)
    s.add_argument("--periodo", choices=["dia","semana","mes"], default="mes")
    s.add_argument("--metrica"); s.add_argument("--op", choices=["soma","contagem","media","min","max"])
    s.add_argument("--onde", action="append"); s.set_defaults(fn=c_tendencia)

    s = sub.add_parser("cruzar"); s.add_argument("arquivo")
    s.add_argument("--linhas", required=True); s.add_argument("--colunas", required=True)
    s.add_argument("--metrica"); s.add_argument("--op", choices=["soma","contagem","media","min","max"])
    s.set_defaults(fn=c_cruzar)

    s = sub.add_parser("resumo"); s.add_argument("arquivo"); s.set_defaults(fn=c_resumo)

    a = p.parse_args()
    a.fn(a)

if __name__ == "__main__":
    main()
