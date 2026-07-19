#!/usr/bin/env python3
"""Balcao - motor deterministico do atendimento inbound (so Python padrao).

O Balcao guarda a base de conhecimento do negocio (servicos, precos, horarios,
politicas e um banco de perguntas e respostas) e faz a parte chata e exata:
buscar a resposta certa na base, classificar (triar) a mensagem que chegou,
registrar perguntas sem resposta (lacunas) e mostrar o que mais perguntam.

Quem escreve a resposta final no tom do dono e o Claude - este motor so entrega
os fatos. O Balcao NUNCA inventa: se nao achou na base, ele diz que nao achou.

Tudo fica em .balcao/ na pasta do usuario (local, fora do controle de versao):
  - config.json / config.md  -> identidade e tom do negocio
  - base.md                  -> base de conhecimento legivel (precos, horarios, politicas)
  - faq.csv                  -> banco de perguntas e respostas (cresce com o uso)
  - lacunas.csv              -> perguntas que chegaram e nao tinham resposta

Comandos:
  buscar "<pergunta do cliente>"            procura resposta no faq + base
  triar  "<mensagem do cliente>"            classifica categoria + urgencia (JSON)
  add --pergunta "..." --resposta "..." --categoria "..." [--tags "a,b"]
                                            adiciona uma Q&A ao banco
  faq [--categoria X]                       lista o banco de FAQ
  usar --id N                               +1 em "vezes_perguntada" (mais pedidas)
  lacuna --pergunta "..." [--cliente "..."] registra pergunta sem resposta
  lacunas                                   lista as lacunas em aberto
  resolver --idl N                          marca uma lacuna como resolvida
  resumo                                    top perguntas + lacunas + categorias
"""

import csv
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))


