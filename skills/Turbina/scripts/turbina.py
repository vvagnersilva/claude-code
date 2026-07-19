#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turbina — motor de tráfego pago (offline, só biblioteca padrão).

Faz a conta que o gestor de tráfego / dono de negócio precisa e LÊ a exportação
de métricas do Gerenciador de Anúncios (Meta) ou do Google Ads, sem nunca
inventar número: só calcula em cima do que foi informado ou colado.

Subcomandos:
  equilibrio   ponto de equilíbrio: ROAS e CPA máximos a partir da SUA margem
  verba        projeta leads/vendas/faturamento de um orçamento (3 cenários)
  diagnostico  lê a tabela de métricas colada e diz MATAR/AJUSTAR/ESCALAR/AGUARDAR
  aprendizado  guarda/lista o que funcionou e o que fracassou (memória)
  painel       resumo do mês a partir dos arquivos locais em .turbina/

Regras de ouro embutidas:
  - Nunca inventa métrica. Se falta dado para decidir, devolve AGUARDAR/faltou-dado.
  - O CPA-alvo vem da SUA margem (conta exata), não de um "benchmark mágico".
  - Benchmarks são só referência; a decisão principal é contra o seu equilíbrio.
  - Tudo é local. O script não conecta em conta nenhuma nem move verba.

Uso via biblioteca padrão apenas (sys, csv, json, argparse, re, io, math).
"""

import sys
import os
import re
import csv
import io
import json
import argparse

# ----------------------------------------------------------------------------
# Parsing de números no padrão brasileiro (e no americano, por segurança)
# ----------------------------------------------------------------------------

def parse_num(valor):
    """Converte 'R$ 1.234,56', '1.234,56', '1,03%', '2.5', '', '-' em float.
    Devolve None quando não há número interpretável (nunca chuta)."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip()
    if s == "" or s in {"-", "–", "—", "N/A", "n/a", "NA", "--"}:
        return None
    # remove moeda, espaços, %, e marcadores comuns
    s = s.replace("R$", "").replace("r$", "").replace("%", "")
    s = s.replace(" ", " ").strip()
    # remove qualquer coisa que não seja dígito, ponto, vírgula ou sinal
    s = re.sub(r"[^\d,.\-]", "", s)
    if s in {"", "-", ".", ","}:
        return None
    # decide o separador decimal (padrão brasileiro por padrão)
    if "," in s and "." in s:
        # o que vier por último é o decimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")   # 1.234,56 -> 1234.56
        else:
            s = s.replace(",", "")                      # 1,234.56 -> 1234.56
    elif "," in s:
        # só vírgula: decimal brasileiro (1,03 -> 1.03; 1.234,56 já tratado acima)
        s = s.replace(",", ".")
    elif "." in s:
        # só ponto: ambíguo. No padrão BR, ponto é MILHAR.
        partes = s.lstrip("-").split(".")
        if len(partes) > 2:
            # 1.234.567 -> milhar em todos
            s = s.replace(".", "")
        elif len(partes) == 2 and len(partes[1]) == 3 and 1 <= len(partes[0]) <= 3:
            # "3.000" / "12.500" / "100.000" -> milhar (mais provável p/ dinheiro BR)
            s = s.replace(".", "")
        # senão (ex.: "2.5", "1.03", "150.00") -> decimal americano, mantém o ponto
    try:
        return float(s)
    except ValueError:
        return None


def parse_pct(valor):
    """Igual a parse_num mas devolve a fração se o texto tinha '%'.
    '1,03%' -> 1.03 (mantemos em pontos percentuais, não em fração)."""
    return parse_num(valor)


def brl(v):
    if v is None:
        return "—"
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def num(v, casas=2):
    if v is None:
        return "—"
    return f"{v:.{casas}f}".replace(".", ",")


# ----------------------------------------------------------------------------
# equilibrio: a conta mais importante — nasce da SUA margem
# ----------------------------------------------------------------------------

