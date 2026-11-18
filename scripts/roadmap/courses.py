"""Structured engineering courses, local cumulative projects, capstones, and ZIP bundles."""
import ast
from pathlib import Path
from urllib.parse import urlsplit
import zipfile

from roadmap.config import CONTENT, LABS, ROOT, escape_html as E, read_json, write_json
from roadmap.content import check_schema
from roadmap.prose import prose as answer_prose, render_reference_list

_LAB_EXTENSIONS = frozenset({'.py', '.html', '.js', '.cjs', '.md', '.json', '.txt', '.sql', '.csv'})
_PROJECT_FILES_ALLOWED = frozenset({'.py', '.ts', '.tsx', '.css', '.json', '.html', '.md', '.yaml'})
_CAPSTONES = (
    (
        'async-engine',
        'Bounded async job engine',
        'async_job_engine.py',
        [
            'Bound admitted work and worker concurrency',
            'Distinguish job failure, timeout and caller cancellation',
            'Release every queue item and clean up child tasks',
        ],
        ['Cancellation after handler starts', 'A handler that never finishes', 'Producer admission under full capacity'],
        'In-memory queues do not survive process restart. Sensitive input must not leak through errors. Bound work before admitting untrusted jobs.',
        'async def run_jobs(jobs, handler, workers=2, capacity=2, deadline=0.1):\n'
        '    raise NotImplementedError("Implement bounded workers and cleanup")\n',
    ),
    (
        'transaction-api',
        'Authorized PostgreSQL task API',
        'transaction_api.py',
        [
            'Validate requests and authenticate synthetic owners',
            'Resolve concurrent matching keys to one task',
            'Reject changed content and other-owner access',
            'Atomically confirm state and outbox intent',
        ],
        ['Concurrent acceptance and confirmation barriers', 'Crash between writes and commit', 'A known resource ID requested by another owner'],
        'Tokens are synthetic local fixtures, not a JWT/login service. Store secrets in the local environment. Object authorization must hold at the query and mutation boundary.',
        'def accept_task(owner, operation_key, message):\n'
        '    raise NotImplementedError("Persist one authorized task identity")\n\n'
        'def confirm_task(task_id, owner):\n'
        '    raise NotImplementedError("Guard state and outbox in one transaction")\n',
    ),
    (
        'rag-quality',
        'Retrieval evaluation and regression gate',
        'rag_evaluation.py',
        [
            'Separate tenant-scoped retrieval from answer generation',
            'Compute quality against independent relevance labels',
            'Detect a deliberately dropped policy and correct abstention',
        ],
        ['Remove the sale policy from the candidate set', 'Query another owner’s private exception', 'Request evidence absent from the index'],
        'Fixture documents are synthetic. Apply ownership filters before exposing candidates. A relevance score is not a policy authorization decision.',
        'def retrieve(query, owner, documents):\n'
        '    raise NotImplementedError("Scope candidates before ranking")\n\n'
        'def evaluate(cases):\n'
        '    raise NotImplementedError("Measure relevance and abstention independently")\n',
    ),
    (
        'durable-agent',
        'Recoverable agent effects',
        'durable_agent.py',
        [
            'Record approval before effect dispatch',
            'Reuse a stable operation identity after a lost acknowledgment',
            'Reject owner and payload conflicts',
            'Inspect durable provider effects separately from calls',
        ],
        ['Crash after provider commit and before local acknowledgment', 'Retry the same operation twice', 'Try an unapproved or cross-owner operation'],
        'The local provider is a fixture, not an external connector. The real receiver must deduplicate or reconcile using the same effect key. A local rollback cannot undo its commit.',
        'def execute(path, key, owner, payload, approved):\n'
        '    raise NotImplementedError("Persist approval and reconcile a stable effect key")\n',
    ),
)


def load_projects() -> list[dict]:
    """Load and validate cumulative local engineering projects."""
    rows = read_json(CONTENT / 'projects.json')
    references = read_json(CONTENT / 'shared/references.json')
    seen: set[str] = set()
    import re

    for row in rows:
        identity = row['id']
        if not re.fullmatch(r'[a-z][a-z0-9-]+', identity) or identity in seen:
            raise ValueError('Invalid or duplicate local project identity')
        seen.add(identity)
        if not (ROOT / 'projects' / identity / 'README.md').is_file():
            raise ValueError('Project README missing')
        if not row['title'] or not row['description'] or not row['sections']:
            raise ValueError('Project teaching metadata missing')
        if any(not section['title'] or not section['text'] for section in row['sections']):
            raise ValueError('Incomplete project section')
        if any(key not in references for key in row['references']):
            raise ValueError('Unknown project reference')
    return rows


