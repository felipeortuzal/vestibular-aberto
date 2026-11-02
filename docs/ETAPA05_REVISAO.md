# Etapa 05 — classificação e pré-revisão do piloto Unicamp 2026

**Data:** 02/11/2026. **Escopo:** questões 43, 45, 49, 51 e 52, 1ª fase, prova comentada Q, Unicamp 2026. **Resultado:** 5 classificações propostas por IA, 5 resoluções matemáticas originais em rascunho, 5 checklists, **zero aprovações humanas e zero questões liberadas**. Não foram adicionados novos PDFs nesta etapa.

## Materiais e evidência

- [Comvest — índice das provas comentadas](https://www.comvest.unicamp.br/vestibulares-anteriores/1a-fase-2a-fase-comentadas/): inclui as condições de **reprodução parcial**, não exclusiva, com atribuição. Acesso público não equivale a liberação de uma prova integral.
- [Comvest — prova comentada 2026, modelo Q](https://www.comvest.unicamp.br/wp-content/uploads/2026/06/F1_2026_Prova-Q.pdf): cinco números, páginas, alternativas comentadas e contexto vistos **visualmente por IA**. O documento é o mesmo da etapa 04, não houve nova importação.
- Arquivo de origem: SHA-256 `2d1d0d375fb8ee7ea84ebb11350ca30851a5c928db80ed6e2479aeeb1ba23284`, 71 páginas, 7.882.756 bytes; conferido na execução CI da etapa 04.
- `pilot/unicamp-2026-math/staging-metadata-v1.json`: classificações e resoluções **originais da IA**, sem copiar enunciados ou alternativas.
- `pilot/unicamp-2026-math/review-checklist-v1.json`: um checklist por questão, decisões humanas nulas e pendências rastreáveis.
- `scripts/validate_review.py`: impede confundir classificado por IA com aprovado por humano e bloqueia export e estado de publicação.

**Aviso de qualidade:** o algoritmo da etapa 04 reconheceu quatro alternativas para todos os cinco itens, mas isso **não comprova** a correspondência integral entre texto extraído e PDF. Em especial, a questão 45 tem alternativas em duas colunas; o parser pode misturar valores. A folha de revisão da etapa 05 **não é** evidência de conferência da transcrição com o staging efêmero.

## Propostas de classificação (taxonomia V1, IDs preservados)

| Nº | Caminho primário | Tags secundárias | Confiança da proposta de IA | Alternativas plausíveis / ponto de decisão |
|---|---|---|---:|---|
| **43** | Matemática → Aritmética e proporcionalidade → **Porcentagem** | Matemática financeira → Juros compostos (analogia de crescimento multiplicativo) | 0,96 | O problema usa sucessão de reajustes salariais, **não** juros de um empréstimo; manter Porcentagem como principal? |
| **45** | Matemática → Álgebra → **Polinômios** | — | 0,99 | O ponto determinante são graus e cancelamento de coeficientes; alternativa ampla “Equações” seria imprecisa. |
| **49** | Matemática → Probabilidade → **Eventos simples** | Análise combinatória → Combinações; Permutações e arranjos | 0,94 | O resultado é uma probabilidade, mas resolver requer contar permutações com exatamente dois pontos fixos. Confirmar Probabilidade como principal. |
| **51** | Matemática → Álgebra → **Equações e inequações** | Conjuntos e lógica → Operações com conjuntos | 0,94 | Precisa resolver inequações modulares e interseção de conjuntos; não confundir com problema puramente de números primos. |
| **52** | Matemática → Álgebra → **Sistemas lineares** | — | 0,99 | O desafio é montar duas restrições e resolver um sistema. Não classificar como Geografia/História pelo cenário de videogame. |

**Confiança** é uma avaliação de confiança da **classificação proposta pela IA**, não é taxa de acerto dos candidatos nem probabilidade de aprovação humana. **Dificuldade editorial e empírica:** ambas `null` até avaliação com critério e amostra verificados. Não foram criados assuntos novos ou alterados IDs do catálogo.

## Checagem matemática independente — resoluções originais

As cinco resoluções estão armazenadas como entidades V1 `explanations`, `authorType=ai_draft`, `reviewStatus=needs_review`, `proposedBy.type=ai`, `reviewedBy=null`. Abaixo estão os **resultados matemáticos independentes**, sem copiar a redação da banca:

| Nº | Resultado calculado de forma independente | Alternativa indicada no comentário oficial | Situação |
|---|---|---|---|
| 43 | Total da proposta fixa: `54S`. Total das progressões anuais: `52,416S`. Diferença relativa à segunda ≈ `3,02%`. | **A** | Coincide; final independente do caderno ainda não reconciliado. |
| 45 | Graus da soma e produto implicam `deg p = deg q = 4`; termos líderes cancelam na soma e somam na diferença. `deg(p−q)=4`. | **B** | Coincide; quatro alternativas lado a lado exigem revisar extração. |
| 49 | `5!=120` permutações possíveis; `C(5,2)×!3=10×2=20` favoráveis. `20/120=1/6`. | **B** | Coincide; conferir quebra entre colunas. |
| 51 | Domínio natural após interseção: `[2,3] ∪ [7,20]`. Primos: `2,3,7,11,13,17,19` (sete). | **C** | Coincide; símbolo `ℕ` desapareceu na extração de texto da fonte e exige correção visual. |
| 52 | `x+y=100`; `70x+20y=30x+80y`; `x=60, y=40`. | **B** | Coincide; confrontar continuação de duas páginas. |

**Importante:** as letras vistas no PDF **comentado da Comvest** e os resultados matemáticos são duas verificações do entendimento, mas ainda falta anexar e conferir o **gabarito final oficial do modelo Q/X** (e eventual histórico de retificação) antes de gravar uma resposta como definitiva no V1. Não se importou nenhuma resolução privada de cursinho.

## Checklist por questão: evidências e bloqueios

| Nº | Origem/página e comentário da banca | Texto completo versus extração efêmera | Fórmulas/alternativas | Gabarito final Q/X | Direitos por item | Revisão humana |
|---|---|---|---|---|---|---|
| 43 | Conferidos visualmente **por IA**, PDF p. física 47 (impressa 46) | **Pendente** | 50%, 20%, três anos e denominador da comparação | Pendente | Pendente | Pendente |
| 45 | Conferidos visualmente **por IA**, PDF p. física 48 (impressa 47) | **Pendente** | **Crítico**: duas colunas, p(x)±q(x), grau, alternativas A–D | Pendente | Pendente | Pendente |
| 49 | Conferidos visualmente **por IA**, PDF p. física 50 (impressa 49) | **Pendente** | **Crítico**: quebra entre colunas, frações 1/6 e 1/25 | Pendente | Pendente | Pendente |
| 51 | Conferidos visualmente **por IA**, PDF p. física 51 (impressa 50) | **Pendente** | **Crítico**: preservar `ℕ`, `|⋅|`, `≥`, `≤` | Pendente | Pendente | Pendente |
| 52 | Conferidos visualmente **por IA**, PDF p. físicas 51–52 (impressas 50–51) | **Pendente** | **Crítico**: questão inicia numa página e termina na próxima | Pendente | Pendente | Pendente |

Em cada item o campo `humanApproval` está `not_done`, sem pessoa e sem horário inventados. Revisão humana exige abrir lado a lado `staging/unicamp-2026-math/candidates.json` e as imagens do PDF, disponíveis **após regenerar localmente** com `python3 scripts/ingest_pilot.py --mode extract`. O staging do GitHub Actions era temporário, e não equivale a um arquivo salvo para revisão. Conferir também elementos de terceiros, o modelo de caderno e a discrepância de ano na introdução da prova comentada.

## Decisões humanas concretas a registrar

1. **Texto e alternativas:** aprovar/corrigir cada transcrição fielmente pelo PDF, incluindo Q45, Q49, Q51 e Q52. Guardar o PDF e a correção apenas no staging privado.
2. **Classificação:** aprovar/reclassificar cada caminho primário e tags secundárias; justificar especialmente 43, 49 e 51. Não alterar o ID da questão ao reclassificar.
3. **Resolução:** conferir independentemente as cinco soluções originais; corrigir qualquer erro e atribuir autor/revisor reais.
4. **Gabarito e direitos:** identificar e comparar o **gabarito final oficial Q/X** no documento apropriado, incluindo versões/retificações; validar se texto, imagens ou trechos de terceiros podem ser usados caso a caso.
5. **Decisão editorial:** só registrar `reviewedBy`, `reviewedAt` e evento de revisão **depois** da pessoa efetivamente revisar. Questões aprovadas e autorizadas seguem para a etapa 06; bloqueadas continuam em staging.

## Contagem e próximo passo

**5** propostas de classificação, **5** rascunhos matemáticos independentes, **5** checklists de revisão, **0** registros de revisão humana, **0** gabaritos finais reconciliados e **0** questões oficiais publicáveis. Os 12 exercícios autorais continuam no site. A etapa 05 de **preparação editorial** está implementada e validável; a **aprovação humana** permanece pendente e não será declarada concluída por IA.

Próxima etapa: `prompts/06-publicacao-piloto.md`, condicionada à conclusão da revisão humana e aos direitos por item. Acesso gratuito da prova não significa liberação integral para republicação.
