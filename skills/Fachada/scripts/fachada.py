#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fachada — motor de vistoria do site (100% biblioteca padrão).

Uso:
    python3 scripts/fachada.py checar fachada-site/index.html
    python3 scripts/fachada.py contraste "#1A1A1A" "#F5F0E8"

`checar` confere os itens técnicos essenciais de um site de uma página e
imprime um relatório em português com ✅/⚠️/❌. Sai com código 1 se houver ❌.
`contraste` calcula a razão de contraste WCAG entre duas cores hex.
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

# ---------------------------------------------------------------- coleta ----

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿←-⇿⬀-⯿️]"
)

PLACEHOLDERS = [
    "lorem", "ipsum", "placeholder", "seu texto", "seu titulo", "seu título",
    "todo:", "xxx", "exemplo.com", "example.com", "[nome", "[cidade",
    "insira aqui", "texto aqui",
]

FONTES_PERMITIDAS = ("fonts.googleapis.com", "fonts.gstatic.com")


class Coletor(HTMLParser):
    """Percorre o HTML e junta tudo que a vistoria precisa."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ""
        self.metas = {}          # name/property -> content
        self.h1 = []             # textos dos h1
        self.headings = []       # (tag, texto) de h1-h3
        self.imgs = []           # (src, alt ou None)
        self.links = []          # hrefs de <a>
        self.scripts_ext = []    # src de <script src=...>
        self.css_ext = []        # href de <link rel=stylesheet>
        self.jsonld = []         # conteúdo de <script type=application/ld+json>
        self.botoes = []         # textos de <button> e <a class*=btn>
        self.viewport = False
        self.favicon = False
        self._pilha = []         # tag atual para captura de texto
        self._buf = ""
        self._em_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        elif tag == "title":
            self._pilha.append("title")
            self._buf = ""
        elif tag == "meta":
            chave = a.get("name") or a.get("property")
            if chave:
                self.metas[chave.lower()] = a.get("content", "")
            if (a.get("name") or "").lower() == "viewport":
                self.viewport = True
        elif tag in ("h1", "h2", "h3"):
            self._pilha.append(tag)
            self._buf = ""
        elif tag == "img":
            self.imgs.append((a.get("src", ""), a.get("alt")))
        elif tag == "a":
            self.links.append(a.get("href", ""))
            cls = a.get("class", "")
            if "btn" in cls or "button" in cls or "cta" in cls:
                self._pilha.append("botao")
                self._buf = ""
        elif tag == "button":
            self._pilha.append("botao")
            self._buf = ""
        elif tag == "script":
            if a.get("src"):
                self.scripts_ext.append(a["src"])
            if (a.get("type") or "").lower() == "application/ld+json":
                self._em_jsonld = True
                self._buf = ""
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if "stylesheet" in rel and a.get("href", "").startswith("http"):
                self.css_ext.append(a["href"])
            if "icon" in rel:
                self.favicon = True

    def handle_endtag(self, tag):
        if self._em_jsonld and tag == "script":
            self.jsonld.append(self._buf)
            self._em_jsonld = False
            self._buf = ""
            return
        if not self._pilha:
            return
        atual = self._pilha[-1]
        if (tag == atual) or (tag in ("a", "button") and atual == "botao") or (
            tag == "title" and atual == "title"
        ):
            texto = re.sub(r"\s+", " ", self._buf).strip()
            self._pilha.pop()
            if atual == "title":
                self.title = texto
            elif atual in ("h1", "h2", "h3"):
                self.headings.append((atual, texto))
                if atual == "h1":
                    self.h1.append(texto)
            elif atual == "botao":
                self.botoes.append(texto)
            self._buf = ""

    def handle_data(self, data):
        if self._pilha or self._em_jsonld:
            self._buf += data


# --------------------------------------------------------------- vistoria ---

def checar(caminho):
    if not os.path.isfile(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return 1

    with open(caminho, encoding="utf-8", errors="replace") as f:
        html = f.read()

    c = Coletor()
    c.feed(html)

    ok, avisos, erros = [], [], []

    def certo(msg):
        ok.append("✅ " + msg)

    def aviso(msg):
        avisos.append("⚠️  " + msg)

    def erro(msg):
        erros.append("❌ " + msg)

    # --- idioma
    if c.lang and c.lang.lower().startswith("pt"):
        certo(f'Idioma declarado ({c.lang})')
    else:
        erro('Falta lang="pt-BR" na tag <html>')

    # --- title
    if not c.title:
        erro("Sem <title> — o Google e a aba do navegador ficam vazios")
    elif len(c.title) > 60:
        aviso(f"<title> com {len(c.title)} caracteres (ideal até 60): “{c.title[:70]}”")
    elif len(c.title) < 15:
        aviso(f"<title> muito curto ({len(c.title)} caracteres) — cabe serviço + cidade + nome")
    else:
        certo(f"<title> ok ({len(c.title)} caracteres)")

    # --- meta description
    desc = c.metas.get("description", "")
    if not desc:
        erro("Sem <meta name=\"description\"> — é o texto que aparece no Google")
    elif not 50 <= len(desc) <= 160:
        aviso(f"Meta description com {len(desc)} caracteres (ideal 120-155)")
    else:
        certo(f"Meta description ok ({len(desc)} caracteres)")

    # --- viewport
    if c.viewport:
        certo("Viewport configurado (site responsivo no celular)")
    else:
        erro("Sem meta viewport — o site vai abrir minúsculo no celular")

    # --- H1
    if len(c.h1) == 1:
        certo(f"Um único H1: “{c.h1[0][:60]}”")
    elif not c.h1:
        erro("Nenhum H1 — a página precisa de um título principal")
    else:
        erro(f"{len(c.h1)} H1 na página — deve haver exatamente um")

    # --- imagens
    sem_alt = [s for s, alt in c.imgs if alt is None or alt == ""]
    if not c.imgs:
        certo("Sem imagens (design tipográfico) — nada a conferir de alt")
    elif sem_alt:
        erro(f"{len(sem_alt)} imagem(ns) sem texto alternativo (alt): {', '.join(sem_alt[:3])}")
    elif len(c.imgs) == 1:
        certo("A única imagem tem alt")
    else:
        certo(f"Todas as {len(c.imgs)} imagens têm alt")

    # --- contato
    tem_wa = any("wa.me" in h or "api.whatsapp.com" in h for h in c.links)
    tem_tel = any(h.startswith("tel:") for h in c.links)
    if tem_wa:
        certo("Link de WhatsApp presente")
    else:
        erro("Nenhum link de WhatsApp (wa.me) — é o caminho principal de contato")
    if tem_tel:
        certo("Telefone clicável (tel:) presente")
    else:
        aviso("Sem link tel: — se o negócio tem telefone, deixe clicável")

    # --- links placeholder
    quebrados = [h for h in c.links if h in ("#", "", "javascript:void(0)")]
    if quebrados:
        aviso(f"{len(quebrados)} link(s) sem destino (href=\"#\") — preencher ou remover")
    else:
        certo("Nenhum link vazio")

    # --- JSON-LD
    achou_lb = False
    for bloco in c.jsonld:
        try:
            dados = json.loads(bloco)
            tipos = json.dumps(dados)
            if "LocalBusiness" in tipos or '"@type"' in tipos:
                achou_lb = True
        except (ValueError, TypeError):
            erro("Bloco JSON-LD com JSON inválido — corrigir a sintaxe")
    if achou_lb:
        certo("Dados estruturados (JSON-LD) presentes")
    elif not c.jsonld:
        aviso("Sem JSON-LD LocalBusiness — recomendado para SEO local (ver seo_local.md)")

    # --- OG
    if c.metas.get("og:title") and c.metas.get("og:description"):
        certo("Open Graph ok (cartão bonito no WhatsApp)")
    else:
        aviso("Faltam og:title/og:description — o link fica sem cartão no WhatsApp")

    # --- favicon
    if c.favicon:
        certo("Favicon presente")
    else:
        aviso("Sem favicon — a aba do navegador fica com ícone genérico")

    # --- placeholders esquecidos
    texto_plano = re.sub(r"<[^>]+>", " ", html).lower()
    achados = sorted({p for p in PLACEHOLDERS if p in texto_plano})
    if achados:
        erro(f"Texto de rascunho esquecido no site: {', '.join(achados)}")
    else:
        certo("Nenhum texto de rascunho/placeholder")

    # --- emoji em interface
    com_emoji = [t for _, t in c.headings if EMOJI_RE.search(t)]
    com_emoji += [t for t in c.botoes if EMOJI_RE.search(t)]
    if com_emoji:
        erro(f"Emoji em título/botão (cara de IA): “{com_emoji[0][:50]}”")
    else:
        certo("Sem emoji em títulos e botões")

    # --- recursos externos
    ruins_js = [s for s in c.scripts_ext if s.startswith("http")]
    if ruins_js:
        aviso(f"Script(s) externo(s): {', '.join(ruins_js[:3])} — o site deve ser autossuficiente")
    else:
        certo("Nenhum script externo")
    css_ruim = [h for h in c.css_ext if not any(d in h for d in FONTES_PERMITIDAS)]
    if css_ruim:
        aviso(f"CSS externo além do Google Fonts: {', '.join(css_ruim[:3])}")
    else:
        certo("CSS externo só do Google Fonts (ou nenhum)")

    # --- peso
    kb = os.path.getsize(caminho) / 1024
    if kb > 1500:
        aviso(f"Arquivo com {kb:.0f} KB — fotos devem ficar na pasta imagens/, não embutidas")
    else:
        certo(f"Peso do arquivo ok ({kb:.0f} KB)")

    # --- relatório
    print("\n═══ VISTORIA DA FACHADA ═══\n")
    for linha in erros + avisos + ok:
        print(linha)
    print(f"\nResumo: {len(erros)} erro(s) · {len(avisos)} aviso(s) · {len(ok)} ok")
    if erros:
        print("Corrija os ❌ antes de publicar.")
        return 1
    if avisos:
        print("Site publicável — avalie os ⚠️ acima.")
    else:
        print("Vistoria limpa. Pronto para publicar.")
    return 0


# --------------------------------------------------------------- contraste --

def _luminancia(hexcor):
    h = hexcor.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in h):
        raise ValueError(f"Cor inválida: {hexcor} (use o formato #RRGGBB)")
    canais = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        canais.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    r, g, b = canais
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(cor1, cor2):
    try:
        l1, l2 = _luminancia(cor1), _luminancia(cor2)
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    razao = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
    print(f"\nContraste entre {cor1} e {cor2}: {razao:.2f}:1\n")
    print(f"  Texto corrido (mínimo 4.5:1): {'✅ passa' if razao >= 4.5 else '❌ não passa'}")
    print(f"  Título grande (mínimo 3.0:1): {'✅ passa' if razao >= 3.0 else '❌ não passa'}")
    print(f"  Conforto máximo (7.0:1):      {'✅ passa' if razao >= 7.0 else '— abaixo (ok se AA passou)'}")
    return 0 if razao >= 3.0 else 1


# ------------------------------------------------------------------- main ---

def main(argv):
    if len(argv) >= 3 and argv[1] == "checar":
        return checar(argv[2])
    if len(argv) >= 4 and argv[1] == "contraste":
        return contraste(argv[2], argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
