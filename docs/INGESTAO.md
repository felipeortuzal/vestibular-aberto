# Como transformar provas em um banco confiável

Este é o processo especificado para os próximos prompts, não um importador já implementado.

1. **Inventariar.** Registrar instituição, escola/curso, edição, semestre, modalidade, fase, dia, caderno, documentos e acessibilidade. Não montar URLs por padrão adivinhado.
2. **Resolver o uso do conteúdo.** Registrar termos/licença/autorização e se a operação permitida é apenas link, extração interna ou republicação. A revisão cobre textos e imagens de terceiros presentes nas provas. Manter pendências sem impedir o restante do projeto.
3. **Capturar documentos permitidos.** Download com timeout, limite de tamanho, verificação do tipo, hash SHA-256 e manifesto. Respeitar restrições e limites do site. Nada de bypass de login/CAPTCHA.
4. **Extrair.** Texto nativo primeiro; OCR apenas nas páginas que precisarem. Registrar o método por página. PDFs com colunas, fórmulas, diagramas e contextos compartilhados exigem reconstrução cuidadosa.
5. **Separar.** Reconhecer início/fim de cada questão, subitens e alternativas. Preservar a numeração, contexto e página. Um lote inicial de 5–10 itens facilita comparação visual.
6. **Conciliar respostas.** Usar gabarito final/retificado do caderno correspondente. Não confundir letras em diferentes versões de prova. Para discursivas, importar a rubrica oficial quando puder ser usada, sem inventar resposta única.
7. **Classificar.** IA sugere matéria/assunto/subassunto e tags secundárias com justificativa; editor confere. Versão da taxonomia e confiança são registradas.
8. **Revisar conteúdo.** Comparação lado a lado com o PDF: 100% do lote piloto, inclusive símbolos, créditos e imagens. Revisão por uma IA não deve ser rotulada como revisão humana.
9. **Publicar.** Validação de esquema, integridade, direitos, versão do gabarito, imagens e estado editorial. Exportar somente itens aprovados.
10. **Medir e manter.** Contagem por prova: documentos encontrados, questões esperadas (se verificadas), extraídas, revisadas, publicadas e bloqueadas. Atualizações de fonte podem invalidar hashes e abrir nova revisão.

## Artefatos por lote

`manifest.json`, dados de staging, relatório de extração, checklist de revisão, candidatos a duplicata, dúvidas e resumo de publicação. Arquivos brutos e staging não devem ser commitados se a autorização não permitir disponibilizá-los no repositório. Não incluir dados pessoais de candidatos.

## Aceite de uma questão

Identidade estável; contexto completo; alternativas/subitens completos; fórmulas e figuras legíveis; referência exata; resposta compatível com caderno/edição e revisão; classificação coerente; situação de direitos definida; revisão identificada; exibição testada; nenhuma pendência crítica.

## Rotina prática com Felipe

Um lote por vez. O implementador entrega a lista de pendências e um exemplo renderizado; Felipe pode conferir PDFs e classificação com o apoio do Astra. Uma pergunta deve pedir a decisão concreta que falta, por exemplo qual caderno está sendo usado, em vez de pedir autorização genérica para continuar trabalhando.
