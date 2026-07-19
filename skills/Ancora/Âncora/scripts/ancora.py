#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ancora - motor de retencao de carteira de clientes recorrentes (Customer Success de bolso).

Somente biblioteca padrao do Python (stdlib). Sem pandas, sem rede, sem chave de API,
sem instalar nada. Guarda tudo em uma pasta local .ancora/ na raiz do projeto do dono:
  .ancora/config.md          -> perfil do dono/negocio (escrito na 1a execucao)
  .ancora/clientes.csv       -> a carteira: um cliente recorrente por linha
  .ancora/saude.csv          -> fotos de saude (uma por avaliacao; usa-se a mais recente)
  .ancora/interacoes.csv     -> registro de toques/check-ins (relacionamento)
  .ancora/oportunidades.csv  -> oportunidades de expansao (upsell/cross-sell)

O motor faz APENAS a parte exata que a IA nao deve chutar:
  - SCORE DE SAUDE: nota ponderada e EXPLICAVEL (0-100) + semaforo, a partir de sinais
    simples de um negocio de servico (pagamento, engajamento, satisfacao, resultado,
    relacionamento) com penalidade por tempo sem contato e reclamacao.
  - RADAR DE RENOVACAO: quem renova em N dias, cruzado com o semaforo, ordenado por
    risco x valor (onde a receita esta mais exposta primeiro).
  - DECISAO ECONOMICA DO RESGATE (EV): vale a pena salvar? EV = prob x valor_em_jogo - custo,
    com a probabilidade de equilibrio (a partir de quando compensa).
  - PAINEL DA CARTEIRA: MRR, distribuicao do semaforo, receita em risco, churn do periodo,
    quem esta sem toque ha muito tempo, oportunidades de expansao abertas.

Quem entrevista o dono, le os sinais e escreve em portugues simples e a IA. O motor
nao inventa nada: so guarda, calcula e ordena.

Uso (a IA chama por baixo; o dono so conversa):
  ancora.py init
  ancora.py cliente-add --nome "Clinica Sorriso" --contato "Dra. Ana" --servico "Gestao de trafego"
                        --valor "R$ 1.500" --ciclo mensal --inicio 01/02/2026 --renovacao 01/02/2027 --canal whatsapp
  ancora.py clientes [--status ativo]              # lista + retrato da carteira (MRR, proximas renovacoes)
  ancora.py cliente-editar --id 1 [--valor ..] [--renovacao ..] [--contato ..] ...
  ancora.py cliente-status --id 1 --status cancelado [--data 10/07/2026] [--motivo "achou caro"]
  ancora.py saude --id 1 --pagamento 2 --engajamento 1 --satisfacao 2 --resultado 1 --relacionamento 2
                 [--dias-sem-contato 40] [--reclamacao n]     # calcula score + semaforo + motivo
  ancora.py saude-ver [--id 1]                     # saude atual (um cliente ou a carteira toda)
  ancora.py renovacao [--dias 90]                  # radar de renovacao/risco ordenado por risco x valor
  ancora.py ev --id 1 --prob 60 --custo "R$ 300" [--horizonte 12]   # vale a pena salvar? (economia da oferta)
  ancora.py toque --id 1 --tipo checkin --nota "liguei, cliente ok"  # registra interacao (relacionamento)
  ancora.py toques [--id 1] [--sem-contato 30]     # historico / quem esta ha X dias sem toque
  ancora.py oportunidade-add --id 1 --tipo mais_servico --descricao "SEO" --valor "R$ 800"
  ancora.py oportunidades [--abertas]              # oportunidades de expansao
  ancora.py painel                                 # resumo da carteira inteira

Sinais de saude (cada um 0, 1 ou 2 - quanto maior, mais saudavel):
  pagamento      2=em dia   1=atrasa as vezes   0=inadimplente
  engajamento    2=responde/participa  1=morno  0=sumido
  satisfacao     2=elogia/NPS alto     1=neutro 0=reclamou/NPS baixo
  resultado      2=tendo resultado claro 1=incerto 0=sem resultado
  relacionamento 2=decisor firme e presente 1=trocou/incerto 0=decisor foi embora

Dinheiro: aceita "R$ 1.500,00", "1500", "1.234,56". Datas: DD/MM/AAAA, DD/MM, AAAA-MM-DD, hoje/amanha.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import unicodedata
from datetime import date, datetime, timedelta

# --------------------------------------------------------------------------- #
# Ancoragem: a pasta .ancora/ mora na RAIZ do projeto do dono, mesmo que o motor
# seja chamado de dentro de .claude/skills/. Sobe a arvore procurando marcadores.
# --------------------------------------------------------------------------- #
def achar_raiz():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    d = os.getcwd()
    while True:
        for marca in (".ancora", ".git", ".claude"):
            if os.path.exists(os.path.join(d, marca)):
                return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return os.getcwd()


