"""Verificação do manifesto de extração sem acesso ao PDF de terceiros."""
from datetime import date
from pathlib import Path
import json

EXPECTED_NUMBERS=("43","45","49","51","52")
EXPECTED_PAGES={"43":[47],"45":[48],"49":[50],"51":[51],"52":[51,52]}
EXPECTED_ANSWERS={"43":"a","45":"b","49":"b","51":"c","52":"b"}
SOURCE="https://www.comvest.unicamp.br/wp-content/uploads/2026/06/F1_2026_Prova-Q.pdf"

class PilotManifestError(ValueError):pass

def check(condition,message):
    if not condition:raise PilotManifestError(message)

def validate_pilot(m,bundle):
    check(m.get("manifestVersion")==1,"Manifesto deve ser versionado")
    check(m.get("lotId")=="pilot-unicamp-2026-f1-math-01","Lote não reconhecido")
    check(m.get("sourceUrl")==SOURCE,"Fonte fora do documento oficial inventariado")
    check(m.get("bookletCode")=="Q","Modelo da prova comentada não corresponde")
    check(m.get("editionYear")==2026 and m.get("appliedAt")=="2025-10-26",
          "Edição de ingresso e aplicação não foram separadas")
    check(m.get("expectedPageCount")==71,"Número de páginas não verificado")
    check(m.get("rightsStatus")=="link_only" and m.get("rightsEvidenceUrl"),
          "Licença parcial não autoriza republicação integral")
    check(m.get("overall",{}).get("published")==0,"Não publicar antes de revisão")
    check(m.get("overall",{}).get("humanReviewed")==0,"Revisão humana não foi realizada")
    check(m.get("overall",{}).get("questionsSelected")==5,"Lote deve ter cinco questões")
    specs=m.get("selectedQuestions",[])
    numbers=[s["number"] for s in specs]
    check(tuple(numbers)==EXPECTED_NUMBERS,"IDs/números do lote divergem das páginas examinadas")
    for s in specs:
        n=s["number"]
        check(s["id"]==f"unicamp-2026-f1-q{int(n):03d}" and
              s["physicalPages"]==EXPECTED_PAGES[n],
              f"Questão {n} com páginas/ID incorretos")
        check(s["commentaryAnswerCandidate"]==EXPECTED_ANSWERS[n],
              f"Questão {n}: alternativa candidata não coincide com a página visualizada")
        check(s["finalKeyStatus"]=="not_cross_checked" and not s["humanReviewed"]
              and not s["publishable"],"Não declarar gabarito/revisão final")
    check(bundle.get("schemaVersion")==1,"Contrato V1 ausente")
    check(len(bundle.get("questions",[]))==5 and len(bundle.get("answers",[]))==5,
          "O staging tem que representar as cinco questões")
    check(len(bundle.get("documents",[]))==1,"Não inventar outro documento oficial")
    doc=bundle["documents"][0]
    check(doc["sourceUrl"]==SOURCE and doc["rightsStatus"]=="link_only"
          and doc["sha256"]==m["sha256"] and doc["accessStatus"]=="accessible",
          "Documento/hash deve corresponder ao obtido pela CI")
    for s,q,a in zip(specs,bundle["questions"],bundle["answers"]):
        check(q["id"]==s["id"] and q["originalNumber"]==s["number"],
              "Questão incompatível com manifesto")
        check(q["pipelineState"]=="discovered" and q["reviewStatus"]=="needs_review"
              and q["rightsStatus"]=="link_only","Item bloqueado até extrair e revisar")
        check(not q["contentBlocks"] and not q["choices"],
              "Enunciados e alternativas de terceiros não podem ser commitados")
        check([l["physicalPage"] for l in q["sourceLocations"]]==s["physicalPages"],
              "Localização da questão não corresponde ao PDF")
        check(a["questionId"]==q["id"] and a["status"]=="missing"
              and a["value"] is None and a["verifiedBy"] is None and
              a["sourceDocumentId"] is None,
              "Candidato do comentário não pode se passar por gabarito validado")
    check(not bundle["user_attempts"] and not bundle["review_events"],
          "Não criar estudantes nem revisões editoriais fictícias")
    return {"selected":5,"verifiedFinalKeys":0,"humanReviewed":0,"published":0}
