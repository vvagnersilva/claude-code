#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alavanca — motor de precificação e cenários para PRODUTO DIGITAL escalável.
Só biblioteca padrão (stdlib). Nada de internet, nada de chave de API.

Não inventa demanda nem "preço mágico": parte de números que o dono informa
(âncora de valor, horas para criar, custo-hora, tamanho do público) e mostra
faixas de preço, ponto de equilíbrio do esforço e cenários de receita.

Subcomandos
-----------
  preco     -> 3 faixas (entrada / principal / premium) + ponto de equilíbrio
  cenario   -> receita conservador / realista / otimista (one-time OU recorrente)

Exemplos
--------
  python3 alavanca.py preco --formato curso --ancora 1500 --horas-criacao 40 --custo-hora 80
  python3 alavanca.py preco --formato comunidade --ancora 400 --horas-criacao 25 --custo-hora 80 --recorrente
  python3 alavanca.py cenario --preco 497 --publico 2000 --conv-baixa 0.5 --conv-alta 2
  python3 alavanca.py cenario --preco 49 --publico 1500 --conv-baixa 1 --conv-alta 3 --recorrente --churn 6
"""

import argparse
import sys

# ---------------------------------------------------------------- formatação BR

def brl(v):
    """Formata número como R$ 1.234,56 (padrão brasileiro)."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "R$ 0,00"
    neg = v < 0
    v = abs(v)
    inteiro, cent = divmod(round(v * 100), 100)
    s = f"{inteiro:,}".replace(",", ".")
    out = f"R$ {s},{cent:02d}"
    return ("-" + out) if neg else out


def parse_num(txt):
    """Aceita '1.234,56', '1234.56', 'R$ 1.200', '1200' e devolve float."""
    if txt is None:
        return 0.0
    if isinstance(txt, (int, float)):
        return float(txt)
    s = str(txt).strip().replace("R$", "").replace(" ", "")
    if not s:
        return 0.0
    # formato BR: vírgula é decimal; ponto é separador de milhar.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")                 # 1.234.567 -> milhares
    elif "." in s:
        intpart, frac = s.rsplit(".", 1)
        if len(frac) == 3:                     # "2.000" no BR = 2000 (milhar)
            s = intpart + frac
        # 1-2 dígitos após o ponto = decimal internacional ("2.50"); mantém
    try:
        return float(s)
    except ValueError:
        return 0.0


# ----------------------------------------------------- multiplicadores por formato
# Quanto cada formato costuma valer em relação à âncora (valor do atendimento 1:1
# do dono). NÃO é regra de mercado fechada — é um ponto de partida transparente
# que o dono ajusta. Produto gravado custa menos que mentoria ao vivo, etc.
FORMATOS = {
    "curso":      dict(nome="Curso gravado",        mult=(0.20, 0.45, 0.90), recorrente=False),
    "ebook":      dict(nome="Ebook / guia",         mult=(0.05, 0.12, 0.25), recorrente=False),
    "template":   dict(nome="Template / kit",       mult=(0.08, 0.18, 0.40), recorrente=False),
    "mentoria":   dict(nome="Mentoria em grupo",    mult=(0.60, 1.10, 2.00), recorrente=True),
    "comunidade": dict(nome="Comunidade / assinatura", mult=(0.06, 0.12, 0.25), recorrente=True),
    "desafio":    dict(nome="Desafio / bootcamp",   mult=(0.15, 0.35, 0.70), recorrente=False),
}

FAIXA_LABEL = ("Entrada", "Principal", "Premium")


def cmd_preco(a):
    fmt = a.formato.lower()
    if fmt not in FORMATOS:
        print(f"Formato desconhecido: {a.formato}. Use: {', '.join(FORMATOS)}", file=sys.stderr)
        return 2
    f = FORMATOS[fmt]
    ancora = parse_num(a.ancora)
    horas = parse_num(a.horas_criacao)
    custo_hora = parse_num(a.custo_hora)
    custo_criacao = horas * custo_hora
    recorrente = a.recorrente or f["recorrente"]

    precos = [round(ancora * m) for m in f["mult"]]
    # arredonda para "preço de vitrine": termina em 7 ou 97 quando faz sentido
    precos = [_preco_vitrine(p) for p in precos]

    sufixo = "/mês" if recorrente else ""
    print("=" * 56)
    print(f"  ALAVANCA — Preço sugerido | {f['nome']}")
    print("=" * 56)
    print(f"  Âncora de valor (seu 1:1): {brl(ancora)}")
    print(f"  Custo para criar: {horas:g} h × {brl(custo_hora)} = {brl(custo_criacao)}")
    if recorrente:
        print("  Modelo: RECORRENTE (cobra todo mês)")
    print("-" * 56)
    for label, preco in zip(FAIXA_LABEL, precos):
        print(f"  {label:<10} {brl(preco)}{sufixo}")
        if custo_criacao > 0 and preco > 0:
            vendas_be = _teto(custo_criacao / preco)
            quando = "no 1º mês" if recorrente else "no total"
            print(f"             ↳ paga o esforço de criação com {vendas_be} venda(s) {quando}")
    print("-" * 56)
    print("  Como ler: 'Principal' é o preço-âncora da oferta. 'Entrada'")
    print("  abaixa a barreira; 'Premium' agrega bônus/acompanhamento.")
    print("  Estes números são ponto de partida — ajuste à sua realidade.")
    print("=" * 56)
    return 0