def raiz_projeto():
    """Raiz do projeto do usuario, mesmo rodando de dentro de .claude/skills/balcao."""
    cwd = os.path.abspath(os.getcwd())
    marcador = os.sep + ".claude" + os.sep
    if marcador in cwd + os.sep:
        return cwd.split(marcador)[0]
    d = cwd
    while True:
        if os.path.isdir(os.path.join(d, ".claude")) or os.path.isdir(os.path.join(d, ".git")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            return cwd
        d = pai


PROJ = raiz_projeto()
DIR = os.path.join(PROJ, ".balcao")
FAQ = os.path.join(DIR, "faq.csv")
LAC = os.path.join(DIR, "lacunas.csv")
BASE = os.path.join(DIR, "base.md")
CFG = os.path.join(DIR, "config.json")

COLS_FAQ = ["id", "pergunta", "resposta", "categoria", "tags", "vezes_perguntada"]
COLS_LAC = ["id", "pergunta", "cliente", "status"]

STOPWORDS = set((
    "a o as os um uma de do da dos das em no na nos nas para por com sem e ou que "
    "se me te lhe meu minha seu sua qual quais quanto quanta quantos quantas como "
    "onde quando porque pra pro voce voces eu ele ela isso isto esse essa este esta "
    "tem ter tens fazem faz fazer e ja so mais menos muito pouco ai aqui la o(a) ne "
    "ola oi bom boa dia tarde noite tudo bem obrigado obrigada por favor gostaria "
    "queria sobre ao aos as vai vou vamos pode posso poderia ser e' eh"
).split())

# Regras de triagem (categoria -> palavras-chave, ja sem acento e minusculas)
REGRAS = [
    ("reclamacao", ["reclamacao", "reclamar", "pessimo", "pessima", "horrivel", "horroroso",
                    "problema", "nao funcionou", "nao funciona", "parou de funcionar",
                    "decepcao", "decepcionado", "processar", "advogado", "procon",
                    "ruim", "demora", "demorou", "atraso", "atrasado", "absurdo", "vergonha",
                    "cancelar", "cancelamento", "estorno", "reembolso", "dinheiro de volta"]),
    ("pagamento", ["pix", "cartao", "parcelar", "parcela", "parcelado", "boleto", "dinheiro",
                   "forma de pagamento", "formas de pagamento", "transferencia", "pagar"]),
    ("preco", ["preco", "precos", "quanto custa", "quanto e", "quanto fica", "valor", "valores",
               "orcamento", "tabela", "caro", "desconto", "promocao", "quanto sai"]),
    ("horario", ["horario", "que horas", "abre", "fecha", "fechado", "aberto", "funciona",
                 "funcionamento", "atende hoje", "atende amanha", "ate que horas"]),
    ("agendamento", ["marcar", "agendar", "agenda", "agendamento", "horario disponivel",
                     "tem vaga", "vaga", "encaixe", "remarcar", "marca pra mim"]),
    ("localizacao", ["onde", "endereco", "fica", "como chego", "como chegar", "estacionamento",
                     "localizacao", "bairro", "mapa", "rua"]),
    ("posvenda", ["como uso", "como usar", "como faco", "como faz", "deu erro", "parou",
                  "garantia", "nota fiscal", "suporte", "instrucao", "instrucoes", "manual",
                  "ja comprei", "ja contratei", "ja sou cliente", "pos venda", "pos-venda"]),
    ("servico", ["fazem", "voces trabalham", "trabalham com", "voces tem", "tem", "atendem",
                 "como funciona", "da pra", "e possivel", "voces fazem", "oferecem"]),
    ("saudacao", ["bom dia", "boa tarde", "boa noite", "ola", "oi", "tudo bem", "e ai"]),
]

URGENTE = ["urgente", "urgencia", "agora", "imediato", "emergencia", "hoje ainda",
           "preciso ja", "rapido", "socorro", "ajuda urgente"]


# ----------------------------------------------------------------------------- util
def normaliza(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def tokens(t):
    return [w for w in normaliza(t).split() if w not in STOPWORDS and len(w) > 1]


def ler_csv(caminho, cols):
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]


def escrever_csv(caminho, cols, linhas):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for l in linhas:
            w.writerow({c: l.get(c, "") for c in cols})


def proximo_id(linhas):
    return str(max([int(l["id"]) for l in linhas if l.get("id", "").isdigit()] or [0]) + 1)


def arg(nome, padrao=None):
    if nome in sys.argv:
        i = sys.argv.index(nome)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return padrao


def texto_posicional():
    """Pega o 1o argumento que nao e flag (para buscar/triar "texto")."""
    for a in sys.argv[2:]:
        if not a.startswith("--"):
            return a
    if "--texto" in sys.argv:
        return arg("--texto")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


# ----------------------------------------------------------------------------- base
def ler_base_texto():
    if os.path.exists(BASE):
        return open(BASE, encoding="utf-8").read()
    return ""


def trechos_base(consulta, limite=3):
    """Quebra a base.md em paragrafos e ranqueia por sobreposicao de palavras.

    Retorna lista de (overlap, bloco). 'overlap' = quantas palavras significativas
    o trecho compartilha com a pergunta - o chamador decide o que e forte (>=2).
    """
    txt = ler_base_texto()
    if not txt.strip():
        return []
    blocos = [b.strip() for b in re.split(r"\n\s*\n", txt) if b.strip()]
    qt = set(tokens(consulta))
    if not qt:
        return []
    pontuados = []
    for b in blocos:
        bt = set(tokens(b))
        overlap = len(qt & bt)
        if overlap:
            pontuados.append((overlap, b))
    pontuados.sort(key=lambda x: -x[0])
    return pontuados[:limite]


# ----------------------------------------------------------------------------- comandos
def cmd_buscar():
    consulta = texto_posicional()
    if not consulta.strip():
        print("Uso: balcao.py buscar \"pergunta do cliente\"", file=sys.stderr)
        sys.exit(1)
    qt = set(tokens(consulta))
    achados = []
    for l in ler_csv(FAQ, COLS_FAQ):
        pergunta_tokens = set(tokens(l["pergunta"]))
        base_tokens = pergunta_tokens | set(tokens(l.get("tags", "")))
        inter = qt & base_tokens
        no_pergunta = len(qt & pergunta_tokens)   # overlap so com a pergunta (mais forte)
        if not base_tokens or not inter:
            continue
        score = len(inter) / max(len(base_tokens), 1) + 0.15 * len(inter)
        # Confiavel = a pergunta praticamente bate (>=2 palavras em comum) ou score alto
        confiavel = (no_pergunta >= 2 and score >= 0.4) or score >= 0.8
        achados.append((score, confiavel, l))
    achados.sort(key=lambda x: -x[0])
    trechos = trechos_base(consulta)
    fortes = [(ov, b) for ov, b in trechos if ov >= 2]   # so trecho com >=2 palavras conta como resposta

    resultado = {
        "consulta": consulta.strip(),
        "encontrou_no_faq": [],     # respostas confiaveis
        "talvez_faq": [],           # parecidas, mas fracas - NAO sao resposta, so pista
        "trechos_da_base": [b for _, b in trechos],
        "tem_resposta": False,
    }
    for score, confiavel, l in achados[:4]:
        item = {"id": l["id"], "pergunta": l["pergunta"], "resposta": l["resposta"],
                "categoria": l.get("categoria", ""), "score": round(score, 2)}
        (resultado["encontrou_no_faq"] if confiavel else resultado["talvez_faq"]).append(item)
    resultado["tem_resposta"] = bool(resultado["encontrou_no_faq"] or fortes)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if not resultado["tem_resposta"]:
        print("\n>> SEM RESPOSTA CONFIAVEL NA BASE. Nao invente preco/prazo/politica. "
              "Escreva uma resposta-ponte ('ja te confirmo'), pergunte a resposta certa ao "
              "dono e registre: balcao.py lacuna --pergunta \"...\"", file=sys.stderr)


def cmd_triar():
    texto = texto_posicional()
    if not texto.strip():
        print("Uso: balcao.py triar \"mensagem do cliente\"", file=sys.stderr)
        sys.exit(1)
    n = " " + normaliza(texto) + " "

    def casa(chave):
        # palavra/frase inteira, nao pedaco (evita "fecha" casar em "fechar negocio")
        return re.search(r"\b" + re.escape(chave) + r"\b", n) is not None

    categorias = []
    for cat, chaves in REGRAS:
        if any(casa(k) for k in chaves):
            categorias.append(cat)
    # categoria principal: a primeira regra que casou (REGRAS esta em ordem de prioridade)
    principal = categorias[0] if categorias else "geral"
    urgencia = "alta" if (principal == "reclamacao" or any(casa(k) for k in URGENTE)) else "normal"
    bravo = bool(re.search(r"!{2,}", texto)) or sum(1 for c in texto if c.isupper()) > max(8, len(texto) * 0.4)
    out = {
        "categoria": principal,
        "todas_categorias": categorias or ["geral"],
        "urgencia": urgencia,
        "cliente_irritado": bravo or principal == "reclamacao",
        "sugestao": {
            "reclamacao": "Acolha primeiro, peca desculpa pelo transtorno, mostre que vai resolver. Nunca discuta.",
            "preco": "Responda o valor exato da base; se nao houver, nao chute - confirme com o dono.",
            "horario": "Informe o horario exato da base; se for fora do horario, diga quando volta a atender.",
            "agendamento": "Isso e marcacao de horario - encaminhe para a agenda (ex.: skill Pauta) ou ofereca horarios.",
            "pagamento": "Liste as formas de pagamento da base, sem prometer o que nao esta la.",
            "localizacao": "Mande o endereco/ponto de referencia exato da base.",
            "posvenda": "E cliente atual - seja atencioso, busque a instrucao na base; se nao houver, abra lacuna.",
            "servico": "Confirme se o negocio faz aquilo (base); se sim, explique simples; se nao, seja honesto.",
            "saudacao": "Cumprimente no tom do negocio e pergunte como pode ajudar.",
            "geral": "Busque na base; se nao achar, pergunte ao dono antes de responder.",
        }.get(principal, "Busque na base antes de responder."),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_add():
    p, r = arg("--pergunta"), arg("--resposta")
    if not p or not r:
        print("Uso: balcao.py add --pergunta \"...\" --resposta \"...\" --categoria \"...\"", file=sys.stderr)
        sys.exit(1)
    linhas = ler_csv(FAQ, COLS_FAQ)
    nova = {"id": proximo_id(linhas), "pergunta": p, "resposta": r,
            "categoria": arg("--categoria", "geral"), "tags": arg("--tags", ""),
            "vezes_perguntada": "1"}
    linhas.append(nova)
    escrever_csv(FAQ, COLS_FAQ, linhas)
    print("Adicionado ao banco de FAQ (id %s)." % nova["id"])


def cmd_faq():
    cat = arg("--categoria")
    linhas = ler_csv(FAQ, COLS_FAQ)
    if cat:
        linhas = [l for l in linhas if l.get("categoria") == cat]
    if not linhas:
        print("Banco de FAQ vazio." if not cat else "Nenhuma FAQ na categoria '%s'." % cat)
        return
    for l in linhas:
        print("[%s] (%s, %sx) %s\n      -> %s" % (
            l["id"], l.get("categoria", ""), l.get("vezes_perguntada", "0"),
            l["pergunta"], l["resposta"]))


def cmd_usar():
    idv = arg("--id")
    linhas = ler_csv(FAQ, COLS_FAQ)
    for l in linhas:
        if l["id"] == idv:
            l["vezes_perguntada"] = str(int(l.get("vezes_perguntada", "0") or "0") + 1)
            escrever_csv(FAQ, COLS_FAQ, linhas)
            print("FAQ %s agora com %s perguntas." % (idv, l["vezes_perguntada"]))
            return
    print("FAQ id %s nao encontrada." % idv, file=sys.stderr)


def cmd_lacuna():
    p = arg("--pergunta")
    if not p:
        print("Uso: balcao.py lacuna --pergunta \"...\" [--cliente \"...\"]", file=sys.stderr)
        sys.exit(1)
    linhas = ler_csv(LAC, COLS_LAC)
    nova = {"id": proximo_id(linhas), "pergunta": p,
            "cliente": arg("--cliente", ""), "status": "aberta"}
    linhas.append(nova)
    escrever_csv(LAC, COLS_LAC, linhas)
    print("Lacuna registrada (id %s). Pergunte a resposta ao dono e depois use 'add'." % nova["id"])


def cmd_lacunas():
    abertas = [l for l in ler_csv(LAC, COLS_LAC) if l.get("status") == "aberta"]
    if not abertas:
        print("Nenhuma lacuna em aberto. A base esta cobrindo as perguntas.")
        return
    print("Lacunas em aberto (perguntas sem resposta na base):")
    for l in abertas:
        quem = " (%s)" % l["cliente"] if l.get("cliente") else ""
        print("  [%s] %s%s" % (l["id"], l["pergunta"], quem))


def cmd_resolver():
    idl = arg("--idl")
    linhas = ler_csv(LAC, COLS_LAC)
    for l in linhas:
        if l["id"] == idl:
            l["status"] = "resolvida"
            escrever_csv(LAC, COLS_LAC, linhas)
            print("Lacuna %s marcada como resolvida." % idl)
            return
    print("Lacuna id %s nao encontrada." % idl, file=sys.stderr)


def cmd_resumo():
    faq = ler_csv(FAQ, COLS_FAQ)
    lac = [l for l in ler_csv(LAC, COLS_LAC) if l.get("status") == "aberta"]
    print("=== Resumo do Balcao ===")
    print("Perguntas no banco: %d | Lacunas em aberto: %d" % (len(faq), len(lac)))
    if faq:
        top = sorted(faq, key=lambda l: -int(l.get("vezes_perguntada", "0") or "0"))[:5]
        print("\nMais perguntadas (candidatas a resposta-padrao / automacao):")
        for l in top:
            print("  %sx  %s" % (l.get("vezes_perguntada", "0"), l["pergunta"]))
        cats = {}
        for l in faq:
            cats[l.get("categoria", "geral")] = cats.get(l.get("categoria", "geral"), 0) + 1
        print("\nPor categoria: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(cats.items(), key=lambda x: -x[1])))
    if lac:
        print("\nLacunas a preencher com o dono:")
        for l in lac[:8]:
            print("  - " + l["pergunta"])


COMANDOS = {
    "buscar": cmd_buscar, "triar": cmd_triar, "add": cmd_add, "faq": cmd_faq,
    "usar": cmd_usar, "lacuna": cmd_lacuna, "lacunas": cmd_lacunas,
    "resolver": cmd_resolver, "resumo": cmd_resumo,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print("Comandos: " + ", ".join(COMANDOS), file=sys.stderr)
        sys.exit(1)
    COMANDOS[sys.argv[1]]()


if __name__ == "__main__":
    main()
