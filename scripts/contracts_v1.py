"""Contrato V1: validação de staging e seleção conservadora para exportação pública.

NÃO altera o seed demonstrativo; não autoriza a ingestão/publicação de oficiais.
Requer jsonschema, listado em requirements-dev.txt.
"""
from collections import defaultdict
from pathlib import Path
import json

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/v1/bundle.schema.json"
COLLECTIONS = (
    "institutions", "processes", "exams", "documents", "question_groups",
    "questions", "answers", "explanations", "classifications",
    "review_events", "question_appearances", "user_attempts",
)
STATES = ("discovered", "acquired", "extracted", "needs_review", "reviewed", "published")
TRANSITIONS = {
    "discovered": {"acquired", "blocked", "rejected"},
    "acquired": {"extracted", "blocked", "rejected"},
    "extracted": {"needs_review", "blocked", "rejected"},
    "needs_review": {"reviewed", "blocked", "rejected"},
    "reviewed": {"published", "needs_review", "blocked", "rejected"},
    "published": {"needs_review", "blocked"},
    "blocked": {"needs_review", "rejected"},
    "rejected": {"discovered"},
}
PUBLIC_RIGHTS = {"authorized", "licensed", "original"}
SCORED_STATUSES = {"final", "corrected"}


class ContractError(ValueError):
    """Contrato inválido, incluindo integridade ou elegibilidade."""


def empty_bundle():
    return {"schemaVersion": 1, **{name: [] for name in COLLECTIONS}}


def _fail(message):
    raise ContractError(message)


def _lookup(items, name):
    result = {}
    for item in items:
        key = item["id"]
        if key in result:
            _fail(f"{name}: ID duplicado: {key}")
        result[key] = item
    return result


def _needed(mapping, key, origin):
    if key not in mapping:
        _fail(f"{origin}: referência ausente: {key}")
    return mapping[key]


def _taxonomy_paths(taxonomy):
    if taxonomy.get("version") != 1:
        _fail("Taxonomia não é V1; migração explícita é necessária")
    subjects, topics, subtopics = set(), set(), set()
    paths = set()
    for subject in taxonomy["subjects"]:
        if subject["id"] in subjects:
            _fail("Matéria duplicada: " + subject["id"])
        subjects.add(subject["id"])
        for topic in subject["topics"]:
            if topic["id"] in topics:
                _fail("Assunto duplicado: " + topic["id"])
            topics.add(topic["id"])
            for subtopic in topic["subtopics"]:
                if subtopic["id"] in subtopics:
                    _fail("Subassunto duplicado: " + subtopic["id"])
                subtopics.add(subtopic["id"])
                paths.add((subject["id"], topic["id"], subtopic["id"]))
    return paths


def _each_block(blocks, group_id, groups, origin):
    for block in blocks:
        if block["type"] == "context_ref":
            if group_id is None or block["groupId"] != group_id:
                _fail(f"{origin}: contexto não corresponde ao grupo da questão")
            _needed(groups, group_id, origin)


