# Estado do projeto — 31/10/2026

## Etapa 01 — auditoria da V0 concluída

A V0.1 continua em HTML/CSS/JS puro, sem alteração de arquitetura nem de dados oficiais. Corrigida a perda de foco do teclado após paginação, remoção de favorita em Favoritas e registro que elimina a questão pelo filtro ativo. O título de resultados pode receber foco programático. Contraste de pequenos textos/badges foi reforçado e quebras responsivas receberam proteção contra overflow. O contador da home agora diz "4 diretórios oficiais", sem confundi-los com provas importadas. Os arquivos de JS/CSS receberam atualização de cache no HTML.

A interface mantém filtros por instituição → matéria → assunto → subassunto, busca sem acentos, paginação, feedback, tentativas repetidas, favoritas, histórico local e exportação/importação. A estatística conta **questões distintas pela última tentativa**; tentativas totais permanecem um indicador separado. O teste de uma questão respondida duas vezes confirma **1 respondida, 2 tentativas** e 100% de acerto pela última resposta, sem apagar o erro anterior.

## Contagens verificadas

- **12 questões autorais** de demonstração, sem instituição, edição ou número oficial inventado.
- **4 diretórios oficiais** (Fuvest/USP, Unicamp/Comvest, Insper e FGV), que são links de consulta, não provas importadas.
- **0 questões oficiais**, **0 provas individualizadas** em `data/exams.json`.
- Taxonomia proposta: **12 matérias, 45 assuntos, 122 subassuntos**.
- **9 testes unitários** passando; um roteiro adicional de smoke test no navegador real.

## Verificação reproduzível

Na CI do GitHub Actions, sobre o repositório verdadeiro (sem instalar dependências npm), passaram:
- `npm run validate`: 12 questões autorais, 122 subassuntos, 4 diretórios; bloqueio de conteúdo oficial preservado.
- `npm test`: **9 aprovados, 0 reprovados**; estados vazios, filtros, última tentativa, favoritas e importação inválida.
- `npm run build`: pasta `dist/` gerada.
- `npm run test:browser`: Chrome headless via protocolo DevTools; busca, filtro oficial vazio, matéria sem exemplo, paginação, navegação por Tab, foco após ações, resposta errada/correta, repetir, favorita, desempenho, persistência após recarregar, importação inválida e armazenamento bloqueado com posterior recuperação.

Layout testado em **360, 768 e 1440 px** por navegador real, sem overflow horizontal. Foram geradas capturas reais das três larguras, anexadas como artefato `screenshots-v0` da CI; as capturas também foram inspecionadas visualmente, sem cortes ou sobreposições evidentes. Não houve teste em dispositivos físicos, nem auditoria completa com leitor de tela.

CI de auditoria aprovada: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41252903781 .
Capturas: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41252903781#artifacts .

## GitHub e publicação

Repositório existente reutilizado: https://github.com/felipeortuzal/vestibular-aberto .
PR de auditoria integrado à `main`: https://github.com/felipeortuzal/vestibular-aberto/pull/1 .
Commit de integração funcional: `e126522748438b863ae1bd166327d22790810ae7`.
CI com **deploy do GitHub Pages concluído com sucesso** após o merge: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41253057882 .
URL pública existente: https://felipeortuzal.github.io/vestibular-aberto/ .

O clone local via `git` não foi possível porque o ambiente de execução não resolvia `github.com` (DNS). As mudanças foram realizadas com acesso autenticado ao repositório e os quatro comandos acima executados **na CI**. GitHub Pages continua exclusivamente estático; não existe backend. O primeiro deploy de criação, preservado como histórico, foi o run https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41251875933 (commit `94560b4`).

## Limitações e pendências

Não há contas, banco remoto, OCR, ingestão oficial, sincronização, painel editorial, simulados ou cobrança. Não houve importação de PDF nem mudança nos direitos de uso; consulte `docs/FONTES.md`. O validador continua rejeitando questões oficiais fora do contrato/revisão das etapas posteriores. Não testar ou presumir que qualquer diretório equivale à autorização de republicação.

Os GitHub Actions ainda podem emitir avisos de transição do runtime Node 20 e da imagem de runner; são avisos não bloqueantes nas execuções acima. Teste de acessibilidade com leitor de tela e teste em dispositivo físico permanecem como verificação manual futura.

## Próximo passo — etapa 02

Executar `prompts/02-contrato-e-taxonomia.md`: contratos e esquemas versionados, estados de revisão, integridade referencial e validação de dados oficiais em staging, **sem desativar o bloqueio de publicação e sem importar conteúdo real antes da revisão de origem e direitos**. Não iniciar a etapa 03 nesta execução.
