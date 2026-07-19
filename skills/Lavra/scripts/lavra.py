#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lavra — ajudante local de bastidor (somente biblioteca-padrão do Python).

Não instala nada, não acessa a internet. Guarda a identidade profissional e o
registro dos documentos lavrados na pasta local .lavra/, e roda o "gate de
completude" que aponta as seções obrigatórias ainda vazias de um rascunho.

Uso (você, a skill, chama nos bastidores — a pessoa só conversa):

  python3 scripts/lavra.py init  --nome "..." --registro "..." --area "..." \
                                 --cidade-uf "Cidade/UF" --saida "ambos"
  python3 scripts/lavra.py save  --tipo laudo --area saude --arquivo rascunho.md \
                                 [--titulo "..."] [--status rascunho|revisado|fechado]
  python3 scripts/lavra.py check --tipo laudo --area saude --arquivo rascunho.md
  python3 scripts/lavra.py list

Todas as áreas: saude, engenharia, juridico, contabil, administrativo, consultoria, generico
Tipos comuns: laudo, parecer, relatorio, atestado, despacho, nota-tecnica
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

ROOT = os.getcwd()
LAVRA_DIR = os.path.join(ROOT, ".lavra")
CONFIG = os.path.join(LAVRA_DIR, "config.json")
DOCS_DIR = os.path.join(LAVRA_DIR, "documentos")
MODELOS_DIR = os.path.join(LAVRA_DIR, "modelos")
REGISTRY = os.path.join(LAVRA_DIR, "registro.json")


# ---------------------------------------------------------------------------
# Seções obrigatórias por (área, tipo). Cada seção é uma lista de sinônimos:
# se QUALQUER um aparecer no texto do rascunho, a seção conta como preenchida.
# Alinhado com referencias/estruturas-por-area.md.
# ---------------------------------------------------------------------------
IDENT_RESP = ["identificacao do profissional", "responsavel tecnico", "identificacao do responsavel",
              "identificacao do servidor", "identificacao do consultor", "assinatura"]
OBJETIVO = ["objetivo", "finalidade", "indicacao", "objeto", "escopo"]
METODO = ["metodo", "metodologia", "tecnica", "abordagem", "base", "documentos analisados"]
ACHADOS = ["achados", "constatacoes", "descricao", "vistoria", "dos fatos", "relatorio",
           "diagnostico", "analise"]
CONCLUSAO = ["conclusao", "parecer", "impressao", "encaminhamento", "resposta", "recomendacoes"]
FECHO = ["local", "data", "assinatura"]

MANDATORY = {
    ("saude", "*"):          [IDENT_RESP, OBJETIVO, METODO, ACHADOS, CONCLUSAO, FECHO],
    ("engenharia", "*"):     [IDENT_RESP, OBJETIVO, METODO, ACHADOS, ["analise"], CONCLUSAO, FECHO],
    ("juridico", "*"):       [["ementa", "resumo"], ["consulente", "objeto"], ["dos fatos", "relatorio"],
                              ["fundamentacao", "analise juridica"], CONCLUSAO, FECHO],
    ("contabil", "*"):       [IDENT_RESP, ["entidade", "objeto"], OBJETIVO,
                              ["base", "documentos analisados"], ["analise"], CONCLUSAO, FECHO],
    ("administrativo", "*"): [["orgao", "processo"], ["servidor", "responsavel"], ["objeto"],
                              ["fundamentacao"], CONCLUSAO, FECHO],
    ("consultoria", "*"):    [["sumario executivo", "sumario"], ["consultor", "cliente"], OBJETIVO,
                              METODO, ACHADOS, ["recomendacoes", "analise"], FECHO],
    ("generico", "*"):       [IDENT_RESP, ["objeto"], OBJETIVO, METODO, ACHADOS, ["analise"], CONCLUSAO, FECHO],
}

# Atestado e despacho têm esqueleto reduzido.
REDUCED = {
    "atestado": [IDENT_RESP, ["finalidade", "objeto"], FECHO],
    "despacho": [["objeto", "processo"], ["fundamentacao"], CONCLUSAO, FECHO],
}


