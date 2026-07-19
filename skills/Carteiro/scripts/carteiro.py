#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carteiro — motor de triagem de correspondencia + follow-up (nada cai).
Somente biblioteca padrao do Python (stdlib). Sem rede, sem dependencias.

O motor cuida da parte EXATA e persistente:
  - guarda quem esta esperando resposta (fila de pendencias) e conta os dias;
  - sugere uma categoria de triagem para uma mensagem (por regras/palavras) com
    um nivel de confianca — match fraco NAO classifica sozinho;
  - guarda respostas reutilizaveis (modelos) com variaveis {assim};
  - da o painel de numeros.
A IA (a skill) conversa, le a pilha e escreve os textos; o motor guarda e calcula.

Dados 100% locais em .carteiro/ na RAIZ do projeto. Nunca inventa nada.
"""
import sys, os, csv, json, re, unicodedata, argparse
from datetime import date, datetime

# --------------------------------------------------------------------------
# Ancoragem: .carteiro/ mora na RAIZ do projeto, nao dentro da skill.
# Sobe a arvore procurando um marcador de raiz; usa CLAUDE_PROJECT_DIR se houver.
# --------------------------------------------------------------------------
def achar_raiz():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    d = os.getcwd()
    while True:
        for marca in (".carteiro", ".git", ".claude"):
            if os.path.exists(os.path.join(d, marca)):
                return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return os.getcwd()

RAIZ = achar_raiz()
DIR = os.path.join(RAIZ, ".carteiro")
DIR_MODELOS = os.path.join(DIR, "modelos")
PEND_CSV = os.path.join(DIR, "pendencias.csv")
CONFIG_MD = os.path.join(DIR, "config.md")

PEND_COLS = ["id", "quem", "assunto", "direcao", "canal",
             "entrou_em", "ultimo_toque", "status", "obs"]

# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def garantir_dirs():
    os.makedirs(DIR, exist_ok=True)
    os.makedirs(DIR_MODELOS, exist_ok=True)

def sem_acento(s):
    if not s:
        return ""
    n = unicodedata.normalize("NFKD", s)
    return "".join(c for c in n if not unicodedata.combining(c)).lower().strip()

def hoje():
    return date.today()

def parse_data(s):
    """Aceita DD/MM/AAAA, DD/MM/AA, DD/MM (ano corrente), AAAA-MM-DD."""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    m = re.match(r"^(\d{1,2})/(\d{1,2})$", s)
    if m:
        try:
            return date(hoje().year, int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None

def fmt_data(d):
    return d.strftime("%d/%m/%Y") if d else ""

def dias_desde(d):
    if not d:
        return None
    return (hoje() - d).days

def ler_pend():
    if not os.path.exists(PEND_CSV):
        return []
    with open(PEND_CSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def salvar_pend(linhas):
    garantir_dirs()
    with open(PEND_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PEND_COLS)
        w.writeheader()
        for l in linhas:
            w.writerow({c: l.get(c, "") for c in PEND_COLS})

def proximo_id(linhas):
    m = 0
    for l in linhas:
        try:
            m = max(m, int(l.get("id", "0")))
        except ValueError:
            pass
    return str(m + 1)

# --------------------------------------------------------------------------
# Config (lido acento-insensitive: "- **Rotulo:** valor")
# --------------------------------------------------------------------------
def ler_config():
    cfg = {}
    if not os.path.exists(CONFIG_MD):
        return cfg
    linha_re = re.compile(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$")
    with open(CONFIG_MD, encoding="utf-8") as f:
        for ln in f:
            m = linha_re.match(ln)
            if m:
                cfg[sem_acento(m.group(1))] = m.group(2).strip()
    return cfg

def cfg_get(cfg, *rotulos, padrao=""):
    for r in rotulos:
        k = sem_acento(r)
        if k in cfg and cfg[k]:
            return cfg[k]
    return padrao

def cfg_lista(cfg, *rotulos):
    v = cfg_get(cfg, *rotulos)
    if not v:
        return []
    return [x.strip() for x in re.split(r"[;,]", v) if x.strip()]

# --------------------------------------------------------------------------
# Classificador de triagem (heuristica com confianca)
#   Categorias: responder_hoje | pode_esperar | arquivar | ignorar
#   A IA usa como PISTA. Confianca "baixa" => a IA decide/pergunta.
# --------------------------------------------------------------------------
PADROES_URGENTE = [
    "urgente", "hoje", "agora", "imediato", "o quanto antes", "asap", "prazo",
    "vence", "vencimento", "ate amanha", "para ontem", "emergencia", "parou",
    "nao funciona", "erro", "reclamacao", "insatisfeito", "cancelar", "cancelamento",
    "aguardo retorno", "aguardando resposta", "podem me responder", "sem retorno",
]
PADROES_FINANCEIRO = [
    "boleto", "fatura", "pagamento", "nota fiscal", "nf-e", "pix", "cobranca",
    "invoice", "deposito", "transferencia", "banco", "fraude", "estorno",
]
PADROES_PERGUNTA = [
    "voce pode", "poderia", "consegue", "me confirma", "qual o", "quando",
    "quanto", "como faco", "duvida", "pergunta", "gostaria de saber", "?",
]
PADROES_RUIDO_ASSUNTO = [
    "newsletter", "novidades", "promocao", "oferta", "desconto", "black friday",
    "imperdivel", "nao perca", "ultimas vagas", "webinar", "convite para",
    "atualizamos nossos termos", "resumo semanal", "digest",
]
PADROES_AUTOMATICO_REMETENTE = [
    "no-reply", "noreply", "nao-responda", "naoresponda", "mailer", "notification",
    "notificacao", "automatic", "bounce", "postmaster", "updates@", "news@",
    "marketing@", "info@", "suporte@nao",
]

def _tem(texto, padroes):
    achados = [p for p in padroes if p in texto]
    return achados

def classificar(remetente, assunto, corpo, cfg):
    r = sem_acento(remetente)
    a = sem_acento(assunto)
    c = sem_acento(corpo)
    full = " ".join([a, c])
    vips = [sem_acento(x) for x in cfg_lista(cfg, "Remetentes VIP", "VIPs", "Contatos importantes")]

    motivos = []
    score_resp = 0
    score_ruido = 0

    # VIP => empurra pra responder
    vip_hit = [v for v in vips if v and (v in r or v in full)]
    if vip_hit:
        score_resp += 3
        motivos.append(f"remetente importante ({', '.join(vip_hit)})")

    urg = _tem(full, PADROES_URGENTE)
    if urg:
        score_resp += 3
        motivos.append("linguagem de urgencia: " + ", ".join(urg[:3]))
    fin = _tem(full, PADROES_FINANCEIRO)
    if fin:
        score_resp += 2
        motivos.append("financeiro: " + ", ".join(fin[:3]))
    perg = _tem(full, PADROES_PERGUNTA)
    if perg:
        score_resp += 2
        motivos.append("tem pergunta/pedido direto")

    auto = _tem(r, PADROES_AUTOMATICO_REMETENTE)
    if auto:
        score_ruido += 3
        motivos.append("remetente automatico (" + ", ".join(auto[:2]) + ")")
    ruido = _tem(a, PADROES_RUIDO_ASSUNTO)
    if ruido:
        score_ruido += 2
        motivos.append("assunto de divulgacao: " + ", ".join(ruido[:2]))

    # Decisao
    if score_resp >= score_ruido and score_resp >= 2:
        cat = "responder_hoje" if score_resp >= 3 else "pode_esperar"
    elif score_ruido > score_resp and score_ruido >= 3:
        cat = "ignorar" if auto and not (urg or perg or vip_hit) else "arquivar"
    elif score_ruido > 0:
        cat = "arquivar"
    else:
        cat = "pode_esperar"

    forca = max(score_resp, score_ruido)
    confianca = "alta" if forca >= 3 else ("media" if forca == 2 else "baixa")
    return {
        "categoria": cat,
        "confianca": confianca,
        "motivos": motivos or ["sem sinais fortes — a IA precisa ler e decidir"],
        "score_responder": score_resp,
        "score_ruido": score_ruido,
    }

# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------
def cmd_config(args):
    cfg = ler_config()
    if not cfg:
        print("Config ainda nao existe (.carteiro/config.md). Rode o setup primeiro.")
        return
    print(json.dumps(cfg, ensure_ascii=False, indent=2))

def cmd_classificar(args):
    corpo = ""
    if args.corpo_arquivo:
        with open(args.corpo_arquivo, encoding="utf-8") as f:
            corpo = f.read()
    elif args.corpo:
        corpo = args.corpo
    cfg = ler_config()
    res = classificar(args.remetente or "", args.assunto or "", corpo, cfg)
    print(json.dumps(res, ensure_ascii=False, indent=2))

def cmd_pend_add(args):
    linhas = ler_pend()
    nid = proximo_id(linhas)
    entrou = parse_data(args.entrou) if args.entrou else hoje()
    if entrou is None:
        print(f"Data invalida: {args.entrou}. Use DD/MM/AAAA.")
        sys.exit(1)
    direcao = args.direcao if args.direcao in ("eu_devo", "aguardo") else "eu_devo"
    nova = {
        "id": nid, "quem": args.quem.strip(), "assunto": (args.assunto or "").strip(),
        "direcao": direcao, "canal": (args.canal or "").strip(),
        "entrou_em": fmt_data(entrou), "ultimo_toque": fmt_data(entrou),
        "status": "aberta", "obs": (args.obs or "").strip(),
    }
    linhas.append(nova)
    salvar_pend(linhas)
    rotulo = "eu devo responder" if direcao == "eu_devo" else "aguardo resposta de"
    print(f"Pendencia #{nid} registrada ({rotulo} {nova['quem']}).")

def _sinal_dias(d):
    if d is None:
        return "🟢", "sem data"
    if d >= 7:
        return "🔴", f"esperando ha {d} dias"
    if d >= 3:
        return "🟡", f"esperando ha {d} dias"
    return "🟢", (f"ha {d} dia(s)" if d > 0 else "hoje")

def cmd_pend_list(args):
    linhas = ler_pend()
    if args.direcao:
        linhas = [l for l in linhas if l.get("direcao") == args.direcao]
    if args.status:
        linhas = [l for l in linhas if l.get("status") == args.status]
    if not linhas:
        print("Nenhuma pendencia com esse filtro.")
        return
    for l in linhas:
        d = dias_desde(parse_data(l.get("ultimo_toque")))
        sinal, txt = _sinal_dias(d)
        rot = "→ eu devo" if l.get("direcao") == "eu_devo" else "← aguardo"
        st = "" if l.get("status") == "aberta" else f" [{l.get('status')}]"
        print(f"{sinal} #{l['id']} {rot} | {l['quem']} — {l.get('assunto','(sem assunto)')} "
              f"| {txt} | {l.get('canal','')}{st}")

def cmd_pend_hoje(args):
    linhas = [l for l in ler_pend()
              if l.get("status") == "aberta" and l.get("direcao") == "eu_devo"]
    if not linhas:
        print("Ninguem esperando resposta sua. Caixa em dia. ✅")
        return
    def chave(l):
        d = dias_desde(parse_data(l.get("ultimo_toque")))
        return -(d if d is not None else -1)
    linhas.sort(key=chave)
    print("Quem esta esperando sua resposta (do mais antigo pro mais novo):\n")
    for l in linhas:
        d = dias_desde(parse_data(l.get("ultimo_toque")))
        sinal, txt = _sinal_dias(d)
        print(f"{sinal} #{l['id']} {l['quem']} — {l.get('assunto','(sem assunto)')} "
              f"| {txt} | {l.get('canal','')}")
    print("\nUse 'pend-tocar --id N' quando enviar o retorno, "
          "ou 'pend-responder --id N' quando resolver.")

def _achar(linhas, nid):
    for l in linhas:
        if l.get("id") == str(nid):
            return l
    return None

def cmd_pend_tocar(args):
    linhas = ler_pend()
    l = _achar(linhas, args.id)
    if not l:
        print(f"Pendencia #{args.id} nao encontrada.")
        sys.exit(1)
    l["ultimo_toque"] = fmt_data(hoje())
    salvar_pend(linhas)
    print(f"Pendencia #{args.id} tocada hoje ({l['quem']}). O contador zerou.")

def cmd_pend_responder(args):
    linhas = ler_pend()
    l = _achar(linhas, args.id)
    if not l:
        print(f"Pendencia #{args.id} nao encontrada.")
        sys.exit(1)
    l["status"] = "respondida"
    l["ultimo_toque"] = fmt_data(hoje())
    salvar_pend(linhas)
    print(f"Pendencia #{args.id} marcada como respondida ({l['quem']}). ✅")

def cmd_pend_editar(args):
    linhas = ler_pend()
    l = _achar(linhas, args.id)
    if not l:
        print(f"Pendencia #{args.id} nao encontrada.")
        sys.exit(1)
    if args.quem:
        l["quem"] = args.quem.strip()
    if args.assunto:
        l["assunto"] = args.assunto.strip()
    if args.canal:
        l["canal"] = args.canal.strip()
    if args.entrou:
        d = parse_data(args.entrou)
        if d is None:
            print(f"Data invalida: {args.entrou}")
            sys.exit(1)
        l["entrou_em"] = fmt_data(d)
    if args.status:
        l["status"] = args.status
    salvar_pend(linhas)
    print(f"Pendencia #{args.id} atualizada.")

def cmd_pend_remover(args):
    linhas = ler_pend()
    novas = [l for l in linhas if l.get("id") != str(args.id)]
    if len(novas) == len(linhas):
        print(f"Pendencia #{args.id} nao encontrada.")
        sys.exit(1)
    salvar_pend(novas)
    print(f"Pendencia #{args.id} removida.")

# ---- Modelos (respostas reutilizaveis) ----
def _slug(s):
    s = sem_acento(s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "modelo"

def _vars(corpo):
    return sorted(set(re.findall(r"\{([a-zA-Z0-9_ ]+)\}", corpo)))

def cmd_modelo_salvar(args):
    garantir_dirs()
    corpo = ""
    if args.corpo_arquivo:
        with open(args.corpo_arquivo, encoding="utf-8") as f:
            corpo = f.read()
    elif args.corpo:
        corpo = args.corpo
    if not corpo.strip():
        print("Corpo vazio. Passe --corpo-arquivo ou --corpo.")
        sys.exit(1)
    slug = args.slug or _slug(args.titulo or "modelo")
    dados = {
        "slug": slug, "titulo": args.titulo or slug,
        "corpo": corpo, "variaveis": _vars(corpo),
        "usos": 0, "criado": fmt_data(hoje()),
    }
    with open(os.path.join(DIR_MODELOS, slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    v = ", ".join("{" + x + "}" for x in dados["variaveis"]) or "nenhuma"
    print(f"Modelo '{slug}' salvo. Variaveis detectadas: {v}.")

def cmd_modelos(args):
    garantir_dirs()
    arqs = sorted(f for f in os.listdir(DIR_MODELOS) if f.endswith(".json"))
    if not arqs:
        print("Nenhum modelo salvo ainda.")
        return
    for a in arqs:
        with open(os.path.join(DIR_MODELOS, a), encoding="utf-8") as f:
            d = json.load(f)
        v = ", ".join("{" + x + "}" for x in d.get("variaveis", [])) or "—"
        print(f"• {d['slug']} — {d['titulo']} (usos: {d.get('usos',0)}; vars: {v})")

def cmd_modelo_usar(args):
    p = os.path.join(DIR_MODELOS, args.slug + ".json")
    if not os.path.exists(p):
        print(f"Modelo '{args.slug}' nao encontrado.")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    d["usos"] = d.get("usos", 0) + 1
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(d["corpo"])
    if d.get("variaveis"):
        sys.stderr.write("\n[preencha: " + ", ".join("{" + x + "}" for x in d["variaveis"]) + "]\n")

def cmd_modelo_remover(args):
    p = os.path.join(DIR_MODELOS, args.slug + ".json")
    if not os.path.exists(p):
        print(f"Modelo '{args.slug}' nao encontrado.")
        sys.exit(1)
    os.remove(p)
    print(f"Modelo '{args.slug}' removido.")

def cmd_resumo(args):
    linhas = ler_pend()
    abertas = [l for l in linhas if l.get("status") == "aberta"]
    eu_devo = [l for l in abertas if l.get("direcao") == "eu_devo"]
    aguardo = [l for l in abertas if l.get("direcao") == "aguardo"]
    def atraso(l):
        return dias_desde(parse_data(l.get("ultimo_toque"))) or 0
    venc7 = [l for l in eu_devo if atraso(l) >= 7]
    venc3 = [l for l in eu_devo if 3 <= atraso(l) < 7]
    modelos = 0
    if os.path.isdir(DIR_MODELOS):
        modelos = len([f for f in os.listdir(DIR_MODELOS) if f.endswith(".json")])
    contagem = {}
    for l in abertas:
        k = sem_acento(l.get("quem", "")) or "?"
        contagem[k] = contagem.get(k, 0) + 1
    top = sorted(contagem.items(), key=lambda x: -x[1])[:5]

    if not abertas and modelos == 0:
        print("Caixa em dia e nenhum modelo salvo. Nada pendente. ✅")
        return
    print("PAINEL DO CARTEIRO")
    print(f"  Pendencias abertas: {len(abertas)}")
    print(f"    → eu devo responder: {len(eu_devo)}")
    print(f"    ← aguardo resposta:  {len(aguardo)}")
    if venc7:
        print(f"  🔴 esperando ha 7+ dias: {len(venc7)}  (#{', #'.join(l['id'] for l in venc7)})")
    if venc3:
        print(f"  🟡 esperando 3–6 dias:   {len(venc3)}  (#{', #'.join(l['id'] for l in venc3)})")
    print(f"  Modelos de resposta salvos: {modelos}")
    if top:
        print("  Quem mais aparece na fila:")
        for nome, n in top:
            print(f"    - {nome}: {n}")

# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(description="Carteiro — triagem + follow-up (nada cai).")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("config").set_defaults(func=cmd_config)

    c = sub.add_parser("classificar", help="sugere categoria de triagem de UMA mensagem")
    c.add_argument("--remetente", default="")
    c.add_argument("--assunto", default="")
    c.add_argument("--corpo", default="")
    c.add_argument("--corpo-arquivo", dest="corpo_arquivo", default="")
    c.set_defaults(func=cmd_classificar)

    a = sub.add_parser("pend-add", help="registra alguem na fila de pendencias")
    a.add_argument("--quem", required=True)
    a.add_argument("--assunto", default="")
    a.add_argument("--direcao", default="eu_devo", choices=["eu_devo", "aguardo"])
    a.add_argument("--canal", default="")
    a.add_argument("--entrou", default="")
    a.add_argument("--obs", default="")
    a.set_defaults(func=cmd_pend_add)

    l = sub.add_parser("pend-list")
    l.add_argument("--direcao", choices=["eu_devo", "aguardo"])
    l.add_argument("--status", choices=["aberta", "respondida", "fechada"])
    l.set_defaults(func=cmd_pend_list)

    sub.add_parser("pend-hoje").set_defaults(func=cmd_pend_hoje)

    t = sub.add_parser("pend-tocar"); t.add_argument("--id", required=True); t.set_defaults(func=cmd_pend_tocar)
    r = sub.add_parser("pend-responder"); r.add_argument("--id", required=True); r.set_defaults(func=cmd_pend_responder)
    rm = sub.add_parser("pend-remover"); rm.add_argument("--id", required=True); rm.set_defaults(func=cmd_pend_remover)

    e = sub.add_parser("pend-editar")
    e.add_argument("--id", required=True)
    e.add_argument("--quem"); e.add_argument("--assunto"); e.add_argument("--canal")
    e.add_argument("--entrou"); e.add_argument("--status", choices=["aberta", "respondida", "fechada"])
    e.set_defaults(func=cmd_pend_editar)

    ms = sub.add_parser("modelo-salvar")
    ms.add_argument("--slug", default="")
    ms.add_argument("--titulo", default="")
    ms.add_argument("--corpo", default="")
    ms.add_argument("--corpo-arquivo", dest="corpo_arquivo", default="")
    ms.set_defaults(func=cmd_modelo_salvar)

    sub.add_parser("modelos").set_defaults(func=cmd_modelos)
    mu = sub.add_parser("modelo-usar"); mu.add_argument("--slug", required=True); mu.set_defaults(func=cmd_modelo_usar)
    mr = sub.add_parser("modelo-remover"); mr.add_argument("--slug", required=True); mr.set_defaults(func=cmd_modelo_remover)

    sub.add_parser("resumo").set_defaults(func=cmd_resumo)
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(0)
    args.func(args)

if __name__ == "__main__":
    main()