RAIZ = achar_raiz()
PASTA = os.path.join(RAIZ, ".ancora")
CONFIG = os.path.join(PASTA, "config.md")
CLIENTES = os.path.join(PASTA, "clientes.csv")
SAUDE = os.path.join(PASTA, "saude.csv")
INTERACOES = os.path.join(PASTA, "interacoes.csv")
OPORT = os.path.join(PASTA, "oportunidades.csv")

CLI_COLS = ["id", "nome", "contato", "servico", "valor", "ciclo", "inicio",
            "renovacao", "status", "canal", "obs", "criado", "cancelado_em", "motivo_saida"]
SAUDE_COLS = ["id_cliente", "data", "pagamento", "engajamento", "satisfacao",
              "resultado", "relacionamento", "dias_sem_contato", "reclamacao",
              "score", "semaforo", "motivo"]
INT_COLS = ["data", "id_cliente", "tipo", "nota"]
OPP_COLS = ["id", "id_cliente", "tipo", "descricao", "valor", "status", "criado"]

# Pesos do score de saude (somam 100). Resultado pesa mais: e o motivo pelo qual
# o cliente contratou. Sem resultado, todo o resto e barulho.
PESOS = {
    "resultado": 25,
    "pagamento": 20,
    "engajamento": 20,
    "satisfacao": 20,
    "relacionamento": 15,
}
SINAIS = ["pagamento", "engajamento", "satisfacao", "resultado", "relacionamento"]

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def semreacento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower().strip()


def parse_data(txt, base: date | None = None) -> date:
    if txt is None or (isinstance(txt, str) and not txt.strip()):
        raise ValueError("data vazia")
    if isinstance(txt, date):
        return txt
    s = str(txt).strip().lower()
    base = base or date.today()
    if s in ("hoje", "today"):
        return base
    if s in ("amanha", "amanhã"):
        return base + timedelta(days=1)
    if s in ("ontem",):
        return base - timedelta(days=1)
    if " de " in s:
        partes = s.replace(" do ", " de ").split(" de ")
        try:
            dia = int(partes[0].strip())
            mes = MESES.get(partes[1].strip())
            ano = int(partes[2].strip()) if len(partes) > 2 and partes[2].strip() else base.year
            if mes:
                return date(ano, mes, dia)
        except (ValueError, IndexError):
            pass
    if "-" in s and s.count("-") == 2:
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            pass
    if "/" in s:
        p = s.split("/")
        try:
            if len(p) == 3:
                dia, mes, ano = int(p[0]), int(p[1]), int(p[2])
                if ano < 100:
                    ano += 2000
                return date(ano, mes, dia)
            if len(p) == 2:
                return date(base.year, int(p[1]), int(p[0]))
        except ValueError:
            pass
    raise ValueError(f"data invalida: {txt!r}")


def iso(d: date) -> str:
    return d.isoformat()


def br_data(d) -> str:
    if not d:
        return "-"
    if isinstance(d, str):
        try:
            d = parse_data(d)
        except ValueError:
            return d
    return d.strftime("%d/%m/%Y")


def parse_dinheiro(txt) -> float:
    """Aceita 'R$ 1.500,00', '1500', '1.234,56', '1,5 mil'."""
    if txt is None:
        return 0.0
    if isinstance(txt, (int, float)):
        return float(txt)
    s = str(txt).strip().lower().replace("r$", "").replace(" ", "")
    if not s:
        return 0.0
    mult = 1.0
    if s.endswith("mil"):
        mult = 1000.0
        s = s[:-3]
    elif s.endswith("k"):
        mult = 1000.0
        s = s[:-1]
    # separadores: no BR ponto e milhar e virgula e decimal
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif "." in s:
        # so ponto: no BR "1.500" e milhar (3 digitos no ultimo grupo);
        # "1.5"/"1500.50" e decimal (1 ou 2 digitos no ultimo grupo).
        partes = s.split(".")
        if len(partes[-1]) == 3:
            s = "".join(partes)                      # milhar: 1.500 -> 1500
        else:
            s = "".join(partes[:-1]) + "." + partes[-1]  # decimal: 1500.50 -> 1500.50
    try:
        return round(float(s) * mult, 2)
    except ValueError:
        return 0.0


def brl(v: float) -> str:
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def mensal_equivalente(valor: float, ciclo: str) -> float:
    c = semreacento(ciclo or "mensal")
    if c.startswith("anual") or c.startswith("ano"):
        return round(valor / 12.0, 2)
    if c.startswith("trimestr") or c.startswith("tri"):
        return round(valor / 3.0, 2)
    if c.startswith("semestr") or c.startswith("sem"):
        return round(valor / 6.0, 2)
    return round(valor, 2)  # mensal (padrao)


# --------------------------------------------------------------------------- #
# Leitura / escrita de CSV
# --------------------------------------------------------------------------- #
def _garantir_pasta():
    os.makedirs(PASTA, exist_ok=True)


