# SEO local — para o Google encontrar (e mostrar) o site

Uma página bem feita para negócio local não disputa o Brasil inteiro: disputa "[serviço] em [cidade]". É jogo ganhável. Tudo abaixo entra no `index.html` na hora de montar.

## Cabeça do documento

```html
<!doctype html>
<html lang="pt-BR">
```

- **`<title>`** — fórmula: `[Serviço principal] em [Cidade] | [Nome do negócio]`. Até 60 caracteres, palavra-chave na frente. Ex.: `Encanador 24h em Curitiba | Hidro Silva`.
- **`<meta name="description">`** — 120-155 caracteres, com o diferencial e um convite à ação. Ex.: `Encanador com atendimento no mesmo dia em Curitiba e região. Orçamento grátis pelo WhatsApp, garantia de 90 dias.`
- **`<meta name="viewport" content="width=device-width, initial-scale=1">`** — obrigatório.
- **Favicon embutido** (SVG inline em data URI com a inicial do negócio na cor do acento) — nada de arquivo externo.

## Estrutura de títulos

- **Exatamente um `<h1>`** — a headline do hero, contendo naturalmente o serviço (a palavra-chave). Cidade no H1 ou no subtítulo.
- `<h2>` para cada seção (Serviços, Como funciona, Sobre…), com variações naturais: "Serviços de elétrica em [bairro/cidade]".
- Perguntas do FAQ em `<h3>` — o Google adora pergunta escrita como o cliente pesquisa.

## Open Graph (o cartão bonito no WhatsApp)

Quando o dono mandar o link no WhatsApp, o cartão que aparece é isto:

```html
<meta property="og:title" content="[Título curto e atraente]">
<meta property="og:description" content="[1 frase de benefício]">
<meta property="og:type" content="website">
<!-- og:image só se houver foto real hospedada; sem foto, omitir -->
```

## JSON-LD LocalBusiness (o crachá do negócio para o Google)

Um `<script type="application/ld+json">` antes do `</body>`, **só com dados confirmados** (campo sem dado = campo fora, nunca inventar):

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Nome do negócio]",
  "description": "[1 frase do que faz]",
  "telephone": "+55DDDNUMERO",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Rua, número]",
    "addressLocality": "[Cidade]",
    "addressRegion": "[UF]",
    "addressCountry": "BR"
  },
  "openingHours": ["Mo-Fr 08:00-18:00", "Sa 08:00-12:00"],
  "areaServed": "[Cidade e região]",
  "sameAs": ["https://instagram.com/[perfil real]"]
}
```

Tipos mais específicos quando couber: `Dentist`, `Restaurant`, `HairSalon`, `Plumber`, `Electrician`, `Attorney`, `AccountingService`, `RealEstateAgent` — usar o mais próximo, senão `LocalBusiness` mesmo.

## Depois de publicar — o combo com o Google Meu Negócio

O site sozinho é meio jogo. Orientar o dono:

1. **Perfil da Empresa no Google** (Google Meu Negócio): criar/reivindicar em `google.com/business` — grátis. Colocar o link do site novo no perfil.
2. **Consistência absoluta**: nome, endereço e telefone IGUAIS no site, no perfil do Google e no Instagram. Divergência confunde o Google.
3. **Pedir avaliações**: cliente satisfeito + link direto de avaliação do perfil = o fator local que mais pesa.
4. **Google Search Console** (`search.google.com/search-console`): adicionar o site e pedir indexação da URL — em linguagem simples: "avisar o Google que o site existe".
5. Colocar o link também na bio do Instagram e no status/perfil do WhatsApp Business.

## O que NÃO fazer

- Não entupir o texto de palavra-chave repetida — o Google pune e o cliente foge.
- Não criar página para cidade que o negócio não atende.
- Não prometer posição no Google ("primeiro lugar garantido" não existe).
