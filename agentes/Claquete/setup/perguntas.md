# Roteiro de Setup da Claquete

O Claude usa este roteiro para afinar a equipe na primeira execução. Conduza em PT-BR, **uma pergunta de cada vez** (use AskUserQuestion). Aceite "não sei / decide pra mim" em qualquer pergunta — nesse caso, sugira uma opção sensata e siga. Ao final, grave tudo em `.claquete/config.md` seguindo `exemplos/config.exemplo.md` e rode `bash setup/concluir-setup.sh`.

## Perguntas

1. **Nome do canal** — como o canal se chama (ou vai se chamar)?
2. **Nicho / tema** — sobre o que o canal fala? Quanto mais específico, melhor. (ex.: "receitas de marmita fitness", "como abrir MEI", "review de ferramenta de IA para advogados")
3. **Objetivo do canal** — o que esse canal precisa gerar? (ex.: só views/inscritos, leads para um serviço, vendas de um produto, autoridade na área)
4. **Para quem é** — quem é o público? Idade, momento de vida, e qual a **dor principal** que ele tem.
5. **Voz do canal** — qual o tom? (ex.: direto e animado, calmo e didático, técnico e sério) Tem bordão ou jeito de falar? Como costuma abrir e fechar os vídeos?
6. **Formato principal** — vídeo longo (8–15 min), Shorts/Reels (até 60s) ou os dois? Se os dois, qual é o carro-chefe?
7. **Frequência desejada** — quantos vídeos por semana/mês você consegue manter de verdade?
8. **Limites (o que NUNCA fazer)** — alguma promessa que o canal não pode fazer, tema proibido, ou regra do seu mercado? (ex.: nada de promessa de saúde/financeira, nada de clickbait mentiroso)

## Regras do setup
- Apenas o `.claquete/config.md` guarda essas respostas. Essa pasta é ignorada pelo git.
- **Nenhuma chave/segredo** vai para qualquer arquivo do repositório. A Claquete não precisa de credenciais — ela trabalha em texto e quem grava/edita/publica é o dono. Se o membro tentar colar uma chave, recuse e oriente a não versionar segredos.
- Não invente valores. Se o membro não souber, sugira uma opção comum para o nicho dele e confirme.
- Depois de gravar o config, rode `bash setup/concluir-setup.sh` para remover os arquivos de instalação.
