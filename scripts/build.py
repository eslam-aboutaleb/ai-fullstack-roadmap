"""Build a progressively ordered course; topic depth follows content, never a quota."""
from pathlib import Path
import ast,html,json,os,re,shutil,textwrap,hashlib
from course_data import load,STAGES
from examples import EXAMPLES
from rich_content import lesson_content, question_content
from answer_format import AnswerWriter, prose as answer_prose, answer_diagram, validate_diagrams, VISUALS, normalize as normalize_answer
from learning_navigation import question_finder, scenario_page
from interview_teaching import answer_terms, teaching_title, ACRONYMS
from question_examples import load_question_examples
from learning_pages import build as build_learning_pages, load_practice
from question_bank import build as build_question_bank, search_shards
from course_pages import build as build_course_pages, load as load_courses
from curriculum_audit import build as build_curriculum_audit
from learning_blueprint import build as build_learning_blueprint
from simulation_pages import build as build_simulations, panel as simulation_panel, CHAPTERS as SIMULATION_CHAPTERS
HERE=Path(__file__).resolve().parent;REPOSITORY=HERE.parent;CONTENT=REPOSITORY/'content';ROOT=REPOSITORY/'_build'
CHAPTERS=load();BY={c['slug']:c for c in CHAPTERS}
CURRICULUM=json.loads((CONTENT/'curriculum.json').read_text())
QUESTION_RECIPES,QUESTION_CODE=load_question_examples(CHAPTERS)
IDS=[q['id'] for c in CHAPTERS for q in c['questions']+c['lessons']]
TOTAL=len(IDS)
COURSE_STUDY_IDS=[unit['study_id'] for course in load_courses() for unit in course['units']]
STUDY_TOTAL=len(IDS)+len(COURSE_STUDY_IDS);MAX_ID=max(IDS+COURSE_STUDY_IDS)
E=lambda x:html.escape(str(x),quote=True)
PRACTICE, BROWSER_LABS = load_practice(CHAPTERS)
PRACTICE_BY_TOPIC = {item['topic']:item for item in PRACTICE}
CODE_NOTES={c['slug']:json.loads((CONTENT/'chapters'/c['slug']/'code-notes.json').read_text()) for c in CHAPTERS}

BASE_PATH=os.environ.get('PAGES_BASE_PATH','')
if BASE_PATH and not BASE_PATH.startswith('/'):
    BASE_PATH='/'+BASE_PATH
if BASE_PATH and not BASE_PATH.endswith('/'):
    BASE_PATH=BASE_PATH+'/'
def url(path):
    if not path or path.startswith(('http://','https://','#','mailto:')):
        return path
    # Flat relative URLs work under Pages subpaths and downloaded file:// reading.
    return path
def asset(name):
    return url(name+"?v="+hashlib.sha256((ROOT/name).read_bytes()).hexdigest()[:10])

def term_id(name):
 return 'term-'+hashlib.sha256(name.encode()).hexdigest()[:12]

def paragraphs(text):
 sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',text)
 return ''.join('<p>'+E(' '.join(sentences[i:i+2]))+'</p>' for i in range(0,len(sentences),2))

def shell(title,body,active='',search=False):
 current=BY.get(active);stage=current['stage'] if current else 1
 nav=''
 for n,(label,level,summary,slugs) in enumerate(STAGES,1):
  entries=''.join(f'<a href="{url(slug+".html")}" {"aria-current=page" if active==slug else ""}><span>{CHAPTERS.index(BY[slug])+1:02}</span>{E(BY[slug]["title"])}</a>' for slug in slugs)
  nav+=f'<details class="nav-stage" {"open" if n==stage else ""}><summary><span>{n:02}</span>{E(label)}</summary>{entries}</details>'
 search_tag='<script src="'+asset('search-loader.js')+'" defer></script>'
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Learn AI engineering through explained lessons, interactive diagrams, worked examples, practical labs, and interview practice."><title>{E(title)} · AI Engineering Roadmap</title><link rel="icon" type="image/svg+xml" sizes="any" href="{asset('favicon.svg')}"><link rel="stylesheet" href="{asset('style.css')}">{search_tag}<script src="{asset('highlight.js')}" defer></script><script src="{asset('study-model.js')}" defer></script><script src="{asset('study-store.js')}" defer></script><script src="{asset('app.js')}" defer></script><script src="{asset('course.js')}" defer></script></head><body data-page="{active}" data-question-count="{MAX_ID}" data-topic-count="{STUDY_TOTAL}"><a class="skip" href="{url('#main')}">Skip to lesson</a><aside class="sidebar" id="navigation"><a class="brand" href="{url('index.html')}"><b>ai<span>/</span></b><strong>ENGINEERING<br><small>THE LEARNING ROADMAP</small></strong></a><nav class="utility-nav" aria-label="Course tools"><a href="{url('index.html')}">Learning journey</a><a href="{url('index.html')}#search">Search all topics</a><a href="{url('curriculum-map.html')}">Curriculum map</a><a href="{url('courses.html')}">Engineering courses</a><a href="{url('capstones.html')}">Capstones</a><a href="{url('simulations.html')}">System visualizers</a><a href="{url('coding-labs.html')}">Coding labs</a><a href="{url('assessments.html')}">Assessments</a><a href="{url('question-bank.html')}">Question bank</a><a href="{url('topic-coverage.html')}">Topic coverage</a><a href="{url('study.html')}">My study record</a><a href="{url('roadmap.html')}">Project experiments</a><a href="{url('glossary.html')}">Terminology guide</a><a href="{url('examples.html')}">Code studio</a><a href="{url('design-scenarios.html')}">Design scenarios</a></nav><p class="nav-label">YOUR LEARNING PATH</p><nav aria-label="Learning stages">{nav}</nav><div class="sidebar-foot"><small>Explain it. Build it. Test a failure.</small></div></aside><div class="workspace"><header class="toolbar"><button type="button" id="menu-toggle" aria-controls="navigation" aria-expanded="false">Course menu</button><a href="{url('index.html')}#search">Find a topic <kbd>/</kbd></a><span class="toolbar-context">{E(STAGES[current['stage']-1][0] if current else 'A course built around understanding')}</span><button type="button" id="theme">Change theme</button><button type="button" id="distraction-free">Focus mode</button></header><main id="main" tabindex="-1">{body}</main><footer>AI Full-Stack Engineering Roadmap · Fictional examples; no model API needed to read the course. <a href="{url('provenance.html')}">About this edition</a> · <a href="{url('libraries.html')}">References</a> · <a href="{url('LICENSE')}" rel="license">MIT license</a></footer></div></body></html>'''

def write(name,title,body,active='',search=False):
 body=re.sub(r'<pre(?![^>]*\btabindex=)', '<pre tabindex="0"', body)
 (ROOT/name).write_text(shell(title,body,active,search))

def bookmark_control(q):
 label='Bookmark question: '+teaching_title(q) if q.get('Q') else 'Bookmark this unit'
 return f'<button class="bookmark" type="button" data-bookmark="{q["id"]}" aria-pressed="false" aria-label="{E(label)}">Bookmark</button>'


def question_heading(q,tag):
 return f'<div class="question-heading"><{tag}>{E(teaching_title(q))}</{tag}>{bookmark_control(q)}</div>'


