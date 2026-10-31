"""Testes de contrato V1; TODOS os dados são sintéticos e não publicáveis no site."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from contracts_v1 import ContractError, empty_bundle, export_public_bundle, publishability, validate_bundle

TAX = json.loads((ROOT / "data/taxonomy.json").read_text(encoding="utf-8"))
FIXTURE = json.loads((ROOT / "tests/fixtures/v1/synthetic_bundle.json").read_text(encoding="utf-8"))


def sample():
    return copy.deepcopy(FIXTURE)


class ContractTests(unittest.TestCase):
    def fails(self, obj, phrase):
        with self.assertRaisesRegex(ContractError, phrase):
            validate_bundle(obj, TAX)

    def test_positive_synthetic_schema_and_full_bundle(self):
        data = sample()
        self.assertEqual(len(validate_bundle(data, TAX)["questions"]), 1)
        self.assertEqual(publishability(data, TAX)["synthetic-question"], [])

    def test_unknown_fields_are_allowed_in_staging(self):
        data = sample()
        q = data["questions"][0]
        q.update(originalNumber=None, sourceLocations=[], rightsStatus="unknown",
                 rightsEvidence=None, reviewStatus="draft", pipelineState="needs_review")
        data["documents"][0].update(sourceUrl=None, sha256=None, accessStatus="unverified")
        data["review_events"] = []  # trabalho em staging antes do histórico publicado
        self.assertEqual(len(validate_bundle(data, TAX)["questions"]), 1)
        self.assertTrue(publishability(data, TAX)["synthetic-question"])

    def test_cross_discipline_secondary_path_is_allowed(self):
        data = sample()
        data["classifications"][0]["secondaryTags"].append(
            {"subjectId": "geografia", "topicId": "geografia.cartografia",
             "subtopicId": "geografia.cartografia.escalas"})
        validate_bundle(data, TAX)

    def test_discursive_and_subitems_are_valid_staging_not_public(self):
        data = sample()
        q = data["questions"][0]
        q["format"] = "discursive"
        q["subitems"].append({"id":"synthetic-subitem","label":"a","order":1,
                              "format":"numeric","contentBlocks":[{"type":"text","text":"Item fictício"}]})
        validate_bundle(data, TAX)
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])

    def test_corrected_answer_keeps_old_revision_and_forces_regrade(self):
        data = sample()
        newer = copy.deepcopy(data["answers"][0])
        newer.update(id="synthetic-answer-r2", status="corrected", value="a",
                     revision=2, supersedes="synthetic-answer")
        data["answers"].append(newer)
        self.fails(data, "reavaliação")
        data["user_attempts"][0]["result"] = "pending"
        validate_bundle(data, TAX)
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["answers"][0]["revision"],2)

    def test_ai_cannot_verify_answer_as_human(self):
        data = sample()
        data["answers"][0]["verifiedBy"]={"type":"ai","id":"synthetic-ai"}
        self.fails(data, "conferência humana")

    def test_restricted_key_document_blocks_public_export(self):
        data = sample()
        data["documents"][1]["rightsStatus"]="unknown"
        data["documents"][1]["rightsEvidence"]=None
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])

    def test_public_group_does_not_leak_unpublished_question_id(self):
        data = sample()
        other = copy.deepcopy(data["questions"][0])
        other.update(id="synthetic-unpublished",reviewStatus="draft",
                     pipelineState="blocked",rightsStatus="unknown",rightsEvidence=None)
        data["questions"].append(other)
        data["question_groups"][0]["questionIds"].append("synthetic-unpublished")
        public=export_public_bundle(data, TAX, enable_official=True)
        self.assertEqual(public["question_groups"][0]["questionIds"],["synthetic-question"])
        self.assertNotIn("synthetic-unpublished",str(public))

    def test_wrong_choice_is_rejected(self):
        data = sample()
        data["answers"][0]["value"] = "c"
        self.fails(data, "alternativa correta inexistente")

    def test_orphan_official_question_is_rejected(self):
        data = sample()
        data["questions"][0]["examId"] = "missing-exam"
        self.fails(data, "referência ausente")

    def test_orphan_origin_document_is_rejected(self):
        data = sample()
        data["questions"][0]["sourceLocations"][0]["documentId"] = "missing-booklet"
        self.fails(data, "referência ausente")

    def test_invalid_primary_or_secondary_path_is_rejected(self):
        data = sample()
        data["classifications"][0]["primary"]["subtopicId"] = "matematica.fake"
        self.fails(data, "caminho inválido")
        data = sample()
        data["classifications"][0]["secondaryTags"].append(
            {"subjectId": "fisica", "topicId": "matematica.geometria-plana",
             "subtopicId": "matematica.geometria-plana.areas-de-figuras-planas"})
        self.fails(data, "caminho inválido")

    def test_duplicate_id_or_answer_revision_is_rejected(self):
        data = sample()
        data["questions"].append(copy.deepcopy(data["questions"][0]))
        self.fails(data, "ID duplicado")
        data = sample()
        answer = copy.deepcopy(data["answers"][0])
        answer["id"] = "synthetic-answer-duplicate"
        data["answers"].append(answer)
        self.fails(data, "mesma revisão")

    def test_answer_key_from_other_booklet_is_rejected(self):
        data = sample()
        data["answers"][0]["bookletCode"] = "FORM-B"
        self.fails(data, "modelo de caderno errado")
        data = sample()
        data["documents"][1]["examId"] = "missing-exam"
        self.fails(data, "referência ausente")

    def test_licence_unknown_and_blocked_state_never_export(self):
        data = sample()
        data["questions"][0]["rightsStatus"] = "link_only"
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])
        data = sample()
        data["questions"][0]["pipelineState"] = "blocked"
        data["review_events"] = []  # nenhum estado publicado herdado como válido
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])

    def test_public_export_opt_in_and_no_editorial_or_user_data(self):
        data = sample()
        self.assertEqual(export_public_bundle(data, TAX)["questions"], [])
        allowed = export_public_bundle(data, TAX, enable_official=True)
        self.assertEqual([x["id"] for x in allowed["questions"]], ["synthetic-question"])
        self.assertNotIn("review_events", allowed)
        self.assertNotIn("user_attempts", allowed)
        self.assertEqual(len(allowed["documents"]), 2)

    def test_anulled_answer_cannot_count_as_student_error(self):
        data = sample()
        data["answers"][0].update(status="annulled", value=None)
        data["user_attempts"][0]["result"] = "incorrect"
        self.fails(data, "anulada")
        data["user_attempts"][0]["result"] = "not_scored"
        validate_bundle(data, TAX)

    def test_missing_answer_and_conflict_cannot_count(self):
        data = sample()
        data["answers"][0].update(status="missing", value=None)
        data["user_attempts"][0]["result"] = "incorrect"
        self.fails(data, "anulada")
        data = sample()
        data["answers"][0].update(reviewStatus="conflict", conflictNote="Conta não coincide com documento")
        data["user_attempts"][0]["result"] = "correct"
        self.fails(data, "conflito")

    def test_ai_cannot_claim_human_review(self):
        data = sample()
        data["review_events"][4]["actor"] = {"type":"ai","id":"synthetic-ai"}
        self.fails(data, "revisão de IA")
        data = sample()
        data["classifications"][0]["reviewedBy"] = {"type":"ai","id":"synthetic-ai"}
        self.fails(data, "sem humano")
        data = sample()
        data["explanations"][0]["authorType"] = "ai_draft"
        self.fails(data, "rascunho de IA")

    def test_invalid_workflow_transition_is_rejected(self):
        data = sample()
        data["review_events"][1]["toState"] = "published"
        self.fails(data, "transição")
        
    def test_state_must_match_last_editorial_event(self):
        data = sample()
        data["questions"][0]["pipelineState"] = "blocked"
        self.fails(data, "último evento editorial")

    def test_cancelled_exam_cannot_be_published(self):
        data = sample()
        data["exams"][0]["applicationStatus"] = "cancelled"
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])

    def test_insper_requires_application_and_fgv_requires_school_course_campus(self):
        data = sample()
        data["institutions"][0]["id"] = "insper"
        data["processes"][0]["institutionId"] = "insper"
        data["exams"][0]["applicationId"] = None
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])
        data = sample()
        data["institutions"][0]["id"] = "fgv"
        data["processes"][0]["institutionId"] = "fgv"
        self.assertEqual(export_public_bundle(data, TAX, enable_official=True)["questions"], [])

    def test_versioned_taxonomy_preserves_known_ids(self):
        self.assertEqual(TAX["version"], 1)
        subjects = {s["id"]: s for s in TAX["subjects"]}
        self.assertIn("matematica.geometria-plana", {t["id"] for t in subjects["matematica"]["topics"]})
        self.assertEqual(len(TAX["subjects"]),12)
        self.assertEqual(sum(len(s["topics"]) for s in TAX["subjects"]),45)
        self.assertEqual(sum(len(t["subtopics"]) for s in TAX["subjects"] for t in s["topics"]),122)

    def test_v0_seed_and_local_progress_are_not_migrated(self):
        demo = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
        self.assertEqual(len(demo),12)
        self.assertTrue(all(q["kind"]=="demo" and q["examId"] is None for q in demo))
        self.assertEqual(json.loads((ROOT / "data/exams.json").read_text(encoding="utf-8")), [])
        self.assertEqual(empty_bundle()["questions"], [])


if __name__ == "__main__":
    unittest.main()
