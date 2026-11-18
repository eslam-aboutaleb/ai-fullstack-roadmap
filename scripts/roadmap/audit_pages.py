"""Curriculum dependency graph, editorial audit outputs, and competency blueprint."""
from collections import Counter, defaultdict
from pathlib import Path
import re

from roadmap.config import CONTENT, escape_html as E, read_json, write_json
from roadmap.courses import load_courses
from roadmap.editorial import evidence_report, has_answered_followup, question_sources

PLAN = CONTENT / 'shared/competency-plan.json'
VALID_STATUS = {'planned', 'in-progress', 'independently-reviewed'}


def validate_plan(plan: dict | None = None, curriculum: dict | None = None) -> dict:
    """Validate competency-plan modules against curriculum chapters."""
    if plan is None:
        plan = read_json(PLAN)
    if curriculum is None:
        curriculum = read_json(CONTENT / 'curriculum.json')
    chapters = set(curriculum['chapters'])
    modules = plan.get('modules')
    if not isinstance(modules, list) or len(modules) < 12:
        raise ValueError('Competency plan must include all planned advanced topic workstreams')
    if len({m['id'] for m in modules}) != len(modules):
        raise ValueError('Duplicate planned competency IDs')
    if len({m['issue'] for m in modules}) != len(modules):
        raise ValueError('Duplicate issue linked to competency')

    for module in modules:
        if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', module['id']):
            raise ValueError('Invalid competency id')
        if module['status'] not in VALID_STATUS:
            raise ValueError('Unsupported competency status')
        if module['status'] == 'independently-reviewed' and not module.get('review_evidence'):
            raise ValueError('Do not label a competency independently reviewed without review evidence')
        for key in ('title', 'intro_problem', 'diagram', 'assessment'):
            if len(str(module.get(key, '')).strip()) < 15:
                raise ValueError(f'Competency {module["id"]}: missing {key}')
        for field in ('source_chapters', 'prerequisite_chapters'):
            if not module[field] or set(module[field]) - chapters:
                raise ValueError(f'Competency {module["id"]}: unknown/empty {field}')
        for field in ('learning_outcomes', 'interview_questions', 'local_exercises'):
            if (
                not isinstance(module.get(field), list)
                or len(module[field]) < 2
                or any(len(text.strip()) < 12 for text in module[field])
            ):
                raise ValueError(f'Competency {module["id"]}: incomplete {field}')
    return plan


def verified_assessment_links(index: list[dict], evidence: dict | None = None) -> dict[str, list[str]]:
    """Validate issue-to-assessment identifiers against indexed assessments."""
    if evidence is None:
        evidence = read_json(CONTENT / 'shared/assessment-evidence.json')
    issues = evidence.get('issues')
    if not isinstance(issues, dict) or not issues:
        raise ValueError('Missing assessment/issue evidence mapping')
    assessment_ids = {x['id'] for x in index}
    if len(assessment_ids) != len(index):
        raise ValueError('Duplicate assessment identifiers')
    for issue, ids in issues.items():
        if not str(issue).isdigit() or not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
            raise ValueError('Invalid issue-to-assessment mapping')
        if set(ids) - assessment_ids:
            raise ValueError(f'Unknown assessment for issue #{issue}: {sorted(set(ids) - assessment_ids)}')
    return {str(k): list(v) for k, v in issues.items()}


def _chapter_blueprint_base(chapter: dict, entry: dict) -> dict:
    return {
        'chapter': chapter['slug'],
        'title': chapter['title'],
        'track': entry['track'],
        'prerequisites': entry['prerequisites'],
        'effort_hours': entry['effort_hours'],
        'competency': entry['competency'],
    }


