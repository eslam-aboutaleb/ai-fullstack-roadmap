"""Static practice pages, question/search shards, deterministic simulations, and chapter navigation."""
from collections import Counter
import json
from pathlib import Path
import re

from roadmap.config import CONTENT, escape_html as E, read_json, write_json
from roadmap.courses import load_courses
from roadmap.prose import teaching_title

SHARD_SIZE = 40
SIMULATION_CHAPTERS = {
    'sources': 'asyncio',
    'database-concurrency': 'locking',
    'foundations': 'retrieval',
    'agent-evaluation': 'retries',
}


def build_question_shards(out: Path, chapters: list[dict]) -> int:
    """Write sharded question metadata JSON files and coverage report."""
    directory = out / 'questions'
    directory.mkdir(exist_ok=True)
    coverage: list[dict] = []
    seen: dict[str, int] = {}
    duplicates: list[list[int]] = []
    shards = 0

    for chapter in chapters:
        rows = chapter['questions']
        for row in rows:
            key = re.sub(r'\W+', ' ', row['Q'].casefold()).strip()
            if key in seen:
                duplicates.append([seen[key], row['id']])
            seen[key] = row['id']
        count = 0
        for index in range(0, len(rows), SHARD_SIZE):
            (directory / f'{chapter["slug"]}-{index // SHARD_SIZE + 1}.json').write_text(
                json.dumps(rows[index:index + SHARD_SIZE], ensure_ascii=False) + '\n',
                encoding='utf-8',
            )
            count += 1
        shards += count
        coverage.append({
            'chapter': chapter['slug'],
            'questions': len(rows),
            'shards': count,
            'facets': dict(Counter(q.get('difficulty', 'unclassified') for q in rows)),
            'enriched': sum('spoken' in q or q.get('answer_format') == 'conceptual' for q in rows),
        })

    report = {
        'shard_size': SHARD_SIZE,
        'total_questions': sum(len(c['questions']) for c in chapters),
        'subjects': coverage,
        'exact_duplicate_ids': duplicates,
    }
    write_json(directory / 'coverage.json', report)
    return shards


def build_search_shards(out: Path, entries: list[dict], curriculum: dict) -> None:
    """Partition lazy search index entries into track-grouped JSON shards."""
    directory = out / 'search'
    directory.mkdir(exist_ok=True)
    tracks = {slug: track['id'] for track in curriculum['tracks'] for slug in track['chapters']}
    shards: list[dict] = []

    for track in [*curriculum['tracks'], {'id': 'courses'}]:
        group = [entry for entry in entries if tracks.get(entry['slug'], entry.get('track')) == track['id']]
        for index in range(0, len(group), 60):
            subset = group[index:index + 60]
            name = f'{track["id"]}-{index // 60 + 1}.json'
            (directory / name).write_text(
                json.dumps(subset, ensure_ascii=False, separators=(',', ':')) + '\n',
                encoding='utf-8',
            )
            shards.append({
                'url': f'search/{name}',
                'track': track['id'],
                'chapters': sorted({r['slug'] for r in subset}),
                'count': len(subset),
            })

    if sum(shard['count'] for shard in shards) != len(entries):
        raise ValueError('Search entries contain an unmapped subject')
    (directory / 'manifest.json').write_text(
        json.dumps({'version': 1, 'count': len(entries), 'shards': shards}, separators=(',', ':')) + '\n',
        encoding='utf-8',
    )


def load_practice(chapters: list[dict]) -> tuple[list[dict], list[dict]]:
    """Load and validate assessments and browser coding labs against chapter topics."""
    topics = {q['id']: c['slug'] for c in chapters for q in c['lessons'] + c['questions']}
    topics.update({unit['study_id']: f'course-{unit["id"]}' for course in load_courses() for unit in course['units']})
    assessments = read_json(CONTENT / 'assessments.json')['items']
    labs = read_json(CONTENT / 'browser-labs.json')['labs']
    seen: set[str] = set()

    for item in assessments + labs:
        if item['id'] in seen or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item['id']):
            raise ValueError('Duplicate or invalid practice ID: ' + item['id'])
        seen.add(item['id'])
        if topics.get(item['topic']) != item['chapter']:
            raise ValueError('Practice topic does not belong to chapter: ' + item['id'])
        for field in ('title', 'objective', 'references', 'hints'):
            if not item.get(field):
                raise ValueError(f'Missing {field}: {item["id"]}')
        if 'cases' in item:
            if item['language'] not in ('javascript', 'python') or not item.get('starter') or not item.get('solution') or not item['cases']:
                raise ValueError('Incomplete coding lab: ' + item['id'])
            if any(not {'name', 'input', 'expected'} <= set(case) for case in item['cases']):
                raise ValueError('Incomplete lab test: ' + item['id'])
        elif item['kind'] == 'self-review':
            if not item.get('rubric') or not item.get('model_answer'):
                raise ValueError('Missing design rubric')
        elif item['kind'] in ('quiz', 'debugging'):
            ids = [option['id'] for option in item['options']]
            if len(ids) != len(set(ids)) or len(ids) < 2 or item['correct'] not in ids or any(not o.get('feedback') for o in item['options']):
                raise ValueError('Invalid answer choices: ' + item['id'])
        else:
            raise ValueError('Unknown assessment kind')

    return assessments, labs


