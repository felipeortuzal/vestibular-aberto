"""Build V0 estático: whitelist para não vazar staging nem questões oficiais."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = ("questions.json", "taxonomy.json", "sources.json", "exams.json")
data = {name[:-5]: json.loads((ROOT / "data" / name).read_text(encoding="utf-8")) for name in DATA_FILES}
if any(q.get("kind") != "demo" for q in data["questions"]):
    raise SystemExit("Build bloqueado: a V0 não publica questões oficiais ou importadas.")
if data["exams"] != []:
    raise SystemExit("Build bloqueado: provas individualizadas exigem etapa de publicação posterior.")
js_payload = {name: data[name] for name in ("questions", "taxonomy", "sources")}
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
(dist / ".nojekyll").touch()
print(f"Site gerado em {dist}; staging e fixtures excluídos do artefato.")
