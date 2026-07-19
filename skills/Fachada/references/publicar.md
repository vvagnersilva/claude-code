# Publicar — como colocar o site no ar (sem sofrimento)

O site da Fachada é um único arquivo (`fachada-site/index.html` + a pasta `imagens/`, se houver fotos). Qualquer hospedagem serve. Guie o dono pelo caminho do caso dele — sempre em passos que uma pessoa sem experiência consegue seguir.

## Caminho 1 — Netlify Drop (o mais fácil, grátis, 2 minutos)

Para quem não tem hospedagem nenhuma e quer o site no ar AGORA:

1. Abrir `app.netlify.com/drop` no navegador.
2. Arrastar a **pasta** `fachada-site` inteira (não só o arquivo) para dentro da página.
3. Pronto — o site ganha um endereço tipo `nome-aleatorio.netlify.app`, já com cadeado (HTTPS).
4. Criar conta grátis (pedem e-mail) para o site não expirar e para poder atualizar depois.
5. Para atualizar o site: entrar na conta → Deploys → arrastar a pasta de novo.
6. Renomear o endereço: Site settings → Change site name → algo como `hidrosilva.netlify.app`.

## Caminho 2 — Hospedagem que o dono já tem (cPanel / Hostinger / Locaweb / HostGator)

Para quem já paga hospedagem (geralmente junto com o domínio):

1. Entrar no painel da hospedagem e abrir o **Gerenciador de Arquivos** (File Manager).
2. Navegar até a pasta pública — chama-se `public_html` (às vezes `www`).
3. Enviar o `index.html` e a pasta `imagens/` para lá (botão Upload).
4. Se já existir um `index.html` antigo, renomear o antigo para `index-antigo.html` antes (dá para voltar atrás).
5. Abrir o domínio no navegador e conferir.

## Caminho 3 — GitHub Pages (para quem já usa GitHub)

1. Criar um repositório (ex.: `meu-site`), enviar `index.html` + `imagens/`.
2. Settings → Pages → Branch `main`, pasta `/ (root)` → Save.
3. O site sobe em `usuario.github.io/meu-site` em ~1 minuto.

## Domínio próprio (o endereço com o nome do negócio)

- **`.com.br`** se registra no **registro.br** (~R$ 40/ano). `.com` internacional: Namecheap, Cloudflare, GoDaddy.
- Depois de registrar, apontar o domínio para a hospedagem:
  - **Netlify**: Domain settings → Add custom domain → seguir as instruções (trocar os "servidores DNS" no registro.br pelos que o Netlify mostrar — é copiar e colar dois endereços).
  - **Hospedagem própria**: o domínio comprado junto já vem apontado.
- A propagação leva de minutos a 24h — normal, não é erro.

## Checklist pós-publicação (fazer com o dono)

1. Abrir o site **no celular** (4G, não só Wi-Fi) — tudo aparece? rápido?
2. Tocar no **botão do WhatsApp** — abre a conversa certa, com a mensagem pré-pronta?
3. Tocar no telefone — o celular oferece a ligação?
4. Tocar no endereço — abre o Google Maps no lugar certo?
5. Mandar o link num grupo de WhatsApp — o cartão (título + descrição) aparece bonito?
6. Cadastrar no **Google Search Console** e pedir indexação (ver `seo_local.md`).
7. Atualizar o link na bio do Instagram e no Perfil da Empresa no Google.

## Perguntas que sempre aparecem

- **"Quanto custa manter?"** — Netlify Drop: R$ 0. Domínio próprio: ~R$ 40/ano. Hospedagem paga: R$ 10-30/mês (só se já tiver ou quiser e-mail próprio).
- **"Posso mudar depois?"** — Sempre. O site é um arquivo do dono; a Fachada ajusta e ele re-publica (arrastar a pasta de novo).
- **"E se eu quiser mais páginas?"** — A Fachada é especialista na página única, que resolve 90% dos negócios locais. Crescer para mais páginas é possível: gerar outro HTML e linkar entre eles.
