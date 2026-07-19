#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cartilha — motor do manual de processos do dono de negócio.

A Cartilha pega um processo que hoje está SÓ na cabeça do dono ("como eu faço
X") e o transforma num POP (Procedimento Operacional Padrão): um passo a passo
claro que QUALQUER pessoa da equipe consegue seguir, com checklist de qualidade
e os erros a evitar. A partir daí o dono consegue TREINAR quem vai assumir e
DELEGAR sem a qualidade cair.

Este motor cuida APENAS de guardar, listar, versionar e contar o uso dos POPs.
Quem CONDUZ a conversa, ESCREVE o POP, monta o treinamento e o briefing de
delegação é a IA (a parte inteligente), lendo o POP que este motor entrega.
Usa SOMENTE a biblioteca padrão do Python. Nunca inventa nada: cada POP é
exatamente o que o dono ditou.

Onde ficam os dados (tudo local, na RAIZ do projeto do usuário):
    .cartilha/config.md          -> configuração (criada na primeira conversa)
    .cartilha/pops/<slug>.json   -> um processo por arquivo (fonte da verdade)

Formato de um POP (.json):
    {
      "slug": "fechar-o-caixa",
      "nome": "Fechar o caixa no fim do dia",
      "objetivo": "Garantir que o dinheiro do dia bate e nada fica solto",
      "quando": "Todo dia, na hora de fechar a loja",
      "responsavel": "Quem está no balcão no fechamento",
      "ferramentas": ["Maquininha", "Planilha do caixa"],
      "entradas": ["Cupons do dia", "Saldo inicial da gaveta"],
      "passos": ["Conte o dinheiro da gaveta", "Compare com o relatório da maquininha", "..."],
      "decisoes": ["Se faltar dinheiro, anote o valor e avise o dono no mesmo dia"],
      "qualidade": ["O valor da gaveta bate com o relatório", "A planilha foi salva"],
      "nao_fazer": ["Nunca leve a diferença pra casa pra 'acertar amanhã'"],
      "saida": "Planilha do caixa do dia preenchida e gaveta conferida",
      "exemplo": "Dia 12/06: gaveta R$ 840, relatório R$ 840, bateu.",
      "nivel": "alto",
      "versao": 1,
      "criado_em": "2026-06-26",
      "atualizado_em": "2026-06-26",
      "historico": [],
      "usos": 0,
      "ultimo_uso": ""
    }

Comandos:
    python3 cartilha.py nova --nome "..." --objetivo "..." [--quando "..."]
            [--responsavel "..."] [--ferramentas "a||b"] [--entradas "a||b"]
            [--passos "p1||p2||p3"] [--decisoes "d1||d2"] [--qualidade "q1||q2"]
            [--nao-fazer "n1||n2"] [--saida "..."] [--exemplo "..."] [--nivel baixo|medio|alto]
    python3 cartilha.py listar                  # todos os POPs da cartilha
    python3 cartilha.py ver --slug X            # mostra o POP (para a IA seguir)
    python3 cartilha.py usar --slug X           # igual ao ver + conta +1 uso
    python3 cartilha.py editar --slug X [--nome ...] [--objetivo ...] ...
            [--nota "o que mudou"]              # registra a mudança no histórico
    python3 cartilha.py revisar --slug X --nota "..."   # sobe a versão (revisão)
    python3 cartilha.py remover --slug X
    python3 cartilha.py stats                   # painel da cartilha
Opções globais: --pasta <dir>   (padrão: raiz/.cartilha)
                --formato json  (padrão: texto)
"""

import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from datetime import date


SEP = "||"  # separador para listas passadas na linha de comando


# ---------------------------------------------------------------- raiz/projeto

def _project_root():
    """Onde guardar o .cartilha/ — sempre a RAIZ do projeto do usuário, nunca a
    pasta da skill, independente de onde o script foi chamado.

    1) Respeita CLAUDE_PROJECT_DIR (definido pelo Claude Code) se existir.
    2) Se o cwd estiver dentro de uma pasta .claude (ex.: a pasta da skill),
       sobe para o nível acima do .claude (a raiz do projeto).
    3) Senão, sobe procurando um marcador .git/.claude.
    4) Último caso: o diretório atual.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return os.path.abspath(env)
    cwd = os.path.abspath(os.getcwd())
    parts = cwd.split(os.sep)
    if ".claude" in parts:
        idx = parts.index(".claude")
        if idx > 0:
            return os.sep.join(parts[:idx]) or os.sep
    p = cwd
    while True:
        if os.path.isdir(os.path.join(p, ".git")) or os.path.isdir(os.path.join(p, ".claude")):
            return p
        novo = os.path.dirname(p)
        if novo == p:
            break
        p = novo
    return cwd


