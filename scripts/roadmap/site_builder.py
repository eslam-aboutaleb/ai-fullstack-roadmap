"""Static HTML site generator, shared page shell, and GitHub Pages packager."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import textwrap

from roadmap.audit_pages import build_audit_pages, build_blueprint
from roadmap.config import (
    ASSETS,
    BUILD_OUT,
    CONTENT,
    LABS,
    ROOT,
    SITE_OUT,
    chapter_reading_minutes,
    escape_html as E,
    read_json,
    write_json,
)
from roadmap.content import STAGES, load_chapters
from roadmap.courses import build_courses, load_courses
from roadmap.examples import load_chapter_examples, load_question_examples
from roadmap.practice import (
    SIMULATION_CHAPTERS,
    build_practice_pages,
    build_question_shards,
    build_search_shards,
    load_practice,
    question_finder,
    scenario_page,
    simulation_panel,
)
from roadmap.prose import (
    ACRONYMS,
    AnswerWriter,
    VISUALS,
    answer_diagram,
    answer_terms,
    lesson_content,
    normalize as normalize_prose,
    prose as answer_prose,
    question_content,
    render_reference_list,
    teaching_title,
    validate_diagrams,
)

_EXTENSION_BY_LANG = {'python': '.py', 'sql': '.sql', 'markdown': '.md', 'javascript': '.js', 'html': '.html'}
_LANGUAGE_SCOPES = {
    'python': 'Run this self-contained example with Python 3.10+. It uses synthetic fixtures and the standard library; it does not connect to a provider or establish a production guarantee.',
    'javascript': 'Run this local JavaScript fixture with Node.js or the documented browser context. External integrations require their stated host configuration.',
    'python-sketch': 'Python integration sketch requiring the documented dependencies and surrounding application.',
    'sql': 'SQL example requiring its declared database engine and schema; dialect and transaction behavior are part of that contract.',
    'json': 'Structured case data. Parsing checks its representation, not the behavior of the system it describes.',
    'bash': 'Shell integration commands requiring the documented tools and environment.',
    'html': 'Browser example requiring the documented page and hosting context.',
    'dockerfile': 'Container build configuration requiring the documented build context and container runtime.',
}
_CAPSTONE_LINKS = {
    'async-engine': ('computer-science-foundations', 'Build a bounded async job engine'),
    'transaction-api': ('api-security', 'Build an authorized transactional API'),
    'rag-quality': ('evaluation', 'Evaluate retrieval against a gold set'),
    'durable-agent': ('agent-harness', 'Recover a durable agent effect'),
}
_LAB_ALLOWED_SUFFIXES = frozenset({
    '.py', '.js', '.cjs', '.md', '.json', '.txt', '.toml',
    '.yaml', '.yml', '.sql', '.html', '.css', '.csv', '.ipynb',
})
_DEFAULT_QCODE_CACHE: dict[int, dict] | None = None

_THEME_FOUC_SCRIPT = (
    '<script>try{'
    "var t=localStorage.getItem('guide-theme');"
    "if(!t){t=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'}"
    "document.documentElement.dataset.theme=t;"
    '}catch{}</script>'
)
_SEARCH_DIALOG_HTML = (
    '<dialog class="search-modal" id="search-modal" aria-label="Search course topics" closedby="any">'
    '<div class="search-modal-box">'
    '<div class="search-modal-input">'
    '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
    '<circle cx="8.5" cy="8.5" r="5.5"/><path d="M13 13l4 4"/></svg>'
    '<input type="search" id="modal-query" aria-label="Search course topics" '
    'placeholder="Search topics, tools, and failure modes" autocomplete="off">'
    '<button type="button" class="search-modal-close" id="modal-close" aria-label="Close modal search">esc</button>'
    '</div>'
    '<div class="search-modal-results" id="modal-results" role="region" aria-label="Search results" aria-live="polite"></div>'
    '<div class="search-modal-footer">'
    '<span><kbd>↑</kbd><kbd>↓</kbd> to navigate</span>'
    '<span><kbd>↵</kbd> to select</span>'
    '<span><kbd>esc</kbd> to close</span>'
    '</div></div></dialog>'
)


def configured_base_path() -> str:
    """Return normalized PAGES_BASE_PATH environment configuration."""
    base = os.environ.get('PAGES_BASE_PATH', '')
    if base and not base.startswith('/'):
        base = '/' + base
    if base and not base.endswith('/'):
        base = base + '/'
    return base


def url(path: str) -> str:
    """Resolve internal relative paths cleanly under subpaths and file:// viewing."""
    if not path or path.startswith(('http://', 'https://', '#', 'mailto:')):
        return path
    return path


def versioned_asset(out: Path, name: str) -> str:
    """Append short content hash to built asset URL when file exists in output."""
    target = out / name
    if not target.is_file():
        return url(name)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()[:10]
    return url(f'{name}?v={digest}')


def term_id(name: str) -> str:
    """Deterministic HTML anchor ID for glossary terms."""
    return 'term-' + hashlib.sha256(name.encode()).hexdigest()[:12]


