#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tato - motor do caderno de conversas dificeis e negociacao.

Somente biblioteca padrao do Python (stdlib). Sem rede, sem chave de API, sem
biblioteca externa. Le e escreve uma pasta local: .tato/ (na raiz do projeto).

A IA e quem CONVERSA, PREPARA e ESCREVE as mensagens dificeis (com base nas
referencias e no tom do dono). O motor faz APENAS a parte exata: guardar uma
mensagem/preparacao pronta como um "cartao" reutilizavel, listar, buscar por
sobreposicao de palavras, carregar para reusar (contando os usos), editar,
remover e dar o painel. O motor nao inventa texto nem manda mensagem.

A ideia: toda vez que o dono resolve uma conversa dificil (recusar, pedir
prazo, dar feedback, negociar preco), ele pode GUARDAR o roteiro no caderno e
reusar da proxima vez, sempre no tom dele - sem comecar do zero.

Uso (a IA chama por baixo; o dono so conversa):
  tato.py init
  tato.py salvar --tipo mensagem --titulo "Recusar orcamento abaixo do minimo" \
          --tags "preco,recusa" --corpo-arquivo /tmp/x.txt [--contexto "..."]
  tato.py listar [--tipo mensagem|preparacao|negociacao|feedback|resposta] [--tag preco]
  tato.py buscar --termo "recusar cliente caro"
  tato.py usar --slug recusar-orcamento-abaixo-do-minimo   # carrega e conta +1 uso
  tato.py ver --slug ...
  tato.py editar --slug ... [--titulo ..] [--tags ..] [--corpo-arquivo ..] [--contexto ..]
  tato.py remover --slug ...
  tato.py stats

O texto longo (o corpo do roteiro) entra por --corpo-arquivo (um arquivo de
texto) para nunca quebrar com aspas/quebras de linha. --contexto e uma linha curta.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import date


# ----------------------------------------------------------------------------
# Localizacao da raiz do projeto (.tato na raiz, nao dentro da skill)
# ----------------------------------------------------------------------------
def achar_raiz():
    # 1) variavel do Claude Code
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    # 2) sobe procurando uma pasta .tato ja existente
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".tato")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    # 3) sobe procurando uma pasta .claude (raiz tipica de projeto)
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".claude")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    # 4) fallback: diretorio atual
    return os.getcwd()


RAIZ = achar_raiz()
BASE = os.path.join(RAIZ, ".tato")
CADERNO = os.path.join(BASE, "caderno")

TIPOS = {"mensagem", "preparacao", "negociacao", "feedback", "resposta"}

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "e", "em", "no", "na", "nos", "nas", "para", "pra", "por", "com",
    "sem", "que", "se", "ao", "aos", "à", "às", "ou", "mas", "como", "meu",
    "minha", "seu", "sua", "the", "of", "to", "is", "eu", "voce", "ele", "ela",
    "isso", "este", "esta", "esse", "essa", "ja", "nao", "sim",
}


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def garantir_dirs():
    os.makedirs(CADERNO, exist_ok=True)


