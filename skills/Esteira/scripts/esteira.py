#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Esteira — motor do rastreador de pipeline comercial (funil de negociações).

Acompanha TODA negociação em aberto por etapa, ranqueia o que precisa de
atenção hoje, avisa quando um negócio está esfriando, prevê quanto deve fechar
(valor × probabilidade) e ajuda a fechar — ganho ou perdido (com o motivo, para
aprender). Usa SOMENTE a biblioteca padrão do Python. Nunca inventa nada: tudo
que sai daqui veio dos negócios que o dono registrou.

Arquivo de dados (.esteira/negocios.csv), com cabeçalho:
    id,cliente,contato,valor,etapa,probabilidade,origem,entrou_em,
    ultimo_contato,proximo_passo,proximo_passo_em,status,fechado_em,
    motivo_perda,observacoes

  - id: número sequencial (o motor cuida)
  - cliente: nome do cliente/empresa
  - contato: telefone, e-mail ou como falar (opcional)
  - valor: valor do negócio em R$ (aceita "R$ 1.234,56", "1.234,56", "1234.56")
  - etapa: lead | qualificado | reuniao | proposta | negociacao | ganho | perdido
  - probabilidade: 0-100 (opcional; se vazio, usa o padrão da etapa)
  - origem: de onde veio (indicacao, instagram, anuncio, prospeccao...) (opcional)
  - entrou_em / ultimo_contato / proximo_passo_em / fechado_em: YYYY-MM-DD (alguns podem ser vazios)
  - proximo_passo: o que fazer a seguir (ex.: "ligar para tirar dúvida")
  - status: aberto | ganho | perdido (derivado da etapa)
  - motivo_perda: por que perdeu (só quando perdido)
  - observacoes: notas livres

Comandos:
    python3 esteira.py adicionar --cliente "..." --valor "R$ 2.000" [--etapa lead]
        [--origem indicacao] [--contato "..."] [--proximo "..."] [--proximo-em DD/MM] [--obs "..."]
        [--entrou-em DD/MM] [--ultimo-contato DD/MM]   # para negócios que já vinham antes da Esteira
    python3 esteira.py mover --id N --etapa proposta [--proximo "..."] [--proximo-em DD/MM]
    python3 esteira.py tocar --id N [--proximo "..."] [--proximo-em DD/MM]   # registra contato (sem mudar etapa)
    python3 esteira.py ganhar --id N
    python3 esteira.py perder --id N --motivo "preço"
    python3 esteira.py hoje                 # negócios que precisam de atenção hoje, ranqueados
    python3 esteira.py esfriando            # negócios parados (sem contato além do limite da etapa)
    python3 esteira.py previsao [--meta "R$ 30.000"]   # previsão ponderada do que deve fechar
    python3 esteira.py funil                # visão do funil: quanto/quantos por etapa + conversão
    python3 esteira.py listar [--etapa X] [--status aberto|ganho|perdido|todos]
    python3 esteira.py editar --id N [--cliente ...] [--valor ...] [--prob N] [--origem ...]
        [--contato ...] [--proximo ...] [--proximo-em DD/MM] [--obs ...]
    python3 esteira.py remover --id N
Opções globais: --arquivo <csv>  (padrão: .esteira/negocios.csv)
                --formato json   (padrão: texto)
