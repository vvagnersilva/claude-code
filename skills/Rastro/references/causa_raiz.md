# Causa-raiz — cavar até a origem

Achar o **porquê**, não só o **quê**. Consertar o sintoma é o que faz o bug voltar
disfarçado e o loop recomeçar. Aqui estão as quatro ferramentas.

---

## 1. Os 5 porquês
Pergunte "por quê?" repetidamente até chegar a uma causa que não dá pra quebrar mais.
Exemplo real:
```
Problema: a API devolve timeout 524
  Por quê? → o Cloudflare corta conexões que passam de 100s
  Por quê? → a chamada da API demora mais de 100s
  Por quê? → a requisição não é streaming; o servidor segura a conexão calado
  Por quê? → o código usa fetch comum, não streaming
  Causa-raiz → usar a API em streaming (o servidor manda dado continuamente; o Cloudflare não corta)

  ❌ ERRADO: trocar por um modelo mais rápido (paliativo — evita o timeout, não resolve)
  ✅ CERTO:  usar streaming (ataca a causa: o Cloudflare precisa de dado contínuo)
```

## 2. O Portão da Causa-Raiz
Antes de propor QUALQUER correção, passe por este portão:
1. Qual é o problema REAL?
2. POR QUE ele acontece? (não só o quê)
3. Minha correção elimina o PORQUÊ?
   - Sim → siga.
   - Não → é um paliativo → PARE.

**O teste do paliativo:** "Se eu remover minha correção, o bug volta?"
- Volta → era paliativo (conserte a causa em vez disso).
- Não volta → correção real. ✅

### Armadilhas de paliativo (o contorno × a correção real)
| Problema | Paliativo (❌) | Correção de causa-raiz (✅) |
|---|---|---|
| Timeout de API | Trocar por modelo mais rápido | Usar streaming / consertar a query lenta |
| Perda de precisão de número | Buscar por nome em vez de ID | Consertar o parse do número grande |
| Busca não retorna nada | Tentar outra estratégia de busca | Consertar a implementação da busca |
| Conflito de dependência | Baixar/travar a versão | Usar o ambiente certo (venv/nvm) |
| Funcionalidade não roda | Remover a funcionalidade | Descobrir por que ela falha |

Pergunta de auto-checagem: **"Estou resolvendo o problema ou fugindo dele?"** Um paliativo
só é aceitável quando (1) o dono aprova explicitamente, (2) está rotulado como temporário e
(3) você registra a correção real como pendência.

## 3. Rastrear o fluxo de dados de trás pra frente
Quando o erro está fundo na pilha de chamadas:
- Onde nasce o valor errado?
- Quem chamou isto com o valor errado?
- Continue subindo até achar a origem.
- **Conserte na origem, não no sintoma.** O bug está onde o dado **primeiro** fica errado —
  não onde o erro finalmente estoura. O sintoma aparece no arquivo A, mas a causa costuma
  estar no B, no C, ou na interação entre eles.

Ordem de prioridade das hipóteses (do mais provável ao menos):
1. **Eu mudei alguma coisa?** → `git diff` / reverta o suspeito primeiro.
2. **O ambiente mudou?** → versões, dependências, config, `.env`.
3. **A entrada externa mudou?** → resposta de API, formato de dado.
4. **Bug novo de verdade?** → só depois de descartar 1-3.

## 4. Matriz ACH (Análise de Hipóteses Concorrentes)
Para bug **intermitente**, com **várias causas possíveis**, ou que **resistiu a 2+ tentativas**.

**Passo 1 — liste TODAS as hipóteses**, até as improváveis:
```
H1: a query devolve dado velho do cache
H2: o token de auth expira entre a requisição e a resposta
H3: condição de corrida no handler assíncrono
H4: a validação de entrada descarta em silêncio um campo obrigatório
```
**Passo 2 — monte a matriz de evidências** (cada evidência apoia/contradiz cada hipótese):
| Evidência | H1 (cache) | H2 (token) | H3 (corrida) | H4 (validação) |
|---|---|---|---|---|
| O bug é intermitente | contradiz | contradiz | **apoia** | contradiz |
| Só acontece sob carga | neutro | neutro | **apoia** | contradiz |
| Log mostra timeout | contradiz | **apoia** | **apoia** | contradiz |
| Deploy novo não resolve | **apoia** | neutro | neutro | **apoia** |

**Passo 3 — elimine** as hipóteses que a evidência contradiz. A que sobra é a melhor pista.
No exemplo, H4 é contradita por duas evidências (elimine primeiro); H2 e H3 sobrevivem —
investigue a mais fácil de testar primeiro.

> A matriz te tira do "eu ACHO que é X" e te bota no "a evidência aponta para X". É o
> antídoto contra a visão de túnel.
