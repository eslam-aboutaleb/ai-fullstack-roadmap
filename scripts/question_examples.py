"""Read topic-organized examples with explicit per-question assignments."""
from pathlib import Path
import json
import re

DIRECTORY = Path(__file__).resolve().parent.parent / 'content/examples/questions'
LANGUAGES = {'python', 'python-sketch', 'javascript', 'html', 'sql', 'bash', 'json', 'dockerfile'}
EXTENSIONS = {'python': 'py', 'python-sketch': 'py', 'javascript': 'js', 'html': 'html',
              'sql': 'sql', 'bash': 'sh', 'json': 'json', 'dockerfile': 'Dockerfile'}


def load_question_examples(chapters):
    recipes, assignments = {}, {}
    for catalog in sorted(DIRECTORY.glob('*/catalog.json')):
        for metadata in json.loads(catalog.read_text()):
            name, language = metadata['name'], metadata['language']
            if not re.fullmatch(r'[a-z0-9-]+', name) or name in recipes:
                raise ValueError('Invalid or duplicate code recipe: ' + name)
            if language not in LANGUAGES:
                raise ValueError('Unsupported language: ' + language)
            if metadata['filename'] != name + '.' + EXTENSIONS[language]:
                raise ValueError('Code filename must match its recipe and language: ' + name)
            if not {'explain', 'steps', 'expect', 'questions'} <= metadata.keys():
                raise ValueError('Missing explanation, assignments, or expected result: ' + name)
            code = (catalog.parent / metadata['filename']).read_text()
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
        listed = {entry['filename'] for entry in json.loads(catalog.read_text())}
        unlisted = {path.name for path in catalog.parent.iterdir()
                    if path.is_file() and path.name != 'catalog.json'} - listed
        if unlisted:
            raise ValueError(f'Unregistered teaching files in {catalog.parent.name}: {sorted(unlisted)}')
    ids = {q['id'] for chapter in chapters for q in chapter['lessons'] + chapter['questions']}
    required = {q['id'] for chapter in chapters for q in chapter['lessons'] + chapter['questions']
                if q.get('answer_format') != 'conceptual'}
    # A conceptual/design question may also gain a useful executable example.
    # Existing code contracts stay required; optional code still needs a known ID.
    if required - set(assignments) or set(assignments) - ids:
        raise ValueError(f'Code coverage mismatch: missing={sorted(required-set(assignments))}, '
                         f'unknown={sorted(set(assignments)-ids)}')
    return recipes, assignments