def iter_project_files(identity: str):
    """Yield sanitized (source_path, archive_member_path) pairs for a project."""
    directory = ROOT / 'projects' / identity
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory)
        if any(part in {'node_modules', 'dist', '__pycache__', '.git'} for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink() and (
            path.suffix in _PROJECT_FILES_ALLOWED or path.name in {'Dockerfile', '.dockerignore'}
        ):
            yield path, f'projects/{identity}/{relative.as_posix()}'


def build_projects(out: Path, write, url) -> int:
    """Build project detail pages, ZIP archives, and the index page."""
    references = read_json(CONTENT / 'shared/references.json')
    destination = out / 'examples/projects'
    destination.mkdir(parents=True, exist_ok=True)
    cards: list[str] = []

    for row in load_projects():
        identity = row['id']
        with zipfile.ZipFile(destination / f'{identity}.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for source, target in iter_project_files(identity):
                archive.write(source, target)
            archive.write(ROOT / 'LICENSE', 'LICENSE')
            if identity == 'evidence-workbench':
                archive.write(ROOT / 'requirements-dev.txt', 'requirements-dev.txt')

        body = (
            f'<p class="eyebrow">OPTIONAL LOCAL PROJECT</p><h1>{E(row["title"])}</h1>'
            f'<p>{E(row["description"])}</p>'
            f'<p><a href="{url(f"examples/projects/{identity}.zip")}">Download complete project source</a>. '
            'Extract the ZIP and read the included README for commands, milestones and review criteria. '
            'It runs locally; no application backend runs on GitHub Pages.</p>'
        )
        for section in row['sections']:
            body += f'<section class="prose"><h2>{E(section["title"])}</h2><p>{E(section["text"])}</p></section>'
        refs_html = ''.join(f'<li><a href="{E(references[k][1])}">{E(references[k][0])}</a></li>' for k in row['references'])
        body += f'<h2>Primary context</h2><ul>{refs_html}</ul>'
        write(f'project-{identity}.html', row['title'], body)
        cards.append(
            f'<article class="map-card"><h2><a href="{url(f"project-{identity}.html")}">{E(row["title"])}</a></h2>'
            f'<p>{E(row["description"])}</p></article>'
        )

    write(
        'engineering-projects.html',
        'Cumulative engineering projects',
        '<h1>Build, break and defend the system.</h1>'
        '<p>Use these projects alongside the engineering practicum. Save observed behavior and complete the independent milestones before requesting review.</p>'
        + ''.join(cards),
    )
    return len(cards)


def load_courses() -> list[dict]:
    """Load, schema-validate, and prerequisite-check all course files."""
    courses: list[dict] = []
    seen: set[str] = set()
    projects = {row['id'] for row in load_projects()}
    references = read_json(CONTENT / 'shared/references.json')
    course_schema = read_json(CONTENT / 'shared/course-schema.json')

    for path in sorted((CONTENT / 'courses').glob('*.json')):
        course = read_json(path)
        check_schema(course, course_schema, 'course', path.stem)
        for unit in course['units']:
            if unit['id'] in seen:
                raise ValueError('Duplicate learning outcome unit: ' + unit['id'])
            seen.add(unit['id'])
            for field in ('title', 'outcomes', 'terms', 'narrative', 'lab', 'practice', 'debugging', 'tradeoffs', 'references'):
                if not unit.get(field):
                    raise ValueError(f'Missing course field {field}: {unit["id"]}')
            for context in unit.get('source_context', []):
                if context['reference_id'] not in references or references[context['reference_id']][1] not in unit['references']:
                    raise ValueError('Unlinked source context')
            if unit.get('project') and unit['project'] not in projects:
                raise ValueError('Unknown local project')
            lab = LABS / unit['lab']
            if lab.parent != LABS or not lab.is_file() or lab.is_symlink():
                raise ValueError('Invalid course lab')
            for ref in unit['references']:
                parsed = urlsplit(ref)
                if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                    raise ValueError('Invalid primary course reference')
            if lab.suffix == '.py':
                ast.parse(lab.read_text(encoding='utf-8'))
            elif lab.suffix == '.html':
                if '<!doctype html>' not in lab.read_text(encoding='utf-8').lower():
                    raise ValueError('HTML exercise needs a complete document')
            else:
                raise ValueError('Unsupported course exercise format')
        courses.append(course)

    order = read_json(CONTENT / 'course.json')['course_order']
    if set(order) != {c['id'] for c in courses} or len(order) != len(courses):
        raise ValueError('Course journey order must list each course once')
    courses.sort(key=lambda c: order.index(c['id']))

    registry = read_json(CONTENT / 'shared/study_ids.json')
    for course in courses:
        for unit in course['units']:
            if registry.get(f'course/{course["id"]}/{unit["id"]}') != unit.get('study_id'):
                raise ValueError('Unregistered course study identity')

    units = {unit['id']: unit for course in courses for unit in course['units']}
    visited: set[str] = set()
    active: set[str] = set()

    def visit(identity: str) -> None:
        if identity in active:
            raise ValueError('Course prerequisite cycle')
        if identity in visited:
            return
        active.add(identity)
        for dep in units[identity]['prerequisites']:
            if dep not in units:
                raise ValueError('Missing prerequisite unit')
            visit(dep)
        active.remove(identity)
        visited.add(identity)

    for identity in units:
        visit(identity)
    return courses


def _render_unit_page(course: dict, index: int, unit: dict, unit_owners: dict, references: dict, observed: dict, url, controls) -> str:
    lab = (LABS / unit['lab']).read_text(encoding='utf-8')
    terms = '<dl>' + ''.join(
        f'<dt><strong>{E(term["term"])}</strong></dt><dd>{E(term["definition"])}</dd>'
        for term in unit['terms']
    ) + '</dl>'
    prereqs = ' · '.join(
        f'<a href="{url(f"course-{dep}.html")}">{E(dep.replace("-", " "))}</a>'
        for dep in unit['prerequisites']
    ) or 'Course entry point'
    body = (
        f'<p class="eyebrow">{E(course["title"])} · UNIT {index + 1}/{len(course["units"])}</p>'
        f'<h1>{E(unit["title"])}</h1><section class="prose">'
        f'<p>About {unit["estimated_minutes"]} minutes · {E(unit["path"])}. Prerequisites: {prereqs}</p>'
        '<h2>Learning outcomes</h2><ul>' + ''.join(f'<li>{E(item)}</li>' for item in unit['outcomes']) + '</ul>'
        f'<h2>Terms before mechanisms</h2>{terms}'
        '<h2>Understand the mechanism</h2>' + ''.join(f'<p>{E(p)}</p>' for p in unit['narrative']) + '</section>'
    )
    for example in unit.get('worked_examples', []):
        steps_html = ''.join(f'<li>{E(step)}</li>' for step in example['steps'])
        body += (
            f'<section class="prose"><h2>{E(example["title"])}</h2><p>{E(example["setup"])}</p>'
            f'<ol>{steps_html}</ol><p><strong>Result:</strong> {E(example["result"])}</p></section>'
        )
    incident = unit.get('incident')
    if incident:
        sections = ''.join(
            f'<h3>{E(label)}</h3><p>{E(incident[field])}</p>'
            for field, label in (
                ('symptom', 'Observed symptom'),
                ('evidence', 'Evidence to collect'),
                ('investigation', 'Investigation'),
                ('recovery', 'Recovery'),
                ('prevention', 'Prevention and regression check'),
            )
        )
        body += f'<section class="practice-card"><h2>Production incident walkthrough</h2>{sections}</section>'

    deps = (
        'Open the self-contained HTML exercise in a browser. It uses deterministic local fixtures and no API keys.'
        if unit['lab'].endswith('.html')
        else E(unit['dependencies'])
        if unit.get('dependencies')
        else 'Python 3.11+, standard library only.'
        if unit['lab'] not in {'transaction_api.py', 'request_lifecycle.py'}
        else 'Optional FastAPI/PostgreSQL dependencies; follow the project setup. This server never runs on GitHub Pages.'
    )
    body += (
        f'<section class="practice-card"><h2>Runnable local implementation</h2>'
        f'<p><a href="{url("examples/labs/" + unit["lab"])}">Download {E(unit["lab"])}</a>. {deps}</p>'
        '<p>Run the reference exercise, change one boundary, and inspect the observable result. '
        'Python references include executable assertions; the browser fixture exposes reproducible failure scenarios.</p>'
        f'<div class="code-panel"><button class="copy" type="button" aria-live="polite">Copy code</button><pre><code>{E(lab)}</code></pre></div></section>'
        f'<p><a href="{url("examples/local-projects.zip")}">Download all local sources, dependency requirements and setup instructions</a></p>'
    )
    if unit['lab'] in observed:
        body += (
            f'<h2>Observed reference output</h2><p>{E(observed[unit["lab"]]["scope"])}</p>'
            f'<pre><code>{E(observed[unit["lab"]]["observed_output"])}</code></pre>'
        )
    practice_items = ''.join(f'<li>{E(item)}</li>' for item in unit['practice'])
    body += (
        f'<section class="prose"><h2>Debug the boundary</h2><p>{E(unit["debugging"])}</p>'
        f'<h2>Costs and alternatives</h2><p>{E(unit["tradeoffs"])}</p>'
        f'<h2>Independent work</h2><ol>{practice_items}</ol>'
        '<h2>Check your understanding</h2><p>Explain the invariant, show the tested input/output, introduce a controlled failure, '
        'and defend one alternative. Passing the provided fixture does not establish correctness for every input.</p>'
    )
    if unit.get('project'):
        body += f'<p><a href="{url("project-" + unit["project"] + ".html")}">Continue to the complete local project and independent review tasks</a></p>'
    if unit.get('assessment'):
        body += f'<p><a href="{url("assessments.html")}#a-{unit["assessment"]}">Try the related graded scenario</a></p>'
    if unit.get('interviews'):
        body += '<h2>Technical interview and design defense</h2>'
        for interview in unit['interviews']:
            rubric_html = ''.join(f'<li>{E(item)}</li>' for item in interview['rubric'])
            body += (
                f'<details><summary>{E(interview["question"])}</summary>'
                f'<h3>Complete interview answer</h3>{answer_prose(interview["deep"])}'
                f'<h3>Follow-up</h3><p><strong>{E(interview["follow_up"]["question"])}</strong></p>'
                f'<p>{E(interview["follow_up"]["answer"])}</p>'
                f'<h3>What a strong answer demonstrates</h3><ul>{rubric_html}</ul></details>'
            )
    if unit.get('source_context'):
        ctx_items = ''.join(
            f'<li><a href="{E(references[c["reference_id"]][1])}">{E(references[c["reference_id"]][0])}</a>: '
            f'{E(c["explanation"])} <strong>Limit:</strong> {E(c["boundary"])} Checked {E(c["accessed_at"])}.</li>'
            for c in unit['source_context']
        )
        body += f'<h2>How the references inform this unit</h2><ul>{ctx_items}</ul>'
    body += render_reference_list(unit['references'], 'h2') + '</section>'
    pager = f'<nav class="pager"><a href="{url(unit_owners[unit["id"]] + ".html#worked-units")}">Return to the chapter</a>'
    if index + 1 < len(course['units']):
        next_unit = course['units'][index + 1]
        pager += f'<a href="{url("course-" + next_unit["id"] + ".html")}">Next: {E(next_unit["title"])}</a>'
    pager += '</nav>'
    body += pager + f'<section id="q{unit["study_id"]}" data-question="{unit["study_id"]}"><h2>My notes and bookmarks for this unit</h2>{controls({"id": unit["study_id"]})}</section>'
    return body


def build_courses(out: Path, write, url, controls=lambda q: '') -> dict:
    """Render course unit pages, capstone pages/starters, outcomes JSON, and local-projects.zip."""
    courses = load_courses()
    outcomes: list[dict] = []
    project_count = build_projects(out, write, url)
    references = read_json(CONTENT / 'shared/references.json')
    curriculum = read_json(CONTENT / 'curriculum.json')['chapters']
    unit_owners = {unit: slug for slug, chapter in curriculum.items() for unit in chapter.get('course_units', [])}
    observed = read_json(CONTENT / 'lab-results.json')

    for course in courses:
        for index, unit in enumerate(course['units']):
            body = _render_unit_page(course, index, unit, unit_owners, references, observed, url, controls)
            write(f'course-{unit["id"]}.html', unit['title'], body, f'course-{unit["id"]}')
            outcomes.append({
                'unit': unit['id'],
                'study_id': unit['study_id'],
                'course': course['id'],
                'outcomes': [{'id': f'{unit["id"]}.outcome-{i + 1}', 'text': text} for i, text in enumerate(unit['outcomes'])],
                'lab': unit['lab'],
                'assessment': unit.get('assessment'),
                'review': course['review_status'],
                'prerequisites': unit['prerequisites'],
                'path': unit['path'],
            })

    capstone_dir = out / 'examples/capstones'
    capstone_dir.mkdir(parents=True, exist_ok=True)
    for identity, title, lab_name, requirements, faults, threat, interface_stub in _CAPSTONES:
        reqs_html = ''.join(f'<li>{E(item)}</li>' for item in requirements)
        faults_html = ''.join(f'<li>{E(item)}</li>' for item in faults)
        env_note = (
            '<p>Requires PostgreSQL 16+, FastAPI, httpx and psycopg. From a repository checkout, run '
            '<code>python scripts/test_postgres_pilot.py</code>; it creates a new disposable loopback-only PostgreSQL cluster '
            'and removes it afterwards. See CONTRIBUTING for dependencies. This requires local PostgreSQL tools, not a cloud account.</p>'
            if lab_name == 'transaction_api.py'
            else f'<p>On macOS/Linux: <code>python3.11 {E(lab_name)}</code>. On Windows: <code>py -3.11 {E(lab_name)}</code>. '
            'Use an isolated Python environment; these three projects require only the standard library and small synthetic fixtures. No GPU or provider account is needed.</p>'
        )
        body = (
            f'<p class="eyebrow">LOCAL-FIRST CAPSTONE</p><h1>{E(title)}</h1>'
            '<p>This project is downloaded and run locally. GitHub Pages hosts instructions and source only. '
            'The reference implementation has an executable verification routine; independent work starts from the blank starter.</p>'
            f'<h2>Requirements and acceptance checks</h2><ol>{reqs_html}</ol>'
            f'<h2>Threat model and scope</h2><p>{E(threat)}</p>'
            '<h2>Architecture</h2><pre><code>Caller → validated operation → authoritative state → effect boundary → independent oracle</code></pre>'
            '<p>Follow each boundary in the source; identify which state survives a process restart and which effects commit independently.</p>'
            '<h2>Milestones</h2><ol><li>Run the reference and save its verification output.</li>'
            '<li>Implement the public interfaces in the starter without copying the solution.</li>'
            '<li>Add the failure fixtures below and prove they reject a broken implementation.</li>'
            '<li>Document costs, recovery limits, setup and a clean-start command.</li></ol>'
            f'<h2>Failure injection</h2><ul>{faults_html}</ul>'
        )
        body += (
            '<h2>Downloads and setup</h2><ul>'
            f'<li><a href="{url("examples/labs/" + lab_name)}">Reference solution and acceptance routine</a></li>'
            f'<li><a href="{url(f"examples/capstones/{identity}-starter.py")}">Starter template</a></li>'
            f'<li><a href="{url("examples/labs/README.md")}">Platform and dependency instructions</a></li></ul>'
            + env_note
            + '<h2>Review rubric and deliverables</h2><ul><li>Correct happy path and observed durable state.</li>'
            '<li>A reproduced failure with an independent assertion.</li>'
            '<li>No unauthorized effects or duplicate operation identities.</li>'
            '<li>Commands, environment, test output, architecture explanation and known limitations.</li></ul>'
            '<p>A project passes review only when its behavior is demonstrated. Reading the reference alone is insufficient.</p>'
        )
        write(f'capstone-{identity}.html', title, body)
        starter = (
            '"""Implement requirements before consulting the reference."""\n\n'
            + interface_stub
            + '\ndef verify():\n    raise NotImplementedError("Add independent invariants and failure cases")\n\n'
            'if __name__ == "__main__":\n    verify()\n'
        )
        (capstone_dir / f'{identity}-starter.py').write_text(starter, encoding='utf-8')

    bundle = out / 'examples/local-projects.zip'
    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(LABS.iterdir()):
            if (
                source.is_file()
                and not source.is_symlink()
                and not source.name.startswith('.')
                and source.suffix in _LAB_EXTENSIONS
            ):
                archive.write(source, f'labs/{source.name}')
        if not (LABS / '__init__.py').exists():
            archive.writestr('labs/__init__.py', '')
        for name in ('LICENSE', 'requirements-labs.txt', 'requirements-models.txt', 'requirements-advanced.txt', 'requirements-dev.txt'):
            archive.write(ROOT / name, name)
        archive.write(LABS / 'README.md', 'README.md')
        archive.write(ROOT / 'scripts/test_postgres_pilot.py', 'scripts/test_postgres_pilot.py')
        archive.write(ROOT / 'scripts/test_kafka_recovery.py', 'scripts/test_kafka_recovery.py')
        for project in load_projects():
            for source, target in iter_project_files(project['id']):
                archive.write(source, target)

    write_json(out / 'questions/outcomes.json', outcomes)
    all_units = [unit for course in courses for unit in course['units']]
    return {
        'foundation_courses': sum(c['id'] in {'python-backend', 'math-models'} for c in courses),
        'engineering_courses': len(courses),
        'cumulative_projects': project_count,
        'course_units': len(all_units),
        'course_interviews': sum(len(unit['interviews']) for unit in all_units),
        'worked_cases': sum(len(unit['worked_examples']) for unit in all_units),
        'incident_walkthroughs': sum('incident' in unit for unit in all_units),
        'connected_capstones': len(_CAPSTONES),
    }
