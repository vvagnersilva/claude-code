#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alambique — motor do destilador de conteúdo (somente biblioteca padrão).

O dono entrega conteúdo longo (transcrição de vídeo, podcast, aula, artigo, PDF).
A IA DESTILA em material de estudo (resumo, conceitos, como aplicar, ações) e
gera cartões de revisão. Este motor faz só a parte exata: guardar o estudo,
guardar/agendar os cartões pela curva de revisão espaçada (SM-2), dizer quais
cartões vencem hoje, reagendar conforme o acerto, buscar no histórico e dar o
painel. Também tenta puxar as legendas de um vídeo do YouTube (se o yt-dlp
estiver instalado) — e, se não estiver, avisa em bom português e segue com texto.

A IA conversa, resume e pensa; o motor guarda e calcula. Nunca inventa nada.
Dados 100% locais em .alambique/ (na raiz do projeto do dono). Sem rede própria.

Uso (a IA traduz a conversa nestes comandos):
  salvar-estudo   --titulo "..." [--fonte "..."] [--tipo video|podcast|aula|artigo|pdf|outro] [--tags "a,b"]
                  (o corpo destilado vem por stdin)
  listar-estudos  [--busca "texto"] [--tag X] [--limite N]
  ver-estudo      --id <id>
  remover-estudo  --id <id>
  add-cartao      --estudo <id> --pergunta "..." --resposta "..."
  add-cartoes     --estudo <id>            (várias linhas por stdin: pergunta|||resposta)
  revisar         [--n N] [--mostrar]      (cartões que vencem hoje ou antes)
  ver-cartao      --id <cid>
  nota            --id <cid> --nota errei|dificil|bom|facil
  buscar          "consulta" [--n 5]
  stats
  legendas        "<url do youtube>" [--lang pt,en]

