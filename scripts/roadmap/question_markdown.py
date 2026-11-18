"""Pure-stdlib lossless parser and formatter for per-chapter questions.md packs.

Format overview (one readable Markdown file per chapter):
    # <Question title>

    <!-- meta
    answer_format: conceptual
    domain: ai-rag
    ...
    review.status: draft
    review.reviewer: independent technical review pending
    review.reviewed_at: 2026-10-29
    -->

    ## Answer
    ...markdown prose...

    ## Follow-ups
    ### Follow-up question?
    Follow-up answer.

    ## Example
    > Explanation: ...
    > Output: verified

    ```python
    ...
    ```
"""
from __future__ import annotations

import json
import re

META_KEYS = (
    'answer_format',
    'domain',
    'subdomain',
    'module',
    'concept',
    'difficulty',
    'misconception_target',
    'reference',
    'local_lab',
    'added',
)

PROSE_SECTIONS = (
    ('Answer', 'A'),
    ('Spoken Summary', 'spoken'),
    ('Why', 'Why'),
    ('Worked Case', 'worked_case'),
    ('Production Case', 'production_case'),
    ('Risk', 'Risk'),
    ('Trade-off', 'Trade'),
    ('Try This', 'Try'),
    ('Execution Timeline', 'execution_timeline'),
    ('Complexity', 'complexity'),
)

PROSE_HEADING_TO_KEY = {heading: key for heading, key in PROSE_SECTIONS}
LIST_SECTIONS = {
    'Alternatives': 'alternatives',
    'Pitfalls': 'pitfalls',
    'Citations': 'citations',
}
SPECIAL_SECTIONS = {'Definitions', 'Follow-ups', 'Example'}
ALL_SECTIONS = set(PROSE_HEADING_TO_KEY) | set(LIST_SECTIONS) | SPECIAL_SECTIONS

_FENCE_RE = re.compile(r'^(`{3,})(.*)$')
_DEFINITION_RE = re.compile(r'^- \*\*(.+?)\*\*:\s*(.*)$')


def _fence_for(code: str, lang: str = 'python') -> tuple[str, str]:
    runs = [len(m.group(0)) for m in re.finditer(r'`+', code)]
    tick_len = max([3, *(r + 1 for r in runs)])
    fence = '`' * tick_len
    return f'{fence}{lang}', fence


def _update_fence_state(line: str, in_fence: str | None) -> str | None:
    fence_match = _FENCE_RE.match(line)
    if not fence_match:
        return in_fence
    ticks = fence_match.group(1)
    if in_fence is None:
        return ticks
    if len(ticks) >= len(in_fence) and not fence_match.group(2).strip():
        return None
    return in_fence


def _append_bullet_section(lines: list[str], heading: str, items: list[object]) -> None:
    lines.extend([f'## {heading}', ''])
    lines.extend(f'- {item}' for item in items)
    lines.append('')


def _format_scalar(value: object) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    text = str(value)
    if '\n' in text or text != text.strip():
        return json.dumps(text, ensure_ascii=False)
    return text


def _parse_scalar(raw: str) -> object:
    val = raw.strip()
    if val == 'true':
        return True
    if val == 'false':
        return False
    if val.startswith('"') and val.endswith('"'):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, str):
                return parsed
        except json.JSONDecodeError:
            pass
    return val


def format_question_md(question: dict) -> str:
    """Serialize one question record into clean readable Markdown."""
    lines: list[str] = [f"# {question['Q']}", '']

    meta_lines: list[str] = []
    for key in META_KEYS:
        if key in question:
            meta_lines.append(f'{key}: {_format_scalar(question[key])}')
    review = question.get('reviewer_status')
    if isinstance(review, dict):
        for rkey in ('status', 'reviewer', 'reviewed_at'):
            if rkey in review:
                meta_lines.append(f'review.{rkey}: {_format_scalar(review[rkey])}')
    if meta_lines:
        lines.append('<!-- meta')
        lines.extend(meta_lines)
        lines.append('-->')
        lines.append('')

    for heading, key in PROSE_SECTIONS:
        if key in question:
            lines.append(f'## {heading}')
            lines.append('')
            lines.append(str(question[key]))
            lines.append('')

    if 'definitions' in question:
        lines.append('## Definitions')
        lines.append('')
        for entry in question['definitions']:
            term = str(entry['term']).replace('**', r'\*\*')
            definition = str(entry['definition'])
            if '\n' in term or '\n' in definition:
                lines.append(f'- {json.dumps(entry, ensure_ascii=False)}')
            else:
                lines.append(f'- **{term}**: {definition}')
        lines.append('')

    for heading, key in (('Alternatives', 'alternatives'), ('Pitfalls', 'pitfalls')):
        if key in question:
            _append_bullet_section(lines, heading, question[key])

    if 'follow_ups' in question:
        lines.append('## Follow-ups')
        lines.append('')
        for item in question['follow_ups']:
            lines.append(f"### {item['Q']}")
            lines.append('')
            lines.append(str(item['A']))
            lines.append('')

    if 'example' in question:
        ex = question['example']
        lines.append('## Example')
        lines.append('')
        lines.append(f"> Explanation: {ex['explanation']}")
        lines.append(f"> Output: {ex['output']}")
        lines.append('')
        code = str(ex['code']).rstrip('\n')
        opener, closer = _fence_for(code, 'python')
        lines.append(opener)
        lines.append(code)
        lines.append(closer)
        lines.append('')

    if 'citations' in question:
        _append_bullet_section(lines, 'Citations', question['citations'])

    return '\n'.join(lines).rstrip() + '\n'


