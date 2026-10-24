"""Verify intentional coverage, rendered examples, and their stated outputs."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import ast
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from course_data import load
from question_examples import load_question_examples
from interview_teaching import teaching_title, answer_acronyms

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'


class QuestionExamples(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.question = None
        self.examples = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'data-question' in values:
            self.question = int(values['data-question'])
        if 'data-code-example' in values:
            assert self.question is not None, 'Example outside a question'
            assert values['id'] == f'code-q{self.question}'
            self.examples.append((self.question, values['data-code-example']))

    def handle_data(self, data):
        self.text.append(data)

    def handle_endtag(self, tag):
        if tag in ('p','li','h2','h3','h4','dd','td','th','figcaption'):
            self.text.append(' ')
        if tag == 'article':
            self.question = None


def checked_process(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, timeout=15, **kwargs)
    assert result.returncode == 0, (command[0], result.stderr)
    return result.stdout.strip()


def check():
    chapters = load()
    recipes, assigned = load_question_examples(chapters)
    rendered = []
    for chapter in chapters:
        page = QuestionExamples((SITE / (chapter['slug'] + '.html')).read_text())
        expected = {q['id'] for q in chapter['lessons'] + chapter['questions'] if q['id'] in assigned}
        # Conceptual defenses retain detailed, visible cases; do not manufacture
        # irrelevant executable snippets to inflate code coverage.
        import html, re
        text=(SITE / (chapter['slug'] + '.html')).read_text()
        visible=re.sub(r'\s+',' ',''.join(page.text))
        assert not 'data-topic-redirect' in text, chapter['slug']
        for q in chapter['lessons']+chapter['questions']:
            assert teaching_title(q).endswith('?'), q['Q']
            assert html.escape(teaching_title(q),quote=True) in text
            for _, definition in answer_acronyms(q):
                assert definition in visible
        for q in chapter['questions']:
            if q.get('answer_format') == 'conceptual':
                assert q['worked_case'] in visible
                assert f'id="q{q["id"]}"' in text
        assert {question_id for question_id, _ in page.examples} == expected
        assert len(page.examples) == len(expected), chapter['slug']
        rendered.extend(page.examples)
    assert len(rendered) == len(assigned)
    assert all(name == assigned[question_id]['name'] for question_id, name in rendered)
    counts = Counter()
    node = shutil.which('node')
    assert node, 'Node.js is needed to syntax-check the JavaScript teaching snippets'
    sqlite_examples = {
        'relational-schema': [('D1', 'A', 2)],
        'index-plan': None,
        'optimistic-write': [(2, 'first')],
    }
    with tempfile.TemporaryDirectory(prefix='question-example-check-') as directory:
        temporary = Path(directory)
        for name, example in recipes.items():
            language, code = example['language'], example['code']
            published = SITE / 'examples' / 'questions' / example['filename']
            assert published.read_text() == code, ('download differs', name)
            if language in {'python', 'python-sketch'}:
                ast.parse(code)
                counts['python_syntax_checked'] += 1
            if language == 'python':
                actual = checked_process([sys.executable, '-I', '-c', code], cwd=temporary)
                assert actual == example['expect'], (name, actual, example['expect'])
                counts['python_executed_with_expected_output'] += 1
            elif language == 'javascript':
                path = temporary / (name + '.js')
                path.write_text(code)
                checked_process([node, '--check', str(path)])
                counts['javascript_syntax_checked'] += 1
                if name in {'local-server-state', 'client-operation-key'} or example.get('execute'):
                    actual = checked_process([node, str(path)])
                    assert actual == example['expect'], (name, actual)
                    counts['javascript_executed_with_expected_output'] += 1
            elif language == 'json':
                json.loads(code)
                counts['json_parsed'] += 1
            elif language == 'bash':
                checked_process(['bash', '-n'], input=code)
                counts['bash_syntax_checked'] += 1
            elif language == 'sql' and name in sqlite_examples:
                # Keep the final SELECT separate so its actual rows can be verified.
                setup, query = code.rsplit('\nSELECT ', 1) if '\nSELECT ' in code else (None, None)
                with sqlite3.connect(':memory:') as db:
                    if name == 'index-plan':
                        db.executescript(code.split('EXPLAIN QUERY PLAN')[0])
                        plan = db.execute('EXPLAIN QUERY PLAN' + code.split('EXPLAIN QUERY PLAN')[1]).fetchall()
                        assert 'owner_time' in str(plan)
                    else:
                        assert setup and query
                        db.executescript(setup)
                        rows = db.execute('SELECT ' + query).fetchall()
                        assert rows == sqlite_examples[name], (name, rows)
                counts['sqlite_examples_executed'] += 1
            else:
                counts['integration_or_configuration_sketches'] += 1
    print(json.dumps({'questions_with_inline_code': len(assigned), 'distinct_examples': len(recipes),
                      'rendered_examples': len(rendered), **counts}, indent=2))


if __name__ == '__main__':
    check()
