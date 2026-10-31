# Como usar os prompts

O Astra organiza decisões e revisa resultados. O Sol 6 implementa a etapa delimitada no repositório. Isso não depende de uma suposta diferença fixa de capacidade: o benefício é manter escopo, evidência e continuidade.

1. Extraia o projeto e disponibilize o repositório ao ambiente de implementação.
2. Cole o prompt 00 no começo de uma nova sessão, ou peça a leitura direta do arquivo.
3. Envie só o prompt da etapa atual. Não cole os 11 de uma vez.
4. Receba código, testes, commit e STATUS atualizado. Confira o resultado no site.
5. Traga dúvidas, screenshots, diff e relatório para a revisão antes de avançar.

| Ordem | Arquivo | Resultado esperado |
|---|---|---|
| 00 | contexto-mestre | Regras e contexto da sessão |
| 01 | auditoria-v0 | Base atual conferida e GitHub/Pages publicados quando acessíveis |
| 02 | contrato-e-taxonomia | Esquemas, estados e testes de dados reais |
| 03 | inventario-oficial | Matriz de provas/documentos sem conteúdo inventado |
| 04 | extracao-piloto | Um lote de 5–10 questões em staging rastreável |
| 05 | classificacao-e-revisao | Classificação e revisão editorial do lote |
| 06 | banco-real-e-materiais | Publicação do lote elegível e provas individualizadas |
| 07 | sessoes-e-progresso | Listas, simulado e caderno de erros |
| 08 | escala-e-editorial | Particionamento, importação repetível e cobertura |
| 09 | contas-e-backend | Sincronização quando necessária; serviço escolhido conscientemente |
| 10 | revisao-de-lancamento | Qualidade, recuperação e prontidão de lançamento |

Repita 04–06 para cada lote; não rode 09 antes de haver motivo concreto para contas. Meta inicial sugerida: 20 questões reais revisadas cobrindo as quatro instituições quando viável, seguida de 100 com qualidade equivalente. Quantidade é meta, nunca evidência de que já existe conteúdo.

## Pedido rápido para uma sessão

“Leia AGENTS.md, docs/STATUS.md e prompts/00-contexto-mestre.md. Execute apenas prompts/01-auditoria-v0.md. Faça as alterações, valide e atualize o status. Se houver um bloqueio externo, conclua o restante e descreva exatamente o que falta.”

## Pedido de revisão ao Astra

“Esta foi a entrega do Sol 6 para a etapa [número]. Confira se o pedido e os critérios de aceite foram cumpridos. Analise o diff, o relatório de testes e a tela. Dê prioridade a erros de dados, gabarito, filtros e perda de progresso. Produza um prompt de correção limitado às falhas encontradas. Não mande reescrever tudo sem necessidade.”
