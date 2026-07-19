#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fichário — motor do segundo cérebro pessoal (somente biblioteca padrão).

Guarda cada ideia como um CARTÃO em .fichario/cartoes/<id>.md (markdown com
cabeçalho simples). A IA conversa, atomiza e responde; este motor só faz a parte
exata: gravar, ligar por sobreposição de palavras, buscar com porta de confiança,
listar, revisar/destilar e dar o painel. Nunca inventa nada.

Uso (a IA traduz a conversa nestes comandos):
  guardar  --titulo "..." [--tags "a,b"] [--fonte "..."]   (corpo vem por stdin)
  buscar   "consulta" [--n 5]
  ligar    --id <id>                       (sugere cartões parecidos)
  conectar --de <id> --para <id>           (cria ligação nos dois sentidos)
  listar   [--tag X] [--limite N] [--busca "texto"]
  ver      --id <id>
  orfaos
  revisar  [--dias 30]                     (cartões esquecidos + possíveis duplicados)
  revisado --id <id>                       (marca como revisado hoje)
  mapa     [--tag X]
  stats
  remover  --id <id>
  editar   --id <id> [--titulo ...] [--tags ...] [--fonte ...] [--corpo-stdin]

Dados 100% locais. Sem rede, sem dependências externas.
"""
import sys, os, re, csv, json, argparse, unicodedata, datetime

# ----------------------------------------------------------------------------
# Localização da raiz do projeto (.fichario na raiz, não dentro da skill)
# ----------------------------------------------------------------------------
def achar_raiz():
    # 1) variável do Claude Code
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    # 2) sobe procurando uma pasta .fichario já existente
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".fichario")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    # 3) sobe procurando uma pasta .claude (raiz típica de projeto)
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".claude")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    # 4) fallback: diretório atual
    return os.getcwd()

RAIZ = achar_raiz()
BASE = os.path.join(RAIZ, ".fichario")
CARTOES = os.path.join(BASE, "cartoes")

def garantir_dirs():
    os.makedirs(CARTOES, exist_ok=True)

HOJE = datetime.date.today()

# ----------------------------------------------------------------------------
# Texto: normalização e tokens (PT-BR, sem acento, sem stopwords)
# ----------------------------------------------------------------------------
STOP = set("""a o e de da do das dos em no na nos nas um uma uns umas para por com sem que
se ao aos as os à às e ou mas como quando onde qual quais quem cujo cuja este esta isto esse
essa isso aquele aquela aquilo meu minha seu sua nosso nossa eu voce ele ela nos eles elas
ja nao sim muito mais menos tambem entao porque pois entre sobre apos ate desde tem ser estar
foi era sao está estão fazer faz feito ter ha haja são pra pro vou vai ir la aqui isso tudo
todo toda todos todas cada algum alguma nenhum nenhuma outro outra coisa coisas""".split())

def fold(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()

def tokens(texto):
    base = fold(texto or "")
    crus = re.findall(r"[a-z0-9]{3,}", base)
    return [t for t in crus if t not in STOP]

def conjunto_tokens(texto):
    return set(tokens(texto))

# ----------------------------------------------------------------------------
# Cartão: ler / escrever (markdown com cabeçalho de chaves simples)
# ----------------------------------------------------------------------------
# Formato do arquivo .fichario/cartoes/<id>.md:
#   ---
#   id: 20260627-001
#   titulo: ...
#   tags: produtividade, ia
#   fonte: ...
#   criado: 2026-06-27
#   revisado: 2026-06-27
#   ligacoes: 20260626-003, 20260627-002
#   ---
#   <corpo do cartão>

def caminho(cid):
    return os.path.join(CARTOES, cid + ".md")

def ler_cartao(cid):
    p = caminho(cid)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    meta = {"id": cid, "titulo": "", "tags": [], "fonte": "",
            "criado": "", "revisado": "", "ligacoes": [], "corpo": ""}
    if txt.startswith("---"):
        partes = txt.split("---", 2)
        cab = partes[1] if len(partes) >= 3 else ""
        corpo = partes[2] if len(partes) >= 3 else ""
        for linha in cab.splitlines():
            if ":" not in linha:
                continue
            k, v = linha.split(":", 1)
            k = k.strip().lower(); v = v.strip()
            if k == "tags":
                meta["tags"] = [x.strip() for x in v.split(",") if x.strip()]
            elif k == "ligacoes":
                meta["ligacoes"] = [x.strip() for x in v.split(",") if x.strip()]
            elif k in meta:
                meta[k] = v
        meta["corpo"] = corpo.strip()
    else:
        meta["corpo"] = txt.strip()
    return meta

def escrever_cartao(m):
    garantir_dirs()
    cab = ["---",
           f"id: {m['id']}",
           f"titulo: {m.get('titulo','')}",
           f"tags: {', '.join(m.get('tags',[]))}",
           f"fonte: {m.get('fonte','')}",
           f"criado: {m.get('criado','')}",
           f"revisado: {m.get('revisado','')}",
           f"ligacoes: {', '.join(m.get('ligacoes',[]))}",
           "---", ""]
    with open(caminho(m["id"]), "w", encoding="utf-8") as f:
        f.write("\n".join(cab))
        f.write((m.get("corpo","") or "").strip() + "\n")

def todos_ids():
    if not os.path.isdir(CARTOES):
        return []
    ids = [f[:-3] for f in os.listdir(CARTOES) if f.endswith(".md")]
    return sorted(ids)

def todos_cartoes():
    return [ler_cartao(c) for c in todos_ids()]

def novo_id():
    pref = HOJE.strftime("%Y%m%d")
    n = 1
    existentes = [c for c in todos_ids() if c.startswith(pref)]
    if existentes:
        nums = []
        for c in existentes:
            m = re.search(r"-(\d+)$", c)
            if m:
                nums.append(int(m.group(1)))
        n = (max(nums) + 1) if nums else (len(existentes) + 1)
    return f"{pref}-{n:03d}"

# ----------------------------------------------------------------------------
# Similaridade por sobreposição de palavras
# ----------------------------------------------------------------------------
def texto_cartao(m):
    return " ".join([m.get("titulo",""), " ".join(m.get("tags",[])), m.get("corpo","")])

def pontuar(consulta_tokens, m):
    ct = conjunto_tokens(texto_cartao(m))
    if not ct or not consulta_tokens:
        return 0.0, 0
    comuns = consulta_tokens & ct
    if not comuns:
        return 0.0, 0
    # peso extra se a sobreposição cai no título
    titulo_tok = conjunto_tokens(m.get("titulo",""))
    bonus = len(comuns & titulo_tok) * 0.5
    score = (len(comuns) + bonus) / (len(consulta_tokens) ** 0.5)
    return score, len(comuns)

# ----------------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------------
def cmd_guardar(a):
    corpo = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    if a.corpo:
        corpo = a.corpo.strip()
    if not corpo and not a.titulo:
        print("ERRO: o cartão precisa de um título (--titulo) e de um corpo (por stdin)."); return 1
    cid = novo_id()
    tags = [t.strip() for t in (a.tags or "").split(",") if t.strip()]
    m = {"id": cid, "titulo": (a.titulo or "").strip(), "tags": tags,
         "fonte": (a.fonte or "").strip(),
         "criado": HOJE.isoformat(), "revisado": HOJE.isoformat(),
         "ligacoes": [], "corpo": corpo}
    # sugerir ligações automáticas
    ctok = conjunto_tokens(texto_cartao(m))
    sug = []
    for outro in todos_cartoes():
        sc, comuns = pontuar(ctok, outro)
        if comuns >= 2 and sc >= 0.8:
            sug.append((sc, outro["id"], outro["titulo"]))
    sug.sort(reverse=True)
    # liga automaticamente aos 3 melhores (bidirecional)
    ligados = []
    for sc, oid, otit in sug[:3]:
        m["ligacoes"].append(oid)
        om = ler_cartao(oid)
        if om and cid not in om["ligacoes"]:
            om["ligacoes"].append(cid)
            escrever_cartao(om)
        ligados.append((oid, otit))
    escrever_cartao(m)
    print(f"OK cartão guardado: {cid}")
    print(f"Título: {m['titulo']}")
    if tags: print(f"Tags: {', '.join(tags)}")
    if ligados:
        print("Liguei automaticamente a cartões parecidos:")
        for oid, otit in ligados:
            print(f"  - {oid}  {otit}")
    else:
        print("Nenhum cartão parecido ainda — as ligações crescem com o tempo.")
    return 0

def cmd_buscar(a):
    cs = conjunto_tokens(a.consulta)
    if not cs:
        print("ERRO: digite uma consulta com palavras de busca."); return 1
    res = []
    for m in todos_cartoes():
        sc, comuns = pontuar(cs, m)
        if comuns >= 1:
            res.append((sc, comuns, m))
    res.sort(key=lambda x: x[0], reverse=True)
    if not res:
        print("NADA_ENCONTRADO: não há cartão no seu fichário sobre isso.")
        return 0
    forte = [r for r in res if r[0] >= 1.0 and r[1] >= 2]
    usar = (forte or res)[: a.n]
    if not forte:
        print("CONFIANCA_BAIXA: nada bate bem; mostro o mais próximo (pode não responder de fato).")
    for sc, comuns, m in usar:
        print(f"\n[{m['id']}] {m['titulo']}   (relevância {sc:.2f})")
        if m["tags"]: print(f"  tags: {', '.join(m['tags'])}")
        corpo = m["corpo"].replace("\n", " ")
        print(f"  {corpo[:280]}")
        if m["fonte"]: print(f"  fonte: {m['fonte']}")
        if m["ligacoes"]: print(f"  ligado a: {', '.join(m['ligacoes'])}")
    return 0

def cmd_ligar(a):
    base = ler_cartao(a.id)
    if not base:
        print(f"ERRO: cartão {a.id} não existe."); return 1
    ctok = conjunto_tokens(texto_cartao(base))
    res = []
    for m in todos_cartoes():
        if m["id"] == a.id or m["id"] in base["ligacoes"]:
            continue
        sc, comuns = pontuar(ctok, m)
        if comuns >= 2:
            res.append((sc, m))
    res.sort(key=lambda x: x[0], reverse=True)
    print(f"Cartão base: [{base['id']}] {base['titulo']}")
    if not res:
        print("Nenhum cartão parecido ainda não ligado.")
        return 0
    print("Cartões parecidos que você pode conectar:")
    for sc, m in res[:6]:
        print(f"  [{m['id']}] {m['titulo']}   (parecido {sc:.2f})")
    print("Para conectar: fichario.py conectar --de", a.id, "--para <id>")
    return 0

def cmd_conectar(a):
    de = ler_cartao(a.de); para = ler_cartao(a.para)
    if not de or not para:
        print("ERRO: um dos cartões não existe."); return 1
    mudou = False
    if a.para not in de["ligacoes"]:
        de["ligacoes"].append(a.para); escrever_cartao(de); mudou = True
    if a.de not in para["ligacoes"]:
        para["ligacoes"].append(a.de); escrever_cartao(para); mudou = True
    print("OK conectados" if mudou else "Já estavam conectados", f": {a.de} <-> {a.para}")
    return 0

def cmd_listar(a):
    cards = todos_cartoes()
    if a.tag:
        tf = fold(a.tag)
        cards = [m for m in cards if any(fold(t) == tf for t in m["tags"])]
    if a.busca:
        cs = conjunto_tokens(a.busca)
        cards = [m for m in cards if conjunto_tokens(texto_cartao(m)) & cs]
    cards.sort(key=lambda m: m["id"], reverse=True)
    if a.limite:
        cards = cards[: a.limite]
    if not cards:
        print("Nenhum cartão encontrado com esse filtro."); return 0
    print(f"{len(cards)} cartão(ões):")
    for m in cards:
        tg = f"  #{' #'.join(m['tags'])}" if m["tags"] else ""
        print(f"  [{m['id']}] {m['titulo']}{tg}")
    return 0

def cmd_ver(a):
    m = ler_cartao(a.id)
    if not m:
        print(f"ERRO: cartão {a.id} não existe."); return 1
    print(f"[{m['id']}] {m['titulo']}")
    print(f"tags: {', '.join(m['tags']) or '-'}")
    print(f"fonte: {m['fonte'] or '-'}")
    print(f"criado: {m['criado']}   revisado: {m['revisado']}")
    print(f"ligado a: {', '.join(m['ligacoes']) or '-'}")
    print("-" * 40)
    print(m["corpo"])
    return 0

def cmd_orfaos(a):
    orf = [m for m in todos_cartoes() if not m["ligacoes"]]
    if not orf:
        print("Nenhum cartão órfão — tudo está conectado a algo. 👏"); return 0
    print(f"{len(orf)} cartão(ões) sem nenhuma ligação (vale conectar a outros):")
    for m in orf:
        print(f"  [{m['id']}] {m['titulo']}")
    return 0

def dias_desde(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return (HOJE - d).days
    except Exception:
        return 9999

def cmd_revisar(a):
    cards = todos_cartoes()
    if not cards:
        print("Seu fichário ainda está vazio."); return 0
    limite = a.dias
    esquecidos = [(dias_desde(m["revisado"]), m) for m in cards
                  if dias_desde(m["revisado"]) >= limite]
    esquecidos.sort(key=lambda x: x[0], reverse=True)
    print(f"== Destilar o fichário (o que ainda é verdade?) ==")
    if esquecidos:
        print(f"\nCartões não revisados há {limite}+ dias ({len(esquecidos)}):")
        for d, m in esquecidos[:12]:
            print(f"  [{m['id']}] {m['titulo']}  (há {d} dias)")
    else:
        print(f"\nNenhum cartão esquecido há {limite}+ dias. 👏")
    # possíveis duplicados: pares com alta sobreposição
    dups = []
    for i in range(len(cards)):
        ti = conjunto_tokens(texto_cartao(cards[i]))
        for j in range(i + 1, len(cards)):
            tj = conjunto_tokens(texto_cartao(cards[j]))
            if not ti or not tj:
                continue
            comuns = ti & tj
            uniao = ti | tj
            jac = len(comuns) / len(uniao) if uniao else 0
            if jac >= 0.5 and len(comuns) >= 3:
                dups.append((jac, cards[i], cards[j]))
    dups.sort(key=lambda x: x[0], reverse=True)
    if dups:
        print(f"\nPossíveis cartões repetidos (talvez fundir num só, mais afiado):")
        for jac, a1, a2 in dups[:8]:
            print(f"  {int(jac*100)}% parecidos: [{a1['id']}] {a1['titulo']}  ~  [{a2['id']}] {a2['titulo']}")
    else:
        print("\nNenhum cartão claramente repetido.")
    print("\nDica: ao revisar um cartão, rode  fichario.py revisado --id <id>")
    return 0

def cmd_revisado(a):
    m = ler_cartao(a.id)
    if not m:
        print(f"ERRO: cartão {a.id} não existe."); return 1
    m["revisado"] = HOJE.isoformat()
    escrever_cartao(m)
    print(f"OK [{a.id}] marcado como revisado hoje.")
    return 0

def cmd_mapa(a):
    cards = todos_cartoes()
    if not cards:
        print("Seu fichário ainda está vazio."); return 0
    if a.tag:
        tf = fold(a.tag)
        sel = [m for m in cards if any(fold(t) == tf for t in m["tags"])]
        print(f"== Mapa do assunto: {a.tag} ({len(sel)} cartões) ==")
        for m in sel:
            print(f"  [{m['id']}] {m['titulo']}")
            for lid in m["ligacoes"]:
                om = ler_cartao(lid)
                if om:
                    print(f"      ↳ {om['titulo']}")
        return 0
    # mapa geral: tags com contagem
    contagem = {}
    for m in cards:
        for t in m["tags"]:
            contagem[t] = contagem.get(t, 0) + 1
    print(f"== Mapa geral do fichário ({len(cards)} cartões) ==")
    if contagem:
        print("Assuntos (tags) por tamanho:")
        for t, n in sorted(contagem.items(), key=lambda x: -x[1]):
            print(f"  #{t}: {n} cartão(ões)")
    sem = [m for m in cards if not m["tags"]]
    if sem:
        print(f"Sem tag: {len(sem)} cartão(ões)")
    print("\nDica: fichario.py mapa --tag <assunto>  para abrir um assunto.")
    return 0

def cmd_stats(a):
    cards = todos_cartoes()
    n = len(cards)
    print("== Painel do Fichário ==")
    print(f"Cartões: {n}")
    if n == 0:
        print("Comece guardando sua primeira ideia.")
        return 0
    contagem = {}
    for m in cards:
        for t in m["tags"]:
            contagem[t] = contagem.get(t, 0) + 1
    orf = sum(1 for m in cards if not m["ligacoes"])
    rev = sum(1 for m in cards if dias_desde(m["revisado"]) >= 30)
    lig = sum(len(m["ligacoes"]) for m in cards) // 2
    ids = sorted(m["id"] for m in cards)
    print(f"Ligações entre cartões: {lig}")
    print(f"Cartões órfãos (sem ligação): {orf}")
    print(f"Para revisar (30+ dias): {rev}")
    print(f"Assuntos diferentes: {len(contagem)}")
    if contagem:
        top = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        print("Top assuntos: " + ", ".join(f"#{t}({c})" for t, c in top))
    print(f"Mais antigo: {ids[0]}   mais novo: {ids[-1]}")
    return 0

def cmd_remover(a):
    m = ler_cartao(a.id)
    if not m:
        print(f"ERRO: cartão {a.id} não existe."); return 1
    # tira as ligações dos vizinhos
    for lid in m["ligacoes"]:
        om = ler_cartao(lid)
        if om and a.id in om["ligacoes"]:
            om["ligacoes"].remove(a.id); escrever_cartao(om)
    os.remove(caminho(a.id))
    print(f"OK cartão {a.id} removido.")
    return 0

def cmd_editar(a):
    m = ler_cartao(a.id)
    if not m:
        print(f"ERRO: cartão {a.id} não existe."); return 1
    if a.titulo is not None: m["titulo"] = a.titulo.strip()
    if a.tags is not None:
        m["tags"] = [t.strip() for t in a.tags.split(",") if t.strip()]
    if a.fonte is not None: m["fonte"] = a.fonte.strip()
    if a.corpo_stdin:
        novo = sys.stdin.read().strip()
        if novo: m["corpo"] = novo
    escrever_cartao(m)
    print(f"OK cartão {a.id} atualizado.")
    return 0

# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Fichário — motor do segundo cérebro pessoal")
    sub = p.add_subparsers(dest="cmd")

    g = sub.add_parser("guardar"); g.add_argument("--titulo", required=True)
    g.add_argument("--tags", default=""); g.add_argument("--fonte", default="")
    g.add_argument("--corpo", default="")

    b = sub.add_parser("buscar"); b.add_argument("consulta"); b.add_argument("--n", type=int, default=5)

    l = sub.add_parser("ligar"); l.add_argument("--id", required=True)
    c = sub.add_parser("conectar"); c.add_argument("--de", required=True); c.add_argument("--para", required=True)

    ls = sub.add_parser("listar"); ls.add_argument("--tag"); ls.add_argument("--limite", type=int)
    ls.add_argument("--busca")

    v = sub.add_parser("ver"); v.add_argument("--id", required=True)
    sub.add_parser("orfaos")

    r = sub.add_parser("revisar"); r.add_argument("--dias", type=int, default=30)
    rv = sub.add_parser("revisado"); rv.add_argument("--id", required=True)

    mp = sub.add_parser("mapa"); mp.add_argument("--tag")
    sub.add_parser("stats")

    rm = sub.add_parser("remover"); rm.add_argument("--id", required=True)

    e = sub.add_parser("editar"); e.add_argument("--id", required=True)
    e.add_argument("--titulo"); e.add_argument("--tags"); e.add_argument("--fonte")
    e.add_argument("--corpo-stdin", dest="corpo_stdin", action="store_true")

    a = p.parse_args()
    if not a.cmd:
        p.print_help(); return 0
    fn = {
        "guardar": cmd_guardar, "buscar": cmd_buscar, "ligar": cmd_ligar,
        "conectar": cmd_conectar, "listar": cmd_listar, "ver": cmd_ver,
        "orfaos": cmd_orfaos, "revisar": cmd_revisar, "revisado": cmd_revisado,
        "mapa": cmd_mapa, "stats": cmd_stats, "remover": cmd_remover, "editar": cmd_editar,
    }[a.cmd]
    return fn(a)

if __name__ == "__main__":
    sys.exit(main())
