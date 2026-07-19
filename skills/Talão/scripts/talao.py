#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Talão — motor do talão de orçamentos para prestadores de serviço.

Para o DONO do serviço (instalador, obra, manutenção, edição, marketing,
consultoria, qualquer trabalho por job): guarda cada orçamento, soma material +
mão de obra + custos, aplica custo indireto, margem, desconto e imposto NA ORDEM
CERTA, e acompanha o ciclo do orçamento (rascunho → enviado → aceito/recusado).
Usa SOMENTE a biblioteca padrão do Python. Nunca inventa nada: tudo que sai daqui
veio do que você registrou ou de uma conta feita aqui. O Talão organiza e calcula
o número; a conversa com o cliente e a decisão de fechar são suas (a IA escreve as
mensagens; o motor faz a matemática).

Dinheiro é tratado com Decimal (centavo exato, sem erro de float). A ordem das
contas é a correta de um orçamento honesto:
    1. cada item: (valor_unit × qtd × coef) + frete      -> custo direto do item
    2. soma por tipo (material / mão de obra / serviço / custo) -> CUSTO DIRETO
    3. custo indireto (overhead %) sobre o custo direto  -> some -> BASE DE CUSTO
    4. margem/lucro (%) sobre a base de custo            -> SUBTOTAL (preço cheio)
    5. desconto (R$ ou %) sobre o subtotal               -> BASE TRIBUTÁVEL
    6. imposto (%) sobre a base tributável (por fora)    -> + imposto -> TOTAL
    7. parcelas: total ÷ nº de parcelas

O documento que vai pro CLIENTE (comando `html`) mostra os itens e o TOTAL — nunca
o seu custo/overhead/margem (isso é interno, do comando `calcular`).

Cada orçamento é um arquivo JSON em .talao/orcamentos/<numero>.json com:
    numero, cliente, contato, descricao, criado_em, validade_dias, validade_data,
    status (rascunho|enviado|aceito|recusado|expirado),
    enviado_em, respondido_em, motivo,
    itens[]   -> {id, tipo, descricao, qtd, unidade, valor_unit, coef, frete}
    overhead  -> % de custo indireto
    margem    -> % de lucro
    desconto  -> {tipo: "valor"|"percent", valor}
    imposto   -> % (ISS/Simples), por fora
    parcelas  -> nº
    obs       -> texto livre que aparece no documento

Comandos (resumo — veja --help de cada um no SKILL.md):
    novo, listar, editar, item-add, item-rm, itens, ajustes,
    calcular, html, status, pendentes, resumo
Opções globais:
    --pasta <dir>     (padrão: .talao)
    --formato json    (padrão: texto)
