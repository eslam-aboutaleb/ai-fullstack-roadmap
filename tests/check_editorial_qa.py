"""Editorial QA: duplicate and near-duplicate question detection."""
from pathlib import Path
import json, sys, re, difflib

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / 'content'

def normalize(text):
    return re.sub(r'\s+', ' ', text.lower().strip())


def check():
    course = json.loads((CONTENT / 'course.json').read_text())
    STAGES = [tuple(stage) for stage in course['stages']]

    all_questions = []
    for number, (_, _, _, slugs) in enumerate(STAGES, 1):
        for slug in slugs:
            q_path = CONTENT / 'chapters' / slug / 'questions.json'
            if not q_path.exists():
                continue
            questions = json.loads(q_path.read_text())
            for shard in sorted(q_path.parent.glob('questions-*.json')):
                questions.extend(json.loads(shard.read_text()))
            for q in questions:
                qid = q.get('id', normalize(q['Q'])[:20])
                all_questions.append((slug, qid, q['Q']))

    # Exact duplicate detection
    seen = {}
    exact_dups = []
    for slug, qid, qtext in all_questions:
        norm = normalize(qtext)
        if norm in seen:
            exact_dups.append((seen[norm], (slug, qid, qtext)))
        else:
            seen[norm] = (slug, qid, qtext)

    # Near-duplicate detection (>90% similarity)
    near_dups = []
    texts = [(slug, qid, normalize(qtext)) for slug, qid, qtext in all_questions]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = difflib.SequenceMatcher(None, texts[i][2], texts[j][2]).ratio()
            if sim > 0.90:
                near_dups.append((texts[i], texts[j], round(sim, 2)))

    errors = []
    if exact_dups:
        errors.append(f'Exact duplicate questions: {len(exact_dups)}')
        for (s1, q1, t1), (s2, q2, t2) in exact_dups[:5]:
            errors.append(f'  {s1}#{q1} ~ {s2}#{q2}: {t1[:60]}...')
    if near_dups:
        errors.append(f'Near-duplicate questions (>90%): {len(near_dups)}')
        for (s1, q1, t1), (s2, q2, t2), sim in near_dups[:5]:
            errors.append(f'  {s1}#{q1} ~ {s2}#{q2} ({sim}): {t1[:60]}...')

    assert not errors, ('Duplicate detection failed', errors[:10])

    # Glossary/prerequisite link verification
    references = json.loads((CONTENT / 'shared/references.json').read_text())
    link_errors = []
    for number, (_, _, _, slugs) in enumerate(STAGES, 1):
        for slug in slugs:
            review_path = CONTENT / 'chapters' / slug / 'review.json'
            if not review_path.exists():
                continue
            review = json.loads(review_path.read_text())
            for key in review.get('links', '').split(','):
                key = key.strip()
                if key and key not in references:
                    link_errors.append(f'{slug}: broken reference link "{key}"')

    assert not link_errors, ('Broken reference links', link_errors[:10])

    from course_data import load
    from editorial_evidence import evidence_report, inspect_new_question, validate_new_records
    chapters = load()
    assert validate_new_records(chapters) >= 0
    evidence = evidence_report(chapters)
    assert len(evidence['chapters']) == len(chapters)
    assert sum(row['total_interview_questions'] for row in evidence['chapters']) == len(all_questions)
    published = json.loads((ROOT/'_site/questions/editorial-evidence.json').read_text())
    assert published == evidence, 'Published editorial evidence does not match current sources'
    expected_units = sum(len(json.loads(path.read_text())['units']) for path in (CONTENT/'courses').glob('*.json'))
    records = evidence['records']
    assert sum(row['kind'] == 'lesson' for row in records) == sum(len(chapter['lessons']) for chapter in chapters)
    assert sum(row['kind'] == 'interview' for row in records) == len(all_questions)
    assert sum(row['kind'] == 'unit' for row in records) == expected_units
    assert len({row['identity'] for row in records}) == len(records)
    assert evidence['verified_review_records'] == sum(row['review_verified'] for row in records)
    assert evidence['record_review_status'].get('legacy-unreviewed', 0) > 0
    assert evidence['verified_review_records'] >= 56

    synthetic = {'id': 999999, 'Q': 'How should we verify?', 'A': 'TODO: write',
                 'citations': ['http://example.com'],
                 'follow_ups': [], 'reviewer_status': {'status': 'draft'}}
    problems = inspect_new_question(synthetic)
    assert len(problems) >= 3 and inspect_new_question({'id': 1}) == []
    from revised_content_gate import check_fixtures as revised_check_fixtures
    revised_check_fixtures()
    print('Editorial evidence report: source counts, published artifact, and negative gates pass')

    print(json.dumps({
        'issue': 20,
        'total_questions': len(all_questions),
        'exact_duplicates': len(exact_dups),
        'near_duplicates': len(near_dups),
        'broken_links': len(link_errors),
        'scope': 'Lexical question similarity and local reference-key integrity; not external URL freshness or semantic fact checking',
        'editorial_qa': 'pass'
    }, indent=2))


if __name__ == '__main__':
    check()
