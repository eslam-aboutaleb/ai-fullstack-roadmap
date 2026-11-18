"""Safe, structured answer prose, inline teaching terminology, SVG figures, and flow diagrams."""
from hashlib import sha256
import re
import xml.etree.ElementTree as ET

from roadmap.config import CONTENT, escape_html as E, read_json

ACRONYMS: dict[str, str] = read_json(CONTENT / 'shared/acronyms.json')
VISUALS: dict[str, dict] = read_json(CONTENT / 'shared/answer-diagrams.json')
TITLES: dict[str, str] = read_json(CONTENT / 'shared/lesson-titles.json')

_INLINE_TOKEN = re.compile(
    r'(`[^`\n]+`|(?<![\w*])\*\*(?=\S)[^*\n]+(?<=\S)\*\*(?![\w*])|(?<![\w*])\*(?=\S)[^*\n]+(?<=\S)\*(?![\w*]))'
)
_CALLOUT_LABEL = re.compile(r'^(Engineering case|Reasoning under a changed assumption|Worked case):\s*(.*)', re.S)
_ALLOWED_SVG_TAGS = frozenset({
    'svg', 'g', 'rect', 'text', 'tspan', 'line', 'path', 'circle',
    'polygon', 'polyline', 'defs', 'marker', 'title', 'desc',
})
_ALLOWED_SVG_ATTRS = frozenset({
    'id', 'width', 'height', 'viewBox', 'x', 'y', 'x1', 'x2', 'y1', 'y2',
    'cx', 'cy', 'r', 'rx', 'ry', 'd', 'points', 'fill', 'stroke', 'stroke-width',
    'font-size', 'text-anchor', 'marker-end', 'markerWidth', 'markerHeight',
    'refX', 'refY', 'orient', 'dy', 'class',
})
_PROSE_RECORD_KEYS = (
    'Q', 'A', 'Why', 'Risk', 'Trade', 'Try', 'spoken', 'explain', 'example',
    'takeaway', 'conceptual_narrative', 'production_case', 'complexity',
    'worked_case', 'execution_timeline', 'follow_ups', 'underlying_mechanics',
)


def teaching_title(record: dict) -> str:
    """Return display heading for a question or conceptual lesson."""
    return TITLES.get(record['Q'], record['Q'])


def answer_acronyms(record: dict) -> list[tuple[str, str]]:
    """Extract defined glossary acronyms appearing in narrative prose fields."""
    def extract_text(value: object) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return ' '.join(extract_text(item) for item in value)
        if isinstance(value, dict):
            return ' '.join(extract_text(v) for k, v in value.items() if k not in ('code', 'output'))
        return ''

    combined = ' '.join(extract_text(record.get(key, '')) for key in _PROSE_RECORD_KEYS)
    return [
        (key, definition)
        for key, definition in ACRONYMS.items()
        if re.search(r'(?<![\w])' + re.escape(key) + r'(?:s)?(?![\w])', combined)
    ]


def answer_terms(record: dict) -> str:
    """Render aside glossary block for acronyms mentioned in the answer."""
    terms = answer_acronyms(record)
    if not terms:
        return ''
    defs = ''.join(f'<dt>{E(term)}</dt><dd>{E(definition)}</dd>' for term, definition in terms)
    return f'<aside class="answer-terms"><h4>Acronyms in this answer</h4><dl>{defs}</dl></aside>'


def normalize(text: str) -> str:
    """Normalize prose while preserving exact hashes of code spans and code fences."""
    text = re.sub(
        r'^(?:Engineering case|Reasoning under a changed assumption|Worked case):\s*',
        '',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'```[\s\S]*?```|`[^`\n]+`',
        lambda match: ' CODE-' + sha256(match.group().encode()).hexdigest() + ' ',
        text,
    )
    text = re.sub(r'(?<![\w*])\*\*(?=\S)(.+?)(?<=\S)\*\*(?![\w*])', r'\1', text)
    return re.sub(r'\s+', ' ', text).strip()


def blocks(text: str) -> list[str]:
    """Split prose into top-level blocks without splitting inside fenced code."""
    result: list[str] = []
    pending: list[str] = []
    fenced = False
    for line in text.strip().splitlines():
        if line.strip().startswith('```'):
            fenced = not fenced
        if not line.strip() and not fenced:
            if pending:
                result.append('\n'.join(pending).strip())
                pending = []
        else:
            pending.append(line)
    if pending:
        result.append('\n'.join(pending).strip())
    return result


