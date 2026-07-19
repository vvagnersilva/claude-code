# Modelos de checklist por área

> **Aviso (leia sempre antes de usar):** os itens abaixo são um **ponto de partida** para
> montar o checklist da auditoria. Eles **não substituem a norma oficial** e podem estar
> desatualizados. Sempre confirme a **versão vigente** na fonte oficial (gov.br/trabalho
> para as NRs, ANPD para LGPD, ABNT para ISO, vigilância sanitária local, Corpo de
> Bombeiros do estado). Nunca apresente um item como "exigência da norma" sem o usuário
> confirmar. Quando o risco for grave ou a exigência for legal, oriente a procurar o
> responsável técnico (engenheiro de segurança do trabalho, DPO, auditor certificado).

Como usar: escolha a área, copie os itens relevantes para um arquivo `.txt` (um item por
linha), adapte ao caso real do usuário e rode `checklist-add`. Convenções do arquivo:
- `*` no início = item **obrigatório**.
- `::` separa o item do **critério de conformidade** (o que conta como "conforme").
- Linhas começando com `#` são ignoradas.

---

## SST — Segurança e Saúde no Trabalho (NRs)

### Geral (qualquer ambiente — base)
```
*Uso correto de EPI pelos trabalhadores :: EPI adequado, em bom estado e efetivamente usado
*EPIs com CA (Certificado de Aprovação) válido :: CA dentro da validade
*Sinalização de segurança visível e legível
*Rotas de fuga e saídas de emergência desobstruídas e sinalizadas
*Extintores no prazo de recarga e acessíveis
Treinamentos de segurança registrados e atualizados
Ordens de serviço de segurança assinadas pelos trabalhadores
Primeiros socorros: material disponível e dentro da validade
```

### NR-12 (máquinas e equipamentos)
```
*Proteções fixas/móveis nos pontos de operação e transmissão :: proteção instalada e íntegra
*Dispositivo de parada de emergência acessível e funcional
*Procedimento de bloqueio e etiquetagem (LOTO) para manutenção
Comandos bimanuais/cortinas de luz onde exigido
Aterramento elétrico do equipamento
Manual de operação disponível ao operador
Capacitação específica do operador registrada
```

### NR-35 (trabalho em altura, acima de 2 m)
```
*Análise de Risco (AR) e Permissão de Trabalho (PT) emitidas antes do serviço
*Cinto de segurança tipo paraquedista com talabarte e ponto de ancoragem
*Trabalhador com capacitação NR-35 válida (validade 2 anos)
Aptidão de saúde (ASO) para trabalho em altura
Sistema de proteção contra quedas inspecionado
Isolamento e sinalização da área abaixo
```

### NR-06 / NR-17 / NR-23 (EPI, ergonomia, incêndio) — itens-chave
```
*Saídas de emergência e iluminação de emergência funcionando (NR-23)
*Brigada de incêndio treinada onde exigido
Mobiliário e posto de trabalho ajustáveis (NR-17)
Pausas e organização do trabalho para tarefas repetitivas (NR-17)
Análise ergonômica do trabalho (AET) realizada (NR-17)
```

---

## LGPD — Proteção de Dados Pessoais
```
*Base legal definida para cada tratamento de dado pessoal :: base legal mapeada e documentada
*Aviso de privacidade/política disponível aos titulares
*Consentimento coletado e registrado quando essa é a base legal
*Canal para o titular exercer direitos (acesso, correção, exclusão)
Registro das operações de tratamento (ROPA) mantido
Controle de acesso aos dados (mínimo necessário por função)
Dados sensíveis com proteção reforçada
Contratos com operadores/terceiros com cláusulas de proteção de dados
Plano de resposta a incidente de dados (notificação à ANPD/titular)
Prazo de retenção e descarte seguro definidos
Encarregado (DPO) designado e divulgado
```

## ISO 27001 — Segurança da Informação (controles-chave, Anexo A)
```
*Política de segurança da informação aprovada e divulgada
*Controle de acesso por perfil e revisão periódica de acessos
*Backup testado e cópia fora do local
Gestão de vulnerabilidades e atualização (patching)
Senhas/MFA conforme política
Classificação da informação (público/interno/confidencial)
Registro e tratamento de incidentes de segurança
Conscientização/treinamento dos colaboradores
Gestão de riscos de segurança documentada
```

---

## ISO 9001 — Qualidade (auditoria interna, itens-base)
```
*Procedimentos documentados onde a norma/empresa exige
*Registros de qualidade mantidos e rastreáveis
*Tratamento de não-conformidades e ações corretivas registrado
Indicadores e metas de qualidade acompanhados
Controle de documentos (versão vigente disponível, obsoletos retirados)
Calibração de instrumentos de medição em dia
Avaliação e reavaliação de fornecedores
Satisfação do cliente medida e analisada
Análise crítica pela direção realizada
```

---

## Vigilância Sanitária (clínicas, salões, alimentos — base genérica)
```
*Alvará/licença sanitária vigente afixado :: licença dentro da validade
*Boas práticas: higienização de mãos, superfícies e instrumentos
*Descarte de resíduos conforme (PGRSS onde aplicável)
*Esterilização/autoclave com controle e registro (saúde)
Controle de validade de produtos e insumos
Armazenamento adequado (temperatura, identificação)
Responsável técnico presente/registrado
Controle de pragas (dedetização) com comprovante
```

## Corpo de Bombeiros / Prevenção de Incêndio (AVCB — base)
```
*AVCB/CLCB vigente :: certificado dentro da validade
*Extintores carregados, no prazo e sinalizados
*Saídas e rotas de fuga desobstruídas e sinalizadas
Iluminação de emergência funcionando
Hidrantes/mangueiras (onde exigido) com pressão e acesso
Sistema de alarme/detecção testado
Brigada de incêndio treinada
Placas de orientação e ponto de encontro definidos
```

---

## Boas práticas para qualquer área
- Comece pelos itens **obrigatórios** (`*`) — são os que reprovam a auditoria.
- Cada item deve ser **verificável** (dá para olhar e dizer conforme/não conforme), não uma
  opinião vaga. Se um item ficar subjetivo, reescreva com um critério objetivo (o `::`).
- Não copie a lista inteira: escolha o que se aplica ao **escopo real** do usuário.
- Sempre registre a **evidência** do que foi conferido (foto, documento, o que se viu).