def controls(q,include_bookmark=True):
 i=q['id']
 practice_link = f'<a href="{url("assessments.html")}#a-{PRACTICE_BY_TOPIC[i]["id"]}">Test this skill →</a>' if i in PRACTICE_BY_TOPIC else ''
 bookmark='<div class="study-controls">'+bookmark_control(q)+'</div>' if include_bookmark else ''
 return f'''{practice_link}{bookmark}<details class="notes"><summary>Write my explanation</summary><label for="note-{i}">Explain this using your own example</label><textarea id="note-{i}" data-note="{i}" rows="3" placeholder="What goes in? What happens? What comes out? What could fail?"></textarea></details>'''

def question_code(q):
 e=QUESTION_CODE.get(q['id'])
 if e is None:
  return ''
 language=e['language'];runnable=language=='python' or bool(e.get('execute')) or bool(e.get('local_executable'))
 label=('Python' if language=='python' else 'JavaScript')+' · offline example' if runnable else language.replace('-sketch',' integration sketch')
 label=e.get('runtime_label',label)
 default_scope={
  'python':'Run this self-contained example with Python 3.10+. It uses synthetic fixtures and the standard library; it does not connect to a provider or establish a production guarantee.',
  'javascript':'Run this local JavaScript fixture with Node.js or the documented browser context. External integrations require their stated host configuration.',
  'python-sketch':'Python integration sketch requiring the documented dependencies and surrounding application.',
  'sql':'SQL example requiring its declared database engine and schema; dialect and transaction behavior are part of that contract.',
  'json':'Structured case data. Parsing checks its representation, not the behavior of the system it describes.',
  'bash':'Shell integration commands requiring the documented tools and environment.',
  'html':'Browser example requiring the documented page and hosting context.',
  'dockerfile':'Container build configuration requiring the documented build context and container runtime.'
 }[language]
 scope=e.get('limit',default_scope)
 steps=''.join('<li>'+answer_prose(step)+'</li>' for step in e['steps'].split(' || '))
 expected='<pre class="example-output"><code>'+E(e['expect'])+'</code></pre>' if runnable else '<p class="example-output">'+E(e['expect'])+'</p>'
 reference=f'<p><a href="{E(e["reference"])}">Check the primary reference for this example →</a></p>' if e.get('reference') else ''
 change=e.get('change','Change one fixture value or boundary condition, predict the result, and rerun or inspect the example. Explain which step changes the outcome.')
 result=f'''<section class="question-code" id="code-q{q['id']}" data-code-example="{E(e['name'])}" aria-labelledby="code-title-q{q['id']}"><span class="micro-label">EXPLAIN IT WITH CODE / {E(label)}</span><h4 id="code-title-q{q['id']}">What this code does</h4>{answer_prose(e['explain'])}<div class="code-panel"><button type="button" class="copy" aria-live="polite" aria-label="Copy code for {E(q['Q'])}">Copy code</button><pre><code class="language-{E(language)}">{E(e['code'])}</code></pre></div><h4>Read it step by step</h4><ol class="code-walkthrough">{steps}</ol><h4>{'Expected output' if runnable else 'Expected behavior'}</h4>{expected}<p class="code-scope"><strong>How to use it:</strong> {E(scope)}</p><p><strong>Try a change:</strong> {E(change)}</p><p><a href="{url('examples/questions/'+E(e['filename']))}">Open the example file →</a></p>{reference}</section>'''

 return '<details class="case-data"><summary>Inspect the case data</summary>'+result+'</details>' if language=='json' else result

def reading_minutes(c):
  words=sum(len(str(q.get(k,'')).split()) for q in c['lessons']+c['questions'] for k in ('Q','explain','example','takeaway','A','Why','Risk','Trade','Try'))
  return max(1,round(words/180))
def lesson(q,i):
  writer=AnswerWriter(q)
  explanation=writer.render(q['explain'])
  case=writer.render(q['example'])
  return f'''<article class="lesson question" id="q{q['id']}" data-question="{q['id']}"><div class="lesson-kicker">FOUNDATION QUESTION / {i:02}</div>{question_heading(q,"h2")}<details class="answer"><summary class="answer-toggle" role="button"><span class="when-closed">View answer</span><span class="when-open">Hide answer</span></summary><div class="answer-body">{explanation}{answer_diagram(q)}{('<aside class="worked-case"><h4>Worked example</h4>'+case+'</aside>') if case else ''}<p class="takeaway"><strong>Keep this idea:</strong> {E(q['takeaway'])}</p>{lesson_content(q,url,writer)}{rigorous_lesson(q)}{question_code(q)}{answer_terms(q)}</div></details>{controls(q,include_bookmark=False)}</article>'''

def rigorous_lesson(q):
  parts=[]
  if q.get('outcomes'): parts.append(f'<h3>Learning outcomes</h3><ul class="outcomes">'+''.join('<li>'+E(o)+'</li>' for o in q['outcomes'])+'</ul>')
  if q.get('assumed_knowledge'): parts.append(f'<h3>Assumed knowledge</h3><p>'+E(q['assumed_knowledge'])+'</p>')
  if q.get('motivating_problem'): parts.append(f'<h3>Motivating production problem</h3><p>'+E(q['motivating_problem'])+'</p>')
  if q.get('conceptual_model'): parts.append(f'<h3>Conceptual model</h3><p>'+E(q['conceptual_model'])+'</p>')
  if q.get('underlying_mechanics'): parts.append(f'<h3>Underlying mechanics</h3><p>'+E(q['underlying_mechanics'])+'</p>')
  if q.get('line_by_line'): parts.append(f'<h3>Read it line by line</h3><ol>'+''.join('<li>'+E(l)+'</li>' for l in q['line_by_line'])+'</ol>')
  if q.get('edge_cases'): parts.append(f'<h3>Edge cases</h3><ul>'+''.join('<li>'+E(e)+'</li>' for e in q['edge_cases'])+'</ul>')
  if q.get('tradeoffs'): parts.append(f'<h3>Trade-offs</h3><p>'+E(q['tradeoffs'])+'</p>')
  if q.get('security_implications'): parts.append(f'<h3>Security implications</h3><p>'+E(q['security_implications'])+'</p>')
  if q.get('performance_implications'): parts.append(f'<h3>Performance implications</h3><p>'+E(q['performance_implications'])+'</p>')
  if q.get('debugging'): parts.append(f'<h3>Debugging</h3><p>'+E(q['debugging'])+'</p>')
  if q.get('practice'): parts.append(f'<h3>Practice</h3><p>'+E(q['practice'])+'</p>')
  if q.get('recap'): parts.append(f'<h3>Recap</h3><p>'+E(q['recap'])+'</p>')
  if q.get('mastery_checks'): parts.append(f'<h3>Mastery checks</h3><ul>'+''.join('<li>'+E(m)+'</li>' for m in q['mastery_checks'])+'</ul>')
  if not parts: return ''
  return '<details class="rigorous"><summary>Rigorous authoring detail</summary><div class="rigorous-body">'+''.join(parts)+'</div></details>'