def _pasta_padrao():
    return os.path.join(_project_root(), ".cartilha")


# ---------------------------------------------------------------- utilidades

def _hoje():
    return date.today().isoformat()


def _norm(s):
    """minúsculas e sem acento, para gerar slug e comparar."""
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _slugify(nome):
    base = _norm(nome)
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return (base or "processo")[:48]


def _dir_pops(pasta):
    return os.path.join(pasta, "pops")


def _caminho(pasta, slug):
    return os.path.join(_dir_pops(pasta), slug + ".json")


def _slug_unico(pasta, nome):
    """gera um slug que ainda não existe (acrescenta -2, -3... se preciso)."""
    base = _slugify(nome)
    slug = base
    n = 2
    while os.path.exists(_caminho(pasta, slug)):
        slug = "{}-{}".format(base, n)
        n += 1
    return slug


def _split(valor):
    if not valor:
        return []
    return [p.strip() for p in valor.split(SEP) if p.strip()]


def _carregar(pasta, slug):
    caminho = _caminho(pasta, slug)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _salvar(pasta, pop):
    os.makedirs(_dir_pops(pasta), exist_ok=True)
    caminho = _caminho(pasta, pop["slug"])
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(pop, f, ensure_ascii=False, indent=2)
    return caminho


def _todos(pasta):
    arquivos = sorted(glob.glob(os.path.join(_dir_pops(pasta), "*.json")))
    pops = []
    for a in arquivos:
        try:
            with open(a, encoding="utf-8") as f:
                pops.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    return pops


def _erro(msg):
    print("ERRO: " + msg)
    sys.exit(1)


# ---------------------------------------------------------------- renderização

def _render_pop(p):
    """desenha o POP como texto claro para a IA seguir (treinar/delegar) ou
    para o dono imprimir e entregar à equipe."""
    L = []
    nivel = (p.get("nivel") or "").strip()
    selo = {"alto": "  [crítico]", "medio": "  [importante]", "baixo": ""}.get(nivel, "")
    L.append("PROCEDIMENTO: {}{}".format(p["nome"], selo))
    L.append("(slug: {} · versão {})".format(p["slug"], p.get("versao", 1)))
    L.append("")
    if p.get("objetivo"):
        L.append("Para que serve: {}".format(p["objetivo"]))
    if p.get("quando"):
        L.append("Quando fazer: {}".format(p["quando"]))
    if p.get("responsavel"):
        L.append("Quem faz: {}".format(p["responsavel"]))
    ferr = p.get("ferramentas", [])
    if ferr:
        L.append("Ferramentas: " + ", ".join(ferr))
    entr = p.get("entradas", [])
    if entr:
        L.append("Precisa ter em mãos: " + ", ".join(entr))
    if p.get("saida"):
        L.append("Resultado esperado: {}".format(p["saida"]))
    passos = p.get("passos", [])
    if passos:
        L.append("")
        L.append("Passo a passo:")
        for i, s in enumerate(passos, 1):
            L.append("  {}. {}".format(i, s))
    dec = p.get("decisoes", [])
    if dec:
        L.append("")
        L.append("Decisões pelo caminho (se acontecer X, faça Y):")
        for d in dec:
            L.append("  - {}".format(d))
    qual = p.get("qualidade", [])
    if qual:
        L.append("")
        L.append("Como saber que ficou certo (confira tudo):")
        for q in qual:
            L.append("  [ ] {}".format(q))
    nf = p.get("nao_fazer", [])
    if nf:
        L.append("")
        L.append("NUNCA faça:")
        for n in nf:
            L.append("  - {}".format(n))
    if p.get("exemplo"):
        L.append("")
        L.append("Exemplo real:")
        L.append("  {}".format(p["exemplo"].replace("\n", "\n  ")))
    hist = p.get("historico", [])
    if hist:
        L.append("")
        L.append("Histórico de revisões:")
        for h in hist:
            L.append("  • {} — {}".format(h.get("data", "?"), h.get("nota", "")))
    L.append("")
    L.append("Usos registrados: {} | Último uso: {} | Atualizado em: {}".format(
        p.get("usos", 0), p.get("ultimo_uso") or "nunca", p.get("atualizado_em", "?")))
    return "\n".join(L)


