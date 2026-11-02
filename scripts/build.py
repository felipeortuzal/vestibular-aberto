"""Build estático da etapa 06: PUBLICA somente projeção V1 aprovada.

O pacote de publicação V1 é explícito, versionado e validado; os cinco
candidatos da Unicamp em pilot/ não são a fonte do site e nunca são copiados.
"""
import csv
import json
import shutil
from pathlib import Path

from publication_v1 import project_eligible, validate_exam_catalog

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ("questions.json", "taxonomy.json", "sources.json", "exams.json", "inventory.json")
data = {name[:-5]: json.loads((ROOT / "data" / name).read_text(encoding="utf-8")) for name in PUBLIC_FILES}
read = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))

demo = data["questions"]
if any(q.get("kind") != "demo" or q.get("institutionId") != "autoral" for q in demo):
    raise SystemExit("Build bloqueado: data/questions.json permanece exclusivo de exercícios autorais.")
if len({q["id"] for q in demo}) != len(demo):
    raise SystemExit("Build bloqueado: IDs autorais duplicados.")

bundle = read("publication-v1.json")
assets = read("approved-assets.json")
official = project_eligible(bundle, data["taxonomy"], data["exams"], assets, repo_root=ROOT)
all_ids = [q["id"] for q in demo + official]
if len(set(all_ids)) != len(all_ids):
    raise SystemExit("Build bloqueado: IDs duplicados entre autorais e oficiais.")
validate_exam_catalog(data["exams"], official)
stats = {
    "demoQuestions": len(demo),
    "officialQuestions": len(official),
    "individualizedExams": len(data["exams"]),
    "publishedExams": sum(x["status"] == "published" for x in data["exams"]),
    "officialByInstitution": {inst: sum(q["institutionId"] == inst for q in official)
                              for inst in ("fuvest", "unicamp", "insper", "fgv")},
}
js_payload = {
    "questions": demo + official,
    "taxonomy": data["taxonomy"],
    "sources": data["sources"],
    "inventory": data["inventory"],
    "exams": data["exams"],
    "publication": stats,
}
(ROOT / "data/catalog.js").write_text(
    "window.VA_DATA = " + json.dumps(js_payload, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)

dist = ROOT / "dist"
if dist.exists():
    shutil.rmtree(dist)
dist.mkdir(exist_ok=True)
shutil.copy2(ROOT / "index.html", dist / "index.html")
(dist / "assets").mkdir()
# Lista explícita: NÃO copie anexos de revisão ou provas brutas acidentalmente.
for name in ("app.js", "core.js", "styles.css", "favicon.svg"):
    shutil.copy2(ROOT / "assets" / name, dist / "assets" / name)
for asset in assets:
    dest = dist / asset["path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / asset["path"], dest)
(dist / "data").mkdir()
for name in PUBLIC_FILES:
    shutil.copy2(ROOT / "data" / name, dist / "data" / name)
shutil.copy2(ROOT / "data/catalog.js", dist / "data/catalog.js")
(dist / "data" / "official-questions.json").write_text(
    json.dumps(official, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(dist / "data" / "publication-summary.json").write_text(
    json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Inventário CSV vem da matriz canônica, não de planilha duplicada.
FIELDS = ("id", "institutionId", "editionYear", "admissionSemester", "applicationId",
          "appliedAt", "school", "course", "campus", "phase", "day", "bookletCode",
          "selectionType", "documentType", "title", "sourceUrl", "landingPageUrl",
          "checkedAt", "accessStatus", "verification", "rightsStatus",
          "rightsEvidenceUrl", "rightsNote", "notes", "supersedes", "version")
with (dist / "data/inventory.csv").open("w", encoding="utf-8-sig", newline="") as target:
    writer = csv.DictWriter(target, fieldnames=FIELDS)
    writer.writeheader()
    for record in data["inventory"]["documents"]:
        writer.writerow({field: record[field] if record[field] is not None else "" for field in FIELDS})

(dist / ".nojekyll").touch()
print("Build etapa 06: " + json.dumps(stats, ensure_ascii=False)
      + "; staging e fixtures excluídos do artefato.")
