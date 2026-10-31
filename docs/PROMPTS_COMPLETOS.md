# Vestibular Aberto — setup e prompts para desenvolver com o Sol 6

Preparado em 31/10/2026. Nome provisório. Este pacote acompanha um protótipo funcional em HTML e organiza a construção de um banco real de vestibulares.

## O que já está pronto

HTML/CSS/JavaScript com 12 questões autorais de demonstração, filtros por matéria/assunto/subassunto, correção, favoritas, histórico local e diretórios de Fuvest, Unicamp, Insper e FGV. Taxonomia inicial: 12 matérias, 45 assuntos e 122 subassuntos. Ainda não há questões oficiais importadas, provas individualizadas, contas ou backend. Repositório criado: https://github.com/felipeortuzal/vestibular-aberto. Consulte docs/STATUS.md para o resultado final da publicação.

## Como usar

Extraia o ZIP e abra index.html mantendo assets/ e data/ ao lado. No ambiente do Sol 6, disponibilize o repositório, envie o contexto 00 e depois apenas a etapa atual. Comece pelo 01, pois a interface já existe. Execute 04–06 repetidamente para cada lote, sem tentar importar tudo em uma única tarefa. As etapas 09–10 dependem da maturidade do produto.

## Decisão de produto

Duas áreas ligadas por uma origem comum: Provas completas (caderno, gabarito, retificações e grades) e Banco de questões (enunciado, imagens, alternativas, resposta, resolução e classificação). Começar por Fuvest/USP, Unicamp, Insper e FGV. Usar 2024–2026 como recorte proposto de inventário, sem assumir que todos os documentos estão disponíveis. FGV deve ser separada por escola/curso e Insper por semestre/aplicação. Expansão nacional e monetização ficam para depois.

O ativo central será o acervo confiável: uma interface pronta não significa um banco pronto. Cada questão real precisa estar ligada à prova, página e gabarito corretos. Classificação por IA e OCR precisam de revisão; autoral não pode se passar por oficial. Links públicos não comprovam autorização de reprodução de enunciados, imagens ou resoluções.

## Fontes iniciais

| Instituição | Diretório oficial |
|---|---|
| Fuvest / USP | https://www.fuvest.br/acervo-vestibular/ |
| Unicamp / Comvest | https://www2.comvest.unicamp.br/vestibulares-anteriores/ |
| Insper | https://www.insper.edu.br/pt/cursos/vestibular/provas-e-gabaritos |
| FGV | https://vestibular.fgv.br/provas-gabaritos |

Fontes localizadas em 31/10/2026. Fuvest retornou 403 na abertura automatizada; diretório Comvest não pôde ser lido; Insper depende de JavaScript; FGV apresentou seletor de cursos. Nenhum PDF foi transcrito ou importado nesta entrega. Esses limites estão documentados no projeto.