# ---------------------------------------------------------------- comandos

def cmd_nova(args):
    pasta = args.pasta
    if not args.nome:
        _erro("o procedimento precisa de um --nome.")
    nivel = (args.nivel or "").strip().lower()
    if nivel and nivel not in ("baixo", "medio", "alto"):
        _erro('--nivel deve ser baixo, medio ou alto.')
    slug = _slug_unico(pasta, args.nome)
    pop = {
        "slug": slug,
        "nome": args.nome.strip(),
        "objetivo": (args.objetivo or "").strip(),
        "quando": (args.quando or "").strip(),
        "responsavel": (args.responsavel or "").strip(),
        "ferramentas": _split(args.ferramentas),
        "entradas": _split(args.entradas),
        "passos": _split(args.passos),
        "decisoes": _split(args.decisoes),
        "qualidade": _split(args.qualidade),
        "nao_fazer": _split(args.nao_fazer),
        "saida": (args.saida or "").strip(),
        "exemplo": (args.exemplo or "").strip(),
        "nivel": nivel,
        "versao": 1,
        "criado_em": _hoje(),
        "atualizado_em": _hoje(),
        "historico": [],
        "usos": 0,
        "ultimo_uso": "",
    }
    caminho = _salvar(pasta, pop)
    if args.formato == "json":
        print(json.dumps(pop, ensure_ascii=False, indent=2))
    else:
        print("Procedimento criado: {}  (slug: {})".format(pop["nome"], slug))
        print("Arquivo: {}".format(caminho))
    return slug


def cmd_listar(args):
    pops = _todos(args.pasta)
    if args.formato == "json":
        print(json.dumps(pops, ensure_ascii=False, indent=2))
        return
    if not pops:
        print("A cartilha ainda está vazia. Documente o primeiro processo com o modo Mapear.")
        return
    print("Sua cartilha tem {} procedimento(s):".format(len(pops)))
    print("")
    for p in pops:
        nivel = (p.get("nivel") or "").strip()
        selo = {"alto": " [crítico]", "medio": " [importante]", "baixo": ""}.get(nivel, "")
        npassos = len(p.get("passos", []))
        print("• {}{}  (slug: {} · v{})".format(p["nome"], selo, p["slug"], p.get("versao", 1)))
        if p.get("objetivo"):
            print("    {}".format(p["objetivo"]))
        print("    {} passo(s) · usos: {}".format(npassos, p.get("usos", 0)))


def cmd_ver(args, contar=False):
    p = _carregar(args.pasta, args.slug)
    if p is None:
        _erro('não encontrei o procedimento "{}". Use "listar" para ver os slugs.'.format(args.slug))
    if contar:
        p["usos"] = int(p.get("usos", 0)) + 1
        p["ultimo_uso"] = _hoje()
        _salvar(args.pasta, p)
    if args.formato == "json":
        print(json.dumps(p, ensure_ascii=False, indent=2))
    else:
        print(_render_pop(p))


