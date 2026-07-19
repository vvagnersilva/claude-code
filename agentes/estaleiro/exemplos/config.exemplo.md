# Configuração do Estaleiro (exemplo)

> Este é um EXEMPLO. O setup gera o seu `.estaleiro/config.md` real a partir das suas respostas.
> O arquivo real fica em `.estaleiro/config.md`, é ignorado pelo git e é lido por toda a tripulação antes de trabalhar.

## Projeto
- **Linguagem(ns):** TypeScript (Node 20)
- **Framework / runtime:** Next.js 15 (App Router) + Prisma
- **Gerenciador de pacotes:** pnpm

## Comandos
- **Testes:** `pnpm test`
- **Lint/format:** `pnpm lint && pnpm format`
- **Build/checagem:** `pnpm build`

## Convenções do time
- Sem `default export` — sempre named exports.
- Componentes em PascalCase, hooks em `useCamelCase`.
- Conventional commits (`feat:`, `fix:`, `chore:`).
- Funções puras quando possível; efeitos colaterais isolados.
- Nomes de código em inglês; comentários só quando o porquê não é óbvio.

## Zona proibida (NUNCA tocar)
- `prisma/migrations/` — migrations já aplicadas.
- `src/legacy/` — código antigo em descontinuação.
- Qualquer arquivo `*.generated.ts`.

## Observações
- Banco de testes sobe via `docker compose up -d db-test` antes de `pnpm test`.
- Nada de segredo aqui. Variáveis de ambiente ficam em `.env.local` (fora do git).
