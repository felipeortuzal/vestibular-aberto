# Etapa 04 — lote piloto Unicamp 2026, 1ª fase

**Estado:** PDF obtido e processado no GitHub Actions; 5/5 questões têm extrações candidatas em staging temporário. Revisão humana: 0/5; questões publicadas: 0. Data da revisão desta etapa: 01/11/2026.

## Fonte e método

Documento da Comvest: [1ª fase comentada, caderno com marcação Q](https://www.comvest.unicamp.br/wp-content/uploads/2026/06/F1_2026_Prova-Q.pdf), identificado no [acervo oficial](https://www.comvest.unicamp.br/vestibulares-anteriores/1a-fase-2a-fase-comentadas/). O PDF tem **71 páginas** no leitor da fonte. A Comvest informa expressamente que autoriza apenas **reprodução parcial de questões**, com atribuição e sem exclusividade; **não** autoriza a reprodução integral da prova. A autorização não dispensa analisar direitos de textos e imagens de terceiros.

O documento intitula-se “Vestibular Unicamp 2026”, primeira fase; a introdução na página física 2 menciona “vestibular 2025”, discrepância editorial a verificar. A edição 2026 é distinta da data de aplicação (26/10/2025). O nome do PDF e o rodapé indicam “Q”; o vínculo com o **caderno originalmente aplicado** e eventual variante precisa de conferência independente.

O arquivo `pilot/unicamp-2026-math/manifest.json` lista os cinco itens, páginas e **SHA-256 verificado**: `2d1d0d375fb8ee7ea84ebb11350ca30851a5c928db80ed6e2479aeeb1ba23284` (7.882.756 bytes, 71 páginas). O `staging-metadata-v1.json` adere ao contrato editorial V1 e guarda apenas metadados, hash e páginas — sem enunciados ou alternativas. O ambiente local falhou por DNS, mas a CI conseguiu o download e processou os cinco candidatos. Evidência: https://github.com/felipeortuzal/vestibular-aberto/actions/runs/41362067765 . A CI é efêmera; para continuar a revisão em outro computador, execute novamente o pipeline localmente.

## Cinco questões selecionadas

| Questão | Página física no PDF (1-based) | Página impressa | Região de leitura | Alternativa no comentário da Comvest | Pendência principal |
| --- | --- | --- | --- | --- | --- |
| **43** | 47 | 46 | esquerda | **A** | conferir cálculo composto, opções e gabarito final do caderno |
| **45** | 48 | 47 | esquerda | **B** | conferir sinais, operadores e graus dos polinômios |
| **49** | 50 | 49 | esquerda → direita | **B** | texto continua na outra coluna, conferir integridade |
| **51** | 51 | 50 | direita | **C** | conferir inequações, barras de módulo e domínio |
| **52** | 51–52 | 50–51 | direita → esquerda da página seguinte | **B** | enunciado e alternativas atravessam páginas |

As letras acima foram **lidas visualmente** na prova comentada oficial. São **candidatas à reconciliação**, não registros de gabarito final conferido. Por isso, nos registros `answers` do V1, o status ainda é `missing`, valor `null`, `verifiedBy=null`. Não há respostas ou resoluções incorporadas ao site público.

## Pipeline mínimo reproduzível

O script `scripts/ingest_pilot.py` usa HTTPS, timeout de 25 segundos e limite de 25 MiB, verifica MIME e assinatura PDF, gera SHA-256 do **arquivo original** e verifica a contagem de páginas. Não muda os bytes do original. Usa PyMuPDF para extrair **camada textual nativa**, sem OCR automático, recortando cada página em colunas e mantendo numeração, texto e alternativas candidatas para conferência. As prévias de página vêm do próprio PDF, não de imagens geradas artificialmente. Todos os arquivos contendo conteúdo da prova ficam em `raw/` e `staging/`, ignorados pelo Git e excluídos do build estático.

Com Python 3, depois de instalar as dependências de desenvolvimento:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/ingest_pilot.py --mode probe
python3 scripts/ingest_pilot.py --mode extract
# Ou, com um arquivo oficial obtido manualmente:
python3 scripts/ingest_pilot.py --mode extract --pdf "/caminho/prova-oficial.pdf"
npm run test:pilot
```

O modo `probe` informa apenas tamanho, páginas e hash. O modo `extract` produz **localmente** `staging/unicamp-2026-math/bundle-v1.json` e `candidates.json` (com texto integral candidato), além de imagens de comparação da página e `page-report.json` com método de extração por página e indicação de inspeção pendente. O algoritmo rejeita segmentos com menos de quatro alternativas ou sem limites claros; não cria textos, respostas ou diagramas ausentes. A classificação fica para a etapa 05. Se houver fórmula ou símbolo incompleto, a questão permanece bloqueada.

O build de produção **não** executa extração nem inclui `pilot/`, `raw/` ou `staging/`. Apenas os metadados sem enunciado são versionados em `pilot/`. Reproduzir a prova inteira em GitHub Pages é proibido nesta etapa.

## Checklist de qualidade e limitações

- [x] Origem Comvest e link do PDF localizados.
- [x] Cinco números, páginas e letras do comentário comparados **visualmente por IA** com as páginas do PDF.
- [x] Contrato V1 para cinco itens com origem e páginas explícitas, sem alegar revisão humana.
- [x] Autorização de uso delimitada à reprodução parcial; nenhum PDF republicado.
- [x] Hash SHA-256 e tamanho obtidos dos bytes capturados na CI, conferidos em duas execuções.
- [x] Extração nativa automatizada de candidatos para as 5 questões na CI; textos e capturas mantidos fora do repositório.
- [ ] Comparação **integral** do texto extraído com cada página — fórmulas, expoentes, quebras de coluna, unidades, alternativas e contexto.
- [ ] Documento independente de **gabarito final** do mesmo caderno/modelo confrontado; anulações e retificações verificadas.
- [ ] Identificação de créditos e permissão de eventuais figuras/textos de terceiros.
- [ ] Revisão humana dos cinco itens, classificação e explicações editoriais.
- [ ] Aprovação de publicação — fora do escopo da etapa 04.

**Próxima etapa:** 05, classificação e revisão, somente após completar os controles acima. Não reduzir as pendências para preencher a meta de cinco questões publicadas.
