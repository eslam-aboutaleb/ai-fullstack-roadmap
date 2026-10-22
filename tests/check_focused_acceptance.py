"""Keep accepted syllabus evidence attached to real source, practice and pages."""
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from editorial import validate_review
from revised_content_gate import validate_record, validate_unit


def check():
    plan = json.loads((ROOT / 'content/shared/focused-acceptance.json').read_text())
    ids = json.loads((ROOT / 'content/shared/study_ids.json').read_text())
    practices = {x['id']: x for x in json.loads((ROOT / 'content/assessments.json').read_text())['items']}
    seen = set()
    for row in plan['records']:
        identity = 'interview/' + row['chapter'] + '/' + row['question']
        assert identity not in seen, 'duplicate coverage row'
        seen.add(identity)
        assert ids[identity] == row['study_id'], 'changed study identity'
        question = next(x for x in json.loads((ROOT / row['source']).read_text()) if x['Q'] == row['question'])
        assert not validate_record(question, identity, require_review=True), identity
        assessment = practices[row['assessment']]
        assert assessment['topic'] == row['study_id'] and assessment['chapter'] == row['chapter']
        assert assessment['objective'] == row['outcome_id'] and row['subtopics']
        from build import interview
        article = interview(dict(question, id=row['study_id']))
        if question.get('worked_case') == question.get('Why'):
            assert article.count(html.escape(question['worked_case'], quote=True)) == 1, 'duplicate worked case'
        rendered = (ROOT / '_site' / (row['chapter'] + '.html')).read_text()
        assert f'id="q{row["study_id"]}"' in rendered and 'id="walkthrough"' in rendered
        assert row['assessment'] in (ROOT / '_site/practice-data.js').read_text()
    for key, unit in plan['units'].items():
        course = json.loads((ROOT / unit['source']).read_text())
        actual = next(x for x in course['units'] if x['id'] == key)
        assert actual['study_id'] == unit['study_id']
        assert not validate_unit(actual, unit['review_identity'], require_review=True)
        validate_review(actual, unit['review_identity'])
        assert (ROOT / '_site' / unit['reader_url']).is_file()
    for issue, evidence in plan['issues'].items():
        assert (ROOT / evidence['lab']).is_file()
        assert (ROOT / evidence['evidence']).is_file()
        capstone = practices[evidence['capstone']]
        assert capstone['kind'] == 'self-review' and not capstone['independent']
        assert capstone['rubric'] and capstone['model_answer']
        assert all(key in plan['units'] for key in evidence['units'])
        assert any(str(row['issue']) == issue for row in plan['records'])
    print(json.dumps({'focused_acceptance_mapping': 'pass', 'issues': list(plan['issues']),
                      'reviewed_answers': len(seen), 'reviewed_units': len(plan['units'])}))


if __name__ == '__main__':
    check()
