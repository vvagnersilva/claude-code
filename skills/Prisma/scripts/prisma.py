#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prisma — motor da BIBLIOTECA de prompts (somente biblioteca padrão do Python).

A IA é quem CRIA, CONSERTA e AFINA os prompts conversando com o dono.
Este motor só faz a parte exata e chata: GUARDAR, LISTAR, BUSCAR, USAR e CONTAR
os prompts reutilizáveis. Cada prompt vira um arquivo JSON em .prisma/biblioteca/.

Nunca acessa a internet. Nunca executa o prompt. Só organiza o acervo local.

Uso (a IA chama por baixo dos panos; o dono só conversa em português):
  python3 prisma.py salvar  --titulo "T" --categoria "C" --tags "a,b" --texto-arquivo /tmp/p.txt [--ferramenta "ChatGPT"] [--nota "..."]
  python3 prisma.py listar  [--categoria "C"]
  python3 prisma.py buscar  "termos de busca"
  python3 prisma.py usar    <slug-ou-numero>          # imprime o prompt e conta +1 uso
  python3 prisma.py ver     <slug-ou-numero>          # imprime sem contar uso
  python3 prisma.py editar  <slug-ou-numero> [--titulo ...] [--categoria ...] [--tags ...] [--texto-arquivo ...] [--nota ...]
  python3 prisma.py remover <slug-ou-numero>
  python3 prisma.py stats
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path