def write_js_config(out: Path, name: str, variable: str, data: object) -> None:
    """Serialize static browser configuration data safely into an inline JS assignment."""
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    (out / name).write_text(f'window.{variable}={encoded};\n', encoding='utf-8')


def build_practice_pages(out: Path, write, chapters: list[dict], url) -> dict[str, int]:
    """Generate assessments, browser coding labs, and study record pages."""
    assessments, labs = load_practice(chapters)
    write_js_config(out, 'practice-data.js', 'GUIDE_PRACTICE', {'assessments': assessments, 'labs': labs})
    catalogue = [
        {'id': q['id'], 'title': q['Q'], 'chapter': c['title'], 'url': f'{c["slug"]}.html#q{q["id"]}'}
        for c in chapters
        for q in c['lessons'] + c['questions']
    ]
    catalogue += [
        {'id': unit['study_id'], 'title': unit['title'], 'chapter': course['title'], 'url': f'course-{unit["id"]}.html#q{unit["study_id"]}'}
        for course in load_courses()
        for unit in course['units']
    ]
    write_js_config(out, 'study-catalogue.js', 'GUIDE_TOPICS', catalogue)
    scripts = f'<script src="{url("practice-data.js")}" defer></script><script src="{url("practice.js")}" defer></script>'

    assessment_cards: list[str] = []
    for item in assessments:
        identity = item['id']
        if item['kind'] != 'self-review':
            options_html = '<fieldset><legend>Choose the best answer</legend>' + ''.join(
                f'<label class="assessment-option"><input type="radio" name="answer-{identity}" value="{E(o["id"])}"> {E(o["text"])}</label>'
                for o in item['options']
            ) + '</fieldset>'
            action = '<button type="button" data-grade disabled>Check my answer</button>'
            solution = E(item['explanation'])
        else:
            rubric_html = ''.join(f'<li>{E(point)}</li>' for point in item['rubric'])
            options_html = (
                f'<label for="design-{identity}">Write your design and trade-offs</label>'
                f'<textarea id="design-{identity}" data-design rows="6"></textarea>'
                f'<h3>Self-review rubric</h3><ul>{rubric_html}</ul>'
            )
            action = '<button type="button" data-grade disabled>Record my self-review</button>'
            solution = E(item['model_answer'])
        hints = ''.join(f'<li>{E(hint)}</li>' for hint in item['hints'])
        assessment_cards.append(
            f'<article class="practice-card" id="a-{identity}" data-assessment="{identity}" data-topic="{item["topic"]}">'
            f'<p class="eyebrow">{E(item["kind"])} · {E(item["difficulty"])}</p><h2>{E(item["title"])}</h2>'
            f'<p>{E(item["scenario"])}</p><p><small>Learning outcome: {E(item["objective"])}</small></p>'
            f'{options_html}<details data-hint><summary>Show a hint</summary><ul>{hints}</ul></details>'
            f'{action}<p role="status" data-feedback></p>'
            f'<details data-solution><summary>Explanation and answer key</summary><p>{solution}</p></details>'
            f'<p><a href="{url(item["chapter"] + ".html")}#q{item["topic"]}">Review the lesson</a> · '
            f'<a href="{E(item["references"][0])}">Primary reference</a></p></article>'
        )

    write(
        'assessments.html',
        'Practice with evidence',
        '<p class="eyebrow">RECALL · DEBUG · DEFEND</p><h1>Test the decision, not your confidence.</h1>'
        '<p>Quizzes and debugging checks are graded against explicit fixtures. Design responses use a self-review rubric '
        'and are never automatically marked correct. Your attempts stay in this browser. Progress estimates come from recorded practice attempts.</p>'
        '<noscript><p>Enable JavaScript to grade and save attempts. Every scenario, rubric and answer key below is readable without it.</p></noscript>'
        '<div class="practice-tools"><label for="practice-order">Order</label>'
        '<select id="practice-order"><option value="recommended">Recommended: failed and due first</option>'
        '<option value="seeded">Seeded shuffle</option></select>'
        '<label for="practice-seed">Shuffle seed</label><input id="practice-seed" type="number" min="1" max="4294967295" value="42">'
        '<button type="button" id="order-practice">Apply order</button></div>'
        f'<div id="assessment-cards">{"".join(assessment_cards)}</div>{scripts}',
    )

    lab_cards: list[str] = []
    lab_download_dir = out / 'examples/browser-labs'
    lab_download_dir.mkdir(parents=True, exist_ok=True)
    for item in labs:
        identity = item['id']
        language = item['language']
        ext = '.py' if language == 'python' else '.js'
        hints = ''.join(f'<li>{E(hint)}</li>' for hint in item['hints'])
        fixtures = ''.join(
            f'<tr><th scope="row">{E(case["name"])}</th><td><code>{E(json.dumps(case["input"]))}</code></td>'
            f'<td><code>{E(json.dumps(case["expected"]))}</code></td></tr>'
            for case in item['cases']
        )
        runtime_note = (
            'Python loads the optional self-hosted runtime (about 12 MB) on demand; allow up to 30 seconds on a slow device.'
            if language == 'python'
            else 'JavaScript executes in a disposable Worker, never in the page.'
        )
        lab_cards.append(
            f'<article class="practice-card coding-lab" id="lab-{identity}" data-lab="{identity}">'
            f'<p class="eyebrow">{E(language)} · LOCAL BROWSER EXECUTION</p><h2>{E(item["title"])}</h2>'
            f'<p>{E(item["instructions"])}</p><label for="editor-{identity}">Your {E(language)} source</label>'
            f'<textarea class="lab-editor" id="editor-{identity}" spellcheck="false" autocapitalize="off" autocomplete="off" rows="10">{E(item["starter"])}</textarea>'
            '<div class="lab-actions"><button type="button" data-run disabled>Run tests</button>'
            '<button type="button" data-stop disabled>Stop</button><button type="button" data-reset>Reset starter</button></div>'
            f'<p role="status" data-lab-status>Tests run only when you press Run. {runtime_note}</p>'
            '<pre class="lab-output" tabindex="0" role="region" aria-label="Test results and program output"><code data-lab-output></code></pre>'
            f'<details data-hint><summary>Hints</summary><ul>{hints}</ul></details>'
            f'<details data-solution><summary>Reference solution</summary><pre><code>{E(item["solution"])}</code></pre></details>'
            f'<details><summary>Test fixtures and expected results</summary><div class="table-scroll"><table><caption>{E(item["title"])} fixtures</caption>'
            f'<thead><tr><th>Case</th><th>Input</th><th>Expected</th></tr></thead><tbody>{fixtures}</tbody></table></div></details>'
            f'<p><a href="{url("examples/browser-labs/" + identity + ext)}">Download the reference source</a> · '
            f'<a href="{url(item["chapter"] + ".html")}#q{item["topic"]}">Review the lesson</a></p></article>'
        )
        (lab_download_dir / (identity + ext)).write_text(item['solution'] + '\n', encoding='utf-8')

    write(
        'coding-labs.html',
        'Browser coding labs',
        '<p class="eyebrow">IMPLEMENT · RUN · EXPLAIN</p><h1>Small programs. Observable results.</h1>'
        '<p>Practice JavaScript and Python locally in this browser. A fresh Worker is terminated after the time limit or when you press Stop. '
        'Output is capped at 12,000 characters and source at 64,000 characters. A passing test is fixture evidence, not proof of general correctness.</p>'
        '<aside class="failure-note"><strong>Execution limits:</strong> Workers keep the page responsive but are not a hardened security boundary. '
        'Run code you understand. Browsers impose their own memory limits; a large allocation can still exhaust memory. No server, credentials, '
        'package installation or external API is used. Python allows math, json, statistics, collections, itertools and functools imports. '
        'Real databases, network services, Docker and FastAPI run in downloadable local labs.</aside>'
        '<noscript><p>JavaScript is required to run tests. Starters, solutions, fixtures and downloadable files remain readable below.</p></noscript>'
        '<p>Python is optional and loaded from this site\'s runtime folder. If a downloaded copy omits it, use the local source downloads; '
        'core reading and JavaScript labs still work. <a href="runtime/NOTICE.txt">Runtime notices</a>.</p>'
        + ''.join(lab_cards)
        + scripts,
    )

    write(
        'study.html',
        'Your study evidence',
        '<p class="eyebrow">BROWSER-LOCAL STUDY RECORD</p><h1>Evidence guides your next review.</h1>'
        '<p>No account, analytics, server sync or background reminders. IndexedDB stores a versioned event journal; localStorage is the fallback. '
        'Export before clearing browser data or switching devices. Private browsing may discard this record.</p>'
        '<div class="practice-card"><h2>How the estimate works</h2><dl>'
        '<dt><strong>Familiar</strong></dt><dd>A topic with recorded study activity.</dd>'
        '<dt><strong>Practiced</strong></dt><dd>At least one passed deterministic check.</dd>'
        '<dt><strong>Independent</strong></dt><dd>A recorded independent debugging or coding pass without hints, with a passing latest graded result.</dd>'
        '<dt><strong>Mastered</strong></dt><dd>Two distinct independent checks passed at least 24 hours apart, and the latest graded result passed.</dd></dl>'
        '<p>These are local estimates. An answer key or hints used in a session prevents that attempt from counting as independent. '
        'Subjective self-review never grants a graded pass. Failed checks schedule a review in one day; successful reviews use 1, 3, then doubled intervals capped at 90 days.</p></div>'
        '<section class="practice-card"><h2>Your record</h2><p id="study-summary" role="status">Loading local evidence…</p>'
        '<div id="study-due"></div><div id="study-history"></div>'
        '<button id="export" type="button">Export progress</button>'
        '<label class="import-label">Import progress<input id="import" type="file" accept="application/json,.json"></label>'
        '<button id="reset-progress" type="button">Clear study record</button><p id="storage-status" role="status"></p></section>'
        '<noscript><p>Your record is private browser data; JavaScript is required to access it. Continue reading chapters using the course menu.</p></noscript>'
        + scripts
        + f'<script src="{url("study-catalogue.js")}" defer></script>',
    )
    return {'assessments': len(assessments), 'browser_labs': len(labs)}