def _ler(caminho, cols):
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    # normaliza colunas ausentes
    for l in linhas:
        for c in cols:
            l.setdefault(c, "")
    return linhas


def _escrever(caminho, cols, linhas):
    _garantir_pasta()
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for l in linhas:
            w.writerow({c: l.get(c, "") for c in cols})


def ler_clientes():
    return _ler(CLIENTES, CLI_COLS)


def ler_saude():
    return _ler(SAUDE, SAUDE_COLS)


def ler_interacoes():
    return _ler(INTERACOES, INT_COLS)


def ler_oport():
    return _ler(OPORT, OPP_COLS)


def proximo_id(linhas):
    m = 0
    for l in linhas:
        try:
            m = max(m, int(l.get("id", 0)))
        except (ValueError, TypeError):
            pass
    return m + 1


def achar_cliente(clientes, cid):
    for c in clientes:
        if str(c.get("id")) == str(cid):
            return c
    return None


def ler_config() -> dict:
    cfg = {}
    if not os.path.exists(CONFIG):
        return cfg
    for linha in open(CONFIG, encoding="utf-8"):
        linha = linha.strip()
        if linha.startswith("- **") and ":**" in linha:
            chave, _, val = linha[4:].partition(":**")
            cfg[semreacento(chave.strip())] = val.strip()
    return cfg


# --------------------------------------------------------------------------- #
# Saude: score ponderado e explicavel
# --------------------------------------------------------------------------- #
def calcular_saude(sinais: dict, dias_sem_contato=None, reclamacao="n"):
    """
    sinais: dict com pagamento/engajamento/satisfacao/resultado/relacionamento em 0..2.
    Retorna (score 0-100, semaforo, motivo (texto), fatores_arrasto (list)).
    """
    score = 0.0
    for s in SINAIS:
        v = max(0, min(2, int(sinais.get(s, 1))))
        score += (v / 2.0) * PESOS[s]

    penal = []
    # penalidade por tempo sem contato
    if dias_sem_contato not in (None, "", "-"):
        try:
            d = int(dias_sem_contato)
            if d >= 60:
                score -= 10
                penal.append(f"{d} dias sem contato (-10)")
            elif d >= 30:
                score -= 5
                penal.append(f"{d} dias sem contato (-5)")
        except (ValueError, TypeError):
            pass
    # reclamacao recente
    rec = semreacento(str(reclamacao))
    if rec in ("s", "sim", "y", "1", "true"):
        score -= 10
        penal.append("reclamacao recente (-10)")

    score = max(0, min(100, round(score)))

    # semaforo base pelo score
    if score >= 70:
        semaforo = "verde"
    elif score >= 40:
        semaforo = "amarelo"
    else:
        semaforo = "vermelho"

    # travas duras (nao deixam parecer saudavel algo que nao e)
    graves = 0
    if int(sinais.get("pagamento", 1)) == 0:
        graves += 1
    if int(sinais.get("relacionamento", 1)) == 0:
        graves += 1
    if int(sinais.get("resultado", 1)) == 0:
        graves += 1
    if int(sinais.get("satisfacao", 1)) == 0:
        graves += 1
    if graves >= 2:
        semaforo = "vermelho"
    elif graves == 1 and semaforo == "verde":
        semaforo = "amarelo"

    # motivo: o que puxa a saude para baixo
    rotulos = {
        "pagamento": {0: "inadimplente", 1: "paga com atraso"},
        "engajamento": {0: "cliente sumido", 1: "engajamento morno"},
        "satisfacao": {0: "insatisfeito/reclamou", 1: "satisfacao neutra"},
        "resultado": {0: "sem resultado percebido", 1: "resultado incerto"},
        "relacionamento": {0: "decisor foi embora", 1: "decisor trocou/incerto"},
    }
    fatores = []
    for s in SINAIS:
        v = int(sinais.get(s, 1))
        if v in (0, 1):
            fatores.append(rotulos[s][v])
    fatores += penal
    motivo = "; ".join(fatores) if fatores else "todos os sinais saudaveis"
    return score, semaforo, motivo, fatores


def saude_atual_por_cliente():
    """Retorna dict {id_cliente: linha_de_saude_mais_recente}."""
    saude = ler_saude()
    atual = {}
    for s in saude:
        cid = str(s.get("id_cliente"))
        d = s.get("data", "")
        if cid not in atual or d >= atual[cid].get("data", ""):
            atual[cid] = s
    return atual


EMOJI = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}


def emoji_semaforo(sem):
    return EMOJI.get(sem, "⚪")


# --------------------------------------------------------------------------- #
# Comandos
# --------------------------------------------------------------------------- #
def cmd_init(args):
    _garantir_pasta()
    for caminho, cols in ((CLIENTES, CLI_COLS), (SAUDE, SAUDE_COLS),
                          (INTERACOES, INT_COLS), (OPORT, OPP_COLS)):
        if not os.path.exists(caminho):
            _escrever(caminho, cols, [])
    print(f"OK - Ancora iniciada em {PASTA}")