Referências de experiência: [Estuda.com](https://estuda.com/banco-de-questoes/), [Repertório ENEM](https://repertorioenem.com.br/), [Poliedro Resolve](https://poliedroresolve.sistemapoliedro.com.br/busca?page=1) e [Anglo Play](https://www.sistemaanglo.com.br/blog/como-funciona-o-anglo-play). Inspiração funcional, com identidade e conteúdo próprios.

## Publicação

Repositório público: https://github.com/felipeortuzal/vestibular-aberto. O pacote contém README, AGENTS.md e workflow GitHub Actions. Após enviar os arquivos, selecione GitHub Actions em Settings → Pages e confira a execução. A URL confirmada do site será registrada em docs/STATUS.md. [Documentação GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).


## Prompt 00 contexto-mestre

```text
Você é o responsável pela implementação do Vestibular Aberto. Trabalhe no repositório existente, lendo AGENTS.md, README.md e docs/STATUS.md antes de decidir mudanças. Leia também PRODUTO.md, DADOS.md, FONTES.md e INGESTAO.md conforme a etapa.

Objetivo: construir uma plataforma pública de estudos com duas experiências integradas: provas completas e banco de questões por instituição → matéria → assunto → subassunto. Recorte inicial: Fuvest/USP, Unicamp, Insper e FGV. Edições de 2024 a 2026 são uma proposta de inventário, sujeita à existência de documentos verificáveis. Separe escola/curso/campus na FGV e semestre/aplicação no Insper. Não trate a USP como uma segunda banca duplicada da Fuvest.

A V0 já tem HTML/CSS/JS, 12 questões autorais de demonstração, quatro diretórios, filtros, correção, favoritas e progresso no navegador. Ela não contém questões oficiais nem provas individualizadas. O validador bloqueia conteúdo oficial até a implementação do contrato e do fluxo de revisão. Não desligue essa proteção para inflar o banco.

Execute apenas a etapa que eu pedir, com mudanças concretas, verificadas e compatíveis com o estado atual. Não recomece o projeto do zero nem migre para framework sem necessidade demonstrada. Não instale serviço pago nem implemente cobrança agora. O nome Vestibular Aberto é provisório.

Use as plataformas Repertório ENEM, Estuda.com, Anglo e Poliedro como referências de experiência. Produza design e textos próprios. Não copie bases, resoluções privadas, marca ou elementos protegidos dessas plataformas. Priorize fontes oficiais para catalogação e registre a situação de uso/republicação de cada documento. Questões autorais nunca recebem instituição, ano ou numeração oficial fictícios.

Preserve enunciados, contexto compartilhado, imagens, fórmulas, alternativas, subitens e origem. Não complete trechos ilegíveis nem gabaritos ausentes com suposições. A classificação e a resolução propostas por IA são rascunhos identificados até revisão. Nunca rotule revisão de IA como humana. Em conflito entre gabarito e cálculo, abra pendência, sem substituir o oficial silenciosamente.

Faça uma única fonte de verdade para cada dado, IDs estáveis e histórico versionado. Não exponha chaves no navegador. O futuro backend não pode depender de GitHub Pages para execução de servidor. Preserve histórico de estudo ao migrar.

Ao concluir, entregue: resultado objetivo, arquivos alterados, comandos/testes com resultado real, contagens verificadas, limitações, commit/URL quando existirem e próximo passo. Atualize docs/STATUS.md. Não diga que publicou se só fez commit ou gerou um ZIP. Se faltar acesso externo, conclua o restante e descreva a ação específica que falta.
```

## Prompt 01 auditoria-v0

```text
Execute a etapa 01: conferir e preparar a V0 existente para continuação e publicação no GitHub.

1. Leia o código e STATUS. Rode npm run validate, npm test e npm run build. Examine os filtros encadeados, busca sem acentos, paginação, feedback, tentativa repetida, favoritas e persistência. Não reescreva funções que já atendem ao pedido.
2. Teste a interface em 360, 768 e 1440 px quando houver navegador disponível. Corrija overflow, foco perdido, textos truncados, controles sem label e contraste insuficiente. Verifique a navegação por teclado. Documente testes impossíveis.
3. Confirme estados: instituição sem questões, matéria sem exemplos, zero resultados, nenhum progresso, armazenamento bloqueado e importação inválida. Separar tentativa de estudo de questão única nas estatísticas. Não apagar progresso existente para corrigir layout.
4. Mostre claramente as 12 questões autorais e os quatro diretórios. Nunca chame diretório de prova já importada. Não acrescente gabaritos ou questões reais nesta etapa.
5. Verifique se o repositório vestibular-aberto na conta escolhida já existe antes de criar qualquer coisa. Se houver acesso e autorização de publicação, envie os arquivos para a branch correta e habilite o GitHub Pages via Actions. Se o usuário já criou outro nome, use o repositório indicado. Não substituir trabalhos existentes. Se houver bloqueio de login/criação, preserve os arquivos e dê instrução pontual.
6. Confira o workflow remoto e a página publicada. O build local não comprova deploy. Registre URL efetiva, commit e eventuais pendências no STATUS.

Aceite: nenhuma falha conhecida no fluxo de demonstração, testes passando, README reproduzível e situação de publicação descrita honestamente. Entregue o diff e um resumo. O próximo passo é 02; não comece a importar PDFs nesta execução.
```

## Prompt 02 contrato-e-taxonomia

```text
Execute a etapa 02: preparar os dados para provas oficiais sem publicar conteúdo real ainda.

Parta de docs/DADOS.md e da taxonomia existente. Crie esquemas versionados e validação executável para instituições, processos/provas, documentos, grupos de questões, questões, gabaritos, resoluções, classificações e eventos de revisão. Separe o esquema de trabalho, que aceita desconhecidos/pendências, do critério de publicação, que exige informação completa. Não transforme sugestões da especificação em fatos inventados.

Inclua edição de ingresso versus data de aplicação, semestre, fase/dia, modelo do caderno, cursos/escolas/campi, numeração original textual, questões compartilhadas e subitens. Represente texto, fórmula, imagem e tabela por blocos. O campo de formato precisa acomodar objetiva, discursiva, numérica, somatória e redação, mesmo que o renderer inicial só publique objetivas. Trate gabarito preliminar, final, retificado, anulado e ausente separadamente.

Revise a taxonomia de Matemática e as demais matérias sem trocar IDs por motivos cosméticos. Uma classificação tem caminho principal válido e tags secundárias para interdisciplinaridade. Crie migração se precisar alterar estrutura. Dificuldade deve aceitar desconhecido e distinguir editorial/empírica.

Implemente testes que rejeitem: alternativa correta inexistente; questão oficial sem prova/documento de origem; caminhos de taxonomia inválidos; IDs duplicados; gabarito ligado ao caderno errado; conteúdo bloqueado aparecendo no export público; item anulado entrando como erro do estudante. Adicione testes positivos com fixtures claramente sintéticas e excluídas do site.

Preserve o seed autoral e o progresso V0. Não remova a trava de publicação oficial sem substituí-la por critérios equivalentes. Prepare adaptadores compatíveis, schema_version e export que selecione somente o material elegível.

Aceite: modelos, migrações necessárias, exemplos sintéticos, validação e testes demonstram o contrato; a interface V0 continua funcionando; nenhum conteúdo oficial foi publicado. Atualize docs/DADOS.md e STATUS.
```

## Prompt 03 inventario-oficial

```text
Execute a etapa 03: inventariar os documentos oficiais. Ainda não extraia o banco inteiro.

Recorte inicial: edições de 2024 a 2026 de Fuvest, Unicamp, Insper e FGV. Comece pelas entradas de docs/FONTES.md. Na FGV, priorize EAESP/EESP e provas unificadas aplicáveis, respeitando o que os documentos comprovarem. No Insper, preserve semestre e aplicação; simulado não é prova aplicada.

Produza uma matriz com: instituição, escola/curso/campus, edição, data de aplicação quando verificada, semestre, fase, dia, caderno, modalidade, documento (prova/gabarito/grade/retificação), URL oficial, página de origem, data de consulta, acesso, situação dos direitos, evidência e pendências. Verifique os links; não adivinhe URLs a partir de nomes. Não preencha datas ou totais sem evidência. Campo desconhecido deve ficar null.

Diferencie: localizado no resultado de busca, página aberta, arquivo obtido, arquivo identificado e conteúdo revisado. Não marque um PDF como conferido só porque o link abre. Vincule gabaritos retificados às versões anteriores. Se o mesmo caderno serve a vários cursos, modele um documento com vínculos, sem duplicar questões.

Registre quando o site exigir JavaScript, login ou apresentar bloqueio. Não contorne proteções, não use APIs privadas e não tire conteúdo de cursinhos para suprir silenciosamente a fonte oficial. Continue as demais instituições e entregue a lacuna de forma explícita.

Investigue termos e permissões referentes à reprodução do conteúdo; acesso público sozinho não resolve essa questão. Se não houver base documentada para republicar, use link_only e mantenha o trabalho de metadados. Não envie pedidos de autorização a terceiros sem instrução do usuário.

Aceite: inventário legível e JSON/CSV consistente, fontes e limites registrados, duplicidades identificadas e um lote piloto recomendado de 5–10 questões de Matemática da prova mais bem documentada. Não alegue cobertura completa nem invente resultados para atingir um número.
```

## Prompt 04 extracao-piloto

```text
Execute a etapa 04 em um único lote piloto, usando o inventário da etapa 03. Selecione 5–10 questões de Matemática de uma prova cujo documento e gabarito estejam disponíveis e cujo uso nesta etapa esteja estabelecido. Informe a escolha e siga o trabalho. Quando não houver documentação suficiente para usar o conteúdo, conclua os manifestos e descreva a lacuna; não invente questões oficiais.

Implemente o pipeline mínimo reproduzível: download permitido com timeout e limite; verificação de MIME/PDF; SHA-256; manifesto; extração; staging; relatório de erro por página. Não inclua documentos sem permissão de distribuição num repositório público. Preserve os arquivos originais permitidos sem alteração.

Tente extrair a camada textual. Use OCR apenas onde necessário e registre método e versão. Separe colunas, cabeçalhos, rodapés, contextos compartilhados e as questões. Preserve numeração, alternativas e ordem, unidades, sinais, expoentes, equações, gráficos e legendas. Mantenha recortes das figuras com página e coordenadas; não substitua diagramas de prova por imagem gerada.

Vincule cada item ao documento, hash e página. Se um trecho estiver ilegível, grave a dúvida e bloqueie publicação; nunca faça uma reconstrução plausível passar por transcrição fiel. Não parafraseie enunciado durante a extração. Uma resolução deve ser armazenada separadamente do conteúdo da prova.

Concilie o gabarito com edição, fase e modelo exatos. Se for preliminar, mantenha esse estado. Identifique questões anuladas e divergências. Não aplique uma letra do caderno A ao caderno B sem mapa verificado.

Aceite: lote em staging validado pelo esquema, manifesto e relatório, indicação de elementos que precisam de inspeção visual, nenhuma publicação automática. Compare visualmente os 5–10 itens com suas páginas e registre quem ou qual sistema fez a comparação. Se não houver revisão humana, não afirme que houve. Próxima etapa: classificação e revisão.
```

## Prompt 05 classificacao-e-revisao

```text
Execute a etapa 05 sobre o lote de staging indicado em STATUS. Não importe novos PDFs nesta etapa.

Para cada questão, proponha um caminho da taxonomia: matéria, assunto e subassunto. Considere o conhecimento exigido para resolver, e não apenas palavras do enunciado. Exemplo: um problema contextualizado com população pode ser Matemática → Funções, e não necessariamente Geografia. Use tags secundárias para conhecimentos adicionais. Registre justificativa curta, confiança editorial e versão da taxonomia. Não crie um subassunto quase idêntico só por variação de nome.

Demonstre os casos ambíguos em tabela: ID, classificação proposta, alternativas plausíveis e dúvida. Revise também origem, página, conteúdo, imagens, fórmulas, número e correspondência do gabarito. Conteúdo truncado não pode ser liberado porque a classificação ficou boa.

Escreva resoluções originais apenas para os itens elegíveis e com entendimento suficiente. Marque a autoria e o estado de revisão. Explique o raciocínio e a alternativa, não apenas repita o gabarito. Se o cálculo divergir do gabarito oficial, abra uma pendência e confira edição, modelo e retificação antes de propor correção. Não copie soluções de Anglo, Poliedro, Repertório ou Estuda.com.

Não use “fácil/médio/difícil” como fato empírico. Se oferecer dificuldade editorial, identifique o caráter estimado e a justificativa; permita null. Não invente tempo médio de resolução nem taxa de acerto.

Aceite: cada item tem checklist de conteúdo, gabarito, origem, classificação e direitos; status de revisão é real; dúvidas críticas ficam bloqueadas. Entregue relatório para revisão de Felipe com os itens que precisam de decisão humana. Não trate a própria saída de IA como aprovação humana. Os itens aprovados e autorizados ficam prontos para o prompt 06; os restantes continuam em staging.
```

## Prompt 06 banco-real-e-materiais

```text
Execute a etapa 06: incorporar ao site somente o lote elegível que passou pelos prompts 02–05. Não complete a quantidade desejada com conteúdo inventado. Preserve o restante em staging.

Atualize o banco para renderizar metadados reais, blocos de texto/matemática/imagem/tabela, alternativas e fonte com página. Identifique demonstração, prova oficial, simulado e resolução editorial separadamente. Remova quaisquer labels estáticos da V0 que chamariam uma questão real de autoral. Demonstrações podem ficar numa área própria, excluídas dos totais oficiais.

Acrescente filtros de instituição, edição, semestre quando aplicável, fase, escola/curso, matéria, assunto e subassunto. As opções devem vir dos dados. Filtros se combinam, respeitam a hierarquia, têm contagem e estado vazio; a troca de matéria limpa os descendentes. Não esconda a diferença entre instituição e banca organizadora.

Em Provas completas, crie registros de provas individualizadas com links conferidos para caderno, gabarito final/retificado e grade de correção quando houver. Mostre quais documentos existem e a cobertura de questões individualizadas. Diretórios institucionais continuam como atalhos, sem inflar a quantidade de provas. Disponibilize PDF local somente quando o uso estiver autorizado; senão, direcione à fonte.

Na correção, preserve versão do gabarito e trate anuladas/sem resposta final fora da taxa de acerto. Discursivas não podem receber correção binária automática sem suporte real; mostre a rubrica autorizada e a limitação. Aplique saneamento a conteúdo externo e forneça alternativa legível às imagens/fórmulas.

Aceite: uma questão publicável pode ser encontrada pelo conteúdo e aberta no contexto da prova; fonte/página e gabarito conferem; contadores refletem o banco; progresso antigo permanece; pipeline não publica pendências. Rode testes e navegação em desktop/celular. Publique no destino já autorizado e entregue commit, URL confirmada, contagens por instituição e lacunas.
```

## Prompt 07 sessoes-e-progresso

```text
Execute a etapa 07 depois de haver lote real publicado. Implemente listas, sessões e caderno de erros, mantendo o acervo e a interface existentes.

Permita criar lista a partir dos filtros, escolher uma quantidade disponível e salvar ordem, questões e versões. Não repita itens para alcançar o tamanho solicitado: informe o total disponível. Ofereça modo estudo com resposta imediata e modo simulado com correção ao finalizar. Não exponha a resolução antes da finalização no simulado. Um prazo deve se basear em timestamps, não em contagem frágil de setInterval; recuperar a sessão depois de recarregar precisa preservar tempo e escolhas.

O caderno de erros usa a última tentativa de estudo conforme uma regra explícita. Mostre também histórico sem contar uma mesma questão como várias questões distintas. Separe omissões, anuladas, itens sem gabarito e acertos/erros; defina denominadores. Dê ao estudante a opção de revisar uma questão errada sem apagar sua tentativa anterior.

No painel, apresente dados por matéria e assunto, número de questões e tentativas. Não chame porcentagem simples de TRI nem prometa probabilidade de aprovação. Pequenas amostras devem ter tamanho visível.

Inclua exportação/importação das novas entidades, migração do progresso V0, tolerância a storage indisponível, interrupção no meio de sessão e dados inválidos. Evite guardar dados pessoais desnecessários. Continuar sem conta é permitido.

Aceite: sessão retomável, correção com gabarito/versão corretos, favorita preservada, progresso sem duplicação, lista pequena tratada corretamente e estados de finalização claros. Teste recuperar página, finalizar com itens em branco e revisar uma questão cujo gabarito foi retificado. Publique e registre limitações reais.
```

## Prompt 08 escala-e-editorial

```text
Execute a etapa 08: tornar a entrada de novos lotes repetível e preparar um acervo maior.

Meça tamanho de download, tempo de carregamento e filtragem com os dados atuais. Para um ensaio de escala, use fixtures sintéticas identificadas e excluídas da publicação; não acrescente milhares de falsas questões oficiais. Particione conteúdo por instituição/edição/prova e use índice leve. Carregue apenas o necessário. Mantenha paginação, cancelamento de buscas e estados de erro; não baixe todo o corpus na home.

Implemente uma ferramenta editorial local ou protegida para importar staging, validar, comparar com a origem, corrigir metadados e registrar revisão. Ela não deve ter poderes de administração públicos em um site estático. Não coloque tokens de GitHub no cliente. No estágio sem backend, a publicação pode continuar por arquivo/commit revisado.

Adicione relatórios de cobertura por instituição/edição: documentos localizados, esperados quando verificados, itens extraídos, revisados, publicados e bloqueados. Mostre o denominador e o intervalo de cobertura antes de exibir “assuntos que mais caem”. Sem prova de completude, chamar de frequência no acervo disponível.

Automatize deduplicação candidata, checagem de integridade e detecção de alteração de documentos por hash. Não fundir textos parecidos silenciosamente. Uma retificação abre nova revisão e preserva histórico. Planeje backup dos dados e recuperação de uma versão anterior.

Aceite: repetir um lote não duplica entidades; export público não contém staging; busca funciona com carregamento parcial; números de cobertura se reconciliam; um erro de download não derruba todas as instituições. Registre medições e limites, sem prometer escala que não foi testada. Expanda o acervo real por lotes 04–06, primeiro nos quatro vestibulares prioritários.
```

## Prompt 09 contas-e-backend

```text
Execute esta etapa somente quando o usuário pedir contas/sincronização ou quando STATUS registrar essa decisão. Antes disso, encerre explicando a dependência e continue apenas melhorias independentes já autorizadas.

Prepare uma decisão técnica curta para dados relacionais, autenticação, arquivos e API; compare custo, limites, portabilidade e operação com documentação oficial atual. Não crie assinaturas pagas nem migre o projeto inteiro antes de escolher o provedor adequado. GitHub Pages continuará servindo HTML estático se essa for a hospedagem; servidor, banco e segredos precisam de ambiente próprio.

Com a decisão autorizada, modele usuários, tentativas, favoritas, listas, sessões e papéis editor/admin. Implemente autenticação, autorização no servidor por registro, limitação de requisições, validação de entrada e proteção dos endpoints administrativos. Não basta esconder o botão ou confiar no userId enviado pelo cliente. Chaves de serviço ficam exclusivamente no servidor.

Migre o progresso local de forma opt-in, com deduplicação e preview das contagens; não envie dados de um dispositivo compartilhado silenciosamente. Ofereça exportação e exclusão de conta/progresso. Colete o mínimo e examine os requisitos de privacidade aplicáveis ao público estudantil, inclusive menores, com apoio qualificado antes do lançamento público. Isso não deve virar coleta excessiva de idade ou documento.

Teste que dois usuários não leem nem alteram dados um do outro; visitante não acessa administração; sessão expirada é tratada; falha de rede não perde uma resposta; reenvio não duplica tentativa. Faça backup e teste recuperação. Não adicione cobrança nesta etapa.

Aceite: sincronização funciona entre dispositivos, isolamento é verificado, migração é reversível, não há segredo no bundle, custos/limites e procedimentos estão documentados. Entregue ambientes e URL efetivos, sem expor credenciais.
```

## Prompt 10 revisao-de-lancamento

```text
Execute a etapa 10: auditoria do estado real antes de convidar estudantes. Leia todas as etapas concluídas no STATUS e revise a aplicação final, sem presumir que funcionalidades planejadas foram entregues.

Verifique os fluxos: encontrar questão, filtrar até subassunto, abrir prova completa, responder, conferir explicação, salvar, revisar erro e retomar sessão. Se houver contas, verifique login, sincronização, exportação e exclusão. Teste mobile, teclado, foco, contraste, fórmulas, imagens, links e estados vazios/erro. Corrija bugs concretos dentro do escopo.

Audite uma amostra representativa de cada instituição e revise 100% das questões do lote piloto. Confira origem/página, gabarito/retificação, curso/fase/caderno, classificação e situação dos direitos. Conteúdo com pendência crítica sai da publicação, preservando histórico. Diferencie inspeção automatizada, revisão por IA e revisão humana.

Confira proteção de segredos, dependências e exposição de endpoints. No backend, repita testes de isolamento e backup. Na versão estática, confirme que arquivos de staging, brutos e documentos internos não vão para dist. O deploy precisa apontar ao commit validado, sem alterações entre teste e publicação.

Produza um relatório curto com: o que funciona; tamanho e cobertura real do acervo; limitações; bugs corrigidos; testes executados; riscos concretos pendentes; custo conhecido; passos de recuperação; e critério de go/no-go para a primeira turma. Não declare “todos os vestibulares” ou “100% completo” sem evidência.

Monetização continua fora do escopo técnico desta auditoria. Sugira, no máximo, hipóteses para validar depois: sincronização, revisão programada, relatórios ou trilhas, preservando a proposta do banco público. Não implemente checkout, preços, publicidade ou renovação automática sem novo pedido.

Aceite: nenhuma falha crítica conhecida ocultada, relatório honesto, release identificada e deploy verificado quando autorizado. Entregue o próximo passo mais útil para o usuário com base no produto real.
```

## Como pedir a revisão ao Astra

Envie o resultado do Sol 6 com o diff, relatório de testes, URL/screenshot e pendências. Use:

> Confira se esta entrega atende à etapa solicitada. Priorize problemas de origem, gabarito, filtros e persistência. Crie um prompt de correção limitado às falhas encontradas e diga se podemos avançar. Não proponha reescrever tudo sem necessidade.

## Próximo passo concreto

Rodar o prompt 01 sobre o repositório existente. Depois, implementar o contrato de dados e inventariar um primeiro lote verificável. O primeiro marco de acervo sugerido é até 20 questões reais revisadas, idealmente cobrindo as quatro instituições quando fontes e condições de uso permitirem.
