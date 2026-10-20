"""Render structured course units, outcome traceability and local project handoffs."""
from pathlib import Path
import ast
import html
import json
import zipfile
from course_data import _check_schema

ROOT=Path(__file__).resolve().parent.parent
E=lambda value:html.escape(str(value),quote=True)


def load():
    courses=[];seen=set()
    for path in sorted((ROOT/'content/courses').glob('*.json')):
        course=json.loads(path.read_text())
        _check_schema(course,json.loads((ROOT/'content/shared/course-schema.json').read_text()),'course',path.stem)
        for unit in course['units']:
            if unit['id'] in seen:raise ValueError('Duplicate learning outcome unit: '+unit['id'])
            seen.add(unit['id'])
            for field in ('title','outcomes','terms','narrative','lab','practice','debugging','tradeoffs','references'):
                if not unit.get(field):raise ValueError(f'Missing course field {field}: {unit["id"]}')
            lab=ROOT/'labs'/unit['lab']
            if lab.parent!=ROOT/'labs' or not lab.is_file():raise ValueError('Invalid course lab')
            ast.parse(lab.read_text())
        courses.append(course)
    registry=json.loads((ROOT/'content/shared/study_ids.json').read_text())
    for course in courses:
        for unit in course['units']:
            if registry.get('course/'+course['id']+'/'+unit['id'])!=unit.get('study_id'):
                raise ValueError('Unregistered course study identity')
    units={unit['id']:unit for course in courses for unit in course['units']}
    visited=set();active=set()
    def visit(identity):
        if identity in active:raise ValueError('Course prerequisite cycle')
        if identity in visited:return
        active.add(identity)
        for dep in units[identity]['prerequisites']:
            if dep not in units:raise ValueError('Missing prerequisite unit')
            visit(dep)
        active.remove(identity);visited.add(identity)
    for identity in units:visit(identity)
    return courses


