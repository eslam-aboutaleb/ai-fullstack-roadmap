"""Source-derived editorial evidence; never substitute CI checks for expert review."""
from collections import Counter
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
    chapters_out = []
    states = Counter()
    for chapter in chapters:
        questions = chapter['questions']
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
    return {
        'version': 1,
        'scope': 'Source-derived inventory and triage, not semantic quality or learner mastery',
        'adoption_max_study_id': ADOPTION_ID,
        'question_review_status': dict(sorted(states.items())),
        'chapters': chapters_out,
        'human_review_required': True,
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