def validate_bundle(bundle, taxonomy):
    """Validação estrutural JSON Schema 2020-12 + integridade entre entidades.

    Staging aceita unknown/null e não finge que revisão foi humana. Não publica.
    """
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(bundle),
        key=lambda e: (tuple(str(x) for x in e.absolute_path), e.message),
    )
    if errors:
        first = errors[0]
        where = "/".join(str(p) for p in first.absolute_path) or "$"
        _fail(f"JSON Schema {where}: {first.message} ({len(errors)} erro(s))")
    paths = _taxonomy_paths(taxonomy)
    indexed = {name: _lookup(bundle[name], name) for name in COLLECTIONS}
    global_ids = set()
    for name in COLLECTIONS:
        for entity_id in indexed[name]:
            if entity_id in global_ids:
                _fail(f"ID global duplicado entre entidades: {entity_id}")
            global_ids.add(entity_id)
    institutions, processes, exams, docs, groups, questions = (
        indexed[k] for k in ("institutions", "processes", "exams", "documents", "question_groups", "questions")
    )
    answers, explanations, classifications, events, appearances, attempts = (
        indexed[k] for k in ("answers", "explanations", "classifications", "review_events", "question_appearances", "user_attempts")
    )
    for process in processes.values():
        _needed(institutions, process["institutionId"], process["id"])
    for exam in exams.values():
        process = _needed(processes, exam["processId"], exam["id"])
        # Campos desconhecidos podem ser null; valores informados precisam ser consistentes.
        for field in ("editionYear", "admissionSemester"):
            if exam[field] is not None and process[field] is not None and exam[field] != process[field]:
                _fail(f"{exam['id']}: {field} conflitante com processo")
    for doc in docs.values():
        exam = _needed(exams, doc["examId"], doc["id"])
        if doc["bookletCode"] is not None and exam["bookletCode"] is not None and doc["bookletCode"] != exam["bookletCode"]:
            _fail(f"{doc['id']}: documento pertence a outro modelo de caderno")
        if doc["supersedes"]:
            prev = _needed(docs, doc["supersedes"], doc["id"])
            if prev["examId"] != doc["examId"] or prev["type"] != doc["type"] or prev["revision"] >= doc["revision"]:
                _fail(f"{doc['id']}: substituição de documento inconsistente")
    # Verifique a prova da questão antes de testar os grupos compartilhados.
    for q in questions.values():
        _needed(exams, q["examId"], q["id"])
    for group in groups.values():
        _needed(exams, group["examId"], group["id"])
        if len(group["questionIds"]) != len(set(group["questionIds"])):
            _fail(f"{group['id']}: questão repetida no grupo")
        for qid in group["questionIds"]:
            q = _needed(questions, qid, group["id"])
            if q["examId"] != group["examId"] or q["groupId"] != group["id"]:
                _fail(f"{group['id']}: grupo e questão de provas diferentes")
    for q in questions.values():
        _needed(exams, q["examId"], q["id"])
        if q["canonicalId"] and q["canonicalId"] != q["id"]:
            _needed(questions, q["canonicalId"], q["id"])
        if q["groupId"]:
            g = _needed(groups, q["groupId"], q["id"])
            if g["examId"] != q["examId"] or q["id"] not in g["questionIds"]:
                _fail(f"{q['id']}: grupo fora da prova ou sem referência inversa")
        _each_block(q["contentBlocks"], q["groupId"], groups, q["id"])
        for sub in q["subitems"]:
            _each_block(sub["contentBlocks"], q["groupId"], groups, sub["id"])
        for choice in q["choices"]:
            _each_block(choice["contentBlocks"], q["groupId"], groups, choice["id"])
        if len({c["id"] for c in q["choices"]}) != len(q["choices"]) or len({c["order"] for c in q["choices"]}) != len(q["choices"]):
            _fail(f"{q['id']}: alternativa duplicada")
        if len({s["id"] for s in q["subitems"]}) != len(q["subitems"]) or len({s["order"] for s in q["subitems"]}) != len(q["subitems"]):
            _fail(f"{q['id']}: subitem duplicado")
        for loc in q["sourceLocations"]:
            d = _needed(docs, loc["documentId"], q["id"])
            if d["examId"] != q["examId"] or d["type"] != "booklet":
                _fail(f"{q['id']}: documento de origem não é o caderno da prova")
            if d["pageCount"] and loc["physicalPage"] > d["pageCount"]:
                _fail(f"{q['id']}: página excede documento")
            if loc["sourceSha256"] and d["sha256"] and loc["sourceSha256"] != d["sha256"]:
                _fail(f"{q['id']}: hash do recorte diferente do PDF")
    answers_by_question = defaultdict(list)
    for answer in answers.values():
        q = _needed(questions, answer["questionId"], answer["id"])
        answers_by_question[q["id"]].append(answer)
        if answer["status"] in ("missing", "annulled") and answer["value"] is not None:
            _fail(f"{answer['id']}: gabarito ausente/anulado não possui resposta válida")
        if q["format"] == "multiple_choice" and answer["value"] is not None:
            if answer["value"] not in {c["id"] for c in q["choices"]}:
                _fail(f"{answer['id']}: alternativa correta inexistente")
        if answer["sourceDocumentId"]:
            d = _needed(docs, answer["sourceDocumentId"], answer["id"])
            exam = exams[q["examId"]]
            if d["examId"] != q["examId"] or d["type"] != "answer_key":
                _fail(f"{answer['id']}: gabarito ligado ao documento/prova errada")
            if d["bookletCode"] != exam["bookletCode"] or answer["bookletCode"] != exam["bookletCode"]:
                _fail(f"{answer['id']}: gabarito ligado ao modelo de caderno errado")
            if answer["sourcePage"] and d["pageCount"] and answer["sourcePage"] > d["pageCount"]:
                _fail(f"{answer['id']}: página do gabarito fora do PDF")
        if answer["supersedes"]:
            old = _needed(answers, answer["supersedes"], answer["id"])
            if old["questionId"] != answer["questionId"] or old["revision"] >= answer["revision"]:
                _fail(f"{answer['id']}: retificação sem histórico consistente")
    for qid, values in answers_by_question.items():
        versions = [x["revision"] for x in values]
        if len(versions) != len(set(versions)):
            _fail(f"{qid}: duas versões do gabarito com mesma revisão")
    for explanation in explanations.values():
        q = _needed(questions, explanation["questionId"], explanation["id"])
        if explanation["sourceDocumentId"]:
            doc = _needed(docs, explanation["sourceDocumentId"], explanation["id"])
            if doc["examId"] != q["examId"]:
                _fail(f"{explanation['id']}: resolução fora da prova")
        if explanation["reviewStatus"] == "reviewed" and (not explanation["reviewedBy"] or explanation["reviewedBy"]["type"] != "human" or not explanation["reviewedAt"]):
            _fail(f"{explanation['id']}: revisão editorial sem humano identificado")
        if explanation["authorType"] == "ai_draft" and explanation["reviewStatus"] == "reviewed":
            _fail(f"{explanation['id']}: rascunho de IA não pode ser resolução revisada")
    for c in classifications.values():
        _needed(questions, c["questionId"], c["id"])
        if c["taxonomyVersion"] != taxonomy["version"]:
            _fail(f"{c['id']}: versão de taxonomia incompatível")
        for tag in [c["primary"], *c["secondaryTags"]]:
            if (tag["subjectId"], tag["topicId"], tag["subtopicId"]) not in paths:
                _fail(f"{c['id']}: caminho inválido na taxonomia")
        if c["reviewStatus"] == "reviewed" and (not c["reviewedBy"] or c["reviewedBy"]["type"] != "human" or not c["reviewedAt"]):
            _fail(f"{c['id']}: classificação supostamente revisada sem humano")
    grouped_events = defaultdict(list)
    for event in events.values():
        _needed(indexed[event["entityType"]], event["entityId"], event["id"])
        grouped_events[(event["entityType"], event["entityId"])].append(event)
        if event["toState"] == "reviewed" and event["actor"]["type"] != "human":
            _fail(f"{event['id']}: revisão de IA não é revisão humana")
    for key, history in grouped_events.items():
        history.sort(key=lambda x: x["eventVersion"])
        previous = None
        prev_hash = None
        for expected, event in enumerate(history, start=1):
            if event["eventVersion"] != expected or event["fromState"] != previous:
                _fail(f"{event['id']}: sequência de eventos ou estado anterior inválidos")
            if previous is None:
                if event["toState"] != "discovered":
                    _fail(f"{event['id']}: fluxo deve começar em discovered")
            elif event["toState"] not in TRANSITIONS.get(previous, set()):
                _fail(f"{event['id']}: transição {previous} → {event['toState']} inválida")
            if prev_hash and event["previousHash"] != prev_hash:
                _fail(f"{event['id']}: cadeia de hashes interrompida")
            previous = event["toState"]
            prev_hash = event["newHash"]
    for q in questions.values():
        history = grouped_events.get(("questions", q["id"]), [])
        if history and q["pipelineState"] != history[-1]["toState"]:
            _fail(f"{q['id']}: estado não corresponde ao último evento editorial")
    for appearance in appearances.values():
        _needed(questions, appearance["questionId"], appearance["id"])
        _needed(exams, appearance["examId"], appearance["id"])
        doc = _needed(docs, appearance["documentId"], appearance["id"])
        if doc["examId"] != appearance["examId"] or doc["type"] != "booklet":
            _fail(f"{appearance['id']}: aparição vinculada a caderno incorreto")
        if doc["pageCount"] and appearance["physicalPage"] > doc["pageCount"]:
            _fail(f"{appearance['id']}: página da aparição inválida")
    appearance_positions = [(x["documentId"], x["originalNumber"], x["order"]) for x in appearances.values()]
    if len(appearance_positions) != len(set(appearance_positions)):
        _fail("Aparições duplicadas no mesmo caderno")
    for attempt in attempts.values():
        q = _needed(questions, attempt["questionId"], attempt["id"])
        versions = {a["revision"]: a for a in answers_by_question[q["id"]]}
        if attempt["answerRevision"] is not None:
            old_answer = _needed(versions, attempt["answerRevision"], attempt["id"])
            if old_answer["status"] not in SCORED_STATUSES or old_answer["reviewStatus"] == "conflict":
                if attempt["result"] in ("correct", "incorrect"):
                    _fail(f"{attempt['id']}: questão anulada, sem gabarito final ou em conflito não entra na taxa de acerto")
            if versions and attempt["answerRevision"] != max(versions) and attempt["result"] in ("correct", "incorrect"):
                _fail(f"{attempt['id']}: tentativa exige reavaliação após retificação")
        elif attempt["result"] in ("correct", "incorrect"):
            _fail(f"{attempt['id']}: resultado pontuado sem revisão do gabarito")
    return indexed


