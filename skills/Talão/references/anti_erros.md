# Os erros clássicos de orçamento (e como o Talão protege)

Use isto como checklist mental antes de fechar qualquer orçamento. Cada item é um
tropeço real que faz o prestador perder dinheiro — e como o Talão evita.

1. **Preço de material desatualizado.** O preço de insumo muda toda semana. →
   Pergunte sempre o valor atual; nunca reuse um valor antigo de cabeça. Use a
   **validade** para não ficar preso a um preço velho.

2. **Esquecer o custo indireto.** Telefone, ferramenta, deslocamento médio,
   administração, software, impostos fixos — somados, comem a margem. → Sempre
   aplique o **overhead** (`--overhead`), nem que comece em 10%.

3. **Não cobrar o próprio tempo.** Planejamento, ir comprar material, medir,
   orçar — é tempo de trabalho não pago. → Inclua como `mao_de_obra` ou `custo`. Se
   é recorrente, vire item padrão.

4. **"Metragem × tabela" sem fator de dificuldade.** Dois jobs do mesmo tamanho dão
   trabalho diferente (altura, acesso, acabamento). → Use o **coeficiente**
   (`--coef`) por item para refletir dificuldade e perda de material.

5. **Juntar material e mão de obra num número só.** Vira caixa-preta, impossível de
   ajustar e fácil de o cliente questionar. → Lance cada coisa no seu **tipo**.

6. **Margem aplicada no lugar errado.** Margem é sobre o **custo**, não sobre o
   preço final; e imposto vem **depois** do desconto. → O motor já faz na ordem
   certa; nunca tente "embutir tudo no olho".

7. **Mostrar custo/margem pro cliente.** Quebra a confiança e abre negociação na
   sua margem. → O documento do cliente (`html`) traz só **itens e total**; o
   custo/margem fica no `calcular` (interno).

8. **Orçamento sem validade nem condições.** Sem prazo, o cliente cobra o preço de
   3 meses atrás; sem condição de pagamento, dá confusão na hora de fechar. →
   Sempre defina **validade** e **condições** (parcelas, entrada nas observações).

9. **Sumir depois de enviar.** A maioria das vendas se perde por falta de
   follow-up, não por preço. → Use `pendentes` e a mensagem certa de
   `references/condicoes_e_followup.md`.

10. **Chutar imposto.** Errar a alíquota distorce o preço e pode dar problema
    fiscal. → Use a alíquota que o **contador** do dono confirmar; na dúvida, deixe
    em 0 e avise para confirmar.
