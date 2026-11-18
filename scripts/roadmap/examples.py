"""Chapter-level and per-question runnable teaching example catalogs."""
from __future__ import annotations

from pathlib import Path
import re

from .config import CONTENT, read_json

CHAPTER_EXAMPLES_DIR = CONTENT / 'examples/chapters'
QUESTION_EXAMPLES_DIR = CONTENT / 'examples/questions'

EXTENSIONS = {
    'python': 'py',
    'python-sketch': 'py',
    'javascript': 'js',
    'html': 'html',
    'sql': 'sql',
    'bash': 'sh',
    'json': 'json',
    'dockerfile': 'Dockerfile',
}
LANGUAGES = frozenset(EXTENSIONS)


def load_chapter_examples(directory: Path = CHAPTER_EXAMPLES_DIR) -> tuple[dict, dict]:
    """Load chapter-level runnable code recipes declared in catalog.json."""
    catalog = read_json(directory / 'catalog.json')
    examples: dict[str, dict] = {}
    for slug, entry in catalog.items():
        filename = entry['file']
        if Path(filename).name != filename:
            raise ValueError('Chapter example filename must stay inside its source folder')
        examples[slug] = {
            'scope': entry['scope'],
            'language': entry['language'],
            'code': (directory / filename).read_text(encoding='utf-8'),
        }
    return catalog, examples


def load_question_examples(
    chapters: list[dict],
    directory: Path = QUESTION_EXAMPLES_DIR,
) -> tuple[dict, dict]:
    """Load and verify topic-organized question example catalogs and assignments."""
    recipes: dict[str, dict] = {}
    assignments: dict[int, dict] = {}

    for catalog_path in sorted(directory.glob('*/catalog.json')):
        entries = read_json(catalog_path)
        for metadata in entries:
            name, language = metadata['name'], metadata['language']
            if not re.fullmatch(r'[a-z0-9-]+', name) or name in recipes:
                raise ValueError('Invalid or duplicate code recipe: ' + name)
            if language not in LANGUAGES:
                raise ValueError('Unsupported language: ' + language)
            if metadata['filename'] != f'{name}.{EXTENSIONS[language]}':
                raise ValueError('Code filename must match its recipe and language: ' + name)
            if not {'explain', 'steps', 'expect', 'questions'} <= metadata.keys():
                raise ValueError('Missing explanation, assignments, or expected result: ' + name)

            code = (catalog_path.parent / metadata['filename']).read_text(encoding='utf-8')
            if not code.strip() or len(metadata['steps'].split(' || ')) < 2:
                raise ValueError('Missing code or walkthrough: ' + name)

            recipe = dict(metadata, code=code)
            recipes[name] = recipe
            if not recipe['questions']:
                raise ValueError('Example must be assigned to a question: ' + name)
            for question_id in recipe['questions']:
                if question_id in assignments:
                    raise ValueError(f'Duplicate question assignment: {question_id}')
                assignments[question_id] = recipe

        listed = {entry['filename'] for entry in entries}
        unlisted = {
            path.name
            for path in catalog_path.parent.iterdir()
            if path.is_file() and path.name != 'catalog.json' and not path.name.startswith('.')
        } - listed
        if unlisted:
            raise ValueError(f'Unregistered teaching files in {catalog_path.parent.name}: {sorted(unlisted)}')

    ids = {q['id'] for ch in chapters for q in ch['lessons'] + ch['questions']}
    required = {
        q['id']
        for ch in chapters
        for q in ch['lessons'] + ch['questions']
        if q.get('answer_format') != 'conceptual'
    }
    missing = sorted(required - set(assignments))
    unknown = sorted(set(assignments) - ids)
    if missing or unknown:
        raise ValueError(f'Code coverage mismatch: missing={missing}, unknown={unknown}')
    return recipes, assignments
