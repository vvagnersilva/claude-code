#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fisco - motor do organizador fiscal + calendario de obrigacoes.

Somente biblioteca padrao do Python (stdlib). Sem pandas, sem rede, sem chave de
API, sem senha de banco ou da Receita. Guarda tudo numa pasta local .fisco/:
  .fisco/config.md        -> perfil fiscal do negocio (escrito na 1a execucao)
  .fisco/calendario.csv   -> obrigacoes fiscais recorrentes/unicas com vencimento

O motor faz APENAS a PARTE EXATA e SEGURA:
  1) CALENDARIO - guarda as obrigacoes, calcula o PROXIMO vencimento de cada uma
     pela recorrencia, e aponta o que esta 🔴 vencido / 🟠 vence hoje / 🟡 perto.
  2) FATOR R - razao pura folha/receita (nao envolve aliquota nenhuma) para
     indicar a tendencia de Anexo III x Anexo V no Simples.
  3) COMPARAR REGIME - aritmetica transparente sobre as aliquotas EFETIVAS que o
     DONO/CONTADOR informam (o motor NUNCA embute/inventa aliquota de tabela).

O motor NUNCA inventa aliquota, valor legal ou regra tributaria. A explicacao em
portugues simples e a decisao sao da IA + do dono, sempre com "confirme com seu
contador". Isto NAO e parecer contabil.

Uso (a IA chama por baixo; o dono so conversa):
  fisco.py init
  fisco.py add --obrig "DAS Simples Nacional" --freq mensal --dia 20 [--cat Imposto] [--obs ...]
  fisco.py add --obrig "DEFIS" --freq anual --data 31/03 [--cat Declaracao]
  fisco.py add --obrig "Parcelamento" --freq unico --data 15/08/2026
  fisco.py agenda [--dias 60] [--data HOJE]        # o que vence na janela, com semaforo
  fisco.py proximas [--n 5] [--data HOJE]          # as N proximas obrigacoes
  fisco.py concluir --id 3 [--data 20/07/2026]     # marca a competencia atual como cumprida
  fisco.py editar --id 3 [--obrig ..] [--dia ..] [--data ..] [--cat ..] [--obs ..]
  fisco.py remover --id 3
  fisco.py fator-r --receita-anual "R$ 600.000" --folha-anual "R$ 180.000"
  fisco.py comparar --receita-mensal "R$ 50.000" --simples-aliq "11,2%" --presumido-aliq "16,33%"
  fisco.py resumo [--data HOJE]

