# Etapa 06 — banco V1 publicado somente após aprovação

**Data de implementação:** 02/11/2026. **PR:** [#6](https://github.com/felipeortuzal/vestibular-aberto/pull/6).

## Resultado efetivo do primeiro lote

O pipeline de publicação e a interface de provas estão implementados, mas **nenhuma das cinco questões do piloto da Unicamp 2026 é elegível**: falta revisão humana, conferência integral de símbolos/transcrições, reconciliação com o gabarito final do caderno e análise individual de direitos. Isto não autoriza inventar uma decisão editorial.

| Instituição | Provas individualizadas com referência direta | Questões oficiais publicadas | Candidatas da etapa 05 |
|---|---:|---:|---:|
| Fuvest / USP | 0 | 0 | 0 |
| Unicamp / Comvest | 1 (prova comentada, link oficial) | 0 | 5 |
| Insper | 0 | 0 | 0 |
| FGV | 0 | 0 | 0 |
| **Total** | **1** | **0** | **5** |

O inventário de 29 registros e os quatro diretórios oficiais continuam disponíveis. A prova individualizada tem origem, edição 2026, data de aplicação de 26/10/2025, primeira fase, indicação de caderno Q, 71 páginas e hash SHA-256 verificável. A versão aplicada, o gabarito final/retificado e eventuais grades ainda **não** foram conciliados. Por isso, o card exibe apenas o **link da prova comentada**, identifica a limitação e informa **0 questões aprovadas**. O número total de questões desta prova permanece \`null\`, não uma estimativa.

### Fonte e direitos

- [Comvest — provas comentadas por ano](https://www.comvest.unicamp.br/vestibulares-anteriores/1a-fase-2a-fase-comentadas/), onde há autorização explícita somente para **reprodução parcial** de questões anteriores, não exclusiva, com citação da Comvest e do ano.
- [Prova comentada da primeira fase de 2026](https://www.comvest.unicamp.br/wp-content/uploads/2026/06/F1_2026_Prova-Q.pdf). A plataforma **não hospeda** o PDF. O hash registrado é \`2d1d0d375fb8ee7ea84ebb11350ca30851a5c928db80ed6e2479aeeb1ba23284\`.
- A declaração da Comvest **não** resolve automaticamente direitos de imagens, trechos de terceiros, provas integrais ou outras bancas. As cinco questões seguem com \`rightsStatus=link_only\` em staging.

## Arquitetura de publicação

\`data/questions.json\` mantém **exatamente 12 exercícios autorais**, com IDs e formato preservados. A fonte pública de conteúdo real é \`data/publication-v1.json\` (inicialmente um contrato V1 vazio, ainda sem questões aprovadas); **não** é o staging \`pilot/\`, que nunca é copiado. O build usa:

1. \`scripts/contracts_v1.py\` para JSON Schema, integridade, situação dos direitos, revisão humana, resposta final e trilha editorial.
2. \`scripts/publication_v1.py\` para projetar **somente** as entidades V1 elegíveis, conferir se pertencem ao mesmo exame/versão/arquivo do catálogo e converter os blocos revisados para o formato seguro usado pela interface.
3. \`data/exams.json\` para a prova individualizada. O estado \`metadata_only\` e o contador \`approvedQuestionCount=0\` são checados contra o resultado real do projetor. Quando houver aprovações futuras, o exame deve mudar para \`published\` e o contador deve ser igual ao número exportado; a edição/data/modelo também devem conferir.
4. \`data/approved-assets.json\` para imagens autorizadas individualmente, com arquivo local, hash, atribuição e revisão humana. No momento o manifesto é \`[]\`.
5. \`scripts/build.py\` para produzir \`dist/data/official-questions.json\`, \`dist/data/publication-summary.json\` e \`data/catalog.js\`. O pacote publicado recebe só os registros elegíveis e arquivos explícitos; **não** recebe \`data/publication-v1.json\`, \`pilot/\`, \`raw/\`, \`staging/\`, fixtures de teste, direitos em discussão ou eventos editoriais.

A opção técnica \`enable_official=True\` **não** é uma autorização por si só: aplica todos os requisitos de \`publishability()\`. Alterar o status no navegador ou passar uma flag não converte material pendente em publicado.

## Experiência do vestibulando

- Banco: etiquetas explícitas de **DEMONSTRAÇÃO / AUTORAL** e **QUESTÃO OFICIAL** (esta última só é exibida quando houver itens realmente aprovados). Contador de oficiais separado.
- Filtros combinados por instituição, edição, semestre, fase, escola, curso, matéria, assunto e subassunto. As opções se originam dos JSON e não inventam semestres/curso desconhecidos. Estado vazio informa que a seleção ainda não tem questões oficiais aprovadas.
- Área **Provas**: catálogo de provas individualizadas com edição, data, fase, modelo, documentos conferidos por link e estado da cobertura; depois vêm os quatro diretórios e o inventário geral de 29 registros. Sem PDF próprio nem gabarito presumido.
- Blocos editoriais: texto inserido com \`textContent\`, matemática exibida inicialmente via **texto alternativo legível** (o LaTeX revisado permanece no dado), tabelas via DOM e figuras apenas quando houver manifesto/arquivo autorizado com \`alt\` e crédito. **A formatação tipográfica completa de LaTeX ainda não está implementada**; não afirmar que existe.
- Correção: admite apenas gabaritos finais ou retificados em itens publicados. A tentativa registra \`answerRevision\`; a importação V1 do histórico antigo recalcula o acerto conforme versão vigente. Quando um item for anulado ou não tiver gabarito final, a tentativa não conta como acerto nem erro. Não há correção binária automática de discursivas.
- Progresso: mantém a chave \`vestibular-aberto.progress.v1\`, os 12 IDs autorais, favoritas, exportação/importação e cálculos sobre a última tentativa. Não há sincronização entre aparelhos.

## Verificações e pendências

A CI do PR testa os contratos V1, inventário, piloto, etapa 05, **12 novos casos de publicação**, filtros de banco por prova, regressão do progresso, bloqueio de dados editoriais no build e fluxo de navegador (360, 768 e 1440 px). A prova positiva usa exclusivamente a **fixture sintética**, nunca publicada. O teste real exige que o pacote de produção contenha zero questões oficiais.

**Pendências:** revisão editorial humana de texto, fórmulas e figuras das cinco candidatas; gabarito final de Q e eventuais retificações; condições de direitos por item; tipografia de fórmulas via renderizador confiável quando houver conteúdo elegível; validação futura com uma questão autorizada real de ponta a ponta. Não alterar contadores para fabricar cobertura.

**Próxima etapa:** \`prompts/07-sessoes-e-progresso.md\`, após o mecanismo de publicação estar validado, mantendo a aprovação humana da etapa 05 como dependência para publicar conteúdo oficial.
