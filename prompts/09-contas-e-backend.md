Execute esta etapa somente quando o usuário pedir contas/sincronização ou quando STATUS registrar essa decisão. Antes disso, encerre explicando a dependência e continue apenas melhorias independentes já autorizadas.

Prepare uma decisão técnica curta para dados relacionais, autenticação, arquivos e API; compare custo, limites, portabilidade e operação com documentação oficial atual. Não crie assinaturas pagas nem migre o projeto inteiro antes de escolher o provedor adequado. GitHub Pages continuará servindo HTML estático se essa for a hospedagem; servidor, banco e segredos precisam de ambiente próprio.

Com a decisão autorizada, modele usuários, tentativas, favoritas, listas, sessões e papéis editor/admin. Implemente autenticação, autorização no servidor por registro, limitação de requisições, validação de entrada e proteção dos endpoints administrativos. Não basta esconder o botão ou confiar no userId enviado pelo cliente. Chaves de serviço ficam exclusivamente no servidor.

Migre o progresso local de forma opt-in, com deduplicação e preview das contagens; não envie dados de um dispositivo compartilhado silenciosamente. Ofereça exportação e exclusão de conta/progresso. Colete o mínimo e examine os requisitos de privacidade aplicáveis ao público estudantil, inclusive menores, com apoio qualificado antes do lançamento público. Isso não deve virar coleta excessiva de idade ou documento.

Teste que dois usuários não leem nem alteram dados um do outro; visitante não acessa administração; sessão expirada é tratada; falha de rede não perde uma resposta; reenvio não duplica tentativa. Faça backup e teste recuperação. Não adicione cobrança nesta etapa.

Aceite: sincronização funciona entre dispositivos, isolamento é verificado, migração é reversível, não há segredo no bundle, custos/limites e procedimentos estão documentados. Entregue ambientes e URL efetivos, sem expor credenciais.