def simulation_panel(identity: str, url) -> str:
    """Render interactive deterministic state simulation block with static transcript fallback."""
    fixtures = read_json(CONTENT / 'simulations.json')
    fixture = next(item for item in fixtures if item['id'] == identity)
    normal_steps = fixture['normal']['steps']
    failure_steps = fixture['failure']['steps']
    normal_transcript = ''.join(f'<li><strong>{E(s["label"])}</strong>: {E(s["detail"])}</li>' for s in normal_steps)
    failure_transcript = ''.join(f'<li><strong>{E(s["label"])}</strong>: {E(s["detail"])}</li>' for s in failure_steps)
    first = normal_steps[0]
    return (
        f'<section class="practice-card simulation" data-simulation="{identity}">'
        '<p class="eyebrow">DETERMINISTIC STATE SIMULATION</p>'
        f'<h2>Step through {E(identity)}</h2>'
        '<p>A teaching model with explicit state transitions, not a running backend.</p>'
        '<label>Scenario <select data-sim-scenario><option value="normal">Normal path</option>'
        '<option value="failure">Failure or recovery path</option></select></label>'
        f'<label>Step <input type="range" data-sim-step min="0" max="{len(normal_steps) - 1}" value="0"></label>'
        '<div class="lab-actions"><button type="button" data-sim-prev>Previous</button>'
        '<button type="button" data-sim-next>Next</button><button type="button" data-sim-reset>Reset</button></div>'
        '<svg viewBox="0 0 600 80" role="img" aria-label="Current simulation transition">'
        '<rect x="5" y="5" width="590" height="70" rx="12" fill="var(--panel2)" stroke="var(--line)"/>'
        f'<text x="24" y="45" fill="var(--text)" data-sim-svg>{E(first["label"])}</text></svg>'
        f'<div aria-live="polite"><h3 data-sim-label>{E(first["label"])}</h3><p data-sim-detail>{E(first["detail"])}</p></div>'
        f'<pre><code data-sim-state>{E(json.dumps(first["state"], indent=2))}</code></pre>'
        f'<details><summary>Complete text transcript</summary><ol>{normal_transcript}</ol>'
        f'<h3>Failure and recovery variant</h3><ol>{failure_transcript}</ol></details></section>'
        f'<script src="{url("simulation-model.js")}" defer></script><script src="{url("simulation.js")}" defer></script>'
    )


