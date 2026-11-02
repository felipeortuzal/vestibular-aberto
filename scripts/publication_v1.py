"""Etapa 06: projeto público estritamente a partir de lote V1 elegível.

O GitHub Pages recebe apenas a projeção pública; jamais staging, eventos
editoriais, tentativas de estudantes, PDF original ou conteúdo não revisado.
"""
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit

from contracts_v1 import validate_bundle, export_public_bundle

DOMAIN_BY_INSTITUTION = {
    "unicamp": {"www.comvest.unicamp.br"},
    "fuvest": {"www.fuvest.br"},
    "insper": {"www.insper.edu.br", "www.vunesp.com.br"},
    "fgv": {"vestibular.fgv.br"},
}
DOC_TYPES = {"booklet", "commented_booklet", "answer_key", "correction_grid", "expected_answers", "notice"}
ASSET_PATH = re.compile(r"^assets/official/([a-z][a-z0-9-]{2,90})\.(png|jpg|webp)$")


class PublicationError(ValueError):
    pass


def ensure(ok, message):
    if not ok:
        raise PublicationError(message)


def official_https(url, institution_id):
    parts = urlsplit(url)
    return (parts.scheme == "https" and parts.hostname in DOMAIN_BY_INSTITUTION[institution_id]
            and parts.username is None and parts.password is None and not parts.fragment)


def validate_exam_catalog(exams, available_questions=()):
    """Registros de fonte não são automaticamente provas importadas."""
    ids = set()
    published_by_exam = {}
    for q in available_questions:
        published_by_exam[q["examId"]] = published_by_exam.get(q["examId"], 0) + 1
    for e in exams:
        eid = e["id"]
        ensure(eid not in ids, "Prova repetida: " + eid)
        ids.add(eid)
        inst = e["institutionId"]
        ensure(inst in DOMAIN_BY_INSTITUTION, "Instituição não suportada")
        ensure(e["organizer"] and e["title"] and e["selectionType"] == "vestibular",
               eid + ": identidade incompleta")
        ensure(e["status"] in ("metadata_only", "published"), eid + ": estado desconhecido")
        ensure(isinstance(e["editionYear"], int) and e["editionYear"] >= 2000, eid + ": edição incorreta")
        ensure(e.get("appliedAt") and e.get("phase") and e.get("day"), eid + ": aplicação não identificada")
        ensure(e.get("rightsStatus") in ("link_only", "authorized", "licensed"), eid + ": direitos ausentes")
        ensure(isinstance(e["pilotCandidates"], int) and e["pilotCandidates"] >= 0,
               eid + ": contagem de candidatos inválida")
        total = e["expectedQuestionCount"]
        ensure(total is None or (isinstance(total, int) and total >= 0),
               eid + ": total de questões precisa ser fundamentado ou null")
        actual = published_by_exam.get(eid, 0)
        ensure(e["approvedQuestionCount"] == actual, eid + ": contagem publicada não coincide com os itens elegíveis")
        if total is not None:
            ensure(actual <= total, eid + ": publicadas excedem total oficial verificado")
        ensure((e["status"] == "published") == (actual > 0), eid + ": status contradiz a contagem")
        if actual:
            ensure(e["finalAnswerDocumentStatus"] == "verified", eid + ": gabarito não verificado")
        docs = e["documents"]
        ensure(isinstance(docs, list) and len(docs) > 0, eid + ": falta documento real")
        keys = set()
        for d in docs:
            ensure(d["id"] not in keys, eid + ": documento duplicado")
            keys.add(d["id"])
            ensure(d["type"] in DOC_TYPES, eid + ": tipo de documento incorreto")
            ensure(official_https(d["url"], inst), eid + ": URL fora da fonte oficial")
            ensure(d["verified"] is True, eid + ": PDF sem confirmação de origem")
            ensure(d["rightsStatus"] in ("link_only", "authorized", "licensed"),
                   eid + ": direitos do PDF não documentados")
            ensure(re.fullmatch(r"[0-9a-f]{64}", d["sha256"]) is not None and d["pageCount"] >= 1,
                   eid + ": documento sem hash ou páginas")
        if e["finalAnswerDocumentStatus"] == "verified":
            ensure(any(d["type"] == "answer_key" for d in docs), eid + ": faltou arquivo do gabarito final")
    ensure(set(published_by_exam).issubset(ids), "Questão aprovada sem registro de prova")
    return {"individualizedExams": len(exams), "publishedExams": sum(e["status"] == "published" for e in exams)}


def approved_assets(assets, repo_root):
    """Não converter 'assetId' em URL arbitrária ou permitir arquivo não aprovado."""
    found = {}
    for asset in assets:
        aid, rel = asset["id"], asset["path"]
        ensure(aid not in found and ASSET_PATH.fullmatch(rel), "Asset não permitido ou duplicado")
        ensure(ASSET_PATH.fullmatch(rel).group(1) == aid, "AssetId e caminho não correspondem")
        ensure(asset.get("rightsStatus") in ("authorized", "licensed", "original")
               and (asset.get("reviewedBy") or {}).get("type") == "human"
               and asset.get("altText") and asset.get("credit") and asset.get("sourceUrl"),
               "Imagem sem autorização/revisão humana e atribuição")
        p = Path(repo_root) / rel
        ensure(p.is_file() and p.resolve().is_relative_to((Path(repo_root) / "assets" / "official").resolve()),
               "Arquivo de imagem ausente ou fora de assets/official")
        content = p.read_bytes()
        ensure(hashlib.sha256(content).hexdigest() == asset["sha256"], "Hash da imagem divergente")
        found[aid] = {"path": rel, "altText": asset["altText"], "credit": asset["credit"]}
    return found


