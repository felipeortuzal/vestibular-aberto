# Contrato de dados: V0 e evolução

## O que existe agora

`questions.json` contém apenas `kind: demo`, alternativas e explicações autorais. `validate.py` bloqueia conteúdos oficiais deliberadamente: a interface e o contrato completo ainda devem ser implementados pelos prompts 02–06. Não basta desativar o bloqueio. `taxonomy.json` contém IDs estáveis, versão e a hierarquia; é uma proposta editorial, não o programa oficial de qualquer instituição. `sources.json` registra diretórios; `exams.json` está vazio.

O progresso local usa versão 1, array de favoritas e array de tentativas com questionId, choiceId, correct e at. A importação recalcula correct, descarta IDs não presentes e informa substituição. A métrica de acerto usa a última tentativa por questão. Evoluções devem preservar IDs e migrar versões.

## Modelo V1 implementado na etapa 02 (somente staging)

| Entidade | Campos e decisões |
|---|---|
| institutions | id, nome oficial, banca organizadora por processo, região, aliases |
| exams | id opaco estável, institutionId, editionYear, appliedAt, admissionSemester, phase, day, bookletCode, language, applicationStatus, selectionType, campuses[], schools[], courses[] |
| documents | id, examId, type (booklet, answer_key, correction_grid, notice), sourceUrl, landingPageUrl, sha256, páginas, retrievedAt, mimeType, revision, supersedes, accessStatus, rightsStatus, rightsEvidence |
| question_groups | id, examId, texto/figuras compartilhados e ordem das questões |
| questions | id estável, canonicalId, examId, groupId, originalNumber, itemLabel, format, contentBlocks[], choices[], subitems[], sourceLocations[], rightsStatus, reviewStatus |
| answers | questionId, status (preliminary, final, corrected, annulled, missing), value, rubric, sourceDocumentId, sourcePage, revision, verifiedAt |
| explanations | questionId, texto/blocos, authorType (original_editorial, official, licensed), reviewStatus, reviewedAt; IA gera rascunho, não resolução validada automaticamente |
| classifications | questionId, taxonomyVersion, principal (matéria/assunto/subassunto), secondaryTags[], confidence, rationale, proposedBy, reviewedBy, reviewedAt |
| review_events | entidade, id, versão, ação, data, responsável real, comentário, hash anterior e novo |
| user_attempts | id, usuário/visitante, questionId, questionVersion, answerVersion, resposta, resultado, início/fim, modo (study/exam), revisão |

### Regras que evitam perda de informação

- `editionYear` é a edição de ingresso e `appliedAt` é a data da aplicação. Ambos podem divergir. Semestre e fase não devem ser inferidos do nome de um arquivo.
- `originalNumber` é string: “12”, “M.01”, “7b” e variantes são possíveis. Subitens têm IDs e numeração próprios.
- Guardar página física do PDF (1-based) e, se existir, página impressa. Coordenadas de recorte devem informar unidade/origem e hash do arquivo de origem.
- Blocos tipados: texto, matemática/LaTeX, imagem, tabela e referência ao contexto compartilhado. Fórmulas exigem renderizador mantido e sanitizado; não converter tudo em uma imagem sem alternativa acessível.
- Preservar número e ordem original das alternativas, unidades, expoentes, sinais, tabelas, legendas e créditos. Dado ilegível é pendência, não oportunidade de completar por intuição.
- Distinguir objetiva de resposta única, discursiva, numérica, somatória e redação. A V1 publicada pode suportar só a primeira; outros formatos ficam explicitamente não suportados, sem correção automática fictícia.
- Questões anuladas, sem gabarito final ou com conflitos ficam fora da taxa de acerto. Gabarito retificado substitui logicamente o anterior, mantendo histórico e reavaliação transparente de tentativas.
- Dificuldade editorial estimada deve ser rotulada como tal; dificuldade empírica depende de amostra, população, período e mínimo de respostas. Nunca inventar dificuldade com base na banca.
- IDs não dependem de tema, caminho de arquivo ou classificação. Reclasificar não altera favoritas ou histórico.
- Deduplicação por origem/caderno, conteúdo normalizado e imagens. Um hash parecido gera candidato a duplicata; a fusão requer inspeção. Preservar todas as aparições numa tabela de vínculo.

## Estados e publicação

`discovered → acquired → extracted → needs_review → reviewed → published`; `rejected` e `blocked` são saídas possíveis. Armazenar histórico, não apagar pendências.