def inventory(chapters: list[dict], curriculum: dict) -> dict:
    """Build per-chapter/question/assessment competency inventory."""
    plan = validate_plan(curriculum=curriculum)
    practices = read_json(CONTENT / 'assessments.json')['items']
    browser = read_json(CONTENT / 'browser-labs.json')['labs']
    courses = load_courses()
    units = {
        u['id']: {
            'id': u['id'],
            'course': course['id'],
            'study_id': u['study_id'],
            'outcomes': u['outcomes'],
            'lab': u['lab'],
            'prerequisites': u['prerequisites'],
        }
        for course in courses
        for u in course['units']
    }
    assessment_links = verified_assessment_links(practices)
    assessments_by_id = {row['id']: row for row in practices}
    tasks: dict[int, list[dict]] = defaultdict(list)
    for row in practices:
        tasks[row['topic']].append({'kind': row['kind'], 'id': row['id'], 'objective': row['objective']})
    for row in browser:
        tasks[row['topic']].append({'kind': 'browser-code', 'id': row['id'], 'objective': row['objective']})
    for unit in units.values():
        unit['practice'] = tasks[unit['study_id']]

    records: list[dict] = []
    for chapter in chapters:
        slug = chapter['slug']
        entry = curriculum['chapters'][slug]
        guided = [
            {
                'study_id': q['id'],
                'question': q['Q'],
                'practice': tasks[q['id']],
                'explanation_length': len(q.get('explain', '')),
            }
            for q in chapter['lessons']
        ]
        interviews = [
            {
                'study_id': q['id'],
                'question': q['Q'],
                'difficulty': q.get('difficulty', 'not-calibrated'),
                'practice': tasks[q['id']],
                'answer_length': len(q.get('A', '')),
                'has_answered_followup': has_answered_followup(q),
                'has_question_level_reference': bool(question_sources(q)),
            }
            for q in chapter['questions']
        ]
        mapped_units = [units[identity] for identity in entry.get('course_units', []) if identity in units]
        missing_units = sorted(set(entry.get('course_units', [])) - set(units))
        if missing_units:
            raise ValueError(f'{slug}: missing course units: {missing_units}')
        records.append({
            **_chapter_blueprint_base(chapter, entry),
            'introduction': {
                'goal': chapter['goal'],
                'intro': chapter['intro'],
                'terms': [term[0] for term in chapter['terms']],
            },
            'foundation_lessons': guided,
            'interview_questions': interviews,
            'linked_course_units': mapped_units,
            'linked_practice_count': (
                sum(len(row['practice']) for row in guided + interviews)
                + sum(len(u['practice']) for u in mapped_units)
            ),
            'evidence_stage': 'introduced; some local practice is authored, independent learner mastery not verified',
            'independent_technical_review': 'pending',
        })

    issue_evidence = [
        {
            'issue': int(issue),
            'assessment_ids': ids,
            'items': [
                {
                    'id': identity,
                    'topic': assessments_by_id[identity]['topic'],
                    'objective': assessments_by_id[identity]['objective'],
                    'kind': assessments_by_id[identity]['kind'],
                    'status': 'authored-assessment-only',
                }
                for identity in ids
            ],
            'definition_of_done_met': False,
            'external_integration_verified': False,
            'independent_review': 'pending',
        }
        for issue, ids in sorted(assessment_links.items(), key=lambda x: int(x[0]))
    ]
    return {
        'version': 1,
        'review_status': 'planned-and-source-inventory',
        'no_question_cap': True,
        'disclaimer': 'An authored outcome, lab or answered question is not evidence of real learner mastery or independent technical approval.',
        'total_chapters': len(records),
        'total_planned_modules': len(plan['modules']),
        'chapters': records,
        'planned_modules': plan['modules'],
        'assessment_evidence': issue_evidence,
        'registered_assessments': len(practices),
        'evidence_scope': 'Draft assessment authoring and identity traceability, not subject acceptance or learner mastery',
    }


def build_blueprint(out: Path, write, chapters: list[dict], curriculum: dict, url) -> dict:
    """Write competency-blueprint JSON artifact."""
    payload = inventory(chapters, curriculum)
    write_json(out / 'questions/competency-blueprint.json', payload)
    return payload