def cmd_equilibrio(args):
    ticket = parse_num(args.ticket)
    if ticket is None or ticket <= 0:
        print("ERRO: informe --ticket (valor médio de uma venda), ex.: --ticket 'R$ 500'")
        return 2

    margem_pct = None
    margem_valor = None
    if args.margem is not None:
        m = parse_num(args.margem)
        if m is None:
            print("ERRO: --margem não entendida. Use % (ex.: --margem 40) ou R$ (ex.: --margem 'R$ 200').")
            return 2
        # se veio com R$ no texto original, é valor; senão, é percentual
        if "R$" in str(args.margem) or "r$" in str(args.margem):
            margem_valor = m
            margem_pct = (m / ticket) * 100
        else:
            margem_pct = m
            margem_valor = ticket * (m / 100.0)

    if margem_pct is None:
        print("ERRO: informe --margem (quanto sobra de cada venda). Ex.: --margem 40  (40%)  ou  --margem 'R$ 200'")
        print("Sem a margem NÃO dá para calcular o equilíbrio — e a Turbina não inventa esse número.")
        return 2

    if margem_pct <= 0 or margem_pct > 100:
        print(f"ATENÇÃO: margem de {num(margem_pct)}% parece fora do intervalo (0 a 100%). Confira o valor.")

    # ROAS de equilíbrio = faturamento / gasto = 1 / margem_fração
    margem_frac = margem_pct / 100.0
    roas_equilibrio = (1.0 / margem_frac) if margem_frac > 0 else None
    cpa_maximo = margem_valor            # acima disso você paga para vender
    # CPA-alvo saudável: sobra de lucro. Padrão: usar no máx. 1/3 da margem no anúncio.
    fatia = args.fatia_lucro if args.fatia_lucro else 0.33
    cpa_alvo = margem_valor * fatia

    print("=" * 60)
    print("PONTO DE EQUILÍBRIO DA SUA MÍDIA PAGA")
    print("=" * 60)
    print(f"Ticket médio (uma venda):      {brl(ticket)}")
    print(f"Margem por venda:              {num(margem_pct)}%  =  {brl(margem_valor)}")
    print("-" * 60)
    print(f"ROAS de EQUILÍBRIO:            {num(roas_equilibrio)}x")
    print(f"   (abaixo desse ROAS você está PAGANDO para vender)")
    print(f"CPA MÁXIMO (empata):          {brl(cpa_maximo)}")
    print(f"   (pagar mais que isso por venda = prejuízo)")
    print(f"CPA-ALVO saudável (sobra lucro): {brl(cpa_alvo)}")
    print(f"   (mira aqui; usa ~{int(fatia*100)}% da margem no anúncio e guarda o resto)")
    print("=" * 60)
    print("Como usar: no diagnóstico, qualquer conjunto com CPA acima do CPA MÁXIMO")
    print("está no vermelho (candidato a MATAR). Entre o alvo e o máximo = AJUSTAR.")
    print("Abaixo do alvo com volume = candidato a ESCALAR.")
    return 0


# ----------------------------------------------------------------------------
# verba: projeção de resultados de um orçamento (3 cenários honestos)
# ----------------------------------------------------------------------------

