"""Validação do seed demonstrativo V0.1; somente biblioteca padrão."""
import json
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