def cmd_cliente_add(args):
    clientes = ler_clientes()
    cid = proximo_id(clientes)
    valor = parse_dinheiro(args.valor)
    ciclo = (args.ciclo or "mensal").strip().lower()
    novo = {
        "id": cid,
        "nome": args.nome.strip(),
        "contato": (args.contato or "").strip(),
        "servico": (args.servico or "").strip(),
        "valor": f"{valor:.2f}",
        "ciclo": ciclo,
        "inicio": iso(parse_data(args.inicio)) if args.inicio else "",
        "renovacao": iso(parse_data(args.renovacao)) if args.renovacao else "",
        "status": (args.status or "ativo").strip().lower(),
        "canal": (args.canal or "").strip().lower(),
        "obs": (args.obs or "").strip(),
        "criado": iso(date.today()),
        "cancelado_em": "",
        "motivo_saida": "",
    }
    clientes.append(novo)
    _escrever(CLIENTES, CLI_COLS, clientes)
    me = mensal_equivalente(valor, ciclo)
    print(f"OK - cliente #{cid} '{novo['nome']}' cadastrado. "
          f"Valor {brl(valor)}/{ciclo} (equivale a {brl(me)}/mes). "
          f"Renovacao: {br_data(novo['renovacao']) if novo['renovacao'] else 'nao informada'}.")


def cmd_cliente_editar(args):
    clientes = ler_clientes()
    c = achar_cliente(clientes, args.id)
    if not c:
        print(f"ERRO - cliente #{args.id} nao encontrado.")
        return
    if args.nome is not None:
        c["nome"] = args.nome.strip()
    if args.contato is not None:
        c["contato"] = args.contato.strip()
    if args.servico is not None:
        c["servico"] = args.servico.strip()
    if args.valor is not None:
        c["valor"] = f"{parse_dinheiro(args.valor):.2f}"
    if args.ciclo is not None:
        c["ciclo"] = args.ciclo.strip().lower()
    if args.inicio is not None:
        c["inicio"] = iso(parse_data(args.inicio))
    if args.renovacao is not None:
        c["renovacao"] = iso(parse_data(args.renovacao))
    if args.canal is not None:
        c["canal"] = args.canal.strip().lower()
    if args.obs is not None:
        c["obs"] = args.obs.strip()
    _escrever(CLIENTES, CLI_COLS, clientes)
    print(f"OK - cliente #{args.id} atualizado.")


def cmd_cliente_status(args):
    clientes = ler_clientes()
    c = achar_cliente(clientes, args.id)
    if not c:
        print(f"ERRO - cliente #{args.id} nao encontrado.")
        return
    st = args.status.strip().lower()
    c["status"] = st
    if st == "cancelado":
        c["cancelado_em"] = iso(parse_data(args.data)) if args.data else iso(date.today())
        if args.motivo:
            c["motivo_saida"] = args.motivo.strip()
    _escrever(CLIENTES, CLI_COLS, clientes)
    extra = f" em {br_data(c['cancelado_em'])}" if st == "cancelado" else ""
    print(f"OK - cliente #{args.id} agora esta '{st}'{extra}.")


def _retrato(clientes):
    ativos = [c for c in clientes if c.get("status") in ("ativo", "em_risco", "pausado")]
    mrr = sum(mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo")) for c in ativos
              if c.get("status") in ("ativo", "em_risco"))
    return ativos, mrr


def cmd_clientes(args):
    clientes = ler_clientes()
    if args.status:
        clientes = [c for c in clientes if c.get("status") == args.status.strip().lower()]
    if not clientes:
        print("Nenhum cliente na carteira ainda. Cadastre com 'cliente-add'.")
        return
    ativos, mrr = _retrato(ler_clientes())
    saude = saude_atual_por_cliente()
    hoje = date.today()
    print(f"CARTEIRA - {len(ativos)} clientes ativos - MRR {brl(mrr)}\n")
    # ordena por proxima renovacao
    def chave_ren(c):
        r = c.get("renovacao")
        try:
            return parse_data(r)
        except ValueError:
            return date(2999, 1, 1)
    for c in sorted(clientes, key=chave_ren):
        sem = saude.get(str(c.get("id")), {}).get("semaforo", "")
        emo = emoji_semaforo(sem) if sem else "⚪"
        val = parse_dinheiro(c.get("valor"))
        me = mensal_equivalente(val, c.get("ciclo"))
        ren = c.get("renovacao")
        dren = ""
        if ren:
            try:
                dias = (parse_data(ren) - hoje).days
                dren = f"renova em {dias}d ({br_data(ren)})"
            except ValueError:
                dren = ""
        st = c.get("status")
        marca_st = "" if st in ("ativo",) else f" [{st}]"
        print(f"  #{c.get('id')} {emo} {c.get('nome')}{marca_st} - {brl(me)}/mes"
              f"{' - ' + dren if dren else ''}")
        if c.get("servico"):
            print(f"      servico: {c.get('servico')}  contato: {c.get('contato') or '-'}")
    print()


