"""Gates negativos e positivos de revisão editorial da etapa 05."""
import copy
from fractions import Fraction
from math import comb, factorial
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from contracts_v1 import validate_bundle
from validate_pilot import PilotManifestError
from validate_review import ReviewError, validate_review,validate_files
PATH=ROOT/"pilot/unicamp-2026-math"
def source():
    read=lambda name:json.loads((PATH/name).read_text(encoding="utf-8"))
    return read("staging-metadata-v1.json"),read("review-checklist-v1.json"),read("manifest.json"),json.loads((ROOT/"data/taxonomy.json").read_text())

class ReviewStage5Tests(unittest.TestCase):
    def test_five_ai_proposals_all_remain_blocked(self):
        self.assertEqual(validate_files(),{"selected":5,"aiClassified":5,"aiDraftExplanations":5,"humanApproved":0,"officialFinalKeysConfirmed":0,"publicReady":0})

    def test_taxonomy_primary_and_interdisciplinary_tags_are_valid(self):
        b,r,m,t=source()
        validate_bundle(b,t)
        paths={c["questionId"].rsplit("q",1)[-1]:(c["primary"]["subtopicId"],[v["subtopicId"] for v in c["secondaryTags"]]) for c in b["classifications"]}
        self.assertEqual(paths["043"][0],"matematica.aritmetica-e-proporcionalidade.porcentagem")
        self.assertEqual(paths["045"][0],"matematica.algebra.polinomios")
        self.assertEqual(paths["049"][0],"matematica.probabilidade.eventos-simples")
        self.assertIn("matematica.analise-combinatoria.combinacoes",paths["049"][1])
        self.assertEqual(paths["051"][0],"matematica.algebra.equacoes-e-inequacoes")
        self.assertIn("matematica.conjuntos-e-logica.operacoes-com-conjuntos",paths["051"][1])
        self.assertEqual(paths["052"][0],"matematica.algebra.sistemas-lineares")

    def test_human_review_cannot_be_forged_on_checklist(self):
        b,r,m,t=source()
        r["items"][0]["humanApproval"].update(status="approved",reviewer="editor",reviewedAt="2026-11-02T12:00:00Z",decision="approve")
        with self.assertRaisesRegex(ReviewError,"revisão"):validate_review(b,r,m,t)

    def test_ai_classification_cannot_claim_human_signoff(self):
        b,r,m,t=source()
        b["classifications"][0]["reviewedBy"]={"type":"human","id":"invented"}
        with self.assertRaisesRegex(ReviewError,"não é revisão humana"):validate_review(b,r,m,t)

    def test_ai_explanation_cannot_claim_human_signoff(self):
        b,r,m,t=source()
        b["explanations"][0]["authorType"]="official"
        with self.assertRaisesRegex(ReviewError,"não pode se declarar aprovada"):validate_review(b,r,m,t)

    def test_provisional_comment_letter_must_not_become_final_gabarito(self):
        b,r,m,t=source()
        b["answers"][0]["value"]="a"
        with self.assertRaises((ReviewError,PilotManifestError)):validate_review(b,r,m,t)

    def test_rights_without_per_item_check_stay_link_only(self):
        b,r,m,t=source()
        r["items"][0]["checks"]["rights"]["status"]="authorized"
        with self.assertRaisesRegex(ReviewError,"Direitos"):validate_review(b,r,m,t)

    def test_full_text_is_never_committed_as_reviewed(self):
        b,r,m,t=source()
        b["questions"][0]["contentBlocks"]=[{"type":"text","text":"Texto inventado não verificado"}]
        with self.assertRaises((ReviewError,PilotManifestError)):validate_review(b,r,m,t)

    def test_wrong_source_hash_is_blocked(self):
        b,r,m,t=source()
        r["items"][0]["sourceSha256"]="0"*64
        with self.assertRaisesRegex(ReviewError,"Origem/hash"):validate_review(b,r,m,t)

    def test_missing_issue_or_nonpending_check_is_blocked(self):
        b,r,m,t=source()
        r["items"][1]["checks"]["choicesAndFormulas"].update(status="verified",issue="")
        with self.assertRaisesRegex(ReviewError,"choicesAndFormulas"):validate_review(b,r,m,t)

    def test_inventing_empirical_difficulty_is_blocked(self):
        b,r,m,t=source()
        r["items"][0]["checks"]["difficulty"]["empirical"]={"level":"easy"}
        with self.assertRaisesRegex(ReviewError,"Dificuldade"):validate_review(b,r,m,t)

    def test_no_published_question_even_with_external_optin(self):
        b,r,m,t=source()
        r["items"][3]["publicationEligible"]=True
        with self.assertRaisesRegex(ReviewError,"não pode ser publicado"):validate_review(b,r,m,t)

    def test_independent_math_calculations_agree_with_commentary(self):
        salary1=3*12*Fraction(3,2)
        salary2=12*(Fraction(6,5)+Fraction(36,25)+Fraction(216,125))
        self.assertAlmostEqual(float((salary1-salary2)/salary2),0.03021978,places=6)
        self.assertEqual(salary1>salary2,True)
        self.assertEqual(comb(5,2)*2,factorial(5)//6)
        primes=[n for n in range(2,21) if all(n%d for d in range(2,int(n**0.5)+1))]
        allowed=[n for n in primes if abs(n-5)>=2 and abs(n-11)<=9]
        self.assertEqual(allowed,[2,3,7,11,13,17,19])
        self.assertEqual((60+40,70*60+20*40,30*60+80*40),(100,5000,5000))

    def test_original_solution_is_separate_from_official_statement(self):
        b,r,m,t=source()
        self.assertTrue(all(q["contentBlocks"]==[] and q["choices"]==[] for q in b["questions"]))
        self.assertTrue(all(x["authorType"]=="ai_draft" and x["sourceDocumentId"] is None for x in b["explanations"]))
        self.assertEqual(len(json.loads((ROOT/"data/questions.json").read_text(encoding="utf-8"))),12)
        self.assertEqual(json.loads((ROOT/"data/exams.json").read_text(encoding="utf-8")),[])

if __name__=="__main__":unittest.main()
