#!/usr/bin/env python3
"""
Engrenagem — motor de diagnostico e priorizacao de automacoes.

Somente biblioteca padrao do Python (nada de instalar nada).
Le e escreve em ./.engrenagem/ na raiz do projeto do usuario.

Comandos:
  add        Adiciona um processo repetitivo ao mapa.
  listar     Mostra todos os processos cadastrados.
  priorizar  Pontua cada processo (impacto x esforco) e ordena, escreve roteiro.md.
  roi        Calcula horas e R$ economizados por mes/ano.
  status     Muda o status de um processo (a_fazer / fazendo / automatizado).

O usuario NUNCA precisa decorar isto — quem conversa e o Claude, que chama
estes comandos por baixo dos panos. Este arquivo so existe para fazer a conta
sempre igual e nunca inventar numero.
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

DATA_DIR = Path(os.environ.get("ENGRENAGEM_DIR") or (Path.cwd() / ".engrenagem"))
PROCESSOS = DATA_DIR / "processos.csv"
CONFIG = DATA_DIR / "config.md"
ROTEIRO = DATA_DIR / "roteiro.md"

CAMPOS = [
    "processo", "frequencia", "vezes_mes", "minutos",
    "quem", "ferramenta_atual", "dor", "esforco", "status",
]
STATUS_VALIDOS = ("a_fazer", "fazendo", "automatizado")
QUADRANTE_ORDEM = ["Ganho Rapido", "Projeto", "Talvez", "Evite"]


# ----------------------------------------------------------------------------- util
def garantir_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ler_processos():
    if not PROCESSOS.exists():
        return []
    with PROCESSOS.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    for r in linhas:
        for c in CAMPOS:
            r.setdefault(c, "")
    return linhas


def escrever_processos(linhas):
    garantir_dir()
    with PROCESSOS.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for r in linhas:
            w.writerow({c: r.get(c, "") for c in CAMPOS})


def num(v, padrao=0.0):
    try:
        return float(str(v).replace(",", ".").strip())
    except (ValueError, AttributeError):
        return padrao


def custo_hora_do_config(override=None):
    if override is not None:
        return float(override)
    if CONFIG.exists():
        txt = CONFIG.read_text(encoding="utf-8")
        m = re.search(r"custo_hora\s*[:=]\s*R?\$?\s*([\d.,]+)", txt, re.IGNORECASE)
        if m:
            return num(m.group(1), 50.0)
    return None


def moeda(v):
    s = f"{v:,.0f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


# ------------------------------------------------------------------------- scoring
def calcular(r):
    """Devolve (minutos_mes, impacto, esforco, score, quadrante)."""
    vezes = num(r.get("vezes_mes"))
    minutos = num(r.get("minutos"))
    dor = max(1.0, min(3.0, num(r.get("dor"), 1)))
    esforco = max(1.0, min(5.0, num(r.get("esforco"), 3)))

    minutos_mes = vezes * minutos
    horas_mes = minutos_mes / 60.0
    # Impacto = tempo gasto por mes ponderado pela dor (chatice/erro).
    impacto = horas_mes * dor
    # Score = retorno por unidade de esforco. Quanto maior, mais cedo fazer.
    score = impacto / esforco if esforco else impacto

    alto_impacto = impacto >= 4.0          # ~4h/mes ponderadas
    baixo_esforco = esforco <= 2.5
    if alto_impacto and baixo_esforco:
        quad = "Ganho Rapido"
    elif alto_impacto and not baixo_esforco:
        quad = "Projeto"
    elif not alto_impacto and baixo_esforco:
        quad = "Talvez"
    else:
        quad = "Evite"
    return minutos_mes, impacto, esforco, score, quad


# -------------------------------------------------------------------------- add
def cmd_add(a):
    linhas = ler_processos()
    novo = {
        "processo": a.processo.strip(),
        "frequencia": (a.frequencia or "").strip(),
        "vezes_mes": str(a.vezes_mes),
        "minutos": str(a.minutos),
        "quem": (a.quem or "").strip(),
        "ferramenta_atual": (a.ferramenta or "").strip(),
        "dor": str(a.dor),
        "esforco": str(a.esforco),
        "status": "a_fazer",
    }
    # evita duplicar pelo nome
    linhas = [r for r in linhas if r.get("processo", "").lower() != novo["processo"].lower()]
    linhas.append(novo)
    escrever_processos(linhas)
    print(f"[engrenagem] processo registrado: {novo['processo']}")
    print(f"[engrenagem] total no mapa: {len(linhas)}")


# -------------------------------------------------------------------------- listar
def cmd_listar(_a):
    linhas = ler_processos()
    if not linhas:
        print("[engrenagem] nenhum processo no mapa ainda. Use o modo Mapear.")
        return
    _tabela(linhas)


def _tabela(linhas):
    enriquecidas = []
    for r in linhas:
        _, impacto, esforco, score, quad = calcular(r)
        enriquecidas.append((score, impacto, esforco, quad, r))
    enriquecidas.sort(key=lambda x: x[0], reverse=True)

    print()
    print(f"  {'#':>2}  {'PROCESSO':<34} {'h/mes':>6} {'DOR':>3} {'ESF':>3} {'SCORE':>6}  {'QUADRANTE':<12} STATUS")
    print("  " + "-" * 92)
    for i, (score, impacto, esforco, quad, r) in enumerate(enriquecidas, 1):
        minutos_mes = num(r.get("vezes_mes")) * num(r.get("minutos"))
        nome = r.get("processo", "")[:34]
        print(f"  {i:>2}  {nome:<34} {minutos_mes/60:>6.1f} "
              f"{int(num(r.get('dor'),1)):>3} {int(num(r.get('esforco'),3)):>3} "
              f"{score:>6.1f}  {quad:<12} {r.get('status','a_fazer')}")
    print()
    return enriquecidas


# -------------------------------------------------------------------------- priorizar
def cmd_priorizar(_a):
    linhas = ler_processos()
    if not linhas:
        print("[engrenagem] nenhum processo no mapa ainda. Use o modo Mapear primeiro.")
        return
    enriquecidas = _tabela(linhas)

    # roteiro.md
    garantir_dir()
    grupos = {q: [] for q in QUADRANTE_ORDEM}
    for score, impacto, esforco, quad, r in enriquecidas:
        grupos[quad].append((score, impacto, r))

    legendas = {
        "Ganho Rapido": "Comece por aqui — muito tempo ganho, pouco esforco.",
        "Projeto": "Vale muito, mas da trabalho — planeje como projeto.",
        "Talvez": "Facil, porem ganho pequeno — faca nas folgas.",
        "Evite": "Pouco ganho e muito esforco — deixe por ultimo (ou nem faca).",
    }
    out = ["# Roteiro de Automacao\n",
           "_Gerado pela Engrenagem. Ordene de cima para baixo._\n"]
    for q in QUADRANTE_ORDEM:
        itens = grupos[q]
        if not itens:
            continue
        out.append(f"\n## {q}\n_{legendas[q]}_\n")
        for score, impacto, r in itens:
            mm = num(r.get("vezes_mes")) * num(r.get("minutos")) / 60
            out.append(f"- **{r.get('processo','')}** — "
                       f"~{mm:.1f}h/mes hoje · dor {int(num(r.get('dor'),1))}/3 · "
                       f"esforco {int(num(r.get('esforco'),3))}/5 · "
                       f"score {score:.1f} · status: {r.get('status','a_fazer')}")
    ROTEIRO.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[engrenagem] roteiro salvo em {ROTEIRO}")
    print("[engrenagem] dica: ataque o topo de 'Ganho Rapido' primeiro.")


# -------------------------------------------------------------------------- roi
def cmd_roi(a):
    linhas = ler_processos()
    if not linhas:
        print("[engrenagem] nenhum processo no mapa ainda.")
        return
    ch = custo_hora_do_config(a.custo_hora)
    if ch is None:
        ch = 50.0
        print("[engrenagem] aviso: custo_hora nao encontrado no config — usando R$ 50/h. "
              "Passe --custo-hora N para ajustar.")

    pot_h = real_h = 0.0
    for r in linhas:
        minutos_mes, *_ = calcular(r)
        h = minutos_mes / 60.0
        if r.get("status") == "automatizado":
            real_h += h
        else:
            pot_h += h

    print()
    print(f"  custo-hora usado: {moeda(ch)}/h")
    print("  " + "-" * 52)
    print(f"  Ja automatizado .... {real_h:>7.1f} h/mes  =  {moeda(real_h*ch)}/mes")
    print(f"  Ainda a ganhar ..... {pot_h:>7.1f} h/mes  =  {moeda(pot_h*ch)}/mes")
    print("  " + "-" * 52)
    total_h = pot_h + real_h
    print(f"  Potencial TOTAL .... {total_h:>7.1f} h/mes  =  {moeda(total_h*ch)}/mes")
    print(f"  Por ano ............ {total_h*12:>7.0f} h/ano  =  {moeda(total_h*ch*12)}/ano")
    print()
    if pot_h > 0:
        dias = pot_h / 8.0
        print(f"  Traducao: automatizar o que falta devolve ~{dias:.1f} dias de trabalho por mes.")
    print()


# -------------------------------------------------------------------------- status
def cmd_status(a):
    linhas = ler_processos()
    alvo = a.processo.strip().lower()
    novo = a.novo.strip().lower()
    if novo not in STATUS_VALIDOS:
        print(f"[engrenagem] status invalido. Use um de: {', '.join(STATUS_VALIDOS)}")
        sys.exit(1)
    achou = False
    for r in linhas:
        if r.get("processo", "").lower() == alvo:
            r["status"] = novo
            achou = True
    if not achou:
        print(f"[engrenagem] processo nao encontrado: {a.processo}")
        sys.exit(1)
    escrever_processos(linhas)
    print(f"[engrenagem] '{a.processo}' agora esta: {novo}")


# -------------------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description="Engrenagem — motor de automacao")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add")
    pa.add_argument("--processo", required=True)
    pa.add_argument("--frequencia", default="")
    pa.add_argument("--vezes-mes", dest="vezes_mes", type=float, required=True)
    pa.add_argument("--minutos", type=float, required=True)
    pa.add_argument("--quem", default="")
    pa.add_argument("--ferramenta", default="")
    pa.add_argument("--dor", type=int, default=1)
    pa.add_argument("--esforco", type=int, default=3)
    pa.set_defaults(func=cmd_add)

    sub.add_parser("listar").set_defaults(func=cmd_listar)
    sub.add_parser("priorizar").set_defaults(func=cmd_priorizar)

    pr = sub.add_parser("roi")
    pr.add_argument("--custo-hora", dest="custo_hora", type=float, default=None)
    pr.set_defaults(func=cmd_roi)

    ps = sub.add_parser("status")
    ps.add_argument("--processo", required=True)
    ps.add_argument("--novo", required=True)
    ps.set_defaults(func=cmd_status)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