def question_finder(chapter: dict, url) -> str:
    """Render in-chapter collapsible question directory and filter controls."""
    rows: list[str] = []
    for group, label in (('lessons', 'Foundation'), ('questions', 'Deeper')):
        for question in chapter[group]:
            advanced = question.get('difficulty') == 'advanced design scenario'
            kind = 'Advanced scenario' if advanced else label
            title = teaching_title(question)
            rows.append(
                f'<li data-finder-kind="{kind}" data-finder-text="{E(title.lower())}">'
                f'<a href="#q{question["id"]}">{E(title)}</a><small>{kind}</small></li>'
            )
    return (
        '<details class="question-finder" id="question-finder">'
        f'<summary>Find a question in this chapter · {len(rows)} questions</summary>'
        '<p>Start with foundations, then explain a design under constraints. Select a question to jump to its answer.</p>'
        '<div class="finder-controls" hidden>'
        '<label for="chapter-question-query">Search question titles'
        '<input id="chapter-question-query" type="search" placeholder="Try context, retry or metadata"></label>'
        '<label for="chapter-question-kind">Question type<select id="chapter-question-kind">'
        '<option value="">All questions</option><option>Foundation</option><option>Deeper</option><option>Advanced scenario</option>'
        '</select></label><button type="button" id="chapter-question-reset">Clear filters</button></div>'
        f'<p id="chapter-question-count" role="status">{len(rows)} questions</p>'
        '<p id="chapter-question-empty" hidden>No matching questions. Try fewer words or clear the filters.</p>'
        f'<ul class="finder-results">{"".join(rows)}</ul>'
        f'<p><a href="{url("design-scenarios.html")}">Practice advanced system-design scenarios across chapters →</a></p></details>'
    )


