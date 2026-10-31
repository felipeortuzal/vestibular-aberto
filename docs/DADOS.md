# Contrato de dados: V0 e evolução

## O que existe agora

`questions.json` contém apenas `kind: demo`, alternativas e explicações autorais. `validate.py` bloqueia conteúdos oficiais deliberadamente: a interface e o contrato completo ainda devem ser implementados pelos prompts 02–06. Não basta desativar o bloqueio. `taxonomy.json` contém IDs estáveis, versão e a hierarquia; é uma proposta editorial, não o programa oficial de qualquer instituição. `sources.json` registra diretórios; `exams.json` está vazio.

O progresso local usa versão 1, array de favoritas e array de tentativas com questionId, choiceId, correct e at. A importação recalcula correct, descarta IDs não presentes e informa substituição. A métrica de acerto usa a última tentativa por questão. Evoluções devem preservar IDs e migrar versões.

## Modelo a implementar no prompt 02

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

Um item só entra no JSON público se tiver conteúdo e gabarito compatíveis com o formato, fonte/página, revisão editorial e fundamento registrado para a republicação. Se os direitos não estiverem resolvidos, publicar apenas metadados e o link autorizado à fonte, sem embutir enunciado/imagens. Não incluir arquivos de staging no artefato de hospedagem.

## Validação executável futura

Criar JSON Schemas versionados para as entidades acima e validá-los na CI. Testar integridade referencial, taxonomia, duplicatas, alternativa correta, documento correspondente ao modelo de prova, origem de resolução, transições e publicação. O esquema deve aceitar null para desconhecidos e bloquear publicação sem os campos obrigatórios, sem impedir o cadastro de pendências.

## Arquitetura de crescimento

V0: JSON + adaptador JS + localStorage. V1: dados particionados por instituição/edição e índice leve; nenhum download de todo o acervo ao abrir a home. Um catálogo de 100 mil itens não deve virar um único script carregado pelo cliente.

Quando houver contas: banco relacional e armazenamento de arquivos, API paginada, índices de filtros, autenticação, backup e papéis editoriais. GitHub Pages serve apenas o cliente estático; não hospeda um backend persistente. O provedor será escolhido quando a necessidade estiver validada, com custo e limites documentados.
