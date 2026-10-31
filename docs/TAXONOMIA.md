# Auditoria editorial da taxonomia — etapa 02

## Situação e decisão

A taxonomia canônica continua em `data/taxonomy.json`, com **version = 1**, status de proposta editorial, **12 matérias, 45 assuntos e 122 subassuntos**. Nenhum ID foi renomeado nem houve migração: os identificadores já são usados pela V0 para filtros, favoritas e progresso. O esquema `schemas/v1/taxonomy.schema.json` valida a estrutura; `scripts/contracts_v1.py` valida unicidade de IDs e relações de caminho entre matéria, assunto e subassunto.

## Matemática — 14 assuntos existentes

1. Aritmética e proporcionalidade
2. Álgebra
3. Funções
4. Sequências
5. Geometria plana
6. Geometria espacial
7. Geometria analítica
8. Trigonometria
9. Análise combinatória
10. Probabilidade
11. Estatística
12. Matemática financeira
13. Matrizes e determinantes
14. Conjuntos e lógica

Geometria plana distingue triângulos/semelhança, áreas, circunferência/círculo e polígonos. Funções separa afim, quadrática, exponencial, logarítmica, composição/inversa. Não se presume que esse conjunto seja um programa oficial de qualquer prova; futuras questões reais exigirão taxonomia revista no contexto de cada banca e ano.

## Demais matérias e pendências editoriais

Física, Química, Biologia, Português, Literatura, História, Geografia, Inglês, Filosofia, Sociologia e Redação seguem com seus caminhos existentes. Algumas categorias são propositalmente amplas (especialmente Inglês e Redação) e podem exigir novos subassuntos depois de um inventário real, **sem excluir ou reaproveitar IDs antigos**. Reclassificações devem registrar versão da taxonomia, justificativa e evento de revisão; a IA propõe, humano confirma.

Cada classificação V1 possui `primary` válido e `secondaryTags[]` opcionais também validadas na hierarquia, permitindo questões interdisciplinares. Confiança da IA pode ser `null`, e não se declara classificação humana quando `reviewedBy` não é humano. A dificuldade `editorial` pode ser desconhecida ou ser uma estimativa atribuída; a dificuldade `empirical` requer amostra, população e período e também pode ser `null`.

## Política de evolução

Conservar IDs estáveis; adicionar nova taxonomia com versão explícita e mapa de migração de caminhos se houver mudança estrutural. Testar que favoritos e tentativas preservam `questionId` após reclassificação. Não transformar frequência de uma questão num assunto em promessa de incidência por vestibular sem denominador verificado.
