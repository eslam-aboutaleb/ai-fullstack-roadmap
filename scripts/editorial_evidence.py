"""Source-derived editorial evidence; never substitute CI checks for expert review."""
from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
from urllib.parse import urlsplit

ADOPTION_ID = 1211  # immutable October 21 2026 source baseline
PLACEHOLDERS = ('lorem ipsum', 'todo: write', 'tbd answer', 'as an ai language model')


def acceptable_url(value):
    if not isinstance(value, str):
        return False
    result = urlsplit(value)
    return result.scheme == 'https' and bool(result.netloc)


def inspect_new_question(question, baseline=ADOPTION_ID):
    """A fail-closed quality check for *new* questions, not retroactive approval of legacy."""
    if not isinstance(question.get('id'), int) or question['id'] <= baseline:
        return []
    problems = []
    answer = question.get('A', '')
    if not isinstance(answer, str) or len(answer.strip()) < 350:
        problems.append('answer is too brief for a standalone detailed interview response')
    if isinstance(answer, str) and any(marker in answer.casefold() for marker in PLACEHOLDERS):
        problems.append('answer has placeholder text')
    sources = question.get('citations') or question.get('references') or []
    if not sources or not isinstance(sources, list) or any(not acceptable_url(url) for url in sources):
        problems.append('missing or invalid HTTPS primary references')
    followups = question.get('follow_ups')
    if not isinstance(followups, list) or not any(
        isinstance(row, dict) and len(str(row.get('Q', '')).strip()) >= 12
        and len(str(row.get('A', '')).strip()) >= 60 for row in followups
    ):
        problems.append('at least one genuinely answered interview follow-up is required')
    review = question.get('reviewer_status', {})
    if not isinstance(review, dict) or review.get('status') not in ('draft', 'reviewed', 'approved'):
        problems.append('review state must be explicitly draft, reviewed, or approved')
    return problems


def evidence_report(chapters):
    """Aggregate factual source inventory, not a claim about unobserved competence."""
    from editorial import content_digest, validate_review
    assessments = json.loads((ROOT/'content/assessments.json').read_text())['items']
    records = []
    def evidence(record, identity, kind, source, chapter):
        review = record.get('reviewer_status', {})
        status = review.get('status', 'legacy-unreviewed')
        # Fail closed on a claimed review, including lessons and companion units.
        validate_review(record, identity)
        sources = record.get('citations') or record.get('references') or []
        topic = record.get('id', record.get('study_id'))
        return {'identity': identity, 'kind': kind, 'source': source,
                'study_id': topic, 'chapter': chapter, 'sha256': content_digest(record),
                'review_status': status, 'review_verified': status in ('reviewed', 'approved'),
                'reviewer': review.get('reviewer'), 'reviewed_at': review.get('reviewed_at'),
                'primary_sources': sources, 'https_source_links_present': bool(sources) and all(acceptable_url(url) for url in sources),
                'assessment_ids': [a['id'] for a in assessments if a.get('topic') == topic],
                'lab': record.get('local_lab', record.get('lab')),
                'source_check_limit': 'URL shape and recorded review are checked; exhaustive live reference freshness and semantic correctness are not automated'}
    chapters_out = []
    states = Counter()
    for chapter in chapters:
        questions = chapter['questions']
        for kind, group in [('lesson', 'lessons'), ('interview', 'questions')]:
            for record in chapter[group]:
                records.append(evidence(record, f'{kind}/{chapter["slug"]}/{record["Q"]}', kind,
                                        f'content/chapters/{chapter["slug"]}/{"lessons.json" if kind == "lesson" else "questions*.json"}', chapter['slug']))
        for question in questions:
            states[question.get('reviewer_status', {}).get('status', 'legacy-unreviewed')] += 1
        chapters_out.append({
            'chapter': chapter['slug'],
            'total_lessons': len(chapter['lessons']),
            'total_interview_questions': len(questions),
            'short_primary_answers': [q['id'] for q in questions if len(q.get('A', '').strip()) < 350],
            'no_question_level_citations': [q['id'] for q in questions
                                           if not (q.get('citations') or q.get('references'))],
            'missing_answered_followups': [q['id'] for q in questions
                                           if not any(isinstance(x, dict) and x.get('A', '').strip()
                                                      for x in q.get('follow_ups', []))],
            'unapproved_question_ids': [q['id'] for q in questions
                                        if q.get('reviewer_status', {}).get('status') != 'approved'],
        })
    for path in sorted((ROOT/'content/courses').glob('*.json')):
        course = json.loads(path.read_text())
        for unit in course['units']:
            records.append(evidence(unit, f'course/{course["id"]}/{unit["id"]}', 'unit',
                                    str(path.relative_to(ROOT)), 'course-' + unit['id']))
    review_counts = Counter(record['review_status'] for record in records)
    return {
        'version': 2,
        'records': records,
        'record_review_status': dict(sorted(review_counts.items())),
        'verified_review_records': sum(record['review_verified'] for record in records),
        'scope': 'Source-derived inventory and triage, not semantic quality or learner mastery',
        'adoption_max_study_id': ADOPTION_ID,
        'question_review_status': dict(sorted(states.items())),
        'chapters': chapters_out,
        'review_method': 'Per-record digest-matched attestations; delegated AI review is named explicitly and is not independent human review',
        'semantic_duplicate_check': 'Not certified; current CI applies lexical similarity only',
        'external_reference_freshness': 'Not certified by offline CI',
        'historical_questions': 'Published for compatibility, not grandfathered into independent approval',
    }


def validate_new_records(chapters):
    failures = []
    for chapter in chapters:
        for question in chapter['questions']:
            failures += [f"{chapter['slug']}#{question['id']}: {issue}"
                         for issue in inspect_new_question(question)]
    if failures:
        raise ValueError('New interview editorial gate failed:\\n' + '\\n'.join(failures[:25]))
    return sum(q['id'] > ADOPTION_ID for chapter in chapters for q in chapter['questions'])