"""

import argparse
import csv
import json
import os
import sys
import unicodedata
from datetime import date, datetime

ARQUIVO_PADRAO = os.path.join(".esteira", "negocios.csv")
CABECALHO = ["id", "cliente", "contato", "valor", "etapa", "probabilidade",
             "origem", "entrou_em", "ultimo_contato", "proximo_passo",
             "proximo_passo_em", "status", "fechado_em", "motivo_perda",
             "observacoes"]

# Etapas do funil, em ordem, com a probabilidade PADRÃO de fechar e o limite
# (dias sem contato) a partir do qual o negócio é considerado "esfriando".
# As probabilidades são padrões honestos do mercado de serviços — o dono pode
# ajustar negócio a negócio. Quanto mais perto do fim, mais rápido esfria.
ETAPAS = ["lead", "qualificado", "reuniao", "proposta", "negociacao", "ganho", "perdido"]
PROB_PADRAO = {"lead": 10, "qualificado": 25, "reuniao": 45,
               "proposta": 60, "negociacao": 80, "ganho": 100, "perdido": 0}
LIMIAR_FRIO = {"lead": 3, "qualificado": 5, "reuniao": 5,
               "proposta": 4, "negociacao": 3}
NOME_ETAPA = {"lead": "Lead (contato novo)", "qualificado": "Qualificado",
              "reuniao": "Reunião/Diagnóstico", "proposta": "Proposta enviada",
              "negociacao": "Negociação", "ganho": "Ganho", "perdido": "Perdido"}
ABERTAS = ["lead", "qualificado", "reuniao", "proposta", "negociacao"]


# ---------------------------------------------------------------- utilidades

def _norm(s):
    """minúsculas e sem acento, para comparação tolerante."""
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def parse_etapa(bruto):
    """Aceita 'reunião', 'Proposta', 'negociacao' etc. None se inválida."""
    n = _norm(bruto)
    apelidos = {
        "lead": "lead", "novo": "lead", "contato": "lead",
        "qualificado": "qualificado", "qualificada": "qualificado", "qual": "qualificado",
        "reuniao": "reuniao", "reuniões": "reuniao", "diagnostico": "reuniao",
        "call": "reuniao", "demo": "reuniao", "visita": "reuniao",
        "proposta": "proposta", "orcamento": "proposta", "orçamento": "proposta",
        "negociacao": "negociacao", "negociando": "negociacao", "nego": "negociacao",
        "ganho": "ganho", "ganhou": "ganho", "fechado": "ganho", "fechou": "ganho",
        "perdido": "perdido", "perdeu": "perdido", "perda": "perdido",
    }
    return apelidos.get(n)


def parse_valor(bruto):
    """Converte 'R$ 1.234,56' / '3.500' / '1234.56' / '2000' em float (reais).
    Trata a notação BR: vírgula é decimal; ponto é separador de milhar quando
    seguido de exatamente 3 dígitos (ex.: '3.500' = 3500). None se inválido."""
    s = (bruto or "").strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    if "," in s:                          # tem vírgula → ponto=milhar, vírgula=decimal
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:                        # só ponto(s), sem vírgula → decidir o papel
        partes = s.split(".")
        # vários pontos (1.234.567) OU último grupo com 3 dígitos (3.500) = milhar
        if len(partes) > 2 or len(partes[-1]) == 3:
            s = s.replace(".", "")
        # senão (3.5 / 3.50) é decimal de verdade → mantém
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def brl(v):
    """Formata 1234.5 como 'R$ 1.234,50'."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "R$ 0,00"
    neg = v < 0
    inteiro = int(abs(v))
    cent = int(round((abs(v) - inteiro) * 100))
    if cent == 100:
        inteiro += 1
        cent = 0
    txt = "{:,}".format(inteiro).replace(",", ".")
    return ("-" if neg else "") + "R$ {},{:02d}".format(txt, cent)


def parse_data(bruto, hoje=None):
    """Aceita YYYY-MM-DD, DD/MM/YYYY ou DD/MM (ano atual). None se vazio/inválido."""
    s = (bruto or "").strip()
    if not s:
        return None
    hoje = hoje or date.today()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    try:
        d, m = s.split("/")[:2]
        return date(hoje.year, int(m), int(d))
    except (ValueError, IndexError):
        return None


def fmt_data(d):
    return d.strftime("%d/%m/%Y") if d else ""


def iso(d):
    return d.strftime("%Y-%m-%d") if d else ""


