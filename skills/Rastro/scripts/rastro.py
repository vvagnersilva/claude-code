#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rastro — motor do diário de bugs (100% stdlib, offline, sem rede, sem chave).

A IA depura seguindo o método; este motor só faz a parte EXATA e persistente:
guardar cada bug resolvido (sintoma -> causa-raiz -> correção), recuperar
("já vi esse erro antes?") e mostrar o painel. Nada é inventado aqui: o motor
só registra o que a IA e o dono confirmaram.

Uso:
  python3 rastro.py registrar --titulo "..." --sintoma "..." --causa "..." \
      --correcao "..." --arquivos "a.py,b.js" --severidade P2 --status corrigido --tags "auth,token"
  python3 rastro.py buscar "token expira"
  python3 rastro.py listar [--status aberto|corrigido|verificado]
  python3 rastro.py ver 20260718-001
  python3 rastro.py status 20260718-001 verificado
  python3 rastro.py stats
  python3 rastro.py onde        # mostra onde a pasta .rastro foi ancorada
"""

import sys, os, csv, argparse, unicodedata, datetime, re

# ------------------------------------------------------------------ ancoragem
def achar_raiz():
    """Ancora .rastro/ na RAIZ do projeto, não dentro da pasta da skill.
    1) CLAUDE_PROJECT_DIR se existir; 2) sobe procurando .rastro/.git/.claude;
    3) diretório atual como último recurso."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return os.path.abspath(env)
    d = os.getcwd()
    while True:
        for marca in (".rastro", ".git", ".claude"):
            if os.path.isdir(os.path.join(d, marca)):
                return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return os.getcwd()

RAIZ = achar_raiz()
BASE = os.path.join(RAIZ, ".rastro")
DIARIO = os.path.join(BASE, "diario.csv")
CAMPOS = ["id", "data", "titulo", "severidade", "status",
          "sintoma", "causa_raiz", "correcao", "arquivos", "tags"]
STATUS_VALIDOS = ("aberto", "corrigido", "verificado")
SEV_VALIDAS = ("P0", "P1", "P2", "P3")