def curriculum_graph(chapters: list[dict], curriculum: dict, url) -> str:
    """Render scrollable SVG DAG connecting prerequisite chapters."""
    depths: dict[str, int] = {}
    active: set[str] = set()

    def depth(slug: str) -> int:
        if slug in active:
            raise ValueError('Cyclic prerequisite graph')
        if slug not in depths:
            active.add(slug)
            depths[slug] = max((depth(dep) + 1 for dep in curriculum['chapters'][slug]['prerequisites']), default=0)
            active.remove(slug)
        return depths[slug]

    groups: dict[int, list[dict]] = defaultdict(list)
    for chapter in chapters:
        groups[depth(chapter['slug'])].append(chapter)
    positions = {c['slug']: (d * 240 + 15, i * 95 + 15) for d, group in groups.items() for i, c in enumerate(group)}
    width = (max(groups) + 1) * 240
    height = max(len(group) for group in groups.values()) * 95 + 20

    lines: list[str] = []
    nodes: list[str] = []
    for chapter in chapters:
        x, y = positions[chapter['slug']]
        for dep in curriculum['chapters'][chapter['slug']]['prerequisites']:
            dx, dy = positions[dep]
            lines.append(
                f'<path d="M {dx + 210} {dy + 32} C {dx + 235} {dy + 32}, {x - 20} {y + 32}, {x} {y + 32}" '
                'fill="none" stroke="var(--muted)" marker-end="url(#prerequisite-arrow)"/>'
            )
        title = chapter['title']
        first = ''
        second = ''
        for word in title.split():
            if len(first) + len(word) < 24 and not second:
                first += (' ' if first else '') + word
            else:
                second += (' ' if second else '') + word
        nodes.append(
            f'<a href="{url(chapter["slug"] + ".html")}"><title>{E(title)}</title>'
            f'<rect x="{x}" y="{y}" width="210" height="65" rx="10" fill="var(--panel)" stroke="var(--line)"/>'
            f'<text x="{x + 10}" y="{y + 25}" fill="var(--text)" font-size="13">{E(first)}</text>'
            f'<text x="{x + 10}" y="{y + 46}" fill="var(--text)" font-size="12">{E(second[:29])}</text></a>'
        )
    return (
        '<div class="prerequisite-map" role="region" aria-label="Scrollable prerequisite graph; use links or read the table below" tabindex="0">'
        f'<svg width="{width}" height="{height}" role="group" aria-labelledby="prerequisite-title">'
        f'<title id="prerequisite-title">Prerequisite graph for all {len(chapters)} chapters. '
        'Arrows point from prerequisite to dependent chapter; the table below provides every relationship as text.</title>'
        '<defs><marker id="prerequisite-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">'
        '<path d="M0 0L6 3L0 6" fill="var(--muted)"/></marker></defs>'
        + ''.join(lines + nodes)
        + '</svg></div>'
    )


