"""Load chapter-local content and preserve stable study identities."""
from pathlib import Path
import argparse
import json
import re

REPOSITORY = Path(__file__).resolve().parent.parent
CONTENT = REPOSITORY / 'content'
STAGES = [tuple(stage) for stage in json.loads((CONTENT / 'course.json').read_text())['stages']]

LESSON_SCHEMA = json.loads((CONTENT / 'shared/lesson-schema.json').read_text())
QUESTION_SCHEMA = json.loads((CONTENT / 'shared/question-schema.json').read_text())


def _check_schema(obj, schema, label, slug):
    """Validate the JSON Schema subset used by the content contracts recursively."""
    path = f'{label} {slug}'
    def check(value, spec, location):
        types = {'string': str, 'integer': int, 'number': (int, float),
                 'array': list, 'object': dict, 'boolean': bool}
        kind = spec.get('type')
        if kind and (not isinstance(value, types[kind]) or
                     kind in ('integer', 'number') and isinstance(value, bool)):
            raise ValueError(f'{location}: expected {kind}')
        if 'enum' in spec and value not in spec['enum']:
            raise ValueError(f'{location}: invalid enum value {value!r}')
        if isinstance(value, str):
            for key, invalid in (('minLength', len(value) < spec.get('minLength', 0)),
                                 ('maxLength', len(value) > spec.get('maxLength', float('inf')))):
                if invalid:
                    raise ValueError(f'{location}: violates {key}')
            if 'pattern' in spec and not re.search(spec['pattern'], value):
                raise ValueError(f'{location}: invalid pattern')
            if spec.get('format') == 'date':
                from datetime import date
                try:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                        raise ValueError('Expected YYYY-MM-DD')
                    date.fromisoformat(value)
                except ValueError as error:
                    raise ValueError(f'{location}: invalid date') from error
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not spec.get('minimum', -float('inf')) <= value <= spec.get('maximum', float('inf')):
                raise ValueError(f'{location}: outside numeric range')
        if isinstance(value, list):
            if len(value) < spec.get('minItems', 0):
                raise ValueError(f'{location}: too few items')
            for index, item in enumerate(value):
                check(item, spec.get('items', {}), f'{location}[{index}]')
        if isinstance(value, dict):
            for field in spec.get('required', []):
                if field not in value:
                    raise ValueError(f'{location}: missing required field "{field}"')
            properties = spec.get('properties', {})
            for field, item in value.items():
                if field in properties:
                    check(item, properties[field], f'{location}.{field}')
                elif spec.get('additionalProperties') is False:
                    raise ValueError(f'{location}: unknown field "{field}"')
    check(obj, schema, path)


def load(assign_ids=False):
    references = json.loads((CONTENT / 'shared/references.json').read_text())
    ids_path = CONTENT / 'shared/study_ids.json'
    identities = json.loads(ids_path.read_text())
    if any(type(value) is not int or value < 1 for value in identities.values()):
        raise ValueError('Study IDs must be positive integers')
    if len(set(identities.values())) != len(identities):
        raise ValueError('Study IDs must be unique')
    next_id = max(identities.values(), default=0) + 1
    changed = False
    chapters = {}
    for path in sorted((CONTENT / 'chapters').glob('*/chapter.json')):
        chapter = json.loads(path.read_text())
        slug = path.parent.name
        if chapter['slug'] != slug or slug in chapters:
            raise ValueError('Chapter slug does not match its unique folder: ' + slug)
        for group, namespace in (('questions', 'interview'), ('lessons', 'lesson')):
            rows = json.loads((path.parent / (group + '.json')).read_text())
            if group == 'questions':
                for shard in sorted(path.parent.glob('questions-*.json')):
                    rows.extend(json.loads(shard.read_text()))
            if not rows:
                raise ValueError('Missing ' + group + ': ' + slug)
            seen = set()
            for question in rows:
                key = namespace + '/' + slug + '/' + question['Q']
                if key in seen:
                    raise ValueError('Duplicate study question: ' + key)
                seen.add(key)
                if key not in identities:
                    if not assign_ids:
                        raise ValueError('Unregistered question: ' + key +
                                         '. Run python3 scripts/course_data.py --assign-ids first.')
                    identities[key] = next_id
                    next_id += 1
                    changed = True
                question['id'] = identities[key]
            chapter[group] = rows
            # Legacy entries retain their original contract. Enriched records must
            # satisfy the entire new contract even when `added` is absent/false.
            schema = LESSON_SCHEMA if group == 'lessons' else QUESTION_SCHEMA
            marker = 'conceptual_narrative' if group == 'lessons' else 'spoken'
            for question in rows:
                legacy_fields = ('Q', 'explain', 'example', 'takeaway') if group == 'lessons' else ('Q', 'A', 'Why', 'Risk', 'Trade', 'Try')
                for field in legacy_fields:
                    if not isinstance(question.get(field), str) or not question[field].strip():
                        raise ValueError(f'{slug}/{group}: missing text field {field}')
                if question.get('added') or marker in question:
                    _check_schema(question, schema, group, slug)
                    from editorial import validate_review
                    validate_review(question, namespace + '/' + slug + '/' + question['Q'])
                    from urllib.parse import urlsplit
                    for reference in question.get('references', []) + question.get('citations', []):
                        parsed = urlsplit(reference)
                        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                            raise ValueError(f'{slug}: primary references must be HTTP(S) URLs')
                    if 'local_lab' in question:
                        lab = Path(question['local_lab'])
                        target = REPOSITORY/lab
                        if lab.is_absolute() or '..' in lab.parts or lab.parts[0] != 'labs' or not target.is_file():
                            raise ValueError(f'{slug}: local lab must resolve inside labs/')
        review = json.loads((path.parent / 'review.json').read_text())
        review['references'] = [references[key] for key in review['links'].split(',')]
        chapter['review'] = review
        if not chapter['flow'] or len(chapter['case']) != 3:
            raise ValueError('Missing case or flow: ' + slug)
        chapters[slug] = chapter
    ordered, included = [], set()
    for number, (_, level, _, slugs) in enumerate(STAGES, 1):
        for slug in slugs:
            if slug not in chapters or slug in included:
                raise ValueError('Unknown or repeated course chapter: ' + slug)
            included.add(slug)
            chapter = chapters[slug]
            chapter.update(stage=number, level=level)
            ordered.append(chapter)
    if included != set(chapters):
        raise ValueError('Every chapter folder needs a learning stage')
    if changed:
        ids_path.write_text(json.dumps(identities, indent=2, ensure_ascii=False) + '\n')
    return ordered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assign-ids', action='store_true', help='Append IDs for new question titles; never renumber existing IDs')
    args = parser.parse_args()
    chapters = load(assign_ids=args.assign_ids)
    print(json.dumps({c['slug']: {q['Q']: q['id'] for q in c['lessons'] + c['questions']}
                      for c in chapters}, indent=2, ensure_ascii=False))