def interview(q):
  writer=AnswerWriter(q)
  body=writer.render(q['A'],reserve_followups=True)
  body+=answer_diagram(q)
  if normalize_answer(q['Why']) not in writer.followups:
    body+=writer.section('Worked case' if q.get('answer_format')=='conceptual' else 'How it works',q['Why'],'answer-mechanism')
  body+=writer.section('Failure boundary',q['Risk'],'answer-warning')
  if normalize_answer(q['Trade']) not in writer.followups:
    body+=writer.section('Design trade-off',q['Trade'],'answer-decision')
  body+=question_content(q,writer)
  body+=question_code(q)
  for follow in q.get('follow_ups',[]):
    body+=writer.section(follow['Q'],follow['A'],'answer-followup')
  definitions=[]
  for definition in q.get('definitions',[]):
    explanation=writer.render(definition['definition'])
    if explanation:definitions.append('<dt>'+E(definition['term'])+'</dt><dd>'+explanation+'</dd>')
  if definitions:body+='<section class="answer-definitions"><h4>Terminology</h4><dl>'+''.join(definitions)+'</dl></section>'
  body+=answer_terms(q)
  body+=writer.section('Try it yourself',q['Try'],'answer-exercise')
  references=list(dict.fromkeys(([q['reference']] if q.get('reference') else [])+q.get('citations',[])))
  if references:body+='<section class="answer-references"><h4>Primary references</h4><ul>'+''.join('<li><a href="'+E(ref)+'">'+E(ref)+'</a></li>' for ref in references)+'</ul></section>'
  if q.get('reviewer_status'):
    review=q['reviewer_status']
    body+='<p class="editorial-status"><strong>Editorial status: '+E(review['status'])+'</strong> · '+E(review['reviewer'])+'</p>'
  return f'''<article class="interview-question" id="q{q['id']}" data-question="{q['id']}">{question_heading(q,"h3")}<p class="question-meta">{E(' · '.join(q[k] for k in ('difficulty','domain') if q.get(k)))}</p><details class="answer"><summary class="answer-toggle" role="button"><span class="when-closed">View answer</span><span class="when-open">Hide answer</span></summary><div class="answer-body">{body}</div></details>{controls(q,include_bookmark=False)}</article>'''

def diagram(c):
 nodes=c['flow'];width=1100;gap=25;box=(width-20-gap*(len(nodes)-1))/len(nodes);parts=[]
 for i,(name,value) in enumerate(nodes):
  x=10+i*(box+gap);cx=x+box/2
  labels=textwrap.wrap(name,18)
  text=''.join(f'<tspan x="{cx}" dy="{0 if j==0 else 20}">{E(t)}</tspan>' for j,t in enumerate(labels))
  parts.append(f'<g data-diagram-step="{i}" class="flow-node {"active" if i==0 else ""}"><rect x="{x}" y="15" width="{box}" height="102" rx="14"/><text x="{cx}" y="39" class="node-number">0{i+1}</text><text x="{cx}" y="{68 if len(labels)==1 else 61}" class="node-title">{text}</text></g>')
  if i<len(nodes)-1:parts.append(f'<path d="M{x+box+4} 66 h{gap-9}" marker-end="url(#arrow-{c["slug"]})" class="flow-arrow"/>')
 mobile='<ol class="mobile-flow" aria-label="Example flow in order">'+''.join(f'<li data-diagram-step="{i}" class="{"active" if i==0 else ""}"><span>{i+1:02}</span><strong>{E(name)}</strong></li>' for i,(name,value) in enumerate(nodes))+'</ol>'
 buttons=''.join(f'<button type="button" data-flow-step="{i}" data-title="{E(name)}" data-value="{E(value)}" aria-pressed="{str(i==0).lower()}">{i+1}. {E(name)}</button>' for i,(name,value) in enumerate(nodes))
 return f'''<section class="concept-lab" id="walkthrough" data-flow><div class="section-title"><div><span class="micro-label">SEE IT HAPPEN</span><h2>Follow the example through the system</h2></div><span class="interactive-badge">INTERACTIVE WALKTHROUGH</span></div><p>{E(c['case'][0])}</p><div class="flow-canvas"><svg viewBox="0 0 {width} 135" role="img" aria-labelledby="diagram-title-{c['slug']}"><title id="diagram-title-{c['slug']}">{E(c['goal'])}: {E(' → '.join(n for n,v in nodes))}</title><defs><marker id="arrow-{c['slug']}" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6"/></marker></defs>{''.join(parts)}</svg></div>{mobile}<details><summary>Read the complete walkthrough transcript</summary><ol>{''.join('<li><strong>'+E(name)+'</strong>: '+E(value)+'</li>' for name,value in nodes)}</ol><p><strong>Failure case:</strong> {E(c['case'][2])}</p></details><div class="flow-buttons" role="group" aria-label="Choose a step">{buttons}</div><div class="trace-output" aria-live="polite"><span class="micro-label" data-flow-label>STEP 1 / {E(nodes[0][0])}</span><p data-flow-result>{E(nodes[0][1])}</p><p class="trace-meaning" data-flow-meaning>{E(c['case'][1])}</p></div><div class="flow-controls"><button type="button" data-flow-next>Next step →</button><button type="button" data-flow-fail aria-pressed="false">What if this goes wrong?</button></div><p data-flow-failure hidden class="failure-note">{E(c['case'][2])}</p></section>'''

def code_panel(c):
 e=EXAMPLES[c['slug']];extension={'python':'.py','sql':'.sql','markdown':'.md','javascript':'.js','html':'.html'}[e['language']]
 assertions=[]
 if e['language']=='python':
  tree=ast.parse(e['code']);assertions=[ast.unparse(n.test) for n in ast.walk(tree) if isinstance(n,ast.Assert)]
 proof=''.join('<li><code>'+E(x)+'</code></li>' for x in assertions[:3])
 notes='<ol>'+''.join('<li>'+E(note)+'</li>' for note in CODE_NOTES[c['slug']])+'</ol>'
 proof=f'<p>The assertions below state the behavior this small example checks. Read the inputs and expected result, then change one input and predict whether the check will still pass.</p><ul class="assertions">{proof}</ul>' if proof else '<p>This integration sketch needs the compatible dependencies and host configuration described in its scope. It is not an automatically running service in this website.</p>'
 return f'''<section class="code-studio" id="chapter-example"><div class="section-title"><div><span class="micro-label">FROM IDEA TO CODE</span><h2>How does a small implementation work?</h2></div><span>{E(e['language'])}</span></div><p>{E(e['scope'])}</p><div class="code-reading"><p><strong>What this demonstrates:</strong> {E(c['goal'])}.</p><p><strong>Connect it to the case:</strong> {E(c['case'][0])} {E(c['case'][1])}</p></div><div class="code-panel"><button type="button" class="copy" aria-live="polite">Copy code</button><pre><code>{E(e['code'])}</code></pre></div><details open class="code-explanation"><summary>How to read and test this code</summary>{notes}{proof}<p><strong>The boundary to investigate:</strong> {E(c['case'][2])}</p><p><strong>Next change to make:</strong> {E(c['questions'][0]['Try'])}</p></details><a href="{url('examples/'+c['slug']+extension)}">Open the teaching file →</a></section>'''

def lab(c,identifier="chapter-lab"):
 return f'''<section class="chapter-lab" id="{identifier}"><span class="micro-label">BUILD / BREAK / EXPLAIN</span><h2>Turn this chapter into a working experiment</h2><p>{E(c['case'][0])}</p><ol><li><strong>Build the normal path.</strong> {E(c['questions'][0]['Try'])}</li><li><strong>Introduce the failure.</strong> {E(c['case'][2])}</li><li><strong>Verify recovery.</strong> Record what the user sees and what authoritative state remains.</li><li><strong>Defend a trade-off.</strong> {E(c['questions'][-1]['Trade'])}</li></ol><p class="takeaway">Bring back a small implementation, observed input/output, one failure demonstration, and your own explanation.</p></section>'''