def dumps_questions_md(questions: list[dict], *, chapter_slug: str | None = None) -> str:
    """Serialize all questions for a chapter into one organized questions.md document."""
    header = f'<!-- chapter: {chapter_slug} -->\n\n' if chapter_slug else ''
    blocks = [format_question_md(q) for q in questions]
    return header + '\n'.join(blocks).rstrip() + ('\n' if blocks else '')


def _parse_list_section(body_lines: list[str], source: str, lineno: int) -> list[str]:
    items: list[str] = []
    for offset, raw in enumerate(body_lines):
        stripped = raw.strip()
        if not stripped:
            continue
        if not stripped.startswith('- '):
            raise ValueError(f'{source}:{lineno + offset}: expected markdown bullet "- ...", got {stripped!r}')
        items.append(stripped[2:])
    return items


def _parse_definitions_section(body_lines: list[str], source: str, lineno: int) -> list[dict]:
    items: list[dict] = []
    for offset, raw in enumerate(body_lines):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith('- {'):
            items.append(json.loads(stripped[2:]))
            continue
        match = _DEFINITION_RE.match(stripped)
        if not match:
            raise ValueError(f'{source}:{lineno + offset}: expected "- **term**: definition", got {stripped!r}')
        term = match.group(1).replace(r'\*\*', '**')
        items.append({'term': term, 'definition': match.group(2)})
    return items


def _parse_followups_section(body_lines: list[str], source: str, lineno: int) -> list[dict]:
    items: list[dict] = []
    current_q: str | None = None
    answer_lines: list[str] = []
    in_fence: str | None = None

    def flush():
        if current_q is not None:
            items.append({'Q': current_q, 'A': '\n'.join(answer_lines).strip()})

    for offset, line in enumerate(body_lines):
        in_fence = _update_fence_state(line, in_fence)
        if in_fence is None and line.startswith('### '):
            flush()
            current_q = line[4:].strip()
            answer_lines = []
            continue
        if current_q is None:
            if line.strip():
                raise ValueError(f'{source}:{lineno + offset}: unexpected content before "### <follow-up>"')
            continue
        answer_lines.append(line)

    flush()
    return items


def _parse_example_section(body_lines: list[str], source: str, lineno: int) -> dict:
    explanation: str | None = None
    output: str | None = None
    code_lines: list[str] | None = None
    in_fence: str | None = None

    for offset, line in enumerate(body_lines):
        if in_fence is not None:
            close_match = _FENCE_RE.match(line)
            if close_match and len(close_match.group(1)) >= len(in_fence) and not close_match.group(2).strip():
                in_fence = None
                continue
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('> Explanation:'):
            explanation = stripped[len('> Explanation:'):].strip()
            continue
        if stripped.startswith('> Output:'):
            output = stripped[len('> Output:'):].strip()
            continue
        fence_match = _FENCE_RE.match(line)
        if fence_match and code_lines is None:
            in_fence = fence_match.group(1)
            code_lines = []
            continue
        raise ValueError(f'{source}:{lineno + offset}: unexpected line inside ## Example: {line!r}')

    if in_fence is not None:
        raise ValueError(f'{source}:{lineno}: unterminated code block inside ## Example')
    if explanation is None or output is None or code_lines is None:
        raise ValueError(f'{source}:{lineno}: ## Example requires > Explanation:, > Output:, and a code fence')

    return {
        'code': '\n'.join(code_lines),
        'explanation': explanation,
        'output': output,
    }


