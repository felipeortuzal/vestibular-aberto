# Estado do projeto — 01/11/2026

## Etapa 04 — extração piloto Unicamp 2026

Foram selecionadas cinco questões de Matemática da primeira fase comentada da Unicamp 2026: **43, 45, 49, 51 e 52**. A prova oficial possui 71 páginas, 7.882.756 bytes e SHA-256 **2d1d0d375fb8ee7ea84ebb11350ca30851a5c928db80ed6e2479aeeb1ba23284**, obtidos no GitHub Actions.

O pipeline Python/PyMuPDF baixou o arquivo com limite de 25 MiB e timeout, extraiu texto nativo respeitando colunas, identificou **cinco de cinco transcrições candidatas**, gerou prévias do PDF e relatório por página. A questão 45 exigiu ajuste do reconhecimento de alternativas em duas colunas. PDF, transcrições e imagens ficam apenas em `raw/` e `staging/`, fora do Git e do build. A CI usou armazenamento efêmero; o editor pode reproduzir o estágio localmente.

**Estado real:** cinco itens identificados, cinco candidatos extraídos, zero revisões humanas, zero gabaritos finais independentemente conciliados e **zero questões oficiais publicadas**. As alternativas lidas nos comentários Comvest não se transformaram em gabarito final verificado. Direitos conservados em `link_only`; a autorização da Comvest restringe-se à reprodução parcial com atribuição e não exclusiva.

**Testes aprovados na CI do PR #4:** validação de dados, 9 testes V0, 25 testes de contrato, 15 testes de inventário, 9 testes de piloto, build e navegador em 360/768/1440 px. Evidência da extração real: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41362067765 . Ver `docs/ETAPA04_PILOTO.md` para páginas, riscos, método e comandos.

**Limitações:** comparação textual/fórmulas por humano, crédito de figuras, caderno original, gabarito final e retificações precisam de conferência. Nenhuma questão oficial nem PDF está na interface. A V0 preserva 12 exercícios autorais, 29 referências do inventário e progresso local sem migração.

**Próximo passo:** etapa 05 — classificação e revisão humana do lote. Publicação das questões só deve ser considerada na etapa 06, se passar pelos critérios de conteúdo, procedência e direitos.

## Histórico — etapa 03 e redesign


## Etapa 03 + reformulação visual — concluídas na branch de implementação

### Inventário oficial 2024–2026

- **12 recortes**: Fuvest/USP (uma única instituição), Unicamp/Comvest, Insper, FGV × três edições de 2024 a 2026.
- **29 registros catalogados**: 24 referências a documentos + cinco coleções/índices não individualizados. Por instituição: Fuvest 18, Unicamp 6, Insper 2, FGV 3.
- **8 links diretos de arquivo** identificados, dos quais **seis PDFs da Comvest** abertos e os dois gabaritos Fuvest 2024 localizados em busca. PDF aberto não equivale a conteúdo integral revisado.
- **0 questões oficiais extraídas/revisadas/publicadas**, **0 provas individualizadas** em `data/exams.json`; **12 questões autorais de demonstração** preservadas.
- **4 diretórios oficiais** na interface; inventário novo de documentos com filtros por instituição, edição e tipo.
- Situação de uso de todos os registros `rightsStatus: link_only`, sem atribuir autorização generalizada. A Comvest registra exceção **parcial, não exclusiva e com atribuição** para reproduzir questões; cadernos integrais continuam apenas como links externos. Licenças/terceiros e verificação editorial por item pendentes.
- Insper 2026.1/2026.2 em processos distintos Vunesp, sem confundi-los com PDF; edições 2024/25 com lacunas declaradas. FGV unificado 2024.1/2025.1/2026.1 permanece como **coleção**, pois escola/curso/campus não foram conferidos; não foi criado caderno fictício.
- Na Fuvest 2024, gabarito original e retificado são registros separados com `supersedes`. No 2026, retificação localizada sem original para vínculo, mantido como null. Abertura automatizada Fuvest retornou HTTP 403, sem bypass.
- `data/inventory.json` é a fonte canônica, com URL, data de consulta, estado do acesso, pendências, direitos, edição, data de prova quando verificada, caderno e semestre/aplicação. `dist/data/inventory.csv` é derivado durante o build. Matriz legível em `docs/INVENTARIO.md`. Nunca inferir campos desconhecidos.