def cmd_cenario(a):
    preco = parse_num(a.preco)
    publico = int(parse_num(a.publico))
    conv_baixa = parse_num(a.conv_baixa) / 100.0
    conv_alta = parse_num(a.conv_alta) / 100.0
    conv_media = (conv_baixa + conv_alta) / 2.0
    recorrente = a.recorrente
    churn = parse_num(a.churn) / 100.0 if a.churn else 0.0
    publico_fmt = f"{publico:,}".replace(",", ".")

    cenarios = [
        ("Conservador", conv_baixa),
        ("Realista", conv_media),
        ("Otimista", conv_alta),
    ]
    print("=" * 56)
    print("  ALAVANCA — Cenários de receita")
    print("=" * 56)
    print(f"  Preço: {brl(preco)}{'/mês' if recorrente else ''}")
    print(f"  Público alcançável: {publico_fmt} pessoas")
    print(f"  Conversão testada: {conv_baixa*100:g}% a {conv_alta*100:g}%")
    if recorrente:
        print(f"  Cancelamento (churn) mensal: {churn*100:g}%")
    print("-" * 56)
    for nome, conv in cenarios:
        vendas = _teto(publico * conv)
        if recorrente:
            mrr = vendas * preco
            print(f"  {nome:<13} {vendas} assinante(s) → {brl(mrr)}/mês")
        else:
            receita = vendas * preco
            print(f"  {nome:<13} {vendas} venda(s) → {brl(receita)}")
    print("-" * 56)
    if recorrente:
        # projeção 12 meses no cenário realista com churn (sem novas entradas)
        vendas0 = _teto(publico * conv_media)
        print("  Projeção 12 meses (realista, SÓ a 1ª leva, com churn):")
        ativos = float(vendas0)
        total = 0.0
        for mes in (1, 3, 6, 12):
            ativos_mes = vendas0 * ((1 - churn) ** (mes - 1))
            print(f"     mês {mes:>2}: ~{_teto(ativos_mes)} ativos → {brl(ativos_mes*preco)}/mês")
        # receita acumulada 12 meses
        acc = sum(vendas0 * ((1 - churn) ** (m - 1)) * preco for m in range(1, 13))
        print(f"  Receita acumulada em 12 meses (só a 1ª leva): {brl(acc)}")
        print("  (Você ainda soma novas entradas todo mês — isto é o piso.)")
    else:
        vendas = _teto(publico * conv_media)
        print(f"  No realista, cada nova leva de {publico_fmt} "
              f"pessoas rende ~{brl(vendas*preco)}.")
    print("=" * 56)
    print("  Lembrete: estes números dependem de ALCANCE real. Não são")
    print("  promessa — são a conta do 'se X pessoas virem e Y% comprarem'.")
    print("=" * 56)
    return 0


# --------------------------------------------------------------------- utilitários

def _teto(x):
    import math
    return int(math.ceil(x - 1e-9)) if x > 0 else 0


def _preco_vitrine(p):
    """Arredonda para um preço 'de vitrine' agradável, sem distorcer muito."""
    if p <= 0:
        return 0
    if p < 30:
        return int(round(p))
    if p < 100:
        return int(round((p - 7) / 10.0) * 10 + 7)   # ...37, 47, 57
    if p < 1000:
        return int(round((p - 97) / 100.0) * 100 + 97)  # ...297, 497, 997
    return int(round(p / 100.0) * 100 - 3)            # ...1497, 1997


def build_parser():
    p = argparse.ArgumentParser(prog="alavanca", description="Precificação e cenários de produto digital.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("preco", help="Faixas de preço + ponto de equilíbrio do esforço")
    pp.add_argument("--formato", required=True, help="curso|ebook|template|mentoria|comunidade|desafio")
    pp.add_argument("--ancora", required=True, help="Valor do seu atendimento/serviço 1:1 (âncora)")
    pp.add_argument("--horas-criacao", default="0", help="Horas para criar o produto")
    pp.add_argument("--custo-hora", default="0", help="Quanto vale sua hora")
    pp.add_argument("--recorrente", action="store_true", help="Forçar modelo recorrente (cobra/mês)")
    pp.set_defaults(func=cmd_preco)

    pc = sub.add_parser("cenario", help="Receita conservador/realista/otimista")
    pc.add_argument("--preco", required=True, help="Preço do produto")
    pc.add_argument("--publico", required=True, help="Tamanho do público alcançável")
    pc.add_argument("--conv-baixa", default="1", help="Conversão pessimista em %% (ex.: 1)")
    pc.add_argument("--conv-alta", default="3", help="Conversão otimista em %% (ex.: 3)")
    pc.add_argument("--recorrente", action="store_true", help="Produto recorrente (assinatura/mentoria)")
    pc.add_argument("--churn", default="0", help="Cancelamento mensal em %% (recorrente)")
    pc.set_defaults(func=cmd_cenario)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