def _norm(s):
    """minúsculas sem acento, para casar seções de forma robusta."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def _now():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def _ensure_dirs():
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(MODELOS_DIR, exist_ok=True)


def _load_registry():
    if os.path.exists(REGISTRY):
        try:
            return json.load(open(REGISTRY, encoding="utf-8"))
        except Exception:
            return {"documentos": []}
    return {"documentos": []}


def _save_registry(reg):
    json.dump(reg, open(REGISTRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# Marcadores fortes de que uma seção está apenas com placeholder/pendência — ou seja,
# NÃO foi preenchida de verdade. Estas expressões só aparecem em texto de pendência
# (nunca num achado/conclusão real), então bastam para reprovar a seção.
STRONG_PENDING = ["⏳", "pendente", "a preencher", "a definir", "descreva a sua",
                  "descreva o seu", "preencha ", "aguardando", "nada informado",
                  "a ser preenchid", "informe aqui", "(a definir"]


def _section_label(syns):
    return syns[0]


def _split_sections(text):
    """Divide o markdown em blocos (titulo, corpo) pelos cabeçalhos '#'..'######'."""
    blocks = []
    head, body = "__preambulo__", []
    for line in text.splitlines():
        if re.match(r"^\s{0,3}#{1,6}\s", line):
            blocks.append((head, "\n".join(body)))
            head, body = line, []
        else:
            body.append(line)
    blocks.append((head, "\n".join(body)))
    return blocks


def _body_is_filled(body):
    """True só se o corpo tem conteúdo REAL — não vazio e sem marcador de pendência.

    É isto que impede o "verde falso": uma seção obrigatória cujo corpo é apenas o
    placeholder de pendência (⏳/"pendente"/"descreva a sua…") conta como VAZIA,
    mesmo que o placeholder mencione a palavra-chave da seção.
    """
    nb = _norm(body)
    if any(_norm(m) in nb for m in STRONG_PENDING):
        return False
    stripped = re.sub(r"[>*_`#\-•\s]+", " ", nb).strip()
    return len(stripped) >= 8


def _missing_sections(text, tipo, area):
    tipo = _norm(tipo or "").strip()
    area = _norm(area or "").strip()
    if tipo in REDUCED:
        required = REDUCED[tipo]
    else:
        required = MANDATORY.get((area, "*")) or MANDATORY[("generico", "*")]

    blocks = _split_sections(text)
    ntext = _norm(text)
    missing = []
    for syns in required:
        # 1) casa por CABEÇALHO de seção e verifica se o corpo está preenchido de verdade
        matched = [(h, b) for (h, b) in blocks if any(_norm(s) in _norm(h) for s in syns)]
        if matched:
            if not any(_body_is_filled(b) for (_h, b) in matched):
                # o cabeçalho existe, mas o conteúdo está pendente/vazio → obrigatória faltando
                missing.append(_section_label(syns))
            continue
        # 2) sem cabeçalho próprio: cai para presença no texto (cobre o fecho: local/data/assinatura)
        if not any(_norm(s) in ntext for s in syns):
            missing.append(_section_label(syns))
    return missing


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------
def cmd_init(a):
    _ensure_dirs()
    cfg = {
        "nome": a.nome or "",
        "registro": a.registro or "",
        "area": a.area or "",
        "cidade_uf": a.cidade_uf or "",
        "saida": a.saida or "ambos",
        "criado_em": _now(),
    }
    json.dump(cfg, open(CONFIG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if not os.path.exists(REGISTRY):
        _save_registry({"documentos": []})
    print("OK — Lavra configurada.")
    print(json.dumps(cfg, ensure_ascii=False, indent=2))


def cmd_save(a):
    if not os.path.exists(CONFIG):
        print("ERRO: rode 'init' primeiro (a Lavra ainda não foi configurada).")
        sys.exit(1)
    _ensure_dirs()
    reg = _load_registry()
    doc_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    stored_rel = os.path.join("documentos", "%s-%s.md" % (doc_id, _norm(a.tipo or "doc")))
    stored_abs = os.path.join(LAVRA_DIR, stored_rel)
    missing = []
    if a.arquivo and os.path.exists(a.arquivo):
        text = open(a.arquivo, encoding="utf-8", errors="ignore").read()
        open(stored_abs, "w", encoding="utf-8").write(text)
        missing = _missing_sections(text, a.tipo, a.area)
    entry = {
        "id": doc_id,
        "titulo": a.titulo or ("%s (%s)" % (a.tipo, a.area)),
        "tipo": a.tipo or "",
        "area": a.area or "",
        "status": a.status or "rascunho",
        "arquivo": stored_rel,
        "pendencias_obrigatorias": missing,
        "atualizado_em": _now(),
    }
    # substitui se já existir mesmo titulo+tipo em rascunho? Simples: sempre anexa.
    reg["documentos"].append(entry)
    _save_registry(reg)
    print("OK — documento registrado: %s" % entry["titulo"])
    if missing:
        print("PENDÊNCIAS OBRIGATÓRIAS (🔴): " + ", ".join(missing))
    else:
        print("Nenhuma seção obrigatória faltando pela verificação automática.")


def cmd_check(a):
    if not a.arquivo or not os.path.exists(a.arquivo):
        print("ERRO: informe --arquivo com o caminho do rascunho.")
        sys.exit(1)
    text = open(a.arquivo, encoding="utf-8", errors="ignore").read()
    missing = _missing_sections(text, a.tipo, a.area)
    print("=== Gate de completude — %s / %s ===" % (a.tipo, a.area))
    if not missing:
        print("✅ Nenhuma seção obrigatória vazia detectada.")
        print("   (Isto NÃO garante que o conteúdo esteja correto — a revisão linha a linha é do profissional.)")
    else:
        print("⛔ INCOMPLETO. Seções obrigatórias ausentes/vazias:")
        for m in missing:
            print("   🔴 %s" % m)
        print("\nResolva com o profissional (nunca preencha por conta própria) antes de fechar.")


def cmd_list(a):
    reg = _load_registry()
    docs = reg.get("documentos", [])
    if not docs:
        print("Nenhum documento lavrado ainda.")
        return
    icon = {"rascunho": "📝", "revisado": "✅", "fechado": "🔒"}
    print("=== Documentos lavrados ===")
    for d in docs:
        pend = d.get("pendencias_obrigatorias") or []
        pend_txt = ("  ⚠ %d pendência(s): %s" % (len(pend), ", ".join(pend))) if pend else ""
        print("%s  %s  [%s/%s]  %s%s" % (
            icon.get(d.get("status"), "•"),
            d.get("titulo", "?"),
            d.get("tipo", "?"), d.get("area", "?"),
            d.get("atualizado_em", ""),
            pend_txt,
        ))


def main():
    p = argparse.ArgumentParser(description="Lavra — ajudante local (stdlib, offline).")
    sub = p.add_subparsers(dest="cmd")

    pi = sub.add_parser("init")
    pi.add_argument("--nome"); pi.add_argument("--registro"); pi.add_argument("--area")
    pi.add_argument("--cidade-uf", dest="cidade_uf"); pi.add_argument("--saida")
    pi.set_defaults(func=cmd_init)

    ps = sub.add_parser("save")
    ps.add_argument("--tipo"); ps.add_argument("--area"); ps.add_argument("--arquivo")
    ps.add_argument("--titulo"); ps.add_argument("--status")
    ps.set_defaults(func=cmd_save)

    pc = sub.add_parser("check")
    pc.add_argument("--tipo"); pc.add_argument("--area"); pc.add_argument("--arquivo")
    pc.set_defaults(func=cmd_check)

    pl = sub.add_parser("list")
    pl.set_defaults(func=cmd_list)

    a = p.parse_args()
    if not getattr(a, "cmd", None):
        p.print_help()
        return
    a.func(a)


if __name__ == "__main__":
    main()
