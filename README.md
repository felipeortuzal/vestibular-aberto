# Vestibular Aberto

Biblioteca pública de referência e ambiente de prática de vestibulares brasileiros. Nome provisório, ainda sem validação de marca/domínio. Preparada em 31/10/2026 para Felipe.

**Situação real:** protótipo funcional em HTML/CSS/JavaScript, 12 questões autorais de demonstração, 1 prova comentada individualizada por link oficial, 4 diretórios e inventário de 29 referências. **0 questões oficiais aprovadas/publicadas**. Não é ainda um banco de provas oficiais. Repositório: https://github.com/felipeortuzal/vestibular-aberto. Site publicado: https://felipeortuzal.github.io/vestibular-aberto/ . Consulte docs/STATUS.md para o registro de verificação.

## Abrir agora

Extraia o ZIP mantendo as pastas e abra `index.html`. Não abra só o HTML separado dos arquivos `assets/` e `data/`. Não há instalação de dependências para experimentar. O progresso fica neste navegador e pode ser exportado em Meu desempenho. O comportamento de armazenamento em `file://` pode variar por navegador; a publicação em HTTP(S) é o uso recomendado.

## O que já funciona

- Matéria → assunto → subassunto, busca sem acentos, instituição, situação da resposta, ordenação e paginação.
- Marcar alternativa, conferir resposta, ler explicação autoral e tentar novamente.
- Favoritas e estatísticas usando a última resposta de cada questão.
- Exportação/importação de progresso em JSON com validação.
- Diretórios oficiais da Fuvest, Unicamp, Insper e FGV.
- Layout adaptável e navegação por teclado.

Escolher uma instituição oficial retorna um estado vazio honesto, pois as 12 questões são autorais. Algumas matérias da taxonomia ainda não têm exemplos. `data/exams.json` contém 1 prova comentada identificada por link, mas **não** uma prova importada ou conteúdo oficial liberado.

## Estrutura

| Caminho | Função |
|---|---|
| index.html | Interface principal |
| assets/ | Estilo, interface e regras de filtros/progresso |
| data/questions.json | Questões autorais canônicas |
| data/taxonomy.json | 12 matérias, 45 assuntos, 122 subassuntos; proposta inicial |
| data/sources.json | Fontes oficiais e limites da verificação |
| data/exams.json | Catálogo de provas individualizadas com estado e links oficiais; atualmente 1 referência Unicamp 2026 |
| data/publication-v1.json | Contrato V1 reservado a conteúdos integralmente aprovados; atualmente vazio, nunca copiado como staging |
| data/approved-assets.json | Manifesto de imagens autorizadas; atualmente vazio |
| scripts/publication_v1.py | Gates de publicação e projeção segura do V1 para o site |
| data/inventory.json | Matriz oficial 2024–2026, 12 recortes e 29 referências (não provas importadas) |
| dist/data/inventory.csv | CSV gerado pelo build, sem duplicar a fonte de verdade |
| schemas/v1/ | Contrato JSON Schema 2020-12, incluindo taxonomia |
| scripts/contracts_v1.py | Integridade, transições editoriais e seleção conservadora de publicação |
| tests/fixtures/v1/ | Dados FICTÍCIOS usados só em testes; nunca vão ao site |
| requirements-dev.txt | Dependência Python do validador V1 |
| data/catalog.js | Adaptador gerado para abrir sem servidor |
| scripts/ | Validação e preparação da publicação |
| tests/ | Testes de comportamento, sem dependências externas |
| docs/ | Produto, dados, fontes, ingestão, roteiro e status |
| prompts/ | Prompts numerados para o Sol 6 |
| .github/workflows/pages.yml | Validação e publicação estática |
| AGENTS.md | Regras permanentes para a implementação |

## Validar e preparar

Com Python 3 e Node.js instalados:

```bash
python3 -m pip install -r requirements-dev.txt
npm run validate
npm test
npm run test:contract
npm run test:inventory
npm run test:pilot
npm run test:review
npm run test:publication
npm run build
npm run test:browser  # requer Chrome ou Chromium local
```

Não é necessário `npm install`; a V0 roda no navegador sem dependências JavaScript. A validação V1 requer apenas `jsonschema` em Python, com versão fixada em `requirements-dev.txt`. `npm run test:contract` roda as verificações de integridade e de bloqueio usando exclusivamente fixtures sintéticas fora de `dist/`. `npm test` roda os testes unitários; `npm run test:browser` verifica a interface em 360, 768 e 1440 px e os fluxos principais por navegador real (Chrome ou Chromium instalado). O build atualiza `data/catalog.js` e cria `dist/`. Após mudar qualquer JSON, execute o build. `dist/` e `.openai/` são locais e ignorados pelo Git. Não há API, banco remoto, autenticação, OCR ou pipeline de importação implementado nesta versão.

## GitHub e site público

Repositório público criado: https://github.com/felipeortuzal/vestibular-aberto. Os passos abaixo permitem reproduzir a publicação em outro repositório; não crie uma segunda cópia por engano.

1. Crie o repositório e envie esta pasta, incluindo `.github/`, com branch `main`.
2. Em Settings → Pages, selecione GitHub Actions como fonte.
3. Execute o workflow `Validar e publicar HTML` ou faça um push para `main`.
4. Use a URL efetivamente retornada pelo deploy; não anuncie uma URL calculada antes da publicação.

Se tiver Git e GitHub CLI autenticados, o caminho equivalente é:

```bash
git init -b main
git add .
git commit -m "feat: inicia prototipo e roteiro do Vestibular Aberto"
gh repo create vestibular-aberto --public --source=. --remote=origin --push
```

Antes de executar, confira se esse nome ainda está livre. Não execute novamente se o repositório já tiver sido criado. A criação por CLI não habilita automaticamente Pages: configure a fonte e confira a execução. Documentação oficial: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Como trabalhar com Astra + Sol

Leia `docs/ROTEIRO.md`. No início de uma sessão de implementação, leia `AGENTS.md` e `docs/STATUS.md` e use o prompt da etapa vigente. As etapas 01 a 06 tiveram implementação técnica. Cinco candidatas da etapa 05 aguardam aprovação humana; o próximo prompt é o 07 (sessões e progresso), sem desbloquear publicação por suposição. Traga o resultado, diff, testes e pendências para a revisão antes de avançar. Essa divisão organiza o trabalho; não pressupõe que um modelo sempre será superior ao outro.

O próximo objetivo útil é uma pequena seleção de questões reais completamente rastreáveis, e não uma promessa de ter todos os vestibulares. A expansão deve preservar o padrão de qualidade.

## Contrato editorial V1 (etapa 02)

A V0 continua exibindo exclusivamente 12 questões autorais. A camada V1 de **staging** usa `schemaVersion: 1` no lote e nas entidades de provas, processos, documentos, grupos, questões, respostas, explicações, classificação, revisões, aparições e tentativas. Campos desconhecidos são `null`, não suposições; validação de JSON Schema e checagens entre entidades são independentes da interface.

O módulo `scripts/contracts_v1.py` inclui `export_public_bundle(bundle, taxonomy, enable_official=False)`: o padrão **não exporta conteúdo oficial**, e o build V0 bloqueia qualquer dado que não seja demonstração e só copia arquivos expressamente permitidos. A opção de teste `enable_official=True` valida critérios mais estritos para o futuro, sem integração com o site. Os exemplos em `tests/fixtures/v1/` usam identidades e URLs reservadas fictícias, não constituem licença, documento ou revisão real. Veja `docs/DADOS.md` e `docs/TAXONOMIA.md`.

## Etapa 03: biblioteca de fontes e nova interface

A interface V0.3 foi redesenhada com identidade própria, navegação mais direta, tipografia editorial, módulos de estudo e cartões de biblioteca — usando apenas como **referências de experiência** os produtos [Universo Narrado](https://universonarrado.com.br/) e [Estratégia Vestibulares](https://vestibulares.estrategia.com/curso/), sem copiar marcas, conteúdo ou layouts proprietários. Os filtros, o gabarito de demonstração e a persistência local continuam iguais.

Em **Provas e gabaritos**, há dois blocos distintos: os quatro diretórios oficiais e o inventário de **29 registros** de referência (24 referências a documentos e 5 índices/coleções), filtrável por instituição, edição e tipo. Há 8 URLs diretas identificadas, mas **nenhuma prova foi importada**. O CSV é gerado em `dist/data/inventory.csv` a partir do JSON canônico, incluindo pendências e estado dos direitos; não existe base duplicada para editar. `npm run test:inventory` valida a origem e bloqueia a inclusão de conteúdo não autorizado. Consulte `docs/INVENTARIO.md` e `docs/STATUS.md` para evidência e lacunas.

## Etapa 04: extração piloto protegida (Unicamp 2026)

Selecionadas cinco questões de Matemática da primeira fase comentada (43, 45, 49, 51 e 52). Seus **metadados** estão em `pilot/unicamp-2026-math/`. A prova, textos extraídos e imagens ficam exclusivamente em `raw/` e `staging/` (ambos ignorados e não publicados). O script `scripts/ingest_pilot.py` permite `--mode probe` (captura e hash) e `--mode extract` (camada textual e candidatos à revisão). Instale `requirements-dev.txt` e rode `npm run test:pilot`. Nenhum gabarito final foi formalmente conciliado, e **nenhuma questão oficial foi incorporada ao site**. Leia `docs/ETAPA04_PILOTO.md` antes de executar o lote.

## Etapa 05: pré-revisão editorial (aguardando revisão humana)

Foram propostas cinco classificações V1 e cinco resoluções matemáticas originais, todas com `proposedBy.type=ai`, `reviewStatus=needs_review` e `reviewedBy=null`. Os itens 43, 45, 49, 51 e 52 da Unicamp 2026 têm checklist próprio em `pilot/unicamp-2026-math/review-checklist-v1.json`; os textos oficiais continuam fora do repositório. Consulte `docs/ETAPA05_REVISAO.md` para decisões necessárias e execute `npm run test:review` para validar que nenhum item possa aparecer como aprovado ou publicável sem revisão e gabarito final. O site segue exibindo somente as 12 questões autorais.

## Etapa 06 — banco real protegido e provas por edição

A interface V0.6 identifica demonstrações separadamente de eventuais questões oficiais aprovadas, oferece filtros por edição, semestre, fase, escola e curso e mostra uma referência individualizada à prova comentada da Unicamp 2026. Os PDFs são links na fonte; o gabarito final continua pendente. A projeção de `data/publication-v1.json` passa por gates de autoria, revisões humanas, direitos, gabarito, origem e hash, e exclui o material pendente. O build apenas copia arquivos permitidos. O conteúdo público segue com **12 autorais, 0 oficiais e 1 referência de prova**. Leia `docs/ETAPA06_PUBLICACAO.md` antes de tentar publicar novas questões.