def _rights_ok(record):
    status = record["rightsStatus"]
    if status not in PUBLIC_RIGHTS:
        return False
    if status == "original":
        return True
    evidence = record.get("rightsEvidence")
    return bool(
        evidence and evidence["url"] and evidence["verifiedAt"] and
        evidence["verifiedBy"] and evidence["verifiedBy"]["type"] == "human"
    )


def _latest(items):
    return max(items, key=lambda x: x["revision"]) if items else None


def publishability(bundle, taxonomy):
    """Retorna motivos de bloqueio por questão. Não altera staging nem eventos."""
    idx = validate_bundle(bundle, taxonomy)
    answers = defaultdict(list)
    exps = defaultdict(list)
    classifications = defaultdict(list)
    events = defaultdict(list)
    for a in idx["answers"].values():
        answers[a["questionId"]].append(a)
    for e in idx["explanations"].values():
        exps[e["questionId"]].append(e)
    for c in idx["classifications"].values():
        classifications[c["questionId"]].append(c)
    for event in idx["review_events"].values():
        events[(event["entityType"], event["entityId"])].append(event)
    reasons = {}
    for q in idx["questions"].values():
        problem = []
        exam = idx["exams"][q["examId"]]
        process = idx["processes"][exam["processId"]]
        institution = idx["institutions"][process["institutionId"]]
        if q["pipelineState"] != "published" or q["reviewStatus"] != "reviewed":
            problem.append("questão não publicada/revisada")
        history = sorted(events[("questions", q["id"])], key=lambda x: x["eventVersion"])
        if not history or history[-1]["toState"] != "published" or not any(e["toState"] == "reviewed" and e["actor"]["type"] == "human" for e in history):
            problem.append("histórico editorial humano incompleto")
        if q["format"] != "multiple_choice":
            problem.append("formato ainda não suportado pela interface")
        if not q["contentBlocks"] or not q["sourceLocations"] or not q["originalNumber"]:
            problem.append("enunciado ou origem incompletos")
        if q["format"] == "multiple_choice" and (len(q["choices"]) < 2 or any(not c["contentBlocks"] for c in q["choices"])):
            problem.append("alternativas incompletas")
        if not _rights_ok(q):
            problem.append("direitos da questão não autorizam reprodução")
        source_docs = [idx["documents"][loc["documentId"]] for loc in q["sourceLocations"]]
        if any(d["accessStatus"] != "accessible" or not _rights_ok(d) or not d["sourceUrl"] or not d["sha256"] for d in source_docs):
            problem.append("caderno sem origem verificável ou direitos suficientes")
        if institution["id"] == "fgv" and not all([exam["schools"], exam["courses"], exam["campuses"]]):
            problem.append("escola, curso ou campus da FGV ausente")
        if institution["id"] == "insper" and (not exam["admissionSemester"] or not exam["applicationId"]):
            problem.append("semestre ou aplicação do Insper ausente")
        if exam["applicationStatus"] != "applied" or not exam["editionYear"] or not exam["appliedAt"]:
            problem.append("prova cancelada/simulada ou edição/data não conferidas")
        if q["groupId"]:
            group = idx["question_groups"][q["groupId"]]
            if not group["contentBlocks"]:
                problem.append("contexto compartilhado ausente")
        answer = _latest(answers[q["id"]])
        if not answer or answer["status"] not in SCORED_STATUSES or answer["reviewStatus"] != "reviewed" or not answer["verifiedAt"] or not answer["value"] or not answer["sourceDocumentId"]:
            problem.append("gabarito final/retificado não conferido")
        elif answer["value"] not in {c["id"] for c in q["choices"]}:
            problem.append("alternativa final não existe")
        else:
            d = idx["documents"][answer["sourceDocumentId"]]
            if d["type"] != "answer_key" or d["accessStatus"] != "accessible" or not d["sha256"] or not d["sourceUrl"]:
                problem.append("documento de gabarito não verificável")
        approved_class = [c for c in classifications[q["id"]] if c["reviewStatus"] == "reviewed" and c["reviewedBy"] and c["reviewedBy"]["type"] == "human"]
        if len(approved_class) != 1:
            problem.append("classificação humana única não confirmada")
        approved_exp = [e for e in exps[q["id"]] if e["reviewStatus"] == "reviewed" and e["authorType"] != "ai_draft" and _rights_ok(e)]
        if len(approved_exp) != 1:
            problem.append("explicação revisada e publicável ausente")
        reasons[q["id"]] = problem
    return reasons


