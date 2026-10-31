"""Etapa 03: checks do inventário, sem baixar nem publicar provas."""
import copy
import csv
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "scripts"))
from validate_inventory import validate_inventory, InventoryError

BASE=json.loads((ROOT / "data/inventory.json").read_text(encoding="utf-8"))


class InventoryTests(unittest.TestCase):
    def fresh(self):
        return copy.deepcopy(BASE)

    def fail(self, data, message):
        with self.assertRaisesRegex(InventoryError, message):
            validate_inventory(data)

    def test_real_metadata_inventory_counts(self):
        info=validate_inventory(self.fresh())
        self.assertEqual(info, {"entries":29,"directUrls":8,"collections":5,
                                "coverage":12,"physicalListings":24})

    def test_coverage_covers_all_years_without_claiming_pdf(self):
        data=self.fresh()
        self.assertEqual({x["institutionId"] for x in data["coverage"]},
                         {"fuvest","unicamp","insper","fgv"})
        self.assertEqual({x["editionYear"] for x in data["coverage"]},{2024,2025,2026})
        self.assertTrue(all(x["rightsStatus"]=="link_only" for x in data["documents"]))

    def test_fgv_is_not_duplicated_by_course_guess(self):
        records=[x for x in BASE["documents"] if x["institutionId"]=="fgv"]
        self.assertEqual(len(records),3)
        self.assertTrue(all(x["school"] is None and x["campus"] is None
                            and x["documentType"]=="collection" for x in records))

    def test_insper_semester_and_application_separated(self):
        records=[x for x in BASE["documents"] if x["institutionId"]=="insper"]
        self.assertEqual({x["admissionSemester"] for x in records},{"2026.1","2026.2"})
        self.assertEqual({x["applicationId"] for x in records},{"INSP2502","INSP2504"})
        self.assertTrue(all(x["sourceUrl"] is None for x in records))

    def test_original_and_corrected_fuvest_2024_key_related(self):
        rows={x["id"]:x for x in BASE["documents"]}
        corrected=[x for x in rows.values() if x["institutionId"]=="fuvest"
                   and "retificado" in x["title"].lower() and x["editionYear"]==2024]
        self.assertEqual(len(corrected),1)
        old=rows[corrected[0]["supersedes"]]
        self.assertEqual(old["documentType"],"answer_key")
        self.assertNotEqual(old["sourceUrl"],corrected[0]["sourceUrl"])

    def test_legacy_exams_remain_empty(self):
        exams=json.loads((ROOT / "data/exams.json").read_text(encoding="utf-8"))
        questions=json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
        self.assertEqual(exams,[])
        self.assertEqual(len(questions),12)
        self.assertTrue(all(q["kind"]=="demo" and q["examId"] is None for q in questions))

    def test_duplicate_document_is_rejected(self):
        obj=self.fresh()
        obj["documents"].append(copy.deepcopy(obj["documents"][0]))
        self.fail(obj,"ID duplicado")

    def test_unofficial_pdf_is_rejected(self):
        obj=self.fresh()
        obj["documents"][0]["sourceUrl"]="https://random-fake.test/prova.pdf"
        self.fail(obj,"não oficial")

    def test_cannot_claim_full_republication(self):
        obj=self.fresh()
        obj["documents"][0]["rightsStatus"]="authorized"
        self.fail(obj,"direitos")

    def test_catalogue_collection_is_not_pdf(self):
        obj=self.fresh()
        coll=next(x for x in obj["documents"] if x["documentType"]=="collection")
        coll["sourceUrl"]="https://www.vunesp.com.br/INSP2502"
        self.fail(obj,"índice não pode fingir PDF")

    def test_missing_pdf_link_is_rejected(self):
        obj=self.fresh()
        doc=next(x for x in obj["documents"] if x["accessStatus"]=="pdf_opened")
        doc["sourceUrl"]=None
        self.fail(obj,"PDF sem link")

    def test_retification_cannot_point_to_other_institution(self):
        obj=self.fresh()
        corrected=next(x for x in obj["documents"] if x["supersedes"] is not None)
        corrected["supersedes"]=next(x["id"] for x in obj["documents"]
                                    if x["institutionId"]=="unicamp")
        self.fail(obj,"retificação vinculada")

    def test_coverage_gap_is_rejected(self):
        obj=self.fresh()
        obj["coverage"].pop()
        self.fail(obj,"Cobertura")

    def test_edition_is_not_application_date(self):
        obj=self.fresh()
        doc=next(x for x in obj["documents"] if x["institutionId"]=="unicamp" and
                 x["editionYear"]==2026 and x["phase"]=="1")
        self.assertEqual(doc["appliedAt"],"2025-10-26")
        self.assertEqual(doc["editionYear"],2026)

    def test_only_allowed_stage3_fields(self):
        for d in BASE["documents"]:
            self.assertNotIn("statement",d)
            self.assertNotIn("choices",d)
            self.assertNotIn("answer",d)
            self.assertNotIn("pdfBytes",d)


if __name__=="__main__":
    unittest.main()
