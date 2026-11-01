"""Build V0 estático: whitelist para não vazar staging nem questões oficiais."""
import json
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = ("questions.json", "taxonomy.json", "sources.json", "exams.json", "inventory.json")
data = {name[:-5]: json.loads((ROOT / "data" / name).read_text(encoding="utf-8")) for name in DATA_FILES}
if any(q.get("kind") != "demo" for q in data["questions"]):
    raise SystemExit("Build bloqueado: a V0 não publica questões oficiais ou importadas.")
if data["exams"] != []:
    raise SystemExit("Build bloqueado: provas individualizadas exigem etapa de publicação posterior.")
js_payload = {name: data[name] for name in ("questions", "taxonomy", "sources", "inventory")}
(ROOT / "data/catalog.js").write_text(
    "window.VA_DATA = " + json.dumps(js_payload, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
dist = ROOT / "dist"
if dist.exists():
    shutil.rmtree(dist)
dist.mkdir(exist_ok=True)
shutil.copy2(ROOT / "index.html", dist / "index.html")
shutil.copytree(ROOT / "assets", dist / "assets")
(dist / "data").mkdir()
for name in DATA_FILES:
    shutil.copy2(ROOT / "data" / name, dist / "data" / name)
shutil.copy2(ROOT / "data/catalog.js", dist / "data/catalog.js")
# CSV derivado do mesmo JSON canônico; sem segunda fonte de verdade.
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
print(f"Site gerado em {dist}; staging e fixtures excluídos do artefato.")