def scenario_page(chapters: list[dict], url) -> str:
    """Render cross-chapter index of advanced system-design interview scenarios."""
    sections: list[str] = []
    for chapter in chapters:
        questions = [q for q in chapter['questions'] if q.get('difficulty') == 'advanced design scenario']
        if questions:
            links = ''.join(f'<li><a href="{url(chapter["slug"] + ".html")}#q{q["id"]}">{E(q["Q"])}</a></li>' for q in questions)
            sections.append(f'<section class="map-card"><h2>{E(chapter["title"])}</h2><ul>{links}</ul></section>')
    return (
        '<p class="eyebrow">ADVANCED INTERVIEW PRACTICE</p><h1>Design under real constraints.</h1>'
        '<p class="subtitle">Work through context limits, large-file ingestion, permission-aware retrieval, bounded agents, '
        'atomic publication, job recovery, streaming durability, evaluation validity, entity identity, privacy and data contracts. '
        'Each scenario links to a detailed answer, a design diagram and a failure exercise in its chapter.</p>'
        '<section class="prose"><h2>How to practice a design answer</h2><ol>'
        '<li>State the input, scale, latency target and authorization boundary.</li>'
        '<li>Draw the data path and calculate the tightest resource budget.</li>'
        '<li>Trace a crash, retry, cancellation and stale result.</li>'
        '<li>Explain the simplest design that meets the requirement and what evidence would justify more complexity.</li>'
        '<li>Open the answer, compare assumptions, then implement the proposed failure exercise.</li></ol>'
        '<p>These are worked engineering designs, not measured production benchmarks. Follow chapter prerequisites if a mechanism is unfamiliar.</p>'
        '<h2>Which execution model fits?</h2><ul>'
        '<li><strong>Known sequence:</strong> use a durable workflow for upload, parsing, embedding and publication.</li>'
        '<li><strong>Adaptive investigation:</strong> consider one bounded agent for repository diagnosis or iterative evidence gathering.</li>'
        '<li><strong>Independent investigations:</strong> compare ordinary parallel calls with specialist agents, including synthesis cost.</li>'
        '<li><strong>Irreversible business effects:</strong> keep authorization and commitment in deterministic services, even if an agent proposes the action.</li>'
        '</ul></section>' + ''.join(sections)
    )