"""

import argparse
import html as _html
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

PASTA_PADRAO = ".talao"
TIPOS = ["material", "mao_de_obra", "servico", "custo"]
NOME_TIPO = {
    "material": "Material",
    "mao_de_obra": "Mão de obra",
    "servico": "Serviço",
    "custo": "Custo / despesa",
}
STATUS = ["rascunho", "enviado", "aceito", "recusado", "expirado"]
DIN0 = Decimal("0.00")


# ----------------------------------------------------------------- utilidades

def _norm(s):
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def D(x):
    """Para Decimal com 2 casas, arredondando meio-para-cima."""
    if x is None:
        x = 0
    if not isinstance(x, Decimal):
        x = Decimal(str(x))
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_dinheiro(bruto):
    """'R$ 1.234,56', '1.234,56', '1234.56', '1500', 1500 -> Decimal(2) ou None."""
    if bruto is None:
        return None
    if isinstance(bruto, (int, float, Decimal)):
        return D(bruto)
    s = str(bruto).strip()
    if not s:
        return None
    s = s.replace("R$", "").replace("r$", "").strip()
    s = re.sub(r"\s", "", s)
    if "," in s and "." in s:            # 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                        # 1234,56 -> 1234.56
        s = s.replace(",", ".")
    elif "." in s:
        # Só pontos. No padrão BR, "1.890" / "12.000" / "1.234.567" são MILHAR,
        # não decimal. Tratamos o ponto como separador de milhar quando há mais de
        # um ponto, ou quando o grupo após o último ponto tem 3 dígitos (1.890).
        # Caso contrário é decimal (1.89, 10.5, 1234.56).
        partes = s.split(".")
        if len(partes) > 2 or len(partes[-1]) == 3:
            s = "".join(partes)
    try:
        return D(s)
    except (InvalidOperation, ValueError):
        return None


def parse_num(bruto, padrao=None):
    """Número simples (qtd, %, coef). Aceita vírgula decimal. -> Decimal ou padrao."""
    if bruto is None:
        return padrao
    if isinstance(bruto, (int, float, Decimal)):
        return Decimal(str(bruto))
    s = str(bruto).strip().replace("%", "").replace(",", ".")
    if not s:
        return padrao
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return padrao


def fmt(v):
    """Decimal/num -> 'R$ 1.234,56'."""
    v = D(v)
    neg = v < 0
    v = abs(v)
    inteiro, _, dec = f"{v:.2f}".partition(".")
    partes = []
    while len(inteiro) > 3:
        partes.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    partes.insert(0, inteiro)
    txt = "R$ " + ".".join(partes) + "," + dec
    return ("- " + txt) if neg else txt


def fmt_num(v):
    """Decimal -> texto enxuto: 3, 2,5, 1,75 (sem casas inúteis)."""
    v = Decimal(str(v))
    s = f"{v.normalize():f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def hoje():
    return date.today()


def parse_data(bruto):
    """DD/MM/AAAA, DD/MM/AA, AAAA-MM-DD -> date ou None."""
    if not bruto:
        return None
    s = str(bruto).strip()
    for f in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None


def fmt_data(d):
    if isinstance(d, str):
        d = parse_data(d)
    return d.strftime("%d/%m/%Y") if d else "—"


# ----------------------------------------------------------------- persistência

def dir_orcamentos(pasta):
    return os.path.join(pasta, "orcamentos")


def caminho(pasta, numero):
    return os.path.join(dir_orcamentos(pasta), f"{int(numero):04d}.json")


def carregar(pasta, numero):
    p = caminho(pasta, numero)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fp:
        return json.load(fp)


def salvar(pasta, orc):
    os.makedirs(dir_orcamentos(pasta), exist_ok=True)
    with open(caminho(pasta, orc["numero"]), "w", encoding="utf-8") as fp:
        json.dump(orc, fp, ensure_ascii=False, indent=2)


def listar_todos(pasta):
    d = dir_orcamentos(pasta)
    if not os.path.isdir(d):
        return []
    out = []
    for nome in sorted(os.listdir(d)):
        if nome.endswith(".json"):
            with open(os.path.join(d, nome), encoding="utf-8") as fp:
                out.append(json.load(fp))
    return out


def proximo_numero(pasta):
    todos = listar_todos(pasta)
    return (max((o["numero"] for o in todos), default=0)) + 1


# ----------------------------------------------------------------- cálculo

def expirado(orc):
    vd = parse_data(orc.get("validade_data"))
    if not vd:
        return False
    return orc.get("status") in ("rascunho", "enviado") and vd < hoje()


def calcular(orc):
    """Devolve um dicionário com toda a quebra de números (Decimal)."""
    por_tipo = {t: DIN0 for t in TIPOS}
    linhas = []
    for it in orc.get("itens", []):
        qtd = Decimal(str(it.get("qtd", 1)))
        coef = Decimal(str(it.get("coef", 1)))
        vu = D(it.get("valor_unit", 0))
        frete = D(it.get("frete", 0))
        total_item = D(vu * qtd * coef + frete)
        por_tipo[it.get("tipo", "servico")] = por_tipo.get(it.get("tipo", "servico"), DIN0) + total_item
        linhas.append({**it, "total_item": total_item})

    custo_direto = D(sum(por_tipo.values()))
    overhead_pct = Decimal(str(orc.get("overhead", 0)))
    indiretos = D(custo_direto * overhead_pct / 100)
    base_custo = D(custo_direto + indiretos)

    margem_pct = Decimal(str(orc.get("margem", 0)))
    lucro = D(base_custo * margem_pct / 100)
    subtotal = D(base_custo + lucro)

    desc = orc.get("desconto") or {}
    if desc.get("tipo") == "percent":
        desconto_val = D(subtotal * Decimal(str(desc.get("valor", 0))) / 100)
    else:
        desconto_val = D(desc.get("valor", 0))
    if desconto_val > subtotal:
        desconto_val = subtotal
    base_trib = D(subtotal - desconto_val)

    imposto_pct = Decimal(str(orc.get("imposto", 0)))
    imposto_val = D(base_trib * imposto_pct / 100)
    total = D(base_trib + imposto_val)

    parcelas = int(orc.get("parcelas", 1) or 1)
    parcela_val = D(total / parcelas) if parcelas > 0 else total

    return {
        "por_tipo": por_tipo,
        "linhas": linhas,
        "custo_direto": custo_direto,
        "overhead_pct": overhead_pct,
        "indiretos": indiretos,
        "base_custo": base_custo,
        "margem_pct": margem_pct,
        "lucro": lucro,
        "subtotal": subtotal,
        "desconto_val": desconto_val,
        "base_trib": base_trib,
        "imposto_pct": imposto_pct,
        "imposto_val": imposto_val,
        "total": total,
        "parcelas": parcelas,
        "parcela_val": parcela_val,
    }


# ----------------------------------------------------------------- comandos

def cmd_novo(args):
    pasta = args.pasta
    numero = args.numero or proximo_numero(pasta)
    if carregar(pasta, numero):
        print(f"Já existe o orçamento Nº {int(numero):04d}.")
        return 1
    validade = int(args.validade) if args.validade else 15
    orc = {
        "numero": int(numero),
        "cliente": args.cliente or "",
        "contato": args.contato or "",
        "descricao": args.descricao or "",
        "criado_em": hoje().isoformat(),
        "validade_dias": validade,
        "validade_data": (hoje() + timedelta(days=validade)).isoformat(),
        "status": "rascunho",
        "enviado_em": None,
        "respondido_em": None,
        "motivo": "",
        "itens": [],
        "overhead": parse_num(args.overhead, Decimal(0)).__float__() if args.overhead else 0,
        "margem": parse_num(args.margem, Decimal(0)).__float__() if args.margem else 0,
        "desconto": {"tipo": "valor", "valor": 0.0},
        "imposto": parse_num(args.imposto, Decimal(0)).__float__() if args.imposto else 0,
        "parcelas": int(args.parcelas) if args.parcelas else 1,
        "obs": args.obs or "",
    }
    salvar(pasta, orc)
    if args.formato == "json":
        print(json.dumps({"numero": orc["numero"]}, ensure_ascii=False))
    else:
        print(f"Orçamento Nº {orc['numero']:04d} criado para «{orc['cliente'] or 'cliente a definir'}».")
        print(f"Validade: {orc['validade_dias']} dias (até {fmt_data(orc['validade_data'])}).")
        print("Próximo passo: adicione os itens com `item-add`.")
    return 0


def _achar(args):
    orc = carregar(args.pasta, args.num)
    if not orc:
        print(f"Não encontrei o orçamento Nº {args.num}.")
        return None
    return orc


def cmd_editar(args):
    orc = _achar(args)
    if not orc:
        return 1
    if args.cliente is not None:
        orc["cliente"] = args.cliente
    if args.contato is not None:
        orc["contato"] = args.contato
    if args.descricao is not None:
        orc["descricao"] = args.descricao
    if args.obs is not None:
        orc["obs"] = args.obs
    if args.validade:
        orc["validade_dias"] = int(args.validade)
        base = parse_data(orc.get("criado_em")) or hoje()
        orc["validade_data"] = (base + timedelta(days=int(args.validade))).isoformat()
    salvar(args.pasta, orc)
    print(f"Orçamento Nº {orc['numero']:04d} atualizado.")
    return 0


def cmd_item_add(args):
    orc = _achar(args)
    if not orc:
        return 1
    tipo = args.tipo
    if tipo not in TIPOS:
        print(f"Tipo inválido. Use um de: {', '.join(TIPOS)}.")
        return 1
    valor = parse_dinheiro(args.valor)
    if valor is None:
        print("Valor unitário inválido. Ex.: --valor \"R$ 120,00\".")
        return 1
    novo_id = max((i["id"] for i in orc["itens"]), default=0) + 1
    item = {
        "id": novo_id,
        "tipo": tipo,
        "descricao": args.desc or "",
        "qtd": float(parse_num(args.qtd, Decimal(1))),
        "unidade": args.unid or "un",
        "valor_unit": float(valor),
        "coef": float(parse_num(args.coef, Decimal(1))),
        "frete": float(parse_dinheiro(args.frete) or 0),
    }
    orc["itens"].append(item)
    salvar(args.pasta, orc)
    c = calcular(orc)
    print(f"Item #{novo_id} ({NOME_TIPO[tipo]}) adicionado: {item['descricao']}.")
    print(f"Custo direto acumulado: {fmt(c['custo_direto'])}.")
    return 0


def cmd_item_rm(args):
    orc = _achar(args)
    if not orc:
        return 1
    antes = len(orc["itens"])
    orc["itens"] = [i for i in orc["itens"] if i["id"] != int(args.id)]
    if len(orc["itens"]) == antes:
        print(f"Não achei o item #{args.id}.")
        return 1
    salvar(args.pasta, orc)
    print(f"Item #{args.id} removido.")
    return 0


def cmd_itens(args):
    orc = _achar(args)
    if not orc:
        return 1
    c = calcular(orc)
    if args.formato == "json":
        print(json.dumps({"linhas": [
            {"id": l["id"], "tipo": l["tipo"], "descricao": l["descricao"],
             "total_item": float(l["total_item"])} for l in c["linhas"]],
            "custo_direto": float(c["custo_direto"])}, ensure_ascii=False))
        return 0
    print(f"Itens do orçamento Nº {orc['numero']:04d} — {orc.get('cliente','')}")
    if not c["linhas"]:
        print("  (nenhum item ainda — use `item-add`)")
        return 0
    for t in TIPOS:
        grupo = [l for l in c["linhas"] if l["tipo"] == t]
        if not grupo:
            continue
        print(f"\n  {NOME_TIPO[t]}:")
        for l in grupo:
            extra = []
            if Decimal(str(l.get("coef", 1))) != 1:
                extra.append(f"coef {fmt_num(l['coef'])}")
            if D(l.get("frete", 0)) > 0:
                extra.append(f"frete {fmt(l['frete'])}")
            ex = f"  [{'; '.join(extra)}]" if extra else ""
            print(f"    #{l['id']} {l['descricao']} — {fmt_num(l['qtd'])} {l['unidade']} × "
                  f"{fmt(l['valor_unit'])} = {fmt(l['total_item'])}{ex}")
        print(f"    subtotal {NOME_TIPO[t]}: {fmt(c['por_tipo'][t])}")
    print(f"\n  CUSTO DIRETO TOTAL: {fmt(c['custo_direto'])}")
    return 0


def cmd_ajustes(args):
    orc = _achar(args)
    if not orc:
        return 1
    if args.overhead is not None:
        orc["overhead"] = float(parse_num(args.overhead, Decimal(0)))
    if args.margem is not None:
        orc["margem"] = float(parse_num(args.margem, Decimal(0)))
    if args.imposto is not None:
        orc["imposto"] = float(parse_num(args.imposto, Decimal(0)))
    if args.parcelas is not None:
        orc["parcelas"] = int(args.parcelas)
    if args.desconto is not None:
        v = parse_dinheiro(args.desconto)
        orc["desconto"] = {"tipo": "valor", "valor": float(v or 0)}
    if args.desconto_pct is not None:
        orc["desconto"] = {"tipo": "percent", "valor": float(parse_num(args.desconto_pct, Decimal(0)))}
    if args.validade:
        orc["validade_dias"] = int(args.validade)
        base = parse_data(orc.get("criado_em")) or hoje()
        orc["validade_data"] = (base + timedelta(days=int(args.validade))).isoformat()
    salvar(args.pasta, orc)
    print(f"Ajustes do orçamento Nº {orc['numero']:04d} atualizados.")
    return cmd_calcular(args)


def cmd_calcular(args):
    orc = _achar(args)
    if not orc:
        return 1
    c = calcular(orc)
    if args.formato == "json":
        out = {k: (float(v) if isinstance(v, Decimal) else v)
               for k, v in c.items() if k not in ("linhas", "por_tipo")}
        out["por_tipo"] = {t: float(c["por_tipo"][t]) for t in TIPOS}
        print(json.dumps(out, ensure_ascii=False))
        return 0
    print(f"════ Quebra do orçamento Nº {orc['numero']:04d} — {orc.get('cliente','')} ════")
    print("  (visão INTERNA — não mostre custo/margem ao cliente)\n")
    for t in TIPOS:
        if c["por_tipo"][t] > 0:
            print(f"  {NOME_TIPO[t]:<16} {fmt(c['por_tipo'][t])}")
    print(f"  {'─'*34}")
    print(f"  Custo direto        {fmt(c['custo_direto'])}")
    if c["overhead_pct"] > 0:
        print(f"  + Custo indireto ({fmt_num(c['overhead_pct'])}%)  {fmt(c['indiretos'])}")
    print(f"  = Base de custo     {fmt(c['base_custo'])}")
    if c["margem_pct"] > 0:
        print(f"  + Margem ({fmt_num(c['margem_pct'])}%)        {fmt(c['lucro'])}")
    print(f"  = Subtotal          {fmt(c['subtotal'])}")
    if c["desconto_val"] > 0:
        print(f"  - Desconto          {fmt(c['desconto_val'])}")
        print(f"  = Base tributável   {fmt(c['base_trib'])}")
    if c["imposto_pct"] > 0:
        print(f"  + Imposto ({fmt_num(c['imposto_pct'])}%)      {fmt(c['imposto_val'])}")
    print(f"  {'═'*34}")
    print(f"  TOTAL AO CLIENTE    {fmt(c['total'])}")
    if c["parcelas"] > 1:
        print(f"  em {c['parcelas']}× de {fmt(c['parcela_val'])}")
    if c["base_custo"] > 0:
        lucro_liq = D(c["base_trib"] - c["base_custo"])
        pct = D(lucro_liq / c["base_custo"] * 100) if c["base_custo"] else DIN0
        print(f"\n  Lucro estimado (após desconto, antes de imposto): {fmt(lucro_liq)} "
              f"({fmt_num(pct)}% sobre o custo)")
    return 0


def cmd_status(args):
    orc = _achar(args)
    if not orc:
        return 1
    novo = args.status
    if novo not in STATUS:
        print(f"Status inválido. Use: {', '.join(STATUS)}.")
        return 1
    orc["status"] = novo
    if novo == "enviado" and not orc.get("enviado_em"):
        orc["enviado_em"] = hoje().isoformat()
    if novo in ("aceito", "recusado"):
        orc["respondido_em"] = hoje().isoformat()
        if args.motivo:
            orc["motivo"] = args.motivo
    salvar(args.pasta, orc)
    print(f"Orçamento Nº {orc['numero']:04d} agora está «{novo}».")
    return 0


def cmd_pendentes(args):
    todos = listar_todos(args.pasta)
    dias_corte = int(args.dias) if args.dias else 3
    enviados, expirando, expirados = [], [], []
    for o in todos:
        if expirado(o):
            expirados.append(o)
            continue
        if o.get("status") == "enviado":
            env = parse_data(o.get("enviado_em")) or hoje()
            dias = (hoje() - env).days
            if dias >= dias_corte:
                enviados.append((o, dias))
        vd = parse_data(o.get("validade_data"))
        if vd and o.get("status") in ("rascunho", "enviado"):
            faltam = (vd - hoje()).days
            if 0 <= faltam <= 3:
                expirando.append((o, faltam))
    if args.formato == "json":
        print(json.dumps({
            "sem_resposta": [{"numero": o["numero"], "dias": d} for o, d in enviados],
            "expirando": [{"numero": o["numero"], "faltam": f} for o, f in expirando],
            "expirados": [o["numero"] for o in expirados],
        }, ensure_ascii=False))
        return 0
    print("════ Orçamentos que pedem ação ════\n")
    if enviados:
        print(f"  Enviados sem resposta há {dias_corte}+ dias (hora do follow-up):")
        for o, d in sorted(enviados, key=lambda x: -x[1]):
            c = calcular(o)
            print(f"    Nº {o['numero']:04d} — {o.get('cliente','')} — {fmt(c['total'])} — há {d} dias")
    if expirando:
        print("\n  Validade vencendo (≤3 dias):")
        for o, f in sorted(expirando, key=lambda x: x[1]):
            print(f"    Nº {o['numero']:04d} — {o.get('cliente','')} — vence em {f} dia(s) "
                  f"({fmt_data(o.get('validade_data'))})")
    if expirados:
        print("\n  Já expiraram (reenviar ou encerrar):")
        for o in expirados:
            print(f"    Nº {o['numero']:04d} — {o.get('cliente','')} — venceu {fmt_data(o.get('validade_data'))}")
    if not (enviados or expirando or expirados):
        print("  Nada pendente. Tudo em dia. 👍")
    return 0


def cmd_resumo(args):
    todos = listar_todos(args.pasta)
    if args.formato != "json":
        print("════ Painel do Talão ════\n")
    n = len(todos)
    por_status = {s: 0 for s in STATUS}
    valor_aberto = DIN0
    valor_aceito = DIN0
    totais_aceitos = []
    enviados_resp = 0
    aceitos = 0
    for o in todos:
        st = "expirado" if expirado(o) else o.get("status", "rascunho")
        por_status[st] = por_status.get(st, 0) + 1
        c = calcular(o)
        if st in ("rascunho", "enviado"):
            valor_aberto += c["total"]
        if st == "aceito":
            valor_aceito += c["total"]
            totais_aceitos.append(c["total"])
            aceitos += 1
        if o.get("status") in ("aceito", "recusado"):
            enviados_resp += 1
    taxa = (Decimal(aceitos) / Decimal(enviados_resp) * 100) if enviados_resp else DIN0
    ticket = D(sum(totais_aceitos) / len(totais_aceitos)) if totais_aceitos else DIN0
    if args.formato == "json":
        print(json.dumps({
            "total": n, "por_status": por_status,
            "valor_em_aberto": float(valor_aberto), "valor_aceito": float(valor_aceito),
            "taxa_aceite_pct": float(D(taxa)), "ticket_medio": float(ticket),
        }, ensure_ascii=False))
        return 0
    print(f"  Orçamentos no total: {n}")
    for s in STATUS:
        if por_status.get(s):
            print(f"    {s}: {por_status[s]}")
    print(f"\n  Valor em aberto (rascunho + enviado): {fmt(valor_aberto)}")
    print(f"  Valor fechado (aceito): {fmt(valor_aceito)}")
    print(f"  Taxa de aceite (dos respondidos): {fmt_num(D(taxa))}%")
    print(f"  Ticket médio dos aceitos: {fmt(ticket)}")
    return 0


# ----------------------------------------------------------------- documento HTML

def _logo_data_uri(caminho_logo):
    if not caminho_logo or not os.path.exists(caminho_logo):
        return None
    import base64
    import mimetypes
    mt = mimetypes.guess_type(caminho_logo)[0] or "image/png"
    with open(caminho_logo, "rb") as fp:
        b64 = base64.b64encode(fp.read()).decode("ascii")
    return f"data:{mt};base64,{b64}"


def cmd_html(args):
    orc = _achar(args)
    if not orc:
        return 1
    c = calcular(orc)
    cor = args.cor or "#1f6f6b"
    empresa = args.empresa or "Seu Serviço"
    contato = args.contato_rodape or ""
    logo_uri = _logo_data_uri(args.logo) if args.logo else None

    def esc(s):
        return _html.escape(str(s or ""))

    linhas_html = []
    for t in TIPOS:
        grupo = [l for l in c["linhas"] if l["tipo"] == t]
        if not grupo:
            continue
        linhas_html.append(
            f'<tr class="grupo"><td colspan="4">{esc(NOME_TIPO[t])}</td></tr>')
        for l in grupo:
            linhas_html.append(
                f'<tr><td>{esc(l["descricao"])}</td>'
                f'<td class="c">{fmt_num(l["qtd"])} {esc(l["unidade"])}</td>'
                f'<td class="r">{fmt(l["valor_unit"])}</td>'
                f'<td class="r">{fmt(l["total_item"])}</td></tr>')

    totais = [f'<tr><td>Subtotal</td><td class="r">{fmt(c["subtotal"])}</td></tr>']
    if c["desconto_val"] > 0:
        totais.append(f'<tr><td>Desconto</td><td class="r">- {fmt(c["desconto_val"])}</td></tr>')
    if c["imposto_pct"] > 0:
        totais.append(f'<tr><td>Imposto ({fmt_num(c["imposto_pct"])}%)</td>'
                      f'<td class="r">{fmt(c["imposto_val"])}</td></tr>')
    totais.append(f'<tr class="total"><td>TOTAL</td><td class="r">{fmt(c["total"])}</td></tr>')
    if c["parcelas"] > 1:
        totais.append(f'<tr class="parc"><td>Condição</td>'
                      f'<td class="r">{c["parcelas"]}× de {fmt(c["parcela_val"])}</td></tr>')

    logo_html = f'<img src="{logo_uri}" alt="logo" class="logo">' if logo_uri else \
        f'<div class="logo-txt">{esc(empresa)}</div>'

    obs_html = f'<div class="obs"><strong>Observações</strong><br>{esc(orc.get("obs",""))}</div>' \
        if orc.get("obs") else ""

    doc = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orçamento Nº {orc['numero']:04d} — {esc(orc.get('cliente',''))}</title>
<style>
  :root {{ --cor: {cor}; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    color: #222; margin: 0; background: #f4f4f2; }}
  .folha {{ max-width: 800px; margin: 24px auto; background: #fff; padding: 40px;
    box-shadow: 0 2px 14px rgba(0,0,0,.08); }}
  header {{ display: flex; justify-content: space-between; align-items: flex-start;
    border-bottom: 3px solid var(--cor); padding-bottom: 18px; margin-bottom: 22px; }}
  .logo {{ max-height: 64px; max-width: 220px; }}
  .logo-txt {{ font-size: 22px; font-weight: 700; color: var(--cor); }}
  .meta {{ text-align: right; font-size: 13px; color: #555; }}
  .meta .num {{ font-size: 20px; font-weight: 700; color: var(--cor); }}
  h1 {{ font-size: 15px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--cor); margin: 0 0 4px; }}
  .cliente {{ margin: 0 0 20px; font-size: 14px; }}
  .cliente strong {{ display: block; font-size: 16px; color: #111; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  thead th {{ text-align: left; background: var(--cor); color: #fff; padding: 9px 10px;
    font-size: 12px; letter-spacing: .04em; }}
  thead th.r {{ text-align: right; }} thead th.c {{ text-align: center; }}
  tbody td {{ padding: 8px 10px; border-bottom: 1px solid #eee; }}
  td.r {{ text-align: right; }} td.c {{ text-align: center; }}
  tr.grupo td {{ background: #f3f6f6; font-weight: 700; color: var(--cor);
    font-size: 12px; text-transform: uppercase; letter-spacing: .05em; }}
  .totais {{ width: 320px; margin-left: auto; margin-top: 16px; }}
  .totais td {{ padding: 7px 10px; }}
  .totais tr.total td {{ font-size: 18px; font-weight: 700; color: var(--cor);
    border-top: 2px solid var(--cor); }}
  .totais tr.parc td {{ color: #555; font-size: 13px; }}
  .cond {{ margin-top: 26px; font-size: 13px; color: #444; line-height: 1.6; }}
  .obs {{ margin-top: 18px; font-size: 13px; background: #faf8f3; padding: 14px 16px;
    border-left: 3px solid var(--cor); }}
  footer {{ margin-top: 34px; padding-top: 16px; border-top: 1px solid #eee;
    font-size: 12px; color: #888; text-align: center; }}
  @media print {{ body {{ background: #fff; }} .folha {{ box-shadow: none; margin: 0;
    max-width: none; padding: 0; }} }}
</style></head>
<body><div class="folha">
  <header>
    <div>{logo_html}</div>
    <div class="meta">
      <div class="num">ORÇAMENTO Nº {orc['numero']:04d}</div>
      <div>Emitido em {fmt_data(orc.get('criado_em'))}</div>
      <div>Válido até {fmt_data(orc.get('validade_data'))}</div>
    </div>
  </header>
  <h1>Para</h1>
  <div class="cliente"><strong>{esc(orc.get('cliente','Cliente'))}</strong>
    {esc(orc.get('contato',''))}</div>
  {('<p style="font-size:14px;color:#444;margin:-8px 0 18px">'+esc(orc.get('descricao',''))+'</p>') if orc.get('descricao') else ''}
  <table>
    <thead><tr><th>Descrição</th><th class="c">Qtd.</th>
      <th class="r">Valor unit.</th><th class="r">Total</th></tr></thead>
    <tbody>{''.join(linhas_html)}</tbody>
  </table>
  <table class="totais"><tbody>{''.join(totais)}</tbody></table>
  <div class="cond">
    <strong>Condições</strong><br>
    Validade da proposta: até {fmt_data(orc.get('validade_data'))}.<br>
    {('Pagamento: '+str(c['parcelas'])+'× de '+fmt(c['parcela_val'])+'.<br>') if c['parcelas']>1 else ''}
  </div>
  {obs_html}
  <footer>{esc(empresa)}{(' — '+esc(contato)) if contato else ''}</footer>
</div></body></html>"""

    os.makedirs(dir_orcamentos(args.pasta), exist_ok=True)
    saida = args.saida or os.path.join(dir_orcamentos(args.pasta), f"{orc['numero']:04d}.html")
    with open(saida, "w", encoding="utf-8") as fp:
        fp.write(doc)
    print(f"Documento gerado: {saida}")
    print("Abra no navegador e imprima em PDF (Ctrl/Cmd+P → Salvar como PDF) para enviar ao cliente.")
    return 0


