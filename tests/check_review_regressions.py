"""Behavior checks for defects found reviewing issues 1–16."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import shutil
import tempfile
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'scripts'))
import course_data
from course_data import load, _check_schema, LESSON_SCHEMA, QUESTION_SCHEMA
from validate_curriculum import load as load_curriculum, validate
from rich_content import figures


def must_reject(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError('Invalid input was accepted')


def check():
    chapters = load()
    lesson = next(q for c in chapters for q in c['lessons'] if 'conceptual_narrative' in q)
    question = next(q for c in chapters for q in c['questions'] if 'spoken' in q)
    for schema, original, field, value in [
        (LESSON_SCHEMA, lesson, 'outcomes', [123, 'valid']),
        (LESSON_SCHEMA, lesson, 'estimated_time_minutes', True),
        (LESSON_SCHEMA, lesson, 'estimated_time_minutes', -1),
        (LESSON_SCHEMA, lesson, 'worked_examples', [{'title': 'Missing code'}]),
        (QUESTION_SCHEMA, question, 'difficulty', 'made-up'),
        (QUESTION_SCHEMA, question, 'reviewer_status', {'reviewer':'x','reviewed_at':'2026-99-99','status':'approved'}),
    ]:
        mutated = {**original, field: value}
        must_reject(lambda: _check_schema(mutated, schema, 'fixture', 'review'))
    # Exercise the loader, not only its helper: this guards the formerly
    # unreachable interview validation branch, without relying on `added`.
    with tempfile.TemporaryDirectory() as directory:
        copied = Path(directory)/'content'
        shutil.copytree(ROOT/'content', copied)
        path = copied/'chapters/foundations/questions.json'
        rows = json.loads(path.read_text())
        enriched = next(q for q in rows if 'spoken' in q)
        enriched['added'] = False
        enriched['difficulty'] = 'invalid-facet'
        path.write_text(json.dumps(rows))
        old_content = course_data.CONTENT
        try:
            course_data.CONTENT = copied
            must_reject(load)
        finally:
            course_data.CONTENT = old_content
    course, curriculum = load_curriculum()
    for mutation in ('duplicate', 'wrong-track', 'entry', 'cycle', 'counts'):
        fixture = deepcopy(curriculum)
        if mutation == 'duplicate': fixture['tracks'][0]['chapters'].append(fixture['tracks'][1]['chapters'][0])
        elif mutation == 'wrong-track': fixture['chapters']['foundations']['track'] = 'agents'
        elif mutation == 'entry': fixture['tracks'][0]['entry_point'] = 'retrieval'
        elif mutation == 'cycle': fixture['chapters']['foundations']['prerequisites'] = ['foundations']
        else: fixture['coverage_manifest']['total_questions'] += 1
        must_reject(lambda: validate(course, fixture))
    must_reject(lambda: figures([{'svg':'<svg><script>alert(1)</script></svg>', 'alt':'x','description':'x'}], 'fixture'))
    must_reject(lambda: figures([{'svg':'<svg onload="alert(1)"/>', 'alt':'x','description':'x'}], 'fixture'))
    for name in ('reservation_race.py', 'effect_oracle.py'):
        result = subprocess.run([sys.executable, str(ROOT/'labs'/name)], capture_output=True, text=True, timeout=20)
        assert result.returncode == 0, (name, result.stderr)
    for source in (ROOT/'assets/js').glob('*.js'):
        subprocess.run(['node', '--check', str(source)], check=True, capture_output=True)
    for source in (ROOT/'labs').glob('*.js'):
        result = subprocess.run(['node', str(source)], check=True, capture_output=True, text=True, timeout=5)
        assert not result.stderr, (source, result.stderr)
    print(json.dumps({'schema_negative_fixtures': 7, 'curriculum_negative_fixtures': 5,
                      'svg_rejection_fixtures': 2, 'local_python_labs': 2, 'javascript_labs': 3}))


if __name__ == '__main__':
    check()
