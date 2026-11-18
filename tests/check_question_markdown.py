"""Verify lossless Markdown parsing, dynamic fences, scaffold templates, and error handling."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from roadmap.question_markdown import dumps_questions_md, loads_questions_md, scaffold_question_md


def check():
    # 1. Complex enriched + code fence inside A + inline ``` inside example + colon in definition term
    sample = [
        {
            'Q': 'How do fences, comments, and colons round-trip safely?',
            'answer_format': 'conceptual',
            'domain': 'ai-rag',
            'subdomain': 'retrieval',
            'added': True,
            'A': 'Paragraph one:\n\n```python\n# not a new question!\nprint(1)\n```\n\nParagraph two with `inline`.',
            'Why': 'Isolates fence tracking and comment ignoring inside Markdown packs.',
            'worked_case': 'Runs a code snippet containing hash comments and colons cleanly through parse/dump.',
            'Risk': 'Naive heading splits corrupt Python examples.',
            'Trade': 'Deterministic parser avoids third-party YAML dependency.',
            'Try': 'Include a nested triple-backtick string and verify exact identity.',
            'definitions': [{'term': 'Edge: colon **bold**', 'definition': 'Supports colons and stars'}],
            'follow_ups': [{'Q': 'What if code contains ```?', 'A': 'Dynamic fence length extends cleanly.\n\nSecond paragraph.'}],
            'citations': ['https://example.org/spec'],
            'reviewer_status': {'status': 'draft', 'reviewer': 'pending', 'reviewed_at': '2026-11-15'},
        },
        {
            'Q': 'How does example dynamic fence handle backticks?',
            'A': 'First paragraph.\n\nSecond paragraph.',
            'Why': 'Protects literal backticks in Python examples.',
            'Risk': 'Broken markdown fence closes prematurely.',
            'Trade': 'Uses 4-tick fence when code embeds 3 ticks.',
            'Try': 'Parse the dumped output again.',
            'example': {
                'explanation': 'Embeds triple backticks cleanly.',
                'output': 'verified',
                'code': 'doc = """\n```json\n{"a": 1}\n```\n"""\n# comment line\nprint(doc)',
            },
        },
    ]
    dumped = dumps_questions_md(sample, chapter_slug='test-chapter')
    parsed = loads_questions_md(dumped, source='test.md')
    assert parsed == sample, (parsed, sample)

    # 2. Scaffold templates must parse cleanly as valid single-question packs
    for kind in ('conceptual', 'enriched'):
        tpl = scaffold_question_md(kind=kind)
        rows = loads_questions_md(tpl, source=f'{kind}.md')
        assert len(rows) == 1

    # 3. Malformed section heading must fail explicitly instead of dropping data
    try:
        loads_questions_md('# Title\n\n## Unknown Heading\nText\n', source='bad.md')
    except ValueError as err:
        assert 'Unknown Heading' in str(err)
    else:
        raise AssertionError('Expected unknown section heading to raise ValueError')

    print(json.dumps({'check_question_markdown': 'pass', 'roundtrip_edge_cases': 'exact'}))


if __name__ == '__main__':
    check()
