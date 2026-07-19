# Setup do Escriba (roda uma vez)

Quando o usuário pedir **"rode o setup do Escriba"**, faça a configuração inicial:

1. Faça as perguntas de `setup/perguntas.md` (uma de cada vez, de forma simples).
2. Com as respostas, rode o script de conclusão a partir da **raiz do projeto** do usuário:

   ```bash
   bash .claude/skills/escriba/setup/concluir-setup.sh \
     --nome "<nome>" --empresa "<empresa>" --pasta "<pasta de trabalho>" \
     --formato-tabela <xlsx|csv> --formato-doc <docx|md> \
     --tom <formal|cordial|direto> --idioma <pt-BR>
   ```

   (Ajuste o caminho se o Escriba estiver instalado globalmente em `~/.claude/skills/escriba/`.)

3. O script grava `./.escriba/config.md` (ignorado pelo git) e **remove sozinho** o `SETUP.md`
   e a pasta `setup/`. Depois disso o Escriba usa as preferências automaticamente.

O setup é opcional — sem ele o Escriba funciona com bons padrões (PT-BR, XLSX para tabelas,
DOCX para documentos) e só pergunta o necessário na hora.