def inline(text: str, terms: tuple[str, ...] | list[str] = (), seen: set[str] | None = None) -> str:
    """Render inline code, emphasis, and first-mention concept highlighting."""
    seen_set = seen if seen is not None else set()
    unique_terms = sorted({term for term in terms if len(term) > 1}, key=len, reverse=True)
    pattern = (
        re.compile(r'(?<!\w)(' + '|'.join(re.escape(t) for t in unique_terms) + r')(?:s)?(?!\w)', re.I)
        if unique_terms
        else None
    )

    def render_plain(value: str) -> str:
        if not pattern:
            return E(value)
        out: list[str] = []
        position = 0
        for match in pattern.finditer(value):
            out.append(E(value[position:match.start()]))
            key = match.group(1).casefold()
            if key not in seen_set:
                out.append('<strong class="answer-concept">' + E(match.group()) + '</strong>')
                seen_set.add(key)
            else:
                out.append(E(match.group()))
            position = match.end()
        out.append(E(value[position:]))
        return ''.join(out)

    result: list[str] = []
    for part in _INLINE_TOKEN.split(text):
        if not _INLINE_TOKEN.fullmatch(part):
            result.append(render_plain(part))
        elif part.startswith('`'):
            result.append('<code>' + E(part[1:-1]) + '</code>')
        elif part.startswith('**'):
            result.append('<strong>' + E(part[2:-2]) + '</strong>')
        else:
            result.append('<em>' + E(part[1:-1]) + '</em>')
    return ''.join(result)


def code_block(source: str, *, language: str = '', tabindex: bool = False) -> str:
    """Render escaped HTML code panel with copy button."""
    pre_attr = ' tabindex="0"' if tabindex else ''
    lang_attr = f' class="language-{E(language)}"' if language or tabindex else ''
    return (
        '<div class="code-panel"><button type="button" class="copy">Copy code</button>'
        f'<pre{pre_attr}><code{lang_attr}>{E(source)}</code></pre></div>'
    )