Datas aceitas: DD/MM/AAAA, DD/MM/AA, DD/MM, AAAA-MM-DD.
Dinheiro aceito: "R$ 1.234,56", "1.234,56", "1500", "1500.00", "R$ 1.890".
Aliquota aceita: "11,2%", "11.2%", "6" (numero puro = por cento).
"""
from __future__ import annotations

import argparse
import calendar
import csv
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


# --------------------------------------------------------------------------- #
# Ancoragem: a pasta .fisco/ mora na RAIZ do projeto do dono, mesmo que o motor
# seja chamado de dentro de .claude/skills/. Sobe a arvore procurando marcadores.
# --------------------------------------------------------------------------- #
def achar_raiz():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    d = os.getcwd()
    while True:
        for marca in (".fisco", ".git", ".claude"):
            if os.path.exists(os.path.join(d, marca)):
                return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return os.getcwd()


RAIZ = achar_raiz()
PASTA = os.path.join(RAIZ, ".fisco")
CONFIG = os.path.join(PASTA, "config.md")
CAL = os.path.join(PASTA, "calendario.csv")

CAL_COLS = ["id", "obrigacao", "categoria", "freq", "dia", "data", "feito_ate", "status", "obs"]
CENT = Decimal("0.01")
Z = Decimal("0.00")
FREQS = ("mensal", "bimestral", "trimestral", "anual", "unico")


# --------------------------------------------------------------------------- #
# Parsers tolerantes (dinheiro, data, porcentagem no padrao brasileiro)
# --------------------------------------------------------------------------- #
def parse_dinheiro(txt) -> Decimal:
    if txt is None:
        raise ValueError("valor vazio")
    if isinstance(txt, (int, float, Decimal)):
        return Decimal(str(txt)).quantize(CENT, ROUND_HALF_UP)
    s = str(txt).strip()
    if not s:
        raise ValueError("valor vazio")
    s = s.replace("R$", "").replace("r$", "").replace(" ", "").replace(" ", "")
    neg = s.startswith("-")
    s = s.lstrip("-+")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        if s.count(".") == 1:
            ip, dp = s.split(".")
            if len(dp) == 3 and len(ip) <= 3:
                s = ip + dp
        elif s.count(".") > 1:
            s = s.replace(".", "")
    try:
        v = Decimal(s).quantize(CENT, ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError(f"nao entendi o valor: {txt!r}")
    return -v if neg else v


def parse_pct(txt) -> Decimal:
    """'11,2%' -> Decimal('0.112'); '6' -> Decimal('0.06'). Numero puro = por cento."""
    if txt is None:
        raise ValueError("aliquota vazia")
    s = str(txt).strip().replace("%", "").replace(" ", "")
    if not s:
        raise ValueError("aliquota vazia")
    s = s.replace(".", "").replace(",", ".") if ("," in s) else s
    try:
        v = Decimal(s)
    except InvalidOperation:
        raise ValueError(f"nao entendi a aliquota: {txt!r}")
    return (v / Decimal("100"))


def parse_data(txt, base: date | None = None) -> date:
    if txt is None:
        raise ValueError("data vazia")
    if isinstance(txt, date):
        return txt
    s = str(txt).strip().lower()
    if not s:
        raise ValueError("data vazia")
    base = base or date.today()
    if s in ("hoje", "today"):
        return base
    if s in ("amanha", "amanhã"):
        return base + timedelta(days=1)
    if s in ("ontem",):
        return base - timedelta(days=1)
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
                dia, mes = int(p[0]), int(p[1])
                return date(base.year, mes, dia)
        except ValueError:
            pass
    raise ValueError(f"nao entendi a data: {txt!r} (use DD/MM/AAAA)")


def fmt_dinheiro(v: Decimal) -> str:
    if not isinstance(v, Decimal):
        v = Decimal(str(v))
    v = v.quantize(CENT, ROUND_HALF_UP)
    neg = v < 0
    n = abs(v)
    inteiro = int(n)
    cents = int((n - inteiro) * 100)
    ints = f"{inteiro:,}".replace(",", ".")
    txt = f"R$ {ints},{cents:02d}"
    return ("-" + txt) if neg else txt


def fmt_pct(frac: Decimal) -> str:
    p = (frac * Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP)
    s = f"{p}".rstrip("0").rstrip(".")
    return f"{s}%".replace(".", ",")


def fmt_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


# --------------------------------------------------------------------------- #
# Config (leitura tolerante a acento: "- **Rotulo:** valor")
# --------------------------------------------------------------------------- #
def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower().strip()


def ler_config() -> dict:
    cfg = {}
    if not os.path.exists(CONFIG):
        return cfg
    try:
        with open(CONFIG, encoding="utf-8") as f:
            for linha in f:
                m = re.match(r"\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)", linha)
                if m:
                    cfg[_sem_acento(m.group(1))] = m.group(2).strip()
    except OSError:
        pass
    return cfg


def cfg_get(cfg: dict, *chaves, padrao=""):
    for c in chaves:
        k = _sem_acento(c)
        if k in cfg and cfg[k]:
            return cfg[k]
    return padrao


# --------------------------------------------------------------------------- #
# Persistencia
# --------------------------------------------------------------------------- #
def garantir_pasta():
    os.makedirs(PASTA, exist_ok=True)


def carregar() -> list[dict]:
    if not os.path.exists(CAL):
        return []
    with open(CAL, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for row in linhas:
        for c in CAL_COLS:
            row.setdefault(c, "")
    return linhas


def salvar(linhas):
    garantir_pasta()
    with open(CAL, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAL_COLS)
        w.writeheader()
        for row in linhas:
            w.writerow({c: row.get(c, "") for c in CAL_COLS})


def proximo_id(linhas) -> int:
    m = 0
    for r in linhas:
        try:
            m = max(m, int(r.get("id") or 0))
        except (ValueError, TypeError):
            pass
    return m + 1


# --------------------------------------------------------------------------- #
# Recorrencia: calcula a ocorrencia anterior e a proxima ao redor de uma data
# --------------------------------------------------------------------------- #
def _ultimo_dia(ano, mes):
    return calendar.monthrange(ano, mes)[1]


def add_meses(d: date, n: int) -> date:
    """Soma n meses a d, ajustando o dia ao ultimo dia do mes quando necessario."""
    mes = d.month - 1 + n
    ano = d.year + mes // 12
    mes = mes % 12 + 1
    dia = min(d.day, _ultimo_dia(ano, mes))
    return date(ano, mes, dia)


def _passo_meses(freq: str) -> int:
    return {"mensal": 1, "bimestral": 2, "trimestral": 3, "anual": 12}.get(freq, 1)


def _ancora(rule: dict, ref: date) -> date:
    """A data-base da recorrencia (fase). Mensal usa --dia; os demais usam --data."""
    freq = rule.get("freq")
    if freq == "mensal":
        try:
            dia = int(rule.get("dia") or 1)
        except (ValueError, TypeError):
            dia = 1
        dia = max(1, min(dia, 28)) if dia > 28 else max(1, dia)
        return date(ref.year, ref.month, min(dia, _ultimo_dia(ref.year, ref.month)))
    # bimestral/trimestral/anual -> ancora na --data informada
    try:
        return parse_data(rule.get("data"), base=ref)
    except ValueError:
        return ref


def bracket(rule: dict, ref: date):
    """Retorna (anterior, proxima): ocorrencias <= ref e >= ref pela recorrencia."""
    freq = rule.get("freq")
    if freq == "unico":
        try:
            d = parse_data(rule.get("data"), base=ref)
        except ValueError:
            return (None, None)
        return (d if d <= ref else None, d if d >= ref else None)
    passo = _passo_meses(freq)
    anc = _ancora(rule, ref)
    # anda em passos ate cercar ref
    cur = anc
    # recua
    guard = 0
    while cur > ref and guard < 600:
        cur = add_meses(cur, -passo)
        guard += 1
    # cur <= ref agora; avanca ate passar de ref
    ant = cur
    prox = cur
    guard = 0
    while prox < ref and guard < 600:
        ant = prox
        prox = add_meses(prox, passo)
        guard += 1
    if prox < ref:
        ant = prox
        prox = add_meses(prox, passo)
    if ant > ref:
        ant = add_meses(ant, -passo)
    return (ant if ant <= ref else None, prox if prox >= ref else add_meses(prox, passo))


def situacao(rule: dict, ref: date):
    """Devolve (vencimento: date|None, situacao: str). situacao em:
    concluida | vencida | hoje | perto | futura | sem_data"""
    freq = rule.get("freq")
    feito = None
    if rule.get("feito_ate"):
        try:
            feito = parse_data(rule["feito_ate"])
        except ValueError:
            feito = None
    if freq == "unico":
        try:
            d = parse_data(rule.get("data"), base=ref)
        except ValueError:
            return (None, "sem_data")
        if rule.get("status") == "concluida":
            return (d, "concluida")
        if d < ref:
            return (d, "vencida")
        if d == ref:
            return (d, "hoje")
        if d <= ref + timedelta(days=7):
            return (d, "perto")
        return (d, "futura")
    ant, prox = bracket(rule, ref)
    # "Vencida" so aparece com EVIDENCIA: o dono ja marcou alguma competencia como
    # cumprida (feito_ate preenchido) e uma competencia posterior venceu sem baixa.
    # Numa obrigacao recem-cadastrada (sem feito_ate) o motor NAO inventa atraso: o
    # calendario comeca olhando pra FRENTE (mostra a proxima ocorrencia), pra nao
    # assustar quem acabou de configurar. Atraso de periodo passado, o dono informa.
    if feito is not None and ant is not None and feito < ant and ant <= ref:
        if ant == ref:
            return (ant, "hoje")
        return (ant, "vencida")
    # sem evidencia de atraso -> mostra a proxima ocorrencia
    d = prox
    if d is None:
        return (None, "sem_data")
    if d == ref:
        return (d, "hoje")
    if d <= ref + timedelta(days=7):
        return (d, "perto")
    return (d, "futura")


ICONE = {"vencida": "🔴", "hoje": "🟠", "perto": "🟡", "futura": "⚪", "concluida": "✅", "sem_data": "⚫"}
ROT_SIT = {"vencida": "VENCIDA", "hoje": "VENCE HOJE", "perto": "vence em breve",
           "futura": "no prazo", "concluida": "cumprida", "sem_data": "sem data"}


# --------------------------------------------------------------------------- #
# Comandos: calendario
# --------------------------------------------------------------------------- #
def cmd_init(args):
    garantir_pasta()
    if not os.path.exists(CAL):
        salvar([])
    print(f"Fisco pronto em {PASTA}")


def cmd_add(args):
    freq = (args.freq or "").lower()
    if freq not in FREQS:
        print(f"Frequencia deve ser uma de: {', '.join(FREQS)}.")
        return
    if freq == "mensal" and not args.dia:
        print("Para freq mensal, informe --dia (ex.: --dia 20).")
        return
    if freq in ("bimestral", "trimestral", "anual", "unico") and not args.data:
        print(f"Para freq {freq}, informe --data (ex.: --data 31/03 ou 15/08/2026).")
        return
    linhas = carregar()
    nid = proximo_id(linhas)
    linhas.append({
        "id": nid, "obrigacao": args.obrig.strip(),
        "categoria": (args.cat or "").strip(), "freq": freq,
        "dia": str(args.dia) if args.dia else "", "data": (args.data or "").strip(),
        "feito_ate": "", "status": "ativa", "obs": (args.obs or "").strip(),
    })
    salvar(linhas)
    venc, sit = situacao(linhas[-1], date.today())
    quando = f"dia {args.dia}" if freq == "mensal" else args.data
    prox = f" (proximo: {fmt_data(venc)})" if venc else ""
    print(f"#{nid} obrigacao cadastrada: {args.obrig} - {freq} ({quando}){prox}")


def _linhas_ativas(linhas):
    return [r for r in linhas if r.get("status") != "removida"]


def cmd_agenda(args):
    hoje = parse_data(args.data) if args.data else date.today()
    dias = args.dias if args.dias is not None else 60
    fim = hoje + timedelta(days=dias)
    linhas = _linhas_ativas(carregar())
    itens = []
    for r in linhas:
        venc, sit = situacao(r, hoje)
        if sit in ("concluida", "sem_data"):
            continue
        if venc and venc <= fim:
            itens.append((venc, sit, r))
    ordem = {"vencida": 0, "hoje": 1, "perto": 2, "futura": 3}
    itens.sort(key=lambda x: (x[0], ordem.get(x[1], 9)))
    print("=" * 56)
    print(f"AGENDA FISCAL  ate {fmt_data(fim)}  (hoje {fmt_data(hoje)})")
    print("=" * 56)
    if not itens:
        print("  Nada nesta janela. Amplie com --dias ou cadastre obrigacoes.")
        return
    for venc, sit, r in itens:
        dif = (venc - hoje).days
        if sit == "vencida":
            quando = f"venceu ha {(hoje - venc).days}d"
        elif sit == "hoje":
            quando = "vence HOJE"
        else:
            quando = f"em {dif}d"
        cat = f" [{r['categoria']}]" if r.get("categoria") else ""
        print(f"  {ICONE[sit]} #{r['id']} {fmt_data(venc)} ({quando}) {r['obrigacao']}{cat}")
    print("-" * 56)
    print("Nao e parecer contabil. Confirme prazos e valores com seu contador.")


def cmd_proximas(args):
    hoje = parse_data(args.data) if args.data else date.today()
    n = args.n if args.n else 5
    linhas = _linhas_ativas(carregar())
    itens = []
    for r in linhas:
        venc, sit = situacao(r, hoje)
        if venc and sit not in ("concluida", "sem_data"):
            itens.append((venc, sit, r))
    itens.sort(key=lambda x: x[0])
    print(f"PROXIMAS {n} OBRIGACOES (hoje {fmt_data(hoje)})")
    if not itens:
        print("  Nenhuma obrigacao ativa cadastrada.")
        return
    for venc, sit, r in itens[:n]:
        cat = f" [{r['categoria']}]" if r.get("categoria") else ""
        print(f"  {ICONE[sit]} #{r['id']} {fmt_data(venc)} {r['obrigacao']}{cat}")
    print("Nao e parecer contabil. Confirme prazos com seu contador.")


def cmd_concluir(args):
    linhas = carregar()
    hoje = parse_data(args.data) if args.data else date.today()
    for r in linhas:
        if str(r.get("id")) == str(args.id):
            venc, sit = situacao(r, hoje)
            if r.get("freq") == "unico":
                r["status"] = "concluida"
                salvar(linhas)
                print(f"#{args.id} '{r['obrigacao']}' marcada como cumprida.")
                return
            # recorrente: avanca feito_ate ate a competencia em aberto (ant<=hoje)
            ant, prox = bracket(r, hoje)
            alvo = ant if ant is not None else venc
            r["feito_ate"] = fmt_data(alvo) if alvo else fmt_data(hoje)
            salvar(linhas)
            # proximo vencimento = a ocorrencia SEGUINTE a competencia concluida
            base_prox = (alvo + timedelta(days=1)) if alvo else hoje
            nv, _ = situacao(r, base_prox)
            prox_txt = f" Proximo vencimento: {fmt_data(nv)}." if nv else ""
            print(f"#{args.id} '{r['obrigacao']}' cumprida na competencia {r['feito_ate']}.{prox_txt}")
            return
    print(f"Nao achei a obrigacao #{args.id}.")


def cmd_editar(args):
    linhas = carregar()
    for r in linhas:
        if str(r.get("id")) == str(args.id):
            if args.obrig:
                r["obrigacao"] = args.obrig.strip()
            if args.dia:
                r["dia"] = str(args.dia)
            if args.data:
                r["data"] = args.data.strip()
            if args.cat is not None:
                r["categoria"] = args.cat.strip()
            if args.obs is not None:
                r["obs"] = args.obs.strip()
            salvar(linhas)
            print(f"#{args.id} atualizada.")
            return
    print(f"Nao achei a obrigacao #{args.id}.")


def cmd_remover(args):
    linhas = carregar()
    for r in linhas:
        if str(r.get("id")) == str(args.id):
            r["status"] = "removida"
            salvar(linhas)
            print(f"#{args.id} removida da agenda.")
            return
    print(f"Nao achei a obrigacao #{args.id}.")


# --------------------------------------------------------------------------- #
# Comandos: fator R (razao pura, sem aliquota)
# --------------------------------------------------------------------------- #
def cmd_fator_r(args):
    receita = parse_dinheiro(args.receita_anual)
    folha = parse_dinheiro(args.folha_anual)
    if receita <= 0:
        print("Informe uma receita anual maior que zero.")
        return
    fr = (folha / receita)
    frp = (fr * Decimal("100")).quantize(Decimal("0.1"), ROUND_HALF_UP)
    print("=" * 56)
    print("FATOR R (razao folha / receita dos ultimos 12 meses)")
    print("=" * 56)
    print(f"  Receita 12m: {fmt_dinheiro(receita)}")
    print(f"  Folha 12m:   {fmt_dinheiro(folha)}  (inclui pro-labore + salarios + encargos)")
    print(f"  Fator R:     {frp}%")
    print("-" * 56)
    if fr >= Decimal("0.28"):
        print("  >> Fator R >= 28%: a atividade TENDE ao Anexo III (aliquotas menores).")
    else:
        falta = ((Decimal("0.28") * receita) - folha).quantize(CENT, ROUND_HALF_UP)
        print("  >> Fator R < 28%: a atividade TENDE ao Anexo V (aliquotas maiores).")
        print(f"     Para cruzar os 28%, a folha 12m precisaria subir ~{fmt_dinheiro(falta)}.")
        print("     Aumentar pro-labore pode compensar OU nao - simule com o contador.")
    print("-" * 56)
    print("Estimativa direcional. Nem toda atividade usa Fator R e a lista de anexos")
    print("muda por CNAE. Confirme o enquadramento com seu contador.")


# --------------------------------------------------------------------------- #
# Comandos: comparar regime (aritmetica sobre aliquotas EFETIVAS informadas)
# --------------------------------------------------------------------------- #
def cmd_comparar(args):
    receita = parse_dinheiro(args.receita_mensal)
    a_s = parse_pct(args.simples_aliq)
    a_p = parse_pct(args.presumido_aliq)
    if receita <= 0:
        print("Informe uma receita mensal maior que zero.")
        return
    imp_s = (receita * a_s).quantize(CENT, ROUND_HALF_UP)
    imp_p = (receita * a_p).quantize(CENT, ROUND_HALF_UP)
    print("=" * 60)
    print("COMPARACAO DIRECIONAL DE REGIME (por mes)")
    print("=" * 60)
    print(f"  Faturamento mensal considerado: {fmt_dinheiro(receita)}")
    print()
    print(f"  Simples Nacional  | aliquota efetiva {fmt_pct(a_s)}  ->  {fmt_dinheiro(imp_s)}/mes")
    print(f"  Lucro Presumido   | carga efetiva    {fmt_pct(a_p)}  ->  {fmt_dinheiro(imp_p)}/mes")
    print("-" * 60)
    dif = (imp_p - imp_s).quantize(CENT, ROUND_HALF_UP)
    if imp_s < imp_p:
        print(f"  >> Pelos numeros informados, o SIMPLES sai {fmt_dinheiro(abs(dif))}/mes mais barato")
        print(f"     ({fmt_dinheiro(abs(dif) * 12)}/ano).")
    elif imp_p < imp_s:
        print(f"  >> Pelos numeros informados, o PRESUMIDO sai {fmt_dinheiro(abs(dif))}/mes mais barato")
        print(f"     ({fmt_dinheiro(abs(dif) * 12)}/ano).")
    else:
        print("  >> Pelos numeros informados, os dois empatam.")
    print("-" * 60)
    print("  ATENCAO: isto e so a aritmetica das aliquotas que VOCE informou.")
    print("  A carga real depende de ISS do seu municipio, Fator R, folha, creditos,")
    print("  atividade (CNAE) e da Reforma Tributaria. NAO e parecer contabil -")
    print("  peca ao seu contador a aliquota efetiva de cada regime e decida com ele.")


# --------------------------------------------------------------------------- #
# Comando: resumo (painel)
# --------------------------------------------------------------------------- #
def cmd_resumo(args):
    hoje = parse_data(args.data) if args.data else date.today()
    cfg = ler_config()
    negocio = cfg_get(cfg, "Negócio", "Negocio", padrao="(negocio nao configurado)")
    regime = cfg_get(cfg, "Regime tributário", "Regime tributario", "Regime", padrao="(nao informado)")
    linhas = _linhas_ativas(carregar())
    venc_ct = hoje_ct = perto_ct = 0
    prox_lista = []
    for r in linhas:
        venc, sit = situacao(r, hoje)
        if sit == "vencida":
            venc_ct += 1
        elif sit == "hoje":
            hoje_ct += 1
        elif sit == "perto":
            perto_ct += 1
        if venc and sit not in ("concluida", "sem_data"):
            prox_lista.append((venc, sit, r))
    prox_lista.sort(key=lambda x: x[0])
    print("=" * 56)
    print("PAINEL DO FISCO")
    print(f"Negocio: {negocio}")
    print(f"Regime:  {regime}")
    print(f"Referencia: {fmt_data(hoje)}")
    print("=" * 56)
    print(f"Obrigacoes ativas: {len(linhas)}")
    print(f"  🔴 vencidas: {venc_ct}   🟠 vencem hoje: {hoje_ct}   🟡 em ate 7 dias: {perto_ct}")
    print()
    print("PROXIMAS OBRIGACOES")
    if not prox_lista:
        print("  Nenhuma obrigacao cadastrada ainda.")
    else:
        for venc, sit, r in prox_lista[:5]:
            cat = f" [{r['categoria']}]" if r.get("categoria") else ""
            print(f"  {ICONE[sit]} #{r['id']} {fmt_data(venc)} {r['obrigacao']}{cat}")
    print("-" * 56)
    if venc_ct:
        print(">> Ha obrigacao VENCIDA. Fale com seu contador antes que vire multa/juros.")
    else:
        print(">> Nenhuma obrigacao vencida no controle. Siga confirmando prazos com o contador.")
    print("Dados 100% locais em .fisco/. Nao e parecer contabil.")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    p = argparse.ArgumentParser(description="Fisco - organizador fiscal + calendario de obrigacoes")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init")

    s = sub.add_parser("add")
    s.add_argument("--obrig", required=True)
    s.add_argument("--freq", required=True)
    s.add_argument("--dia", type=int)
    s.add_argument("--data")
    s.add_argument("--cat")
    s.add_argument("--obs")

    s = sub.add_parser("agenda")
    s.add_argument("--dias", type=int)
    s.add_argument("--data")

    s = sub.add_parser("proximas")
    s.add_argument("--n", type=int)
    s.add_argument("--data")

    s = sub.add_parser("concluir")
    s.add_argument("--id", required=True)
    s.add_argument("--data")

    s = sub.add_parser("editar")
    s.add_argument("--id", required=True)
    s.add_argument("--obrig")
    s.add_argument("--dia", type=int)
    s.add_argument("--data")
    s.add_argument("--cat")
    s.add_argument("--obs")

    s = sub.add_parser("remover")
    s.add_argument("--id", required=True)

    s = sub.add_parser("fator-r")
    s.add_argument("--receita-anual", required=True)
    s.add_argument("--folha-anual", required=True)

    s = sub.add_parser("comparar")
    s.add_argument("--receita-mensal", required=True)
    s.add_argument("--simples-aliq", required=True)
    s.add_argument("--presumido-aliq", required=True)

    s = sub.add_parser("resumo")
    s.add_argument("--data")

    return p


HANDLERS = {
    "init": cmd_init,
    "add": cmd_add,
    "agenda": cmd_agenda,
    "proximas": cmd_proximas,
    "concluir": cmd_concluir,
    "editar": cmd_editar,
    "remover": cmd_remover,
    "fator-r": cmd_fator_r,
    "comparar": cmd_comparar,
    "resumo": cmd_resumo,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.cmd:
        build_parser().print_help()
        return
    try:
        HANDLERS[args.cmd](args)
    except ValueError as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
