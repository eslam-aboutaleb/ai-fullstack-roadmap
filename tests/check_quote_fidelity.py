"""Check the actual generated source; browser tests exercise JS and clipboard."""
from html.parser import HTMLParser
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from course_data import load
from question_examples import load_question_examples

SOURCE_FIXTURES = [
    'x = "hello world"', "y = 'single quotes'", 'z = """triple double quotes"""',
    "w = '''triple single quotes'''", r'escaped = "He said \"hello\""',
    'f_string = f"value is {x}"', '@decorator\ndef func(): pass',
    '@@@TOK0@@@ should survive highlighting',
    "SELECT * FROM users WHERE name = 'O''Brien';", 'const tpl = `hello ${name}`;',
    '{"key":"value"}', 'unicode = "café 😀"', 'html_entity = "&amp; &lt; &gt;"',
    'user@domain.com', r'printf \'"%s"\' "$HOME"',
    '# comment with "quotes"\nprint("next")', 'value = "# not a comment // --"',
    '<script>alert("data only")</script>', 'a\nb\n',
]


class CodeBlocks(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.active = False
        self.text = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'code':
            self.active, self.text = True, ''

    def handle_data(self, data):
        if self.active:
            self.text += data

    def handle_endtag(self, tag):
        if tag == 'code' and self.active:
            self.blocks.append(self.text)
            self.active = False


def check():
    chapters = load()
    _, examples = load_question_examples(chapters)
    checked = 0
    for chapter in chapters:
        blocks = CodeBlocks((ROOT/'_site'/f'{chapter["slug"]}.html').read_text()).blocks
        for q in chapter['lessons'] + chapter['questions']:
            if q['id'] not in examples:
                continue
            assert examples[q['id']]['code'] in blocks, ('rendered source differs', q['id'])
            for example in q.get('worked_examples', []):
                assert example['code'] in blocks, ('rich source differs', q['id'])
            checked += 1
    print(json.dumps({'rendered_code_sources_match': checked, 'browser_fixtures': len(SOURCE_FIXTURES)}))


if __name__ == '__main__':
    check()