def prose(text: str, terms: tuple[str, ...] | list[str] = ()) -> str:
    """Render paragraphs, lists, tables, callouts, and fenced code safely."""
    lines = text.strip().splitlines()
    out: list[str] = []
    index = 0
    seen: set[str] = set()
    render = lambda value: inline(value, terms, seen)

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith('```'):
            language = line[3:].strip()
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith('```'):
                code_lines.append(lines[index])
                index += 1
            out.append(code_block('\n'.join(code_lines), language=language, tabindex=True))
            index += 1
            continue
        if line.startswith('### '):
            out.append('<h4>' + render(line[4:]) + '</h4>')
            index += 1
            continue
        if (
            index + 1 < len(lines)
            and '|' in line
            and re.fullmatch(r'[\s|:\-]+', lines[index + 1])
            and '-' in lines[index + 1]
        ):
            split_row = lambda row: [cell.strip() for cell in row.strip().strip('|').split('|')]
            headers = split_row(line)
            index += 2
            rows: list[str] = []
            while index < len(lines) and '|' in lines[index] and lines[index].strip():
                cells = split_row(lines[index])
                if len(cells) != len(headers):
                    raise ValueError('Answer table row has a different number of cells')
                rows.append('<tr>' + ''.join('<td>' + render(c) + '</td>' for c in cells) + '</tr>')
                index += 1
            head_html = ''.join('<th scope="col">' + render(c) + '</th>' for c in headers)
            out.append(
                '<div class="answer-table table-scroll" role="region" aria-label="Answer comparison" tabindex="0">'
                f'<table><thead><tr>{head_html}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            )
            continue
        list_match = re.match(r'^(?:([-*])\s+|(\d+)[.)]\s+)(.+)$', line)
        if list_match:
            ordered = bool(list_match.group(2))
            tag = 'ol' if ordered else 'ul'
            items: list[str] = []
            while index < len(lines):
                item = re.match(r'^(?:([-*])\s+|(\d+)[.)]\s+)(.+)$', lines[index].strip())
                if not item or bool(item.group(2)) != ordered:
                    break
                items.append('<li>' + render(item.group(3)) + '</li>')
                index += 1
            out.append(f'<{tag}>{"".join(items)}</{tag}>')
            continue

        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip():
            if re.match(r'^(?:```|### |[-*] |\d+[.)] )', lines[index].strip()):
                break
            paragraph.append(lines[index].strip())
            index += 1
        value = ' '.join(paragraph)
        label = _CALLOUT_LABEL.match(value)
        if label:
            heading = 'Worked case' if label.group(1) != 'Reasoning under a changed assumption' else 'Changed assumption'
            out.append(f'<aside class="answer-callout"><h4>{heading}</h4><p>{render(label.group(2))}</p></aside>')
        else:
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', value) if '`' not in value else [value]
            out.extend('<p>' + render(' '.join(sentences[i:i + 3])) + '</p>' for i in range(0, len(sentences), 3))
    return ''.join(out)


class AnswerWriter:
    """Suppress exact repeated prose blocks within a single rendered answer."""

    def __init__(self, record: dict) -> None:
        self.terms = [d['term'] for d in record.get('definitions', [])] + [
            key for key, _ in answer_acronyms(record)
        ]
        self.seen: list[str] = []
        self.followups = {normalize(f['A']) for f in record.get('follow_ups', [])}

    def take(self, text: str, reserve_followups: bool = False) -> str:
        accepted: list[str] = []
        for part in blocks(text):
            key = normalize(part)
            if not key:
                continue
            if reserve_followups and part.startswith('Reasoning under a changed assumption:') and key in self.followups:
                continue
            if any(key == prior or key in prior for prior in self.seen):
                continue
            self.seen.append(key)
            accepted.append(part)
        return '\n\n'.join(accepted)

    def render(self, text: str, reserve_followups: bool = False) -> str:
        return prose(self.take(text, reserve_followups), self.terms)

    def section(self, title: str, text: str, kind: str = '') -> str:
        body = self.render(text)
        return f'<section class="answer-section {E(kind)}"><h4>{E(title)}</h4>{body}</section>' if body else ''


def validate_diagrams(chapters: list[dict]) -> None:
    """Verify answer diagram keys and step metadata against loaded chapters."""
    known = {str(q['id']) for c in chapters for q in c['lessons'] + c['questions']}
    if set(VISUALS) - known:
        raise ValueError('Answer diagram references an unknown study ID')
    for item in VISUALS.values():
        if not item.get('title') or not item.get('description') or len(item.get('steps', [])) < 2:
            raise ValueError('Answer diagram needs a title, explanation and connected steps')
        for step in item['steps']:
            if not step.get('title') or not step.get('body') or step.get('kind', 'normal') not in (
                'normal', 'state', 'decision', 'warning'
            ):
                raise ValueError('Invalid answer diagram step')


def answer_diagram(record: dict) -> str:
    """Render flow diagram figure for a question ID when defined."""
    diagram = VISUALS.get(str(record['id']))
    if not diagram:
        return ''
    title_id = f'answer-diagram-{record["id"]}'
    steps = ''.join(
        f'<li class="diagram-{E(step.get("kind", "normal"))}">'
        f'<span class="diagram-step">{i + 1:02}</span>'
        f'<strong>{E(step["title"])}</strong><p>{inline(step["body"])}</p></li>'
        for i, step in enumerate(diagram['steps'])
    )
    return (
        f'<figure class="answer-diagram" aria-labelledby="{title_id}">'
        f'<figcaption id="{title_id}"><strong>{E(diagram["title"])}</strong>'
        f'<p>{E(diagram["description"])}</p></figcaption>'
        f'<ol class="answer-flow">{steps}</ol></figure>'
    )


def figures(items: list[dict], prefix: str) -> str:
    """Sanitize and scope inline SVG teaching diagrams with unique marker IDs."""
    result: list[str] = []
    for index, item in enumerate(items):
        svg = ET.fromstring(item['svg'])
        for element in svg.iter():
            tag = element.tag.rsplit('}', 1)[-1]
            if tag not in _ALLOWED_SVG_TAGS:
                raise ValueError(f'Unsupported instructional SVG tag: {tag}')
            element.tag = tag
            for key, value in list(element.attrib.items()):
                if key not in _ALLOWED_SVG_ATTRS or re.search(r'(?:javascript:|https?:|data:|//)', value, re.I):
                    raise ValueError(f'Unsafe instructional SVG attribute: {key}')
                if key == 'id':
                    element.set(key, f'{prefix}-{index}-{value}')
                elif 'url(' in value:
                    if not re.fullmatch(r'url\(#[a-zA-Z0-9_-]+\)', value):
                        raise ValueError('Only local SVG marker references are allowed')
                    element.set(key, value.replace('url(#', f'url(#{prefix}-{index}-'))
        svg.set('role', 'img')
        svg.set('aria-label', item['alt'])
        if 'viewBox' not in svg.attrib:
            svg.set('viewBox', f"0 0 {svg.get('width', '400')} {svg.get('height', '180')}")
        result.append(
            f'<figure class="lesson-figure">{ET.tostring(svg, encoding="unicode")}'
            f'<figcaption><strong>{E(item["alt"])}</strong>. {E(item["description"])}</figcaption></figure>'
        )
    return ''.join(result)


def render_reference_list(refs: list[str], heading_tag: str = 'h2') -> str:
    """Render an HTML section of linked primary references."""
    refs_html = ''.join(f'<li><a href="{E(ref)}">{E(ref)}</a></li>' for ref in refs)
    return f'<{heading_tag}>Primary references</{heading_tag}><ul>{refs_html}</ul>'


def lesson_content(q: dict, url, writer: AnswerWriter | None = None) -> str:
    """Render conceptual textbook sections for enriched lesson records."""
    if 'conceptual_narrative' not in q:
        return ''
    narrative = writer.render(q['conceptual_narrative']) if writer else prose(q['conceptual_narrative'])
    parts = ['<section class="textbook-content">' + ('<h3>Mechanism and intuition</h3>' + narrative if narrative else '')]
    terms_html = ''.join(f'<dt><strong>{E(t["term"])}</strong></dt><dd>{E(t["definition"])}</dd>' for t in q['glossary_terms'])
    parts.append(f'<h3>Terminology</h3><dl>{terms_html}</dl>')
    parts.extend(f'<p class="math-block">{E(derivation)}</p>' for derivation in q.get('mathematical_derivations', []))
    parts.append(figures(q.get('visualizations', []), f'lesson-{q["id"]}'))
    for example in q['worked_examples']:
        parts.append(f'<h3>{E(example["title"])}</h3>{code_block(example["code"])}<p>{E(example["explanation"])}</p>')
    parts.append(f'<h3>Expected output</h3><pre><code>{E(q["expected_output"])}</code></pre>')
    parts.append(
        f'<p><a href="{url("examples/" + q["local_lab"])}">Download the local lab</a>. '
        f'{E(q["review_and_answer_keys"]["known_limitations"])}</p>'
    )
    parts.append('<h3>Independent tasks</h3><ol>' + ''.join(f'<li>{E(task)}</li>' for task in q['independent_tasks']) + '</ol>')
    parts.append(render_reference_list(q['references'], 'h3'))
    parts.append('</section>')
    return ''.join(parts)


def question_content(q: dict, writer: AnswerWriter | None = None) -> str:
    """Render structured enriched question sections without repeating follow-ups."""
    if 'execution_timeline' not in q:
        return ''
    import json

    active_writer = writer or AnswerWriter(q)
    parts: list[str] = []
    for key, title in (
        ('execution_timeline', 'Execution sequence'),
        ('production_case', 'Production case'),
        ('complexity', 'Complexity and cost'),
    ):
        value = q[key]
        if value.startswith(('State the input and invariant →', 'Cost must be measured under the stated input size')):
            continue
        parts.append(active_writer.section(title, value))
    for key, title in (('alternatives', 'Alternatives'), ('pitfalls', 'Pitfalls')):
        items: list[str] = []
        for value in q[key]:
            if normalize(value) in active_writer.followups:
                continue
            rendered = active_writer.render(value)
            if rendered:
                items.append(f'<li>{rendered}</li>')
        if items:
            parts.append(f'<section class="answer-section"><h4>{title}</h4><ul>{"".join(items)}</ul></section>')
    example = q['example']
    try:
        parsed = json.loads(example['code'])
        reasoning_fixture = isinstance(parsed, dict) and 'case' in parsed and (
            'decision' in parsed or 'invariant' in parsed
        )
    except (ValueError, TypeError):
        reasoning_fixture = False
    if not reasoning_fixture:
        parts.append(
            '<section class="answer-section"><h4>Illustrative implementation</h4>'
            '<p>May require the surrounding application.</p>'
            + code_block(example['code'])
            + active_writer.render(example['explanation'])
            + f'<pre><code>{E(example["output"])}</code></pre></section>'
        )
    return ''.join(parts)