def loads_questions_md(text: str, *, source: str = 'questions.md') -> list[dict]:
    """Parse a chapter questions.md document into exact question dicts."""
    lines = text.splitlines()
    questions: list[dict] = []

    current: dict | None = None
    section_name: str | None = None
    section_lines: list[str] = []
    section_start = 1
    in_meta = False
    seen_section = False
    in_fence: str | None = None

    def flush_section() -> None:
        nonlocal section_name, section_lines
        if current is None or section_name is None:
            return
        if section_name in PROSE_HEADING_TO_KEY:
            key = PROSE_HEADING_TO_KEY[section_name]
            current[key] = '\n'.join(section_lines).strip()
        elif section_name in LIST_SECTIONS:
            key = LIST_SECTIONS[section_name]
            current[key] = _parse_list_section(section_lines, source, section_start)
        elif section_name == 'Definitions':
            current['definitions'] = _parse_definitions_section(section_lines, source, section_start)
        elif section_name == 'Follow-ups':
            current['follow_ups'] = _parse_followups_section(section_lines, source, section_start)
        elif section_name == 'Example':
            current['example'] = _parse_example_section(section_lines, source, section_start)
        section_name = None
        section_lines = []

    def flush_question() -> None:
        nonlocal current, seen_section
        flush_section()
        if current is not None:
            questions.append(current)
        current = None
        seen_section = False

    for idx, line in enumerate(lines, 1):
        # Allow top-of-file HTML comment banner such as <!-- chapter: retrieval -->
        if current is None and (not line.strip() or re.fullmatch(r'<!--.*?-->', line.strip())):
            continue

        if in_meta:
            if line.strip() == '-->':
                in_meta = False
                continue
            if ':' not in line:
                raise ValueError(f'{source}:{idx}: malformed metadata line {line!r}')
            raw_key, _, raw_val = line.partition(':')
            key = raw_key.strip()
            val = _parse_scalar(raw_val)
            if key.startswith('review.'):
                review = current.setdefault('reviewer_status', {})
                review[key[len('review.'):]] = val
            else:
                current[key] = val
            continue

        in_fence = _update_fence_state(line, in_fence)

        if in_fence is None and line.startswith('# '):
            flush_question()
            title = line[2:].strip()
            if not title:
                raise ValueError(f'{source}:{idx}: empty question heading')
            current = {'Q': title}
            seen_section = False
            continue

        if current is None:
            raise ValueError(f'{source}:{idx}: expected "# <Question title>" before {line!r}')

        if not seen_section and in_fence is None and line.strip() == '<!-- meta':
            in_meta = True
            continue

        if in_fence is None and line.startswith('## '):
            flush_section()
            heading = line[3:].strip()
            if heading not in ALL_SECTIONS:
                raise ValueError(f'{source}:{idx}: unknown section heading "## {heading}"')
            section_name = heading
            section_lines = []
            section_start = idx + 1
            seen_section = True
            continue

        if section_name is not None:
            section_lines.append(line)
        elif line.strip():
            raise ValueError(f'{source}:{idx}: text outside "## <Section>" heading: {line!r}')

    if in_meta:
        raise ValueError(f'{source}: unterminated <!-- meta --> block')
    if in_fence is not None:
        raise ValueError(f'{source}: unterminated fenced code block')

    flush_question()
    return questions


def scaffold_question_md(
    title: str = 'How does <mechanism> behave under <constraint>?',
    *,
    kind: str = 'conceptual',
    domain: str = 'ai-rag',
    subdomain: str = 'retrieval',
    difficulty: str = 'interview',
) -> str:
    """Return a compliant Markdown authoring template ready to fill in."""
    if kind not in ('conceptual', 'enriched'):
        raise ValueError(f'Unsupported question template kind: {kind}')
    today = '2026-11-15'
    sample: dict[str, object] = {
        'Q': title,
        'domain': domain,
        'subdomain': subdomain,
        'difficulty': difficulty,
        'reviewer_status': {
            'status': 'draft',
            'reviewer': 'independent technical review pending',
            'reviewed_at': today,
        },
        'A': '**Core mechanism.** Replace this paragraph with a direct, precise explanation of how the mechanism works and what invariant it protects.\n\n**Failure mode and design trade-off.** Replace this paragraph with concrete architectural trade-offs, operational limits, and what changes when assumptions shift.',
        'Why': 'Explain why this distinction prevents silent failures or wrong architectural choices in production.',
        'Risk': 'Describe the main failure mode or misconception and how to detect it early.',
        'Trade': 'Contrast this design with the nearest alternative and state when you would choose each.',
        'Try': 'Describe a concrete experiment or edge case the reader can vary to test the boundary.',
        'follow_ups': [
            {'Q': 'What changes if the key assumption reverses?', 'A': 'Explain how the invariant, cost, or fallback behavior shifts.'}
        ],
        'citations': ['https://example.org/primary-reference'],
    }
    if kind == 'conceptual':
        sample['answer_format'] = 'conceptual'
        sample['worked_case'] = (
            'Walk through one concrete input/state sequence showing inputs, intermediate transition, '
            'observed outcome, and what changes if an assumption breaks.'
        )
    else:
        sample.update({
            'module': subdomain,
            'concept': subdomain,
            'misconception_target': 'State the exact misconception this question disproves.',
            'spoken': 'Concise 60-second spoken answer summarizing intuition, trade-off, and boundary.',
            'production_case': 'Concrete production incident or design scenario showing diagnosis and remediation (>= 100 chars).',
            'execution_timeline': 'Input -> Step 1 -> Step 2 -> Guard / output',
            'complexity': 'State time, space, or latency scaling characteristics honestly.',
            'definitions': [{'term': 'Term', 'definition': 'Clear one-sentence definition.'}],
            'alternatives': ['Nearest alternative approach'],
            'pitfalls': ['Common mistake or unguarded edge case'],
            'example': {
                'explanation': 'One-line explanation matching catalog.json.',
                'output': 'verified',
                'code': '"""Minimal runnable self-contained example."""\nassert True\nprint("ok")',
            },
        })
    return format_question_md(sample)