def export_public_bundle(bundle, taxonomy, *, enable_official=False):
    """Export explícito da V1, sem staging, tentativas ou eventos editoriais.

    OFF por padrão; o build da V0 não chama esta função nem publica staging.
    """
    reasons = publishability(bundle, taxonomy)
    selected = {
        qid for qid, issues in reasons.items()
        if not issues and enable_official
    }
    def selected_where(name, predicate):
        return [record for record in bundle[name] if predicate(record)]
    question_rows = selected_where("questions", lambda x: x["id"] in selected)
    answer_rows = []
    classification_rows = []
    explanation_rows = []
    for qid in selected:
        answer_rows.append(_latest([x for x in bundle["answers"] if x["questionId"] == qid]))
        classification_rows.extend(x for x in bundle["classifications"] if x["questionId"] == qid and x["reviewStatus"] == "reviewed")
        explanation_rows.extend(x for x in bundle["explanations"] if x["questionId"] == qid and x["reviewStatus"] == "reviewed")
    used_exam = {q["examId"] for q in question_rows}
    used_groups = {q["groupId"] for q in question_rows if q["groupId"]}
    used_docs = {loc["documentId"] for q in question_rows for loc in q["sourceLocations"]}
    used_docs.update(a["sourceDocumentId"] for a in answer_rows if a["sourceDocumentId"])
    used_docs.update(e["sourceDocumentId"] for e in explanation_rows if e["sourceDocumentId"])
    used_process = {e["processId"] for e in bundle["exams"] if e["id"] in used_exam}
    used_inst = {p["institutionId"] for p in bundle["processes"] if p["id"] in used_process}
    return {
        "schemaVersion": 1,
        "institutions": selected_where("institutions", lambda x: x["id"] in used_inst),
        "processes": selected_where("processes", lambda x: x["id"] in used_process),
        "exams": selected_where("exams", lambda x: x["id"] in used_exam),
        "documents": selected_where("documents", lambda x: x["id"] in used_docs),
        "question_groups": selected_where("question_groups", lambda x: x["id"] in used_groups),
        "questions": question_rows,
        "answers": answer_rows,
        "explanations": explanation_rows,
        "classifications": classification_rows,
        "question_appearances": selected_where("question_appearances", lambda x: x["questionId"] in selected),
    }
