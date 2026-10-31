"""Gera o adaptador de dados e a pasta estática. Sem dependências externas."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = {name: json.loads((ROOT / 'data' / (name + '.json')).read_text()) for name in ('questions', 'taxonomy', 'sources')}
(ROOT / 'data/catalog.js').write_text('window.VA_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
dist = ROOT / 'dist'
if dist.exists():
    shutil.rmtree(dist)
dist.mkdir(exist_ok=True)
shutil.copy2(ROOT / 'index.html', dist / 'index.html')
for directory in ('assets', 'data'):
    shutil.copytree(ROOT / directory, dist / directory, dirs_exist_ok=True)
(dist / '.nojekyll').touch()
print(f'Site gerado em {dist}')
