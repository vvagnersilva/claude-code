#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Farol — motor de análise financeira para pequenos negócios.

Lê o livro de lançamentos em .farol/lancamentos.csv e devolve análises
prontas em português simples. Usa SOMENTE a biblioteca padrão do Python.
Nunca inventa números: tudo que sai daqui veio dos lançamentos.

Formato do CSV (.farol/lancamentos.csv), com cabeçalho:
    data,tipo,categoria,cliente,descricao,valor
    2026-05-03,receita,Consultas,Maria Silva,Consulta de retorno,250.00
    2026-05-04,despesa,Aluguel,,Aluguel da sala,1800.00

  - data: YYYY-MM-DD ou DD/MM/YYYY
  - tipo: receita | despesa
  - categoria: serviço/produto (receitas) ou tipo de gasto (despesas)
  - cliente: opcional (só para receitas)
  - descricao: opcional
  - valor: aceita "1234.56", "1.234,56" ou "R$ 1.234,56"

Comandos:
    python3 farol.py resumo                       # saúde geral (semáforo)
    python3 farol.py fechamento --mes 2026-05     # fechamento do mês
    python3 farol.py margem                       # lucro por categoria
    python3 farol.py ranking --por cliente        # ranking (cliente|categoria)
    python3 farol.py tendencia --meses 6          # evolução mês a mês
    python3 farol.py folego --caixa 12000         # quanto o caixa aguenta
    python3 farol.py alertas                      # sinais de atenção
Opções globais: --arquivo <csv>  (padrão: .farol/lancamentos.csv)
                --formato json   (padrão: texto)
