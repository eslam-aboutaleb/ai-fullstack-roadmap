"""Verify public packaging, links, question IDs, and synthetic examples."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import ast, json, subprocess, sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from examples import EXAMPLES
assert sys.version_info >= (3,10), 'Use Python 3.10+ to exercise examples'
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=set();self.refs=[];self.questions=[]
        self.feed(text)
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if a.get('id'):
            assert a['id'] not in self.ids,('duplicate ID',a['id'])
            self.ids.add(a['id'])
        if 'data-question' in a:self.questions.append(int(a['data-question']))
        for field in ('href','src'):
            if a.get(field):self.refs.append(a[field])
pages={p:Page(p.read_text()) for p in SITE.rglob('*.html')}
links=0;question_ids=[]
for path,page in pages.items():
    if path.parent==SITE:question_ids+=page.questions
    for ref in page.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or parsed.netloc:continue
        target=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
        assert SITE.resolve() in target.parents or target==SITE.resolve(),('escapes site',ref)
        if target.is_dir():target=target/'index.html'
        assert target.exists(),('missing file',path.name,ref)
        if parsed.fragment and target in pages:
            assert unquote(parsed.fragment) in pages[target].ids,('missing fragment',path.name,ref)
        links+=1
manifest=json.loads((SITE/'manifest.json').read_text())
assert len(question_ids)==manifest['questions']
assert len(set(question_ids))==len(question_ids)
assert set(range(1,481)).issubset(question_ids), 'Earlier progress identifiers must remain valid'
assert len(set(manifest['chapter_topics'].values()))>1, 'Chapter depth must not be a uniform quota'
assert sum(len(page.ids & {'walkthrough'}) for path,page in pages.items() if path.parent==SITE)==manifest['chapters']
for path in SITE.rglob('*'):
    if not path.is_file():continue
    text=path.read_text()
    for marker in ('Ragnor','OmniCare','/Users/','insurance-claims-rag-assistant','e57f646','70084f7','eslam-aboutaleb/ragnor'):
        assert marker not in text,(path.name,marker)
    if path.suffix=='.html':assert 'data-print>' not in text and 'id="print"' not in text
assert not (SITE/'sources').exists()
assert not any((SITE/name).exists() for name in ('authoring','content','scripts','tests','docs','labs'))
assert not (SITE/'.git').exists()
optional={'adk-agents','langchain','langgraph','mcp-server-engineering'}
executed=0;syntax=0
for slug,e in EXAMPLES.items():
    if e['language']!='python':continue
    ast.parse(e['code']);syntax+=1
    if slug not in optional:
        result=subprocess.run([sys.executable,'-I','-c',e['code']],capture_output=True,text=True,timeout=10)
        assert result.returncode==0,(slug,result.stderr)
        executed+=1
for path in (SITE/'examples'/'labs').glob('*.py'):ast.parse(path.read_text())
result=subprocess.run([sys.executable,str(SITE/'examples/labs/voice_pipeline.py')],capture_output=True,text=True,timeout=10)
assert result.returncode==0,result.stderr
result=subprocess.run([sys.executable,str(SITE/'examples/labs/foundation_bridge.py')],capture_output=True,text=True,timeout=10)
assert result.returncode==0,result.stderr
for slug in manifest['chapter_order']:
    assert {'review-notes','recommended-practice'}.issubset(pages[SITE/(slug+'.html')].ids),slug
from check_structure import check as check_structure
check_structure()
from check_question_examples import check as check_question_examples
check_question_examples()
print(json.dumps(dict(pages=len(pages),internal_links=links,questions=len(question_ids),python_examples_syntax_checked=syntax,standard_library_examples_executed=executed,injected_voice_lab='pass',public_source_snapshots=0,print_controls=0),indent=2))