def cmd_saude(args):
    clientes = ler_clientes()
    c = achar_cliente(clientes, args.id)
    if not c:
        print(f"ERRO - cliente #{args.id} nao encontrado.")
        return
    sinais = {
        "pagamento": args.pagamento, "engajamento": args.engajamento,
        "satisfacao": args.satisfacao, "resultado": args.resultado,
        "relacionamento": args.relacionamento,
    }
    score, semaforo, motivo, fatores = calcular_saude(
        sinais, args.dias_sem_contato, args.reclamacao or "n")
    saude = ler_saude()
    saude.append({
        "id_cliente": str(args.id),
        "data": iso(date.today()),
        "pagamento": args.pagamento, "engajamento": args.engajamento,
        "satisfacao": args.satisfacao, "resultado": args.resultado,
        "relacionamento": args.relacionamento,
        "dias_sem_contato": args.dias_sem_contato if args.dias_sem_contato is not None else "",
        "reclamacao": args.reclamacao or "n",
        "score": score, "semaforo": semaforo, "motivo": motivo,
    })
    _escrever(SAUDE, SAUDE_COLS, saude)
    # se ficou vermelho, sinaliza o status do cliente como em_risco
    if semaforo == "vermelho" and c.get("status") == "ativo":
        c["status"] = "em_risco"
        _escrever(CLIENTES, CLI_COLS, clientes)
    print(f"{emoji_semaforo(semaforo)} {c.get('nome')} - saude {score}/100 ({semaforo.upper()})")
    print(f"   Por que: {motivo}")
    if semaforo == "vermelho":
        print("   ACAO: rode o modo Salvar (save play) antes da renovacao.")
    elif semaforo == "amarelo":
        print("   ACAO: um plano escrito e um proximo passo com data.")
    else:
        print("   ACAO: cadencia normal. Cliente saudavel e candidato a expansao.")


def cmd_saude_ver(args):
    clientes = ler_clientes()
    atual = saude_atual_por_cliente()
    alvo = [achar_cliente(clientes, args.id)] if args.id else clientes
    alvo = [c for c in alvo if c]
    if not alvo:
        print("Nenhum cliente para mostrar.")
        return
    for c in alvo:
        s = atual.get(str(c.get("id")))
        if not s:
            print(f"  ⚪ #{c.get('id')} {c.get('nome')} - sem avaliacao de saude ainda "
                  f"(rode 'saude --id {c.get('id')}').")
            continue
        print(f"  {emoji_semaforo(s.get('semaforo'))} #{c.get('id')} {c.get('nome')} - "
              f"{s.get('score')}/100 ({s.get('semaforo')}) - {s.get('motivo')}")
        print(f"      avaliado em {br_data(s.get('data'))}")


def _risco_valor(c, saude):
    """Peso de prioridade = grau de risco x valor mensal (para ordenar quem tratar antes)."""
    sem = saude.get(str(c.get("id")), {}).get("semaforo", "")
    grau = {"vermelho": 3, "amarelo": 2, "verde": 1}.get(sem, 1)
    me = mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo"))
    return grau * me, grau, me, sem


def cmd_renovacao(args):
    dias = args.dias or 90
    clientes = [c for c in ler_clientes() if c.get("status") in ("ativo", "em_risco", "pausado")]
    saude = saude_atual_por_cliente()
    hoje = date.today()
    proximos = []
    for c in clientes:
        ren = c.get("renovacao")
        if not ren:
            continue
        try:
            d = (parse_data(ren) - hoje).days
        except ValueError:
            continue
        if d <= dias:
            proximos.append((d, c))
    if not proximos:
        print(f"Nenhuma renovacao nos proximos {dias} dias. "
              "Dica: mantenha a data de renovacao de cada cliente no cadastro.")
        return
    # ordena por (risco x valor) desc e, em empate, pela renovacao mais proxima
    def chave(t):
        d, c = t
        pv, grau, me, sem = _risco_valor(c, saude)
        return (-pv, d)
    proximos.sort(key=chave)
    receita_exposta = 0.0
    print(f"RADAR DE RENOVACAO - proximos {dias} dias (ordenado por risco x valor)\n")
    for d, c in proximos:
        pv, grau, me, sem = _risco_valor(c, saude)
        emo = emoji_semaforo(sem) if sem else "⚪"
        quando = "VENCIDA" if d < 0 else ("hoje" if d == 0 else f"em {d} dias")
        s = saude.get(str(c.get("id")), {})
        motivo = s.get("motivo", "sem avaliacao de saude")
        if sem in ("vermelho", "amarelo"):
            receita_exposta += me
        print(f"  {emo} #{c.get('id')} {c.get('nome')} - renova {quando} "
              f"({br_data(c.get('renovacao'))}) - {brl(me)}/mes")
        print(f"      {motivo}")
    print(f"\nReceita em risco nesta janela (amarelos+vermelhos): {brl(receita_exposta)}/mes")
    print("Comece de cima: e onde ha mais dinheiro exposto ao maior risco.")


