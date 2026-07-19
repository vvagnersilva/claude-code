#!/usr/bin/env python3
"""Forja - motor deterministico da skill (so biblioteca padrao do Python).

Faz duas coisas chatas e exatas, para o Claude focar na parte humana:

  1) precos  - sugere 3 faixas de preco (basico/intermediario/premium) a partir
               do custo da sua hora, das horas de trabalho e do valor que a
               oferta gera para o cliente. Combina piso (custo), referencia e
               teto (valor) - nunca chuta no escuro.

  2) oferta  - monta uma pagina de oferta (one-pager) em HTML, com a marca do
               usuario (nome, cor, logo), a partir de um arquivo JSON. O HTML e
               autossuficiente (abre em qualquer navegador, vira PDF imprimindo).

Uso:
    python3 scripts/forja.py precos --custo-hora 80 --horas 20 --valor-cliente 8000
    python3 scripts/forja.py precos --custo-hora 80 --horas 20 --valor-cliente 8000 --recorrente
    python3 scripts/forja.py oferta --spec /tmp/oferta.json --saida oferta.html

Nada e enviado para a internet. Tudo roda local.
"""

import argparse
import html
import json
import os
import sys


# ----------------------------------------------------------------------------
# PRECOS
# ----------------------------------------------------------------------------

def calcular_precos(custo_hora, horas, valor_cliente, recorrente=False, margem=2.5):
    """Devolve 3 faixas. Logica simples e defensavel:

    - piso  = custo real do trabalho (custo_hora * horas) - voce nunca cobra abaixo.
    - basico = piso * margem  (margem padrao 2.5x cobre impostos, ferramentas, lucro).
    - premium = ancorado no VALOR para o cliente: ~20% do valor que a oferta gera
                (regra pratica: cobre uma fatia justa do resultado que voce entrega).
    - intermediario = meio do caminho entre basico e premium.

    Se 'recorrente', os numeros sao mensais (mensalidade), e o piso considera as
    horas como horas/mes.
    """
    piso = round(custo_hora * horas, 2)
    basico = round(piso * margem, 2)
    teto_valor = round(valor_cliente * 0.20, 2)  # ~20% do valor gerado
    premium = max(teto_valor, round(basico * 1.8, 2))
    intermediario = round((basico + premium) / 2, 2)

    # garante ordem crescente e que premium > basico
    if premium <= basico:
        premium = round(basico * 1.8, 2)
        intermediario = round((basico + premium) / 2, 2)

    unidade = "/mes" if recorrente else " (projeto)"
    return {
        "piso_custo": piso,
        "recorrente": recorrente,
        "faixas": [
            {"nome": "Basico", "preco": basico, "unidade": unidade,
             "ideia": "Entrada acessivel. Escopo enxuto, o essencial que ja gera resultado."},
            {"nome": "Intermediario", "preco": intermediario, "unidade": unidade,
             "ideia": "O mais vendido. Escopo completo + acompanhamento. Ancore o cliente aqui."},
            {"nome": "Premium", "preco": premium, "unidade": unidade,
             "ideia": "Para quem quer o maximo. Prioridade, mais entregas e proximidade."},
        ],
    }


def imprimir_precos(p):
    print("PISO (custo real do trabalho): R$ %.2f - nunca cobre abaixo disso.\n" % p["piso_custo"])
    tipo = "mensalidade" if p["recorrente"] else "preco de projeto"
    print("Sugestao de 3 faixas (%s):" % tipo)
    for f in p["faixas"]:
        print("  - %-14s R$ %10.2f%s" % (f["nome"], f["preco"], f["unidade"]))
        print("      %s" % f["ideia"])
    print("\nDica: ofereca sempre as 3. A do meio costuma ser a mais escolhida (ancoragem).")
    print("Justifique pelo RESULTADO, nunca pelas horas. Preco e sobre valor, nao sobre esforco.")


# ----------------------------------------------------------------------------
# OFERTA (one-pager HTML)
# ----------------------------------------------------------------------------

def _esc(s):
    return html.escape(str(s)) if s is not None else ""


