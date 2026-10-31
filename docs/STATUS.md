# Estado do projeto — 31/10/2026

## Etapa 02 — contrato V1 integrado à main e publicado

Criados contratos JSON Schema Draft 2020-12 versionados para staging e taxonomia, com validação Python de integridade e seleção conservadora para futura publicação. São 12 coleções V1: institutions, processes, exams, documents, question_groups, questions, answers, explanations, classifications, review_events, question_appearances e user_attempts. Os registros possuem schemaVersion=1, versões/revisões, IDs estáveis, referências a cadernos e modelos, contexto compartilhado, subitens, numeração original textual, blocos de texto/matemática/imagem/tabela e origem/página/hash. Campos desconhecidos aceitam null em staging, mas impedem publicação quando essenciais.

A conferência distingue edição de ingresso e data de aplicação, semestre/aplicação Insper, escola/curso/campus FGV, Fuvest/USP sem duplicação, status preliminar/final/retificado/anulado/ausente de gabarito, dificuldade editorial versus empírica e tags interdisciplinares. Transições editoriais e histórico de correção não podem ser reescritos silenciosamente. A revisão da IA permanece rascunho; somente eventos e atores humanos identificados satisfazem revisão humana.

O export V1 está desligado por padrão e não integra o site público. Mesmo com opt-in isolado para testes, a seleção exige questões objetivas completas, origem, gabarito final do caderno, direitos documentados e revisão humana. O build V0 agora copia somente lista explícita de arquivos e rejeita questões oficiais e provas individualizadas. Nenhuma fixture de staging entra em dist/.

## Contagens verificadas

- 12 questões autorais V0; 4 diretórios oficiais; 0 questões oficiais; 0 provas individualizadas.
- Taxonomia: 12 matérias, 45 assuntos, 122 subassuntos; IDs preservados, sem migração.
- 2 schemas versionados; 12 coleções modeladas; 1 lote sintético exclusivo de testes.
- Histórico local do navegador V0 intacto, sem troca de IDs, formato ou versão.

## Testes reais — CI do PR #2

https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41254005150

- python -m pip install -r requirements-dev.txt: OK.
- npm run validate: OK, seed autoral e contratos de staging.
- npm test: 9 aprovados, zero falhas.
- npm run test:contract: 25 aprovados, zero falhas. Testados IDs duplicados, taxonomia inválida, prova/documento ausente, caderno errado, alternativa inexistente, fluxo de revisão, origem/direitos insuficientes, IA rotulada como humana, questões anuladas e retificações, export bloqueado e export positivo exclusivamente sintético.
- npm run build: OK, V0 estática e whitelist sem staging.
- npm run test:browser: OK em 360, 768 e 1440 px, sem overflow; filtros, correção, favoritas e persistência preservados.

A fixture usa nomes synthetic-*, URLs example.test, hashes e pessoas fictícias: **não comprova nenhuma licença, PDF ou revisão humana real**. Testes positivos verificam apenas a lógica.

## GitHub e publicação

Repositório existente: https://github.com/felipeortuzal/vestibular-aberto
PR #2: https://github.com/felipeortuzal/vestibular-aberto/pull/2
Site público V0: https://felipeortuzal.github.io/vestibular-aberto/

Etapa 02 integrada na main pelo PR #2: commit 5d589cff3d2a4dcab88cf89d707b18bbe794c4b5. Build e deploy GitHub Pages concluídos com sucesso no run https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41254196804 . O site continua exclusivamente com a V0 demonstrativa; a camada V1 está no repositório e não é exibida como conteúdo oficial. A presente atualização de STATUS constitui commit documental posterior.

## Limitações

Sem PDFs ou questões oficiais, licenças reais, verificação de gabarito oficial, revisão humana real de questões, painel editorial, OCR, backend, autenticação, cobrança ou renderização de questões V1. Sem dispositivo físico ou auditoria completa de leitor de tela. Dependência Python de desenvolvimento: jsonschema==4.26.0. Não houve necessidade de migrar dados ou progresso; as 12 demonstrações permanecem como antes.

## Próximo passo — etapa 03

Executar somente prompts/03-inventario-oficial.md: catalogar edições e documentos verificáveis 2024–2026, processo/aplicação e caderno correto, fonte oficial, revisões de gabarito e situação de direitos. Não importar enunciados nem inferir dados ausentes.

## Histórico — etapa 01

PR #1 https://github.com/felipeortuzal/vestibular-aberto/pull/1 ; deploy V0 de referência https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41253171901 .
