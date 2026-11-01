"""Valida o seed demonstrativo e os JSON Schemas V1 para staging editorial."""
import json
from jsonschema import Draft202012Validator, FormatChecker
from contracts_v1 import validate_bundle, empty_bundle
from validate_inventory import validate_inventory
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
load = lambda p: json.loads((ROOT / p).read_text())
questions = load('data/questions.json')
taxonomy = load('data/taxonomy.json')
sources = load('data/sources.json')
paths = {(s['id'], t['id'], st['id']) for s in taxonomy['subjects'] for t in s['topics'] for st in t['subtopics']}
assert len({q['id'] for q in questions}) == len(questions), 'IDs de questão duplicados'
assert len({s['id'] for s in sources}) == len(sources), 'Fontes duplicadas'
for q in questions:
    assert q['kind'] == 'demo', 'V0 aceita somente demonstração. Execute os prompts 02–06 antes de publicar questões oficiais.'
    assert q['institutionId'] == 'autoral' and q['examId'] is None
    assert q['editionYear'] is None and q['phase'] is None, 'Não atribua edição oficial a uma demonstração'
    c = q['classification']
    assert (c['subjectId'], c['topicId'], c['subtopicId']) in paths, f'Taxonomia inválida: {q["id"]}'
    assert q['format'] == 'multiple_choice'
    choice_ids = [c['id'] for c in q['choices']]
    assert 2 <= len(choice_ids) <= 6 and len(choice_ids) == len(set(choice_ids))
    assert q['answer']['choiceId'] in choice_ids and q['answer']['status'] == 'authoral'
    assert q['statement'].strip() and q['explanation'].strip()
    assert q['rights']['status'] == 'authoral' and q['provenance']['type'] == 'authoral'
    assert all(isinstance(c['text'], str) and c['text'].strip() for c in q['choices'])
assert {s['id'] for s in sources} == {'fuvest', 'unicamp', 'insper', 'fgv'}
assert all(s['url'].startswith('https://') for s in sources)
assert load('data/exams.json') == [], 'Na V0 existem diretórios, não provas importadas'
for path in ['index.html', 'assets/styles.css', 'assets/core.js', 'assets/app.js']:
    assert (ROOT / path).is_file(), f'Arquivo ausente: {path}'
print(f'OK: {len(questions)} questões autorais, {len(paths)} subassuntos, {len(sources)} diretórios. Nenhuma questão oficial publicada.')


# O seed permanece exclusivo da V0; o contrato de staging é validado em separado.
for schema_path in ("schemas/v1/bundle.schema.json", "schemas/v1/taxonomy.schema.json"):
    Draft202012Validator.check_schema(load(schema_path))
taxonomy_errors = list(Draft202012Validator(
    load("schemas/v1/taxonomy.schema.json"), format_checker=FormatChecker()
).iter_errors(taxonomy))
assert not taxonomy_errors, f"Taxonomia fora do esquema V1: {taxonomy_errors[0].message if taxonomy_errors else ''}"
validate_bundle(empty_bundle(), taxonomy)
synthetic = load("tests/fixtures/v1/synthetic_bundle.json")
validate_bundle(synthetic, taxonomy)
print("OK: JSON Schemas V1, integridade do staging sintético e taxonomia versionada.")

summary_inventory = validate_inventory(load("data/inventory.json"))
print(f"OK: Inventário 2024–2026: {summary_inventory['entries']} registros, {summary_inventory['directUrls']} URLs de arquivo, {summary_inventory['coverage']} recortes de cobertura; sem provas importadas.")

# O lote oficial piloto só contém metadados. Não adicioná-lo ao catálogo publicado.
from validate_pilot import validate_pilot
pilot_manifest=load("pilot/unicamp-2026-math/manifest.json")
pilot_seed=load("pilot/unicamp-2026-math/staging-metadata-v1.json")
pilot_validation=validate_pilot(pilot_manifest,pilot_seed)
validate_bundle(pilot_seed,taxonomy)
print(f"OK: piloto {pilot_validation['selected']} registros em staging de metadados; zero gabaritos finais verificados e zero publicados.")