def montar_html(spec):
    cor = spec.get("cor", "#3b5bdb")
    negocio = spec.get("negocio", "")
    logo = spec.get("logo", "")
    nome_oferta = spec.get("nome_oferta", "Minha Oferta")
    promessa = spec.get("promessa", "")
    para_quem = spec.get("para_quem", "")
    transformacao = spec.get("transformacao", "")
    inclui = spec.get("inclui", []) or []
    nao_inclui = spec.get("nao_inclui", []) or []
    faixas = spec.get("faixas", []) or []
    como_funciona = spec.get("como_funciona", []) or []
    contato = spec.get("contato", "")
    garantia = spec.get("garantia", "")

    logo_html = ('<img src="%s" alt="logo" class="logo">' % _esc(logo)) if logo else (
        '<div class="logo-txt">%s</div>' % _esc(negocio[:2].upper() if negocio else "")
    )

    inclui_html = "".join("<li>%s</li>" % _esc(i) for i in inclui)
    nao_html = "".join("<li>%s</li>" % _esc(i) for i in nao_inclui)

    passos_html = ""
    for n, passo in enumerate(como_funciona, 1):
        passos_html += (
            '<div class="passo"><div class="passo-n">%d</div><div>%s</div></div>'
            % (n, _esc(passo))
        )

    faixas_html = ""
    for i, f in enumerate(faixas):
        destaque = "destaque" if f.get("destaque") else ""
        preco = _esc(f.get("preco", ""))
        faixas_html += (
            '<div class="plano %s">'
            '<div class="plano-nome">%s</div>'
            '<div class="plano-preco">%s</div>'
            '<div class="plano-ideia">%s</div>'
            "</div>"
            % (destaque, _esc(f.get("nome", "")), preco, _esc(f.get("ideia", "")))
        )

    garantia_html = ('<div class="garantia">%s</div>' % _esc(garantia)) if garantia else ""

    return TEMPLATE.format(
        cor=_esc(cor),
        negocio=_esc(negocio),
        logo_html=logo_html,
        nome_oferta=_esc(nome_oferta),
        promessa=_esc(promessa),
        para_quem=_esc(para_quem),
        transformacao=_esc(transformacao),
        inclui_html=inclui_html,
        nao_html=nao_html,
        passos_html=passos_html,
        faixas_html=faixas_html,
        garantia_html=garantia_html,
        contato=_esc(contato),
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{nome_oferta}</title>
<style>
  :root {{ --cor: {cor}; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          color: #1f2330; background: #f4f5f8; line-height: 1.55; padding: 32px 16px; }}
  .pagina {{ max-width: 820px; margin: 0 auto; background: #fff; border-radius: 18px;
             overflow: hidden; box-shadow: 0 18px 50px rgba(20,25,45,.10); }}
  .topo {{ background: linear-gradient(135deg, var(--cor), color-mix(in srgb, var(--cor) 70%, #000));
           color: #fff; padding: 40px 44px; }}
  .marca {{ display: flex; align-items: center; gap: 14px; margin-bottom: 26px; opacity: .95; }}
  .logo {{ height: 46px; width: auto; border-radius: 8px; background: #fff; padding: 4px; }}
  .logo-txt {{ height: 46px; width: 46px; border-radius: 10px; background: rgba(255,255,255,.18);
               display: flex; align-items: center; justify-content: center; font-weight: 800; }}
  .marca-nome {{ font-weight: 600; font-size: 1.05rem; }}
  .topo h1 {{ font-size: 2.1rem; line-height: 1.15; margin-bottom: 12px; font-weight: 800; }}
  .promessa {{ font-size: 1.18rem; opacity: .96; max-width: 60ch; }}
  .corpo {{ padding: 36px 44px; }}
  .bloco {{ margin-bottom: 30px; }}
  .rotulo {{ text-transform: uppercase; letter-spacing: .08em; font-size: .74rem;
             font-weight: 700; color: var(--cor); margin-bottom: 8px; }}
  .bloco p {{ font-size: 1.02rem; color: #353a4a; }}
  .duas {{ display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }}
  ul {{ list-style: none; }}
  .inclui li, .nao li {{ padding: 6px 0 6px 26px; position: relative; font-size: .98rem; }}
  .inclui li::before {{ content: "\\2713"; position: absolute; left: 0; color: var(--cor); font-weight: 800; }}
  .nao li::before {{ content: "\\2715"; position: absolute; left: 0; color: #b9bdc9; font-weight: 800; }}
  .nao li {{ color: #6b7080; }}
  .passos {{ display: flex; flex-direction: column; gap: 12px; }}
  .passo {{ display: flex; align-items: flex-start; gap: 14px; font-size: 1rem; }}
  .passo-n {{ flex: 0 0 30px; height: 30px; border-radius: 50%; background: var(--cor);
              color: #fff; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
  .planos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }}
  .plano {{ border: 2px solid #e7e9f0; border-radius: 14px; padding: 22px 18px; text-align: center; }}
  .plano.destaque {{ border-color: var(--cor); box-shadow: 0 10px 26px color-mix(in srgb, var(--cor) 22%, transparent); }}
  .plano-nome {{ font-weight: 700; color: var(--cor); margin-bottom: 8px; }}
  .plano-preco {{ font-size: 1.5rem; font-weight: 800; margin-bottom: 8px; }}
  .plano-ideia {{ font-size: .9rem; color: #5a6072; }}
  .garantia {{ margin-top: 22px; padding: 16px 20px; background: color-mix(in srgb, var(--cor) 8%, #fff);
               border-radius: 12px; font-size: .98rem; color: #353a4a; }}
  .rodape {{ padding: 26px 44px 38px; border-top: 1px solid #eef0f5; text-align: center; }}
  .cta {{ display: inline-block; background: var(--cor); color: #fff; font-weight: 700;
          padding: 14px 30px; border-radius: 999px; text-decoration: none; font-size: 1.05rem; }}
  @media (max-width: 600px) {{ .duas {{ grid-template-columns: 1fr; }} .topo, .corpo, .rodape {{ padding-left: 24px; padding-right: 24px; }} }}
  @media print {{ body {{ background: #fff; padding: 0; }} .pagina {{ box-shadow: none; border-radius: 0; }} }}
</style>
</head>
<body>
  <div class="pagina">
    <div class="topo">
      <div class="marca">{logo_html}<span class="marca-nome">{negocio}</span></div>
      <h1>{nome_oferta}</h1>
      <p class="promessa">{promessa}</p>
    </div>
    <div class="corpo">
      <div class="bloco"><div class="rotulo">Para quem e</div><p>{para_quem}</p></div>
      <div class="bloco"><div class="rotulo">O que muda na sua vida</div><p>{transformacao}</p></div>
      <div class="bloco duas">
        <div><div class="rotulo">O que esta incluido</div><ul class="inclui">{inclui_html}</ul></div>
        <div><div class="rotulo">O que NAO esta incluido</div><ul class="nao">{nao_html}</ul></div>
      </div>
      <div class="bloco"><div class="rotulo">Como funciona</div><div class="passos">{passos_html}</div></div>
      <div class="bloco"><div class="rotulo">Investimento</div><div class="planos">{faixas_html}</div>{garantia_html}</div>
    </div>
    <div class="rodape"><a class="cta" href="#">{contato}</a></div>
  </div>
</body>
</html>
"""


def cmd_precos(args):
    p = calcular_precos(args.custo_hora, args.horas, args.valor_cliente,
                        recorrente=args.recorrente, margem=args.margem)
    if args.json:
        print(json.dumps(p, ensure_ascii=False, indent=2))
    else:
        imprimir_precos(p)


def cmd_oferta(args):
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    html_str = montar_html(spec)
    with open(args.saida, "w", encoding="utf-8") as f:
        f.write(html_str)
    print("Pagina de oferta gerada: %s" % os.path.abspath(args.saida))
    print("Abra no navegador. Para virar PDF: abrir e imprimir > salvar como PDF.")


def main():
    ap = argparse.ArgumentParser(description="Forja - motor da skill (precos e pagina de oferta).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("precos", help="sugere 3 faixas de preco")
    pp.add_argument("--custo-hora", type=float, required=True, help="quanto vale sua hora (R$)")
    pp.add_argument("--horas", type=float, required=True, help="horas de trabalho (ou horas/mes se recorrente)")
    pp.add_argument("--valor-cliente", type=float, required=True, help="valor que a oferta gera para o cliente (R$)")
    pp.add_argument("--recorrente", action="store_true", help="precos mensais em vez de projeto unico")
    pp.add_argument("--margem", type=float, default=2.5, help="multiplicador sobre o custo (padrao 2.5)")
    pp.add_argument("--json", action="store_true", help="saida em JSON")
    pp.set_defaults(func=cmd_precos)

    po = sub.add_parser("oferta", help="gera a pagina de oferta (one-pager HTML)")
    po.add_argument("--spec", required=True, help="arquivo JSON com os dados da oferta")
    po.add_argument("--saida", default="oferta.html", help="arquivo HTML de saida")
    po.set_defaults(func=cmd_oferta)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
