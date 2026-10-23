"""Validate the interview-first teaching contract without rewriting legacy study IDs.

The baseline is the highest registered study ID at adoption time. New question
identities are append-only; pre-existing questions remain visible and auditable
rather than being silently reclassified as newly approved content.
"""
from pathlib import Path
import json
import re
from urllib.parse import urlsplit

BASELINE_ID = 1211  # main, 21 October 2026; do NOT raise to bypass new-content checks.
MIN_DEEP_ANSWER = 350


def _good_text(value, minimum):
    return isinstance(value, str) and len(value.strip()) >= minimum


def inspect(chapters, baseline=BASELINE_ID):
    """Return actionable diagnostics; no network, credentials or expensive models."""
    problems = []
    for chapter in chapters:
        slug = chapter['slug']
        intro = chapter.get('intro', '')
        if not _good_text(intro, 30):
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
                    for key, minimum in (('Q', 12), ('explain', 220), ('example', 60), ('takeaway', 25)):
                        if not _good_text(item.get(key), minimum):
                            problems.append(f'{prefix}: foundation {key} needs >= {minimum} characters')
                    continue
                # Only the long answer is rendered as the main View answer.
                # No forced code/diagram: explain the mechanism with whichever medium helps.
                for key, minimum in (('Q', 12), ('A', MIN_DEEP_ANSWER),
                                     ('Why', 60), ('Risk', 40), ('Trade', 40),
                                     ('Try', 40), ('worked_case', 100)):
                    if not _good_text(item.get(key), minimum):
                        problems.append(f'{prefix}: {key} needs >= {minimum} characters')
                if len(re.split(r'\n\s*\n', item.get('A', '').strip())) < 2:
                    problems.append(f'{prefix}: detailed A must have distinct explanatory paragraphs')
                if item.get('answer_format') != 'conceptual':
                    problems.append(f'{prefix}: author a single full A using answer_format=conceptual; legacy spoken is not a second visible answer')
                followups = item.get('follow_ups', [])
                if not isinstance(followups, list) or not followups:
                    problems.append(f'{prefix}: add at least one answered changed-assumption follow-up')
                else:
                    for followup in followups:
                        if not isinstance(followup, dict) or not _good_text(followup.get('Q'), 12) or not _good_text(followup.get('A'), 60):
                            problems.append(f'{prefix}: follow-up must have a specific question and substantive answer')
                citations = item.get('citations', [])
                if not isinstance(citations, list) or not citations or any(
                    not isinstance(url, str) or urlsplit(url).scheme != 'https'
                    or not urlsplit(url).netloc for url in citations
                ):
                    problems.append(f'{prefix}: cite at least one official HTTPS primary reference')
                if item.get('reviewer_status', {}).get('status') not in ('draft', 'reviewed', 'approved'):
                    problems.append(f'{prefix}: record an honest draft/reviewed/approved status')
    return problems


def check(chapters=None):
    if chapters is None:
        from course_data import load
        chapters = load()
    errors = inspect(chapters)
    if errors:
        raise ValueError('Interview-first authoring contract:\n' + '\n'.join(errors[:40]))
    return {'baseline_id': BASELINE_ID, 'chapters': len(chapters),
            'new_chapter_topics': sum(q['id'] > BASELINE_ID
                                      for chapter in chapters
                                      for q in chapter['lessons'] + chapter['questions'])}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