def _aplicar_edicoes(p, args):
    mudou = []
    if args.nome:
        p["nome"] = args.nome.strip(); mudou.append("nome")
    if args.objetivo is not None:
        p["objetivo"] = args.objetivo.strip(); mudou.append("objetivo")
    if args.quando is not None:
        p["quando"] = args.quando.strip(); mudou.append("quando")
    if args.responsavel is not None:
        p["responsavel"] = args.responsavel.strip(); mudou.append("responsável")
    if args.ferramentas is not None:
        p["ferramentas"] = _split(args.ferramentas); mudou.append("ferramentas")
    if args.entradas is not None:
        p["entradas"] = _split(args.entradas); mudou.append("entradas")
    if args.passos is not None:
        p["passos"] = _split(args.passos); mudou.append("passos")
    if args.decisoes is not None:
        p["decisoes"] = _split(args.decisoes); mudou.append("decisões")
    if args.qualidade is not None:
        p["qualidade"] = _split(args.qualidade); mudou.append("qualidade")
    if args.nao_fazer is not None:
        p["nao_fazer"] = _split(args.nao_fazer); mudou.append("não-fazer")
    if args.saida is not None:
        p["saida"] = args.saida.strip(); mudou.append("saída")
    if args.exemplo is not None:
        p["exemplo"] = args.exemplo.strip(); mudou.append("exemplo")
    if getattr(args, "nivel", None):
        nivel = args.nivel.strip().lower()
        if nivel not in ("baixo", "medio", "alto"):
            _erro('--nivel deve ser baixo, medio ou alto.')
        p["nivel"] = nivel; mudou.append("nível")
    return mudou


def cmd_editar(args):
    p = _carregar(args.pasta, args.slug)
    if p is None:
        _erro('não encontrei o procedimento "{}".'.format(args.slug))
    mudou = _aplicar_edicoes(p, args)
    p["atualizado_em"] = _hoje()
    nota = (args.nota or "").strip()
    if nota or mudou:
        p.setdefault("historico", []).append({
            "data": _hoje(),
            "nota": nota or ("ajustes em: " + ", ".join(mudou) if mudou else "ajuste"),
        })
    _salvar(args.pasta, p)
    if args.formato == "json":
        print(json.dumps(p, ensure_ascii=False, indent=2))
    else:
        print("Procedimento atualizado: {}  (slug: {} · v{})".format(p["nome"], p["slug"], p.get("versao", 1)))
        if mudou:
            print("Mudou: " + ", ".join(mudou))


def cmd_revisar(args):
    """Sobe a versão do POP — use depois de uma melhoria real vinda do uso."""
    p = _carregar(args.pasta, args.slug)
    if p is None:
        _erro('não encontrei o procedimento "{}".'.format(args.slug))
    _aplicar_edicoes(p, args)
    p["versao"] = int(p.get("versao", 1)) + 1
    p["atualizado_em"] = _hoje()
    nota = (args.nota or "").strip() or "revisão"
    p.setdefault("historico", []).append({"data": _hoje(), "nota": nota})
    _salvar(args.pasta, p)
    if args.formato == "json":
        print(json.dumps(p, ensure_ascii=False, indent=2))
    else:
        print("Procedimento revisado: {} agora na versão {}.".format(p["nome"], p["versao"]))
        print("Anotado: {}".format(nota))


def cmd_remover(args):
    caminho = _caminho(args.pasta, args.slug)
    if not os.path.exists(caminho):
        _erro('não encontrei o procedimento "{}".'.format(args.slug))
    os.remove(caminho)
    print('Procedimento "{}" removido da cartilha.'.format(args.slug))


