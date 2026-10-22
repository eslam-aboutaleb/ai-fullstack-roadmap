"""Verify public packaging, links, question IDs, and synthetic examples."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import ast, json, os, subprocess, sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from examples import EXAMPLES
assert sys.version_info >= (3,11), 'Use Python 3.11+ to exercise examples'
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'

# Verify the site is base-path safe under the GitHub Pages repository path.
env = dict(os.environ, PAGES_BASE_PATH='/ai-fullstack-roadmap/')
subprocess.run([sys.executable,'-B','scripts/build.py'], cwd=ROOT, check=True, env=env)
subprocess.run([sys.executable,'-B','scripts/package.py'], cwd=ROOT, check=True, env=env)
sys.path.insert(0, str(ROOT / 'tests'))
from check_base_path import check as check_base_path
check_base_path()
# Rebuild without a base path for the default local and remaining checks.
subprocess.run([sys.executable,'-B','scripts/build.py'], cwd=ROOT, check=True, env=dict(os.environ, PAGES_BASE_PATH=''))
subprocess.run([sys.executable,'-B','scripts/package.py'], cwd=ROOT, check=True)
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
    if path.parent==SITE and path.stem in [slug for stage in __import__('course_data').STAGES for slug in stage[3]]:question_ids+=page.questions
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
    if path.suffix in {'.wasm', '.zip'}:
        assert 'runtime' in path.parts or path.name == 'local-projects.zip' or (path.parent == SITE/'examples/projects' and path.name in {row['id']+'.zip' for row in json.loads((ROOT/'content/projects.json').read_text())}), ('unexpected binary', path)
        continue
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
from check_curriculum import check as check_curriculum
check_curriculum()
# Performance budgets: static asset size limits for Pages delivery.
for asset,limit in (('style.css',50*1024),('app.js',100*1024),('course.js',100*1024),('highlight.js',20*1024)):
    p=SITE/asset
    if p.exists():
        size=p.stat().st_size
        assert size<=limit,(asset,size,limit)
print(json.dumps(dict(pages=len(pages),internal_links=links,questions=len(question_ids),python_examples_syntax_checked=syntax,standard_library_examples_executed=executed,injected_voice_lab='pass',public_source_snapshots=0,print_controls=0,curriculum_tracks=len(json.loads((ROOT/'content/curriculum.json').read_text())['tracks']),curriculum_chapters=manifest['chapters'],curriculum_dag_acyclic=True,performance_budget='pass'),indent=2))
from check_answer_format import check as check_answer_format
check_answer_format()
from check_quote_fidelity import check as check_quote_fidelity
check_quote_fidelity()
from check_editorial_qa import check as check_editorial_qa
check_editorial_qa()

from check_review_regressions import check as check_review_regressions
check_review_regressions()

for page_path in SITE.glob('*.html'):
    text = page_path.read_text()
    import re
    assert not re.search(r'<script[^>]+src=["\']https?://', text), page_path

subprocess.run(['node', str(ROOT/'tests/check_study.cjs')], check=True)
from check_question_data import check as check_question_data
check_question_data()

for lab_name in ('async_job_engine.py', 'model_training.py', 'attention_math.py', 'rag_evaluation.py', 'durable_agent.py',
                 'data_contract_pipeline.py', 'llm_contracts.py', 'retrieval_scorecard.py', 'production_scorecard.py', 'restore_drill.py'):
    result = subprocess.run([sys.executable, '-B', str(ROOT/'labs'/lab_name)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, (lab_name, result.stderr)
print('Async, training/gradients, attention, retrieval and durable-effect pilots: pass')

rag_pipeline_result=subprocess.run([sys.executable,'-B',str(ROOT/'labs/grounded_policy_pipeline.py')],capture_output=True,text=True,timeout=10)
assert rag_pipeline_result.returncode==0,(rag_pipeline_result.stdout,rag_pipeline_result.stderr)
assert 'PASS' in rag_pipeline_result.stdout

expected = json.loads((ROOT/'content/simulations.json').read_text())
actual = json.loads(subprocess.check_output(['node',str(ROOT/'scripts/simulation_fixtures.cjs')],text=True))
assert actual == expected, 'Simulation transition fixtures drifted'
assert actual[1]['normal']['final']['invariant'] is True and actual[1]['failure']['final']['invariant'] is False
assert actual[3]['failure']['final']['calls'] == 2 and actual[3]['failure']['final']['effects'] == 1
print('Four deterministic simulation transition fixtures: pass')

assert not any(path.suffix in {'.pyc','.db','.sqlite','.key','.pem'} or path.name.startswith('.env') for path in SITE.rglob('*')), 'Private local runtime files leaked into the artifact'
import zipfile
with zipfile.ZipFile(SITE/'examples/local-projects.zip') as archive:
    assert len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate ZIP members'
    assert {'labs/async_job_engine.py','labs/transaction_api.py','labs/fullstack_demo.py','requirements-models.txt','LICENSE'} <= set(archive.namelist())
    assert not any(name.startswith('/') or '..' in Path(name).parts or '__pycache__' in name for name in archive.namelist())
from course_pages import load as load_courses
course_units = [unit for course in load_courses() for unit in course['units']]
assert len({unit['study_id'] for unit in course_units}) == len(course_units)
print('Course schemas/DAG/IDs, project ZIP and private-artifact exclusions: pass')
search_manifest=json.loads((SITE/'search/manifest.json').read_text())
search_entries=[row for shard in search_manifest['shards'] for row in json.loads((SITE/shard['url']).read_text())]
assert {unit['study_id'] for unit in course_units} <= {row['id'] for row in search_entries}, 'Course units absent from global search'
for unit in course_units:
    text=(SITE/('course-'+unit['id']+'.html')).read_text()
    assert 'Technical interview and design defense' in text and unit['worked_examples'][0]['title'] in text
    from html import escape
    assert escape((ROOT/'labs'/unit['lab']).read_text(),quote=True) in text, 'Course lab source was altered or omitted'
    if unit.get('source_context'):assert 'How the references inform this unit' in text
    if unit.get('project'):assert 'project-'+unit['project']+'.html' in text
with zipfile.ZipFile(SITE/'examples/local-projects.zip') as archive:
    assert 'labs/streaming_reader.html' in archive.namelist()
from editorial import content_digest, validate_review
review_fixture={'Q':'Attestation fixture','A':'Original answer','reviewer_status':{'status':'reviewed','reviewer':'Fixture reviewer','reviewed_at':'2026-10-20'}}
proof={'fixture':{'sha256':content_digest(review_fixture),'reviewer':'Fixture reviewer','reviewed_at':'2026-10-20','review_notes':'Synthetic test only'}}
validate_review(review_fixture,'fixture',proof)
for candidate, attestations in ((review_fixture,{}),({**review_fixture,'A':'Changed after review'},proof)):
    try:validate_review(candidate,'fixture',attestations)
    except ValueError:pass
    else:raise AssertionError('Missing or stale editorial attestation accepted')
print('Missing/stale editorial attestation regressions: pass')

for project in ('evidence-workbench','review-packet'):
    assert (SITE/('project-'+project+'.html')).is_file()
    with zipfile.ZipFile(SITE/('examples/projects/'+project+'.zip')) as archive:
        names=archive.namelist()
        assert len(names)==len(set(names)) and 'projects/'+project+'/README.md' in names
        assert not any(set(Path(name).parts) & {'node_modules','dist','__pycache__','.git'} for name in names)
        if project=='evidence-workbench':
            assert {'projects/evidence-workbench/package-lock.json','projects/evidence-workbench/src/App.tsx','projects/evidence-workbench/server.py'} <= set(names)
print('Cumulative project downloads and dependency/build exclusions: pass')

# The learning journey owns discovery. Removing duplicate index pages must not
# strand the unique worked units, projects or inline transition simulations.
retired_pages = {'courses.html', 'capstones.html', 'simulations.html', 'question-bank.html', 'topic-coverage.html'}
assert not any((SITE/name).exists() for name in retired_pages)
assert not list(SITE.glob('questions-*.html')), 'Answers must have one canonical chapter page'
curriculum = json.loads((ROOT/'content/curriculum.json').read_text())['chapters']
placements = {}
for slug, entry in curriculum.items():
    for identity in entry.get('course_units', []):
        assert identity not in placements, ('ambiguous unit placement', identity)
        placements[identity] = slug
        assert 'course-'+identity+'.html' in (SITE/(slug+'.html')).read_text()
assert set(placements) == {unit['id'] for unit in course_units}, 'A unique worked unit lost its chapter entry point'
for identity, slug in {'asyncio':'sources', 'locking':'database-concurrency', 'retrieval':'foundations', 'retries':'agent-evaluation'}.items():
    assert 'data-simulation="'+identity+'"' in (SITE/(slug+'.html')).read_text()
portfolio = (SITE/'portfolio-capstone.html').read_text()
for identity in ('async-engine', 'transaction-api', 'rag-quality', 'durable-agent'):
    assert 'capstone-'+identity+'.html' in portfolio
print('Single learning journey: retired duplicate pages absent; every unit, project and simulation remains reachable')
