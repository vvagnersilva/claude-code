# Proposta comercial — estrutura e one-pager em HTML

Use no modo **Proposta**, só depois de Briefing + Mapear + Escopo + ROI. A
proposta é escrita **na língua do cliente** (sem jargão técnico), com a marca do
usuário, e **trava o escopo** (dentro × fora). Tudo que for suposição vai marcado
**[CONFIRMAR]**.

## Estrutura (nesta ordem)
1. **Cabeçalho** — logo/nome da agência, nome do cliente, data.
2. **O problema** — 2-3 frases que mostram que você entendeu a dor (do briefing).
   Tem que fazer o cliente assentir com a cabeça.
3. **O resultado (output + ganho)** — o que muda na prática + o **número** ("de X
   para Y") + o **ROI** (economia por mês/ano vindos do modo ROI). Esta é a parte
   que vende.
4. **A solução, em linguagem simples** — o que será feito, passo a passo, sem
   nomes técnicos. O que fica automático e o que continua com a equipe.
5. **O que está incluído (DENTRO)** — lista clara dos itens do escopo.
6. **O que NÃO está incluído (FORA)** — igualmente claro. Protege contra "mais uma
   coisinha". Diga que itens fora viram um adendo à parte.
7. **Fases e prazo** — as fases do escopo e o prazo estimado (do motor). Deixe a
   condição: prazo conta a partir da entrega de acessos/dados pelo cliente.
8. **Investimento** — o valor (você define, com base no piso + valor entregue) e,
   quando fizer sentido, o modelo **projeto único + mensalidade** (recorrência:
   manutenção e melhoria contínua). Nunca um "preço mágico" — ancore no ganho.
9. **Próximo passo** — uma ação única e clara ("para começar, basta aprovar por
   aqui e enviar os acessos da lista abaixo").
10. **O que precisamos de você** — acessos, dados, aprovações que destravam o início.

## Regras de escrita
- Língua do cliente, frases curtas, zero jargão ("discovery", "deliverable", "n8n"
  só se o cliente já fala isso).
- Ancore o preço no **ganho**, não no esforço. O cliente compra o resultado.
- Toda suposição = **[CONFIRMAR]** visível. Se houver 3+ suposições de negócio,
  abra um quadro "Pontos a confirmar antes de começar" no topo.
- Honestidade: prazo e número são estimativas ("deve ficar perto de").

## One-pager em HTML (gerar e salvar)
Gere **um único arquivo HTML autossuficiente** (sem dependência externa, vira PDF
imprimindo) e salve em `.planta/propostas/<slug>-proposta.html`.

Diretrizes visuais:
- Use a **cor de destaque** e o **nome/logo** do `config.md` (logo embutido como
  data URI, se houver). Fundo claro, muito espaço em branco, uma cor de destaque só.
- Tipografia limpa e legível; títulos claros; o **resultado/ROI** em destaque
  (um bloco/card com o número grande).
- Tabela simples para "Dentro × Fora" e para "Fases/Prazo".
- Rodapé com nome da agência + contato.
- Cabe em 1-2 páginas A4 ao imprimir. Sem imagens pesadas, sem script.

Esqueleto sugerido (adapte ao conteúdo real do projeto — nunca deixe placeholder
solto na versão entregue ao cliente; use [CONFIRMAR] só para suposições reais):

```html
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Proposta — {cliente}</title>
<style>
  :root{ --accent:{cor_destaque}; --ink:#1a1a1a; --muted:#6b6b6b; --line:#e6e3dc; }
  *{box-sizing:border-box} body{font-family:Georgia,'Times New Roman',serif;
    color:var(--ink);background:#fff;margin:0;padding:32px;line-height:1.6;font-size:13px}
  .wrap{max-width:660px;margin:0 auto}
  header{display:flex;justify-content:space-between;align-items:center;
    border-bottom:3px solid var(--accent);padding-bottom:12px;margin-bottom:20px}
  h1{font-size:24px;margin:.2em 0} h2{color:var(--accent);font-size:15px;
    margin-top:22px;border-bottom:1px solid var(--line);padding-bottom:4px}
  .ganho{background:#faf8f3;border:1px solid var(--line);border-left:4px solid var(--accent);
    padding:14px 18px;border-radius:6px;margin:14px 0}
  .ganho .num{font-size:22px;color:var(--accent);font-weight:bold}
  table{width:100%;border-collapse:collapse;margin:8px 0} td,th{border:1px solid var(--line);
    padding:7px 10px;text-align:left;vertical-align:top} th{background:#faf8f3}
  .cta{background:var(--accent);color:#fff;padding:12px 16px;border-radius:6px;margin-top:18px}
  footer{margin-top:26px;color:var(--muted);font-size:11px;border-top:1px solid var(--line);padding-top:10px}
  @media print{body{padding:0}}
</style></head><body><div class="wrap">
  <header><div><strong>{agencia}</strong></div><div>{data}</div></header>
  <h1>Proposta para {cliente}</h1>
  <h2>O desafio</h2><p>{problema}</p>
  <h2>O resultado</h2>
  <div class="ganho"><div class="num">{de X → para Y}</div>
    <div>Economia estimada: {ROI/mês} · {ROI/ano}</div></div>
  <h2>Como vamos resolver</h2><p>{solução em linguagem simples}</p>
  <h2>O que está incluído × o que não está</h2>
  <table><tr><th>Incluído</th><th>Não incluído (vira adendo)</th></tr>
    <tr><td>{lista dentro}</td><td>{lista fora}</td></tr></table>
  <h2>Fases e prazo</h2><table><tr><th>Fase</th><th>Entrega</th><th>Prazo</th></tr>
    {linhas de fase}</table>
  <h2>Investimento</h2><p>{valor / modelo projeto + mensalidade}</p>
  <div class="cta"><strong>Próximo passo:</strong> {ação única}</div>
  <footer>{agencia} · {contato}</footer>
</div></body></html>
```