def cmd_stats(args):
    pops = _todos(args.pasta)
    total = len(pops)
    usos_total = sum(int(p.get("usos", 0)) for p in pops)
    criticos = [p for p in pops if (p.get("nivel") or "") == "alto"]
    sem_qualidade = [p for p in pops if not p.get("qualidade")]
    sem_uso = [p for p in pops if int(p.get("usos", 0)) == 0]
    mais_usados = sorted(pops, key=lambda p: int(p.get("usos", 0)), reverse=True)[:5]
    if args.formato == "json":
        print(json.dumps({
            "total": total,
            "usos_total": usos_total,
            "criticos": [p["slug"] for p in criticos],
            "sem_checklist_de_qualidade": [p["slug"] for p in sem_qualidade],
            "nunca_usados": [p["slug"] for p in sem_uso],
            "mais_usados": [{"slug": p["slug"], "nome": p["nome"], "usos": int(p.get("usos", 0))} for p in mais_usados],
        }, ensure_ascii=False, indent=2))
        return
    print("Painel da Cartilha")
    print("------------------")
    print("Procedimentos documentados: {}".format(total))
    print("Vezes que a cartilha foi usada: {}".format(usos_total))
    if criticos:
        print("Críticos (não pode falhar): {}".format(", ".join(p["nome"] for p in criticos)))
    if mais_usados and usos_total > 0:
        print("")
        print("Mais usados:")
        for p in mais_usados:
            if int(p.get("usos", 0)) > 0:
                print("  • {} — {} uso(s)".format(p["nome"], p.get("usos", 0)))
    if sem_qualidade:
        print("")
        print("Sem checklist de qualidade ({}): {}".format(
            len(sem_qualidade), ", ".join(p["nome"] for p in sem_qualidade)))
        print("  (vale a pena fechar esses — é o que garante que a equipe não erre)")
    if sem_uso:
        print("")
        print("Ainda não usados ({}): {}".format(
            len(sem_uso), ", ".join(p["nome"] for p in sem_uso)))


# ---------------------------------------------------------------- CLI

def _add_campos_edicao(sp, novos=False):
    """argumentos compartilhados por nova/editar/revisar."""
    req = novos
    sp.add_argument("--nome", required=req, default=None)
    sp.add_argument("--objetivo", default=None)
    sp.add_argument("--quando", default=None)
    sp.add_argument("--responsavel", default=None)
    sp.add_argument("--ferramentas", default=None)
    sp.add_argument("--entradas", default=None)
    sp.add_argument("--passos", default=None)
    sp.add_argument("--decisoes", default=None)
    sp.add_argument("--qualidade", default=None)
    sp.add_argument("--nao-fazer", dest="nao_fazer", default=None)
    sp.add_argument("--saida", default=None)
    sp.add_argument("--exemplo", default=None)
    sp.add_argument("--nivel", default=None)


def construir_parser():
    p = argparse.ArgumentParser(description="Cartilha — motor do manual de processos.")
    p.add_argument("--pasta", default=None, help="pasta de dados (padrão: raiz/.cartilha)")
    p.add_argument("--formato", default="texto", choices=["texto", "json"])
    sub = p.add_subparsers(dest="comando", required=True)

    n = sub.add_parser("nova", help="documenta um novo procedimento (POP)")
    _add_campos_edicao(n, novos=True)

    sub.add_parser("listar", help="lista todos os procedimentos")

    v = sub.add_parser("ver", help="mostra um procedimento")
    v.add_argument("--slug", required=True)

    u = sub.add_parser("usar", help="mostra um procedimento e conta +1 uso")
    u.add_argument("--slug", required=True)

    e = sub.add_parser("editar", help="edita um procedimento existente")
    e.add_argument("--slug", required=True)
    e.add_argument("--nota", default=None, help="o que mudou (vai pro histórico)")
    _add_campos_edicao(e, novos=False)

    r = sub.add_parser("revisar", help="sobe a versão após uma melhoria do uso real")
    r.add_argument("--slug", required=True)
    r.add_argument("--nota", default=None, help="o que melhorou nesta versão")
    _add_campos_edicao(r, novos=False)

    rm = sub.add_parser("remover", help="apaga um procedimento")
    rm.add_argument("--slug", required=True)

    sub.add_parser("stats", help="painel da cartilha")
    return p


def main(argv=None):
    args = construir_parser().parse_args(argv)
    if args.pasta is None:
        args.pasta = _pasta_padrao()
    if args.comando == "nova":
        cmd_nova(args)
    elif args.comando == "listar":
        cmd_listar(args)
    elif args.comando == "ver":
        cmd_ver(args, contar=False)
    elif args.comando == "usar":
        cmd_ver(args, contar=True)
    elif args.comando == "editar":
        cmd_editar(args)
    elif args.comando == "revisar":
        cmd_revisar(args)
    elif args.comando == "remover":
        cmd_remover(args)
    elif args.comando == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
