#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Planta — motor do escritório de projetos de automação para clientes.

Para o IMPLEMENTADOR (agência/consultor/freelancer de IA): guarda cada projeto
de cliente, soma o esforço do escopo, calcula prazo e ROI, e acompanha o
checklist de build/teste/entrega. Usa SOMENTE a biblioteca padrão do Python.
Nunca inventa nada: tudo que sai daqui veio do que você registrou ou de uma
conta feita aqui. A Planta organiza e calcula; o desenho da solução e a conversa
com o cliente são feitos pela skill (a IA), não pelo motor.

Cada projeto é um arquivo JSON em .planta/projetos/<slug>.json com:
    slug, cliente, setor, criado_em,
    output       -> o resultado concreto que o cliente quer (ex.: "responder lead em 30 min")
    metrica      -> o número a mover (ex.: "de 4h para 30 min")
    escopo[]     -> {id, titulo, horas, fase, tipo(dentro|fora), complexidade(simples|moderado|complexo)}
    tarefas[]    -> {id, titulo, etapa(build|teste|handoff), status(aberto|feito)}
    notas        -> texto livre

Comandos:
    python3 planta.py novo --cliente "Clínica X" [--setor "saúde"]
        [--output "..."] [--metrica "..."]
    python3 planta.py listar
    python3 planta.py info --proj <slug> [--output "..."] [--metrica "..."]
        [--setor "..."]                       # edita campos do projeto
    python3 planta.py escopo-add --proj <slug> --titulo "..." --horas 6
        [--fase 1] [--tipo dentro|fora] [--complex simples|moderado|complexo]
    python3 planta.py escopo --proj <slug>     # lista o escopo + soma horas + prazo + mix
    python3 planta.py escopo-rm --proj <slug> --id N
    python3 planta.py prazo --proj <slug> [--capacidade-semana 10]
    python3 planta.py roi --proj <slug> --horas-mes 20 --custo-hora-cliente "R$ 60"
        [--seu-custo-hora "R$ 150"] [--recorrencia "R$ 800"]
    python3 planta.py tarefa-add --proj <slug> --titulo "..." [--etapa build|teste|handoff]
    python3 planta.py tarefas --proj <slug> [--etapa build|teste|handoff]
    python3 planta.py concluir --proj <slug> --id N
    python3 planta.py reabrir --proj <slug> --id N
    python3 planta.py resumo --proj <slug>
Opções globais:
    --pasta <dir>     (padrão: .planta)
    --formato json    (padrão: texto)