def cmd_ev(args):
    clientes = ler_clientes()
    c = achar_cliente(clientes, args.id)
    if not c:
        print(f"ERRO - cliente #{args.id} nao encontrado.")
        return
    me = mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo"))
    horizonte = args.horizonte if args.horizonte else 12
    valor_em_jogo = round(me * horizonte, 2)
    p = max(0.0, min(1.0, (args.prob or 0) / 100.0))
    custo = parse_dinheiro(args.custo)
    ev = round(p * valor_em_jogo - custo, 2)
    # probabilidade de equilibrio: a partir de que chance o resgate compensa
    breakeven = (custo / valor_em_jogo * 100) if valor_em_jogo > 0 else 0
    print(f"DECISAO DE RESGATE - {c.get('nome')}")
    print(f"  Valor em jogo:        {brl(me)}/mes x {horizonte} meses = {brl(valor_em_jogo)}")
    print(f"  Chance de reter:      {p*100:.0f}%")
    print(f"  Custo do resgate:     {brl(custo)} (desconto + esforco)")
    print(f"  Valor esperado (EV):  {p*100:.0f}% x {brl(valor_em_jogo)} - {brl(custo)} = {brl(ev)}")
    print(f"  Ponto de equilibrio:  compensa se a chance de reter for > {breakeven:.0f}%")
    if ev > 0:
        print("  >> VALE A PENA tentar salvar: o retorno esperado supera o custo.")
    else:
        print("  >> NAO compensa investir pesado. Faca UMA tentativa honesta e barata; "
              "se nao voltar, deixe ir com dignidade e foque a energia em quem esta saudavel.")


def cmd_toque(args):
    clientes = ler_clientes()
    c = achar_cliente(clientes, args.id)
    if not c:
        print(f"ERRO - cliente #{args.id} nao encontrado.")
        return
    inter = ler_interacoes()
    inter.append({
        "data": iso(parse_data(args.data)) if args.data else iso(date.today()),
        "id_cliente": str(args.id),
        "tipo": (args.tipo or "checkin").strip().lower(),
        "nota": (args.nota or "").strip(),
    })
    _escrever(INTERACOES, INT_COLS, inter)
    print(f"OK - toque registrado com {c.get('nome')} ({args.tipo or 'checkin'}).")


def _ultimo_toque_por_cliente():
    inter = ler_interacoes()
    ult = {}
    for i in inter:
        cid = str(i.get("id_cliente"))
        d = i.get("data", "")
        if cid not in ult or d >= ult[cid]:
            ult[cid] = d
    return ult


def cmd_toques(args):
    clientes = ler_clientes()
    hoje = date.today()
    if args.id:
        inter = [i for i in ler_interacoes() if str(i.get("id_cliente")) == str(args.id)]
        c = achar_cliente(clientes, args.id)
        nome = c.get("nome") if c else f"#{args.id}"
        if not inter:
            print(f"Nenhum toque registrado com {nome} ainda.")
            return
        print(f"HISTORICO DE TOQUES - {nome}\n")
        for i in sorted(inter, key=lambda x: x.get("data", ""), reverse=True):
            print(f"  {br_data(i.get('data'))} - {i.get('tipo')}: {i.get('nota') or '-'}")
        return
    # sem --id: quem esta ha X dias sem toque
    limite = args.sem_contato if args.sem_contato else 30
    ult = _ultimo_toque_por_cliente()
    ativos = [c for c in clientes if c.get("status") in ("ativo", "em_risco")]
    pendentes = []
    for c in ativos:
        d = ult.get(str(c.get("id")))
        if not d:
            pendentes.append((9999, c, "nunca"))
            continue
        try:
            dias = (hoje - parse_data(d)).days
        except ValueError:
            dias = 9999
        if dias >= limite:
            pendentes.append((dias, c, f"{dias} dias"))
    if not pendentes:
        print(f"Todo mundo com toque nos ultimos {limite} dias. Relacionamento em dia. 👏")
        return
    pendentes.sort(key=lambda t: -t[0])
    print(f"PRECISAM DE UM TOQUE - sem contato ha {limite}+ dias\n")
    for dias, c, txt in pendentes:
        me = mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo"))
        print(f"  #{c.get('id')} {c.get('nome')} - ultimo toque: {txt} - {brl(me)}/mes")
    print("\nSugira um check-in no seu tom; quem envia e voce (WhatsApp na frente).")


