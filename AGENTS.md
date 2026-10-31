# Vestibular Aberto — instruções de implementação

Leia README.md, docs/PRODUTO.md, docs/DADOS.md, docs/FONTES.md e docs/STATUS.md antes de editar. O pedido do usuário prevalece. Não use subagentes sem pedido expresso.

- Comece por HTML, CSS e JavaScript puro. Sem framework, banco remoto, autenticação ou cobrança na V0. Não migre toda a aplicação para realizar um ajuste pontual.
- O pacote atual é um protótipo: 12 questões autorais, 4 diretórios, ZERO questões oficiais e ZERO provas importadas. Contadores devem refletir dados reais. Não atribua as demonstrações a Fuvest, Unicamp, Insper ou FGV.
- Dados canônicos ficam nos JSON de data/. data/catalog.js é gerado por scripts/build.py e permite abrir index.html sem servidor. Não edite catalog.js diretamente.
- Não invente enunciados oficiais, URLs de PDF, alternativas, anos, números de questões, gabaritos, licenças ou percentuais de cobertura. Preserve null e pendências quando não houver evidência.
- Não copie resoluções ou bancos privados de concorrentes. Fontes oficiais são o ponto inicial para catalogação; disponibilidade pública não é comprovação de autorização de republicação. Registre situação dos direitos antes de publicar conteúdo integral.
- Mantenha fonte, caderno, edição e revisão do gabarito junto à questão. Não misture semestres do Insper nem cursos/escolas da FGV. Não duplique um caderno compartilhado entre cursos.
- Taxonomia é hierárquica e versionada; classificação interdisciplinar deve comportar tags secundárias. Dificuldade editorial e empírica são informações distintas, e ambas podem estar ausentes.
- Use textContent para texto externo; nunca injete HTML de OCR, PDFs ou importações sem sanitização. Não coloque chaves de API no cliente, nos commits ou em localStorage.
- Preserve progressos e IDs estáveis. Alteração incompatível pede migração explícita e teste de recuperação.
- Implemente a etapa solicitada e complete sua verificação. Rode `npm run validate`, `npm test`, `npm run build`. Faça teste visual quando houver navegador disponível e descreva qualquer limitação.
- Ao concluir, atualize docs/STATUS.md com recursos entregues, contagens, testes, pendências e o próximo prompt. Informe arquivos e commit reais; não declare publicação sem URL confirmada.
- Commits pequenos e claros. Não faça force push nem altere outras aplicações do usuário. Não crie contas, assinaturas ou serviços pagos por iniciativa própria.