def cmd_verba(args):
    orcamento = parse_num(args.orcamento)
    if orcamento is None or orcamento <= 0:
        print("ERRO: informe --orcamento (quanto pretende investir), ex.: --orcamento 'R$ 3.000'")
        return 2
    if args.periodo == "dia":
        orcamento_mes = orcamento * 30
        orcamento_dia = orcamento
    else:
        orcamento_mes = orcamento
        orcamento_dia = orcamento / 30.0

    custo_lead = parse_num(args.cpl) if args.cpl else None
    custo_venda = parse_num(args.cpa) if args.cpa else None
    conv = parse_num(args.conv) if args.conv else None   # % lead -> venda
    ticket = parse_num(args.ticket) if args.ticket else None

    if custo_lead is None and custo_venda is None:
        print("ERRO: informe pelo menos o custo esperado por lead (--cpl) OU por venda (--cpa).")
        print("Não tem histórico? Comece com uma estimativa conservadora do seu nicho — e trate")
        print("a projeção como HIPÓTESE a validar, nunca como promessa. A Turbina não inventa custo.")
        return 2

    print("=" * 60)
    print("PROJEÇÃO DE RESULTADO DO INVESTIMENTO")
    print("=" * 60)
    print(f"Investimento:  {brl(orcamento_mes)}/mês   (~{brl(orcamento_dia)}/dia)")
    if custo_lead is not None:
        print(f"Custo por lead estimado (CPL): {brl(custo_lead)}")
    if custo_venda is not None:
        print(f"Custo por venda estimado (CPA): {brl(custo_venda)}")
    if conv is not None:
        print(f"Conversão lead→venda: {num(conv)}%")
    if ticket is not None:
        print(f"Ticket médio: {brl(ticket)}")
    print("-" * 60)

    cenarios = [("CONSERVADOR", 1.30), ("REALISTA", 1.00), ("OTIMISTA", 0.75)]
    print(f"{'Cenário':<14}{'Leads':>8}{'Vendas':>9}{'Faturam.':>14}{'ROAS':>8}")
    for nome, fator in cenarios:
        leads = vendas = fat = roas = None
        if custo_lead is not None:
            cl = custo_lead * fator
            leads = orcamento_mes / cl if cl > 0 else None
            if conv is not None and leads is not None:
                vendas = leads * (conv / 100.0)
        if custo_venda is not None:
            cv = custo_venda * fator
            vendas = orcamento_mes / cv if cv > 0 else vendas
        if vendas is not None and ticket is not None:
            fat = vendas * ticket
            roas = fat / orcamento_mes if orcamento_mes > 0 else None
        print(f"{nome:<14}"
              f"{(num(leads,0) if leads is not None else '—'):>8}"
              f"{(num(vendas,1) if vendas is not None else '—'):>9}"
              f"{(brl(fat) if fat is not None else '—'):>14}"
              f"{(num(roas)+'x' if roas is not None else '—'):>8}")
    print("=" * 60)
    print("Leitura: o CONSERVADOR assume custo 30% pior que o esperado. Se mesmo no")
    print("conservador a conta fecha (ROAS acima do seu equilíbrio), o risco é baixo.")
    print("Projeção é hipótese — valide com os números REAIS na primeira semana.")
    return 0


# ----------------------------------------------------------------------------
# diagnostico: lê a exportação colada e classifica cada campanha/conjunto/anúncio
# ----------------------------------------------------------------------------

# apelidos de coluna (tudo minúsculo, sem acento) -> chave canônica
ALIASES = {
    "nome": ["nome", "campanha", "conjunto de anuncios", "conjunto", "anuncio", "anuncios",
             "nome da campanha", "campaign", "ad set name", "ad set", "ad name", "ad", "adset"],
    "gasto": ["gasto", "valor gasto", "valor usado", "custo", "investimento", "amount spent",
              "spend", "cost", "gasto (brl)", "valor investido"],
    "impressoes": ["impressoes", "impressao", "impressions", "impr", "impr."],
    "cliques": ["cliques", "cliques no link", "clicks", "link clicks", "cliques (todos)"],
    "ctr": ["ctr", "ctr (todos)", "ctr do link", "ctr (link)", "ctr link", "click-through rate",
            "taxa de cliques"],
    "cpm": ["cpm", "cpm (brl)", "custo por mil"],
    "cpc": ["cpc", "cpc (link)", "cpc do link", "custo por clique", "cost per click"],
    "resultados": ["resultados", "resultado", "conversoes", "conversao", "vendas", "compras",
                   "leads", "cadastros", "results", "conversions", "purchases", "cadastro"],
    "cpa": ["cpa", "cpl", "custo por resultado", "custo por lead", "custo por venda",
            "custo por compra", "custo por conversao", "cost per result", "cpr",
            "custo por resultados"],
    "roas": ["roas", "retorno", "roas de compras", "purchase roas", "retorno sobre investimento"],
    "frequencia": ["frequencia", "freq", "frequency", "frequencia media"],
    "receita": ["receita", "valor de conversao", "valor de compra", "faturamento",
                "conversion value", "purchase value", "revenue"],
}


def _norm(s):
    s = str(s).strip().lower()
    for a, b in zip("áàâãäéèêëíìîïóòôõöúùûüç", "aaaaaeeeeiiiiooooouuuuc"):
        s = s.replace(a, b)
    return s


def _map_headers(headers):
    mapa = {}
    for i, h in enumerate(headers):
        hn = _norm(h)
        for chave, apelidos in ALIASES.items():
            if hn in apelidos and chave not in mapa:
                mapa[chave] = i
                break
    # segunda passada: match por "contém" para cabeçalhos compostos
    for i, h in enumerate(headers):
        hn = _norm(h)
        for chave, apelidos in ALIASES.items():
            if chave in mapa:
                continue
            if any(ap in hn for ap in apelidos):
                mapa[chave] = i
    return mapa


