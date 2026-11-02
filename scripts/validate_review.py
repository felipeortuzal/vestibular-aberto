"""Etapa 05: confere propostas de IA e mantém gates humanos de publicação.
Arquivos versionados de pilot/ contêm somente metadados e soluções originais;
a transcrição oficial gerada na etapa 04 permanece em staging/ privado.
"""
import json
from pathlib import Path

from contracts_v1 import validate_bundle, export_public_bundle
from validate_pilot import validate_pilot

ROOT=Path(__file__).resolve().parents[1]
PILOT=ROOT/"pilot/unicamp-2026-math"
def load(path):return json.loads(Path(path).read_text(encoding="utf-8"))

class ReviewError(ValueError):
    pass

def require(condition,message):
    if not condition:raise ReviewError(message)

def validate_review(bundle,checklist,manifest,taxonomy):
    idx=validate_bundle(bundle,taxonomy)
    validate_pilot(manifest,bundle)
    require(checklist.get("schemaVersion")==1,"Esquema de revisão não versionado")
    require(checklist.get("lotId")==manifest["lotId"],"Checklist de outro lote")
    require(checklist.get("reviewMode")=="ai_pre_review_not_human_approval","IA não pode aprovar como humano")
    require(len(bundle["questions"])==len(checklist.get("items",[]))==5,"O lote deve conter os mesmos cinco itens")
    require(len(bundle["classifications"])==len(bundle["explanations"])==5,"Todos os itens precisam de proposta e rascunho de resolução")
    require(not bundle["review_events"] and not bundle["user_attempts"],"Proibido fabricar evento editorial ou tentativa de estudante")
    require(not bundle["question_groups"] and not bundle["question_appearances"],"Não criar vínculos não revisados")
    require(all(q["reviewStatus"]=="needs_review" and q["pipelineState"]=="discovered" for q in bundle["questions"]),
            "Questões não foram humanamente revisadas nem formalmente promovidas de estado")
    require(all(q["rightsStatus"]=="link_only" and not q["contentBlocks"] and not q["choices"] for q in bundle["questions"]),
            "Enunciado/alternativa oficial não pode entrar no repositório neste estágio")
    require(all(a["status"]=="missing" and a["value"] is None and a["verifiedBy"] is None
                and a["sourceDocumentId"] is None and a["reviewStatus"]=="needs_review" for a in bundle["answers"]),
            "Rascunho ou comentário não é gabarito final oficial validado")
    require(len({x["questionId"] for x in bundle["classifications"]})==5,"Classificação duplicada por questão")
    require(len({x["questionId"] for x in bundle["explanations"]})==5,"Explicação duplicada por questão")
    for c in bundle["classifications"]:
        require(c["taxonomyVersion"]==taxonomy["version"],"Versão da taxonomia mudou")
        require(c["primary"]["subjectId"]=="matematica","Questões deste lote são de Matemática")
        require(c["proposedBy"]["type"]=="ai" and c["reviewStatus"]=="needs_review"
                and c["reviewedBy"] is None and c["reviewedAt"] is None,
                "Classificação de IA não é revisão humana")
        require(c["confidence"] is not None and 0<=c["confidence"]<=1 and c["rationale"],
                "Proposta deve conter confiança e justificativa")
    for e in bundle["explanations"]:
        require(e["authorType"]=="ai_draft" and e["proposedBy"]["type"]=="ai"
                and e["reviewedBy"] is None and e["reviewedAt"] is None
                and e["reviewStatus"]=="needs_review","Resolução de IA não pode se declarar aprovada")
        require(e["rightsStatus"]=="original" and e["sourceDocumentId"] is None
                and e["contentBlocks"] and all(b["type"]=="text" and b["text"] for b in e["contentBlocks"]),
                "Resolução original deve ficar separada do texto da prova")
    ids=[x["questionId"] for x in checklist["items"]]
    require(len(set(ids))==5 and set(ids)==set(idx["questions"]),"Checklists duplicados/ausentes")
    for item in checklist["items"]:
        id=item["questionId"]
        question=idx["questions"][id]
        cl=next(x for x in bundle["classifications"] if x["questionId"]==id)
        ex=next(x for x in bundle["explanations"] if x["questionId"]==id)
        sp=next(s for s in manifest["selectedQuestions"] if s["id"]==id)
        ch=item["checks"]
        require(item["schemaVersion"]==1 and item["stage"]=="needs_review","Checklist não pode marcar item como aprovado")
        require(item["sourceSha256"]==manifest["sha256"] and item["sourceDocumentId"]==manifest["documentId"],"Origem/hash do checklist divergente")
        require(item["originalNumber"]==question["originalNumber"]==sp["number"],"Número original divergente")
        require(item["physicalPages"]==sp["physicalPages"] and item["printedPages"]==sp["printedPages"],"Páginas incorretas")
        require(ch["origin"]["status"]=="verified_by_ai" and ch["pageAndNumber"]["status"]=="verified_by_ai","Método de verificação da fonte deve estar explícito")
        for field in ("fullText","choicesAndFormulas","figuresAndThirdParty"):
            require(ch[field]["status"]=="pending_human" and ch[field]["issue"],field+": falta pendência de revisão")
        answer=ch["officialFinalKey"]
        require(answer["status"]=="pending_official_confirmation" and
                answer["commentaryCandidate"]==sp["commentaryAnswerCandidate"].upper() and
                answer["reviewedFinalValue"] is None and answer["verifiedBy"] is None and
                answer["sourceDocumentId"] is None,"Não inventar gabarito final conferido")
        require(ch["classification"]["status"]=="proposed_by_ai" and
                ch["classification"]["classificationId"]==cl["id"] and
                ch["classification"]["primary"]==cl["primary"] and
                ch["classification"]["secondaryTags"]==cl["secondaryTags"] and
                ch["classification"]["reviewedBy"] is None,"Classificação do checklist é diferente da proposta")
        require(ch["rights"]["status"]=="link_only" and ch["rights"]["reviewedBy"] is None,"Direitos não autorizam reprodução integral")
        require(ch["originalSolution"]["status"]=="ai_draft" and
                ch["originalSolution"]["explanationId"]==ex["id"] and
                ch["originalSolution"]["independentMathAnswer"]==sp["commentaryAnswerCandidate"].upper() and
                ch["originalSolution"]["humanChecked"] is False,"Solução não foi aprovada por humano")
        require(ch["difficulty"]["editorial"] is None and ch["difficulty"]["empirical"] is None,"Dificuldade não medida deve permanecer nula")
        approval=item["humanApproval"]
        require(approval["status"]=="not_done" and approval["reviewer"] is None
                and approval["reviewedAt"] is None and approval["decision"] is None,
                "Não simular revisão de Felipe ou outro humano")
        require(item["publicationEligible"] is False,"Item não pode ser publicado antes do gate")
    counts=checklist["totals"]
    require(counts=={"selected":5,"aiClassified":5,"aiDraftExplanations":5,
                     "humanApproved":0,"officialFinalKeysConfirmed":0,"publicReady":0},
            "Contadores da etapa 05 precisam refletir fatos")
    require(export_public_bundle(bundle,taxonomy,enable_official=True)["questions"]==[],
            "Export oficial liberou questão do lote sem revisão")
    return counts

def validate_files():
    bundle=load(PILOT/"staging-metadata-v1.json")
    manifest=load(PILOT/"manifest.json")
    checklist=load(PILOT/"review-checklist-v1.json")
    taxonomy=load(ROOT/"data/taxonomy.json")
    return validate_review(bundle,checklist,manifest,taxonomy)

if __name__=="__main__":
    print("OK etapa 05:",json.dumps(validate_files(),ensure_ascii=False))
