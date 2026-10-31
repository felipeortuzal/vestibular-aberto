# Vestibular Aberto

Primeira base de uma plataforma de questões de vestibulares brasileiros. Nome provisório, ainda sem validação de marca/domínio. Preparada em 31/10/2026 para Felipe.

**Situação real:** protótipo funcional em HTML/CSS/JavaScript, 12 questões autorais de demonstração e links para 4 diretórios oficiais. Não é ainda um banco de provas oficiais. Repositório: https://github.com/felipeortuzal/vestibular-aberto. A configuração inicial do GitHub Pages está em andamento; consulte docs/STATUS.md.

## Abrir agora

Extraia o ZIP mantendo as pastas e abra `index.html`. Não abra só o HTML separado dos arquivos `assets/` e `data/`. Não há instalação de dependências para experimentar. O progresso fica neste navegador e pode ser exportado em Meu desempenho. O comportamento de armazenamento em `file://` pode variar por navegador; a publicação em HTTP(S) é o uso recomendado.

## O que já funciona

- Matéria → assunto → subassunto, busca sem acentos, instituição, situação da resposta, ordenação e paginação.
- Marcar alternativa, conferir resposta, ler explicação autoral e tentar novamente.
- Favoritas e estatísticas usando a última resposta de cada questão.
- Exportação/importação de progresso em JSON com validação.
- Diretórios oficiais da Fuvest, Unicamp, Insper e FGV.
- Layout adaptável e navegação por teclado.

Escolher uma instituição oficial retorna um estado vazio honesto, pois as 12 questões são autorais. Algumas matérias da taxonomia ainda não têm exemplos. `data/exams.json` está vazio: os quatro links são diretórios, não quatro provas completas cadastradas.

## Estrutura

| Caminho | Função |
|---|---|
| index.html | Interface principal |
| assets/ | Estilo, interface e regras de filtros/progresso |
| data/questions.json | Questões autorais canônicas |
| data/taxonomy.json | 12 matérias, 45 assuntos, 122 subassuntos; proposta inicial |
| data/sources.json | Fontes oficiais e limites da verificação |
| data/exams.json | Reservado para provas individualizadas; vazio na V0 |
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
npm run validate
npm test
npm run build
```

Não é necessário `npm install`. O build atualiza `data/catalog.js` e cria `dist/`. Após mudar qualquer JSON, execute o build. `dist/` e `.openai/` são locais e ignorados pelo Git. Não há API, banco remoto, autenticação, OCR ou pipeline de importação implementado nesta versão.

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

Leia `docs/ROTEIRO.md`. No início da sessão de implementação, cole `prompts/00-contexto-mestre.md`; depois, use apenas o prompt da etapa atual. O primeiro é `01-auditoria-v0.md`, pois a interface básica já existe. Traga o resultado, diff, testes e pendências para a revisão antes de avançar. Essa divisão organiza o trabalho; não pressupõe que um modelo sempre será superior ao outro.

O próximo objetivo útil é uma pequena seleção de questões reais completamente rastreáveis, e não uma promessa de ter todos os vestibulares. A expansão deve preservar o padrão de qualidade.
