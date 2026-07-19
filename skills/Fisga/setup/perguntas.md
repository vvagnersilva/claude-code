# Setup da Fisga — perguntas da primeira execução

O Claude faz estas perguntas UMA vez (uma de cada vez, linguagem simples), depois grava as
respostas em `.fisga/config.md` e remove os arquivos de instalação. Tudo é editável depois.

1. **Seu nome / nome do negócio** — como você assina as mensagens.
2. **O que você vende, em uma frase** — sua oferta principal.
3. **Seu diferencial** — por que escolher você e não o concorrente (em uma frase).
4. **Nicho(s)-alvo** — o ramo/tipo de cliente que você quer atrair (ex.: "clínicas odontológicas",
   "advogados", "lojas de roupa", "restaurantes").
5. **Porte do cliente** — pequeno / médio / grande, ou faturamento aproximado que você atende.
6. **Região** — cidade/estado/país onde você atua (ou "online/Brasil todo").
7. **Ticket médio** — faixa de valor do seu serviço (ajuda a qualificar leads).
8. **Canais preferidos** — por onde você prefere abordar: WhatsApp, Instagram, e-mail, LinkedIn
   (pode ser mais de um; o padrão é WhatsApp).
9. **Tom de voz** — como você fala com cliente: informal / cordial / direto / formal.

Depois de coletar tudo, rode:

```bash
bash setup/concluir-setup.sh \
  --nome "<nome>" --oferta "<oferta>" --diferencial "<diferencial>" \
  --nicho "<nicho>" --porte "<porte>" --regiao "<regiao>" \
  --ticket "<faixa>" --canais "<whatsapp,instagram,...>" --tom "<tom>"
```

O script grava `.fisga/config.md` na raiz do projeto (ignorado pelo git) e se autodestrói.
