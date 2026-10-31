# JSON Schemas versionados

- \`v1/bundle.schema.json\`: JSON Schema Draft 2020-12, contrato de **staging** com \`schemaVersion: 1\` no lote e em cada entidade. As 12 coleções são: institutions, processes, exams, documents, question_groups, questions, answers, explanations, classifications, review_events, question_appearances e user_attempts.
- \`v1/taxonomy.schema.json\`: hierarquia de matérias, assuntos e subassuntos preservada da V0; revisão de nomenclatura pendente de editor.
- \`../scripts/contracts_v1.py\`: valida estrutura com \`jsonschema\`, referência entre entidades, taxonomia, modelos de caderno, respostas e transições, além de portas para futura publicação.
- \`../tests/fixtures/v1/synthetic_bundle.json\`: lote FICTÍCIO para testes negativos/positivos. **Nunca publicar esse arquivo nem alegar que houve revisão real, direito de uso ou verificação de PDF.**

Execução após \`python3 -m pip install -r requirements-dev.txt\`:

\`\`\`bash
npm run validate
npm run test:contract
\`\`\`

\`npm run build\` usa allowlist de arquivos da V0; não copia schemas, staging, fixtures, tentativas ou revisão ao site. Nenhuma questão oficial será publicada na etapa 02. O validador legado do seed autoral continua intocado em suas regras de bloqueio.
