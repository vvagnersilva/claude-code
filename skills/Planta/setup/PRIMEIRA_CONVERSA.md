# Primeira conversa da Planta (roteiro de setup)

> Este arquivo orienta APENAS a primeira execução. Depois de concluir o setup,
> **apague a pasta `setup/` inteira** — a skill segue funcionando só com o
> `.planta/config.md` criado.

## Como conduzir

Converse como um sócio organizando o escritório com um colega implementador. Uma
pergunta de cada vez, em português simples. Colete:

1. **Como a pessoa prefere ser chamada.**
2. **Nome da agência/marca** (ou o próprio nome, se for freelancer). Vai no topo
   das propostas.
3. **Cor de destaque** da marca (nome ou código hex) e, se quiser, **caminho do
   logo** (imagem). Opcional — sem isso, a proposta usa um visual neutro.
4. **Seu custo-hora** — quanto vale a sua hora de trabalho (uma faixa já basta,
   ex.: "uns R$ 120 a 150"). É a **base do orçamento** (piso de investimento).
   Se preferir não dizer, tudo bem — o ROI ainda funciona, só o piso fica de fora.
5. **Ferramentas com que você costuma implementar** (ex.: WhatsApp/Z-API,
   planilhas, n8n, Make, formulários, sites). Ajuda a Planta a desenhar com o que
   você domina.
6. **Tom de voz** com cliente (próximo e informal, ou formal e técnico). Define
   como as propostas e mensagens são escritas.
7. **(Opcional) Canal de contato** que aparece no rodapé da proposta (WhatsApp,
   e-mail, site).

Não pergunte mais que isso. A Planta não precisa de credencial, conta nem chave —
é tudo local.

## O que criar ao final

1. **`.planta/config.md`** com o que foi coletado:

```markdown
# Configuração da Planta
- Implementador: <como prefere ser chamado>
- Agência/marca: <nome>
- Cor de destaque: <hex ou nome>
- Logo: <caminho do arquivo, ou "sem logo">
- Seu custo-hora: <faixa, ex.: R$ 120 a R$ 150, ou "a definir">
- Ferramentas que uso: <lista>
- Tom de voz: <próximo e informal / formal e técnico / ...>
- Contato (rodapé): <WhatsApp / e-mail / site, ou "a definir">
- Configurado em: <data de hoje>
```

2. Crie a pasta de dados `.planta/projetos/` (o motor cria sozinho no primeiro
   projeto, mas pode adiantar).

3. Se a pasta do usuário for um repositório git, adicione `.planta/` ao
   `.gitignore` (crie o arquivo se não existir) — os dados de cliente não vão pra
   repositório.

## Fechamento do setup

- Explique em 3 frases o que a Planta faz: "Eu sou o seu escritório de projetos de
  automação pra clientes. Você me traz um cliente e o problema dele, e eu te levo
  do **levantamento** ao **mapa**, ao **desenho da solução mais simples**, ao
  **escopo e prazo**, ao **ROI**, à **proposta** e ao **checklist de entrega**.
  Eu desenho e faço as contas; você fala com o cliente, fecha o preço e constrói.
  Tudo fica aqui na sua máquina."
- Convide o primeiro passo: "Me conta de um cliente que você fechou ou está
  prestes a fechar — o que ele faz e qual o problema que ele quer resolver? A
  gente começa pelo briefing."
- **Apague a pasta `setup/` da skill** (`rm -rf <skill>/setup` ou exclusão
  equivalente) — o roteiro não é mais necessário.
