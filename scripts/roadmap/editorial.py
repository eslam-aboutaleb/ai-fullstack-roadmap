"""Editorial attestation, evidence validation, and post-baseline interview contract."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

from .config import BASELINE_ID, CONTENT

ADOPTION_ID = BASELINE_ID
MIN_DEEP_ANSWER = 350
PLACEHOLDERS = ('lorem ipsum', 'todo: write', 'tbd answer', 'as an ai language model')
LESSON_FIELD_MINS = (('Q', 12), ('explain', 220), ('example', 60), ('takeaway', 25))


def content_digest(record: dict) -> str:
    """Compute a deterministic SHA-256 digest of a record excluding mutable metadata."""
    payload = {
        key: value
        for key, value in record.items()
        if key not in ('id', 'reviewer_status')
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return sha256(encoded).hexdigest()


def validate_review(
    record: dict,
    identity: str,
    attestations: dict | None = None,
    *,
    content_dir: Path = CONTENT,
) -> None:
    """Require a matching SHA-256 attestation for reviewed/approved records."""
    review = record.get('reviewer_status', {})
    if review.get('status') not in ('reviewed', 'approved'):
        return
    if attestations is None:
        attestations = json.loads((content_dir / 'reviews.json').read_text(encoding='utf-8'))
    proof = attestations.get(identity, {})
    if (
        proof.get('sha256') != content_digest(record)
        or proof.get('reviewer') != review.get('reviewer')
        or proof.get('reviewed_at') != review.get('reviewed_at')
        or not proof.get('review_notes', '').strip()
        or not review.get('reviewer', '').strip()
        or 'pending' in review.get('reviewer', '').lower()
    ):
        raise ValueError('Reviewed content needs a matching content-specific attestation: ' + identity)


def acceptable_url(url: object) -> bool:
    """Return True if url is a syntactically valid HTTPS URL with a network location."""
    if not isinstance(url, str):
        return False
    parsed = urlsplit(url.strip())
    return parsed.scheme == 'https' and bool(parsed.netloc)


def contains_placeholder(value: object) -> bool:
    """Return True if a nested JSON value contains a known placeholder phrase."""
    if isinstance(value, str):
        lowered = ' '.join(value.lower().split())
        return any(phrase in lowered for phrase in PLACEHOLDERS)
    if isinstance(value, dict):
        return any(contains_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_placeholder(item) for item in value)
    return False


def question_sources(record: dict) -> list[str]:
    """Return citation or reference links attached to a question, lesson, or unit."""
    raw = record.get('citations') or record.get('references') or []
    return [item.strip() for item in raw if isinstance(item, str) and item.strip()]


def has_valid_https_sources(record: dict) -> list[str]:
    """Return non-empty HTTPS source URLs when every recorded source link is valid."""
    urls = question_sources(record)
    return urls if urls and all(acceptable_url(url) for url in urls) else []


def has_answered_followup(record: dict) -> bool:
    """Return True if at least one follow-up entry carries a non-empty answer."""
    return any(isinstance(x, dict) and str(x.get('A', '')).strip() for x in record.get('follow_ups', []))


def good_text(value: object, minimum: int) -> bool:
    """Return True if value is a non-placeholder string meeting normalized minimum length."""
    if not isinstance(value, str):
        return False
    cleaned = ' '.join(value.split())
    return len(cleaned) >= minimum and not contains_placeholder(cleaned)


_good_text = good_text


def inspect_new_question(question: dict, baseline: int = ADOPTION_ID) -> list[str]:
    """Validate editorial requirements for questions created after ADOPTION_ID."""
    if not isinstance(question.get('id'), int) or question['id'] <= baseline:
        return []
    problems: list[str] = []
    answer = question.get('A', '')
    if not isinstance(answer, str) or len(answer.strip()) < MIN_DEEP_ANSWER:
        problems.append('answer is too brief for a standalone detailed interview response')
    if isinstance(answer, str) and any(marker in answer.casefold() for marker in PLACEHOLDERS):
        problems.append('answer has placeholder text')
    sources = question.get('citations') or question.get('references') or []
    if not sources or not isinstance(sources, list) or any(not acceptable_url(url) for url in sources):
        problems.append('missing or invalid HTTPS primary references')
    followups = question.get('follow_ups')
    if not isinstance(followups, list) or not any(
        isinstance(row, dict)
        and len(str(row.get('Q', '')).strip()) >= 12
        and len(str(row.get('A', '')).strip()) >= 60
        for row in followups
    ):
        problems.append('at least one genuinely answered interview follow-up is required')
    review = question.get('reviewer_status', {})
    if not isinstance(review, dict) or review.get('status') not in ('draft', 'reviewed', 'approved'):
        problems.append('review state must be explicitly draft, reviewed, or approved')
    return problems


def validate_new_records(chapters: list[dict], baseline: int = ADOPTION_ID) -> int:
    """Check all post-baseline interview questions and raise on any violation."""
    failures: list[str] = []
    checked = 0
    for chapter in chapters:
        slug = chapter['slug']
        for question in chapter.get('questions', []):
            if isinstance(question.get('id'), int) and question['id'] > baseline:
                checked += 1
                for issue in inspect_new_question(question, baseline=baseline):
                    failures.append(f'{slug}#{question["id"]}: {issue}')
    if failures:
        raise ValueError('New content evidence gate failed: ' + '; '.join(failures))
    return checked


def evidence_report(chapters: list[dict], *, content_dir: Path = CONTENT) -> dict:
    """Aggregate factual source inventory across chapters, questions, and courses."""
    repo_root = content_dir.parent
    attestations = json.loads((content_dir / 'reviews.json').read_text(encoding='utf-8'))
    assessments = json.loads((content_dir / 'assessments.json').read_text(encoding='utf-8'))['items']
    records: list[dict] = []

    def build_entry(record: dict, identity: str, kind: str, source: str, chapter_slug: str) -> dict:
        review = record.get('reviewer_status', {})
        status = review.get('status', 'legacy-unreviewed')
        validate_review(record, identity, attestations, content_dir=content_dir)
        sources = question_sources(record)
        topic = record.get('id', record.get('study_id'))
        return {
            'identity': identity,
            'kind': kind,
            'source': source,
            'study_id': topic,
            'chapter': chapter_slug,
            'sha256': content_digest(record),
            'review_status': status,
            'review_verified': status in ('reviewed', 'approved'),
            'reviewer': review.get('reviewer'),
            'reviewed_at': review.get('reviewed_at'),
            'primary_sources': sources,
            'https_source_links_present': bool(sources) and all(acceptable_url(url) for url in sources),
            'assessment_ids': [a['id'] for a in assessments if a.get('topic') == topic],
            'lab': record.get('local_lab', record.get('lab')),
            'source_check_limit': 'URL shape and recorded review are checked; exhaustive live reference freshness and semantic correctness are not automated',
        }

    chapters_out: list[dict] = []
    states: Counter[str] = Counter()
    for chapter in chapters:
        slug = chapter['slug']
        questions = chapter['questions']
        for kind, group in (('lesson', 'lessons'), ('interview', 'questions')):
            filename = 'lessons.json' if kind == 'lesson' else 'questions.md'
            for record in chapter[group]:
                records.append(
                    build_entry(
                        record,
                        f'{kind}/{slug}/{record["Q"]}',
                        kind,
                        f'content/chapters/{slug}/{filename}',
                        slug,
                    )
                )
        for question in questions:
            states[question.get('reviewer_status', {}).get('status', 'legacy-unreviewed')] += 1
        chapters_out.append({
            'chapter': slug,
            'total_lessons': len(chapter['lessons']),
            'total_interview_questions': len(questions),
            'short_primary_answers': [q['id'] for q in questions if len(q.get('A', '').strip()) < MIN_DEEP_ANSWER],
            'no_question_level_citations': [q['id'] for q in questions if not question_sources(q)],
            'missing_answered_followups': [q['id'] for q in questions if not has_answered_followup(q)],
            'unapproved_question_ids': [
                q['id']
                for q in questions
                if q.get('reviewer_status', {}).get('status') != 'approved'
            ],
        })

    for path in sorted((content_dir / 'courses').glob('*.json')):
        course = json.loads(path.read_text(encoding='utf-8'))
        for unit in course['units']:
            rel_source = str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else f'content/courses/{path.name}'
            records.append(
                build_entry(
                    unit,
                    f'course/{course["id"]}/{unit["id"]}',
                    'unit',
                    rel_source,
                    'course-' + unit['id'],
                )
            )

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


def _has_verified_enriched_shape(item: dict) -> bool:
    """Return True if a non-conceptual question carries full enriched evidence and code."""
    ex = item.get('example')
    return (
        _good_text(item.get('production_case'), 100)
        and isinstance(ex, dict)
        and ex.get('output') == 'verified'
        and _good_text(ex.get('code'), 60)
        and _good_text(item.get('execution_timeline'), 20)
        and _good_text(item.get('complexity'), 20)
    )


def inspect_interview_contract(chapters: list[dict] | None = None, baseline: int = BASELINE_ID) -> list[str]:
    """Validate chapter framing and post-baseline question/lesson pedagogical depth."""
    if chapters is None:
        from roadmap.content import load_chapters

        chapters = load_chapters()
    problems: list[str] = []
    for chapter in chapters:
        slug = chapter['slug']
        if not _good_text(chapter.get('intro', ''), 30):
            problems.append(f'{slug}: introduce the topic in chapter.intro before questions')
        if not chapter.get('terms') or not chapter.get('flow') or len(chapter.get('case', [])) != 3:
            problems.append(f'{slug}: introduction needs terms, flow and a three-part case')
        if not chapter.get('lessons') or not chapter.get('questions'):
            problems.append(f'{slug}: foundation lessons and deeper interview questions required')

        for group in ('lessons', 'questions'):
            for item in chapter.get(group, []):
                identity = item.get('id')
                if not isinstance(identity, int) or identity <= baseline:
                    continue
                prefix = f'{slug}/{group}#{identity}'
                if group == 'lessons':
                    for key, minimum in LESSON_FIELD_MINS:
                        if not _good_text(item.get(key), minimum):
                            problems.append(f'{prefix}: foundation {key} needs >= {minimum} characters')
                    continue

                for key, minimum in (('Q', 12), ('A', MIN_DEEP_ANSWER), ('Why', 60), ('Risk', 40), ('Trade', 40), ('Try', 40)):
                    if not _good_text(item.get(key), minimum):
                        problems.append(f'{prefix}: {key} needs >= {minimum} characters')
                if len(re.split(r'\n\s*\n', str(item.get('A', '')).strip())) < 2:
                    problems.append(f'{prefix}: detailed A must have distinct explanatory paragraphs')

                fmt = item.get('answer_format')
                if fmt == 'conceptual':
                    if not _good_text(item.get('worked_case'), 100):
                        problems.append(f'{prefix}: worked_case needs >= 100 characters')
                elif not _has_verified_enriched_shape(item):
                    problems.append(
                        f'{prefix}: author a single full A using answer_format=conceptual with worked_case, '
                        'or an enriched record with production_case (>=100), timeline, complexity, and verified example'
                    )

                followups = item.get('follow_ups', [])
                if not isinstance(followups, list) or not followups:
                    problems.append(f'{prefix}: add at least one answered changed-assumption follow-up')
                else:
                    for followup in followups:
                        if not isinstance(followup, dict) or not _good_text(followup.get('Q'), 12) or not _good_text(followup.get('A'), 60):
                            problems.append(f'{prefix}: follow-up must have a specific question and substantive answer')

                citations = item.get('citations', [])
                if not isinstance(citations, list) or not citations or any(not acceptable_url(u) for u in citations):
                    problems.append(f'{prefix}: cite at least one official HTTPS primary reference')
                if item.get('reviewer_status', {}).get('status') not in ('draft', 'reviewed', 'approved'):
                    problems.append(f'{prefix}: record an honest draft/reviewed/approved status')
    return problems


def check_interview_contract(chapters: list[dict] | None = None, baseline: int = BASELINE_ID) -> dict:
    """Enforce interview_contract rules and return summary telemetry."""
    if chapters is None:
        from roadmap.content import load_chapters

        chapters = load_chapters()
    problems = inspect_interview_contract(chapters, baseline=baseline)
    if problems:
        raise ValueError('Interview authoring contract failed:\n' + '\n'.join(problems[:20]))
    return {
        'baseline_id': baseline,
        'chapters': len(chapters),
        'new_chapter_topics': sum(
            item['id'] > baseline
            for ch in chapters
            for item in ch['lessons'] + ch['questions']
        ),
        'new_questions_reviewed_or_draft': sum(
            item.get('reviewer_status', {}).get('status') in ('draft', 'reviewed', 'approved')
            for ch in chapters
            for item in ch['questions']
            if item['id'] > baseline
        ),
    }