def cmd_oportunidade_add(args):
    clientes = ler_clientes()
    c = achar_cliente(clientes, args.id)
    if not c:
        print(f"ERRO - cliente #{args.id} nao encontrado.")
        return
    opp = ler_oport()
    oid = proximo_id(opp)
    opp.append({
        "id": oid,
        "id_cliente": str(args.id),
        "tipo": (args.tipo or "mais_servico").strip().lower(),
        "descricao": (args.descricao or "").strip(),
        "valor": f"{parse_dinheiro(args.valor):.2f}",
        "status": "aberta",
        "criado": iso(date.today()),
    })
    _escrever(OPORT, OPP_COLS, opp)
    print(f"OK - oportunidade #{oid} aberta em {c.get('nome')}: "
          f"{args.descricao} (+{brl(parse_dinheiro(args.valor))}/mes potencial).")


def cmd_oportunidades(args):
    clientes = ler_clientes()
    opp = ler_oport()
    if args.abertas:
        opp = [o for o in opp if o.get("status") == "aberta"]
    if not opp:
        print("Nenhuma oportunidade de expansao registrada.")
        return
    saude = saude_atual_por_cliente()
    total = 0.0
    print("OPORTUNIDADES DE EXPANSAO\n")
    for o in opp:
        c = achar_cliente(clientes, o.get("id_cliente"))
        nome = c.get("nome") if c else f"#{o.get('id_cliente')}"
        sem = saude.get(str(o.get("id_cliente")), {}).get("semaforo", "")
        emo = emoji_semaforo(sem) if sem else "⚪"
        v = parse_dinheiro(o.get("valor"))
        if o.get("status") == "aberta":
            total += v
        alerta = ""
        if sem in ("amarelo", "vermelho"):
            alerta = "  ⚠️ so expanda cliente saudavel - primeiro recupere a saude"
        print(f"  #{o.get('id')} {emo} {nome} - {o.get('tipo')}: {o.get('descricao')} "
              f"(+{brl(v)}/mes) [{o.get('status')}]{alerta}")
    print(f"\nPotencial de expansao em aberto: +{brl(total)}/mes")