def _sniff_delim(texto):
    linha = texto.splitlines()[0] if texto.splitlines() else ""
    if "\t" in linha:
        return "\t"
    if linha.count(";") >= linha.count(","):
        if ";" in linha:
            return ";"
    if "," in linha:
        return ","
    # colunas separadas por múltiplos espaços
    return None


def _read_table(caminho):
    with open(caminho, "r", encoding="utf-8-sig", errors="replace") as f:
        texto = f.read()
    texto = texto.strip("\n")
    if not texto.strip():
        return [], []
    delim = _sniff_delim(texto)
    linhas = [l for l in texto.splitlines() if l.strip()]
    if delim is None:
        # divide por 2+ espaços
        rows = [re.split(r"\s{2,}|\t", l.strip()) for l in linhas]
    else:
        rows = list(csv.reader(linhas, delimiter=delim))
    if not rows:
        return [], []
    headers = [c.strip() for c in rows[0]]
    dados = [r for r in rows[1:]]
    return headers, dados


def _benchmarks():
    # Referência Meta Ads Brasil 2026 — SÓ referência, varia MUITO por nicho.
    return {
        "ctr_bom": 1.5,      # % CTR de link acima disso é bom
        "ctr_ruim": 0.6,     # abaixo disso, criativo/oferta fraca
        "cpm_alto": 40.0,    # R$ acima disso, público caro/saturado (feed)
        "freq_alerta": 2.5,  # frequência acima disso em público frio = fadiga
        "freq_critica": 4.0,
        "gasto_minimo": None,  # definido por CPA-alvo (2x) na função
    }


