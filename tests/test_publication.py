"""Testes da publicação real: fixture sintética NUNCA é copiada para o site."""
import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publication_v1 import (PublicationError, validate_exam_catalog, project_eligible,
    blocks_for_view, approved_assets, readable)
from contracts_v1 import empty_bundle

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

TAX=load("data/taxonomy.json")
CAT=load("data/exams.json")
PUBLISHED=load("data/publication-v1.json")
FIXTURE=load("tests/fixtures/v1/synthetic_bundle.json")

def eligible_fixture():
    data=copy.deepcopy(FIXTURE)
    data["institutions"][0]["id"]="unicamp"
    data["processes"][0]["institutionId"]="unicamp"
    data["processes"][0]["organizer"]="Comvest"
    data["documents"][0]["sourceUrl"]="https://www.comvest.unicamp.br/fictional-synthetic-booklet.pdf"
    data["documents"][1]["sourceUrl"]="https://www.comvest.unicamp.br/fictional-synthetic-key.pdf"
    # Não criar uma imagem baseada em fixture no catálogo real. É só validação do projetor.
    q=data["questions"][0]
    q["contentBlocks"]=[b for b in q["contentBlocks"] if b["type"]!="image"]
    ex=data["exams"][0]
    catalog=[{
      "id":ex["id"],"institutionId":"unicamp","organizer":"Comvest",
      "selectionType":"vestibular","editionYear":ex["editionYear"],"appliedAt":ex["appliedAt"],
      "admissionSemester":ex["admissionSemester"],"applicationId":ex["applicationId"],
      "phase":ex["phase"],"day":ex["day"],"bookletCode":ex["bookletCode"],
      "schools":[],"campuses":[],"courses":[],"title":"Caderno 100% fictício do teste",
      "status":"published","rightsStatus":"authorized","sourceInventoryId":None,
      "documents":[
          {"id":d["id"],"type":d["type"],"title":"Fictício",
           "url":d["sourceUrl"],"sha256":d["sha256"],"verified":True,
           "rightsStatus":"authorized","pageCount":d["pageCount"]}
          for d in data["documents"]],
      "finalAnswerDocumentStatus":"verified","expectedQuestionCount":None,
      "pilotCandidates":0,"approvedQuestionCount":1,"notes":"Fixture sintética só para teste."
    }]
    return data,catalog