def cmd_painel(args):
    clientes = ler_clientes()
    if not clientes:
        print("Carteira vazia. Cadastre seus clientes recorrentes com 'cliente-add'.")
        return
    saude = saude_atual_por_cliente()
    hoje = date.today()
    ativos = [c for c in clientes if c.get("status") in ("ativo", "em_risco", "pausado")]
    ativos_pagantes = [c for c in clientes if c.get("status") in ("ativo", "em_risco")]
    mrr = sum(mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo")) for c in ativos_pagantes)

    cont = {"verde": 0, "amarelo": 0, "vermelho": 0, "sem": 0}
    risco_valor = 0.0
    for c in ativos_pagantes:
        sem = saude.get(str(c.get("id")), {}).get("semaforo", "")
        if sem in cont:
            cont[sem] += 1
        else:
            cont["sem"] += 1
        if sem in ("amarelo", "vermelho"):
            risco_valor += mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo"))

    # churn nos ultimos 30 dias
    jan = hoje - timedelta(days=30)
    cancelados = []
    for c in clientes:
        if c.get("status") == "cancelado" and c.get("cancelado_em"):
            try:
                if parse_data(c.get("cancelado_em")) >= jan:
                    cancelados.append(c)
            except ValueError:
                pass
    receita_perdida = sum(mensal_equivalente(parse_dinheiro(c.get("valor")), c.get("ciclo")) for c in cancelados)
    base_ini = len(ativos_pagantes) + len(cancelados)
    churn = (len(cancelados) / base_ini * 100) if base_ini else 0

    # renovacoes proximas (30 dias)
    ren30 = []
    for c in ativos_pagantes:
        r = c.get("renovacao")
        if not r:
            continue
        try:
            d = (parse_data(r) - hoje).days
            if 0 <= d <= 30:
                ren30.append((d, c))
        except ValueError:
            pass

    # sem toque ha 30+ dias
    ult = _ultimo_toque_por_cliente()
    sem_toque = 0
    for c in ativos_pagantes:
        d = ult.get(str(c.get("id")))
        if not d:
            sem_toque += 1
            continue
        try:
            if (hoje - parse_data(d)).days >= 30:
                sem_toque += 1
        except ValueError:
            sem_toque += 1

    opp_abertas = [o for o in ler_oport() if o.get("status") == "aberta"]
    pot_exp = sum(parse_dinheiro(o.get("valor")) for o in opp_abertas)

    print("=" * 52)
    print("  PAINEL DA CARTEIRA - Ancora")
    print("=" * 52)
    print(f"  Clientes ativos:        {len(ativos_pagantes)}")
    print(f"  MRR (receita recorrente): {brl(mrr)}/mes")
    print(f"  Saude:  🟢 {cont['verde']}   🟡 {cont['amarelo']}   🔴 {cont['vermelho']}"
          f"   ⚪ {cont['sem']} (sem avaliar)")
    print(f"  Receita em risco:       {brl(risco_valor)}/mes (amarelos + vermelhos)")
    print(f"  Churn ultimos 30 dias:  {len(cancelados)} cliente(s) = {churn:.0f}% "
          f"(perda de {brl(receita_perdida)}/mes)")
    print(f"  Renovam em ate 30 dias: {len(ren30)}")
    print(f"  Sem toque ha 30+ dias:  {sem_toque}")
    print(f"  Expansao em aberto:     +{brl(pot_exp)}/mes ({len(opp_abertas)} oportunidade(s))")
    print("=" * 52)
    # o que fazer agora
    acoes = []
    if cont["vermelho"]:
        acoes.append(f"Rodar o SAVE PLAY nos {cont['vermelho']} vermelho(s) antes da renovacao.")
    if ren30:
        acoes.append(f"Confirmar as {len(ren30)} renovacao(oes) dos proximos 30 dias.")
    if cont["sem"]:
        acoes.append(f"Avaliar a saude dos {cont['sem']} cliente(s) ainda sem semaforo.")
    if sem_toque:
        acoes.append(f"Dar um toque nos {sem_toque} cliente(s) sem contato ha 30+ dias.")
    if opp_abertas:
        acoes.append(f"Avancar a expansao (+{brl(pot_exp)}/mes) nos clientes saudaveis.")
    if acoes:
        print("  PROXIMAS ACOES:")
        for i, a in enumerate(acoes, 1):
            print(f"   {i}. {a}")
    else:
        print("  Carteira saudavel e sob controle. 👏")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    p = argparse.ArgumentParser(prog="ancora", description="Motor de retencao de carteira (Ancora).")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init")

    a = sub.add_parser("cliente-add")
    a.add_argument("--nome", required=True)
    a.add_argument("--contato")
    a.add_argument("--servico")
    a.add_argument("--valor", required=True)
    a.add_argument("--ciclo", default="mensal")
    a.add_argument("--inicio")
    a.add_argument("--renovacao")
    a.add_argument("--status", default="ativo")
    a.add_argument("--canal")
    a.add_argument("--obs")

    e = sub.add_parser("cliente-editar")
    e.add_argument("--id", required=True)
    for campo in ("nome", "contato", "servico", "valor", "ciclo", "inicio", "renovacao", "canal", "obs"):
        e.add_argument(f"--{campo}")

    st = sub.add_parser("cliente-status")
    st.add_argument("--id", required=True)
    st.add_argument("--status", required=True)
    st.add_argument("--data")
    st.add_argument("--motivo")

    cl = sub.add_parser("clientes")
    cl.add_argument("--status")

    s = sub.add_parser("saude")
    s.add_argument("--id", required=True)
    for sig in SINAIS:
        s.add_argument(f"--{sig}", type=int, default=1)
    s.add_argument("--dias-sem-contato", dest="dias_sem_contato", type=int)
    s.add_argument("--reclamacao", default="n")

    sv = sub.add_parser("saude-ver")
    sv.add_argument("--id")

    r = sub.add_parser("renovacao")
    r.add_argument("--dias", type=int, default=90)

    ev = sub.add_parser("ev")
    ev.add_argument("--id", required=True)
    ev.add_argument("--prob", type=float, required=True)
    ev.add_argument("--custo", default="0")
    ev.add_argument("--horizonte", type=int, default=12)

    t = sub.add_parser("toque")
    t.add_argument("--id", required=True)
    t.add_argument("--tipo", default="checkin")
    t.add_argument("--nota")
    t.add_argument("--data")

    ts = sub.add_parser("toques")
    ts.add_argument("--id")
    ts.add_argument("--sem-contato", dest="sem_contato", type=int)

    oa = sub.add_parser("oportunidade-add")
    oa.add_argument("--id", required=True)
    oa.add_argument("--tipo", default="mais_servico")
    oa.add_argument("--descricao")
    oa.add_argument("--valor", default="0")

    op = sub.add_parser("oportunidades")
    op.add_argument("--abertas", action="store_true")

    sub.add_parser("painel")
    return p


COMANDOS = {
    "init": cmd_init,
    "cliente-add": cmd_cliente_add,
    "cliente-editar": cmd_cliente_editar,
    "cliente-status": cmd_cliente_status,
    "clientes": cmd_clientes,
    "saude": cmd_saude,
    "saude-ver": cmd_saude_ver,
    "renovacao": cmd_renovacao,
    "ev": cmd_ev,
    "toque": cmd_toque,
    "toques": cmd_toques,
    "oportunidade-add": cmd_oportunidade_add,
    "oportunidades": cmd_oportunidades,
    "painel": cmd_painel,
}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0
    func = COMANDOS.get(args.cmd)
    if not func:
        parser.print_help()
        return 1
    try:
        func(args)
    except ValueError as e:
        print(f"ERRO - {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
