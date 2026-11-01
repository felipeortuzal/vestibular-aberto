"""Testes do pipeline/manifesto; PDF sintético é gerado apenas em memória."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from contracts_v1 import validate_bundle,export_public_bundle
from validate_pilot import PilotManifestError,validate_pilot
from ingest_pilot import section,alternatives,split_columns,inspect_pdf

M=json.loads((ROOT/"pilot/unicamp-2026-math/manifest.json").read_text())
B=json.loads((ROOT/"pilot/unicamp-2026-math/staging-metadata-v1.json").read_text())
T=json.loads((ROOT/"data/taxonomy.json").read_text())

class PilotTests(unittest.TestCase):
    def test_staging_v1_is_valid_and_not_public(self):
        self.assertEqual(validate_pilot(copy.deepcopy(M),copy.deepcopy(B))["selected"],5)
        self.assertEqual(len(validate_bundle(copy.deepcopy(B),T)["questions"]),5)
        self.assertEqual(export_public_bundle(copy.deepcopy(B),T,enable_official=True)["questions"],[])
        self.assertTrue(all(not q["contentBlocks"] for q in B["questions"]))

    def test_correct_source_and_model_required(self):
        m=copy.deepcopy(M);m["sourceUrl"]="https://outro.tld/exame.pdf"
        with self.assertRaisesRegex(PilotManifestError,"Fonte"):validate_pilot(m,B)
        m=copy.deepcopy(M);m["bookletCode"]="P"
        with self.assertRaisesRegex(PilotManifestError,"Modelo"):validate_pilot(m,B)

    def test_no_fake_hash_no_fake_final_answers(self):
        b=copy.deepcopy(B);b["documents"][0]["sha256"]="a"*64
        with self.assertRaisesRegex(PilotManifestError,"hash"):validate_pilot(M,b)
        b=copy.deepcopy(B);b["answers"][0]["value"]="a"
        with self.assertRaisesRegex(PilotManifestError,"gabarito"):validate_pilot(M,b)

    def test_correct_page_and_number_per_question(self):
        m=copy.deepcopy(M);m["selectedQuestions"][4]["physicalPages"]=[51]
        with self.assertRaisesRegex(PilotManifestError,"páginas"):validate_pilot(m,B)
        m=copy.deepcopy(M);m["selectedQuestions"][1]["commentaryAnswerCandidate"]="a"
        with self.assertRaisesRegex(PilotManifestError,"candidata"):validate_pilot(m,B)

    def test_two_columns_and_native_text_on_synthetic_pdf(self):
        doc=fitz.open()
        p=doc.new_page(width=600,height=840)
        p.insert_text((40,80),"QUESTAO 43")
        p.insert_text((40,110),"Uma questao totalmente sintetica, apenas para testar a extracao.")
        for i,v in enumerate(("a) alternativa um","b) alternativa dois","c) alternativa tres","d) alternativa quatro")):
            p.insert_text((40,145+i*21),v)
        p.insert_text((40,240),"Objetivo da Questao")
        p.insert_text((340,85),"QUESTAO 44")
        left,right=split_columns(p)
        self.assertIn("43",left)
        self.assertIn("44",right)
        candidate=section(left,"43")
        self.assertTrue(candidate)
        choices=alternatives(candidate)
        self.assertIsNotNone(choices)
        self.assertEqual(list(choices["choices"].keys()),list("abcd"))
        self.assertNotIn("Objetivo",choices["stem"])

    def test_pdf_magic_page_count_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            pdf=fitz.open();pdf.new_page()
            path=Path(d)/"synthetic.pdf"
            pdf.save(path);pdf.close()
            proof=inspect_pdf(path,1)
            self.assertEqual(len(proof["sha256"]),64)
            self.assertEqual(proof["pageCount"],1)
            with self.assertRaisesRegex(ValueError,"Páginas divergentes"):
                inspect_pdf(path,71)
            (Path(d)/"bad.pdf").write_bytes(b"not a pdf")
            with self.assertRaisesRegex(ValueError,"não é PDF"):
                inspect_pdf(Path(d)/"bad.pdf",1)

    def test_unparseable_math_keeps_candidate_blocked(self):
        self.assertIsNone(alternatives("a) teste apenas sem b c d"))
        self.assertIsNone(section("QUESTAO 43 sem delimitador","43"))

    def test_public_seed_and_browser_progress_unchanged(self):
        self.assertEqual(len(json.loads((ROOT/"data/questions.json").read_text())),12)
        self.assertEqual(json.loads((ROOT/"data/exams.json").read_text()),[])
        self.assertFalse((ROOT/"data/questions-official.json").exists())

if __name__=="__main__":
    unittest.main()
