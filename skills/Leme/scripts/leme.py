#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leme — motor do sistema pessoal de tarefas do dono de negócio.

Captura as tarefas do dia a dia, calcula uma prioridade EXPLICÁVEL (dá para
mostrar por que cada tarefa subiu na fila), escolhe as 3 mais importantes de
hoje e conduz a revisão da semana. Usa SOMENTE a biblioteca padrão do Python.
Nunca inventa nada: tudo que sai daqui veio das tarefas que o dono registrou.

Arquivo de dados (.leme/tarefas.csv), com cabeçalho:
    id,descricao,criada_em,vence_em,urgente,importante,projeto,bloqueada,status,concluida_em
    1,Enviar proposta pro João,2026-06-15,2026-06-18,sim,sim,Comercial,nao,aberta,
    2,Pagar o contador,2026-06-10,2026-06-20,sim,nao,Financeiro,nao,aberta,

  - id: número sequencial (o motor cuida)
  - descricao: o que precisa ser feito
  - criada_em / vence_em / concluida_em: YYYY-MM-DD (vence_em e concluida_em podem ser vazios)
  - urgente / importante / bloqueada: "sim" ou "nao"
  - projeto: rótulo opcional (ex.: Comercial, Pessoal, Financeiro)
  - status: "aberta" ou "concluida"

Comandos:
    python3 leme.py capturar --desc "..." [--vence DD/MM] [--urgente] [--importante] [--projeto X] [--bloqueada]
    python3 leme.py hoje                       # as 3 tarefas mais importantes de hoje + o resto
    python3 leme.py priorizar                  # fila inteira ranqueada, com o porquê de cada nota
    python3 leme.py listar [--projeto X] [--status aberta|concluida|todas]
    python3 leme.py concluir --id N            # marca como feita
    python3 leme.py reabrir --id N             # volta para aberta
    python3 leme.py adiar --id N --vence DD/MM # muda o prazo
    python3 leme.py editar --id N [--desc ...] [--urgente sim|nao] [--importante sim|nao] [--bloqueada sim|nao] [--projeto X]
    python3 leme.py remover --id N
    python3 leme.py revisar                    # revisão da semana (4 quadros)
Opções globais: --arquivo <csv>  (padrão: .leme/tarefas.csv)
                --formato json   (padrão: texto)