# ----------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(description="Talão — motor de orçamentos por serviço.")
    p.add_argument("--pasta", default=PASTA_PADRAO)
    p.add_argument("--formato", choices=["texto", "json"], default="texto")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("novo")
    n.add_argument("--cliente"); n.add_argument("--contato"); n.add_argument("--descricao")
    n.add_argument("--validade"); n.add_argument("--numero", type=int)
    n.add_argument("--overhead"); n.add_argument("--margem"); n.add_argument("--imposto")
    n.add_argument("--parcelas"); n.add_argument("--obs")
    n.set_defaults(func=cmd_novo)

    e = sub.add_parser("editar"); e.add_argument("--num", required=True)
    e.add_argument("--cliente"); e.add_argument("--contato"); e.add_argument("--descricao")
    e.add_argument("--obs"); e.add_argument("--validade")
    e.set_defaults(func=cmd_editar)

    ia = sub.add_parser("item-add"); ia.add_argument("--num", required=True)
    ia.add_argument("--tipo", required=True); ia.add_argument("--desc", required=True)
    ia.add_argument("--qtd"); ia.add_argument("--unid"); ia.add_argument("--valor", required=True)
    ia.add_argument("--coef"); ia.add_argument("--frete")
    ia.set_defaults(func=cmd_item_add)

    ir = sub.add_parser("item-rm"); ir.add_argument("--num", required=True)
    ir.add_argument("--id", required=True); ir.set_defaults(func=cmd_item_rm)

    it = sub.add_parser("itens"); it.add_argument("--num", required=True)
    it.set_defaults(func=cmd_itens)

    aj = sub.add_parser("ajustes"); aj.add_argument("--num", required=True)
    aj.add_argument("--overhead"); aj.add_argument("--margem"); aj.add_argument("--imposto")
    aj.add_argument("--parcelas"); aj.add_argument("--desconto"); aj.add_argument("--desconto-pct", dest="desconto_pct")
    aj.add_argument("--validade")
    aj.set_defaults(func=cmd_ajustes)

    ca = sub.add_parser("calcular"); ca.add_argument("--num", required=True)
    ca.set_defaults(func=cmd_calcular)

    st = sub.add_parser("status"); st.add_argument("--num", required=True)
    st.add_argument("--status", required=True); st.add_argument("--motivo")
    st.set_defaults(func=cmd_status)

    pe = sub.add_parser("pendentes"); pe.add_argument("--dias")
    pe.set_defaults(func=cmd_pendentes)

    re_ = sub.add_parser("resumo"); re_.set_defaults(func=cmd_resumo)

    h = sub.add_parser("html"); h.add_argument("--num", required=True)
    h.add_argument("--empresa"); h.add_argument("--cor"); h.add_argument("--logo")
    h.add_argument("--contato-rodape", dest="contato_rodape"); h.add_argument("--saida")
    h.set_defaults(func=cmd_html)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