`rightsStatus`: `unknown`, `link_only`, `authorized`, `licensed`, `original`. A evidência deve ser verificável; a própria IA não concede autorização.

Um item só pode vir a entrar no JSON público se tiver conteúdo e gabarito compatíveis com o formato, fonte/página, revisão editorial e fundamento registrado para a republicação. Se os direitos não estiverem resolvidos, publicar apenas metadados e o link autorizado à fonte, sem embutir enunciado/imagens. Não incluir arquivos de staging no artefato de hospedagem.

## Validação executável — entregue na etapa 02

O contrato de trabalho está em `schemas/v1/bundle.schema.json` (JSON Schema Draft 2020-12) e `schemas/v1/taxonomy.schema.json`. Os campos obrigatórios podem conter `null` quando desconhecidos; isso é válido para **staging**, não torna o item publicável. Cada entidade e o lote têm `schemaVersion: 1`, além de `version` ou `revision` quando aplicável. As 12 coleções V1 são: `institutions`, `processes`, `exams`, `documents`, `question_groups`, `questions`, `answers`, `explanations`, `classifications`, `review_events`, `question_appearances`, `user_attempts`.

O validador `scripts/contracts_v1.py` complementa o esquema com referências entre entidades, esquema e hierarquia de taxonomia, unicidade de IDs, número/ordem de alternativas e subitens, modelo de caderno e gabarito, revisão com histórico, origem/página/hash do documento, conflitos e tentativas não pontuáveis. Um gabarito retificado não destrói o anterior: usa `revision` e `supersedes`; tentativas antigas pontuadas exigem reavaliação. Questão anulada, sem gabarito final, em conflito ou com versão superada não pode entrar como acerto/erro.

**O contrato de staging e os critérios de export são diferentes.** `publishability(bundle, taxonomy)` devolve motivos de bloqueio. Para conteúdo oficial objetivo, a seleção futura exige, no mínimo, enunciado e alternativas completos, origem documental e página, hashes, documento e gabarito verificáveis do mesmo caderno, edição e data, direitos adequados com evidência humana verificável, classificação e explicação revisadas por humano real e sequência editorial concluída em `published`. Status `link_only` ou `unknown` não permitem reprodução integral. A função `export_public_bundle(..., enable_official=False)` **retorna seleção vazia por padrão**, e `scripts/build.py` continua recusando qualquer questão não autoral e qualquer prova individualizada até uma etapa posterior. Exportar conteúdo V1 para o site requer integração e checagens adicionais na etapa 06; alterar só o parâmetro do teste **não habilita** publicação.

Os exemplos `tests/fixtures/v1/synthetic_bundle.json` usam IDs `synthetic-*`, URLs `example.test`, hashes e atestados **fabricados exclusivamente para teste** — não são documentos, licenças nem revisão realmente realizada. `npm run test:contract` valida casos positivos/negativos com `jsonschema==4.26.0` instalado por `requirements-dev.txt`. A CI também roda `npm run validate`, `npm test`, `npm run build` e `npm run test:browser`, sem publicar fixtures ou staging.

## Arquitetura de crescimento

V0: JSON + adaptador JS + localStorage. V1: dados particionados por instituição/edição e índice leve; nenhum download de todo o acervo ao abrir a home. Um catálogo de 100 mil itens não deve virar um único script carregado pelo cliente.

Quando houver contas: banco relacional e armazenamento de arquivos, API paginada, índices de filtros, autenticação, backup e papéis editoriais. GitHub Pages serve apenas o cliente estático; não hospeda um backend persistente. O provedor será escolhido quando a necessidade estiver validada, com custo e limites documentados.

## Compatibilidade e migração

Não há migração de dados na etapa 02. `data/questions.json`, `data/exams.json`, `data/taxonomy.json`, IDs `demo-001`–`demo-012` e o formato `vestibular-aberto.progress.v1` do navegador foram preservados. O esquema V1 aplica-se **a novos lotes editoriais**, não diretamente ao JSON legado da V0. Um adaptador de renderização e migração versionada só será necessário quando houver conteúdo oficial elegível; não alterar silenciosamente favoritos nem tentativas.

Para FGV, registrar `schools[]`, `campuses[]` e `courses[]` **no processo e na prova aplicável**, sem clonar um PDF compartilhado. Para Insper, `admissionSemester` e `applicationId` distinguem processo e aplicação; nunca inferir esses campos do nome de um arquivo. Para Fuvest/USP a identidade institucional é única com banca Fuvest, não dois acervos duplicados. Edição de ingresso e data de aplicação são campos independentes.
