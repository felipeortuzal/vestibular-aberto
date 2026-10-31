# Estado do projeto — 31/10/2026

## Entregue

V0.1 em HTML/CSS/JS puro; 12 questões autorais; 4 diretórios oficiais; taxonomia proposta com 12 matérias, 45 assuntos e 122 subassuntos. Filtros dependentes, busca, paginação, alternativas com correção, explicações, favoritas, histórico local, painel e importação/exportação de progresso. Fluxo GitHub Actions preparado. Documentação de dados, ingestão, produto e prompts.

## Não entregue / não afirmar

Zero questões oficiais importadas. Zero provas individualizadas em exams.json. Diretórios não contam como provas completas importadas. Não há contas, banco remoto, sincronização, OCR, painel editorial, simulados, cobrança ou revisão humana de conteúdo. Os diretórios possuem limites de acesso registrados em FONTES.md.

GitHub: repositório público criado em https://github.com/felipeortuzal/vestibular-aberto. Primeiro deploy concluído com sucesso pelo GitHub Actions: https://felipeortuzal.github.io/vestibular-aberto/ . Execução: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41251875933 . Commit de implantação inicial: 94560b4225646a3757dacf78f8679df411366fa1.

## Verificação

Validador de dados e seis testes de comportamento passaram. Build estático concluído. Navegador desktop: filtro Matemática → Geometria plana, resposta correta com explicação, favorita e persistência após recarregar conferidos. Layout conferido também em frame de 375 px; navegação móvel ajustada para duas colunas. Não foi realizado teste em dispositivo físico.

## Próximo passo

Executar o prompt 01 sobre a base já publicada. Depois, prompt 02 antes de qualquer ingestão de conteúdo oficial. A taxonomia detalhada em Matemática já está disponível para refinamento editorial.

A primeira CI apresentou avisos de transição de runtime das Actions e de imagem ubuntu-latest, sem falha de testes/build/deploy. A atualização das versões das Actions pode ser feita na auditoria 01. Exportação/importação tem validação unitária; o diálogo nativo de arquivo não foi testado ponta a ponta nesta sessão.

A segunda execução de testes/build/deploy também passou: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41252015707 . O CSS recebeu versão na URL para atualizar a navegação móvel em navegadores que abriram a implantação inicial.