def paragraphs(text: str) -> str:
    """Group dense plain sentences into readable 2-sentence paragraphs."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return ''.join('<p>' + E(' '.join(sentences[i:i + 2])) + '</p>' for i in range(0, len(sentences), 2))


def render_head(title: str, *, asset_fn, description: str = '') -> str:
    """Render shared HTML <head> with color-scheme meta and FOUC prevention."""
    desc_tag = f'<meta name="description" content="{E(description)}">' if description else ''
    return (
        f'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="color-scheme" content="light dark">{desc_tag}'
        f'<title>{E(title)} · AI Engineering Roadmap</title>'
        f'{_THEME_FOUC_SCRIPT}'
        f'<link rel="icon" type="image/svg+xml" sizes="any" href="{asset_fn("favicon.svg")}">'
        f'<link rel="stylesheet" href="{asset_fn("style.css")}">'
        + ''.join(
            f'<script src="{asset_fn(name)}" defer></script>'
            for name in ('search-loader.js', 'highlight.js', 'study-model.js', 'study-store.js', 'app.js', 'course.js')
        )
        + '</head>'
    )


def render_page(
    title: str,
    body: str,
    *,
    chapters: list[dict],
    by_slug: dict[str, dict],
    max_id: int,
    study_total: int,
    out: Path,
    active: str = '',
) -> str:
    """Render complete accessible site chrome around page body content."""
    current = by_slug.get(active)
    stage = current['stage'] if current else 1
    nav_stages: list[str] = []
    for n, (label, _level, _summary, slugs) in enumerate(STAGES, 1):
        entries = ''.join(
            f'<a href="{url(slug + ".html")}" {"aria-current=page" if active == slug else ""}>'
            f'<span>{chapters.index(by_slug[slug]) + 1:02}</span>{E(by_slug[slug]["title"])}</a>'
            for slug in slugs
        )
        nav_stages.append(
            f'<details class="nav-stage" {"open" if n == stage else ""}>'
            f'<summary><span>{n:02}</span>{E(label)}</summary>{entries}</details>'
        )

    asset_fn = lambda name: versioned_asset(out, name)
    head_html = render_head(
        title,
        asset_fn=asset_fn,
        description='Learn AI engineering through explained lessons, interactive diagrams, worked examples, practical labs, and interview practice.',
    )
    context_label = E(STAGES[current['stage'] - 1][0] if current else 'A course built around understanding')
    body_clean = re.sub(r'<pre(?![^>]*\btabindex=)', '<pre tabindex="0"', body)

    return (
        f'<!doctype html><html lang="en">{head_html}'
        f'<body data-page="{active}" data-question-count="{max_id}" data-topic-count="{study_total}">'
        f'<a class="skip" href="{url("#main")}">Skip to lesson</a>'
        '<aside class="sidebar" id="navigation">'
        f'<a class="brand" href="{url("index.html")}"><b>ai<span>/</span></b>'
        '<strong>ENGINEERING<br><small>THE LEARNING ROADMAP</small></strong></a>'
        '<nav class="utility-nav" aria-label="Course tools">'
        + ''.join(
            f'<a href="{url(href)}">{label}</a>'
            for href, label in (
                ('index.html', 'Learning journey'),
                ('index.html#search', 'Search all topics'),
                ('curriculum-map.html', 'Curriculum map'),
                ('coding-labs.html', 'Coding labs'),
                ('assessments.html', 'Assessments'),
                ('study.html', 'My study record'),
                ('roadmap.html', 'Project experiments'),
                ('glossary.html', 'Terminology guide'),
                ('examples.html', 'Code studio'),
                ('design-scenarios.html', 'Design scenarios'),
            )
        )
        + '</nav>'
        '<p class="nav-label">YOUR LEARNING PATH</p>'
        f'<nav aria-label="Learning stages">{"".join(nav_stages)}</nav>'
        '<div class="sidebar-foot"><small>Explain it. Build it. Test a failure.</small></div>'
        '</aside>'
        '<div class="workspace">'
        '<header class="toolbar">'
        '<button type="button" id="menu-toggle" aria-controls="navigation" aria-expanded="false">Course menu</button>'
        f'<a href="{url("index.html")}#search">Find a topic <kbd>/</kbd></a>'
        f'<span class="toolbar-context">{context_label}</span>'
        '<button type="button" id="theme">Change theme</button>'
        '<button type="button" id="distraction-free">Focus mode</button>'
        '</header>'
        f'<main id="main" tabindex="-1">{body_clean}</main>'
        '<footer>AI Full-Stack Engineering Roadmap · Fictional examples; no model API needed to read the course. '
        f'<a href="{url("provenance.html")}">About this edition</a> · '
        f'<a href="{url("libraries.html")}">References</a> · '
        f'<a href="{url("LICENSE")}" rel="license">MIT license</a></footer>'
        '</div>'
        f'{_SEARCH_DIALOG_HTML}</body></html>'
    )


def _get_default_question_code_map() -> dict[int, dict]:
    global _DEFAULT_QCODE_CACHE
    if _DEFAULT_QCODE_CACHE is None:
        _, _DEFAULT_QCODE_CACHE = load_question_examples(load_chapters())
    return _DEFAULT_QCODE_CACHE


def bookmark_control(q: dict) -> str:
    """Render toggleable bookmark button for a study question or unit."""
    label = 'Bookmark question: ' + teaching_title(q) if q.get('Q') else 'Bookmark this unit'
    return f'<button class="bookmark" type="button" data-bookmark="{q["id"]}" aria-pressed="false" aria-label="{E(label)}">Bookmark</button>'


def question_heading(q: dict, tag: str) -> str:
    """Render question heading paired with its bookmark control."""
    return f'<div class="question-heading"><{tag}>{E(teaching_title(q))}</{tag}>{bookmark_control(q)}</div>'


def controls(q: dict, *, practice_by_topic: dict[int, dict], include_bookmark: bool = True) -> str:
    """Render practice link, optional bookmark button, and explanation notes box."""
    i = q['id']
    practice_link = f'<a href="{url("assessments.html")}#a-{practice_by_topic[i]["id"]}">Test this skill →</a>' if i in practice_by_topic else ''
    bookmark = f'<div class="study-controls">{bookmark_control(q)}</div>' if include_bookmark else ''
    return (
        f'{practice_link}{bookmark}<details class="notes"><summary>Write my explanation</summary>'
        f'<label for="note-{i}">Explain this using your own example</label>'
        f'<textarea id="note-{i}" data-note="{i}" rows="3" '
        'placeholder="What goes in? What happens? What comes out? What could fail?"></textarea></details>'
    )


def question_code(q: dict, question_code_map: dict[int, dict] | None = None) -> str:
    """Render inline runnable or integration code panel attached to a question."""
    code_map = question_code_map if question_code_map is not None else _get_default_question_code_map()
    e = code_map.get(q['id'])
    if e is None:
        return ''
    language = e['language']
    runnable = language == 'python' or bool(e.get('execute')) or bool(e.get('local_executable'))
    default_label = f'{"Python" if language == "python" else "JavaScript"} · offline example' if runnable else language.replace('-sketch', ' integration sketch')
    label = e.get('runtime_label', default_label)
    scope = e.get('limit', _LANGUAGE_SCOPES[language])
    steps = ''.join('<li>' + answer_prose(step) + '</li>' for step in e['steps'].split(' || '))
    expected = f'<pre class="example-output"><code>{E(e["expect"])}</code></pre>' if runnable else f'<p class="example-output">{E(e["expect"])}</p>'
    reference = f'<p><a href="{E(e["reference"])}">Check the primary reference for this example →</a></p>' if e.get('reference') else ''
    change = e.get('change', 'Change one fixture value or boundary condition, predict the result, and rerun or inspect the example. Explain which step changes the outcome.')
    result = (
        f'<section class="question-code" id="code-q{q["id"]}" data-code-example="{E(e["name"])}" '
        f'aria-labelledby="code-title-q{q["id"]}"><span class="micro-label">EXPLAIN IT WITH CODE / {E(label)}</span>'
        f'<h4 id="code-title-q{q["id"]}">What this code does</h4>{answer_prose(e["explain"])}'
        f'<div class="code-panel"><button type="button" class="copy" aria-live="polite" aria-label="Copy code for {E(q["Q"])}">Copy code</button>'
        f'<pre><code class="language-{E(language)}">{E(e["code"])}</code></pre></div>'
        f'<h4>Read it step by step</h4><ol class="code-walkthrough">{steps}</ol>'
        f'<h4>{"Expected output" if runnable else "Expected behavior"}</h4>{expected}'
        f'<p class="code-scope"><strong>How to use it:</strong> {E(scope)}</p>'
        f'<p><strong>Try a change:</strong> {E(change)}</p>'
        f'<p><a href="{url("examples/questions/" + E(e["filename"]))}">Open the example file →</a></p>{reference}</section>'
    )
    return f'<details class="case-data"><summary>Inspect the case data</summary>{result}</details>' if language == 'json' else result


def rigorous_lesson(q: dict) -> str:
    """Render structured deep-dive fields on rigorous foundation lessons."""
    parts: list[str] = []
    if q.get('outcomes'):
        parts.append('<h3>Learning outcomes</h3><ul class="outcomes">' + ''.join(f'<li>{E(o)}</li>' for o in q['outcomes']) + '</ul>')
    for key, heading in (
        ('assumed_knowledge', 'Assumed knowledge'),
        ('motivating_problem', 'Motivating production problem'),
        ('conceptual_model', 'Conceptual model'),
        ('underlying_mechanics', 'Underlying mechanics'),
    ):
        if q.get(key):
            parts.append(f'<h3>{heading}</h3><p>{E(q[key])}</p>')
    if q.get('line_by_line'):
        parts.append('<h3>Read it line by line</h3><ol>' + ''.join(f'<li>{E(l)}</li>' for l in q['line_by_line']) + '</ol>')
    if q.get('edge_cases'):
        parts.append('<h3>Edge cases</h3><ul>' + ''.join(f'<li>{E(e)}</li>' for e in q['edge_cases']) + '</ul>')
    for key, heading in (
        ('tradeoffs', 'Trade-offs'),
        ('security_implications', 'Security implications'),
        ('performance_implications', 'Performance implications'),
        ('debugging', 'Debugging'),
        ('practice', 'Practice'),
        ('recap', 'Recap'),
    ):
        if q.get(key):
            parts.append(f'<h3>{heading}</h3><p>{E(q[key])}</p>')
    if q.get('mastery_checks'):
        parts.append('<h3>Mastery checks</h3><ul>' + ''.join(f'<li>{E(m)}</li>' for m in q['mastery_checks']) + '</ul>')
    if not parts:
        return ''
    return f'<details class="rigorous"><summary>Rigorous authoring detail</summary><div class="rigorous-body">{"".join(parts)}</div></details>'


def _render_qa_body(
    q: dict,
    *,
    writer: AnswerWriter,
    question_code_map: dict[int, dict] | None,
    include_worked_example: bool,
) -> str:
    """Render shared structured Q&A answer sections for both interviews and Q&A-backed lessons."""
    body = writer.render(q['A'], reserve_followups=True)
    if q.get('answer_format') == 'conceptual' and q.get('worked_case'):
        body += writer.section('Worked scenario', q['worked_case'], 'answer-mechanism')
    body += answer_diagram(q)
    if (
        normalize_prose(q['Why']) not in writer.followups
        and not (
            q.get('answer_format') == 'conceptual'
            and normalize_prose(q['Why']) == normalize_prose(q.get('worked_case', ''))
        )
    ):
        why_heading = 'Worked case' if q.get('answer_format') == 'conceptual' else 'How it works'
        body += writer.section(why_heading, q['Why'], 'answer-mechanism')
    if include_worked_example and q.get('worked_case'):
        body += writer.section('Worked example and observed result', q['worked_case'], 'answer-example')
    if q.get('Risk'):
        body += writer.section('Failure boundary', q['Risk'], 'answer-warning')
    if q.get('Trade') and normalize_prose(q['Trade']) not in writer.followups:
        body += writer.section('Design trade-off', q['Trade'], 'answer-decision')
    body += question_content(q, writer)
    body += question_code(q, question_code_map)
    for follow in q.get('follow_ups', []):
        body += writer.section(follow['Q'], follow['A'], 'answer-followup')
    definitions = [
        f'<dt>{E(defn["term"])}</dt><dd>{rendered}</dd>'
        for defn in q.get('definitions', [])
        if (rendered := writer.render(defn['definition']))
    ]
    if definitions:
        body += f'<section class="answer-definitions"><h4>Terminology</h4><dl>{"".join(definitions)}</dl></section>'
    body += answer_terms(q)
    if q.get('Try'):
        body += writer.section('Try it yourself', q['Try'], 'answer-exercise')
    references = list(dict.fromkeys(([q['reference']] if q.get('reference') else []) + q.get('citations', [])))
    if references:
        body += f'<section class="answer-references">{render_reference_list(references, "h4")}</section>'
    return body


def _render_answer_article(
    q: dict,
    body: str,
    *,
    css_class: str = 'interview-question',
    meta_html: str = '',
    practice_by_topic: dict[int, dict] | None = None,
) -> str:
    return (
        f'<article class="{css_class}" id="q{q["id"]}" data-question="{q["id"]}">'
        f'{question_heading(q, "h3")}{meta_html}'
        '<details class="answer"><summary class="answer-toggle" role="button">'
        '<span class="when-closed">View answer</span><span class="when-open">Hide answer</span></summary>'
        f'<div class="answer-body">{body}</div></details>'
        f'{controls(q, practice_by_topic=practice_by_topic or {}, include_bookmark=False)}</article>'
    )


def render_lesson(
    q: dict,
    index: int,
    *,
    question_code_map: dict[int, dict] | None = None,
    practice_by_topic: dict[int, dict] | None = None,
) -> str:
    """Render a foundation lesson article card."""
    writer = AnswerWriter(q)
    if 'A' in q and 'Why' in q:
        body = _render_qa_body(
            q,
            writer=writer,
            question_code_map=question_code_map,
            include_worked_example=False,
        ) + lesson_content(q, url, writer) + rigorous_lesson(q)
        return _render_answer_article(q, body, practice_by_topic=practice_by_topic)

    explanation = writer.render(q['explain'])
    case = writer.render(q['example'])
    case_html = f'<aside class="worked-case"><h4>Worked example</h4>{case}</aside>' if case else ''
    body = (
        f'{explanation}{answer_diagram(q)}{case_html}'
        f'<p class="takeaway"><strong>Keep this idea:</strong> {E(q["takeaway"])}</p>'
        f'{lesson_content(q, url, writer)}{rigorous_lesson(q)}'
        f'{question_code(q, question_code_map)}{answer_terms(q)}'
    )
    return _render_answer_article(
        q,
        body,
        css_class='interview-question lesson question',
        practice_by_topic=practice_by_topic,
    )


def render_interview(
    q: dict,
    *,
    question_code_map: dict[int, dict] | None = None,
    practice_by_topic: dict[int, dict] | None = None,
) -> str:
    """Render an interview question article card with full structured defense."""
    writer = AnswerWriter(q)
    body = _render_qa_body(
        q,
        writer=writer,
        question_code_map=question_code_map,
        include_worked_example=True,
    )
    meta = E(' · '.join(q[k] for k in ('difficulty', 'domain') if q.get(k)))
    return _render_answer_article(
        q,
        body,
        meta_html=f'<p class="question-meta">{meta}</p>',
        practice_by_topic=practice_by_topic,
    )


def chapter_diagram(c: dict) -> str:
    """Render interactive chapter concept flow SVG and step controls."""
    nodes = c['flow']
    width = 1100
    gap = 25
    box = (width - 20 - gap * (len(nodes) - 1)) / len(nodes)
    parts: list[str] = []
    for i, (name, _value) in enumerate(nodes):
        x = 10 + i * (box + gap)
        cx = x + box / 2
        labels = textwrap.wrap(name, 18)
        text = ''.join(f'<tspan x="{cx}" dy="{0 if j == 0 else 20}">{E(t)}</tspan>' for j, t in enumerate(labels))
        parts.append(
            f'<g data-diagram-step="{i}" class="flow-node {"active" if i == 0 else ""}">'
            f'<rect x="{x}" y="15" width="{box}" height="102" rx="14"/>'
            f'<text x="{cx}" y="39" class="node-number">0{i + 1}</text>'
            f'<text x="{cx}" y="{68 if len(labels) == 1 else 61}" class="node-title">{text}</text></g>'
        )
        if i < len(nodes) - 1:
            parts.append(f'<path d="M{x + box + 4} 66 h{gap - 9}" marker-end="url(#arrow-{c["slug"]})" class="flow-arrow"/>')

    mobile = '<ol class="mobile-flow" aria-label="Example flow in order">' + ''.join(
        f'<li data-diagram-step="{i}" class="{"active" if i == 0 else ""}"><span>{i + 1:02}</span><strong>{E(name)}</strong></li>'
        for i, (name, _val) in enumerate(nodes)
    ) + '</ol>'
    buttons = ''.join(
        f'<button type="button" data-flow-step="{i}" data-title="{E(name)}" data-value="{E(value)}" '
        f'aria-pressed="{str(i == 0).lower()}">{i + 1}. {E(name)}</button>'
        for i, (name, value) in enumerate(nodes)
    )
    transcript = ''.join(f'<li><strong>{E(name)}</strong>: {E(value)}</li>' for name, value in nodes)
    flow_summary = ' → '.join(n for n, _v in nodes)
    return (
        '<section class="concept-lab" id="walkthrough" data-flow>'
        '<div class="section-title"><div><span class="micro-label">SEE IT HAPPEN</span>'
        '<h2>Follow the example through the system</h2></div><span class="interactive-badge">INTERACTIVE WALKTHROUGH</span></div>'
        f'<p>{E(c["case"][0])}</p><div class="flow-canvas"><svg viewBox="0 0 {width} 135" role="img" '
        f'aria-labelledby="diagram-title-{c["slug"]}"><title id="diagram-title-{c["slug"]}">'
        f'{E(c["goal"])}: {E(flow_summary)}</title><defs><marker id="arrow-{c["slug"]}" markerWidth="7" '
        'markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6"/></marker></defs>'
        f'{"".join(parts)}</svg></div>{mobile}'
        f'<details><summary>Read the complete walkthrough transcript</summary><ol>{transcript}</ol>'
        f'<p><strong>Failure case:</strong> {E(c["case"][2])}</p></details>'
        f'<div class="flow-buttons" role="group" aria-label="Choose a step">{buttons}</div>'
        f'<div class="trace-output" aria-live="polite"><span class="micro-label" data-flow-label>STEP 1 / {E(nodes[0][0])}</span>'
        f'<p data-flow-result>{E(nodes[0][1])}</p><p class="trace-meaning" data-flow-meaning>{E(c["case"][1])}</p></div>'
        '<div class="flow-controls"><button type="button" data-flow-next>Next step →</button>'
        '<button type="button" data-flow-fail aria-pressed="false">What if this goes wrong?</button></div>'
        f'<p data-flow-failure hidden class="failure-note">{E(c["case"][2])}</p></section>'
    )


def chapter_code_panel(c: dict, code_notes: dict[str, list[str]], chapter_examples: dict[str, dict]) -> str:
    """Render chapter-level runnable example panel."""
    e = chapter_examples[c['slug']]
    extension = _EXTENSION_BY_LANG[e['language']]
    assertions: list[str] = []
    if e['language'] == 'python':
        tree = ast.parse(e['code'])
        assertions = [ast.unparse(n.test) for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    notes = '<ol>' + ''.join(f'<li>{E(note)}</li>' for note in code_notes[c['slug']]) + '</ol>'
    proof_items = ''.join(f'<li><code>{E(x)}</code></li>' for x in assertions[:3])
    proof = (
        '<p>The assertions below state the behavior this small example checks. Read the inputs and expected result, '
        f'then change one input and predict whether the check will still pass.</p><ul class="assertions">{proof_items}</ul>'
        if proof_items
        else '<p>This integration sketch needs the compatible dependencies and host configuration described in its scope. It is not an automatically running service in this website.</p>'
    )
    return (
        '<section class="code-studio" id="chapter-example"><div class="section-title">'
        '<div><span class="micro-label">FROM IDEA TO CODE</span><h2>How does a small implementation work?</h2></div>'
        f'<span>{E(e["language"])}</span></div><p>{E(e["scope"])}</p>'
        f'<div class="code-reading"><p><strong>What this demonstrates:</strong> {E(c["goal"])}.</p>'
        f'<p><strong>Connect it to the case:</strong> {E(c["case"][0])} {E(c["case"][1])}</p></div>'
        f'<div class="code-panel"><button type="button" class="copy" aria-live="polite">Copy code</button><pre><code>{E(e["code"])}</code></pre></div>'
        f'<details open class="code-explanation"><summary>How to read and test this code</summary>{notes}{proof}'
        f'<p><strong>The boundary to investigate:</strong> {E(c["case"][2])}</p>'
        f'<p><strong>Next change to make:</strong> {E(c["questions"][0]["Try"])}</p></details>'
        f'<a href="{url("examples/" + c["slug"] + extension)}">Open the teaching file →</a></section>'
    )


def chapter_lab(c: dict, identifier: str = 'chapter-lab') -> str:
    """Render build/break/explain experiment checklist for a chapter."""
    return (
        f'<section class="chapter-lab" id="{identifier}"><span class="micro-label">BUILD / BREAK / EXPLAIN</span>'
        f'<h2>Turn this chapter into a working experiment</h2><p>{E(c["case"][0])}</p><ol>'
        f'<li><strong>Build the normal path.</strong> {E(c["questions"][0]["Try"])}</li>'
        f'<li><strong>Introduce the failure.</strong> {E(c["case"][2])}</li>'
        '<li><strong>Verify recovery.</strong> Record what the user sees and what authoritative state remains.</li>'
        f'<li><strong>Defend a trade-off.</strong> {E(c["questions"][-1]["Trade"])}</li></ol>'
        '<p class="takeaway">Bring back a small implementation, observed input/output, one failure demonstration, and your own explanation.</p></section>'
    )


def capstone_links(chapter: dict) -> str:
    """Link owning and portfolio chapters to downloadable local capstone specs."""
    selected = [(identity, title) for identity, (owner, title) in _CAPSTONE_LINKS.items() if chapter['slug'] in (owner, 'portfolio-capstone')]
    if not selected:
        return ''
    links = ''.join(f'<li><a href="{url("capstone-" + identity + ".html")}">{E(title)}</a></li>' for identity, title in selected)
    return (
        '<section class="chapter-lab" id="local-projects"><h2>Put this topic into practice</h2>'
        f'<p>Use the starter, failure cases and review rubric to build and defend your own implementation.</p><ul>{links}</ul>'
        f'<p><a href="{url("examples/local-projects.zip")}">Download local project sources and setup</a></p></section>'
    )


def review_panel(c: dict, by_slug: dict[str, dict]) -> str:
    """Render review notes callout and optional chapter capstone milestones."""
    r = c['review']
    extra = ''
    if r.get('capstone'):
        cap = r['capstone']
        phases = ''.join(
            f'<div class="capstone-phase"><h4>{E(p["name"])}</h4><ul>'
            + ''.join(f'<li>{E(s)}</li>' for s in p['steps'])
            + f'</ul><p class="capstone-verify"><strong>Verify:</strong> {E(p["verify"])}</p></div>'
            for p in cap['phases']
        )
        prereqs = ''.join(f'<a href="{url(p + ".html")}">{E(by_slug[p]["title"])}</a>' for p in cap['prerequisite_chapters'])
        artifacts = ', '.join(E(a) for a in cap['artifacts'])
        extra = f'<section class="capstone-project"><h2>{E(cap["title"])}</h2><p>{E(cap["description"])}</p>{phases}<p><strong>Builds on:</strong> {prereqs}</p><p><strong>Deliverables:</strong> {artifacts}</p></section>'

    return (
        '<aside class="worked-case" id="review-notes" aria-label="Content review notes">'
        '<span class="micro-label">REVIEW NOTES / ADDED LEARNING SUPPORT</span>'
        f'<h2>What to strengthen in this chapter</h2>{paragraphs(r["review"])}'
        '<p>The original material is retained. The additional explanations below connect the idea to implementation; '
        'use the deeper questions after you can explain the example.</p>'
        f'{extra}<a href="#recommended-practice">Try the recommended extension and completion checks →</a></aside>'
    )


def review_practice(c: dict) -> str:
    """Render observable completion checks and downloadable lab links."""
    r = c['review']
    links = ''.join(f'<li><a href="{E(href)}">{E(name)}</a></li>' for name, href in r['references'])
    for filename in r.get('labs', []):
        if Path(filename).name != filename or not (LABS / filename).is_file():
            raise ValueError('Unknown chapter lab: ' + filename)
        links += f'<li><a href="{url("examples/labs/" + filename)}">Download {E(filename)}</a></li>'
    if c['slug'] in {'foundations', 'models', 'database-modeling', 'embeddings', 'retrieval', 'evaluation'}:
        links = (
            f'<li><a href="{url("examples/labs/foundation_bridge.py")}">'
            'Run the offline foundation bridge: gradient, cosine, metrics, and SQL</a> — Python 3.10+, standard library only; '
            'save the file and run <code>python foundation_bridge.py</code>.</li>' + links
        )
    return (
        '<section class="chapter-lab" id="recommended-practice">'
        '<span class="micro-label">ADDITIONAL PRACTICE / CHECK THE RESULT</span>'
        f'<h2>Extend the experiment</h2>{paragraphs(r["build"])}'
        f'<h3>Observable completion checks</h3>{paragraphs(r["verify"])}'
        '<p>Keep the command, fixture version, observed result, one failure case, and your trade-off explanation with your implementation. '
        'These are exercises to implement; their presence does not mean the described production behavior has already been built.</p>'
        '<h3>Primary references</h3><p>Use the reference matching your installed version for exact API details. '
        f'The explanations and worked cases in this course provide the learning path; references support implementation and further study.</p><ul>{links}</ul></section>'
    )


def coverage_review(chapters: list[dict]) -> str:
    """Render responsibility-level coverage comparison table and chapter notes."""
    rows = [
        ('Programming and reproducibility', 'The entry lessons assumed the ability to run and inspect code.', 'foundations', 'Added runtime setup, functions and collections, debugging, Git, and a clean-checkout exercise.'),
        ('Web and frontend engineering', 'Realtime behavior was better explained than the ordinary interface underneath it.', 'application-architecture', 'Added HTTP, JSON, JavaScript promises, types, data structures, and a fake-provider vertical slice. See product delivery for HTML, CSS, component state, forms, race handling, and accessibility.'),
        ('ML foundations', 'Training and model choice needed numerical examples before advanced terminology.', 'models', 'Added a gradient update, supervised-learning baselines, precision and recall, data leakage, attention shapes, and adaptation/serving experiments in model engineering.'),
        ('Data and retrieval', 'Correct mechanisms needed more worked calculations and recovery criteria.', 'database-modeling', 'Added SQL relationships, schema compatibility, concurrency races, source deletion, ingestion publication, vector similarity, fusion arithmetic, and per-slice retrieval checks.'),
        ('Agent and protocol engineering', 'Framework examples needed a plain-code baseline and compatibility discipline.', 'agent-harness', 'Added controlled loops, unknown effect reconciliation, replay-safe nodes, delegated scope, bounded tools, and version-pinned contract exercises.'),
        ('Testing and evidence', 'Broad experiments needed observable outcomes and an independent oracle.', 'evaluation', 'Added metric arithmetic, layered deterministic tests, effect-ledger checks, paired comparisons, uncertainty, and portable evaluation records.'),
        ('Delivery and operations', 'Readiness guidance needed an executable delivery and recovery plan.', 'deployment-reliability', 'Added container/state boundaries, CI artifacts, secrets, gradual rollout, recovery and capacity arithmetic, quotas, and capstone handoff requirements.'),
    ]
    table = ''.join(
        f'<tr><th scope="row">{E(area)}</th><td>{E(gap)}</td><td><a href="{url(slug + ".html")}#review-notes">{E(added)}</a></td></tr>'
        for area, gap, slug, added in rows
    )
    chapter_cards = ''.join(
        f'<section class="map-card"><h3><a href="{url(c["slug"] + ".html")}#review-notes">{E(c["title"])}</a></h3>'
        f'{paragraphs(c["review"]["review"])}'
        f'<p><strong>Recommended work:</strong> {E(c["review"]["build"])}</p>'
        f'<p><strong>Completion evidence:</strong> {E(c["review"]["verify"])}</p></section>'
        for c in chapters
    )
    return (
        '<section class="prose" id="content-review"><p class="eyebrow">CONTENT REVIEW / 19 OCTOBER 2026</p>'
        '<h2>Use the course as a central learning path</h2>'
        '<p>The original AI-focused chapters provide particularly strong coverage of retrieval, evidence, agent boundaries, and realtime behavior. '
        'The review found thinner explanations of prerequisite programming, ordinary frontend development, mathematical learning steps, '
        'and how to verify a completed implementation. The additions address those gaps within the existing chapters and preserve the original lessons and study identifiers.</p>'
        '<p>Study one sequence: understand the explanation, trace the example, implement it, reproduce a failure, and defend a trade-off. '
        'Questions are not assigned experience levels. If you already know a concept, demonstrate its completion checks and continue into the deeper material.</p>'
        '<p>This can organize your learning in one place, but reading the pages alone cannot establish full-stack engineering competence. '
        'SDK sketches are not complete deployed services, proposed exercises are not measured results, and some projects need optional dependencies or provider access. '
        'Operating a project, collaborating in review, and responding to real incidents remain necessary practice. Use primary references for version-specific implementation details.</p></section>'
        '<div class="table-scroll" role="region" aria-label="Coverage comparison" tabindex="0">'
        f'<table><caption>Coverage gaps and additions</caption><thead><tr><th scope="col">Responsibility</th><th scope="col">Gap found</th><th scope="col">Addition and starting chapter</th></tr></thead><tbody>{table}</tbody></table></div>'
        '<section class="prose"><h2>A practical route through the additions</h2><ol>'
        '<li>Begin with Programming foundations, Computer science, Web fundamentals and Frontend foundations. Build a deterministic form-to-result path before paying for model calls.</li>'
        '<li>Work through model mathematics and a small training experiment, then build the authorized data and retrieval path using synthetic fixtures.</li>'
        '<li>Connect one provider and evaluate it against the baseline. Add agents only for tasks that benefit from choosing tools dynamically.</li>'
        '<li>Use Frontend foundations before Product delivery, then extend the same task to streaming, voice, or remote agents. Treat alternative frameworks as comparisons rather than a mandatory combined stack.</li>'
        '<li>Finish with the delivery pipeline, recovery drill, and capstone handoff. Revisit the first boundary you cannot demonstrate without following the page.</li></ol>'
        f'<p><a href="{url("programming-foundations.html")}#review-notes">Start programming foundations →</a> · '
        f'<a href="{url("product-delivery.html")}#review-notes">Open frontend practice →</a> · '
        f'<a href="{url("portfolio-capstone.html")}#recommended-practice">Check the final handoff →</a></p>'
        f'<h2>Chapter-by-chapter findings and recommendations</h2></section>{chapter_cards}'
    )


def rag_playground() -> str:
    """Render deterministic RAG evidence playground panel on Foundations chapter."""
    return (
        '<section class="rag-playground" data-rag-playground><div class="section-title"><div>'
        '<span class="micro-label">CHANGE ONE INPUT / OBSERVE THE CONSEQUENCE</span>'
        '<h2>What can this evidence support?</h2></div></div>'
        "<p>The customer's question stays the same: <strong>Can I get a refund for a sale item?</strong> "
        'Change what retrieval supplies and see why the next action changes.</p>'
        '<label for="rag-scenario">Evidence returned by the search</label>'
        '<select id="rag-scenario"><option value="supported">The actual sale-item rule</option>'
        '<option value="irrelevant">An unrelated shipping article</option>'
        '<option value="missing">No matching passage</option>'
        '<option value="outage">Search service unavailable</option></select>'
        '<div class="scenario-result" aria-live="polite"><span class="micro-label">THE READING PACKET</span>'
        '<pre><code id="rag-packet"></code></pre><span class="micro-label">THE SUPPORTED NEXT ACTION</span>'
        '<p id="rag-action"></p><p class="takeaway" id="rag-reason"></p></div>'
        '<small>Deterministic teaching simulation. These outcomes illustrate an evidence policy; no model is being called.</small></section>'
    )


def design_system_showcase() -> str:
    """Render design token and component reference page."""
    return (
        '<section class="design-showcase"><h1>Design System Showcase</h1>'
        '<p class="subtitle">Every component used across the learning guide, with realistic AI lesson content.</p>'
        '<h2>Design Tokens</h2><table class="comparison-table"><caption>Design tokens in light and dark themes</caption>'
        '<thead><tr><th>Token</th><th>Light</th><th>Dark</th><th>Usage</th></tr></thead><tbody>'
        '<tr><td>--bg</td><td>#f4f6fb</td><td>#0c1423</td><td>Page background</td></tr>'
        '<tr><td>--panel</td><td>#fff</td><td>#141f32</td><td>Card/panel surface</td></tr>'
        '<tr><td>--text</td><td>#1a2941</td><td>#e9effb</td><td>Primary text</td></tr>'
        '<tr><td>--accent</td><td>#2458d3</td><td>#96b7ff</td><td>Links, accents</td></tr>'
        '<tr><td>--mint</td><td>#08766c</td><td>#75dec8</td><td>Success, mastery</td></tr>'
        '<tr><td>--warm</td><td>#8b5208</td><td>#f0be75</td><td>Warnings</td></tr></tbody></table>'
        '<h2>Typography Scale</h2><p class="callout callout-definition"><span class="callout-icon">A</span>'
        'Root: 16px · Scale: xs 0.75rem, sm 0.875rem, base 1rem, lg 1.125rem, xl 1.25rem, 2xl 1.5rem, 3xl 2rem</p>'
        '<h2>Components</h2><h3>Comparison Table</h3><table class="comparison-table">'
        '<thead><tr><th>Approach</th><th>Best for</th><th>Trade-off</th></tr></thead><tbody>'
        '<tr><td>Dense retrieval</td><td>Semantic similarity</td><td>Misses exact terms</td></tr>'
        '<tr><td>BM25 keyword</td><td>Exact term matching</td><td>Misses synonyms</td></tr>'
        '<tr><td>Hybrid + RRF</td><td>Both semantic and exact</td><td>More infrastructure</td></tr></tbody></table>'
        '<h3>Math Block</h3><div class="math-block"><span class="math-label">Cosine similarity</span>sim(A,B) = (A · B) / (||A|| × ||B||)</div>'
        '<h3>Quote Block</h3><div class="quote-block"><p>Task success is real authorized state, not fluent text.</p>'
        '<p class="quote-source">— Agent evaluation lesson</p></div>'
        '<h3>Callouts</h3>'
        '<div class="callout callout-definition"><span class="callout-icon">D</span><strong>Definition:</strong> An oracle is an independent specification of correct behavior.</div>'
        '<div class="callout callout-tip"><span class="callout-icon">T</span><strong>Tip:</strong> Use deterministic oracles where possible; reviewed judgments only where needed.</div>'
        '<div class="callout callout-warning"><span class="callout-icon">W</span><strong>Warning:</strong> Random sleep tests do not reliably reproduce races.</div>'
        '<div class="callout callout-danger"><span class="callout-icon">!</span><strong>Danger:</strong> An oracle that only checks final text misses unauthorized side effects.</div>'
        '<div class="callout callout-production"><span class="callout-icon">P</span><strong>Production:</strong> Validate every tool parameter against a schema before execution.</div>'
        '<h3>Glossary Term</h3><p>Use <a class="glossary-term" href="glossary.html">RAG</a> to ground answers in your documents.</p>'
        '<h3>Figure + Caption</h3><figure class="lesson-figure">'
        '<svg viewBox="0 0 360 150" role="img" aria-label="Retriever sends evidence to generator" width="360" height="150" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="50" y="50" width="100" height="60" fill="var(--panel2)" stroke="var(--line)"/>'
        '<text x="100" y="85" text-anchor="middle" fill="var(--text)">Retriever</text>'
        '<rect x="200" y="50" width="100" height="60" fill="var(--panel2)" stroke="var(--line)"/>'
        '<text x="250" y="85" text-anchor="middle" fill="var(--text)">Generator</text>'
        '<line x1="150" y1="80" x2="200" y2="80" stroke="var(--accent)" stroke-width="2" marker-end="url(#arr)"/>'
        '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<polygon points="0 0, 8 4, 0 8" fill="var(--accent)"/></marker></defs></svg>'
        '<figcaption>RAG pipeline: retriever feeds evidence to generator. '
        '<span class="figure-alt">Alt: Two boxes labeled Retriever and Generator with an arrow from Retriever to Generator.</span></figcaption></figure>'
        '<h3>Expandable Follow-up</h3><details class="expandable-followup">'
        '<summary>Why evaluate the full trajectory instead of just the answer?</summary>'
        '<div class="followup-content"><p>Fluent final text can mask unauthorized reads, duplicate writes, or wrong tool choices. '
        'The effect ledger captures every tool call, argument, result, and durable write so evaluation checks actual behavior, not just prose.</p></div></details>'
        '<h3>Next / Prerequisite Navigation</h3><div class="nav-pair"><a href="api-security.html" class="nav-prev">← Prerequisite: API Security</a>'
        '<a href="agent-evaluation.html" class="nav-next">Next: Agent Evaluation →</a></div>'
        '<h3>Detailed interview answers</h3><p>Use <strong>View answer</strong> to reveal one detailed explanation '
        'with worked cases, diagrams, code where useful, trade-offs and follow-up exercises.</p></section>'
    )


def _public_lab_ignore(directory: str, names: list[str]) -> list[str]:
    return [
        name for name in names
        if name.startswith('.')
        or name in {'__pycache__', 'node_modules'}
        or (Path(directory) / name).is_symlink()
        or ((Path(directory) / name).is_file() and Path(name).suffix not in _LAB_ALLOWED_SUFFIXES)
    ]


def _prepare_runtime_and_diagrams(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    (out / '.nojekyll').write_text('', encoding='utf-8')
    shutil.copy2(ROOT / 'LICENSE', out / 'LICENSE')
    for source in ASSETS.glob('*/*'):
        if source.is_file():
            shutil.copy2(source, out / source.name)
    for directory in ('diagrams', 'examples'):
        (out / directory).mkdir()
    shutil.copytree(CONTENT / 'runtime', out / 'runtime')

    pyodide_dir = ROOT / 'vendor/pyodide'
    manifest_file = pyodide_dir / 'runtime-manifest.json'
    if manifest_file.exists():
        from vendor_pyodide import FILES, VERSION

        runtime_manifest = read_json(manifest_file)
        if runtime_manifest.get('version') != VERSION:
            raise ValueError('Runtime version mismatch; rerun make runtime')
        (out / 'runtime/pyodide').mkdir()
        for runtime_name in FILES:
            runtime_file = pyodide_dir / runtime_name
            if hashlib.sha256(runtime_file.read_bytes()).hexdigest() != runtime_manifest['files'].get(runtime_name):
                raise ValueError('Runtime integrity mismatch: ' + runtime_name)
            shutil.copy2(runtime_file, out / 'runtime/pyodide' / runtime_name)
        shutil.copy2(manifest_file, out / 'runtime/pyodide/runtime-manifest.json')

    for stem in ('context', 'harness', 'streaming', 'quality'):
        text = (CONTENT / 'diagrams' / f'{stem}.html').read_text(encoding='utf-8')
        text = re.sub(r'<button\b[^>]*\bdata-print\b[^>]*>.*?</button>', '', text, flags=re.S)
        text = text.replace(
            "item=>item.matches('[data-print]') ? window.print() : exportImage(item.dataset.exportImage)",
            'item=>exportImage(item.dataset.exportImage)',
        )
        text = re.sub(r'"sourcePath":"[^"]*"', f'"sourcePath":"content/diagrams/{stem}.archify.md"', text)
        text = re.sub(r'<link\b[^>]*\brel=["\'](?:shortcut )?icon["\'][^>]*>', '', text)
        text = text.replace('</head>', '<link rel="icon" type="image/svg+xml" sizes="any" href="../favicon.svg"></head>', 1)
        text = re.sub(r'"baseDir":"[^"]*"', '"baseDir":"content/diagrams"', text)
        (out / 'diagrams' / f'{stem}.html').write_text(text, encoding='utf-8')


def build_site(out: Path = BUILD_OUT) -> dict:
    """Validate content, generate HTML/shards/examples into _build, and write manifest.json."""
    from validate_curriculum import validate as validate_curriculum

    validate_curriculum()
    chapters = load_chapters()
    by_slug = {c['slug']: c for c in chapters}
    curriculum = read_json(CONTENT / 'curriculum.json')
    courses = load_courses()
    question_recipes, question_code_map = load_question_examples(chapters)
    _, chapter_examples = load_chapter_examples()
    validate_diagrams(chapters)
    practice_items, _labs = load_practice(chapters)
    practice_by_topic = {item['topic']: item for item in practice_items}
    code_notes = {c['slug']: read_json(CONTENT / 'chapters' / c['slug'] / 'code-notes.json') for c in chapters}

    ids = [q['id'] for c in chapters for q in c['questions'] + c['lessons']]
    course_study_ids = [unit['study_id'] for course in courses for unit in course['units']]
    total = len(ids)
    study_total = total + len(course_study_ids)
    max_id = max(ids + course_study_ids)

    _prepare_runtime_and_diagrams(out)

    def write_html(name: str, title: str, body: str, active: str = '') -> None:
        html_doc = render_page(
            title,
            body,
            chapters=chapters,
            by_slug=by_slug,
            max_id=max_id,
            study_total=study_total,
            out=out,
            active=active,
        )
        (out / name).write_text(html_doc, encoding='utf-8')

    search_entries: list[dict] = []
    for c in chapters:
        for group, kind in (('lessons', 'Foundation interview'), ('questions', 'Interview depth')):
            for q in c[group]:
                keys = ('Q', 'explain', 'example', 'takeaway') if (group == 'lessons' and 'A' not in q) else ('Q', 'A', 'Why', 'Risk', 'Trade', 'Try')
                extra_code = question_code_map.get(q['id'], {})
                search_entries.append({
                    'id': q['id'],
                    'slug': c['slug'],
                    'chapter': c['title'],
                    'title': teaching_title(q),
                    'type': kind,
                    'text': f"{' '.join(q.get(k, '') for k in keys)} {extra_code.get('explain', '')} {extra_code.get('code', '')}",
                })
    question_shards = build_question_shards(out, chapters)
    for entry in search_entries:
        entry['href'] = f'{entry["slug"]}.html#q{entry["id"]}'
        entry['text'] = entry['text'][:2200]
    for course in courses:
        for unit in course['units']:
            search_entries.append({
                'id': unit['study_id'],
                'slug': f'course-{course["id"]}',
                'track': 'courses',
                'chapter': course['title'],
                'title': unit['title'],
                'type': 'Engineering course',
                'href': f'course-{unit["id"]}.html',
                'text': ' '.join([unit['title'], *unit['outcomes'], *[i['question'] for i in unit['interviews']], *unit['narrative']])[:2200],
            })
    build_search_shards(out, search_entries, curriculum)

    write_html('design-scenarios.html', 'Advanced system-design scenarios', scenario_page(chapters, url))

    for position, c in enumerate(chapters):
        previous = chapters[position - 1] if position else None
        following = chapters[position + 1] if position + 1 < len(chapters) else None
        prereq_links = ' · '.join(
            f'<a href="{url(slug + ".html")}">{E(by_slug[slug]["title"])}</a>'
            for slug in curriculum['chapters'][c['slug']]['prerequisites']
        ) or 'No prerequisite chapters. Start here.'
        terms_html = ''.join(
            f'<div><dt><a href="{url("glossary.html")}#{term_id(name)}">{E(name)}</a></dt><dd>{E(meaning)}</dd></div>'
            for name, meaning in c['terms']
        )
        mins = chapter_reading_minutes(c)
        lessons_html = ''.join(
            render_lesson(q, i, question_code_map=question_code_map, practice_by_topic=practice_by_topic)
            for i, q in enumerate(c['lessons'], 1)
        )
        bank_html = ''.join(
            render_interview(q, question_code_map=question_code_map, practice_by_topic=practice_by_topic)
            for q in c['questions']
        )
        toc = ''.join(f'<a href="#q{q["id"]}">{i}. {E(teaching_title(q))}</a>' for i, q in enumerate(c['lessons'], 1))
        toc += ''.join(
            f'<a href="#q{q["id"]}">{i}. {E(teaching_title(q))}</a>'
            for i, q in enumerate(c['questions'], len(c['lessons']) + 1)
        )
        prev_link = f'<a href="{url(previous["slug"] + ".html")}">← {E(previous["title"])}</a>' if previous else f'<a href="{url("index.html")}">← Learning journey</a>'
        next_link = f'<a href="{url(following["slug"] + ".html")}">Continue: {E(following["title"])} →</a>' if following else f'<a href="{url("roadmap.html")}">Revisit your experiments →</a>'
        pager = f'<nav class="pager">{prev_link}{next_link}</nav>'
        sim_html = simulation_panel(SIMULATION_CHAPTERS[c['slug']], url) if c['slug'] in SIMULATION_CHAPTERS else ''
        play_html = rag_playground() if c['slug'] == 'foundations' else ''
        course_unit_ids = curriculum['chapters'][c['slug']].get('course_units', [])
        unit_links = (
            '<section class="prose" id="worked-units"><h2>Worked examples and local projects</h2>'
            '<p>Continue this topic through its detailed implementation, failure cases and independent practice.</p><ol>'
            + ''.join(f'<li><a href="{url("course-" + identity + ".html")}">{E(identity.replace("-", " "))}</a></li>' for identity in course_unit_ids)
            + '</ol></section>'
            if course_unit_ids
            else ''
        )
        body = (
            f'<div class="chapter-breadcrumb"><a href="{url("index.html")}#stage-{c["stage"]}">'
            f'STAGE {c["stage"]} / {E(STAGES[c["stage"] - 1][0])}</a><span>Explain → apply → investigate</span></div>'
            f'<section class="chapter-hero"><div><p class="eyebrow">CHAPTER {position + 1:02} / {E(c["title"])}</p>'
            f'<h1>{E(c["goal"])}</h1><p class="subtitle">{E(c["intro"])}</p></div>'
            f'<aside class="outcome-card"><span class="micro-label">BY THE END, YOU CAN EXPLAIN</span>'
            f'<p>{E(c["case"][1])}</p><small>Before this chapter: {prereq_links}</small>'
            f'<p class="track-meta">About {mins} min read · {len(c["lessons"]) + len(c["questions"])} interview questions · all answers on this page</p>'
            '</aside></section>'
            '<nav class="section-nav" aria-label="Chapter sections">'
            '<a href="#walkthrough">See the flow</a><a href="#learn">Core questions</a>'
            '<a href="#chapter-example">Read the code</a><a href="#interview">Deep dive questions</a>'
            '<a href="#chapter-lab">Build it</a><a href="#review-notes">Review notes</a>'
            '<a href="#recommended-practice">Extend it</a></nav>'
            f'{question_finder(c, url)}{chapter_diagram(c)}{sim_html}{play_html}'
            f'<section class="terms-panel"><h2>Which terms do you need for these questions?</h2><dl>{terms_html}</dl>'
            f'<a href="{url("glossary.html")}">Open the full terminology guide →</a></section>'
            f'<div class="reading-layout"><div>{review_panel(c, by_slug)}'
            '<section id="learn" class="interview-bank"><div class="section-title"><div>'
            '<span class="micro-label">CORE SYSTEM MECHANICS</span><h2>Core interview questions and detailed answers</h2></div>'
            f'<button id="practice" type="button" aria-pressed="false">View all answers</button></div>{lessons_html}</section>'
            f'{unit_links}{chapter_code_panel(c, code_notes, chapter_examples)}'
            '<section id="interview" class="interview-bank"><span class="micro-label">SYSTEM DESIGN & FAILURE BOUNDARIES</span>'
            '<h2>Deep dive engineering questions</h2><p>Continue on this page through detailed explanations, worked cases, '
            'failure boundaries and design decisions. Acronyms used in an answer are explained inside it. '
            'All chapter answers are included here; there is no question-count cap.</p>'
            f'<button id="expand" type="button">View all answers</button>{bank_html}</section>'
            f'{chapter_lab(c)}{review_practice(c)}{capstone_links(c)}{pager}</div>'
            f'<aside class="lesson-toc"><span class="micro-label">IN THIS CHAPTER</span>{toc}'
            '<a href="#chapter-example">→ Code walkthrough</a><a href="#chapter-lab">→ Practical experiment</a>'
            '<a href="#recommended-practice">→ Completion checks</a></aside></div>'
        )
        write_html(f'{c["slug"]}.html', c['goal'], body, c['slug'])

    for slug, e in chapter_examples.items():
        (out / 'examples' / f'{slug}{_EXTENSION_BY_LANG[e["language"]]}').write_text(e['code'], encoding='utf-8')
    question_dir = out / 'examples/questions'
    question_dir.mkdir()
    for recipe in question_recipes.values():
        (question_dir / recipe['filename']).write_text(recipe['code'], encoding='utf-8')
    write_json(
        question_dir / 'index.json',
        {
            str(qid): {'recipe': e['name'], 'file': e['filename'], 'language': e['language'], 'expected': e['expect']}
            for qid, e in question_code_map.items()
        },
    )
    shutil.copytree(LABS, out / 'examples/labs', ignore=_public_lab_ignore)
    (out / 'examples/__init__.py').write_text('', encoding='utf-8')
    (out / 'examples/labs/__init__.py').write_text('', encoding='utf-8')

    stage_cards = []
    for n, (title, _level, summary, slugs) in enumerate(STAGES, 1):
        items = ''.join(
            f'<a class="chapter-card" href="{url(slug + ".html")}">'
            f'<span class="card-number">{chapters.index(by_slug[slug]) + 1:02}</span><div>'
            f'<small>{E(by_slug[slug]["title"])}</small><h3>{E(by_slug[slug]["goal"])}</h3>'
            f'<p>{E(by_slug[slug]["intro"])}</p>'
            '<span class="card-link">Explained lessons · diagram · code · lab →</span></div></a>'
            for slug in slugs
        )
        stage_cards.append(
            f'<section class="journey-stage" id="stage-{n}"><div class="stage-heading">'
            f'<span class="stage-number">{n:02}</span><div><span class="micro-label">EXPLAIN / APPLY / INVESTIGATE</span>'
            f'<h2>{E(title)}</h2><p>{E(summary)}</p></div></div><div class="chapter-grid">{items}</div></section>'
        )

    options = ''.join(f'<option value="{c["slug"]}">{E(c["title"])}</option>' for c in chapters)
    options += ''.join(f'<option value="course-{c["id"]}">{E(c["title"])}</option>' for c in courses)
    track_list = ''.join(
        f'<li><a href="{url("tracks/" + t["id"] + ".html")}">{E(t["title"])}</a> — {E(t["description"])}</li>'
        for t in curriculum['tracks']
    )
    home = (
        '<section class="home-hero"><div><p class="eyebrow">A GUIDED COURSE FOR AI FULL-STACK ENGINEERS</p>'
        '<h1>Understand the idea.<br><em>See it work.</em><br>Build it yourself.</h1>'
        '<p class="subtitle">Begin with Python, computer science, HTTP and accessible interfaces. '
        'Continue through data, mathematics and machine learning before RAG, agents and production systems. '
        'Every chapter explains a real problem, walks through a concrete example, and gives you something to build.</p>'
        f'<a class="primary" href="{url("programming-foundations.html")}">Start with programming foundations →</a>'
        f'<a class="continue-link" id="continue-reading" href="{url("roadmap.html")}">Choose your learning path</a></div>'
        '<aside class="preview-card"><span class="micro-label">THIS IS HOW THE COURSE TEACHES</span>'
        '<h2>Can you transform three records safely?</h2>'
        '<div class="preview-flow"><span>Read the input</span>↓<span>Validate its type</span>↓<span>Transform the values</span>↓<span>Check the expected result</span></div>'
        '<p>You will follow the information, inspect the code, then see what happens when a step fails.</p>'
        f'<a href="{url("programming-foundations.html")}#walkthrough">Try the first walkthrough →</a></aside></section>'
        '<section class="learning-contract">'
        '<div><b>01</b><h2>Start with a use case</h2><p>Know the problem before learning its terminology.</p></div>'
        '<div><b>02</b><h2>Trace inputs and outputs</h2><p>Step through a chapter-specific diagram and simulate a failure.</p></div>'
        '<div><b>03</b><h2>Build and defend</h2><p>Read the code, test a boundary, explain a trade-off.</p></div></section>'
        '<section class="journey-intro"><p class="eyebrow">EXPLANATIONS → WORKED EXAMPLES → DEEPER PRACTICE</p>'
        '<h2>A path with prerequisites,<br>not a list of technologies.</h2>'
        '<p>Follow the stages in order, or use the chapter\'s prerequisite link to fill a gap. '
        'Chapter depth follows the subject; there is no fixed question quota.</p></section>'
        + ''.join(stage_cards)
        + '<section class="search-panel" id="search"><span class="micro-label">FIND A CONCEPT OR A QUESTION</span>'
        '<h2>Search the whole course</h2><label for="query">Topic, failure, framework, or use case</label>'
        '<input type="search" id="query" placeholder="Try token budget, replay, OCR, or approval">'
        f'<div class="search-options"><label>Chapter<select id="chapter-filter"><option value="">All chapters</option>{options}</select></label>'
        '<label>Study status<select id="status-filter"><option value="all">All topics</option><option value="unlearned">Not learned yet</option>'
        '<option value="learned">Started</option><option value="familiar">Familiar</option><option value="practiced">Practiced</option>'
        '<option value="independent">Independent</option><option value="mastered">Estimated Mastered</option>'
        '<option value="bookmarked">Bookmarked</option><option value="review">Due for review</option></select></label></div>'
        '<p id="search-count" role="status"></p><div id="results"></div>'
        '<button id="more-results" type="button" hidden>Show more results</button>'
        '<button id="random" type="button">Practice a random topic</button></section>'
        '<section class="record-panel"><h2>Keep your explanations</h2>'
        '<p>Notes, bookmarks, practice attempts, and review schedules stay in this browser profile using IndexedDB, with a localStorage fallback. '
        'No account, server sync, or personal-data transmission is used. Practice attempts update your review schedule. '
        'Practiced and Independent require passing checks; estimated Mastered requires distinct independent checks at least a day apart. '
        'This is study evidence, not certification. Your earlier question history remains available after the chapter reorder. Export a backup before switching devices.</p>'
        '<p><progress id="progress" value="0"></progress> <span id="progress-label">0 topics understood</span> · '
        '<span id="review-label">Nothing due for review</span></p>'
        '<button id="export" type="button">Export progress</button><button id="reset-progress" type="button">Clear study record</button>'
        '<label class="import-label">Import progress<input id="import" type="file" accept="application/json,.json"></label>'
        '<p id="storage-status" role="status"></p></section>'
        f'<section class="prose"><h2>Choose a track</h2><ul>{track_list}</ul></section>'
    )
    write_html('index.html', 'Learn AI engineering through explained examples', home)

    lab_entries = [
        f'<section class="lab-entry" id="lab-{c["slug"]}"><a href="{url(c["slug"] + ".html")}">Chapter {i}: {E(c["title"])} →</a>'
        f'{chapter_lab(c, "lab-body-" + c["slug"])}</section>'
        for i, c in enumerate(chapters, 1)
    ]
    write_html(
        'roadmap.html',
        'Practical experiments',
        '<p class="eyebrow">BUILD / BREAK / EXPLAIN</p><h1>Practice the actual boundaries.</h1>'
        '<p class="subtitle">Each experiment uses the chapter case. Bring back working behavior, a failure demonstration, '
        f'and evidence supporting your design choice.</p>{"".join(lab_entries)}',
    )

    integration_links = ''.join(
        f'<li><a href="{url("examples/labs/" + p)}">{p}</a></li>'
        for p in ('README.md', 'streaming_app.py', 'voice_pipeline.py', 'ocr_extract.py')
    )
    examples_cards = ''.join(
        '<div id="' + c['slug'] + '">'
        + chapter_code_panel(c, code_notes, chapter_examples).replace('id="chapter-example"', f'id="code-{c["slug"]}"')
        + '</div>'
        for c in chapters
    )
    write_html(
        'examples.html',
        'Code studio',
        '<p class="eyebrow">READ SMALL IMPLEMENTATIONS / THEN CONNECT THE LAYERS</p><h1>Code with an explanation.</h1>'
        '<p class="subtitle">Examples use synthetic data. Python scope labels distinguish executable standard-library examples '
        'from optional framework sketches. SQL fragments need a disposable schema.</p>'
        '<section class="code-studio" id="integration-labs"><h2>Connect HTTP, SSE, WebSocket, voice, and OCR</h2>'
        '<p>The optional backend demonstrates task acceptance, status, replay, and cancellation. Its state is process-local, not production durability.</p>'
        f'<ul>{integration_links}</ul></section>{examples_cards}',
    )

    terms_map = dict(read_json(CONTENT / 'shared/glossary.json'))
    terms_map.update(ACRONYMS)
    for c in chapters:
        for name, meaning in c['terms']:
            terms_map.setdefault(name, meaning)
    glossary_grid = ''.join(
        f'<article id="{term_id(name)}" data-term="{E((name + " " + meaning).lower())}"><h2>{E(name)}</h2><p>{E(meaning)}</p></article>'
        for name, meaning in sorted(terms_map.items())
    )
    write_html(
        'glossary.html',
        'Terminology without assumed knowledge',
        '<p class="eyebrow">PLAIN DEFINITIONS BEFORE TECHNICAL DETAIL</p><h1>Make the words useful.</h1>'
        f'<label for="term-search">Find a term</label><input type="search" id="term-search"><div class="glossary-grid">{glossary_grid}</div>',
    )

    references = read_json(CONTENT / 'shared/references.json')
    ref_links = ''.join(f'<a href="{E(href)}"><strong>{E(name)}</strong><span>Official reference ↗</span></a>' for name, href in references.values())
    write_html(
        'libraries.html',
        'Frameworks and references',
        '<p class="eyebrow">CHOOSE BY RESPONSIBILITY</p><h1>Read the contract,<br>then choose the tool.</h1>'
        '<p class="subtitle">Runtime, protocol, database, and evaluation libraries solve different problems. They are not a mandatory stack. '
        f'Follow compatible version documentation and use measured task needs to justify additions.</p><section class="reference-list" id="official-docs">{ref_links}</section>',
    )

    diagram_cards = ''.join(
        f'<a class="map-card" href="{url("diagrams/" + slug + ".html")}"><h2>{title}</h2><span>Open the larger interactive map →</span></a>'
        for slug, title in [
            ('context', 'Context and evidence'),
            ('harness', 'Agent harness and business authority'),
            ('streaming', 'Streaming and voice delivery'),
            ('quality', 'Documents and evaluation'),
        ]
    )
    write_html(
        'diagrams.html',
        'Interactive system maps',
        '<p class="eyebrow">TWO LEVELS OF EXPLORATION</p><h1>Follow the information.</h1>'
        '<p class="subtitle">Every teaching chapter contains its own step-through diagram and failure simulation. '
        f'These larger maps connect the responsibilities across chapters.</p>{diagram_cards}',
    )

    atlas_cards = ''.join(
        f'<section class="map-card"><h2>{title}</h2><p>{summary}</p><ul>'
        + ''.join(f'<li><a href="{url(slug + ".html")}">{E(by_slug[slug]["title"])}</a></li>' for slug in slugs)
        + '</ul></section>'
        for title, _level, summary, slugs in STAGES
    )
    write_html(
        'atlas.html',
        'Course responsibility map',
        f'<p class="eyebrow">THE REORDERED LEARNING PATH</p><h1>Find the responsibility.</h1>{atlas_cards}',
    )

    write_html(
        'provenance.html',
        'How to use this course',
        '<p class="eyebrow">A COURSE BUILT AROUND UNDERSTANDING</p><h1>Read, trace, build, explain.</h1>'
        '<section class="prose"><h2>What changed</h2><p>Chapters now follow explicit dependencies from programming and web foundations to advanced systems. '
        'Each has a specific use case, plain definitions, its own interactive flow, explained lessons, code, and a practical experiment. '
        'Topic coverage determines chapter depth; no fixed number of questions is required.</p>'
        '<h2>Two reading depths</h2><p>Start with the guided explanations and concrete cases. Use the additional interview questions for technical depth, '
        'trade-offs, and failure boundaries. Existing question identifiers are preserved even though their chapters moved. '
        'New guided lessons have independent stable identifiers.</p>'
        '<h2>Scope and evidence</h2><p>The platform and data are fictional. This website does not expose private project code or call model providers. '
        'Standard-library examples use synthetic fixtures. Optional agent SDK examples are syntax-checked sketches; the OCR engine and SQL fragments are not executed. '
        'The synthetic FastAPI lab has authentication, ownership, SSE replay, cancellation, and WebSocket checks, but uses process-local state.</p>'
        '<h2>Your study record</h2><p>Notes and learned flags are personal study tools, not certification. They stay in your browser and can be exported. '
        'No print control is included; core content remains readable without JavaScript. Interactive examples are deterministic teaching simulations, not live model output.</p></section>',
    )

    write_html(
        'coverage-audit.html',
        'Coverage and learning structure',
        '<h1>Coverage follows the subject.</h1><p>Use the responsibility map to find the complete ordered course. '
        'Each chapter now has its own guided lessons, concrete case, diagram, implementation, and deeper questions.</p>'
        f'<p><a href="{url("editorial-report.html")}">Editorial evidence and pending review</a></p>'
        f'<a href="{url("atlas.html")}">Open the responsibility map →</a>{coverage_review(chapters)}',
    )

    for old, new in [('insurance-system', 'application-architecture'), ('insurance-decisions', 'evidence-applicability')]:
        write_html(
            f'{old}.html',
            'Chapter moved',
            f'<h1>Continue to the updated chapter.</h1><a href="{url(new + ".html")}">Open chapter →</a>'
            f'<script>location.replace("{url(new + ".html")}"+location.search+location.hash)</script>',
        )

    write_html('design-system.html', 'Design System Showcase', design_system_showcase())

    practice_counts = build_practice_pages(out, write_html, chapters, url)
    unit_controls = lambda q: controls(q, practice_by_topic=practice_by_topic)
    course_counts = build_courses(out, write_html, url, unit_controls)
    build_audit_pages(out, write_html, chapters, curriculum, url)
    build_blueprint(out, write_html, chapters, curriculum, url)

    domain_counts = {
        d: sum(1 for c in chapters for q in c.get('questions', []) if q.get('domain') == d)
        for d in {q.get('domain', '') for c in chapters for q in c.get('questions', []) if q.get('domain')}
    }
    manifest = {
        'edition': 'interview-led-v6',
        'title': 'AI Full-Stack Engineering Roadmap',
        'questions': total,
        'study_topics': study_total,
        'max_study_id': max_id,
        'chapters': len(chapters),
        'chapters_with_review_notes': len(chapters),
        'added_guided_lessons': sum(q.get('added', False) for c in chapters for q in c['lessons']),
        'guided_lessons': sum(len(c['lessons']) for c in chapters),
        'chapter_topics': {c['slug']: len(c['questions']) + len(c['lessons']) for c in chapters},
        'chapter_order': [c['slug'] for c in chapters],
        'stages': len(STAGES),
        'suggested_experiments': len(chapters),
        'downloadable_labs': sum(len(list(LABS.glob(p))) for p in ('*.py', '*.js', '*.html')),
        'examples': len(chapter_examples),
        'questions_with_code': len(question_code_map),
        'distinct_question_examples': len(question_recipes),
        'chapter_specific_diagrams': len(chapters),
        'overview_diagrams': 4,
        'source_snapshots': 0,
        'answer_diagrams': len(VISUALS),
        'chapter_answer_limit': None,
        'conceptual_worked_questions': sum(q.get('answer_format') == 'conceptual' for c in chapters for q in c['questions']),
        'acronym_definitions': len(ACRONYMS),
        'configured_base_path': configured_base_path(),
        'question_data_shards': question_shards,
        **practice_counts,
        **course_counts,
        'coverage_matrix': domain_counts,
    }
    write_json(out / 'manifest.json', manifest)
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('chapter_order', 'chapter_topics')}, indent=2))
    return manifest


def package_site(source: Path = BUILD_OUT, out: Path = SITE_OUT) -> None:
    """Copy clean public artifacts from _build into _site and render track landing pages."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for pattern in ('*.html', '*.css', '*.js', '*.svg'):
        for path in source.glob(pattern):
            shutil.copy2(path, out / path.name)
    for name in ('.nojekyll', 'LICENSE'):
        if (source / name).exists():
            shutil.copy2(source / name, out / name)
    if (source / 'manifest.json').exists():
        shutil.copy2(source / 'manifest.json', out / 'manifest.json')
    else:
        write_json(out / 'manifest.json', {'note': 'manifest not generated in this environment'})
    for name in ('diagrams', 'examples', 'runtime', 'search', 'questions'):
        if (source / name).exists():
            shutil.copytree(source / name, out / name)

    curriculum = read_json(CONTENT / 'curriculum.json')
    curr_chapters = curriculum['chapters']
    chapters = load_chapters()
    by_slug = {c['slug']: c for c in chapters}
    max_id = max(read_json(CONTENT / 'shared/study_ids.json').values())
    tracks_dir = out / 'tracks'
    tracks_dir.mkdir(exist_ok=True)
    track_head_asset = lambda name: f'../{name}'

    for track in curriculum['tracks']:
        items: list[str] = []
        for slug in track['chapters']:
            c = by_slug[slug]
            entry = curr_chapters[slug]
            mins = chapter_reading_minutes(c)
            has_rigorous = any(q.get('conceptual_narrative') for q in c.get('lessons', []))
            pre = ''.join(f'<a href="../{p}.html">{E(by_slug[p]["title"])}</a>' for p in entry['prerequisites'])
            badge = '<span class="track-badge complete">Enriched lesson present</span>' if has_rigorous else '<span class="track-badge pending">Standard</span>'
            items.append(
                f'<article class="track-chapter"><h2><a href="../{slug}.html">{E(c["title"])}</a></h2>{badge}'
                f'<p>{E(c["goal"])}</p>'
                f'<p><span class="track-meta">{mins} min read · {len(c["lessons"])} lessons · {len(c["questions"])} practice</span></p>'
                f'<p><strong>Prerequisites:</strong> {pre or "None — start here"}</p>'
                f'<p class="track-meta">Competency: {E(entry["competency"])}</p></article>'
            )

        head_html = render_head(track['title'], asset_fn=track_head_asset)
        track_page = (
            f'<!doctype html><html lang="en">{head_html}'
            f'<body data-question-count="{max_id}"><a class="skip" href="#main">Skip to content</a>'
            '<main id="main" tabindex="-1"><section class="track-page">'
            '<a href="../index.html">Learning journey</a> · <a href="../index.html#search">Search course</a>'
            f'<div class="track-header"><h1>{E(track["title"])}</h1>'
            f'<p class="track-level">{E(track["level"])} · {E(track["description"])}</p>'
            f'<p class="track-meta">Entry point: <a href="../{track["entry_point"]}.html">{E(by_slug[track["entry_point"]]["title"])}</a></p>'
            f'<p class="track-meta">Prerequisite-ordered track · {len(track["chapters"])} chapters</p></div>'
            f'<div class="track-chapters">{"".join(items)}</div></section></main>{_SEARCH_DIALOG_HTML}</body></html>'
        )
        (tracks_dir / f'{track["id"]}.html').write_text(track_page, encoding='utf-8')
    print('Static Pages artifact ready')