# ------------------------------------------------------------------ utilidades
def sem_acento(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()

STOP = set("de da do das dos e ou o a os as um uma no na nos nas em para por que com "
           "se ao aos the of to in is it a an and or not no".split())

def tokens(s):
    # mantém identificadores de código (camelCase, snake_case, file.ext) como pistas
    brutos = re.findall(r"[A-Za-z0-9_.:/]+", sem_acento(s))
    out = []
    for t in brutos:
        t = t.strip("._:/")
        if len(t) >= 2 and t not in STOP:
            out.append(t)
    return out

def garantir_base():
    os.makedirs(BASE, exist_ok=True)
    if not os.path.exists(DIARIO):
        with open(DIARIO, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CAMPOS).writeheader()

def ler():
    if not os.path.exists(DIARIO):
        return []
    with open(DIARIO, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]

def escrever(linhas):
    garantir_base()
    with open(DIARIO, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for r in linhas:
            w.writerow({k: r.get(k, "") for k in CAMPOS})

def novo_id(linhas):
    hoje = datetime.date.today().strftime("%Y%m%d")
    n = sum(1 for r in linhas if r.get("id", "").startswith(hoje)) + 1
    return f"{hoje}-{n:03d}"

def achar(linhas, id_):
    for r in linhas:
        if r.get("id") == id_:
            return r
    return None

# ------------------------------------------------------------------ comandos
def cmd_registrar(a):
    linhas = ler()
    sev = (a.severidade or "P2").upper()
    if sev not in SEV_VALIDAS:
        print(f"Severidade inválida: {sev}. Use uma de {', '.join(SEV_VALIDAS)}.")
        return 1
    status = (a.status or "corrigido").lower()
    if status not in STATUS_VALIDOS:
        print(f"Status inválido: {status}. Use um de {', '.join(STATUS_VALIDOS)}.")
        return 1
    reg = {
        "id": novo_id(linhas),
        "data": datetime.date.today().isoformat(),
        "titulo": (a.titulo or "").strip(),
        "severidade": sev,
        "status": status,
        "sintoma": (a.sintoma or "").strip(),
        "causa_raiz": (a.causa or "").strip(),
        "correcao": (a.correcao or "").strip(),
        "arquivos": (a.arquivos or "").strip(),
        "tags": (a.tags or "").strip(),
    }
    if not reg["titulo"]:
        print("Falta --titulo. Todo registro precisa de um título curto.")
        return 1
    linhas.append(reg)
    escrever(linhas)
    print(f"Registrado no diário: {reg['id']} — {reg['titulo']} [{sev}/{status}]")
    print(f"Diário: {DIARIO}")
    return 0

def _score(reg, termos):
    corpo = " ".join([reg.get("titulo", ""), reg.get("sintoma", ""),
                      reg.get("causa_raiz", ""), reg.get("tags", ""),
                      reg.get("arquivos", "")])
    tset = set(tokens(corpo))
    if not tset or not termos:
        return 0.0
    comuns = sum(1 for t in termos if t in tset)
    return comuns / len(termos)

def cmd_buscar(a):
    linhas = ler()
    if not linhas:
        print("Diário vazio ainda. Nenhum bug registrado — nada para recuperar.")
        return 0
    termos = tokens(" ".join(a.termo))
    if not termos:
        print("Diga o que procurar. Ex.: buscar \"token expira\"")
        return 1
    marcados = []
    for r in linhas:
        s = _score(r, termos)
        if s > 0:
            marcados.append((s, r))
    marcados.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    if not marcados:
        print("Nada parecido no diário. Provavelmente é um bug NOVO — investigue do zero.")
        return 0
    forte = [m for m in marcados if m[0] >= 0.5]
    usar = forte if forte else marcados[:3]
    rot = "JÁ VI ALGO PARECIDO — confira antes de investigar do zero:" if forte \
          else "Talvez relacionado (confiança baixa — confirme):"
    print(rot + "\n")
    for s, r in usar:
        print(f"  [{r['id']}] {r['titulo']}  ({int(s*100)}% de sobreposição, {r['severidade']}/{r['status']})")
        if r.get("causa_raiz"):
            print(f"       causa-raiz: {r['causa_raiz']}")
        if r.get("correcao"):
            print(f"       correção:   {r['correcao']}")
        print()
    return 0

def cmd_listar(a):
    linhas = ler()
    if a.status:
        linhas = [r for r in linhas if r.get("status") == a.status.lower()]
    if not linhas:
        print("Nenhum bug no diário para esse filtro.")
        return 0
    for r in sorted(linhas, key=lambda x: x.get("id", ""), reverse=True):
        print(f"  [{r['id']}] {r['severidade']}/{r['status']:<11} {r['titulo']}")
    print(f"\n  {len(linhas)} bug(s).  Diário: {DIARIO}")
    return 0

def cmd_ver(a):
    reg = achar(ler(), a.id)
    if not reg:
        print(f"Não achei o id {a.id}. Use 'listar' para ver os ids.")
        return 1
    print(f"# {reg['id']} — {reg['titulo']}")
    print(f"- Data: {reg['data']}   Severidade: {reg['severidade']}   Status: {reg['status']}")
    print(f"- Sintoma:    {reg.get('sintoma','') or '—'}")
    print(f"- Causa-raiz: {reg.get('causa_raiz','') or '—'}")
    print(f"- Correção:   {reg.get('correcao','') or '—'}")
    print(f"- Arquivos:   {reg.get('arquivos','') or '—'}")
    print(f"- Tags:       {reg.get('tags','') or '—'}")
    return 0

def cmd_status(a):
    novo = a.novo_status.lower()
    if novo not in STATUS_VALIDOS:
        print(f"Status inválido: {novo}. Use um de {', '.join(STATUS_VALIDOS)}.")
        return 1
    linhas = ler()
    reg = achar(linhas, a.id)
    if not reg:
        print(f"Não achei o id {a.id}.")
        return 1
    reg["status"] = novo
    escrever(linhas)
    print(f"{a.id} agora está: {novo}")
    return 0

def cmd_stats(a):
    linhas = ler()
    if not linhas:
        print("Diário vazio. Registre o primeiro bug resolvido com 'registrar'.")
        return 0
    por_sev = {}
    por_status = {}
    for r in linhas:
        por_sev[r.get("severidade", "?")] = por_sev.get(r.get("severidade", "?"), 0) + 1
        por_status[r.get("status", "?")] = por_status.get(r.get("status", "?"), 0) + 1
    # recorrência por tag e por arquivo (sinal de dívida técnica)
    contagem_tag = {}
    contagem_arq = {}
    for r in linhas:
        for t in [x.strip() for x in r.get("tags", "").split(",") if x.strip()]:
            contagem_tag[t] = contagem_tag.get(t, 0) + 1
        for f in [x.strip() for x in r.get("arquivos", "").split(",") if x.strip()]:
            contagem_arq[f] = contagem_arq.get(f, 0) + 1
    print(f"# Painel do Rastro  —  {len(linhas)} bug(s) no diário\n")
    print("Por severidade: " + "  ".join(f"{k}:{v}" for k, v in sorted(por_sev.items())))
    print("Por status:     " + "  ".join(f"{k}:{v}" for k, v in sorted(por_status.items())))
    recor_tag = sorted([kv for kv in contagem_tag.items() if kv[1] >= 2], key=lambda x: -x[1])
    recor_arq = sorted([kv for kv in contagem_arq.items() if kv[1] >= 2], key=lambda x: -x[1])
    if recor_tag:
        print("\nAssuntos recorrentes (>=2 bugs) — candidatos a causa estrutural:")
        for k, v in recor_tag[:8]:
            print(f"  - {k}: {v} bugs")
    if recor_arq:
        print("\nArquivos que mais quebram (>=2 bugs) — foco de refatoração:")
        for k, v in recor_arq[:8]:
            print(f"  - {k}: {v} bugs")
    return 0

def cmd_onde(a):
    print(f"Raiz do projeto detectada: {RAIZ}")
    print(f"Pasta de dados:            {BASE}")
    print(f"Diário:                    {DIARIO}")
    print(f"Existe? {'sim' if os.path.exists(DIARIO) else 'ainda não (será criado no 1º registro)'}")
    return 0

# ------------------------------------------------------------------ CLI
def main():
    p = argparse.ArgumentParser(prog="rastro", description="Diário de bugs do Rastro (offline).")
    sub = p.add_subparsers(dest="cmd")

    r = sub.add_parser("registrar", help="registra um bug resolvido no diário")
    r.add_argument("--titulo", required=True)
    r.add_argument("--severidade", default="P2")
    r.add_argument("--status", default="corrigido")
    r.add_argument("--sintoma", default="")
    r.add_argument("--causa", default="")
    r.add_argument("--correcao", default="")
    r.add_argument("--arquivos", default="")
    r.add_argument("--tags", default="")
    r.set_defaults(func=cmd_registrar)

    b = sub.add_parser("buscar", help="'já vi esse erro antes?' — recupera bugs parecidos")
    b.add_argument("termo", nargs="+")
    b.set_defaults(func=cmd_buscar)

    l = sub.add_parser("listar", help="lista os bugs do diário")
    l.add_argument("--status", default="")
    l.set_defaults(func=cmd_listar)

    v = sub.add_parser("ver", help="mostra um bug inteiro")
    v.add_argument("id")
    v.set_defaults(func=cmd_ver)

    s = sub.add_parser("status", help="muda o status de um bug")
    s.add_argument("id")
    s.add_argument("novo_status")
    s.set_defaults(func=cmd_status)

    st = sub.add_parser("stats", help="painel do diário")
    st.set_defaults(func=cmd_stats)

    o = sub.add_parser("onde", help="mostra onde a pasta .rastro foi ancorada")
    o.set_defaults(func=cmd_onde)

    a = p.parse_args()
    if not getattr(a, "cmd", None):
        p.print_help()
        return 0
    return a.func(a)

if __name__ == "__main__":
    sys.exit(main())