"""

import argparse
import json
import math
import os
import re
import sys
import unicodedata
from datetime import date

PASTA_PADRAO = ".planta"
ETAPAS_TAREFA = ["build", "teste", "handoff"]
NOME_ETAPA = {"build": "Construção", "teste": "Teste real", "handoff": "Entrega / treinamento"}
COMPLEX = ["simples", "moderado", "complexo"]
CAPACIDADE_PADRAO = 10.0  # horas por semana dedicadas ao projeto (estimativa de prazo)


# ----------------------------------------------------------------- utilidades

def _norm(s):
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def slugify(texto):
    base = _norm(texto)
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or "projeto"


def parse_dinheiro(bruto):
    """Aceita 'R$ 1.234,56', '1.234,56', '1234.56', '1500', 1500 -> float ou None."""
    if bruto is None:
        return None
    if isinstance(bruto, (int, float)):
        return float(bruto)
    s = str(bruto).strip()
    if not s:
        return None
    s = s.replace("R$", "").replace("r$", "").strip()
    s = re.sub(r"\s", "", s)
    if "," in s and "." in s:          # 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                       # 1234,56 -> 1234.56
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_horas(bruto):
    if bruto is None:
        return None
    s = str(bruto).strip().lower().replace("h", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def brl(v):
    if v is None:
        return "—"
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def hoje_iso():
    return date.today().isoformat()


# -------------------------------------------------------------- armazenamento

def dir_projetos(pasta):
    return os.path.join(pasta, "projetos")


def caminho_projeto(pasta, slug):
    return os.path.join(dir_projetos(pasta), slug + ".json")


def carregar(pasta, slug):
    cam = caminho_projeto(pasta, slug)
    if not os.path.exists(cam):
        return None
    with open(cam, encoding="utf-8") as f:
        return json.load(f)


def salvar(pasta, proj):
    os.makedirs(dir_projetos(pasta), exist_ok=True)
    cam = caminho_projeto(pasta, proj["slug"])
    with open(cam, "w", encoding="utf-8") as f:
        json.dump(proj, f, ensure_ascii=False, indent=2)


def todos_projetos(pasta):
    d = dir_projetos(pasta)
    if not os.path.isdir(d):
        return []
    out = []
    for nome in sorted(os.listdir(d)):
        if nome.endswith(".json"):
            with open(os.path.join(d, nome), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def _proximo_id(itens):
    return (max((it["id"] for it in itens), default=0)) + 1


def _erro(msg):
    print("ERRO: " + msg, file=sys.stderr)
    sys.exit(1)


def _exige(pasta, slug):
    proj = carregar(pasta, slug)
    if proj is None:
        _erro(f"projeto '{slug}' não encontrado em {dir_projetos(pasta)}. "
              f"Rode 'listar' para ver os projetos ou 'novo' para criar.")
    return proj


# ----------------------------------------------------------------- comandos

def cmd_novo(a):
    slug = slugify(a.cliente)
    pasta = a.pasta
    # evita sobrescrever: se já existe, acrescenta sufixo
    base, n = slug, 2
    while carregar(pasta, slug) is not None:
        slug = f"{base}-{n}"
        n += 1
    proj = {
        "slug": slug,
        "cliente": a.cliente.strip(),
        "setor": (a.setor or "").strip(),
        "criado_em": hoje_iso(),
        "output": (a.output or "").strip(),
        "metrica": (a.metrica or "").strip(),
        "escopo": [],
        "tarefas": [],
        "notas": "",
    }
    salvar(pasta, proj)
    if a.formato == "json":
        print(json.dumps(proj, ensure_ascii=False))
    else:
        print(f"✔ Projeto criado: {proj['cliente']}  (slug: {slug})")
        print(f"  Arquivo: {caminho_projeto(pasta, slug)}")
        if not proj["output"]:
            print("  Próximo passo: defina o OUTPUT e a MÉTRICA (modo Briefing/Mapear).")
    return proj


def cmd_info(a):
    proj = _exige(a.pasta, a.proj)
    for campo in ("setor", "output", "metrica"):
        val = getattr(a, campo, None)
        if val is not None:
            proj[campo] = val.strip()
    salvar(a.pasta, proj)
    if a.formato == "json":
        print(json.dumps(proj, ensure_ascii=False))
    else:
        print(f"Projeto: {proj['cliente']}  (slug: {proj['slug']})")
        print(f"  Setor:   {proj['setor'] or '—'}")
        print(f"  Output:  {proj['output'] or '—'}")
        print(f"  Métrica: {proj['metrica'] or '—'}")


def cmd_listar(a):
    projs = todos_projetos(a.pasta)
    if a.formato == "json":
        print(json.dumps(projs, ensure_ascii=False))
        return
    if not projs:
        print("Nenhum projeto ainda. Crie o primeiro com: planta.py novo --cliente \"...\"")
        return
    print(f"{len(projs)} projeto(s):\n")
    for p in projs:
        dentro = sum(i["horas"] for i in p["escopo"] if i["tipo"] == "dentro")
        tarefas = p["tarefas"]
        feitas = sum(1 for t in tarefas if t["status"] == "feito")
        pct = f"{round(100*feitas/len(tarefas))}%" if tarefas else "—"
        print(f"• {p['cliente']}  (slug: {p['slug']})")
        print(f"    setor: {p['setor'] or '—'} | escopo: {dentro:g}h | "
              f"entrega: {feitas}/{len(tarefas)} ({pct})")


def cmd_escopo_add(a):
    proj = _exige(a.pasta, a.proj)
    horas = parse_horas(a.horas)
    if horas is None or horas < 0:
        _erro("--horas inválido (ex.: 6, 6.5, '4h').")
    tipo = (a.tipo or "dentro").lower()
    if tipo not in ("dentro", "fora"):
        _erro("--tipo deve ser 'dentro' ou 'fora' do escopo.")
    complex_ = (a.complex or "moderado").lower()
    if complex_ not in COMPLEX:
        _erro("--complex deve ser simples | moderado | complexo.")
    item = {
        "id": _proximo_id(proj["escopo"]),
        "titulo": a.titulo.strip(),
        "horas": horas,
        "fase": (a.fase or "1").strip(),
        "tipo": tipo,
        "complexidade": complex_,
    }
    proj["escopo"].append(item)
    salvar(a.pasta, proj)
    onde = "DENTRO" if tipo == "dentro" else "FORA"
    print(f"✔ Escopo #{item['id']} ({onde}): {item['titulo']} — {horas:g}h, "
          f"fase {item['fase']}, {complex_}")


def cmd_escopo_rm(a):
    proj = _exige(a.pasta, a.proj)
    antes = len(proj["escopo"])
    proj["escopo"] = [i for i in proj["escopo"] if i["id"] != a.id]
    if len(proj["escopo"]) == antes:
        _erro(f"item de escopo #{a.id} não encontrado.")
    salvar(a.pasta, proj)
    print(f"✔ Item de escopo #{a.id} removido.")


def _prazo_semanas(horas_dentro, capacidade):
    if capacidade <= 0:
        return None
    return math.ceil(horas_dentro / capacidade)


def cmd_escopo(a):
    proj = _exige(a.pasta, a.proj)
    dentro = [i for i in proj["escopo"] if i["tipo"] == "dentro"]
    fora = [i for i in proj["escopo"] if i["tipo"] == "fora"]
    total = sum(i["horas"] for i in dentro)
    if a.formato == "json":
        print(json.dumps({"dentro": dentro, "fora": fora, "total_horas": total},
                         ensure_ascii=False))
        return
    print(f"ESCOPO — {proj['cliente']}\n")
    if not dentro:
        print("  (nenhum item dentro do escopo ainda)")
    # agrupa por fase
    fases = {}
    for i in dentro:
        fases.setdefault(i["fase"], []).append(i)
    for fase in sorted(fases):
        sub = sum(i["horas"] for i in fases[fase])
        print(f"  Fase {fase}  ({sub:g}h)")
        for i in fases[fase]:
            print(f"    #{i['id']} {i['titulo']} — {i['horas']:g}h [{i['complexidade']}]")
    print(f"\n  TOTAL no escopo: {total:g}h")
    mix = {c: sum(1 for i in dentro if i["complexidade"] == c) for c in COMPLEX}
    print(f"  Complexidade: {mix['simples']} simples · {mix['moderado']} moderado · {mix['complexo']} complexo")
    sem = _prazo_semanas(total, CAPACIDADE_PADRAO)
    if sem:
        print(f"  Prazo estimado: ~{sem} semana(s) a {CAPACIDADE_PADRAO:g}h/semana "
              f"(ajuste com 'prazo --capacidade-semana N')")
    if fora:
        print("\n  FORA do escopo (não incluído — protege contra 'mais uma coisinha'):")
        for i in fora:
            print(f"    • {i['titulo']}")


def cmd_prazo(a):
    proj = _exige(a.pasta, a.proj)
    cap = a.capacidade_semana or CAPACIDADE_PADRAO
    total = sum(i["horas"] for i in proj["escopo"] if i["tipo"] == "dentro")
    sem = _prazo_semanas(total, cap)
    if a.formato == "json":
        print(json.dumps({"total_horas": total, "capacidade_semana": cap,
                          "semanas": sem}, ensure_ascii=False))
        return
    print(f"PRAZO — {proj['cliente']}")
    print(f"  Esforço no escopo: {total:g}h")
    print(f"  Capacidade: {cap:g}h/semana dedicadas a este projeto")
    if sem:
        print(f"  → Prazo estimado: ~{sem} semana(s)")
    print("  (estimativa honesta — depende do cliente entregar acessos e dados no prazo)")


def cmd_roi(a):
    proj = _exige(a.pasta, a.proj)
    horas_mes = parse_horas(a.horas_mes)
    custo_cliente = parse_dinheiro(a.custo_hora_cliente)
    if horas_mes is None or custo_cliente is None:
        _erro("informe --horas-mes (horas economizadas por mês) e "
              "--custo-hora-cliente (quanto vale a hora de quem faz isso hoje).")
    economia_mes = horas_mes * custo_cliente
    economia_ano = economia_mes * 12

    total_horas = sum(i["horas"] for i in proj["escopo"] if i["tipo"] == "dentro")
    seu_custo = parse_dinheiro(a.seu_custo_hora)
    investimento = total_horas * seu_custo if (seu_custo and total_horas) else None
    recorrencia = parse_dinheiro(a.recorrencia)

    payback = None
    if investimento and economia_mes > 0:
        payback = investimento / economia_mes

    out = {
        "horas_economizadas_mes": horas_mes,
        "economia_mes": economia_mes,
        "economia_ano": economia_ano,
        "esforco_horas": total_horas,
        "investimento_estimado": investimento,
        "recorrencia_mes": recorrencia,
        "payback_meses": payback,
    }
    if a.formato == "json":
        print(json.dumps(out, ensure_ascii=False))
        return
    print(f"ROI & INVESTIMENTO — {proj['cliente']}\n")
    print(f"  O cliente economiza ~{horas_mes:g}h/mês × {brl(custo_cliente)}/h")
    print(f"  = {brl(economia_mes)}/mês  ({brl(economia_ano)}/ano)")
    if investimento:
        print(f"\n  Esforço do projeto: {total_horas:g}h × {brl(seu_custo)}/h (seu custo)")
        print(f"  = piso de investimento ~{brl(investimento)} (projeto único)")
        print("  ↳ Este é o PISO (custo do seu tempo). O preço final pode subir pelo")
        print("    VALOR entregue — quem economiza muito paga mais. (precificar = Forja)")
    if payback:
        print(f"\n  Payback: o cliente recupera o investimento em ~{payback:.1f} mês(es).")
    if recorrencia:
        print(f"\n  Recorrência sugerida: {brl(recorrencia)}/mês (manutenção + melhoria)")
        print("  Modelo recomendado: projeto único até subir + mensalidade depois de no ar.")
    print("\n  (todos os números vêm do que você informou — nada é inventado)")


def cmd_tarefa_add(a):
    proj = _exige(a.pasta, a.proj)
    etapa = (a.etapa or "build").lower()
    if etapa not in ETAPAS_TAREFA:
        _erro("--etapa deve ser build | teste | handoff.")
    item = {
        "id": _proximo_id(proj["tarefas"]),
        "titulo": a.titulo.strip(),
        "etapa": etapa,
        "status": "aberto",
    }
    proj["tarefas"].append(item)
    salvar(a.pasta, proj)
    print(f"✔ Tarefa #{item['id']} [{NOME_ETAPA[etapa]}]: {item['titulo']}")


def cmd_tarefas(a):
    proj = _exige(a.pasta, a.proj)
    tarefas = proj["tarefas"]
    if a.etapa:
        et = a.etapa.lower()
        if et not in ETAPAS_TAREFA:
            _erro("--etapa deve ser build | teste | handoff.")
        tarefas = [t for t in tarefas if t["etapa"] == et]
    if a.formato == "json":
        print(json.dumps(tarefas, ensure_ascii=False))
        return
    print(f"ENTREGA — {proj['cliente']}\n")
    if not tarefas:
        print("  (nenhuma tarefa de entrega ainda)")
        return
    feitas = sum(1 for t in tarefas if t["status"] == "feito")
    for et in ETAPAS_TAREFA:
        grupo = [t for t in tarefas if t["etapa"] == et]
        if not grupo:
            continue
        print(f"  {NOME_ETAPA[et]}")
        for t in grupo:
            box = "✔" if t["status"] == "feito" else "☐"
            print(f"    {box} #{t['id']} {t['titulo']}")
    pct = round(100 * feitas / len(tarefas)) if tarefas else 0
    print(f"\n  Progresso: {feitas}/{len(tarefas)} ({pct}%)")


def _muda_status(a, novo):
    proj = _exige(a.pasta, a.proj)
    for t in proj["tarefas"]:
        if t["id"] == a.id:
            t["status"] = novo
            salvar(a.pasta, proj)
            verbo = "concluída" if novo == "feito" else "reaberta"
            print(f"✔ Tarefa #{a.id} {verbo}: {t['titulo']}")
            return
    _erro(f"tarefa #{a.id} não encontrada.")


def cmd_concluir(a):
    _muda_status(a, "feito")


def cmd_reabrir(a):
    _muda_status(a, "aberto")


def cmd_resumo(a):
    proj = _exige(a.pasta, a.proj)
    dentro = [i for i in proj["escopo"] if i["tipo"] == "dentro"]
    fora = [i for i in proj["escopo"] if i["tipo"] == "fora"]
    total = sum(i["horas"] for i in dentro)
    sem = _prazo_semanas(total, CAPACIDADE_PADRAO)
    tarefas = proj["tarefas"]
    feitas = sum(1 for t in tarefas if t["status"] == "feito")
    if a.formato == "json":
        print(json.dumps({
            "cliente": proj["cliente"], "setor": proj["setor"],
            "output": proj["output"], "metrica": proj["metrica"],
            "escopo_horas": total, "itens_dentro": len(dentro),
            "itens_fora": len(fora), "semanas": sem,
            "tarefas_total": len(tarefas), "tarefas_feitas": feitas,
        }, ensure_ascii=False))
        return
    print(f"═══ RESUMO DO PROJETO ═══")
    print(f"Cliente: {proj['cliente']}   |   Setor: {proj['setor'] or '—'}")
    print(f"Output desejado: {proj['output'] or '— (defina no Briefing)'}")
    print(f"Métrica a mover: {proj['metrica'] or '— (defina no Mapear)'}")
    print(f"\nEscopo: {len(dentro)} item(ns) dentro · {len(fora)} fora · {total:g}h")
    if sem:
        print(f"Prazo estimado: ~{sem} semana(s) a {CAPACIDADE_PADRAO:g}h/semana")
    if tarefas:
        pct = round(100 * feitas / len(tarefas))
        print(f"Entrega: {feitas}/{len(tarefas)} tarefas ({pct}%)")
    else:
        print("Entrega: checklist ainda não montado (modo Entrega)")


# ----------------------------------------------------------------- argparse

def build_parser():
    p = argparse.ArgumentParser(description="Planta — motor de projetos de automação para clientes")
    p.add_argument("--pasta", default=PASTA_PADRAO)
    p.add_argument("--formato", default="texto", choices=["texto", "json"])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("novo"); s.add_argument("--cliente", required=True)
    s.add_argument("--setor"); s.add_argument("--output"); s.add_argument("--metrica")
    s.set_defaults(func=cmd_novo)

    s = sub.add_parser("info"); s.add_argument("--proj", required=True)
    s.add_argument("--setor"); s.add_argument("--output"); s.add_argument("--metrica")
    s.set_defaults(func=cmd_info)

    s = sub.add_parser("listar"); s.set_defaults(func=cmd_listar)

    s = sub.add_parser("escopo-add"); s.add_argument("--proj", required=True)
    s.add_argument("--titulo", required=True); s.add_argument("--horas", required=True)
    s.add_argument("--fase"); s.add_argument("--tipo"); s.add_argument("--complex")
    s.set_defaults(func=cmd_escopo_add)

    s = sub.add_parser("escopo"); s.add_argument("--proj", required=True)
    s.set_defaults(func=cmd_escopo)

    s = sub.add_parser("escopo-rm"); s.add_argument("--proj", required=True)
    s.add_argument("--id", type=int, required=True); s.set_defaults(func=cmd_escopo_rm)

    s = sub.add_parser("prazo"); s.add_argument("--proj", required=True)
    s.add_argument("--capacidade-semana", type=float, dest="capacidade_semana")
    s.set_defaults(func=cmd_prazo)

    s = sub.add_parser("roi"); s.add_argument("--proj", required=True)
    s.add_argument("--horas-mes", dest="horas_mes", required=True)
    s.add_argument("--custo-hora-cliente", dest="custo_hora_cliente", required=True)
    s.add_argument("--seu-custo-hora", dest="seu_custo_hora")
    s.add_argument("--recorrencia")
    s.set_defaults(func=cmd_roi)

    s = sub.add_parser("tarefa-add"); s.add_argument("--proj", required=True)
    s.add_argument("--titulo", required=True); s.add_argument("--etapa")
    s.set_defaults(func=cmd_tarefa_add)

    s = sub.add_parser("tarefas"); s.add_argument("--proj", required=True)
    s.add_argument("--etapa"); s.set_defaults(func=cmd_tarefas)

    s = sub.add_parser("concluir"); s.add_argument("--proj", required=True)
    s.add_argument("--id", type=int, required=True); s.set_defaults(func=cmd_concluir)

    s = sub.add_parser("reabrir"); s.add_argument("--proj", required=True)
    s.add_argument("--id", type=int, required=True); s.set_defaults(func=cmd_reabrir)

    s = sub.add_parser("resumo"); s.add_argument("--proj", required=True)
    s.set_defaults(func=cmd_resumo)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