def blocks_for_view(blocks, assets):
    """Somente dados estruturados; frontend usa textContent/createElement, nunca innerHTML."""
    result = []
    for b in blocks:
        t = b["type"]
        if t == "text":
            result.append({"type": "text", "text": b["text"]})
        elif t == "math":
            # Texto alternativo aprovado é usado como fallback legível de LaTex.
            result.append({"type": "math", "latex": b["latex"], "altText": b["altText"]})
        elif t == "image":
            ensure(b["assetId"] in assets, "Imagem não aprovada: " + b["assetId"])
            asset = assets[b["assetId"]]
            result.append({"type": "image", "url": asset["path"], "altText": b["altText"],
                           "caption": b.get("caption"), "credit": b.get("credit") or asset["credit"]})
        elif t == "table":
            rows = b["rows"]
            ensure(all(len(row) == len(rows[0]) for row in rows), "Tabela irregular")
            result.append({"type": "table", "rows": rows, "caption": b.get("caption")})
        elif t == "context_ref":
            # Resolvido no projector de questões usando question_groups.
            result.append({"type": "context_ref", "groupId": b["groupId"]})
        else:
            raise PublicationError("Bloco não suportado: " + t)
    return result


def readable(blocks):
    output = []
    for b in blocks:
        if b["type"] == "text":
            output.append(b["text"])
        elif b["type"] == "math":
            output.append(b["altText"])
        elif b["type"] == "image":
            output.append(b["altText"])
        elif b["type"] == "table":
            output.append(" ".join(" ".join(row) for row in b["rows"]))
    return "\n".join(output)


def project_eligible(bundle, taxonomy, exam_catalog, assets=(), repo_root=None):
    """Projeta somente registros que passam por TODO o contrato V1.
    
    A aprovação humana, gabarito final, versão e direitos são verificados em
    export_public_bundle; nenhum flag público permite ignorar essas regras.
    """
    repo_root = Path(repo_root or Path(__file__).resolve().parents[1])
    approved = approved_assets(assets, repo_root)
    validate_bundle(bundle, taxonomy)
    public = export_public_bundle(bundle, taxonomy, enable_official=True)
    docs = {d["id"]: d for d in public["documents"]}
    exams = {e["id"]: e for e in public["exams"]}
    processes = {p["id"]: p for p in public["processes"]}
    group = {g["id"]: g for g in public["question_groups"]}
    answers = {a["questionId"]: a for a in public["answers"]}
    classes = {c["questionId"]: c for c in public["classifications"]}
    explanations = {e["questionId"]: e for e in public["explanations"]}
    names = {s["id"]: s for s in taxonomy["subjects"]}
    result = []
    for q in public["questions"]:
        if q["format"] != "multiple_choice":
            raise PublicationError("Questão discursiva não suportada no banco de correção automática")
        exam = exams[q["examId"]]
        process = processes[exam["processId"]]
        sid = process["institutionId"]
        path = classes[q["id"]]["primary"]
        subject = names[path["subjectId"]]
        topic = next(t for t in subject["topics"] if t["id"] == path["topicId"])
        subtopic = next(t for t in topic["subtopics"] if t["id"] == path["subtopicId"])
        content = blocks_for_view(q["contentBlocks"], approved)
        if q["groupId"]:
            ensure(q["groupId"] in group, "Contexto não foi importado")
            shared = blocks_for_view(group[q["groupId"]]["contentBlocks"], approved)
        else:
            shared = []
        # Contextos podem vir como bloco 'context_ref', deduplicar nesse caso.
        all_content = shared + [b for b in content if b["type"] != "context_ref"]
        ensure(readable(all_content).strip(), "Questão sem texto acessível")
        choices = []
        for c in sorted(q["choices"], key=lambda x: x["order"]):
            view = blocks_for_view(c["contentBlocks"], approved)
            ensure(readable(view).strip(), "Alternativa sem texto acessível")
            choices.append({"id": c["id"], "label": c["label"], "text": readable(view), "blocks": view})
        answer = answers[q["id"]]
        ensure(answer["status"] in ("final", "corrected"), "Questão sem gabarito pontuável final")
        explain = blocks_for_view(explanations[q["id"]]["contentBlocks"], approved)
        loc = q["sourceLocations"][0]
        document = docs[loc["documentId"]]
        ensure(official_https(document["sourceUrl"], sid), "Documento de questão não pertence à instituição")
        result.append({
            "id": q["id"], "kind": "official", "institutionId": sid, "organizer": process["organizer"],
            "examId": q["examId"], "editionYear": exam["editionYear"],
            "admissionSemester": exam["admissionSemester"], "phase": exam["phase"],
            "day": exam["day"], "bookletCode": exam["bookletCode"],
            "schools": exam["schools"], "courses": exam["courses"], "campuses": exam["campuses"],
            "number": q["originalNumber"], "format": q["format"],
            "statement": readable(all_content), "contentBlocks": all_content,
            "choices": choices,
            "answer": {"status": answer["status"], "choiceId": answer["value"],
                       "revision": answer["revision"], "sourcePage": answer["sourcePage"]},
            "explanation": readable(explain), "explanationBlocks": explain,
            "classification": {**path, "secondaryTags": classes[q["id"]]["secondaryTags"],
                               "status": "human-reviewed"},
            "tags": [subject["label"], topic["label"], subtopic["label"]],
            "provenance": {"type": "official", "url": document["sourceUrl"],
                           "page": loc["physicalPage"], "printedPage": loc["printedPage"],
                           "sha256": loc["sourceSha256"], "answerVersion": answer["revision"]},
            "rights": {"status": q["rightsStatus"]}, "reviewStatus": "reviewed"
        })
    validate_exam_catalog(exam_catalog, result)
    return result