**Lote piloto proposto para etapa 04:** 5–10 questões objetivas de Matemática da 1ª fase da Unicamp 2026, após conferir caderno, questões, gabarito e imagens de terceiros. Nenhum número, enunciado ou resposta oficial foi transcrito nesta etapa. A prova comentada tem possível divergência editorial entre capa e introdução, registrada como pendência. Fontes e detalhes: `docs/INVENTARIO.md` e `docs/FONTES.md`.

### Reformulação do site (visual V0.3)

A estrutura funcional existente em HTML/CSS/JS puro foi mantida, mas a experiência visual foi refeita: identidade própria azul-marinho/menta, tipografia editorial forte, hero original feito em CSS, navegação lateral simplificada, atalhos de matéria, filtros organizados, cartões de questões e biblioteca integrada com 29 referências filtráveis. Referências apenas de experiência: Universo Narrado e Estratégia Vestibulares; nenhuma marca, logo, código ou banco privado foi copiado. Favicon próprio atualizado.

Preservados: IDs das 12 demonstrações, respostas, busca sem acentos, filtros encadeados, paginação, feedback, repetição, favoritas, importação/exportação e formato de progresso `vestibular-aberto.progress.v1`. O contrato V1 da etapa 02 e o bloqueio de publicação oficial permanecem ativos. O build continua restrito aos arquivos permitidos, não copia staging nem os exemplos sintéticos e rejeita questões reais colocadas no seed da V0.

### Verificação executada na CI

PR #3: https://github.com/felipeortuzal/vestibular-aberto/pull/3

Run aprovado após inventário e documentação: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41254902512
- `python -m pip install -r requirements-dev.txt`: OK.
- `npm run validate`: OK, seed autoral, schemas V1 e inventário 2024–2026.
- `npm test`: 9 testes de comportamento aprovados.
- `npm run test:contract`: 25 testes de contrato aprovados.
- `npm run test:inventory`: 15 testes de inventário aprovados.
- `npm run build`: OK; JSON adaptador e CSV gerados, staging fora do artefato.
- `npm run test:browser`: OK em Chrome headless com 360/768/1440 px, sem overflow horizontal; biblioteca, filtro por instituição/edição, estados vazios e fluxo de estudo/progresso testados.
- Capturas reais de 360/768/1440 px obtidas como artefato de CI; celular e tablet também revisados visualmente. Testes em dispositivo físico e leitor de tela completo ainda pendentes.

### GitHub / publicação

Repositório reutilizado: https://github.com/felipeortuzal/vestibular-aberto
Site público de referência: https://felipeortuzal.github.io/vestibular-aberto/

**Reformulação publicada:** PR #3 integrado na `main` no commit `f23acb41d10b287afbb033668c065f27f29843c5`. O job `build` e o job `deploy` do GitHub Pages terminaram com `conclusion=success` na execução https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41255086160 . URL pública: https://felipeortuzal.github.io/vestibular-aberto/ . A versão nova apresenta 12 demonstrações e 29 registros de metadados, sem conteúdo oficial republicado. Esta atualização documental gera commit próprio posterior ao deploy e não altera a interface. Nenhuma mudança foi feita em outros repositórios.

### Limitações

Não existe importador de questões, prova completa espelhada, revisão humana de conteúdo oficial, verificação integral de todos os PDFs, autorização geral de republicação, sincronização entre navegadores, backend, contas, OCR ou cobrança. Inventário **não é prova importada**; nomes genéricos e coleções FGV/Insper não foram individualizados. Não houve acesso a áreas restritas ou APIs privadas.

## Próximo passo — Etapa 04

Executar `prompts/04-extracao-piloto.md` em staging para até 5–10 questões objetivas de Matemática da Unicamp 2026, conferindo fonte, modelo, página, figura, gabarito, contexto compartilhado e termos de reprodução, com rastreabilidade e revisão explícita. Não liberar publicação antes das etapas 05–06.

## Histórico

Etapa 01: PR #1 e deploy https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41253171901 .
Etapa 02: PR #2 e deploy https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41254258880 .