def cmd_diagnostico(args):
    caminho = args.arquivo
    if not caminho or not os.path.exists(caminho):
        print("ERRO: passe --arquivo com o caminho da tabela colada (CSV/TSV/tabela).")
        print("Dica: cole a exportação do Gerenciador de Anúncios num arquivo .csv e aponte aqui.")
        return 2

    cpa_alvo = parse_num(args.cpa_alvo) if args.cpa_alvo else None
    cpa_max = parse_num(args.cpa_max) if args.cpa_max else None
    if cpa_max is None and cpa_alvo is not None:
        cpa_max = cpa_alvo * 3   # heurística: máximo ~3x o alvo se só o alvo foi dado
    bm = _benchmarks()

    headers, dados = _read_table(caminho)
    if not headers or not dados:
        print("ERRO: não consegui ler nenhuma linha de dados no arquivo.")
        return 2
    mapa = _map_headers(headers)
    if "gasto" not in mapa and "resultados" not in mapa:
        print("ATENÇÃO: não reconheci as colunas de gasto/resultados no cabeçalho.")
        print(f"Cabeçalho lido: {headers}")
        print("Renomeie as colunas para algo como: Nome, Gasto, Impressões, Cliques, Resultados, CPA, ROAS, Frequência")
        return 2

    def val(row, chave):
        i = mapa.get(chave)
        if i is None or i >= len(row):
            return None
        return row[i]

    linhas_out = []
    gasto_total = 0.0
    result_total = 0.0
    receita_total = 0.0
    for row in dados:
        if not any((c or "").strip() for c in row):
            continue
        nome = (val(row, "nome") or "(sem nome)").strip()
        gasto = parse_num(val(row, "gasto"))
        impr = parse_num(val(row, "impressoes"))
        cliques = parse_num(val(row, "cliques"))
        ctr = parse_pct(val(row, "ctr"))
        cpc = parse_num(val(row, "cpc"))
        resultados = parse_num(val(row, "resultados"))
        cpa = parse_num(val(row, "cpa"))
        roas = parse_num(val(row, "roas"))
        freq = parse_num(val(row, "frequencia"))
        receita = parse_num(val(row, "receita"))

        # deriva o que der (só com o que foi colado — nunca inventa)
        if ctr is None and impr and cliques is not None and impr > 0:
            ctr = (cliques / impr) * 100.0
        if cpc is None and cliques and gasto is not None and cliques > 0:
            cpc = gasto / cliques
        if cpa is None and resultados and gasto is not None and resultados > 0:
            cpa = gasto / resultados
        if roas is None and receita is not None and gasto and gasto > 0:
            roas = receita / gasto

        if gasto:
            gasto_total += gasto
        if resultados:
            result_total += resultados
        if receita:
            receita_total += receita

        # ---------- decisão (precedência explícita) ----------
        veredito = None
        emoji = "⚪"
        motivos = []
        acoes = []

        re_eq = parse_num(args.roas_equilibrio) if args.roas_equilibrio else None
        tem_zero_result = (resultados is not None and resultados == 0)

        # "ainda é cedo": pouco gasto E pouco resultado acumulado
        pouco_gasto = False
        poucos_result = (resultados is None or resultados < 10)
        if cpa_max is not None and gasto is not None:
            if gasto < cpa_max and poucos_result:
                pouco_gasto = True
        elif gasto is not None and gasto < 20 and poucos_result:
            pouco_gasto = True

        # PRECEDÊNCIA 1 — gastou acima do teto e trouxe ZERO resultado: MATAR
        if tem_zero_result and gasto is not None and (
                (cpa_max is not None and gasto >= cpa_max) or (cpa_max is None and gasto >= 50)):
            veredito, emoji = "MATAR", "🔴"
            motivos.append(f"gastou {brl(gasto)} e 0 resultado (acima do custo de 1 venda)")
            acoes.append("pausar; com 0 resultado o gargalo costuma ser oferta/página, não só o anúncio")

        # PRECEDÊNCIA 2 — CPA contra o equilíbrio do dono
        elif cpa is not None and cpa_max is not None:
            if cpa > cpa_max:
                veredito, emoji = "MATAR", "🔴"
                motivos.append(f"CPA {brl(cpa)} acima do máximo {brl(cpa_max)} (paga p/ vender)")
                acoes.append("pausar; realocar verba para o que converte abaixo do teto")
            elif cpa_alvo is not None and cpa <= cpa_alvo:
                veredito, emoji = "ESCALAR", "🟢"
                motivos.append(f"CPA {brl(cpa)} dentro/abaixo do alvo {brl(cpa_alvo)}")
                acoes.append("subir verba ~20%/dia SEM resetar aprendizado; duplicar em público novo")
            else:
                veredito, emoji = "AJUSTAR", "🟡"
                motivos.append(f"CPA {brl(cpa)} entre o alvo e o teto — dá pra melhorar")
                acoes.append("testar novo criativo/gancho; refinar público; checar a página")

        # PRECEDÊNCIA 3 — ROAS contra o equilíbrio (quando não há CPA)
        elif roas is not None and re_eq:
            if roas < re_eq:
                veredito, emoji = "MATAR", "🔴"
                motivos.append(f"ROAS {num(roas)}x abaixo do equilíbrio {num(re_eq)}x")
                acoes.append("pausar ou reformular oferta/criativo")
            elif roas >= re_eq * 1.5:
                veredito, emoji = "ESCALAR", "🟢"
                motivos.append(f"ROAS {num(roas)}x bem acima do equilíbrio {num(re_eq)}x")
                acoes.append("subir verba gradual; proteger o que funciona")
            else:
                veredito, emoji = "AJUSTAR", "🟡"
                motivos.append(f"ROAS {num(roas)}x perto do equilíbrio — margem apertada")
                acoes.append("otimizar antes de escalar")

        # PRECEDÊNCIA 4 — ainda é cedo
        if veredito is None and pouco_gasto:
            veredito, emoji = "AGUARDAR", "⚪"
            motivos.append("gasto/resultado ainda baixo p/ decidir (fase de aprendizado)")
            acoes.append("aguardar ~50 resultados ou 3-4 dias antes de mexer")

        # PRECEDÊNCIA 5 — não deu pra decidir sem inventar
        if veredito is None:
            veredito, emoji = "FALTOU DADO", "⚠️"
            motivos.append("sem CPA nem ROAS na tabela — não dá pra julgar sem inventar")
            acoes.append("inclua a coluna de resultados/CPA ou de ROAS na exportação")

        # sinais secundários (não mudam o veredito, mas avisam)
        avisos = []
        if freq is not None and freq >= bm["freq_critica"]:
            avisos.append(f"frequência {num(freq)} MUITO alta → fadiga de criativo, troque já")
        elif freq is not None and freq >= bm["freq_alerta"]:
            avisos.append(f"frequência {num(freq)} subindo → prepare criativo novo")
        if ctr is not None and ctr < bm["ctr_ruim"]:
            avisos.append(f"CTR {num(ctr)}% baixo → criativo/gancho não para o dedo")
        if cpc is not None and ctr is not None and ctr < bm["ctr_ruim"]:
            pass  # já coberto

        linhas_out.append({
            "nome": nome, "gasto": gasto, "resultados": resultados, "cpa": cpa,
            "roas": roas, "ctr": ctr, "freq": freq, "veredito": veredito,
            "emoji": emoji, "motivos": motivos, "acoes": acoes, "avisos": avisos,
        })

    # ordena: MATAR primeiro, depois AJUSTAR, ESCALAR, AGUARDAR, FALTOU DADO; dentro por gasto desc
    ordem = {"MATAR": 0, "AJUSTAR": 1, "ESCALAR": 2, "AGUARDAR": 3, "FALTOU DADO": 4}
    linhas_out.sort(key=lambda x: (ordem.get(x["veredito"], 9), -(x["gasto"] or 0)))

    print("=" * 66)
    print("DIAGNÓSTICO DE MÍDIA PAGA")
    if cpa_alvo is not None or cpa_max is not None:
        print(f"CPA-alvo: {brl(cpa_alvo)}   |   CPA máximo (teto): {brl(cpa_max)}")
    print("=" * 66)
    contagem = {}
    for l in linhas_out:
        contagem[l["veredito"]] = contagem.get(l["veredito"], 0) + 1
        print(f"\n{l['emoji']} {l['veredito']}  —  {l['nome']}")
        campos = []
        if l["gasto"] is not None: campos.append(f"gasto {brl(l['gasto'])}")
        if l["resultados"] is not None: campos.append(f"result. {num(l['resultados'],0)}")
        if l["cpa"] is not None: campos.append(f"CPA {brl(l['cpa'])}")
        if l["roas"] is not None: campos.append(f"ROAS {num(l['roas'])}x")
        if l["ctr"] is not None: campos.append(f"CTR {num(l['ctr'])}%")
        if l["freq"] is not None: campos.append(f"freq {num(l['freq'])}")
        if campos:
            print("   " + "  ·  ".join(campos))
        for m in l["motivos"]:
            print(f"   → {m}")
        for a in l["acoes"]:
            print(f"   ✔ {a}")
        for w in l["avisos"]:
            print(f"   ⚠ {w}")

    print("\n" + "=" * 66)
    print("RESUMO: " + "  ·  ".join(f"{k} {v}" for k, v in
          sorted(contagem.items(), key=lambda kv: ordem.get(kv[0], 9))))
    cpa_geral = (gasto_total / result_total) if result_total > 0 else None
    roas_geral = (receita_total / gasto_total) if gasto_total > 0 and receita_total > 0 else None
    linha = f"Gasto total {brl(gasto_total)}"
    if result_total: linha += f"  ·  {num(result_total,0)} resultados  ·  CPA geral {brl(cpa_geral)}"
    if roas_geral: linha += f"  ·  ROAS geral {num(roas_geral)}x"
    print(linha)
    print("Lembre: a Turbina SUGERE. Quem pausa/escala na conta é você.")
    print("=" * 66)
    return 0


