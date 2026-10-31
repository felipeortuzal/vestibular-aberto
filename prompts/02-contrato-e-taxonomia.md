Execute a etapa 02: preparar os dados para provas oficiais sem publicar conteúdo real ainda.

Parta de docs/DADOS.md e da taxonomia existente. Crie esquemas versionados e validação executável para instituições, processos/provas, documentos, grupos de questões, questões, gabaritos, resoluções, classificações e eventos de revisão. Separe o esquema de trabalho, que aceita desconhecidos/pendências, do critério de publicação, que exige informação completa. Não transforme sugestões da especificação em fatos inventados.

Inclua edição de ingresso versus data de aplicação, semestre, fase/dia, modelo do caderno, cursos/escolas/campi, numeração original textual, questões compartilhadas e subitens. Represente texto, fórmula, imagem e tabela por blocos. O campo de formato precisa acomodar objetiva, discursiva, numérica, somatória e redação, mesmo que o renderer inicial só publique objetivas. Trate gabarito preliminar, final, retificado, anulado e ausente separadamente.

Revise a taxonomia de Matemática e as demais matérias sem trocar IDs por motivos cosméticos. Uma classificação tem caminho principal válido e tags secundárias para interdisciplinaridade. Crie migração se precisar alterar estrutura. Dificuldade deve aceitar desconhecido e distinguir editorial/empírica.

Implemente testes que rejeitem: alternativa correta inexistente; questão oficial sem prova/documento de origem; caminhos de taxonomia inválidos; IDs duplicados; gabarito ligado ao caderno errado; conteúdo bloqueado aparecendo no export público; item anulado entrando como erro do estudante. Adicione testes positivos com fixtures claramente sintéticas e excluídas do site.

Preserve o seed autoral e o progresso V0. Não remova a trava de publicação oficial sem substituí-la por critérios equivalentes. Prepare adaptadores compatíveis, schema_version e export que selecione somente o material elegível.

Aceite: modelos, migrações necessárias, exemplos sintéticos, validação e testes demonstram o contrato; a interface V0 continua funcionando; nenhum conteúdo oficial foi publicado. Atualize docs/DADOS.md e STATUS.