def review_panel(c):
  r=c['review'];extra=''
  if r.get('capstone'):
    cap=r['capstone']
    phases=''.join(f'<div class="capstone-phase"><h4>{E(p["name"])}</h4><ul>'+''.join('<li>'+E(s)+'</li>' for s in p['steps'])+'</ul><p class="capstone-verify"><strong>Verify:</strong> '+E(p['verify'])+'</p></div>' for p in cap['phases'])
    prereqs=''.join(f'<a href="{url(p+".html")}">{E(BY[p]["title"])}</a>' for p in cap['prerequisite_chapters'])
    extra=f'''<section class="capstone-project"><h2>{E(cap["title"])}</h2><p>{E(cap["description"])}</p>{phases}<p><strong>Builds on:</strong> {prereqs}</p><p><strong>Deliverables:</strong> {', '.join(E(a) for a in cap['artifacts'])}</p></section>'''
  return f'''<aside class="worked-case" id="review-notes" aria-label="Content review notes"><span class="micro-label">REVIEW NOTES / ADDED LEARNING SUPPORT</span><h2>What to strengthen in this chapter</h2>{paragraphs(r['review'])}<p>The original material is retained. The additional explanations below connect the idea to implementation; use the deeper questions after you can explain the example.</p>{extra}<a href="#recommended-practice">Try the recommended extension and completion checks →</a></aside>'''

def review_practice(c):
 r=c['review']
 links=''.join(f'<li><a href="{E(url)}">{E(name)}</a></li>' for name,url in r['references'])
 for filename in r.get('labs',[]):
  if Path(filename).name!=filename or not (REPOSITORY/'labs'/filename).is_file():raise ValueError('Unknown chapter lab: '+filename)
  links+='<li><a href="'+url('examples/labs/'+filename)+'">Download '+E(filename)+'</a></li>'
 if c['slug'] in {'foundations','models','database-modeling','embeddings','retrieval','evaluation'}:
  links='<li><a href="'+url('examples/labs/foundation_bridge.py')+'">Run the offline foundation bridge: gradient, cosine, metrics, and SQL</a> — Python 3.10+, standard library only; save the file and run <code>python foundation_bridge.py</code>.</li>'+links
 return f'''<section class="chapter-lab" id="recommended-practice"><span class="micro-label">ADDITIONAL PRACTICE / CHECK THE RESULT</span><h2>Extend the experiment</h2>{paragraphs(r['build'])}<h3>Observable completion checks</h3>{paragraphs(r['verify'])}<p>Keep the command, fixture version, observed result, one failure case, and your trade-off explanation with your implementation. These are exercises to implement; their presence does not mean the described production behavior has already been built.</p><h3>Primary references</h3><p>Use the reference matching your installed version for exact API details. The explanations and worked cases in this course provide the learning path; references support implementation and further study.</p><ul>{links}</ul></section>'''

def coverage_review():
 rows=[
  ('Programming and reproducibility','The entry lessons assumed the ability to run and inspect code.','foundations','Added runtime setup, functions and collections, debugging, Git, and a clean-checkout exercise.'),
  ('Web and frontend engineering','Realtime behavior was better explained than the ordinary interface underneath it.','application-architecture','Added HTTP, JSON, JavaScript promises, types, data structures, and a fake-provider vertical slice. See product delivery for HTML, CSS, component state, forms, race handling, and accessibility.'),
  ('ML foundations','Training and model choice needed numerical examples before advanced terminology.','models','Added a gradient update, supervised-learning baselines, precision and recall, data leakage, attention shapes, and adaptation/serving experiments in model engineering.'),
  ('Data and retrieval','Correct mechanisms needed more worked calculations and recovery criteria.','database-modeling','Added SQL relationships, schema compatibility, concurrency races, source deletion, ingestion publication, vector similarity, fusion arithmetic, and per-slice retrieval checks.'),
  ('Agent and protocol engineering','Framework examples needed a plain-code baseline and compatibility discipline.','agent-harness','Added controlled loops, unknown effect reconciliation, replay-safe nodes, delegated scope, bounded tools, and version-pinned contract exercises.'),
  ('Testing and evidence','Broad experiments needed observable outcomes and an independent oracle.','evaluation','Added metric arithmetic, layered deterministic tests, effect-ledger checks, paired comparisons, uncertainty, and portable evaluation records.'),
  ('Delivery and operations','Readiness guidance needed an executable delivery and recovery plan.','deployment-reliability','Added container/state boundaries, CI artifacts, secrets, gradual rollout, recovery and capacity arithmetic, quotas, and capstone handoff requirements.')]
 table=''.join(f'<tr><th scope="row">{E(area)}</th><td>{E(gap)}</td><td><a href="{url(slug+".html")}#review-notes">{E(added)}</a></td></tr>' for area,gap,slug,added in rows)
 chapters=''.join(f'<section class="map-card"><h3><a href="{url(c["slug"]+".html")}#review-notes">{E(c["title"])}</a></h3>{paragraphs(c["review"]["review"])}<p><strong>Recommended work:</strong> {E(c["review"]["build"])}</p><p><strong>Completion evidence:</strong> {E(c["review"]["verify"])}</p></section>' for c in CHAPTERS)
 return f'''<section class="prose" id="content-review"><p class="eyebrow">CONTENT REVIEW / 19 OCTOBER 2026</p><h2>Use the course as a central learning path</h2><p>The original AI-focused chapters provide particularly strong coverage of retrieval, evidence, agent boundaries, and realtime behavior. The review found thinner explanations of prerequisite programming, ordinary frontend development, mathematical learning steps, and how to verify a completed implementation. The additions address those gaps within the existing chapters and preserve the original lessons and study identifiers.</p><p>Study one sequence: understand the explanation, trace the example, implement it, reproduce a failure, and defend a trade-off. Questions are not assigned experience levels. If you already know a concept, demonstrate its completion checks and continue into the deeper material.</p><p>This can organize your learning in one place, but reading the pages alone cannot establish full-stack engineering competence. SDK sketches are not complete deployed services, proposed exercises are not measured results, and some projects need optional dependencies or provider access. Operating a project, collaborating in review, and responding to real incidents remain necessary practice. Use primary references for version-specific implementation details.</p></section><div class="table-scroll" role="region" aria-label="Coverage comparison" tabindex="0"><table><caption>Coverage gaps and additions</caption><thead><tr><th scope="col">Responsibility</th><th scope="col">Gap found</th><th scope="col">Addition and starting chapter</th></tr></thead><tbody>{table}</tbody></table></div><section class="prose"><h2>A practical route through the additions</h2><ol><li>Begin with Programming foundations, Computer science, Web fundamentals and Frontend foundations. Build a deterministic form-to-result path before paying for model calls.</li><li>Work through model mathematics and a small training experiment, then build the authorized data and retrieval path using synthetic fixtures.</li><li>Connect one provider and evaluate it against the baseline. Add agents only for tasks that benefit from choosing tools dynamically.</li><li>Use Frontend foundations before Product delivery, then extend the same task to streaming, voice, or remote agents. Treat alternative frameworks as comparisons rather than a mandatory combined stack.</li><li>Finish with the delivery pipeline, recovery drill, and capstone handoff. Revisit the first boundary you cannot demonstrate without following the page.</li></ol><p><a href="{url("programming-foundations.html")}#review-notes">Start programming foundations →</a> · <a href="{url("product-delivery.html")}#review-notes">Open frontend practice →</a> · <a href="{url("portfolio-capstone.html")}#recommended-practice">Check the final handoff →</a></p><h2>Chapter-by-chapter findings and recommendations</h2></section>{chapters}'''