def fold(s):
    """minuscula sem acento."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def tokens(texto):
    palavras = re.findall(r"[a-z0-9]+", fold(texto))
    return [p for p in palavras if len(p) > 2 and p not in STOPWORDS]


def conjunto_tokens(texto):
    return set(tokens(texto))


def slugificar(titulo):
    s = fold(titulo)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60] or "sem-titulo"


def hoje_iso():
    return date.today().isoformat()


def caminho(slug):
    return os.path.join(CADERNO, slug + ".json")


def ler_cartao(slug):
    p = caminho(slug)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def escrever_cartao(m):
    garantir_dirs()
    with open(caminho(m["slug"]), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)


def todos_cartoes():
    if not os.path.isdir(CADERNO):
        return []
    out = []
    for nome in sorted(os.listdir(CADERNO)):
        if nome.endswith(".json"):
            try:
                with open(os.path.join(CADERNO, nome), encoding="utf-8") as f:
                    out.append(json.load(f))
            except Exception:
                pass
    return out


def ler_corpo(args):
    if getattr(args, "corpo_arquivo", None):
        with open(args.corpo_arquivo, encoding="utf-8") as f:
            return f.read().strip()
    if getattr(args, "corpo", None):
        return args.corpo.strip()
    return ""


# ----------------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------------
def cmd_init(args):
    garantir_dirs()
    print("OK: caderno do Tato pronto em", BASE)


def cmd_salvar(args):
    garantir_dirs()
    tipo = (args.tipo or "mensagem").strip().lower()
    if tipo not in TIPOS:
        print("ERRO: tipo deve ser um de:", ", ".join(sorted(TIPOS)))
        sys.exit(1)
    if not args.titulo:
        print("ERRO: --titulo e obrigatorio")
        sys.exit(1)
    corpo = ler_corpo(args)
    if not corpo:
        print("ERRO: corpo vazio. Use --corpo-arquivo <arquivo> com o roteiro.")
        sys.exit(1)
    slug = slugificar(args.titulo)
    # nao sobrescrever sem querer: se ja existe, sufixa
    base_slug = slug
    n = 2
    while os.path.exists(caminho(slug)) and not args.sobrescrever:
        slug = f"{base_slug}-{n}"
        n += 1
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    m = {
        "slug": slug,
        "tipo": tipo,
        "titulo": args.titulo.strip(),
        "tags": tags,
        "contexto": (args.contexto or "").strip(),
        "corpo": corpo,
        "criado": hoje_iso(),
        "usos": 0,
    }
    escrever_cartao(m)
    print("OK: guardado no caderno como", slug, f"(tipo: {tipo})")


def pontuar(consulta, m):
    alvo = conjunto_tokens(
        " ".join([m.get("titulo", ""), " ".join(m.get("tags", [])),
                  m.get("contexto", ""), m.get("corpo", "")])
    )
    titulo_tok = conjunto_tokens(m.get("titulo", "")) | conjunto_tokens(
        " ".join(m.get("tags", [])))
    comuns = consulta & alvo
    if not comuns:
        return 0.0
    score = len(comuns) / max(1, len(consulta))
    # bonus se bater no titulo/tags
    score += 0.4 * len(consulta & titulo_tok)
    return score


def cmd_buscar(args):
    consulta = conjunto_tokens(args.termo or "")
    if not consulta:
        print("ERRO: --termo vazio")
        sys.exit(1)
    ranq = []
    for m in todos_cartoes():
        s = pontuar(consulta, m)
        if s > 0:
            ranq.append((s, m))
    ranq.sort(key=lambda x: x[0], reverse=True)
    if not ranq:
        print("NADA_ENCONTRADO")
        return
    for s, m in ranq[: args.limite]:
        print(f"[{m['slug']}] ({m['tipo']}) {m['titulo']}  ~{s:.2f}  usos:{m.get('usos',0)}")
        if m.get("contexto"):
            print("    contexto:", m["contexto"])


def cmd_listar(args):
    cartoes = todos_cartoes()
    if args.tipo:
        cartoes = [m for m in cartoes if m.get("tipo") == args.tipo.lower()]
    if args.tag:
        tg = args.tag.strip().lower()
        cartoes = [m for m in cartoes if tg in [t.lower() for t in m.get("tags", [])]]
    if not cartoes:
        print("(caderno vazio para esse filtro)")
        return
    # mais usados primeiro
    cartoes.sort(key=lambda m: (-m.get("usos", 0), m.get("titulo", "")))
    for m in cartoes:
        tags = ", ".join(m.get("tags", []))
        print(f"[{m['slug']}] ({m['tipo']}) {m['titulo']}"
              f"{('  #' + tags) if tags else ''}  usos:{m.get('usos',0)}")


def cmd_ver(args):
    m = ler_cartao(args.slug)
    if not m:
        print("NAO_ENCONTRADO:", args.slug)
        sys.exit(1)
    print(json.dumps(m, ensure_ascii=False, indent=2))


def cmd_usar(args):
    m = ler_cartao(args.slug)
    if not m:
        print("NAO_ENCONTRADO:", args.slug)
        sys.exit(1)
    m["usos"] = int(m.get("usos", 0)) + 1
    escrever_cartao(m)
    # imprime o roteiro pronto para a IA reaproveitar e adaptar
    print(f"### {m['titulo']}  ({m['tipo']})")
    if m.get("contexto"):
        print("Contexto:", m["contexto"])
    if m.get("tags"):
        print("Tags:", ", ".join(m["tags"]))
    print("Usos (agora):", m["usos"])
    print("---")
    print(m.get("corpo", ""))


def cmd_editar(args):
    m = ler_cartao(args.slug)
    if not m:
        print("NAO_ENCONTRADO:", args.slug)
        sys.exit(1)
    if args.titulo:
        m["titulo"] = args.titulo.strip()
    if args.tags is not None:
        m["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if args.contexto is not None:
        m["contexto"] = args.contexto.strip()
    corpo = ler_corpo(args)
    if corpo:
        m["corpo"] = corpo
    escrever_cartao(m)
    print("OK: atualizado", m["slug"])


def cmd_remover(args):
    p = caminho(args.slug)
    if not os.path.exists(p):
        print("NAO_ENCONTRADO:", args.slug)
        sys.exit(1)
    os.remove(p)
    print("OK: removido", args.slug)


def cmd_stats(args):
    cartoes = todos_cartoes()
    if not cartoes:
        print("Caderno vazio. Guarde seu primeiro roteiro com 'salvar'.")
        return
    por_tipo = {}
    usos_total = 0
    for m in cartoes:
        por_tipo[m.get("tipo", "?")] = por_tipo.get(m.get("tipo", "?"), 0) + 1
        usos_total += int(m.get("usos", 0))
    print(f"Roteiros no caderno: {len(cartoes)}")
    print("Por tipo:")
    for t in sorted(por_tipo):
        print(f"  - {t}: {por_tipo[t]}")
    print(f"Reusos totais: {usos_total}")
    mais = sorted(cartoes, key=lambda m: -m.get("usos", 0))[:3]
    if mais and mais[0].get("usos", 0) > 0:
        print("Mais reusados:")
        for m in mais:
            if m.get("usos", 0) > 0:
                print(f"  - {m['titulo']} ({m.get('usos',0)})")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(description="Tato - caderno de conversas dificeis")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init"); sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("salvar")
    sp.add_argument("--tipo", default="mensagem")
    sp.add_argument("--titulo", required=True)
    sp.add_argument("--tags", default="")
    sp.add_argument("--contexto", default="")
    sp.add_argument("--corpo")
    sp.add_argument("--corpo-arquivo", dest="corpo_arquivo")
    sp.add_argument("--sobrescrever", action="store_true")
    sp.set_defaults(func=cmd_salvar)

    sp = sub.add_parser("buscar")
    sp.add_argument("--termo", required=True)
    sp.add_argument("--limite", type=int, default=8)
    sp.set_defaults(func=cmd_buscar)

    sp = sub.add_parser("listar")
    sp.add_argument("--tipo")
    sp.add_argument("--tag")
    sp.set_defaults(func=cmd_listar)

    sp = sub.add_parser("ver")
    sp.add_argument("--slug", required=True)
    sp.set_defaults(func=cmd_ver)

    sp = sub.add_parser("usar")
    sp.add_argument("--slug", required=True)
    sp.set_defaults(func=cmd_usar)

    sp = sub.add_parser("editar")
    sp.add_argument("--slug", required=True)
    sp.add_argument("--titulo")
    sp.add_argument("--tags")
    sp.add_argument("--contexto")
    sp.add_argument("--corpo")
    sp.add_argument("--corpo-arquivo", dest="corpo_arquivo")
    sp.set_defaults(func=cmd_editar)

    sp = sub.add_parser("remover")
    sp.add_argument("--slug", required=True)
    sp.set_defaults(func=cmd_remover)

    sp = sub.add_parser("stats"); sp.set_defaults(func=cmd_stats)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
