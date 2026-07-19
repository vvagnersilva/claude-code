# Roteiro de Setup do Estaleiro

O Claude usa este roteiro para afinar a tripulação na primeira execução. Conduza em PT-BR, **uma pergunta de cada vez** (use AskUserQuestion). Aceite "não sei / detecta pra mim" em qualquer pergunta — nesse caso, infira lendo os manifests do projeto. Ao final, grave tudo em `.estaleiro/config.md` seguindo `exemplos/config.exemplo.md` e rode `bash setup/concluir-setup.sh`.

## Perguntas

1. **Linguagem(ns) principal(is)** — qual a stack do projeto? (ex.: TypeScript/Node, Python, Go, Ruby, PHP, Java)
2. **Framework / runtime** — qual framework principal? (ex.: Next.js, NestJS, Django, FastAPI, Rails, Laravel, Spring)
3. **Comando de teste** — como roda a suíte de testes? (ex.: `npm test`, `pytest`, `go test ./...`, `bundle exec rspec`). Se não houver testes ainda, diga "não há".
4. **Comando de lint/format** — como formata/linta? (ex.: `npm run lint`, `ruff check .`, `gofmt -w .`, `prettier --write`). Pode deixar em branco.
5. **Convenções do time** — há padrões importantes? (ex.: "sem default export", "commits em conventional commits", "funções puras quando possível", "nomes em inglês"). Cole o que tiver.
6. **Zona proibida** — há arquivos/pastas que a tripulação NUNCA deve tocar? (ex.: `migrations/`, `legacy/`, arquivos gerados, infra de produção)
7. **Gerenciador de pacotes** (opcional) — npm, pnpm, yarn, poetry, uv, etc. Ajuda o Construtor e o Testes a rodarem os comandos certos.

## Regras do setup
- Apenas o `.estaleiro/config.md` guarda essas respostas. Essa pasta é ignorada pelo git.
- **Nenhuma chave/segredo** vai para qualquer arquivo do repositório. O Estaleiro não precisa de credenciais. Se o membro tentar colar uma chave, recuse e oriente a não versionar segredos.
- Não invente valores. Se o membro não souber, detecte pelos manifests (package.json, pyproject.toml, go.mod, Gemfile, composer.json) e confirme.
- Depois de gravar o config, rode `bash setup/concluir-setup.sh` para remover os arquivos de instalação.