def _project_root() -> Path:
    """Onde guardar o .prisma/ — sempre a RAIZ do projeto do usuário, nunca a
    pasta da skill, independente de onde o script foi chamado.

    1) Respeita CLAUDE_PROJECT_DIR (definido pelo Claude Code) se existir.
    2) Se o cwd estiver dentro de uma pasta .claude (ex.: a pasta da skill),
       sobe para o nível acima do .claude (a raiz do projeto).
    3) Senão, sobe procurando um marcador .git/.claude.
    4) Último caso: o diretório atual.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    cwd = Path.cwd().resolve()
    parts = cwd.parts
    if ".claude" in parts:
        idx = parts.index(".claude")
        if idx > 0:
            return Path(*parts[:idx])
    for p in [cwd, *cwd.parents]:
        if (p / ".git").is_dir() or (p / ".claude").is_dir():
            return p
    return cwd


BASE = _project_root() / ".prisma"
LIB = BASE / "biblioteca"

# ---------------------------------------------------------------- utilidades

def _ensure():
    LIB.mkdir(parents=True, exist_ok=True)

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def slugify(texto: str) -> str:
    s = _strip_accents(texto.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s or "prompt")[:48]

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _unique_slug(base_slug: str) -> str:
    slug, n = base_slug, 2
    while (LIB / f"{slug}.json").exists():
        slug = f"{base_slug}-{n}"
        n += 1
    return slug

def _load_all():
    """Lê todos os prompts, ordenados por data de criação (mais novo por último)."""
    _ensure()
    itens = []
    for f in sorted(LIB.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            d["_arquivo"] = f
            itens.append(d)
        except Exception as e:
            print(f"  (aviso: pulei {f.name}: {e})", file=sys.stderr)
    itens.sort(key=lambda x: (x.get("criado_em", ""), x.get("slug", "")))
    return itens

def _resolve(ref: str):
    """Aceita um slug exato ou um número da última listagem (1-based)."""
    itens = _load_all()
    if ref.isdigit():
        i = int(ref) - 1
        if 0 <= i < len(itens):
            return itens[i]
        return None
    p = LIB / f"{ref}.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        d["_arquivo"] = p
        return d
    # tolera referência parcial
    cand = [x for x in itens if ref in x.get("slug", "")]
    return cand[0] if len(cand) == 1 else None

def _tokens(texto: str):
    return set(re.findall(r"[a-z0-9]{3,}", _strip_accents(texto.lower())))

def _variaveis(texto: str):
    """Extrai variáveis no formato {assim} de um molde."""
    return sorted(set(re.findall(r"\{([^{}]+)\}", texto)))

# ---------------------------------------------------------------- comandos

def cmd_salvar(a):
    _ensure()
    texto = Path(a.texto_arquivo).read_text(encoding="utf-8").strip()
    if not texto:
        print("ERRO: o prompt está vazio.", file=sys.stderr); sys.exit(1)
    slug = _unique_slug(slugify(a.titulo))
    tags = [t.strip() for t in (a.tags or "").split(",") if t.strip()]
    d = {
        "slug": slug,
        "titulo": a.titulo.strip(),
        "categoria": (a.categoria or "Geral").strip(),
        "tags": tags,
        "ferramenta": (a.ferramenta or "").strip(),
        "nota": (a.nota or "").strip(),
        "texto": texto,
        "variaveis": _variaveis(texto),
        "criado_em": _now(),
        "usos": 0,
    }
    (LIB / f"{slug}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    vs = f" · variáveis: {', '.join('{'+v+'}' for v in d['variaveis'])}" if d["variaveis"] else ""
    print(f"✅ Guardado na biblioteca: «{d['titulo']}»  [{d['categoria']}]  (slug: {slug}){vs}")

def _linha(i, d):
    tags = ("  #" + " #".join(d["tags"])) if d.get("tags") else ""
    vs = f"  ·{len(d['variaveis'])} var" if d.get("variaveis") else ""
    usos = d.get("usos", 0)
    return f"{i:>2}. [{d.get('categoria','Geral')}] {d['titulo']}{tags}{vs}  ({usos} usos · {d.get('slug')})"

def cmd_listar(a):
    itens = _load_all()
    if a.categoria:
        itens = [x for x in itens if x.get("categoria", "").lower() == a.categoria.lower()]
    if not itens:
        print("Biblioteca vazia (ou nenhuma nessa categoria). Crie um prompt e salve para começar.")
        return
    print(f"📚 Biblioteca de prompts — {len(itens)} item(ns):\n")
    for i, d in enumerate(itens, 1):
        print(_linha(i, d))
    print("\nDica: use «usar <número ou slug>» para pegar um prompt pronto.")

def cmd_buscar(a):
    termos = _tokens(" ".join(a.termos))
    if not termos:
        print("Diga o que procura, ex.: buscar e-mail cobrança"); return
    itens = _load_all()
    pont = []
    for d in itens:
        campo = " ".join([d.get("titulo", ""), d.get("categoria", ""),
                          " ".join(d.get("tags", [])), d.get("texto", ""),
                          d.get("nota", "")])
        score = len(termos & _tokens(campo))
        if score:
            pont.append((score, d))
    pont.sort(key=lambda x: (-x[0], x[1].get("titulo", "")))
    if not pont:
        print("Nada encontrado. Tente outras palavras ou veja tudo com «listar»."); return
    print(f"🔎 {len(pont)} resultado(s):\n")
    for i, (sc, d) in enumerate(pont, 1):
        print(_linha(i, d))

def _imprimir(d):
    print("─" * 60)
    print(f"TÍTULO:    {d['titulo']}")
    print(f"CATEGORIA: {d.get('categoria','Geral')}", end="")
    if d.get("ferramenta"):
        print(f"   ·  FERRAMENTA: {d['ferramenta']}", end="")
    print()
    if d.get("tags"):
        print(f"TAGS:      #{' #'.join(d['tags'])}")
    if d.get("variaveis"):
        print(f"PREENCHA:  {', '.join('{'+v+'}' for v in d['variaveis'])}")
    print("─" * 60)
    print(d["texto"])
    print("─" * 60)
    if d.get("nota"):
        print(f"📝 Nota: {d['nota']}")

def cmd_usar(a):
    d = _resolve(a.ref)
    if not d:
        print(f"Não achei «{a.ref}». Veja a lista com «listar».", file=sys.stderr); sys.exit(1)
    d["usos"] = d.get("usos", 0) + 1
    f = d.pop("_arquivo")
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    _imprimir(d)
    if d.get("variaveis"):
        print(f"\n👉 Troque {', '.join('{'+v+'}' for v in d['variaveis'])} pelos dados de hoje antes de colar na sua ferramenta.")

def cmd_ver(a):
    d = _resolve(a.ref)
    if not d:
        print(f"Não achei «{a.ref}».", file=sys.stderr); sys.exit(1)
    _imprimir(d)

def cmd_editar(a):
    d = _resolve(a.ref)
    if not d:
        print(f"Não achei «{a.ref}».", file=sys.stderr); sys.exit(1)
    f = d.pop("_arquivo")
    if a.titulo:    d["titulo"] = a.titulo.strip()
    if a.categoria: d["categoria"] = a.categoria.strip()
    if a.tags is not None:
        d["tags"] = [t.strip() for t in a.tags.split(",") if t.strip()]
    if a.ferramenta is not None: d["ferramenta"] = a.ferramenta.strip()
    if a.nota is not None:       d["nota"] = a.nota.strip()
    if a.texto_arquivo:
        d["texto"] = Path(a.texto_arquivo).read_text(encoding="utf-8").strip()
        d["variaveis"] = _variaveis(d["texto"])
    d["atualizado_em"] = _now()
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Atualizado: «{d['titulo']}» ({d['slug']})")

def cmd_remover(a):
    d = _resolve(a.ref)
    if not d:
        print(f"Não achei «{a.ref}».", file=sys.stderr); sys.exit(1)
    d["_arquivo"].unlink()
    print(f"🗑️  Removido: «{d['titulo']}» ({d['slug']})")

def cmd_stats(a):
    itens = _load_all()
    if not itens:
        print("Biblioteca vazia."); return
    cats = {}
    for d in itens:
        cats[d.get("categoria", "Geral")] = cats.get(d.get("categoria", "Geral"), 0) + 1
    mais = sorted(itens, key=lambda x: -x.get("usos", 0))[:5]
    print(f"📊 Painel da biblioteca\n")
    print(f"Total de prompts: {len(itens)}")
    print(f"Usos somados:     {sum(d.get('usos',0) for d in itens)}\n")
    print("Por categoria:")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  · {c}: {n}")
    print("\nMais usados:")
    for d in mais:
        print(f"  · {d['titulo']} — {d.get('usos',0)} usos")

# ---------------------------------------------------------------- cli

def main():
    p = argparse.ArgumentParser(description="Motor da biblioteca de prompts do Prisma.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("salvar"); s.set_defaults(fn=cmd_salvar)
    s.add_argument("--titulo", required=True)
    s.add_argument("--categoria")
    s.add_argument("--tags")
    s.add_argument("--ferramenta")
    s.add_argument("--nota")
    s.add_argument("--texto-arquivo", dest="texto_arquivo", required=True)

    s = sub.add_parser("listar"); s.set_defaults(fn=cmd_listar)
    s.add_argument("--categoria")

    s = sub.add_parser("buscar"); s.set_defaults(fn=cmd_buscar)
    s.add_argument("termos", nargs="+")

    s = sub.add_parser("usar"); s.set_defaults(fn=cmd_usar)
    s.add_argument("ref")

    s = sub.add_parser("ver"); s.set_defaults(fn=cmd_ver)
    s.add_argument("ref")

    s = sub.add_parser("editar"); s.set_defaults(fn=cmd_editar)
    s.add_argument("ref")
    s.add_argument("--titulo")
    s.add_argument("--categoria")
    s.add_argument("--tags")
    s.add_argument("--ferramenta")
    s.add_argument("--nota")
    s.add_argument("--texto-arquivo", dest="texto_arquivo")

    s = sub.add_parser("remover"); s.set_defaults(fn=cmd_remover)
    s.add_argument("ref")

    s = sub.add_parser("stats"); s.set_defaults(fn=cmd_stats)

    a = p.parse_args()
    a.fn(a)

if __name__ == "__main__":
    main()