Notas de revisão (PT-BR) → qualidade SM-2: errei=2 (recomeça), dificil=3, bom=4, facil=5.
"""
import sys, os, re, csv, json, argparse, unicodedata, datetime, shutil, subprocess, tempfile, glob

# ----------------------------------------------------------------------------
# Raiz do projeto (.alambique na raiz do dono, não dentro da skill)
# ----------------------------------------------------------------------------
def achar_raiz():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".alambique")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, ".claude")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return os.getcwd()

RAIZ = achar_raiz()
BASE = os.path.join(RAIZ, ".alambique")
ESTUDOS = os.path.join(BASE, "estudos")
CARTOES_CSV = os.path.join(BASE, "cartoes.csv")

def garantir_dirs():
    os.makedirs(ESTUDOS, exist_ok=True)

HOJE = datetime.date.today()
CAMPOS = ["id", "estudo_id", "pergunta", "resposta", "ef", "n", "intervalo",
          "proxima_revisao", "acertos", "erros", "criado", "ultima_revisao"]

# ----------------------------------------------------------------------------
# Texto: normalização e tokens (PT-BR, sem acento, sem stopwords)
# ----------------------------------------------------------------------------
STOP = set("""a o e de da do das dos em no na nos nas um uma uns umas para por com sem que
se ao aos as os à às ou mas como quando onde qual quais quem cujo cuja este esta isto esse
essa isso aquele aquela aquilo meu minha seu sua nosso nossa eu voce ele ela nos eles elas
ja nao sim muito mais menos tambem entao porque pois entre sobre apos ate desde tem ser estar
foi era sao esta estao fazer faz feito ter ha haja pra pro vou vai ir la aqui tudo todo toda
todos todas cada algum alguma nenhum nenhuma outro outra coisa coisas""".split())

def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def tokens(texto):
    return [t for t in re.findall(r"[a-z0-9]+", fold(texto)) if len(t) > 2 and t not in STOP]

def conjunto_tokens(texto):
    return set(tokens(texto))

# ----------------------------------------------------------------------------
# Estudos (um arquivo markdown por estudo)
# ----------------------------------------------------------------------------
def caminho_estudo(eid):
    return os.path.join(ESTUDOS, eid + ".md")

def novo_id_estudo():
    pref = HOJE.strftime("%Y%m%d")
    n = 1
    while os.path.exists(caminho_estudo(f"{pref}-{n:03d}")):
        n += 1
    return f"{pref}-{n:03d}"

def escrever_estudo(m, corpo):
    with open(caminho_estudo(m["id"]), "w", encoding="utf-8") as f:
        f.write("---\n")
        for k in ["id", "titulo", "fonte", "tipo", "tags", "criado"]:
            f.write(f"{k}: {m.get(k,'')}\n")
        f.write("---\n\n")
        f.write(corpo.rstrip() + "\n")

def ler_estudo(eid):
    p = caminho_estudo(eid)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    meta = {"id": eid, "titulo": "", "fonte": "", "tipo": "", "tags": "", "criado": ""}
    corpo = txt
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", txt, re.DOTALL)
    if m:
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                if k.strip() in meta:
                    meta[k.strip()] = v.strip()
        corpo = m.group(2)
    meta["corpo"] = corpo.strip()
    return meta

def todos_estudos():
    out = []
    for p in sorted(glob.glob(os.path.join(ESTUDOS, "*.md"))):
        eid = os.path.splitext(os.path.basename(p))[0]
        e = ler_estudo(eid)
        if e:
            out.append(e)
    return out

# ----------------------------------------------------------------------------
# Cartões (CSV com estado da revisão espaçada)
# ----------------------------------------------------------------------------
def ler_cartoes():
    if not os.path.exists(CARTOES_CSV):
        return []
    with open(CARTOES_CSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def escrever_cartoes(linhas):
    garantir_dirs()
    with open(CARTOES_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for l in linhas:
            w.writerow({k: l.get(k, "") for k in CAMPOS})

def novo_id_cartao(linhas):
    m = 0
    for l in linhas:
        try:
            m = max(m, int(l["id"]))
        except (ValueError, KeyError):
            pass
    return str(m + 1)

def parse_data(s):
    try:
        return datetime.date.fromisoformat(s)
    except (ValueError, TypeError):
        return HOJE

# ----------------------------------------------------------------------------
# SM-2: agenda a próxima revisão a partir da qualidade da resposta
# ----------------------------------------------------------------------------
NOTA_QUALIDADE = {"errei": 2, "dificil": 3, "difícil": 3, "bom": 4, "facil": 5, "fácil": 5}

def aplicar_sm2(cartao, nota):
    q = NOTA_QUALIDADE.get(fold(nota), 4)
    ef = float(cartao.get("ef") or 2.5)
    n = int(cartao.get("n") or 0)
    if q < 3:
        # errou: volta pro começo, revê amanhã, e o cartão fica um tico mais "difícil"
        n = 0
        intervalo = 1
        ef = max(1.3, ef - 0.2)
        cartao["erros"] = str(int(cartao.get("erros") or 0) + 1)
    else:
        if n == 0:
            intervalo = 1
        elif n == 1:
            intervalo = 6
        else:
            intervalo = int(round(int(cartao.get("intervalo") or 1) * ef))
        n += 1
        ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        ef = max(1.3, ef)
        cartao["acertos"] = str(int(cartao.get("acertos") or 0) + 1)
    cartao["ef"] = f"{ef:.2f}"
    cartao["n"] = str(n)
    cartao["intervalo"] = str(intervalo)
    cartao["proxima_revisao"] = (HOJE + datetime.timedelta(days=intervalo)).isoformat()
    cartao["ultima_revisao"] = HOJE.isoformat()
    return intervalo

# ----------------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------------
def cmd_salvar_estudo(a):
    garantir_dirs()
    corpo = sys.stdin.read()
    if not corpo.strip():
        print("ERRO: o corpo destilado do estudo veio vazio (passe por stdin).")
        return 1
    eid = novo_id_estudo()
    meta = {
        "id": eid,
        "titulo": (a.titulo or "Estudo sem título").strip(),
        "fonte": (a.fonte or "").strip(),
        "tipo": (a.tipo or "outro").strip(),
        "tags": ",".join(t.strip() for t in (a.tags or "").split(",") if t.strip()),
        "criado": HOJE.isoformat(),
    }
    escrever_estudo(meta, corpo)
    print(f"Estudo guardado: {eid} — {meta['titulo']}")
    print(f"Arquivo: {caminho_estudo(eid)}")
    return 0

def cmd_listar_estudos(a):
    ests = todos_estudos()
    if a.tag:
        alvo = fold(a.tag)
        ests = [e for e in ests if alvo in [fold(t) for t in e["tags"].split(",")]]
    if a.busca:
        q = conjunto_tokens(a.busca)
        ests = [e for e in ests if q & conjunto_tokens(e["titulo"] + " " + e["corpo"] + " " + e["tags"])]
    ests.sort(key=lambda e: e["criado"], reverse=True)
    if a.limite:
        ests = ests[: a.limite]
    if not ests:
        print("Nenhum estudo guardado ainda.")
        return 0
    cart = ler_cartoes()
    for e in ests:
        nc = sum(1 for c in cart if c["estudo_id"] == e["id"])
        fonte = f" · {e['fonte']}" if e["fonte"] else ""
        print(f"[{e['id']}] {e['titulo']} ({e['tipo']}{fonte}) — {nc} cartão(ões) · {e['criado']}")
    return 0

def cmd_ver_estudo(a):
    e = ler_estudo(a.id)
    if not e:
        print(f"Estudo {a.id} não encontrado.")
        return 1
    print(f"# {e['titulo']}  [{e['id']}]")
    meta = [e["tipo"]]
    if e["fonte"]:
        meta.append(e["fonte"])
    if e["tags"]:
        meta.append("tags: " + e["tags"])
    print(" · ".join(m for m in meta if m))
    print()
    print(e["corpo"])
    cart = [c for c in ler_cartoes() if c["estudo_id"] == a.id]
    if cart:
        print(f"\n--- {len(cart)} cartão(ões) de revisão deste estudo ---")
        for c in cart:
            print(f"  [{c['id']}] {c['pergunta']}  (vence {c['proxima_revisao']})")
    return 0

def cmd_remover_estudo(a):
    p = caminho_estudo(a.id)
    if not os.path.exists(p):
        print(f"Estudo {a.id} não encontrado.")
        return 1
    os.remove(p)
    linhas = [c for c in ler_cartoes() if c["estudo_id"] != a.id]
    escrever_cartoes(linhas)
    print(f"Estudo {a.id} e seus cartões removidos.")
    return 0

def _add_um_cartao(linhas, eid, pergunta, resposta):
    cid = novo_id_cartao(linhas)
    linhas.append({
        "id": cid, "estudo_id": eid,
        "pergunta": pergunta.strip(), "resposta": resposta.strip(),
        "ef": "2.50", "n": "0", "intervalo": "0",
        "proxima_revisao": HOJE.isoformat(),  # vence já hoje (primeira revisão)
        "acertos": "0", "erros": "0",
        "criado": HOJE.isoformat(), "ultima_revisao": "",
    })
    return cid

def cmd_add_cartao(a):
    if not ler_estudo(a.estudo):
        print(f"Estudo {a.estudo} não encontrado — guarde o estudo primeiro.")
        return 1
    linhas = ler_cartoes()
    cid = _add_um_cartao(linhas, a.estudo, a.pergunta, a.resposta)
    escrever_cartoes(linhas)
    print(f"Cartão {cid} criado para o estudo {a.estudo} (vence hoje).")
    return 0

def cmd_add_cartoes(a):
    if not ler_estudo(a.estudo):
        print(f"Estudo {a.estudo} não encontrado — guarde o estudo primeiro.")
        return 1
    linhas = ler_cartoes()
    novos = 0
    for linha in sys.stdin.read().splitlines():
        if "|||" not in linha:
            continue
        p, r = linha.split("|||", 1)
        if p.strip() and r.strip():
            _add_um_cartao(linhas, a.estudo, p, r)
            novos += 1
    escrever_cartoes(linhas)
    print(f"{novos} cartão(ões) criado(s) para o estudo {a.estudo} (vencem hoje).")
    return 0

def cmd_revisar(a):
    linhas = ler_cartoes()
    devidos = [c for c in linhas if parse_data(c["proxima_revisao"]) <= HOJE]
    devidos.sort(key=lambda c: parse_data(c["proxima_revisao"]))
    if a.n:
        devidos = devidos[: a.n]
    if not devidos:
        prox = [parse_data(c["proxima_revisao"]) for c in linhas]
        if prox:
            d = min(prox)
            print(f"Nada para revisar hoje. Próxima revisão em {d.isoformat()} ({(d-HOJE).days} dia(s)).")
        else:
            print("Você ainda não tem cartões de revisão. Destile um conteúdo e crie os primeiros.")
        return 0
    print(f"{len(devidos)} cartão(ões) para revisar hoje:")
    for c in devidos:
        e = ler_estudo(c["estudo_id"])
        titulo = e["titulo"] if e else "?"
        print(f"\n[{c['id']}] (de: {titulo})")
        print(f"  P: {c['pergunta']}")
        if a.mostrar:
            print(f"  R: {c['resposta']}")
    print("\nResponda de cabeça, confira, e registre com: nota --id <N> --nota errei|dificil|bom|facil")
    print("(o <N> é o número entre colchetes de cada cartão acima.)")
    return 0

def cmd_ver_cartao(a):
    c = next((x for x in ler_cartoes() if x["id"] == a.id), None)
    if not c:
        print(f"Cartão {a.id} não encontrado.")
        return 1
    e = ler_estudo(c["estudo_id"])
    print(f"[{c['id']}] (de: {e['titulo'] if e else '?'})")
    print(f"P: {c['pergunta']}")
    print(f"R: {c['resposta']}")
    print(f"Acertos: {c['acertos']} · Erros: {c['erros']} · Vence: {c['proxima_revisao']}")
    return 0

def cmd_nota(a):
    linhas = ler_cartoes()
    c = next((x for x in linhas if x["id"] == a.id), None)
    if not c:
        print(f"Cartão {a.id} não encontrado.")
        return 1
    if fold(a.nota) not in NOTA_QUALIDADE:
        print("Nota inválida. Use: errei | dificil | bom | facil")
        return 1
    intervalo = aplicar_sm2(c, a.nota)
    escrever_cartoes(linhas)
    if fold(a.nota) == "errei":
        print(f"Sem problema — esse cartão volta amanhã pra você fixar. (cartão {a.id})")
    else:
        print(f"Boa! Próxima revisão em {intervalo} dia(s): {c['proxima_revisao']}. (cartão {a.id})")
    return 0

def cmd_buscar(a):
    q = conjunto_tokens(a.consulta)
    if not q:
        print("CONSULTA_VAZIA")
        return 0
    marcados = []
    for e in todos_estudos():
        alvo = conjunto_tokens(e["titulo"] + " " + e["corpo"] + " " + e["tags"])
        if not alvo:
            continue
        comuns = q & alvo
        score = len(comuns) / (len(q) ** 0.5)
        # bônus se casar no título
        if q & conjunto_tokens(e["titulo"]):
            score += 0.5
        if comuns:
            marcados.append((score, len(comuns), e))
    marcados.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not marcados:
        print("NADA_ENCONTRADO")
        return 0
    if marcados[0][1] < 2 and marcados[0][0] < 1.0:
        print("CONFIANCA_BAIXA")
    for score, comuns, e in marcados[: (a.n or 5)]:
        print(f"[{e['id']}] {e['titulo']} ({e['tipo']}) — {comuns} termo(s) em comum")
    return 0

def cmd_stats(a):
    ests = todos_estudos()
    cart = ler_cartoes()
    devidos = [c for c in cart if parse_data(c["proxima_revisao"]) <= HOJE]
    ac = sum(int(c.get("acertos") or 0) for c in cart)
    er = sum(int(c.get("erros") or 0) for c in cart)
    total_rev = ac + er
    taxa = (ac / total_rev * 100) if total_rev else 0
    tags = {}
    for e in ests:
        for t in e["tags"].split(","):
            t = t.strip()
            if t:
                tags[t] = tags.get(t, 0) + 1
    print("=== Painel do Alambique ===")
    print(f"Estudos guardados: {len(ests)}")
    print(f"Cartões de revisão: {len(cart)}")
    print(f"Para revisar hoje: {len(devidos)}")
    print(f"Revisões feitas: {total_rev} · taxa de acerto: {taxa:.0f}%")
    if tags:
        top = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:8]
        print("Assuntos: " + ", ".join(f"{t} ({n})" for t, n in top))
    return 0

# ----------------------------------------------------------------------------
# Legendas do YouTube (opcional; degrada com elegância se não houver yt-dlp)
# ----------------------------------------------------------------------------
def limpar_vtt(txt):
    linhas = []
    for l in txt.splitlines():
        s = l.strip()
        if not s or s == "WEBVTT" or "-->" in s:
            continue
        if re.match(r"^\d+$", s):
            continue
        if s.startswith(("Kind:", "Language:", "NOTE")):
            continue
        s = re.sub(r"<[^>]+>", "", s)  # tira tags de tempo inline
        linhas.append(s)
    # remove repetições consecutivas (legenda rolante)
    out = []
    for l in linhas:
        if not out or out[-1] != l:
            out.append(l)
    return "\n".join(out).strip()

def cmd_legendas(a):
    if not shutil.which("yt-dlp"):
        print("YT_DLP_AUSENTE")
        print("Para eu ler vídeos do YouTube automaticamente, instale o yt-dlp uma vez:")
        print("    pip install yt-dlp")
        print("Enquanto isso, é só COLAR aqui a transcrição do vídeo (ou o texto do")
        print("podcast/aula/artigo) que eu destilo do mesmo jeito.")
        return 2
    lang = a.lang or "pt,en"
    tmp = tempfile.mkdtemp(prefix="alambique-yt.")
    try:
        subprocess.run(
            ["yt-dlp", "--write-auto-sub", "--write-sub", "--sub-lang", lang,
             "--skip-download", "--sub-format", "vtt", "-o", os.path.join(tmp, "%(id)s"), a.url],
            check=False, capture_output=True, text=True, timeout=120,
        )
        vtts = glob.glob(os.path.join(tmp, "*.vtt"))
        if not vtts:
            print("SEM_LEGENDAS")
            print("Não encontrei legendas para esse vídeo. Cole a transcrição aqui que eu destilo.")
            return 2
        # prefere pt, depois en, depois o que houver
        def rank(p):
            b = os.path.basename(p)
            return (0 if ".pt" in b else 1 if ".en" in b else 2)
        vtts.sort(key=rank)
        with open(vtts[0], encoding="utf-8") as f:
            texto = limpar_vtt(f.read())
        print(texto)
        return 0
    except Exception as e:
        print("ERRO_LEGENDAS")
        print(f"Não consegui puxar as legendas ({e}). Cole a transcrição aqui que eu destilo.")
        return 2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ----------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Alambique — motor do destilador de conteúdo")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("salvar-estudo"); s.add_argument("--titulo"); s.add_argument("--fonte")
    s.add_argument("--tipo"); s.add_argument("--tags"); s.set_defaults(fn=cmd_salvar_estudo)

    s = sub.add_parser("listar-estudos"); s.add_argument("--busca"); s.add_argument("--tag")
    s.add_argument("--limite", type=int); s.set_defaults(fn=cmd_listar_estudos)

    s = sub.add_parser("ver-estudo"); s.add_argument("--id", required=True); s.set_defaults(fn=cmd_ver_estudo)
    s = sub.add_parser("remover-estudo"); s.add_argument("--id", required=True); s.set_defaults(fn=cmd_remover_estudo)

    s = sub.add_parser("add-cartao"); s.add_argument("--estudo", required=True)
    s.add_argument("--pergunta", required=True); s.add_argument("--resposta", required=True)
    s.set_defaults(fn=cmd_add_cartao)

    s = sub.add_parser("add-cartoes"); s.add_argument("--estudo", required=True); s.set_defaults(fn=cmd_add_cartoes)

    s = sub.add_parser("revisar"); s.add_argument("--n", type=int); s.add_argument("--mostrar", action="store_true")
    s.set_defaults(fn=cmd_revisar)

    s = sub.add_parser("ver-cartao"); s.add_argument("--id", required=True); s.set_defaults(fn=cmd_ver_cartao)

    s = sub.add_parser("nota"); s.add_argument("--id", required=True); s.add_argument("--nota", required=True)
    s.set_defaults(fn=cmd_nota)

    s = sub.add_parser("buscar"); s.add_argument("consulta"); s.add_argument("--n", type=int); s.set_defaults(fn=cmd_buscar)
    s = sub.add_parser("stats"); s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("legendas"); s.add_argument("url"); s.add_argument("--lang"); s.set_defaults(fn=cmd_legendas)

    a = p.parse_args()
    if not getattr(a, "cmd", None):
        p.print_help()
        return 0
    return a.fn(a)

if __name__ == "__main__":
    sys.exit(main())
