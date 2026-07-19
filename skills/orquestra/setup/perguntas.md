# Roteiro de Setup da Orquestra

O Maestro usa este roteiro para afinar a orquestra na primeira execução. Conduza em PT-BR, uma pergunta de cada vez (use AskUserQuestion). Ao final, grave tudo em `.orquestra/config.md` seguindo `exemplos/config.exemplo.md` e rode `setup/concluir-setup.sh`.

## Perguntas

1. **Nome do negócio** — como o negócio se chama?
2. **Nicho / segmento** — o que vocês fazem? (ex.: agência de tráfego, clínica de fisioterapia, escritório de advocacia, barbearia, consultoria)
3. **Principais serviços** — liste de 2 a 5 serviços que vocês vendem.
4. **Cliente ideal (persona)** — para quem vocês vendem? (ex.: "donos de clínica que querem mais agendamentos")
5. **Tom de voz da marca** — como vocês falam? (ex.: próximo e direto / formal e técnico / descontraído). Se tiver um exemplo de texto de vocês, pode colar.
6. **Cidade / região de atuação** — onde atuam? (importante para SEO local e anúncios)
7. **Chaves de API (opcional)** — o núcleo da Orquestra funciona **sem nenhuma chave**. Só preencha se quiser ativar integrações futuras. Deixe em branco se não tiver. NUNCA invente uma chave.

## Regras do setup
- Apenas o `.orquestra/config.md` guarda essas respostas. Essa pasta é ignorada pelo git.
- Nenhuma chave/segredo vai para qualquer outro arquivo do repositório.
- Depois de gravar o config, rode `bash setup/concluir-setup.sh` para remover os arquivos de instalação.