def prob_de(neg):
    """Probabilidade efetiva de um negócio: a informada, ou o padrão da etapa."""
    p = (neg.get("probabilidade") or "").strip()
    if p:
        try:
            return max(0, min(100, int(float(p))))
        except ValueError:
            pass
    return PROB_PADRAO.get(neg.get("etapa"), 0)


def valor_de(neg):
    return parse_valor(neg.get("valor")) or 0.0


def esperado(neg):
    """Valor esperado = valor × probabilidade (o quanto esse negócio 'vale' hoje)."""
    return valor_de(neg) * prob_de(neg) / 100.0


# ---------------------------------------------------------------- persistência

def carregar(arquivo):
    if not os.path.exists(arquivo):
        return []
    negocios = []
    with open(arquivo, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if not (row.get("cliente") or "").strip():
                continue
            for c in CABECALHO:
                row.setdefault(c, "")
            negocios.append(row)
    return negocios


def salvar(arquivo, negocios):
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    with open(arquivo, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO)
        w.writeheader()
        for n in negocios:
            w.writerow({c: n.get(c, "") for c in CABECALHO})


def proximo_id(negocios):
    ids = [int(n["id"]) for n in negocios if str(n.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


def achar(negocios, _id):
    for n in negocios:
        if str(n.get("id")) == str(_id):
            return n
    return None


def status_de(etapa):
    if etapa == "ganho":
        return "ganho"
    if etapa == "perdido":
        return "perdido"
    return "aberto"


# ---------------------------------------------------------------- priorização

def avaliar(neg, hoje):
    """Calcula uma nota EXPLICÁVEL de atenção para um negócio aberto.
    Retorna (nota, motivos[], precisa_hoje). Quanto maior, mais urgente."""
    motivos = []
    etapa = neg.get("etapa")

    # 1) valor esperado — negócios maiores e mais perto de fechar pedem mais atenção
    ve = esperado(neg)
    comp_valor = min(ve / 1000.0, 10.0)      # satura em R$ 10k esperado
    if ve > 0:
        motivos.append("vale {} hoje (valor × {}%)".format(brl(ve), prob_de(neg)))

    # 2) próximo passo — atrasado, hoje, ou não definido
    comp_passo = 0.0
    pe = parse_data(neg.get("proximo_passo_em"), hoje)
    passo_txt = (neg.get("proximo_passo") or "").strip()
    precisa = False
    if pe:
        d = (pe - hoje).days
        if d < 0:
            comp_passo = 12.0 + min(-d, 10)
            motivos.append("próximo passo ATRASADO há {} dia(s)".format(-d))
            precisa = True
        elif d == 0:
            comp_passo = 10.0
            motivos.append("próximo passo é HOJE")
            precisa = True
        elif d <= 2:
            comp_passo = 5.0
            motivos.append("próximo passo em {} dia(s)".format(d))
    else:
        comp_passo = 3.0
        motivos.append("sem próximo passo definido")
        precisa = True

    # 3) esfriamento — tempo sem contato acima do limite da etapa
    comp_frio = 0.0
    uc = parse_data(neg.get("ultimo_contato"), hoje) or parse_data(neg.get("entrou_em"), hoje)
    if uc:
        parado = (hoje - uc).days
        limite = LIMIAR_FRIO.get(etapa, 5)
        if parado >= limite:
            comp_frio = 6.0 + min(parado - limite, 10)
            motivos.append("esfriando: {} dia(s) sem contato (limite {} nesta etapa)".format(parado, limite))
            precisa = True

    nota = round(comp_valor + comp_passo + comp_frio, 2)
    if passo_txt:
        motivos.append('próximo passo: "{}"'.format(passo_txt))
    return nota, motivos, precisa


# ---------------------------------------------------------------- saída

def _print(payload, como_json):
    if como_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False))


def linha_neg(neg):
    et = NOME_ETAPA.get(neg.get("etapa"), neg.get("etapa"))
    return "#{} {} — {} — {} ({}%)".format(
        neg.get("id"), neg.get("cliente"), brl(valor_de(neg)), et, prob_de(neg))


# ---------------------------------------------------------------- comandos

def cmd_adicionar(args, negocios, arquivo, hoje, como_json):
    etapa = parse_etapa(args.etapa) or "lead" if args.etapa else "lead"
    if args.etapa and not parse_etapa(args.etapa):
        _print("Etapa inválida: '{}'. Use: {}".format(args.etapa, ", ".join(ABERTAS)), como_json)
        return 1
    valor = parse_valor(args.valor)
    entrou = parse_data(args.entrou_em, hoje) or hoje
    # último contato: o informado, senão a data de entrada (permite negócios
    # que já vinham acontecendo antes de entrarem na Esteira — assim o detector
    # de "esfriando" funciona em quem você cadastra hoje mas falou faz dias).
    ultimo = parse_data(args.ultimo_contato, hoje) or entrou
    novo = {
        "id": str(proximo_id(negocios)),
        "cliente": (args.cliente or "").strip(),
        "contato": (args.contato or "").strip(),
        "valor": "" if valor is None else "{:.2f}".format(valor),
        "etapa": etapa,
        "probabilidade": str(args.prob) if args.prob is not None else "",
        "origem": (args.origem or "").strip(),
        "entrou_em": iso(entrou),
        "ultimo_contato": iso(ultimo),
        "proximo_passo": (args.proximo or "").strip(),
        "proximo_passo_em": iso(parse_data(args.proximo_em, hoje)),
        "status": "aberto",
        "fechado_em": "",
        "motivo_perda": "",
        "observacoes": (args.obs or "").strip(),
    }
    if not novo["cliente"]:
        _print("Falta o nome do cliente (--cliente).", como_json)
        return 1
    negocios.append(novo)
    salvar(arquivo, negocios)
    if como_json:
        _print(novo, True)
    else:
        _print("✅ Negócio registrado:\n   " + linha_neg(novo) +
               ("\n   próximo passo: " + novo["proximo_passo"] if novo["proximo_passo"] else ""), False)
    return 0


def cmd_mover(args, negocios, arquivo, hoje, como_json):
    neg = achar(negocios, args.id)
    if not neg:
        _print("Não achei o negócio #{}.".format(args.id), como_json)
        return 1
    etapa = parse_etapa(args.etapa)
    if not etapa:
        _print("Etapa inválida: '{}'.".format(args.etapa), como_json)
        return 1
    antes = neg.get("etapa")
    neg["etapa"] = etapa
    neg["status"] = status_de(etapa)
    neg["ultimo_contato"] = iso(hoje)
    if etapa in ("ganho", "perdido"):
        neg["fechado_em"] = iso(hoje)
    if args.proximo is not None:
        neg["proximo_passo"] = args.proximo.strip()
    if args.proximo_em is not None:
        neg["proximo_passo_em"] = iso(parse_data(args.proximo_em, hoje))
    salvar(arquivo, negocios)
    if como_json:
        _print(neg, True)
    else:
        _print("➡️  #{} {} moveu de {} para {}.".format(
            neg["id"], neg["cliente"], NOME_ETAPA.get(antes, antes), NOME_ETAPA.get(etapa, etapa)), False)
    return 0


def cmd_tocar(args, negocios, arquivo, hoje, como_json):
    neg = achar(negocios, args.id)
    if not neg:
        _print("Não achei o negócio #{}.".format(args.id), como_json)
        return 1
    neg["ultimo_contato"] = iso(hoje)
    if args.proximo is not None:
        neg["proximo_passo"] = args.proximo.strip()
    if args.proximo_em is not None:
        neg["proximo_passo_em"] = iso(parse_data(args.proximo_em, hoje))
    salvar(arquivo, negocios)
    _print("📞 Contato registrado em #{} {} (hoje).".format(neg["id"], neg["cliente"]), como_json) \
        if not como_json else _print(neg, True)
    return 0


def cmd_fechar(args, negocios, arquivo, hoje, como_json, ganhar):
    neg = achar(negocios, args.id)
    if not neg:
        _print("Não achei o negócio #{}.".format(args.id), como_json)
        return 1
    neg["etapa"] = "ganho" if ganhar else "perdido"
    neg["status"] = status_de(neg["etapa"])
    neg["fechado_em"] = iso(hoje)
    neg["proximo_passo"] = ""
    neg["proximo_passo_em"] = ""
    if not ganhar:
        neg["motivo_perda"] = (args.motivo or "").strip()
    salvar(arquivo, negocios)
    if como_json:
        _print(neg, True)
    elif ganhar:
        _print("🎉 #{} {} marcado como GANHO ({}). Parabéns!".format(
            neg["id"], neg["cliente"], brl(valor_de(neg))), False)
    else:
        mt = " — motivo: " + neg["motivo_perda"] if neg["motivo_perda"] else ""
        _print("❌ #{} {} marcado como PERDIDO{}.".format(neg["id"], neg["cliente"], mt), False)
    return 0


def cmd_hoje(args, negocios, arquivo, hoje, como_json):
    abertos = [n for n in negocios if n.get("etapa") in ABERTAS]
    itens = []
    for n in abertos:
        nota, motivos, precisa = avaliar(n, hoje)
        if precisa:
            itens.append((nota, n, motivos))
    itens.sort(key=lambda t: t[0], reverse=True)
    if como_json:
        _print([{"nota": nota, "negocio": linha_neg(n), "id": n["id"],
                 "cliente": n["cliente"], "motivos": motivos} for nota, n, motivos in itens], True)
        return 0
    if not itens:
        _print("👍 Nada pegando fogo hoje. Nenhum negócio atrasado ou esfriando.\n"
               "Quer ver o funil inteiro? Rode 'funil'. Quer a previsão? Rode 'previsao'.", False)
        return 0
    linhas = ["🎯 Negócios que pedem atenção hoje ({}):\n".format(len(itens))]
    for i, (nota, n, motivos) in enumerate(itens, 1):
        marca = "⭐ " if i <= 3 else "   "
        linhas.append("{}{}. {}".format(marca, i, linha_neg(n)))
        for m in motivos:
            linhas.append("       • " + m)
        linhas.append("")
    linhas.append("Comece pelos ⭐ (os 3 de maior atenção). Eu sugiro o próximo toque — você envia.")
    _print("\n".join(linhas), False)
    return 0


def cmd_esfriando(args, negocios, arquivo, hoje, como_json):
    frios = []
    for n in negocios:
        if n.get("etapa") not in ABERTAS:
            continue
        uc = parse_data(n.get("ultimo_contato"), hoje) or parse_data(n.get("entrou_em"), hoje)
        if not uc:
            continue
        parado = (hoje - uc).days
        limite = LIMIAR_FRIO.get(n.get("etapa"), 5)
        if parado >= limite:
            frios.append((parado, limite, n))
    frios.sort(key=lambda t: t[0], reverse=True)
    if como_json:
        _print([{"id": n["id"], "cliente": n["cliente"], "dias_parado": p,
                 "limite": lim, "negocio": linha_neg(n)} for p, lim, n in frios], True)
        return 0
    if not frios:
        _print("🌡️  Nenhum negócio esfriando. Todos tiveram contato dentro do prazo da etapa.", False)
        return 0
    linhas = ["🌡️  Negócios esfriando ({}) — sem contato além do limite da etapa:\n".format(len(frios))]
    for p, lim, n in frios:
        linhas.append("   • {}  →  {} dia(s) sem contato (limite {})".format(linha_neg(n), p, lim))
    linhas.append("\nReaqueça com um toque leve. Use o modo 'próximo toque' da Esteira pra eu sugerir a mensagem.")
    _print("\n".join(linhas), False)
    return 0


def cmd_previsao(args, negocios, arquivo, hoje, como_json):
    abertos = [n for n in negocios if n.get("etapa") in ABERTAS]
    total_bruto = sum(valor_de(n) for n in abertos)
    total_pond = sum(esperado(n) for n in abertos)
    por_etapa = {}
    for et in ABERTAS:
        ns = [n for n in abertos if n.get("etapa") == et]
        por_etapa[et] = {
            "qtd": len(ns),
            "bruto": sum(valor_de(n) for n in ns),
            "ponderado": sum(esperado(n) for n in ns),
        }
    meta = parse_valor(args.meta) if args.meta else None
    if como_json:
        _print({"total_bruto": total_bruto, "total_ponderado": total_pond,
                "meta": meta, "por_etapa": por_etapa}, True)
        return 0
    linhas = ["🔮 Previsão do pipeline (valor × probabilidade de cada etapa):\n"]
    for et in ABERTAS:
        d = por_etapa[et]
        if d["qtd"]:
            linhas.append("   {:<22} {:>2} negócio(s) | bruto {:>14} | esperado {:>14}".format(
                NOME_ETAPA[et], d["qtd"], brl(d["bruto"]), brl(d["ponderado"])))
    linhas.append("   " + "-" * 68)
    linhas.append("   {:<22} {:>2} negócio(s) | bruto {:>14} | esperado {:>14}".format(
        "TOTAL EM ABERTO", len(abertos), brl(total_bruto), brl(total_pond)))
    linhas.append("\n💡 'Esperado' é a previsão realista: se nada mudar, deve entrar perto de {}.".format(brl(total_pond)))
    if meta is not None and meta > 0:
        cobertura = total_bruto / meta
        linhas.append("\n🎯 Meta informada: {}".format(brl(meta)))
        linhas.append("   Previsão ponderada vs meta: {} de {} ({:.0f}%).".format(
            brl(total_pond), brl(meta), 100 * total_pond / meta))
        linhas.append("   Cobertura do funil (valor bruto ÷ meta): {:.1f}x.".format(cobertura))
        if cobertura < 3:
            linhas.append("   ⚠️  Cobertura abaixo de 3x — o funil está magro pra essa meta. "
                          "Hora de alimentar a Esteira com mais negócios (veja a Fisga).")
        else:
            linhas.append("   ✅ Cobertura saudável (acima de 3x).")
    _print("\n".join(linhas), False)
    return 0


def cmd_funil(args, negocios, arquivo, hoje, como_json):
    abertos = [n for n in negocios if n.get("etapa") in ABERTAS]
    ganhos = [n for n in negocios if n.get("etapa") == "ganho"]
    perdidos = [n for n in negocios if n.get("etapa") == "perdido"]
    fechados = len(ganhos) + len(perdidos)
    conv = (100.0 * len(ganhos) / fechados) if fechados else None
    ticket = (sum(valor_de(n) for n in ganhos) / len(ganhos)) if ganhos else None
    # ciclo médio: dias entre entrou_em e fechado_em dos ganhos
    ciclos = []
    for n in ganhos:
        e = parse_data(n.get("entrou_em"), hoje)
        f = parse_data(n.get("fechado_em"), hoje)
        if e and f and f >= e:
            ciclos.append((f - e).days)
    ciclo = (sum(ciclos) / len(ciclos)) if ciclos else None
    if como_json:
        _print({"abertos": len(abertos), "ganhos": len(ganhos), "perdidos": len(perdidos),
                "conversao_pct": conv, "ticket_medio": ticket, "ciclo_medio_dias": ciclo}, True)
        return 0
    linhas = ["📊 Visão do funil:\n"]
    for et in ABERTAS:
        ns = [n for n in abertos if n.get("etapa") == et]
        barra = "█" * len(ns)
        linhas.append("   {:<22} {:>2}  {}  {}".format(
            NOME_ETAPA[et], len(ns), barra, brl(sum(valor_de(n) for n in ns))))
    linhas.append("")
    linhas.append("   Ganhos: {} | Perdidos: {}".format(len(ganhos), len(perdidos)))
    if conv is not None:
        linhas.append("   Taxa de conversão (ganhos ÷ fechados): {:.0f}%".format(conv))
    if ticket is not None:
        linhas.append("   Ticket médio dos ganhos: {}".format(brl(ticket)))
    if ciclo is not None:
        linhas.append("   Ciclo médio até fechar: {:.0f} dia(s)".format(ciclo))
    if perdidos:
        motivos = {}
        for n in perdidos:
            m = (n.get("motivo_perda") or "sem motivo").strip() or "sem motivo"
            motivos[m] = motivos.get(m, 0) + 1
        top = sorted(motivos.items(), key=lambda x: x[1], reverse=True)[:3]
        linhas.append("   Top motivos de perda: " + ", ".join("{} ({})".format(m, c) for m, c in top))
    _print("\n".join(linhas), False)
    return 0


def cmd_listar(args, negocios, arquivo, hoje, como_json):
    filtro_status = (args.status or "aberto").lower()
    etapa = parse_etapa(args.etapa) if args.etapa else None
    sel = []
    for n in negocios:
        st = status_de(n.get("etapa"))
        if filtro_status != "todos" and st != filtro_status:
            continue
        if etapa and n.get("etapa") != etapa:
            continue
        sel.append(n)
    sel.sort(key=lambda n: esperado(n), reverse=True)
    if como_json:
        _print([{"id": n["id"], "cliente": n["cliente"], "etapa": n["etapa"],
                 "valor": valor_de(n), "prob": prob_de(n), "esperado": esperado(n),
                 "proximo_passo": n.get("proximo_passo"),
                 "ultimo_contato": n.get("ultimo_contato")} for n in sel], True)
        return 0
    if not sel:
        _print("Nenhum negócio nesse filtro.", False)
        return 0
    linhas = ["📋 Negócios ({} | {}):\n".format(filtro_status, len(sel))]
    for n in sel:
        extra = "  →  " + n["proximo_passo"] if n.get("proximo_passo") else ""
        linhas.append("   " + linha_neg(n) + extra)
    _print("\n".join(linhas), False)
    return 0


def cmd_editar(args, negocios, arquivo, hoje, como_json):
    neg = achar(negocios, args.id)
    if not neg:
        _print("Não achei o negócio #{}.".format(args.id), como_json)
        return 1
    if args.cliente is not None:
        neg["cliente"] = args.cliente.strip()
    if args.valor is not None:
        v = parse_valor(args.valor)
        neg["valor"] = "" if v is None else "{:.2f}".format(v)
    if args.prob is not None:
        neg["probabilidade"] = str(args.prob)
    if args.origem is not None:
        neg["origem"] = args.origem.strip()
    if args.contato is not None:
        neg["contato"] = args.contato.strip()
    if args.proximo is not None:
        neg["proximo_passo"] = args.proximo.strip()
    if args.proximo_em is not None:
        neg["proximo_passo_em"] = iso(parse_data(args.proximo_em, hoje))
    if args.obs is not None:
        neg["observacoes"] = args.obs.strip()
    if args.entrou_em is not None:
        d = parse_data(args.entrou_em, hoje)
        if d:
            neg["entrou_em"] = iso(d)
    if args.ultimo_contato is not None:
        d = parse_data(args.ultimo_contato, hoje)
        if d:
            neg["ultimo_contato"] = iso(d)
    salvar(arquivo, negocios)
    _print("✏️  #{} atualizado:\n   {}".format(neg["id"], linha_neg(neg)), como_json) \
        if not como_json else _print(neg, True)
    return 0


def cmd_remover(args, negocios, arquivo, hoje, como_json):
    neg = achar(negocios, args.id)
    if not neg:
        _print("Não achei o negócio #{}.".format(args.id), como_json)
        return 1
    negocios.remove(neg)
    salvar(arquivo, negocios)
    _print("🗑️  Negócio #{} ({}) removido.".format(args.id, neg.get("cliente")), como_json) \
        if not como_json else _print({"removido": args.id}, True)
    return 0


# ---------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(description="Esteira — pipeline comercial (funil de negociações).")
    p.add_argument("--arquivo", default=ARQUIVO_PADRAO)
    p.add_argument("--formato", choices=["texto", "json"], default="texto")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("adicionar")
    a.add_argument("--cliente", required=True)
    a.add_argument("--valor", default="")
    a.add_argument("--etapa", default="")
    a.add_argument("--origem", default="")
    a.add_argument("--contato", default="")
    a.add_argument("--proximo", default="")
    a.add_argument("--proximo-em", dest="proximo_em", default="")
    a.add_argument("--prob", type=int, default=None)
    a.add_argument("--obs", default="")
    a.add_argument("--entrou-em", dest="entrou_em", default="")
    a.add_argument("--ultimo-contato", dest="ultimo_contato", default="")

    m = sub.add_parser("mover")
    m.add_argument("--id", required=True)
    m.add_argument("--etapa", required=True)
    m.add_argument("--proximo", default=None)
    m.add_argument("--proximo-em", dest="proximo_em", default=None)

    t = sub.add_parser("tocar")
    t.add_argument("--id", required=True)
    t.add_argument("--proximo", default=None)
    t.add_argument("--proximo-em", dest="proximo_em", default=None)

    g = sub.add_parser("ganhar")
    g.add_argument("--id", required=True)

    pe = sub.add_parser("perder")
    pe.add_argument("--id", required=True)
    pe.add_argument("--motivo", default="")

    sub.add_parser("hoje")
    sub.add_parser("esfriando")

    pv = sub.add_parser("previsao")
    pv.add_argument("--meta", default="")

    sub.add_parser("funil")

    ls = sub.add_parser("listar")
    ls.add_argument("--etapa", default="")
    ls.add_argument("--status", default="aberto")

    ed = sub.add_parser("editar")
    ed.add_argument("--id", required=True)
    ed.add_argument("--cliente", default=None)
    ed.add_argument("--valor", default=None)
    ed.add_argument("--prob", type=int, default=None)
    ed.add_argument("--origem", default=None)
    ed.add_argument("--contato", default=None)
    ed.add_argument("--proximo", default=None)
    ed.add_argument("--proximo-em", dest="proximo_em", default=None)
    ed.add_argument("--obs", default=None)
    ed.add_argument("--entrou-em", dest="entrou_em", default=None)
    ed.add_argument("--ultimo-contato", dest="ultimo_contato", default=None)

    rm = sub.add_parser("remover")
    rm.add_argument("--id", required=True)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    como_json = (args.formato == "json")
    hoje = date.today()
    negocios = carregar(args.arquivo)
    despacho = {
        "adicionar": cmd_adicionar,
        "mover": cmd_mover,
        "tocar": cmd_tocar,
        "hoje": cmd_hoje,
        "esfriando": cmd_esfriando,
        "previsao": cmd_previsao,
        "funil": cmd_funil,
        "listar": cmd_listar,
        "editar": cmd_editar,
        "remover": cmd_remover,
    }
    if args.cmd == "ganhar":
        return cmd_fechar(args, negocios, args.arquivo, hoje, como_json, True)
    if args.cmd == "perder":
        return cmd_fechar(args, negocios, args.arquivo, hoje, como_json, False)
    return despacho[args.cmd](args, negocios, args.arquivo, hoje, como_json)


if __name__ == "__main__":
    sys.exit(main())
