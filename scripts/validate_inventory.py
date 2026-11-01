"""Validação do inventário da etapa 03 (metadados e links públicos, sem reprodução).

O formato de inventory.json é propositalmente separado do contrato de
ingestão V1: uma listagem de documentos não é um exame/caderno verificado.
"""
from datetime import date
from urllib.parse import urlparse

IDS = {"fuvest", "unicamp", "insper", "fgv"}
DOC_TYPES = {"booklet", "answer_key", "commented_booklet", "expected_answers", "collection"}
VERIFICATION = {"search_listing", "search_pdf_link", "pdf_cover_checked",
                "pdf_link_opened", "search_filtered_listing", "process_page_opened"}
ACCESS = {"listing_only", "search_only", "pdf_opened", "dynamic_listing"}
ALLOWED_HOSTS = {"www.fuvest.br", "www.comvest.unicamp.br",
                 "vestibular.fgv.br", "www.vunesp.com.br",
                 "www.insper.edu.br"}


class InventoryError(ValueError):
    pass


def check(condition, message):
    if not condition:
        raise InventoryError(message)


def _url(value, label):
    if value is None:
        return
    address = urlparse(value)
    check(address.scheme == "https" and address.hostname in ALLOWED_HOSTS,
          f"{label}: URL não oficial ou não HTTPS: {value}")


def validate_inventory(inventory):
    check(inventory.get("schemaVersion") == 1, "Versão do inventário incorreta")
    check(inventory.get("policy", {}).get("publicPresentation") == "metadata_and_links_only",
          "Política de acesso externo inválida")
    check(inventory["policy"]["officialQuestionsImported"] == 0
          and inventory["policy"]["importedExams"] == 0,
          "Inventário não pode declarar conteúdo oficial importado")
    date.fromisoformat(inventory["checkedAt"])
    coverage = inventory.get("coverage", [])
    expected = {(i, y) for i in IDS for y in (2024, 2025, 2026)}
    keys = [(r["institutionId"], r["editionYear"]) for r in coverage]
    check(set(keys) == expected and len(keys) == len(expected),
          "Cobertura deve distinguir as quatro instituições e 2024–2026 sem duplicação")
    for r in coverage:
        _url(r["landingPageUrl"], "Página do recorte")
        check(r["pending"] and r["verification"], "Cobertura sem pendência/status")
    documents = inventory.get("documents", [])
    ids = [r["id"] for r in documents]
    check(len(ids) == len(set(ids)), "ID duplicado no inventário")
    index = {r["id"]: r for r in documents}
    keys = set()
    for d in documents:
        check(d["institutionId"] in IDS and d["editionYear"] in (2024, 2025, 2026),
              f"{d['id']}: instituição/edição inválidas")
        check(d["id"].startswith(f"inv-{d['institutionId']}-{d['editionYear']}-"),
              f"{d['id']}: ID não estável por origem")
        check(d["documentType"] in DOC_TYPES and d["verification"] in VERIFICATION
              and d["accessStatus"] in ACCESS, f"{d['id']}: estado inválido")
        _url(d["landingPageUrl"], d["id"])
        _url(d["sourceUrl"], d["id"])
        _url(d["rightsEvidenceUrl"], d["id"])
        check(d["rightsStatus"] == "link_only" and d["rightsNote"],
              f"{d['id']}: direitos incertos não liberam reprodução")
        check(d["selectionType"] == "vestibular" and d["title"] and d["notes"],
              f"{d['id']}: metadados insuficientes")
        check(d["checkedAt"] == inventory["checkedAt"], f"{d['id']}: consulta divergente")
        if d["appliedAt"]:
            date.fromisoformat(d["appliedAt"])
        if d["admissionSemester"]:
            check(d["admissionSemester"] in ("2024.1","2024.2","2025.1","2025.2","2026.1","2026.2"),
                  f"{d['id']}: semestre incorreto")
        if d["accessStatus"] == "pdf_opened" or d["verification"] in ("pdf_cover_checked","pdf_link_opened","search_pdf_link"):
            check(d["sourceUrl"] is not None, f"{d['id']}: PDF sem link comprovado")
        if d["documentType"] == "collection":
            check(d["sourceUrl"] is None and d["bookletCode"] is None,
                  f"{d['id']}: índice não pode fingir PDF ou caderno")
        key=(d["institutionId"],d["editionYear"],d["documentType"],d["title"],d["admissionSemester"],d["applicationId"])
        check(key not in keys, f"{d['id']}: duplicidade de documento/coleção")
        keys.add(key)
    for d in documents:
        prev=d["supersedes"]
        if prev is None:
            continue
        check(prev in index and prev != d["id"], f"{d['id']}: retificação sem antecedente")
        old=index[prev]
        check(old["institutionId"] == d["institutionId"]
              and old["editionYear"] == d["editionYear"]
              and old["documentType"] == d["documentType"],
              f"{d['id']}: retificação vinculada a outra prova")
    return {"entries": len(documents), "directUrls": sum(x["sourceUrl"] is not None for x in documents),
            "collections": sum(x["documentType"] == "collection" for x in documents),
            "coverage": len(coverage), "physicalListings": sum(x["documentType"] != "collection" for x in documents)}