def build_audit_pages(out: Path, write, chapters: list[dict], curriculum: dict, url) -> None:
    """Write editorial report, curriculum map, audit JSONs, and topic coverage outputs."""
    states = Counter(
        q.get('reviewer_status', {}).get('status', 'legacy unreviewed')
        for chapter in chapters
        for q in chapter['questions']
    )
    report = {
        'version': 1,
        'question_review_states': dict(states),
        'automated_checks': 'Schemas, source fidelity, local executable fixtures, links, duplicates and browser behavior are checked in CI. These do not establish factual accuracy.',
        'limitations': [
            'Legacy unreviewed records remain itemized',
            'External reference freshness is not exhaustively checked',
            'Near-duplicate matching is lexical, not a semantic correctness proof',
        ],
        'review_policy': 'Reviewed/approved question labels require a matching reviewer, date, notes and SHA-256 content attestation. Drafts remain visibly marked.',
    }
    write_json(out / 'questions/editorial-report.json', report)

    state_items = ''.join(f'<li>{E(state)}: {count}</li>' for state, count in sorted(states.items()))
    limitation_items = ''.join(
        f'<li>{E(item)}</li>'
        for item in report['limitations']
        if item != 'Independent technical review pending'
    )
    write(
        'editorial-report.html',
        'Editorial evidence and review state',
        f'<h1>Editorial evidence and review state</h1>'
        f'<p>Counts below come from source records. A draft label identifies material awaiting independent technical review.</p>'
        f'<ul>{state_items}</ul><h2>What automation establishes</h2><p>{E(report["automated_checks"])}</p>'
        f'<h2>Review policy</h2><p>{E(report["review_policy"])}</p>'
        f'<h2>Remaining review</h2><ul>{limitation_items}</ul>'
        f'<p><a href="{url("questions/editorial-report.json")}">Download the report</a> · '
        f'<a href="{url("curriculum-map.html")}">Chapter inventory</a></p>',
    )

    inventory_rows: list[dict] = []
    by_slug = {c['slug']: c for c in chapters}
    for chapter in chapters:
        entry = curriculum['chapters'][chapter['slug']]
        inventory_rows.append({
            **_chapter_blueprint_base(chapter, entry),
            'artifacts': entry['artifacts'],
            'lesson_ids': [q['id'] for q in chapter['lessons']],
            'question_ids': [q['id'] for q in chapter['questions']],
            'enriched_lessons': sum('conceptual_narrative' in q for q in chapter['lessons']),
            'enriched_questions': sum('spoken' in q or q.get('answer_format') == 'conceptual' for q in chapter['questions']),
            'legacy_lessons_needing_depth_review': [
                q['id'] for q in chapter['lessons']
                if len(q.get('explain', q.get('A', '')).split()) < 120 and 'conceptual_narrative' not in q
            ],
            'references': chapter['review']['references'],
            'technical_review': 'independent review pending',
        })
    write_json(
        out / 'questions/curriculum-audit.json',
        {
            'version': 1,
            'chapters': inventory_rows,
            'notes': 'Counts and metadata are automatic. Word count flags prioritize review; they do not prove factual accuracy or depth.',
        },
    )

    table_rows = ''.join(
        f'<tr><th scope="row"><a href="{url(c["chapter"] + ".html")}">{E(c["title"])}</a></th>'
        f'<td>{E(c["track"])}</td>'
        f'<td>{" · ".join(f"""<a href="{url(dep + ".html")}">{E(by_slug[dep]["title"])}</a>""" for dep in c["prerequisites"]) or "Entry point"}</td>'
        f'<td>{len(c["lesson_ids"])} lessons / {len(c["question_ids"])} questions</td>'
        f'<td>{c["enriched_lessons"]} / {c["enriched_questions"]}</td>'
        f'<td>{len(c["legacy_lessons_needing_depth_review"])}</td></tr>'
        for c in inventory_rows
    )
    write(
        'curriculum-map.html',
        'Curriculum map and migration audit',
        '<p class="eyebrow">PREREQUISITES · OUTCOMES · OBSERVED COVERAGE</p>'
        '<h1>Choose a path and see its dependencies.</h1>'
        '<p>All chapter relationships come from the versioned curriculum manifest. Entry points are optional starting routes; '
        'chapters remain directly accessible. The graph is scrollable and keyboard linked; the complete table below is its text equivalent.</p>'
        + curriculum_graph(chapters, curriculum, url)
        + f'<p><a href="{url("questions/competency-blueprint.json")}">Download competency, assessment and review evidence (JSON)</a></p>'
        '<div class="table-scroll"><table><caption>Actual source coverage and prerequisite relationships. '
        'Enriched counts mean schema fields exist, not independent approval.</caption>'
        '<thead><tr><th>Chapter</th><th>Track</th><th>Prerequisites</th><th>Actual content</th>'
        f'<th>Enriched lessons/questions</th><th>Short legacy lessons to review</th></tr></thead><tbody>{table_rows}</tbody></table></div>',
    )

    coverage: list[dict] = []
    for position, chapter in enumerate(chapters, 1):
        coverage.append({
            'position': position,
            'chapter': chapter['slug'],
            'title': chapter['title'],
            'stage': chapter['stage'],
            'prerequisites': curriculum['chapters'][chapter['slug']]['prerequisites'],
            'defined_terms': [term for term, _ in chapter['terms']],
            'lessons': [{'id': q['id'], 'title': q['Q']} for q in chapter['lessons']],
            'interview_topics': [
                {
                    'id': q['id'],
                    'question': q['Q'],
                    'answered_followups': len(q.get('follow_ups', [])),
                    'source_linked': bool(question_sources(q) or q.get('reference')),
                }
                for q in chapter['questions']
            ],
            'companion_units': curriculum['chapters'][chapter['slug']].get('course_units', []),
            'same_page_answers': len(chapter['lessons']) + len(chapter['questions']),
            'conceptual_worked_cases': sum(q.get('answer_format') == 'conceptual' for q in chapter['questions']),
            'review_state': 'See per-record digest-backed editorial evidence',
        })
    if any(
        not row['lessons'] or not row['interview_topics'] or not any(q['answered_followups'] for q in row['interview_topics'])
        for row in coverage
    ):
        raise ValueError('Every chapter needs teaching, interview questions and an answered boundary defense')

    write_json(out / 'questions/editorial-evidence.json', evidence_report(chapters))
    write_json(
        out / 'questions/topic-coverage.json',
        {
            'version': 1,
            'question_count_limit': None,
            'full_answers_per_chapter': None,
            'question_data_shard_size': 40,
            'scope': 'Topic and artifact inventory, not certification of semantic completeness or independent approval',
            'chapters': coverage,
        },
    )