"""

import argparse
import csv
import json
import os
import sys
import unicodedata
from collections import defaultdict
from datetime import date

ARQUIVO_PADRAO = os.path.join(".farol", "lancamentos.csv")


# ---------------------------------------------------------------- utilidades

def _norm(s):
    """minúsculas e sem acento, para comparação tolerante."""
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def parse_valor(bruto):
    """Converte 'R$ 1.234,56' / '1.234,56' / '1234.56' em float. None se inválido."""
    s = (bruto or "").strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    if "," in s:                       # formato brasileiro: . = milhar, , = decimal
        s = s.replace(".", "").replace(",", ".")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def parse_data(bruto):
    """Aceita YYYY-MM-DD ou DD/MM/YYYY. Devolve date ou None."""
    s = (bruto or "").strip()
    for fmt in (("-", (0, 1, 2)), ("/", (2, 1, 0))):
        sep, ordem = fmt
        partes = s.split(sep)
        if len(partes) == 3:
            try:
                nums = [int(p) for p in partes]
                ano, mes, dia = nums[ordem[0]], nums[ordem[1]], nums[ordem[2]]
                return date(ano, mes, dia)
            except ValueError:
                continue
    return None


def brl(v):
    """Formata 1234.5 como 'R$ 1.234,50'."""
    neg = v < 0
    v = abs(v)
    inteiro, cent = divmod(round(v * 100), 100)
    txt = "{:,}".format(int(inteiro)).replace(",", ".")
    return ("-" if neg else "") + "R$ " + txt + "," + "{:02d}".format(int(cent))


def carregar(caminho):
    """Lê o CSV e devolve (lançamentos válidos, linhas ignoradas)."""
    if not os.path.exists(caminho):
        sys.exit("Arquivo não encontrado: %s\n"
                 "Crie o livro de lançamentos primeiro (veja o SKILL.md)." % caminho)
    linhas, ignoradas = [], []
    with open(caminho, newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            row = { _norm(k): (v or "").strip() for k, v in row.items() if k }
            d = parse_data(row.get("data"))
            v = parse_valor(row.get("valor"))
            tipo = _norm(row.get("tipo"))
            if tipo.startswith("receita"):
                tipo = "receita"
            elif tipo.startswith("despesa") or tipo.startswith("gasto") or tipo.startswith("custo"):
                tipo = "despesa"
            else:
                tipo = ""
            if d is None or v is None or tipo not in ("receita", "despesa"):
                ignoradas.append(i)
                continue
            linhas.append({
                "data": d, "tipo": tipo,
                "categoria": row.get("categoria") or "(sem categoria)",
                "cliente": row.get("cliente") or "",
                "descricao": row.get("descricao") or "",
                "valor": abs(v),
            })
    return linhas, ignoradas


def meses_de(lancs):
    """Lista ordenada de 'YYYY-MM' presentes nos lançamentos."""
    return sorted({l["data"].strftime("%Y-%m") for l in lancs})


def soma_mes(lancs, mes):
    rec = sum(l["valor"] for l in lancs if l["tipo"] == "receita" and l["data"].strftime("%Y-%m") == mes)
    desp = sum(l["valor"] for l in lancs if l["tipo"] == "despesa" and l["data"].strftime("%Y-%m") == mes)
    return rec, desp


def nome_mes(mes):
    nomes = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    ano, m = mes.split("-")
    return "%s/%s" % (nomes[int(m) - 1], ano)


def emitir(obj, texto, formato):
    if formato == "json":
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
    else:
        print(texto)


# ----------------------------------------------------------------- comandos

def cmd_resumo(lancs, args):
    meses = meses_de(lancs)
    if not meses:
        sys.exit("Nenhum lançamento válido encontrado.")
    ult = meses[-1]
    rec, desp = soma_mes(lancs, ult)
    sobra = rec - desp
    margem = (sobra / rec * 100) if rec else 0.0

    # semáforo simples e honesto
    if rec == 0:
        farol, leitura = "VERMELHO", "sem receita registrada no mês"
    elif sobra < 0:
        farol, leitura = "VERMELHO", "as despesas passaram a receita"
    elif margem < 10:
        farol, leitura = "AMARELO", "sobra muito apertada (margem abaixo de 10%)"
    else:
        farol, leitura = "VERDE", "a receita cobre as despesas com folga"

    # comparação com o mês anterior, se houver
    comparacao = ""
    if len(meses) >= 2:
        rec_ant, _ = soma_mes(lancs, meses[-2])
        if rec_ant > 0:
            delta = (rec - rec_ant) / rec_ant * 100
            direcao = "subiu" if delta >= 0 else "caiu"
            comparacao = "Receita %s %.0f%% em relação a %s." % (direcao, abs(delta), nome_mes(meses[-2]))

    obj = {"mes": ult, "farol": farol, "receita": rec, "despesa": desp,
           "sobra": sobra, "margem_pct": round(margem, 1)}
    texto = "\n".join(filter(None, [
        "=== FAROL — RESUMO DE %s ===" % nome_mes(ult).upper(),
        "Sinal: %s (%s)" % (farol, leitura),
        "Entrou:  %s" % brl(rec),
        "Saiu:    %s" % brl(desp),
        "Sobrou:  %s  (margem de %.1f%%)" % (brl(sobra), margem),
        comparacao,
        "Períodos com dados: %s a %s (%d meses)" % (nome_mes(meses[0]), nome_mes(ult), len(meses)),
    ]))
    emitir(obj, texto, args.formato)


def cmd_fechamento(lancs, args):
    meses = meses_de(lancs)
    mes = args.mes or (meses[-1] if meses else None)
    if not mes or mes not in meses:
        sys.exit("Não há lançamentos para o mês pedido. Meses disponíveis: %s" % ", ".join(meses))
    do_mes = [l for l in lancs if l["data"].strftime("%Y-%m") == mes]
    rec, desp = soma_mes(lancs, mes)

    por_cat_rec = defaultdict(float)
    por_cat_desp = defaultdict(float)
    for l in do_mes:
        (por_cat_rec if l["tipo"] == "receita" else por_cat_desp)[l["categoria"]] += l["valor"]

    linhas = ["=== FECHAMENTO DE %s ===" % nome_mes(mes).upper(),
              "Entrou: %s | Saiu: %s | Sobrou: %s" % (brl(rec), brl(desp), brl(rec - desp)), "",
              "DE ONDE VEIO O DINHEIRO:"]
    for cat, v in sorted(por_cat_rec.items(), key=lambda x: -x[1]):
        pct = v / rec * 100 if rec else 0
        linhas.append("  %-28s %12s  (%.0f%%)" % (cat[:28], brl(v), pct))
    linhas += ["", "PARA ONDE FOI O DINHEIRO:"]
    for cat, v in sorted(por_cat_desp.items(), key=lambda x: -x[1]):
        pct = v / desp * 100 if desp else 0
        linhas.append("  %-28s %12s  (%.0f%%)" % (cat[:28], brl(v), pct))

    obj = {"mes": mes, "receita": rec, "despesa": desp, "sobra": rec - desp,
           "receitas_por_categoria": dict(por_cat_rec),
           "despesas_por_categoria": dict(por_cat_desp)}
    emitir(obj, "\n".join(linhas), args.formato)


def cmd_margem(lancs, args):
    """Lucro estimado por categoria de receita: receita da categoria menos a
    fatia proporcional das despesas (rateio simples e transparente)."""
    rec_total = sum(l["valor"] for l in lancs if l["tipo"] == "receita")
    desp_total = sum(l["valor"] for l in lancs if l["tipo"] == "despesa")
    if rec_total == 0:
        sys.exit("Sem receitas registradas — não dá para calcular margem.")
    por_cat = defaultdict(float)
    for l in lancs:
        if l["tipo"] == "receita":
            por_cat[l["categoria"]] += l["valor"]

    linhas = ["=== MARGEM POR CATEGORIA (todo o período) ===",
              "Rateio: cada categoria carrega despesas na proporção da receita que gera.", ""]
    resultado = []
    for cat, v in sorted(por_cat.items(), key=lambda x: -x[1]):
        fatia = v / rec_total
        custo = desp_total * fatia
        lucro = v - custo
        resultado.append({"categoria": cat, "receita": v,
                          "custo_rateado": round(custo, 2), "lucro_estimado": round(lucro, 2)})
        linhas.append("  %-26s receita %12s | custo %12s | sobra %12s"
                      % (cat[:26], brl(v), brl(custo), brl(lucro)))
    linhas += ["", "Atenção: rateio proporcional é uma estimativa. Se souber o custo real",
               "de cada serviço, informe — o resultado fica mais preciso."]
    emitir({"total_receita": rec_total, "total_despesa": desp_total,
            "categorias": resultado}, "\n".join(linhas), args.formato)


def cmd_ranking(lancs, args):
    chave = "cliente" if args.por == "cliente" else "categoria"
    por = defaultdict(float)
    for l in lancs:
        if l["tipo"] == "receita":
            nome = l[chave] or "(não informado)"
            por[nome] += l["valor"]
    total = sum(por.values())
    if total == 0:
        sys.exit("Sem receitas registradas.")
    ordenado = sorted(por.items(), key=lambda x: -x[1])

    linhas = ["=== RANKING DE RECEITA POR %s ===" % chave.upper(), ""]
    acumulado = 0.0
    for i, (nome, v) in enumerate(ordenado, 1):
        acumulado += v
        linhas.append("  %2d. %-26s %12s  (%.0f%% | acumulado %.0f%%)"
                      % (i, nome[:26], brl(v), v / total * 100, acumulado / total * 100))

    # concentração: quantos respondem por 80%
    acumulado, n80 = 0.0, 0
    for _, v in ordenado:
        acumulado += v
        n80 += 1
        if acumulado >= total * 0.8:
            break
    linhas += ["", "%d de %d %ss respondem por 80%% da receita."
               % (n80, len(ordenado), chave)]
    if len(ordenado) >= 3 and ordenado[0][1] / total > 0.5:
        linhas.append("Atenção: '%s' sozinho é mais da metade da receita — risco de concentração."
                      % ordenado[0][0])
    emitir({"por": chave, "total": total,
            "ranking": [{"nome": n, "valor": v} for n, v in ordenado]},
           "\n".join(linhas), args.formato)


def cmd_tendencia(lancs, args):
    meses = meses_de(lancs)[-args.meses:]
    if len(meses) < 2:
        sys.exit("Preciso de pelo menos 2 meses de lançamentos para mostrar tendência.")
    serie = []
    linhas = ["=== TENDÊNCIA — ÚLTIMOS %d MESES ===" % len(meses), ""]
    maior = max(soma_mes(lancs, m)[0] for m in meses) or 1
    for m in meses:
        rec, desp = soma_mes(lancs, m)
        barra = "█" * max(1, int(rec / maior * 30)) if rec else ""
        serie.append({"mes": m, "receita": rec, "despesa": desp, "sobra": rec - desp})
        linhas.append("  %-14s %12s  %s" % (nome_mes(m), brl(rec), barra))

    primeira, ultima = serie[0]["receita"], serie[-1]["receita"]
    if primeira > 0:
        delta = (ultima - primeira) / primeira * 100
        rumo = "crescendo" if delta > 5 else ("caindo" if delta < -5 else "estável")
        linhas += ["", "Receita está %s: %.0f%% de %s para %s."
                   % (rumo, delta, nome_mes(meses[0]), nome_mes(meses[-1]))]
    media_sobra = sum(s["sobra"] for s in serie) / len(serie)
    linhas.append("Sobra média por mês no período: %s." % brl(media_sobra))
    emitir({"serie": serie, "sobra_media": round(media_sobra, 2)},
           "\n".join(linhas), args.formato)


def cmd_folego(lancs, args):
    if args.caixa is None:
        sys.exit("Informe o dinheiro em caixa: folego --caixa 12000")
    meses = meses_de(lancs)
    ult3 = meses[-3:] if len(meses) >= 3 else meses
    desp_media = sum(soma_mes(lancs, m)[1] for m in ult3) / len(ult3) if ult3 else 0
    rec_media = sum(soma_mes(lancs, m)[0] for m in ult3) / len(ult3) if ult3 else 0

    linhas = ["=== FÔLEGO DE CAIXA ===",
              "Caixa informado: %s" % brl(args.caixa),
              "Despesa média (últimos %d meses): %s/mês" % (len(ult3), brl(desp_media)),
              "Receita média (últimos %d meses): %s/mês" % (len(ult3), brl(rec_media)), ""]
    obj = {"caixa": args.caixa, "despesa_media": round(desp_media, 2),
           "receita_media": round(rec_media, 2)}
    if desp_media <= 0:
        linhas.append("Sem despesas registradas — não dá para calcular o fôlego.")
    else:
        # cenário 1: tudo para (sem receita)
        meses_parado = args.caixa / desp_media
        linhas.append("Se a receita PARASSE hoje, o caixa segura %.1f meses." % meses_parado)
        obj["meses_sem_receita"] = round(meses_parado, 1)
        # cenário 2: ritmo atual
        saldo = rec_media - desp_media
        if saldo >= 0:
            linhas.append("No ritmo atual o caixa CRESCE %s por mês — sem risco no horizonte." % brl(saldo))
            obj["saldo_mensal"] = round(saldo, 2)
        else:
            meses_ritmo = args.caixa / abs(saldo)
            linhas.append("No ritmo atual (queimando %s/mês), o caixa acaba em %.1f meses."
                          % (brl(abs(saldo)), meses_ritmo))
            obj["meses_no_ritmo_atual"] = round(meses_ritmo, 1)
        linhas += ["", "Referência saudável: caixa para cobrir pelo menos 3 a 6 meses de despesa fixa."]
    emitir(obj, "\n".join(linhas), args.formato)


def cmd_alertas(lancs, args):
    meses = meses_de(lancs)
    alertas = []
    if len(meses) >= 2:
        rec, desp = soma_mes(lancs, meses[-1])
        rec_ant, desp_ant = soma_mes(lancs, meses[-2])
        if rec_ant > 0 and rec < rec_ant * 0.85:
            alertas.append("Receita caiu %.0f%% de %s para %s."
                           % ((1 - rec / rec_ant) * 100, nome_mes(meses[-2]), nome_mes(meses[-1])))
        if desp_ant > 0 and desp > desp_ant * 1.2:
            alertas.append("Despesas subiram %.0f%% de %s para %s."
                           % ((desp / desp_ant - 1) * 100, nome_mes(meses[-2]), nome_mes(meses[-1])))
        if rec > 0 and (rec - desp) / rec < 0.10:
            alertas.append("Margem do último mês abaixo de 10%% — sobra apertada.")
        if rec == 0:
            alertas.append("Nenhuma receita registrada em %s." % nome_mes(meses[-1]))

    # concentração de clientes (todo o período)
    por_cli = defaultdict(float)
    for l in lancs:
        if l["tipo"] == "receita" and l["cliente"]:
            por_cli[l["cliente"]] += l["valor"]
    tot_cli = sum(por_cli.values())
    if tot_cli > 0:
        top = max(por_cli.items(), key=lambda x: x[1])
        if top[1] / tot_cli > 0.5 and len(por_cli) >= 3:
            alertas.append("Cliente '%s' representa %.0f%% da receita — se ele sair, o negócio sente."
                           % (top[0], top[1] / tot_cli * 100))

    # queda de ritmo em 3+ meses
    if len(meses) >= 3:
        ult3 = [soma_mes(lancs, m)[0] for m in meses[-3:]]
        if ult3[0] > ult3[1] > ult3[2]:
            alertas.append("Receita caiu por 2 meses seguidos — vale investigar a causa.")

    if alertas:
        texto = "=== ALERTAS DO FAROL ===\n" + "\n".join("  ⚠ " + a for a in alertas)
    else:
        texto = "=== ALERTAS DO FAROL ===\n  Nenhum sinal de atenção nos dados atuais. Siga o jogo."
    emitir({"alertas": alertas}, texto, args.formato)


# -------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="Farol — análises financeiras do seu negócio")
    p.add_argument("--arquivo", default=ARQUIVO_PADRAO)
    p.add_argument("--formato", choices=["texto", "json"], default="texto")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("resumo")
    f = sub.add_parser("fechamento"); f.add_argument("--mes")
    sub.add_parser("margem")
    r = sub.add_parser("ranking"); r.add_argument("--por", choices=["cliente", "categoria"], default="categoria")
    t = sub.add_parser("tendencia"); t.add_argument("--meses", type=int, default=6)
    fo = sub.add_parser("folego"); fo.add_argument("--caixa", type=float)
    sub.add_parser("alertas")

    args = p.parse_args()
    lancs, ignoradas = carregar(args.arquivo)
    if ignoradas and args.formato == "texto":
        print("(aviso: %d linha(s) ignorada(s) por dados incompletos: linhas %s)\n"
              % (len(ignoradas), ", ".join(map(str, ignoradas[:10]))))

    {"resumo": cmd_resumo, "fechamento": cmd_fechamento, "margem": cmd_margem,
     "ranking": cmd_ranking, "tendencia": cmd_tendencia, "folego": cmd_folego,
     "alertas": cmd_alertas}[args.cmd](lancs, args)


if __name__ == "__main__":
    main()
