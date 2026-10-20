"""Verify contribution sources, source references, and generated-file boundaries."""
from pathlib import Path
import json
import re
import sys
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import course_data
from course_data import load
from examples import CATALOG, EXAMPLES
from question_examples import load_question_examples


def check():
    chapters = load()
    recipes, assigned = load_question_examples(chapters)
    assert set(EXAMPLES) == {chapter['slug'] for chapter in chapters}
    for chapter in chapters:
        folder = ROOT / 'content/chapters' / chapter['slug']
        assert {path.name for path in folder.iterdir() if path.is_file() and not re.fullmatch(r'questions-[a-zA-Z0-9_-]+\.json', path.name)} == {
            'chapter.json', 'lessons.json', 'questions.json', 'review.json', 'code-notes.json'}
        notes = json.loads((folder / 'code-notes.json').read_text())
        assert notes and all(isinstance(note, str) and note for note in notes)
    registered = {item['file'] for item in CATALOG.values()} | {'catalog.json'}
    files = {path.name for path in (ROOT / 'content/examples/chapters').iterdir() if path.is_file()}
    assert files == registered, ('unregistered chapter examples', files ^ registered)
    assets = [path for path in (ROOT / 'assets').glob('*/*') if path.is_file()]
    assert len({path.name for path in assets}) == len(assets), 'Published asset names collide'
    assert not any(ROOT.glob('*.html')), 'Generated HTML belongs in output folders'
    assert not any(ROOT.glob('*.css')), 'Editable CSS belongs in assets/css'
    assert not any(ROOT.glob('*.js')), 'Editable JavaScript belongs in assets/js'
    assert not any((ROOT / name).exists() for name in ('authoring', 'examples', 'diagrams'))
    assert {'_build/', '_site/'} <= set((ROOT / '.gitignore').read_text().splitlines())
    for document in [ROOT / 'README.md', ROOT / 'CONTRIBUTING.md', *list((ROOT / 'docs').glob('*.md'))]:
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', document.read_text()):
            if '://' in link or link.startswith('#'):
                continue
            target = document.parent / link.split('#', 1)[0]
            assert target.exists(), ('broken contributor link', document, link)
    # Registration is explicit and append-only, including on a clean contributor copy.
    with tempfile.TemporaryDirectory(prefix='study-identity-check-') as temporary:
        content_copy = Path(temporary) / 'content'
        shutil.copytree(ROOT / 'content', content_copy)
        old_content = course_data.CONTENT
        try:
            course_data.CONTENT = content_copy
            identities_path = content_copy / 'shared/study_ids.json'
            original_identities = json.loads(identities_path.read_text())
            questions_path = content_copy / 'chapters/foundations/questions.json'
            questions = json.loads(questions_path.read_text())
            questions.append({**questions[0], 'Q': 'Synthetic contributor registration check?'})
            questions_path.write_text(json.dumps(questions))
            try:
                load()
            except ValueError as error:
                assert 'Unregistered question' in str(error)
            else:
                raise AssertionError('Build implicitly registered a new study identity')
            assert json.loads(identities_path.read_text()) == original_identities
            load(assign_ids=True)
            updated = json.loads(identities_path.read_text())
            assert all(updated[key] == value for key, value in original_identities.items())
            assert updated['interview/foundations/Synthetic contributor registration check?'] == max(original_identities.values()) + 1
        finally:
            course_data.CONTENT = old_content
    print(json.dumps({'source_chapters': len(chapters), 'chapter_examples': len(EXAMPLES),
                      'inline_examples': len(recipes), 'assigned_questions': len(assigned),
                      'source_layout': 'pass', 'contributor_links': 'pass', 'append_only_id_registration': 'pass'}, indent=2))


if __name__ == '__main__':
    check()