# ----------------------------------------------------------------------------
# aprendizado: memória do que funcionou / fracassou
# ----------------------------------------------------------------------------

def _turbina_dir(args):
    d = args.dir or ".turbina"
    os.makedirs(d, exist_ok=True)
    return d


def cmd_aprendizado(args):
    d = _turbina_dir(args)
    caminho = os.path.join(d, "aprendizados.csv")
    campos = ["tipo", "o_que", "publico", "resultado", "nota"]
    if args.listar or (not args.o_que):
        if not os.path.exists(caminho):
            print("Nenhum aprendizado registrado ainda. Use --tipo venceu/fracassou --o-que \"...\"")
            return 0
        with open(caminho, encoding="utf-8") as f:
            r = list(csv.DictReader(f))
        if not r:
            print("Nenhum aprendizado registrado ainda.")
            return 0
        print("APRENDIZADOS (memória de tráfego)")
        print("-" * 50)
        for row in r:
            marca = "🏆" if row.get("tipo", "").startswith("venc") else "💀"
            print(f"{marca} [{row.get('tipo','')}] {row.get('o_que','')}"
                  + (f" · público: {row['publico']}" if row.get('publico') else "")
                  + (f" · {row['resultado']}" if row.get('resultado') else ""))
        return 0
    # grava
    novo = {
        "tipo": args.tipo or "venceu",
        "o_que": args.o_que,
        "publico": args.publico or "",
        "resultado": args.resultado or "",
        "nota": args.nota or "",
    }
    existe = os.path.exists(caminho)
    with open(caminho, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            w.writeheader()
        w.writerow(novo)
    print(f"Aprendizado guardado: [{novo['tipo']}] {novo['o_que']}")
    return 0


# ----------------------------------------------------------------------------
# painel: resumo a partir de metricas.csv (última exportação) e aprendizados
# ----------------------------------------------------------------------------

def cmd_painel(args):
    d = args.dir or ".turbina"
    print("=" * 56)
    print("PAINEL TURBINA")
    print("=" * 56)
    met = os.path.join(d, "metricas.csv")
    if os.path.exists(met):
        headers, dados = _read_table(met)
        mapa = _map_headers(headers)
        gt = rt = 0.0
        for row in dados:
            i = mapa.get("gasto"); r = mapa.get("resultados")
            if i is not None and i < len(row):
                g = parse_num(row[i]);  gt += g or 0
            if r is not None and r < len(row):
                res = parse_num(row[r]); rt += res or 0
        print(f"Última exportação: gasto {brl(gt)}  ·  {num(rt,0)} resultados"
              + (f"  ·  CPA geral {brl(gt/rt)}" if rt else ""))
    else:
        print("Sem metricas.csv ainda — rode um diagnóstico e salve a exportação em .turbina/metricas.csv")
    apr = os.path.join(d, "aprendizados.csv")
    if os.path.exists(apr):
        with open(apr, encoding="utf-8") as f:
            n = max(0, sum(1 for _ in f) - 1)
        print(f"Aprendizados guardados: {n}")
    print("=" * 56)
    return 0


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(prog="turbina", description="Motor de tráfego pago (offline).")
    sub = p.add_subparsers(dest="cmd")

    pe = sub.add_parser("equilibrio", help="ROAS/CPA de equilíbrio a partir da sua margem")
    pe.add_argument("--ticket", required=True)
    pe.add_argument("--margem", required=False)
    pe.add_argument("--fatia-lucro", type=float, default=None,
                    help="fração da margem que aceita gastar no anúncio (padrão 0.33)")
    pe.set_defaults(func=cmd_equilibrio)

    pv = sub.add_parser("verba", help="projeta resultado de um orçamento (3 cenários)")
    pv.add_argument("--orcamento", required=True)
    pv.add_argument("--periodo", choices=["mes", "dia"], default="mes")
    pv.add_argument("--cpl", required=False)
    pv.add_argument("--cpa", required=False)
    pv.add_argument("--conv", required=False, help="conversao lead->venda em pct")
    pv.add_argument("--ticket", required=False)
    pv.set_defaults(func=cmd_verba)

    pd = sub.add_parser("diagnostico", help="lê a tabela colada e classifica cada campanha")
    pd.add_argument("--arquivo", required=True)
    pd.add_argument("--cpa-alvo", required=False)
    pd.add_argument("--cpa-max", required=False)
    pd.add_argument("--roas-equilibrio", required=False)
    pd.set_defaults(func=cmd_diagnostico)

    pa = sub.add_parser("aprendizado", help="guarda/lista o que venceu/fracassou")
    pa.add_argument("--tipo", choices=["venceu", "fracassou"], required=False)
    pa.add_argument("--o-que", dest="o_que", required=False)
    pa.add_argument("--publico", required=False)
    pa.add_argument("--resultado", required=False)
    pa.add_argument("--nota", required=False)
    pa.add_argument("--listar", action="store_true")
    pa.add_argument("--dir", required=False, help="pasta de dados (padrao .turbina)")
    pa.set_defaults(func=cmd_aprendizado)

    pp = sub.add_parser("painel", help="resumo do mês a partir dos arquivos locais")
    pp.add_argument("--dir", required=False)
    pp.set_defaults(func=cmd_painel)

    args = p.parse_args()
    if not getattr(args, "cmd", None):
        p.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
