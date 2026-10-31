Execute a etapa 07 depois de haver lote real publicado. Implemente listas, sessões e caderno de erros, mantendo o acervo e a interface existentes.

Permita criar lista a partir dos filtros, escolher uma quantidade disponível e salvar ordem, questões e versões. Não repita itens para alcançar o tamanho solicitado: informe o total disponível. Ofereça modo estudo com resposta imediata e modo simulado com correção ao finalizar. Não exponha a resolução antes da finalização no simulado. Um prazo deve se basear em timestamps, não em contagem frágil de setInterval; recuperar a sessão depois de recarregar precisa preservar tempo e escolhas.

O caderno de erros usa a última tentativa de estudo conforme uma regra explícita. Mostre também histórico sem contar uma mesma questão como várias questões distintas. Separe omissões, anuladas, itens sem gabarito e acertos/erros; defina denominadores. Dê ao estudante a opção de revisar uma questão errada sem apagar sua tentativa anterior.

No painel, apresente dados por matéria e assunto, número de questões e tentativas. Não chame porcentagem simples de TRI nem prometa probabilidade de aprovação. Pequenas amostras devem ter tamanho visível.

Inclua exportação/importação das novas entidades, migração do progresso V0, tolerância a storage indisponível, interrupção no meio de sessão e dados inválidos. Evite guardar dados pessoais desnecessários. Continuar sem conta é permitido.

Aceite: sessão retomável, correção com gabarito/versão corretos, favorita preservada, progresso sem duplicação, lista pequena tratada corretamente e estados de finalização claros. Teste recuperar página, finalizar com itens em branco e revisar uma questão cujo gabarito foi retificado. Publique e registre limitações reais.
