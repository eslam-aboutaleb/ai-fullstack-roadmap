"""Canonical loader, schema validator, and study ID registry for chapters."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

from .config import CONTENT, ROOT, read_json
from .editorial import validate_review
from .question_markdown import loads_questions_md

STAGES = [tuple(stage) for stage in read_json(CONTENT / 'course.json')['stages']]
LESSON_SCHEMA = read_json(CONTENT / 'shared/lesson-schema.json')
QUESTION_SCHEMA = read_json(CONTENT / 'shared/question-schema.json')
CONCEPTUAL_QUESTION_SCHEMA = read_json(CONTENT / 'shared/conceptual-question-schema.json')


def check_schema(obj: object, schema: dict, label: str, slug: str) -> None:
    """Validate the JSON Schema subset used by the content contracts recursively."""
    root_path = f'{label} {slug}'
    types = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'array': list,
        'object': dict,
        'boolean': bool,
    }

    def validate(value: object, spec: dict, location: str) -> None:
        kind = spec.get('type')
        if kind and (
            not isinstance(value, types[kind])
            or (kind in ('integer', 'number') and isinstance(value, bool))
        ):
            raise ValueError(f'{location}: expected {kind}')
        if 'enum' in spec and value not in spec['enum']:
            raise ValueError(f'{location}: invalid enum value {value!r}')
        if isinstance(value, str):
            if len(value) < spec.get('minLength', 0):
                raise ValueError(f'{location}: violates minLength')
            if len(value) > spec.get('maxLength', float('inf')):
                raise ValueError(f'{location}: violates maxLength')
            if 'pattern' in spec and not re.search(spec['pattern'], value):
                raise ValueError(f'{location}: invalid pattern')
            if spec.get('format') == 'date':
                try:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                        raise ValueError('Expected YYYY-MM-DD')
                    date.fromisoformat(value)
                except ValueError as err:
                    raise ValueError(f'{location}: invalid date') from err
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not spec.get('minimum', -float('inf')) <= value <= spec.get('maximum', float('inf')):
                raise ValueError(f'{location}: outside numeric range')
        if isinstance(value, list):
            if len(value) < spec.get('minItems', 0):
                raise ValueError(f'{location}: too few items')
            item_spec = spec.get('items', {})
            for index, item in enumerate(value):
                validate(item, item_spec, f'{location}[{index}]')
        if isinstance(value, dict):
            for field in spec.get('required', []):
                if field not in value:
                    raise ValueError(f'{location}: missing required field "{field}"')
            properties = spec.get('properties', {})
            for field, item in value.items():
                if field in properties:
                    validate(item, properties[field], f'{location}.{field}')
                elif spec.get('additionalProperties') is False:
                    raise ValueError(f'{location}: unknown field "{field}"')

    validate(obj, schema, root_path)


def load_chapter_questions(chapter_dir: Path) -> list[dict]:
    """Load questions from the canonical questions.md pack (or legacy JSON if present in fixtures)."""
    md_path = chapter_dir / 'questions.md'
    json_path = chapter_dir / 'questions.json'
    shards = sorted(chapter_dir.glob('questions-*.json'))

    if md_path.is_file():
        if json_path.exists() or shards:
            raise ValueError(f'{chapter_dir.name}: remove legacy questions*.json alongside questions.md')
        return loads_questions_md(md_path.read_text(encoding='utf-8'), source=f'{chapter_dir.name}/questions.md')

    if not json_path.is_file():
        raise ValueError(f'{chapter_dir.name}: missing questions.md')
    rows = json.loads(json_path.read_text(encoding='utf-8'))
    for shard in shards:
        rows.extend(json.loads(shard.read_text(encoding='utf-8')))
    return rows


def _validate_urls(slug: str, urls: list[str], message: str) -> None:
    for ref in urls:
        parsed = urlsplit(ref)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise ValueError(f'{slug}: {message}')


def _validate_local_lab(slug: str, raw_lab: str, repo_root: Path) -> None:
    lab = Path(raw_lab)
    target = repo_root / lab
    if lab.is_absolute() or '..' in lab.parts or lab.parts[0] != 'labs' or not target.is_file():
        raise ValueError(f'{slug}: local lab must resolve inside labs/')


def load_chapters(assign_ids: bool = False, *, content_dir: Path | None = None) -> list[dict]:
    """Load, schema-validate, and stage-order every chapter and its lessons/questions."""
    base_content = content_dir or CONTENT
    repo_root = base_content.parent if (base_content.parent / 'labs').is_dir() else ROOT

    references = read_json(base_content / 'shared/references.json')
    reviews = read_json(base_content / 'reviews.json')
    conceptual_schema = read_json(base_content / 'shared/conceptual-question-schema.json')
    lesson_schema = read_json(base_content / 'shared/lesson-schema.json')
    question_schema = read_json(base_content / 'shared/question-schema.json')

    ids_path = base_content / 'shared/study_ids.json'
    identities = read_json(ids_path)
    if any(type(v) is not int or v < 1 for v in identities.values()):
        raise ValueError('Study IDs must be positive integers')
    if len(set(identities.values())) != len(identities):
        raise ValueError('Study IDs must be unique')

    next_id = max(identities.values(), default=0) + 1
    changed = False
    chapters: dict[str, dict] = {}

    for chapter_json in sorted((base_content / 'chapters').glob('*/chapter.json')):
        chapter_dir = chapter_json.parent
        slug = chapter_dir.name
        chapter = json.loads(chapter_json.read_text(encoding='utf-8'))
        if chapter['slug'] != slug or slug in chapters:
            raise ValueError('Chapter slug does not match its unique folder: ' + slug)

        for group, namespace in (('questions', 'interview'), ('lessons', 'lesson')):
            if group == 'questions':
                rows = load_chapter_questions(chapter_dir)
            else:
                rows = json.loads((chapter_dir / 'lessons.json').read_text(encoding='utf-8'))

            if not rows:
                raise ValueError(f'Missing {group}: {slug}')

            seen: set[str] = set()
            for item in rows:
                key = f'{namespace}/{slug}/{item["Q"]}'
                if key in seen:
                    raise ValueError('Duplicate study question: ' + key)
                seen.add(key)
                if key not in identities:
                    if not assign_ids:
                        raise ValueError(
                            f'Unregistered question: {key}. Run python3 scripts/course_data.py --assign-ids first.'
                        )
                    identities[key] = next_id
                    next_id += 1
                    changed = True
                item['id'] = identities[key]

            chapter[group] = rows
            schema = lesson_schema if group == 'lessons' else question_schema
            marker = 'conceptual_narrative' if group == 'lessons' else 'spoken'

            for item in rows:
                if group == 'lessons':
                    legacy = ('Q', 'A', 'Why', 'Risk', 'Trade', 'Try') if 'A' in item and 'explain' not in item else ('Q', 'explain', 'example', 'takeaway')
                else:
                    legacy = ('Q', 'A', 'Why', 'Risk', 'Trade', 'Try')
                for field in legacy:
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        raise ValueError(f'{slug}/{group}: missing text field {field}')

                identity = f'{namespace}/{slug}/{item["Q"]}'
                if item.get('answer_format') == 'conceptual':
                    check_schema(item, conceptual_schema, group, slug)
                    validate_review(item, identity, reviews, content_dir=base_content)
                    _validate_urls(slug, item['citations'], 'conceptual citations must be HTTP(S) URLs')

                if item.get('added') or marker in item:
                    check_schema(item, schema, group, slug)
                    validate_review(item, identity, reviews, content_dir=base_content)
                    _validate_urls(slug, item.get('references', []) + item.get('citations', []), 'primary references must be HTTP(S) URLs')
                    if 'local_lab' in item:
                        _validate_local_lab(slug, item['local_lab'], repo_root)

        review = json.loads((chapter_dir / 'review.json').read_text(encoding='utf-8'))
        review['references'] = [references[key] for key in review['links'].split(',')]
        chapter['review'] = review
        if not chapter['flow'] or len(chapter['case']) != 3:
            raise ValueError('Missing case or flow: ' + slug)
        chapters[slug] = chapter

    ordered: list[dict] = []
    included: set[str] = set()
    stages = [tuple(s) for s in json.loads((base_content / 'course.json').read_text(encoding='utf-8'))['stages']]
    for number, (_, level, _, slugs) in enumerate(stages, 1):
        for slug in slugs:
            if slug not in chapters or slug in included:
                raise ValueError('Unknown or repeated course chapter: ' + slug)
            included.add(slug)
            ch = chapters[slug]
            ch.update(stage=number, level=level)
            ordered.append(ch)
    if included != set(chapters):
        raise ValueError('Every chapter folder needs a learning stage')

    if changed:
        ids_path.write_text(json.dumps(identities, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return ordered