class PublicationTests(unittest.TestCase):
    def test_current_production_has_zero_official_and_one_link_only_exam(self):
        self.assertEqual(len(PUBLISHED["questions"]),0)
        self.assertEqual(len(project_eligible(PUBLISHED,TAX,CAT,[],ROOT)),0)
        self.assertEqual(validate_exam_catalog(CAT,[]),{"individualizedExams":1,"publishedExams":0})
        self.assertEqual(CAT[0]["finalAnswerDocumentStatus"],"not_verified")
        self.assertEqual(CAT[0]["pilotCandidates"],5)
        self.assertEqual(CAT[0]["approvedQuestionCount"],0)

    def test_synthetic_fully_eligible_is_rendered_without_editorial_metadata(self):
        data,cat=eligible_fixture()
        rows=project_eligible(data,TAX,cat,[],ROOT)
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["kind"],"official")
        self.assertEqual(row["id"],"synthetic-question")
        self.assertEqual(row["answer"]["status"],"final")
        self.assertEqual(row["answer"]["revision"],1)
        self.assertEqual(row["answer"]["choiceId"],"b")
        self.assertEqual(row["provenance"]["page"],1)
        self.assertEqual(row["provenance"]["sha256"],"a"*64)
        self.assertEqual(row["institutionId"],"unicamp")
        self.assertEqual(row["editionYear"],2026)
        self.assertIn("Questão sintética",row["statement"])
        self.assertTrue(any(b["type"]=="math" for b in row["contentBlocks"]))
        self.assertTrue(any(b["type"]=="table" for b in row["contentBlocks"]))
        self.assertNotIn("review_events",json.dumps(rows))
        self.assertNotIn("user_attempts",json.dumps(rows))

    def test_pending_human_review_not_rendered_with_opt_in(self):
        data,cat=eligible_fixture()
        data["classifications"][0]["reviewedBy"]=None
        cat[0]["approvedQuestionCount"]=0
        cat[0]["status"]="metadata_only"
        self.assertEqual(project_eligible(data,TAX,cat,[],ROOT),[])

    def test_unapproved_image_cannot_publish(self):
        data,cat=eligible_fixture()
        data["questions"][0]["contentBlocks"].append(
            {"type":"image","assetId":"unauthorized-image","altText":"desenho"})
        with self.assertRaisesRegex(PublicationError,"Imagem não aprovada"):
            project_eligible(data,TAX,cat,[],ROOT)

    def test_metadata_cannot_overclaim_published_coverage(self):
        catalog=copy.deepcopy(CAT)
        catalog[0]["approvedQuestionCount"]=5
        with self.assertRaisesRegex(PublicationError,"contagem publicada"):
            validate_exam_catalog(catalog,[])

    def test_catalog_must_stay_linked_to_source_and_booklet(self):
        data,cat=eligible_fixture()
        cat[0]["bookletCode"]="WRONG"
        with self.assertRaisesRegex(PublicationError,"aplicação/caderno"):
            project_eligible(data,TAX,cat,[],ROOT)
        data,cat=eligible_fixture()
        cat[0]["documents"][0]["sha256"]="f"*64
        with self.assertRaisesRegex(PublicationError,"documento de questão divergente"):
            project_eligible(data,TAX,cat,[],ROOT)

    def test_gabarito_final_required_if_published(self):
        data,cat=eligible_fixture()
        cat[0]["finalAnswerDocumentStatus"]="not_verified"
        with self.assertRaisesRegex(PublicationError,"gabarito não verificado"):
            project_eligible(data,TAX,cat,[],ROOT)
        data,cat=eligible_fixture()
        cat[0]["documents"]=[d for d in cat[0]["documents"] if d["type"]!="answer_key"]
        with self.assertRaisesRegex(PublicationError,"faltou arquivo"):
            project_eligible(data,TAX,cat,[],ROOT)

    def test_no_external_or_unverified_pdf_url(self):
        catalog=copy.deepcopy(CAT)
        catalog[0]["documents"][0]["url"]="https://fake-exam.example/prova.pdf"
        with self.assertRaisesRegex(PublicationError,"URL fora"):
            validate_exam_catalog(catalog,[])
        catalog=copy.deepcopy(CAT)
        catalog[0]["documents"][0]["verified"]=False
        with self.assertRaisesRegex(PublicationError,"sem confirmação"):
            validate_exam_catalog(catalog,[])

    def test_sanitized_text_math_table_are_plain_data_not_html(self):
        pieces=blocks_for_view([
          {"type":"text","text":"<img src=x onerror=alert(1)>"},
          {"type":"math","latex":r"\frac{1}{2}","altText":"um meio"},
          {"type":"table","rows":[["A","B"],["<script>x</script>","2"]]}
        ],{})
        self.assertEqual(pieces[0]["text"],"<img src=x onerror=alert(1)>")
        self.assertEqual(pieces[1]["altText"],"um meio")
        self.assertIn("<script>x</script>",readable(pieces))
        self.assertTrue(all("html" not in p for p in pieces))

    def test_asset_traversal_and_fake_approval_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(PublicationError,"Asset não permitido"):
                approved_assets([{"id":"abc","path":"../secrets.txt"}],temp)
            with self.assertRaisesRegex(PublicationError,"autorização"):
                approved_assets([{"id":"img","path":"assets/official/img.png",
                    "rightsStatus":"unknown","reviewedBy":None,
                    "altText":"texto","credit":"autor","sourceUrl":"https://example.test",
                    "sha256":"0"*64}],temp)

    def test_source_approval_requires_link_not_local_pdf(self):
        self.assertEqual(CAT[0]["rightsStatus"],"link_only")
        self.assertTrue(all(d["url"].startswith("https://") for d in CAT[0]["documents"]))
        self.assertFalse(any(d["type"]=="answer_key" for d in CAT[0]["documents"]))
        self.assertEqual(len(load("data/questions.json")),12)
        self.assertEqual(empty_bundle(),PUBLISHED)

    def test_eligible_fixture_excludes_learner_records_even_if_present(self):
        data,cat=eligible_fixture()
        data["user_attempts"][0]["answerVersion"]=1
        rows=project_eligible(data,TAX,cat,[],ROOT)
        self.assertNotIn("user_attempts",str(rows))
        self.assertNotIn("synthetic-user",str(rows))

if __name__=="__main__":
    unittest.main()