def build(out,write,url,controls=lambda q:""):
    courses=load();outcomes=[]
    observed=json.loads((ROOT/'content/lab-results.json').read_text())
    for course in courses:
        nav='<ol>'+''.join(f'<li><a href="{url("course-"+unit["id"]+".html")}">{E(unit["title"])}</a></li>' for unit in course['units'])+'</ol>'
        write('course-'+course['id']+'.html',course['title'],'<p class="eyebrow">FOUNDATIONS → MECHANISMS → WORKING PROGRAMS</p><h1>'+E(course['title'])+'</h1><p>'+E(course['description'])+'</p><p>Technical review: '+E(course['review_status'])+'. These units include runnable local fixtures and independent exercises; they are not a professional certification.</p>'+nav)
        for index,unit in enumerate(course['units']):
            lab=(ROOT/'labs'/unit['lab']).read_text()
            terms='<dl>'+''.join('<dt><strong>'+E(term['term'])+'</strong></dt><dd>'+E(term['definition'])+'</dd>' for term in unit['terms'])+'</dl>'
            prereqs=' · '.join('<a href="'+url('course-'+dep+'.html')+'">'+E(dep.replace('-',' '))+'</a>' for dep in unit['prerequisites']) or 'Course entry point'
            body=f'<p class="eyebrow">{E(course["title"])} · UNIT {index+1}/{len(course["units"])}</p><h1>{E(unit["title"])}</h1><section class="prose"><p>About {unit["estimated_minutes"]} minutes · {E(unit["path"])}. Prerequisites: {prereqs}</p><h2>Learning outcomes</h2><ul>'+''.join('<li>'+E(item)+'</li>' for item in unit['outcomes'])+'</ul><h2>Terms before mechanisms</h2>'+terms+'<h2>Understand the mechanism</h2>'+''.join('<p>'+E(paragraph)+'</p>' for paragraph in unit['narrative'])+'</section>'
            body+='<section class="practice-card"><h2>Runnable local implementation</h2><p><a href="'+url('examples/labs/'+unit['lab'])+'">Download '+E(unit['lab'])+'</a>. '+(E(unit['dependencies']) if unit.get('dependencies') else 'Python 3.11+, standard library only.' if unit['lab'] not in {'transaction_api.py','request_lifecycle.py'} else 'Optional FastAPI/PostgreSQL dependencies; follow the project setup. This server never runs on GitHub Pages.')+'</p><p>The source includes assertions and a deterministic verification routine. Run it locally, change one boundary, then rerun the checks.</p><div class="code-panel"><button class="copy" type="button" aria-live="polite">Copy code</button><pre><code>'+E(lab)+'</code></pre></div></section>'
            if unit['lab'] in observed:
                body+='<h2>Observed reference output</h2><p>'+E(observed[unit['lab']]['scope'])+'</p><pre><code>'+E(observed[unit['lab']]['observed_output'])+'</code></pre>'
            body+='<section class="prose"><h2>Debug the boundary</h2><p>'+E(unit['debugging'])+'</p><h2>Costs and alternatives</h2><p>'+E(unit['tradeoffs'])+'</p><h2>Independent work</h2><ol>'+''.join('<li>'+E(item)+'</li>' for item in unit['practice'])+'</ol><h2>Check your understanding</h2><p>Explain the invariant, show the tested input/output, introduce a controlled failure, and defend one alternative. Passing the provided fixture does not establish correctness for every input.</p>'
            if unit.get('assessment'):body+='<p><a href="'+url('assessments.html')+'#a-'+unit['assessment']+'">Try the related graded scenario</a></p>'
            body+='<h2>Primary references</h2><ul>'+''.join('<li><a href="'+E(ref)+'">'+E(ref)+'</a></li>' for ref in unit['references'])+'</ul></section>'
            body+='<nav class="pager"><a href="'+url('course-'+course['id']+'.html')+'">Course contents</a>'
            if index+1<len(course['units']):body+='<a href="'+url('course-'+course['units'][index+1]['id']+'.html')+'">Next: '+E(course['units'][index+1]['title'])+'</a>'
            body+='</nav>'
            body += '<section id="q'+str(unit['study_id'])+'" data-question="'+str(unit['study_id'])+'"><h2>My study record for this unit</h2>'+controls({'id':unit['study_id']})+'</section>'
            write('course-'+unit['id']+'.html',unit['title'],body,'course-'+unit['id'])
            outcomes.append({'unit':unit['id'],'study_id':unit['study_id'],'course':course['id'],'outcomes':[{'id':unit['id']+'.outcome-'+str(i+1),'text':text} for i,text in enumerate(unit['outcomes'])],'lab':unit['lab'],'assessment':unit.get('assessment'),'review':course['review_status'],'prerequisites':unit['prerequisites'],'path':unit['path']})
    projects=[
      ('async-engine','Bounded async job engine','async_job_engine.py',['Bound admitted work and worker concurrency','Distinguish job failure, timeout and caller cancellation','Release every queue item and clean up child tasks'],['Cancellation after handler starts','A handler that never finishes','Producer admission under full capacity'],'In-memory queues do not survive process restart. Sensitive input must not leak through errors. Bound work before admitting untrusted jobs.'),
      ('transaction-api','Authorized PostgreSQL task API','transaction_api.py',['Validate requests and authenticate synthetic owners','Resolve concurrent matching keys to one task','Reject changed content and other-owner access','Atomically confirm state and outbox intent'],['Concurrent acceptance and confirmation barriers','Crash between writes and commit','A known resource ID requested by another owner'],'Tokens are synthetic local fixtures, not a JWT/login service. Store secrets in the local environment. Object authorization must hold at the query and mutation boundary.'),
      ('rag-quality','Retrieval evaluation and regression gate','rag_evaluation.py',['Separate tenant-scoped retrieval from answer generation','Compute quality against independent relevance labels','Detect a deliberately dropped policy and correct abstention'],['Remove the sale policy from the candidate set','Query another owner’s private exception','Request evidence absent from the index'],'Fixture documents are synthetic. Apply ownership filters before exposing candidates. A relevance score is not a policy authorization decision.'),
      ('durable-agent','Recoverable agent effects','durable_agent.py',['Record approval before effect dispatch','Reuse a stable operation identity after a lost acknowledgment','Reject owner and payload conflicts','Inspect durable provider effects separately from calls'],['Crash after provider commit and before local acknowledgment','Retry the same operation twice','Try an unapproved or cross-owner operation'],'The local provider is a fixture, not an external connector. The real receiver must deduplicate or reconcile using the same effect key. A local rollback cannot undo its commit.')]
    cards=[]
    for identity,title,lab,requirements,faults,threat in projects:
        body=f'<p class="eyebrow">LOCAL-FIRST CAPSTONE</p><h1>{E(title)}</h1><p>This project is downloaded and run locally. GitHub Pages hosts instructions and source only. The reference implementation has an executable verification routine; independent work starts from the blank starter.</p>'
        body+='<h2>Requirements and acceptance checks</h2><ol>'+''.join('<li>'+E(item)+'</li>' for item in requirements)+'</ol><h2>Threat model and scope</h2><p>'+E(threat)+'</p>'
        body+='<h2>Architecture</h2><pre><code>Caller → validated operation → authoritative state → effect boundary → independent oracle</code></pre><p>Follow each boundary in the source; identify which state survives a process restart and which effects commit independently.</p><h2>Milestones</h2><ol><li>Run the reference and save its verification output.</li><li>Implement the public interfaces in the starter without copying the solution.</li><li>Add the failure fixtures below and prove they reject a broken implementation.</li><li>Document costs, recovery limits, setup and a clean-start command.</li></ol><h2>Failure injection</h2><ul>'+''.join('<li>'+E(item)+'</li>' for item in faults)+'</ul>'
        body+='<h2>Downloads and setup</h2><ul><li><a href="'+url('examples/labs/'+lab)+'">Reference solution and acceptance routine</a></li><li><a href="'+url('examples/capstones/'+identity+'-starter.py')+'">Starter template</a></li><li><a href="'+url('examples/labs/README.md')+'">Platform and dependency instructions</a></li></ul>'
        if lab=='transaction_api.py':
            body+='<p>Requires PostgreSQL 16+, FastAPI, httpx and psycopg. From a repository checkout, run <code>python scripts/test_postgres_pilot.py</code>; it creates a new disposable loopback-only PostgreSQL cluster and removes it afterwards. See CONTRIBUTING for dependencies. This requires local PostgreSQL tools, not a cloud account.</p>'
        else:body+='<p>On macOS/Linux: <code>python3.11 '+E(lab)+'</code>. On Windows: <code>py -3.11 '+E(lab)+'</code>. Use an isolated Python environment; these three projects require only the standard library and small synthetic fixtures. No GPU or provider account is needed.</p>'
        body+='<h2>Review rubric and deliverables</h2><ul><li>Correct happy path and observed durable state.</li><li>A reproduced failure with an independent assertion.</li><li>No unauthorized effects or duplicate operation identities.</li><li>Commands, environment, test output, architecture explanation and known limitations.</li></ul><p>A project passes review only when its behavior is demonstrated. Reading the reference or clicking Familiar is insufficient.</p>'
        write('capstone-'+identity+'.html',title,body)
        folder=out/'examples/capstones';folder.mkdir(exist_ok=True)
        interfaces = {
          'async-engine':'async def run_jobs(jobs, handler, workers=2, capacity=2, deadline=0.1):\n    raise NotImplementedError("Implement bounded workers and cleanup")\n',
          'transaction-api':'def accept_task(owner, operation_key, message):\n    raise NotImplementedError("Persist one authorized task identity")\n\ndef confirm_task(task_id, owner):\n    raise NotImplementedError("Guard state and outbox in one transaction")\n',
          'rag-quality':'def retrieve(query, owner, documents):\n    raise NotImplementedError("Scope candidates before ranking")\n\ndef evaluate(cases):\n    raise NotImplementedError("Measure relevance and abstention independently")\n',
          'durable-agent':'def execute(path, key, owner, payload, approved):\n    raise NotImplementedError("Persist approval and reconcile a stable effect key")\n'
        }
        starter='"""Implement requirements before consulting the reference."""\n\n'+interfaces[identity]+'\ndef verify():\n    raise NotImplementedError("Add independent invariants and failure cases")\n\nif __name__ == "__main__":\n    verify()\n'
        (folder/(identity+'-starter.py')).write_text(starter)
        cards.append(f'<article class="map-card"><h2><a href="{url("capstone-"+identity+".html")}">{E(title)}</a></h2><p>{E(requirements[0])}. Local reference, starter, failure cases and review rubric.</p></article>')
    bundle=out/'examples/local-projects.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for source in (ROOT/'labs').glob('*.py'):
            archive.write(source,'labs/'+source.name)
        archive.writestr('labs/__init__.py','')
        for name in ('LICENSE','requirements-labs.txt','requirements-models.txt'):
            archive.write(ROOT/name,name)
        archive.write(ROOT/'labs/README.md','README.md')
        archive.write(ROOT/'scripts/test_postgres_pilot.py','scripts/test_postgres_pilot.py')
    write('capstones.html','Connected local capstones','<p class="eyebrow">BUILD A SYSTEM · VERIFY ITS BOUNDARIES</p><h1>From cooperative tasks to durable effects.</h1><p><a href="'+url('examples/local-projects.zip')+'">Download all local project sources and tests as a ZIP</a></p><p>Work through the async engine, authorized task API, retrieval quality gate and recoverable agent effect ledger. Connect them only after each boundary passes its independent checks. The final integration uses the task API to admit work, bounded workers to execute it, retrieval evaluation to guard evidence quality, and the ledger to reconcile effects.</p><p><a href="'+url('examples/labs/fullstack_demo.py')+'">Download the connected local full-stack demo</a>. Its acceptance routine uses the PostgreSQL task API, bounded async engine, scoped retrieval and durable demo-effect ledger. See the lab README for setup; no server runs on Pages.</p>'+''.join(cards))
    (out/'questions/outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n')
    write('courses.html','Foundations courses','<p class="eyebrow">MECHANISMS WITH RUNNABLE EVIDENCE</p><h1>Fill the foundations deliberately.</h1>'+''.join('<article class="map-card"><h2><a href="'+url('course-'+course['id']+'.html')+'">'+E(course['title'])+'</a></h2><p>'+E(course['description'])+'</p></article>' for course in courses)+'<p><a href="'+url('capstones.html')+'">Continue to the connected capstones</a> · <a href="'+url('questions/outcomes.json')+'">Outcome-to-exercise map</a></p>')
    return {'foundation_courses':len(courses),'course_units':sum(len(c['units']) for c in courses),'connected_capstones':len(projects)}