def rag_playground():
 return '''<section class="rag-playground" data-rag-playground><div class="section-title"><div><span class="micro-label">CHANGE ONE INPUT / OBSERVE THE CONSEQUENCE</span><h2>What can this evidence support?</h2></div></div><p>The customer's question stays the same: <strong>Can I get a refund for a sale item?</strong> Change what retrieval supplies and see why the next action changes.</p><label for="rag-scenario">Evidence returned by the search</label><select id="rag-scenario"><option value="supported">The actual sale-item rule</option><option value="irrelevant">An unrelated shipping article</option><option value="missing">No matching passage</option><option value="outage">Search service unavailable</option></select><div class="scenario-result" aria-live="polite"><span class="micro-label">THE READING PACKET</span><pre><code id="rag-packet"></code></pre><span class="micro-label">THE SUPPORTED NEXT ACTION</span><p id="rag-action"></p><p class="takeaway" id="rag-reason"></p></div><small>Deterministic teaching simulation. These outcomes illustrate an evidence policy; no model is being called.</small></section>'''

def public_lab_ignore(directory,names):
 allowed={'.py','.js','.md','.json','.txt','.toml','.yaml','.yml','.sql','.html','.css','.csv','.ipynb'}
 return [name for name in names if name.startswith('.') or name in {'__pycache__','node_modules'} or (Path(directory)/name).is_symlink() or ((Path(directory)/name).is_file() and (Path(name).suffix not in allowed))]


