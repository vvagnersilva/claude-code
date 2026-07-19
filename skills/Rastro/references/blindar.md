# Blindar — verificar, travar a regressão e limpar

A correção "parece" funcionar. Ainda não acabou. Blindar é o que impede o bug de voltar,
tira o lixo de debug do código e transforma o esforço em memória que economiza tokens no
futuro.

---

## Corrigido × Verificado (não confunda)
Um bug está **Corrigido** quando:
1. o sintoma descrito não acontece mais;
2. o código novo/alterado passa na checagem de tipos/build (o comando do `.rastro/config.md`);
3. os testes relevantes que já existiam passam;
4. existe um teste novo cobrindo o cenário do bug (guarda de regressão);
5. o diário foi atualizado.

Está **Verificado** quando tudo acima é verdade **E** a correção foi confirmada rodando o
app / os testes de verdade — não só por leitura de código. "Achei que funcionou" não é
verificado. Rodou e o sintoma sumiu diante dos seus olhos = verificado.

## A guarda de regressão (o passo que a maioria pula)
Escreva **um teste que FALHA antes da correção e PASSA depois**:
- Ele testa o **cenário da causa-raiz**, não o sintoma superficial.
- Confirme que ele realmente falharia antes: leia a lógica do teste e cheque que ele exercita
  o caminho que quebrava. Um teste escrito só para "passar" depois da correção não pega regressão nenhuma.
- Coloque-o junto dos testes da área afetada.
- **Projeto sem infraestrutura de teste?** Então, no mínimo, deixe registrado no diário o
  passo manual exato para re-verificar (o comando/ação que reproduz e o resultado esperado).

## Limpeza (obrigatória)
1. **Remova toda a instrumentação de debug.** Todo log/print com o marcador `[RASTRO]` sai.
   Nada de `console.log`/`print`/`TODO de debug` esquecido.
2. **Confira o `git diff` final.** Ele só pode conter a correção intencional — nenhuma linha
   de debug, nenhuma "melhoria de passagem", nenhum arquivo mexido sem motivo.
   ```
   git diff        # leia linha por linha; se aparecer algo que não é a correção, tire
   ```
3. **Explique por que funciona.** Em uma frase: "a correção resolve porque [mecanismo]". Se
   você não consegue explicar, você não corrigiu — voltou a chutar; volte à causa-raiz.

## Registrar no diário (fechar o ciclo)
Grave o bug resolvido para que ele **nunca seja re-investigado do zero**:
```
python3 scripts/rastro.py registrar \
  --titulo "Token JWT expira no meio da requisição" \
  --sintoma "API devolve 401 aleatório em requisições longas" \
  --causa "token verificado no início mas expira antes da resposta em chamadas >60s" \
  --correcao "renovar token antes de chamadas longas; TTL revisto" \
  --arquivos "auth/middleware.js,api/client.js" \
  --severidade P1 --status verificado --tags "auth,token,jwt"
```
Na próxima vez que um 401 estranho aparecer, `buscar "401 token"` devolve essa causa-raiz
em segundos — e você não gasta tokens redescobrindo o que já sabia.

## Checagem final de "pronto"
- [ ] Reprodução passa agora.
- [ ] Testes existentes relevantes passam (nada quebrou).
- [ ] Guarda de regressão escrita (falha-antes / passa-depois) — ou passo manual registrado.
- [ ] Toda instrumentação `[RASTRO]` removida; `git diff` só tem a correção.
- [ ] Sei explicar por que funciona.
- [ ] Registrado no diário (status verificado).