"""

import argparse
import csv
import json
import os
import sys
import unicodedata
from datetime import date, datetime, timedelta

ARQUIVO_PADRAO = os.path.join(".leme", "tarefas.csv")
CABECALHO = ["id", "descricao", "criada_em", "vence_em", "urgente",
             "importante", "projeto", "bloqueada", "status", "concluida_em"]

# Pesos da prioridade (somatório aditivo e explicável — inspirado no urgency
# score do Taskwarrior, mas em PT-BR e com perguntas simples no lugar de tags).
PESOS = {
    "vence": 12.0,        # prazo chegando / vencido
    "importante": 9.0,    # marcada como importante
    "urgente": 7.0,       # marcada como urgente
    "idade": 2.0,         # tempo parada na fila (não deixa nada cair no esquecimento)
    "projeto": 1.0,       # ter um projeto/área associado
    "bloqueada": -8.0,    # esperando algo/alguém — desce na fila de hoje
}
IDADE_MAX_DIAS = 90       # idade satura em ~3 meses
PARADA_DIAS = 14          # aberta há mais de 14 dias sem prazo = "parada"


# ---------------------------------------------------------------- utilidades

def _norm(s):
    """minúsculas e sem acento, para comparação tolerante."""
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _sim(v):
    return _norm(v) in ("sim", "s", "1", "true", "x")


def parse_data(bruto, hoje=None):
    """Aceita YYYY-MM-DD, DD/MM/YYYY ou DD/MM (ano atual). None se vazio/inválido."""
    s = (bruto or "").strip()
    if not s:
        return None
    hoje = hoje or date.today()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    # DD/MM sem ano → assume ano corrente
    try:
        d, m = s.split("/")[:2]
        return date(hoje.year, int(m), int(d))
    except (ValueError, IndexError):
        return None


def fmt_data(d):
    return d.strftime("%d/%m/%Y") if d else ""


def iso(d):
    return d.strftime("%Y-%m-%d") if d else ""


# ---------------------------------------------------------------- persistência

def carregar(arquivo):
    if not os.path.exists(arquivo):
        return []
    tarefas = []
    with open(arquivo, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if not (row.get("descricao") or "").strip():
                continue
            tarefas.append(row)
    return tarefas


def salvar(arquivo, tarefas):
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    with open(arquivo, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO)
        w.writeheader()
        for t in tarefas:
            w.writerow({k: t.get(k, "") for k in CABECALHO})


def proximo_id(tarefas):
    ids = [int(t["id"]) for t in tarefas if str(t.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


# ---------------------------------------------------------------- prioridade

def quadrante(t):
    """Matriz de Eisenhower a partir de duas perguntas simples."""
    u, i = _sim(t.get("urgente")), _sim(t.get("importante"))
    if u and i:
        return "Faça agora"
    if i and not u:
        return "Agende"
    if u and not i:
        return "Delegue"
    return "Avalie/elimine"


def _fator_vence(t, hoje):
    d = parse_data(t.get("vence_em"), hoje)
    if not d:
        return 0.0
    atraso = (hoje - d).days          # positivo = vencida
    if atraso >= 7:
        return 1.0
    if atraso <= -14:                 # mais de 2 semanas no futuro
        return 0.2
    return ((atraso + 14) * 0.8 / 21) + 0.2


def _fator_idade(t, hoje):
    d = parse_data(t.get("criada_em"), hoje)
    if not d:
        return 0.0
    return min(max((hoje - d).days, 0) / IDADE_MAX_DIAS, 1.0)


def prioridade(t, hoje=None):
    """Devolve (nota, detalhamento) — detalhamento explica de onde veio cada ponto."""
    hoje = hoje or date.today()
    fatores = {
        "vence": _fator_vence(t, hoje),
        "importante": 1.0 if _sim(t.get("importante")) else 0.0,
        "urgente": 1.0 if _sim(t.get("urgente")) else 0.0,
        "idade": _fator_idade(t, hoje),
        "projeto": 1.0 if (t.get("projeto") or "").strip() else 0.0,
        "bloqueada": 1.0 if _sim(t.get("bloqueada")) else 0.0,
    }
    detalhe = {}
    nota = 0.0
    for k, f in fatores.items():
        pts = round(PESOS[k] * f, 1)
        if pts:
            detalhe[k] = pts
        nota += pts
    return round(nota, 1), detalhe


def explica(detalhe):
    """Transforma o detalhamento em motivos legíveis em PT-BR."""
    rotulos = {
        "vence": "prazo chegando",
        "importante": "marcada como importante",
        "urgente": "marcada como urgente",
        "idade": "está parada há um tempo",
        "projeto": "tem projeto associado",
        "bloqueada": "está bloqueada (esperando algo)",
    }
    partes = []
    for k, pts in sorted(detalhe.items(), key=lambda kv: -abs(kv[1])):
        sinal = "+" if pts >= 0 else ""
        partes.append(f"{rotulos[k]} ({sinal}{pts})")
    return ", ".join(partes)


# ---------------------------------------------------------------- saída

def _dump(payload, formato):
    if formato == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return True
    return False


def linha_tarefa(t, hoje, mostrar_motivo=False):
    nota, detalhe = prioridade(t, hoje)
    venc = parse_data(t.get("vence_em"), hoje)
    selo = ""
    if venc:
        atraso = (hoje - venc).days
        if atraso > 0:
            selo = f"  ⚠ vencida há {atraso}d"
        elif atraso == 0:
            selo = "  ⏰ vence HOJE"
        else:
            selo = f"  · vence {fmt_data(venc)}"
    bloq = "  🔒 bloqueada" if _sim(t.get("bloqueada")) else ""
    proj = f"  [{t['projeto']}]" if (t.get("projeto") or "").strip() else ""
    base = f"  #{t['id']} ({nota:>5.1f}) {t['descricao']}{proj}{selo}{bloq}"
    if mostrar_motivo and detalhe:
        base += f"\n        por quê: {explica(detalhe)}"
    return base


# ---------------------------------------------------------------- comandos

def cmd_capturar(args, tarefas, arquivo):
    hoje = date.today()
    nova = {
        "id": str(proximo_id(tarefas)),
        "descricao": args.desc.strip(),
        "criada_em": iso(hoje),
        "vence_em": iso(parse_data(args.vence, hoje)),
        "urgente": "sim" if args.urgente else "nao",
        "importante": "sim" if args.importante else "nao",
        "projeto": (args.projeto or "").strip(),
        "bloqueada": "sim" if args.bloqueada else "nao",
        "status": "aberta",
        "concluida_em": "",
    }
    tarefas.append(nova)
    salvar(arquivo, tarefas)
    nota, detalhe = prioridade(nova, hoje)
    if _dump({"criada": nova, "nota": nota, "quadrante": quadrante(nova)}, args.formato):
        return
    print(f"✓ Tarefa #{nova['id']} registrada — quadrante: {quadrante(nova)} · prioridade {nota}")
    if detalhe:
        print(f"  por quê: {explica(detalhe)}")


def cmd_hoje(args, tarefas, arquivo):
    hoje = date.today()
    abertas = [t for t in tarefas if _norm(t.get("status")) != "concluida"]
    livres = [t for t in abertas if not _sim(t.get("bloqueada"))]
    livres.sort(key=lambda t: prioridade(t, hoje)[0], reverse=True)
    top3, resto = livres[:3], livres[3:]
    bloqueadas = [t for t in abertas if _sim(t.get("bloqueada"))]
    if _dump({
        "top3": [{"id": t["id"], "descricao": t["descricao"],
                  "nota": prioridade(t, hoje)[0], "motivos": explica(prioridade(t, hoje)[1])}
                 for t in top3],
        "depois": [t["id"] for t in resto],
        "bloqueadas": [t["id"] for t in bloqueadas],
    }, args.formato):
        return
    if not abertas:
        print("Nada na fila. Quer capturar a primeira tarefa? Use o modo Capturar.")
        return
    print("🎯 AS 3 DE HOJE (faça estas primeiro):\n")
    if top3:
        for t in top3:
            print(linha_tarefa(t, hoje, mostrar_motivo=True))
    else:
        print("  (todas as tarefas abertas estão bloqueadas — veja abaixo)")
    if resto:
        print(f"\n📋 Depois ({len(resto)}):")
        for t in resto:
            print(linha_tarefa(t, hoje))
    if bloqueadas:
        print(f"\n🔒 Bloqueadas — esperando algo/alguém ({len(bloqueadas)}):")
        for t in bloqueadas:
            print(linha_tarefa(t, hoje))


def cmd_priorizar(args, tarefas, arquivo):
    hoje = date.today()
    abertas = [t for t in tarefas if _norm(t.get("status")) != "concluida"]
    abertas.sort(key=lambda t: prioridade(t, hoje)[0], reverse=True)
    if _dump([{"id": t["id"], "descricao": t["descricao"],
               "nota": prioridade(t, hoje)[0],
               "quadrante": quadrante(t),
               "motivos": explica(prioridade(t, hoje)[1])} for t in abertas], args.formato):
        return
    if not abertas:
        print("Nenhuma tarefa aberta.")
        return
    print(f"Fila priorizada ({len(abertas)} tarefas abertas) — maior nota primeiro:\n")
    for t in abertas:
        print(linha_tarefa(t, hoje, mostrar_motivo=True))


def cmd_listar(args, tarefas, arquivo):
    hoje = date.today()
    alvo = args.status or "aberta"
    sel = tarefas
    if alvo != "todas":
        sel = [t for t in sel if _norm(t.get("status")) == _norm(alvo)
               or (alvo == "aberta" and _norm(t.get("status")) != "concluida")]
    if args.projeto:
        sel = [t for t in sel if _norm(t.get("projeto")) == _norm(args.projeto)]
    sel.sort(key=lambda t: prioridade(t, hoje)[0], reverse=True)
    if _dump([{k: t.get(k, "") for k in CABECALHO} for t in sel], args.formato):
        return
    if not sel:
        print("Nenhuma tarefa com esse filtro.")
        return
    for t in sel:
        marca = "✓" if _norm(t.get("status")) == "concluida" else " "
        print(f"[{marca}]" + linha_tarefa(t, hoje))


def _achar(tarefas, tid):
    for t in tarefas:
        if str(t.get("id")) == str(tid):
            return t
    return None


def cmd_concluir(args, tarefas, arquivo):
    t = _achar(tarefas, args.id)
    if not t:
        print(f"Não achei a tarefa #{args.id}.")
        return
    t["status"] = "concluida"
    t["concluida_em"] = iso(date.today())
    salvar(arquivo, tarefas)
    if _dump({"concluida": t}, args.formato):
        return
    print(f"✓ Feito! Tarefa #{t['id']} — \"{t['descricao']}\" concluída.")


def cmd_reabrir(args, tarefas, arquivo):
    t = _achar(tarefas, args.id)
    if not t:
        print(f"Não achei a tarefa #{args.id}.")
        return
    t["status"] = "aberta"
    t["concluida_em"] = ""
    salvar(arquivo, tarefas)
    if _dump({"reaberta": t}, args.formato):
        return
    print(f"↺ Tarefa #{t['id']} voltou para aberta.")


def cmd_adiar(args, tarefas, arquivo):
    t = _achar(tarefas, args.id)
    if not t:
        print(f"Não achei a tarefa #{args.id}.")
        return
    nova = parse_data(args.vence, date.today())
    if not nova:
        print("Data inválida. Use DD/MM ou DD/MM/AAAA.")
        return
    t["vence_em"] = iso(nova)
    salvar(arquivo, tarefas)
    if _dump({"adiada": t}, args.formato):
        return
    print(f"📅 Tarefa #{t['id']} agora vence em {fmt_data(nova)}.")


def cmd_editar(args, tarefas, arquivo):
    t = _achar(tarefas, args.id)
    if not t:
        print(f"Não achei a tarefa #{args.id}.")
        return
    if args.desc is not None:
        t["descricao"] = args.desc.strip()
    for campo in ("urgente", "importante", "bloqueada"):
        val = getattr(args, campo)
        if val is not None:
            t[campo] = "sim" if _sim(val) else "nao"
    if args.projeto is not None:
        t["projeto"] = args.projeto.strip()
    if args.vence is not None:
        t["vence_em"] = iso(parse_data(args.vence, date.today()))
    salvar(arquivo, tarefas)
    if _dump({"editada": t}, args.formato):
        return
    print(f"✓ Tarefa #{t['id']} atualizada.")


def cmd_remover(args, tarefas, arquivo):
    t = _achar(tarefas, args.id)
    if not t:
        print(f"Não achei a tarefa #{args.id}.")
        return
    tarefas.remove(t)
    salvar(arquivo, tarefas)
    if _dump({"removida": args.id}, args.formato):
        return
    print(f"🗑  Tarefa #{args.id} removida.")


def cmd_revisar(args, tarefas, arquivo):
    hoje = date.today()
    limite_semana = hoje - timedelta(days=7)

    concluidas = []
    atrasadas = []
    paradas = []
    sem_data = []
    for t in tarefas:
        st = _norm(t.get("status"))
        if st == "concluida":
            cd = parse_data(t.get("concluida_em"), hoje)
            if cd and cd >= limite_semana:
                concluidas.append(t)
            continue
        venc = parse_data(t.get("vence_em"), hoje)
        criada = parse_data(t.get("criada_em"), hoje)
        if venc and venc < hoje:
            atrasadas.append(t)
        elif not venc:
            sem_data.append(t)
            if criada and (hoje - criada).days > PARADA_DIAS:
                paradas.append(t)
        elif criada and (hoje - criada).days > PARADA_DIAS:
            paradas.append(t)

    if _dump({
        "concluidas_semana": [t["id"] for t in concluidas],
        "atrasadas": [t["id"] for t in atrasadas],
        "paradas": [t["id"] for t in paradas],
        "sem_data": [t["id"] for t in sem_data],
    }, args.formato):
        return

    print("🧭 REVISÃO DA SEMANA\n")
    print(f"✅ Concluídas nos últimos 7 dias: {len(concluidas)}")
    for t in concluidas:
        print(f"   ✓ #{t['id']} {t['descricao']}")
    print(f"\n⚠️  Atrasadas (prazo já passou) — {len(atrasadas)}:")
    for t in atrasadas:
        print(linha_tarefa(t, hoje))
    print(f"\n🐢 Paradas há mais de {PARADA_DIAS} dias — decidir: fazer, agendar, delegar ou eliminar? ({len(paradas)})")
    for t in paradas:
        print(linha_tarefa(t, hoje))
    print(f"\n📭 Sem data definida — quando cada uma acontece? ({len(sem_data)}):")
    for t in sem_data:
        print(linha_tarefa(t, hoje))
    print("\n👉 Para fechar a revisão: escolha as 3 tarefas-chave da próxima semana "
          "e marque-as como importantes.")


# ---------------------------------------------------------------- CLI

def build_parser():
    # Opções globais aceitas ANTES ou DEPOIS do comando (--arquivo / --formato).
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("--arquivo", default=ARQUIVO_PADRAO)
    comum.add_argument("--formato", choices=["texto", "json"], default="texto")

    p = argparse.ArgumentParser(description="Leme — sistema pessoal de tarefas do dono.",
                                parents=[comum])
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(nome):
        return sub.add_parser(nome, parents=[comum])

    c = add("capturar")
    c.add_argument("--desc", required=True)
    c.add_argument("--vence")
    c.add_argument("--urgente", action="store_true")
    c.add_argument("--importante", action="store_true")
    c.add_argument("--bloqueada", action="store_true")
    c.add_argument("--projeto")

    add("hoje")
    add("priorizar")
    add("revisar")

    l = add("listar")
    l.add_argument("--projeto")
    l.add_argument("--status", choices=["aberta", "concluida", "todas"])

    for nome in ("concluir", "reabrir", "remover"):
        s = add(nome)
        s.add_argument("--id", required=True)

    a = add("adiar")
    a.add_argument("--id", required=True)
    a.add_argument("--vence", required=True)

    e = add("editar")
    e.add_argument("--id", required=True)
    e.add_argument("--desc")
    e.add_argument("--urgente")
    e.add_argument("--importante")
    e.add_argument("--bloqueada")
    e.add_argument("--projeto")
    e.add_argument("--vence")
    return p


DISPATCH = {
    "capturar": cmd_capturar, "hoje": cmd_hoje, "priorizar": cmd_priorizar,
    "listar": cmd_listar, "concluir": cmd_concluir, "reabrir": cmd_reabrir,
    "adiar": cmd_adiar, "editar": cmd_editar, "remover": cmd_remover,
    "revisar": cmd_revisar,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    tarefas = carregar(args.arquivo)
    DISPATCH[args.cmd](args, tarefas, args.arquivo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