def build():
 from validate_curriculum import validate
 validate()
 validate_diagrams(CHAPTERS)
 if ROOT.exists():shutil.rmtree(ROOT)
 ROOT.mkdir()
 (ROOT/'.nojekyll').write_text('')
 shutil.copy2(REPOSITORY/'LICENSE',ROOT/'LICENSE')
 for source in (REPOSITORY/'assets').glob('*/*'):
  if source.is_file():shutil.copy2(source,ROOT/source.name)
 for directory in ('diagrams','examples','sources'):
  path=ROOT/directory
  if path.exists():shutil.rmtree(path)
  if directory!='sources':path.mkdir()
 for p in ROOT.glob('*.html'):p.unlink()
 shutil.copytree(CONTENT/'runtime', ROOT/'runtime')
 if (REPOSITORY/'vendor/pyodide/runtime-manifest.json').exists():
  from vendor_pyodide import FILES, VERSION
  source_runtime=REPOSITORY/'vendor/pyodide';runtime_manifest=json.loads((source_runtime/'runtime-manifest.json').read_text())
  if runtime_manifest.get('version')!=VERSION:raise ValueError('Runtime version mismatch; rerun make runtime')
  (ROOT/'runtime/pyodide').mkdir()
  for runtime_name in FILES:
   runtime_file=source_runtime/runtime_name
   if hashlib.sha256(runtime_file.read_bytes()).hexdigest()!=runtime_manifest['files'].get(runtime_name):raise ValueError('Runtime integrity mismatch: '+runtime_name)
   shutil.copy2(runtime_file,ROOT/'runtime/pyodide'/runtime_name)
  shutil.copy2(source_runtime/'runtime-manifest.json',ROOT/'runtime/pyodide/runtime-manifest.json')
 for stem in ('context','harness','streaming','quality'):
  text=(CONTENT/'diagrams'/f'{stem}.html').read_text()
  text=re.sub(r'<button\b[^>]*\bdata-print\b[^>]*>.*?</button>','',text,flags=re.S)
  text=text.replace("item=>item.matches('[data-print]') ? window.print() : exportImage(item.dataset.exportImage)","item=>exportImage(item.dataset.exportImage)")
  text=re.sub(r'"sourcePath":"[^"]*"','"sourcePath":"content/diagrams/'+stem+'.archify.md"',text)
  text=re.sub(r'<link\b[^>]*\brel=["\x27](?:shortcut )?icon["\x27][^>]*>', '', text)
  text=text.replace('</head>','<link rel="icon" type="image/svg+xml" sizes="any" href="../favicon.svg"></head>',1)
  text=re.sub(r'"baseDir":"[^"]*"','"baseDir":"content/diagrams"',text)
  (ROOT/'diagrams'/f'{stem}.html').write_text(text)
 search=[]
 for c in CHAPTERS:
  for q in c['lessons']:
   search.append(dict(id=q['id'],slug=c['slug'],chapter=c['title'],title=teaching_title(q),type='Foundation interview',text=' '.join(q[k] for k in ('Q','explain','example','takeaway'))+' '+QUESTION_CODE.get(q['id'],{}).get('explain','')+' '+QUESTION_CODE.get(q['id'],{}).get('code','')))
  for q in c['questions']:
   search.append(dict(id=q['id'],slug=c['slug'],chapter=c['title'],title=teaching_title(q),type='Interview depth',text=' '.join(q[k] for k in ('Q','A','Why','Risk','Trade','Try'))+' '+QUESTION_CODE.get(q['id'],{}).get('explain','')+' '+QUESTION_CODE.get(q['id'],{}).get('code','')))
 _,bank_pages=build_question_bank(ROOT,CHAPTERS,interview,write,url)
 for entry in search:
  entry['href']=entry['slug']+'.html#q'+str(entry['id'])
  entry['text']=entry['text'][:2200]
 for course in load_courses():
  for unit in course['units']:
   search.append(dict(id=unit['study_id'],slug='course-'+course['id'],track='courses',chapter=course['title'],title=unit['title'],type='Engineering course',href='course-'+unit['id']+'.html',text=(' '.join([unit['title'],*unit['outcomes'],*[item['question'] for item in unit['interviews']],*unit['narrative']]))[:2200]))
 search_shards(ROOT,search,CURRICULUM)

 write('design-scenarios.html','Advanced system-design scenarios',scenario_page(CHAPTERS,url))
 for position,c in enumerate(CHAPTERS):
  previous=CHAPTERS[position-1] if position else None;following=CHAPTERS[position+1] if position+1<len(CHAPTERS) else None
  prerequisites=' · '.join(f'<a href="{url(slug+".html")}">{E(BY[slug]["title"])}</a>' for slug in CURRICULUM['chapters'][c['slug']]['prerequisites']) or 'No prerequisite chapters. Start here.'
  terms=''.join(f'<div><dt><a href="{url("glossary.html")}#{term_id(name)}">{E(name)}</a></dt><dd>{E(meaning)}</dd></div>' for name,meaning in c['terms'])
  mins=reading_minutes(c)
  toc=''.join(f'<a href="#q{q["id"]}">{i}. {E(teaching_title(q))}</a>' for i,q in enumerate(c['lessons'],1))
  lessons=''.join(lesson(q,i) for i,q in enumerate(c['lessons'],1))
  bank=''.join(interview(q) for q in c['questions'])
  toc+=''.join(f'<a href="#q{q["id"]}">{i}. {E(teaching_title(q))}</a>' for i,q in enumerate(c['questions'],len(c['lessons'])+1))
  pager=f'<nav class="pager">'+(f'<a href="{url(previous["slug"]+".html")}">← {E(previous["title"])}</a>' if previous else f'<a href="{url("index.html")}">← Learning journey</a>')+(f'<a href="{url(following["slug"]+".html")}">Continue: {E(following["title"])} →</a>' if following else f'<a href="{url("roadmap.html")}">Revisit your experiments →</a>')+'</nav>'
  playground=rag_playground() if c['slug']=='foundations' else ''
  unit_links='<section class="prose"><h2>Complete worked course units</h2><p>Follow these companion units for the mechanism, worked cases and runnable source. Use the chapter prerequisites to decide when to begin.</p><ol>'+''.join('<li><a href="'+url('course-'+identity+'.html')+'">'+E(identity.replace('-',' '))+'</a></li>' for identity in c.get('course_units',[]))+'</ol></section>' if c.get('course_units') else ''
  body=f'''<div class="chapter-breadcrumb"><a href="{url('index.html')}#stage-{c['stage']}">STAGE {c['stage']} / {E(STAGES[c['stage']-1][0])}</a><span>Explain → apply → investigate</span></div><section class="chapter-hero"><div><p class="eyebrow">CHAPTER {position+1:02} / {E(c['title'])}</p><h1>{E(c['goal'])}</h1><p class="subtitle">{E(c['intro'])}</p></div><aside class="outcome-card"><span class="micro-label">BY THE END, YOU CAN EXPLAIN</span><p>{E(c['case'][1])}</p><small>Before this chapter: {prerequisites}</small><p class="track-meta">About {mins} min read · {len(c['lessons'])+len(c['questions'])} interview questions · all answers on this page</p></aside></section><nav class="section-nav" aria-label="Chapter sections"><a href="#walkthrough">See the flow</a><a href="#learn">Foundation questions</a><a href="#chapter-example">Read the code</a><a href="#interview">Deeper questions</a><a href="#chapter-lab">Build it</a><a href="#review-notes">Review notes</a><a href="#recommended-practice">Extend it</a></nav>{question_finder(c,url)}{diagram(c)}{simulation_panel(SIMULATION_CHAPTERS[c["slug"]],url) if c["slug"] in SIMULATION_CHAPTERS else ""}{playground}<section class="terms-panel"><h2>Which terms do you need for these questions?</h2><dl>{terms}</dl><a href="{url('glossary.html')}">Open the full terminology guide →</a></section><div class="reading-layout"><div>{review_panel(c)}<section id="learn"><div class="section-title"><div><span class="micro-label">LEARN THROUGH INTERVIEW QUESTIONS</span><h2>Foundation questions and detailed answers</h2></div><button id="practice" type="button" aria-pressed="false">View all answers</button></div>{lessons}</section>{unit_links}{code_panel(c)}<section id="interview" class="interview-bank"><span class="micro-label">MECHANISMS / IMPLEMENTATION / DEBUGGING / DESIGN</span><h2>Go deeper with interview questions</h2><p>Continue on this page through detailed explanations, worked cases, failure boundaries and design decisions. Acronyms used in an answer are explained inside it. All chapter answers are included here; there is no question-count cap.</p><button id="expand" type="button">View all answers</button>{bank}</section>{lab(c)}{review_practice(c)}{pager}</div><aside class="lesson-toc"><span class="micro-label">IN THIS CHAPTER</span>{toc}<a href="#chapter-example">→ Code walkthrough</a><a href="#chapter-lab">→ Practical experiment</a><a href="#recommended-practice">→ Completion checks</a></aside></div>'''
  write(c['slug']+'.html',c['goal'],body,c['slug'])
 for slug,e in EXAMPLES.items():
  extension={'python':'.py','sql':'.sql','markdown':'.md','javascript':'.js','html':'.html'}[e['language']]
  (ROOT/'examples'/(slug+extension)).write_text(e['code'])
 question_directory=ROOT/'examples'/'questions'
 question_directory.mkdir()
 for recipe in QUESTION_RECIPES.values():
  (question_directory/recipe['filename']).write_text(recipe['code'])
 (question_directory/'index.json').write_text(json.dumps({str(qid):dict(recipe=e['name'],file=e['filename'],language=e['language'],expected=e['expect']) for qid,e in QUESTION_CODE.items()},indent=2)+'\n')
 shutil.copytree(REPOSITORY/'labs',ROOT/'examples'/'labs',ignore=public_lab_ignore);(ROOT/'examples/__init__.py').write_text('');(ROOT/'examples/labs/__init__.py').write_text('')
 cards=[]
 for n,(title,level,summary,slugs) in enumerate(STAGES,1):
  items=''.join(f'<a class="chapter-card" href="{url(slug+".html")}"><span class="card-number">{CHAPTERS.index(BY[slug])+1:02}</span><div><small>{E(BY[slug]["title"])}</small><h3>{E(BY[slug]["goal"])}</h3><p>{E(BY[slug]["intro"])}</p><span class="card-link">Explained lessons · diagram · code · lab →</span></div></a>' for slug in slugs)
  cards.append(f'<section class="journey-stage" id="stage-{n}"><div class="stage-heading"><span class="stage-number">{n:02}</span><div><span class="micro-label">EXPLAIN / APPLY / INVESTIGATE</span><h2>{E(title)}</h2><p>{E(summary)}</p></div></div><div class="chapter-grid">{items}</div></section>')
 options=''.join(f'<option value="{c["slug"]}">{E(c["title"])}</option>' for c in CHAPTERS)
 options+=''.join(f'<option value="course-{c["id"]}">{E(c["title"])}</option>' for c in load_courses())
 home=f'''<section class="home-hero"><div><p class="eyebrow">A GUIDED COURSE FOR AI FULL-STACK ENGINEERS</p><h1>Understand the idea.<br><em>See it work.</em><br>Build it yourself.</h1><p class="subtitle">Begin with Python, computer science, HTTP and accessible interfaces. Continue through data, mathematics and machine learning before RAG, agents and production systems. Every chapter explains a real problem, walks through a concrete example, and gives you something to build.</p><a class="primary" href="{url('programming-foundations.html')}">Start with programming foundations →</a><a class="continue-link" id="continue-reading" href="{url('roadmap.html')}">Choose your learning path</a></div><aside class="preview-card"><span class="micro-label">THIS IS HOW THE COURSE TEACHES</span><h2>Can you transform three records safely?</h2><div class="preview-flow"><span>Read the input</span>↓<span>Validate its type</span>↓<span>Transform the values</span>↓<span>Check the expected result</span></div><p>You will follow the information, inspect the code, then see what happens when a step fails.</p><a href="{url('programming-foundations.html')}#walkthrough">Try the first walkthrough →</a></aside></section><section class="learning-contract"><div><b>01</b><h2>Start with a use case</h2><p>Know the problem before learning its terminology.</p></div><div><b>02</b><h2>Trace inputs and outputs</h2><p>Step through a chapter-specific diagram and simulate a failure.</p></div><div><b>03</b><h2>Build and defend</h2><p>Read the code, test a boundary, explain a trade-off.</p></div></section><section class="journey-intro"><p class="eyebrow">EXPLANATIONS → WORKED EXAMPLES → DEEPER PRACTICE</p><h2>A path with prerequisites,<br>not a list of technologies.</h2><p>Follow the stages in order, or use the chapter's prerequisite link to fill a gap. Chapter depth follows the subject; there is no fixed question quota.</p></section><section class="prose"><h2>Review notes and missing foundations</h2><p>Each chapter now includes additional explanations, a content review, recommended work, and observable completion checks. Start with programming and web basics where needed, then follow the same topic into deeper engineering decisions.</p><a href="{url('coverage-audit.html')}#content-review">Read the coverage review and recommended route →</a></section>{''.join(cards)}<section class="search-panel" id="search"><span class="micro-label">FIND A CONCEPT OR A QUESTION</span><h2>Search the whole course</h2><label for="query">Topic, failure, framework, or use case</label><input type="search" id="query" placeholder="Try token budget, replay, OCR, or approval"><div class="search-options"><label>Chapter<select id="chapter-filter"><option value="">All chapters</option>{options}</select></label><label>Study status<select id="status-filter"><option value="all">All topics</option><option value="unlearned">Not learned yet</option><option value="learned">Started</option><option value="familiar">Familiar</option><option value="practiced">Practiced</option><option value="independent">Independent</option><option value="mastered">Estimated Mastered</option><option value="bookmarked">Bookmarked</option><option value="review">Due for review</option></select></label></div><p id="search-count" role="status"></p><div id="results"></div><button id="more-results" type="button" hidden>Show more results</button><button id="random" type="button">Practice a random topic</button></section><section class="record-panel"><h2>Keep your explanations</h2><p>Notes, bookmarks, practice attempts, and review schedules stay in this browser profile using IndexedDB, with a localStorage fallback. No account, server sync, or personal-data transmission is used. Practice attempts update your review schedule. Practiced and Independent require passing checks; estimated Mastered requires distinct independent checks at least a day apart. This is study evidence, not certification. Your earlier question history remains available after the chapter reorder. Export a backup before switching devices.</p><p><progress id="progress" value="0"></progress> <span id="progress-label">0 topics understood</span> · <span id="review-label">Nothing due for review</span></p><button id="export" type="button">Export progress</button><button id="reset-progress" type="button">Clear study record</button><label class="import-label">Import progress<input id="import" type="file" accept="application/json,.json"></label><p id="storage-status" role="status"></p></section>'''
 home += '<section class="prose"><h2>Choose a track</h2><ul>'+''.join(f'<li><a href="{url("tracks/"+t["id"]+".html")}">{E(t["title"])}</a> — {E(t["description"])}</li>' for t in CURRICULUM['tracks'])+'</ul></section>'
 write('index.html','Learn AI engineering through explained examples',home,search=True)
 lab_entries=[]
 for i,c in enumerate(CHAPTERS,1):
  lab_body=lab(c,'lab-body-'+c['slug'])
  lab_entries.append(f'<section class="lab-entry" id="lab-{c["slug"]}"><a href="{url(c["slug"]+".html")}">Chapter {i}: {E(c["title"])} →</a>{lab_body}</section>')
 write('roadmap.html','Practical experiments','<p class="eyebrow">BUILD / BREAK / EXPLAIN</p><h1>Practice the actual boundaries.</h1><p class="subtitle">Each experiment uses the chapter case. Bring back working behavior, a failure demonstration, and evidence supporting your design choice.</p>'+''.join(lab_entries))
 write('examples.html','Code studio','<p class="eyebrow">READ SMALL IMPLEMENTATIONS / THEN CONNECT THE LAYERS</p><h1>Code with an explanation.</h1><p class="subtitle">Examples use synthetic data. Python scope labels distinguish executable standard-library examples from optional framework sketches. SQL fragments need a disposable schema.</p><section class="code-studio" id="integration-labs"><h2>Connect HTTP, SSE, WebSocket, voice, and OCR</h2><p>The optional backend demonstrates task acceptance, status, replay, and cancellation. Its state is process-local, not production durability.</p><ul>'+''.join(f'<li><a href="{url("examples/labs/"+p)}">{p}</a></li>' for p in ('README.md','streaming_app.py','voice_pipeline.py','ocr_extract.py'))+'</ul></section>'+''.join('<div id="'+c['slug']+'">'+code_panel(c).replace('id="chapter-example"','id="code-'+c['slug']+'"')+'</div>' for c in CHAPTERS))
 glossary=json.loads((CONTENT/'shared/glossary.json').read_text());terms=dict(glossary);terms.update(ACRONYMS)
 for c in CHAPTERS:
  for name,meaning in c['terms']:terms.setdefault(name,meaning)
 write('glossary.html','Terminology without assumed knowledge','<p class="eyebrow">PLAIN DEFINITIONS BEFORE TECHNICAL DETAIL</p><h1>Make the words useful.</h1><label for="term-search">Find a term</label><input id="term-search" type="search"><div class="glossary-grid">'+''.join(f'<article id="{term_id(name)}" data-term="{E((name+" "+meaning).lower())}"><h2>{E(name)}</h2><p>{E(meaning)}</p></article>' for name,meaning in sorted(terms.items()))+'</div>')
 references=json.loads((CONTENT/'shared/references.json').read_text())
 write('libraries.html','Frameworks and references','<p class="eyebrow">CHOOSE BY RESPONSIBILITY</p><h1>Read the contract,<br>then choose the tool.</h1><p class="subtitle">Runtime, protocol, database, and evaluation libraries solve different problems. They are not a mandatory stack. Follow compatible version documentation and use measured task needs to justify additions.</p><section class="reference-list" id="official-docs">'+''.join(f'<a href="{E(url)}"><strong>{E(name)}</strong><span>Official reference ↗</span></a>' for name,url in references.values())+'</section>')
 write('diagrams.html','Interactive system maps','<p class="eyebrow">TWO LEVELS OF EXPLORATION</p><h1>Follow the information.</h1><p class="subtitle">Every teaching chapter contains its own step-through diagram and failure simulation. These larger maps connect the responsibilities across chapters.</p>'+''.join(f'<a class="map-card" href="{url("diagrams/"+slug+".html")}"><h2>{title}</h2><span>Open the larger interactive map →</span></a>' for slug,title in [('context','Context and evidence'),('harness','Agent harness and business authority'),('streaming','Streaming and voice delivery'),('quality','Documents and evaluation')]))
 write('atlas.html','Course responsibility map','<p class="eyebrow">THE REORDERED LEARNING PATH</p><h1>Find the responsibility.</h1>'+''.join(f'<section class="map-card"><h2>{title}</h2><p>{summary}</p><ul>'+''.join(f'<li><a href="{url(slug+".html")}">{E(BY[slug]["title"])}</a></li>' for slug in slugs)+'</ul></section>' for title,level,summary,slugs in STAGES))
 write('provenance.html','How to use this course','''<p class="eyebrow">A COURSE BUILT AROUND UNDERSTANDING</p><h1>Read, trace, build, explain.</h1><section class="prose"><h2>What changed</h2><p>Chapters now follow explicit dependencies from programming and web foundations to advanced systems. Each has a specific use case, plain definitions, its own interactive flow, explained lessons, code, and a practical experiment. Topic coverage determines chapter depth; no fixed number of questions is required.</p><h2>Two reading depths</h2><p>Start with the guided explanations and concrete cases. Use the additional interview questions for technical depth, trade-offs, and failure boundaries. Existing question identifiers are preserved even though their chapters moved. New guided lessons have independent stable identifiers.</p><h2>Scope and evidence</h2><p>The platform and data are fictional. This website does not expose private project code or call model providers. Standard-library examples use synthetic fixtures. Optional agent SDK examples are syntax-checked sketches; the OCR engine and SQL fragments are not executed. The synthetic FastAPI lab has authentication, ownership, SSE replay, cancellation, and WebSocket checks, but uses process-local state.</p><h2>Your study record</h2><p>Notes and learned flags are personal study tools, not certification. They stay in your browser and can be exported. No print control is included; core content remains readable without JavaScript. Interactive examples are deterministic teaching simulations, not live model output.</p></section>''')
 write('coverage-audit.html','Coverage and learning structure',f'<h1>Coverage follows the subject.</h1><p>Use the responsibility map to find the complete ordered course. Each chapter now has its own guided lessons, concrete case, diagram, implementation, and deeper questions.</p><p><a href="{url("editorial-report.html")}">Editorial evidence and pending review</a></p><a href="{url("atlas.html")}">Open the responsibility map →</a>'+coverage_review())
 for old,new in [('insurance-system','application-architecture'),('insurance-decisions','evidence-applicability')]:write(old+'.html','Chapter moved',f'<h1>Continue to the updated chapter.</h1><a href="{url(new+".html")}">Open chapter →</a><script>location.replace("{url(new+".html")}"+location.search+location.hash)</script>')
 design_html=f'''<section class="design-showcase"><h1>Design System Showcase</h1><p class="subtitle">Every component used across the learning guide, with realistic AI lesson content.</p>

 <h2>Design Tokens</h2>
 <table class="comparison-table"><caption>Design tokens in light and dark themes</caption><thead><tr><th>Token</th><th>Light</th><th>Dark</th><th>Usage</th></tr></thead><tbody>
 <tr><td>--bg</td><td>#f4f6fb</td><td>#0c1423</td><td>Page background</td></tr>
 <tr><td>--panel</td><td>#fff</td><td>#141f32</td><td>Card/panel surface</td></tr>
 <tr><td>--text</td><td>#1a2941</td><td>#e9effb</td><td>Primary text</td></tr>
 <tr><td>--accent</td><td>#2458d3</td><td>#96b7ff</td><td>Links, accents</td></tr>
 <tr><td>--mint</td><td>#08766c</td><td>#75dec8</td><td>Success, mastery</td></tr>
 <tr><td>--warm</td><td>#8b5208</td><td>#f0be75</td><td>Warnings</td></tr>
 </tbody></table>

 <h2>Typography Scale</h2>
 <p class="callout callout-definition"><span class="callout-icon">A</span>Root: 16px · Scale: xs 0.75rem, sm 0.875rem, base 1rem, lg 1.125rem, xl 1.25rem, 2xl 1.5rem, 3xl 2rem</p>

 <h2>Components</h2>

 <h3>Comparison Table</h3>
 <table class="comparison-table"><thead><tr><th>Approach</th><th>Best for</th><th>Trade-off</th></tr></thead><tbody>
 <tr><td>Dense retrieval</td><td>Semantic similarity</td><td>Misses exact terms</td></tr>
 <tr><td>BM25 keyword</td><td>Exact term matching</td><td>Misses synonyms</td></tr>
 <tr><td>Hybrid + RRF</td><td>Both semantic and exact</td><td>More infrastructure</td></tr>
 </tbody></table>

 <h3>Math Block</h3>
 <div class="math-block"><span class="math-label">Cosine similarity</span>sim(A,B) = (A · B) / (||A|| × ||B||)</div>

 <h3>Quote Block</h3>
 <div class="quote-block"><p>Task success is real authorized state, not fluent text.</p><p class="quote-source">— Agent evaluation lesson</p></div>

 <h3>Callouts</h3>
 <div class="callout callout-definition"><span class="callout-icon">D</span><strong>Definition:</strong> An oracle is an independent specification of correct behavior.</div>
 <div class="callout callout-tip"><span class="callout-icon">T</span><strong>Tip:</strong> Use deterministic oracles where possible; reviewed judgments only where needed.</div>
 <div class="callout callout-warning"><span class="callout-icon">W</span><strong>Warning:</strong> Random sleep tests do not reliably reproduce races.</div>
 <div class="callout callout-danger"><span class="callout-icon">!</span><strong>Danger:</strong> An oracle that only checks final text misses unauthorized side effects.</div>
 <div class="callout callout-production"><span class="callout-icon">P</span><strong>Production:</strong> Validate every tool parameter against a schema before execution.</div>

 <h3>Glossary Term</h3>
 <p>Use <a class="glossary-term" href="glossary.html">RAG</a> to ground answers in your documents.</p>

 <h3>Figure + Caption</h3>
 <figure class="lesson-figure"><svg viewBox="0 0 360 150" role="img" aria-label="Retriever sends evidence to generator" width="360" height="150" xmlns="http://www.w3.org/2000/svg"><rect x="50" y="50" width="100" height="60" fill="var(--panel2)" stroke="var(--line)"/><text x="100" y="85" text-anchor="middle" fill="var(--text)">Retriever</text><rect x="200" y="50" width="100" height="60" fill="var(--panel2)" stroke="var(--line)"/><text x="250" y="85" text-anchor="middle" fill="var(--text)">Generator</text><line x1="150" y1="80" x2="200" y2="80" stroke="var(--accent)" stroke-width="2" marker-end="url(#arr)"/><defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><polygon points="0 0, 8 4, 0 8" fill="var(--accent)"/></marker></defs></svg><figcaption>RAG pipeline: retriever feeds evidence to generator. <span class="figure-alt">Alt: Two boxes labeled Retriever and Generator with an arrow from Retriever to Generator.</span></figcaption></figure>

 <h3>Expandable Follow-up</h3>
 <details class="expandable-followup"><summary>Why evaluate the full trajectory instead of just the answer?</summary><div class="followup-content"><p>Fluent final text can mask unauthorized reads, duplicate writes, or wrong tool choices. The effect ledger captures every tool call, argument, result, and durable write so evaluation checks actual behavior, not just prose.</p></div></details>

 <h3>Next / Prerequisite Navigation</h3>
 <div class="nav-pair"><a href="api-security.html" class="nav-prev">← Prerequisite: API Security</a><a href="agent-evaluation.html" class="nav-next">Next: Agent Evaluation →</a></div>

 <h3>Detailed interview answers</h3>
 <p>Use <strong>View answer</strong> to reveal one detailed explanation with worked cases, diagrams, code where useful, trade-offs and follow-up exercises.</p>

 </section>'''
 write('design-system.html','Design System Showcase',design_html)
 practice_counts=build_learning_pages(ROOT,write,CHAPTERS,url)
 course_counts=build_course_pages(ROOT,write,url,controls)
 build_simulations(write,url)
 build_curriculum_audit(ROOT,write,CHAPTERS,CURRICULUM,url)
 build_learning_blueprint(ROOT,write,CHAPTERS,CURRICULUM,url)
 manifest=dict(edition='interview-led-v6',title='AI Full-Stack Engineering Roadmap',questions=TOTAL,study_topics=STUDY_TOTAL,max_study_id=MAX_ID,chapters=len(CHAPTERS),chapters_with_review_notes=len(CHAPTERS),added_guided_lessons=sum(q.get('added',False) for c in CHAPTERS for q in c['lessons']),guided_lessons=sum(len(c['lessons']) for c in CHAPTERS),chapter_topics={c['slug']:len(c['questions'])+len(c['lessons']) for c in CHAPTERS},chapter_order=[c['slug'] for c in CHAPTERS],stages=len(STAGES),suggested_experiments=len(CHAPTERS),downloadable_labs=sum(len(list((REPOSITORY/'labs').glob(pattern))) for pattern in ('*.py','*.js','*.html')),examples=len(EXAMPLES),questions_with_code=len(QUESTION_CODE),distinct_question_examples=len(QUESTION_RECIPES),chapter_specific_diagrams=len(CHAPTERS),overview_diagrams=4,source_snapshots=0,answer_diagrams=len(VISUALS),chapter_answer_limit=None,conceptual_worked_questions=sum(q.get('answer_format')=='conceptual' for c in CHAPTERS for q in c['questions']),acronym_definitions=len(ACRONYMS),configured_base_path=BASE_PATH,question_bank_pages=bank_pages,**practice_counts,**course_counts,coverage_matrix={d:sum(1 for c in CHAPTERS for q in c.get('questions',[]) if q.get('domain')==d) for d in set(q.get('domain','') for c in CHAPTERS for q in c.get('questions',[]) if q.get('domain'))})
 manifest_path=ROOT/'manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k not in ('chapter_order','chapter_topics')},indent=2))
if __name__=='__main__':build()
