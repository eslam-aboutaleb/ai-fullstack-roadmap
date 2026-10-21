"""Render structured course units, outcome traceability and local project handoffs."""
from pathlib import Path
import ast
import html
import json
import zipfile
from urllib.parse import urlsplit
from course_data import _check_schema
from engineering_projects import load as load_projects, files as project_files, build as build_projects

ROOT=Path(__file__).resolve().parent.parent
E=lambda value:html.escape(str(value),quote=True)


def load():
    courses=[];seen=set()
    projects={row['id'] for row in load_projects()}
    references=json.loads((ROOT/'content/shared/references.json').read_text())
    for path in sorted((ROOT/'content/courses').glob('*.json')):
        course=json.loads(path.read_text())
        _check_schema(course,json.loads((ROOT/'content/shared/course-schema.json').read_text()),'course',path.stem)
        for unit in course['units']:
            if unit['id'] in seen:raise ValueError('Duplicate learning outcome unit: '+unit['id'])
            seen.add(unit['id'])
            for field in ('title','outcomes','terms','narrative','lab','practice','debugging','tradeoffs','references'):
                if not unit.get(field):raise ValueError(f'Missing course field {field}: {unit["id"]}')
            for context in unit.get('source_context',[]):
                if context['reference_id'] not in references or references[context['reference_id']][1] not in unit['references']:raise ValueError('Unlinked source context')
            if unit.get('project') and unit['project'] not in projects:raise ValueError('Unknown local project')
            lab=ROOT/'labs'/unit['lab']
            if lab.parent!=ROOT/'labs' or not lab.is_file() or lab.is_symlink():raise ValueError('Invalid course lab')
            for reference in unit['references']:
                parsed=urlsplit(reference)
                if parsed.scheme not in ('http','https') or not parsed.netloc:raise ValueError('Invalid primary course reference')
            if lab.suffix=='.py':ast.parse(lab.read_text())
            elif lab.suffix=='.html':
                if '<!doctype html>' not in lab.read_text().lower():raise ValueError('HTML exercise needs a complete document')
            else:raise ValueError('Unsupported course exercise format')
        courses.append(course)
    order=json.loads((ROOT/'content/course.json').read_text())['course_order']
    if set(order)!={course['id'] for course in courses} or len(order)!=len(courses):raise ValueError('Course journey order must list each course once')
    courses.sort(key=lambda course:order.index(course['id']))
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
    project_count=build_projects(out,write,url)
    references=json.loads((ROOT/'content/shared/references.json').read_text())
    observed=json.loads((ROOT/'content/lab-results.json').read_text())
    for course in courses:
        nav='<ol>'+''.join(f'<li><a href="{url("course-"+unit["id"]+".html")}">{E(unit["title"])}</a></li>' for unit in course['units'])+'</ol>'
        write('course-'+course['id']+'.html',course['title'],'<p class="eyebrow">FOUNDATIONS → MECHANISMS → WORKING PROGRAMS</p><h1>'+E(course['title'])+'</h1><p>'+E(course['description'])+'</p>'+nav)
        for index,unit in enumerate(course['units']):
            lab=(ROOT/'labs'/unit['lab']).read_text()
            terms='<dl>'+''.join('<dt><strong>'+E(term['term'])+'</strong></dt><dd>'+E(term['definition'])+'</dd>' for term in unit['terms'])+'</dl>'
            prereqs=' · '.join('<a href="'+url('course-'+dep+'.html')+'">'+E(dep.replace('-',' '))+'</a>' for dep in unit['prerequisites']) or 'Course entry point'
            body=f'<p class="eyebrow">{E(course["title"])} · UNIT {index+1}/{len(course["units"])}</p><h1>{E(unit["title"])}</h1><section class="prose"><p>About {unit["estimated_minutes"]} minutes · {E(unit["path"])}. Prerequisites: {prereqs}</p><h2>Learning outcomes</h2><ul>'+''.join('<li>'+E(item)+'</li>' for item in unit['outcomes'])+'</ul><h2>Terms before mechanisms</h2>'+terms+'<h2>Understand the mechanism</h2>'+''.join('<p>'+E(paragraph)+'</p>' for paragraph in unit['narrative'])+'</section>'
            for example in unit.get('worked_examples',[]):
                body+='<section class="prose"><h2>'+E(example['title'])+'</h2><p>'+E(example['setup'])+'</p><ol>'+''.join('<li>'+E(step)+'</li>' for step in example['steps'])+'</ol><p><strong>Result:</strong> '+E(example['result'])+'</p></section>'
            incident=unit.get('incident')
            if incident:
                body+='<section class="practice-card"><h2>Production incident walkthrough</h2>'+''.join('<h3>'+E(title)+'</h3><p>'+E(incident[field])+'</p>' for field,title in [('symptom','Observed symptom'),('evidence','Evidence to collect'),('investigation','Investigation'),('recovery','Recovery'),('prevention','Prevention and regression check')])+'</section>'
            if unit['lab'].endswith('.html'):
                unit={**unit,'dependencies':'Open the self-contained HTML exercise in a browser. It uses deterministic local fixtures and no API keys.'}
            body+='<section class="practice-card"><h2>Runnable local implementation</h2><p><a href="'+url('examples/labs/'+unit['lab'])+'">Download '+E(unit['lab'])+'</a>. '+(E(unit['dependencies']) if unit.get('dependencies') else 'Python 3.11+, standard library only.' if unit['lab'] not in {'transaction_api.py','request_lifecycle.py'} else 'Optional FastAPI/PostgreSQL dependencies; follow the project setup. This server never runs on GitHub Pages.')+'</p><p>Run the reference exercise, change one boundary, and inspect the observable result. Python references include executable assertions; the browser fixture exposes reproducible failure scenarios.</p><div class="code-panel"><button class="copy" type="button" aria-live="polite">Copy code</button><pre><code>'+E(lab)+'</code></pre></div></section>'
            body+='<p><a href="'+url('examples/local-projects.zip')+'">Download all local sources, dependency requirements and setup instructions</a></p>'
            if unit['lab'] in observed:
                body+='<h2>Observed reference output</h2><p>'+E(observed[unit['lab']]['scope'])+'</p><pre><code>'+E(observed[unit['lab']]['observed_output'])+'</code></pre>'
            body+='<section class="prose"><h2>Debug the boundary</h2><p>'+E(unit['debugging'])+'</p><h2>Costs and alternatives</h2><p>'+E(unit['tradeoffs'])+'</p><h2>Independent work</h2><ol>'+''.join('<li>'+E(item)+'</li>' for item in unit['practice'])+'</ol><h2>Check your understanding</h2><p>Explain the invariant, show the tested input/output, introduce a controlled failure, and defend one alternative. Passing the provided fixture does not establish correctness for every input.</p>'
            if unit.get('project'):body+='<p><a href="'+url('project-'+unit['project']+'.html')+'">Continue to the complete local project and independent review tasks</a></p>'
            if unit.get('assessment'):body+='<p><a href="'+url('assessments.html')+'#a-'+unit['assessment']+'">Try the related graded scenario</a></p>'
            if unit.get('interviews'):
                body+='<h2>Technical interview and design defense</h2>'
                for interview in unit['interviews']:
                    body+='<details><summary>'+E(interview['question'])+'</summary><h3>Interview response</h3><p>'+E(interview['spoken'])+'</p><h3>Detailed reasoning</h3><p>'+E(interview['deep'])+'</p><h3>Follow-up</h3><p><strong>'+E(interview['follow_up']['question'])+'</strong></p><p>'+E(interview['follow_up']['answer'])+'</p><h3>What a strong answer demonstrates</h3><ul>'+''.join('<li>'+E(item)+'</li>' for item in interview['rubric'])+'</ul></details>'
            if unit.get('source_context'):
                body+='<h2>How the references inform this unit</h2><ul>'+''.join('<li><a href="'+E(references[context['reference_id']][1])+'">'+E(references[context['reference_id']][0])+'</a>: '+E(context['explanation'])+' <strong>Limit:</strong> '+E(context['boundary'])+' Checked '+E(context['accessed_at'])+'.</li>' for context in unit['source_context'])+'</ul>'
            body+='<h2>Primary references</h2><ul>'+''.join('<li><a href="'+E(ref)+'">'+E(ref)+'</a></li>' for ref in unit['references'])+'</ul></section>'
            body+='<nav class="pager"><a href="'+url('course-'+course['id']+'.html')+'">Course contents</a>'
            if index+1<len(course['units']):body+='<a href="'+url('course-'+course['units'][index+1]['id']+'.html')+'">Next: '+E(course['units'][index+1]['title'])+'</a>'
            body+='</nav>'
            body += '<section id="q'+str(unit['study_id'])+'" data-question="'+str(unit['study_id'])+'"><h2>My notes and bookmarks for this unit</h2>'+controls({'id':unit['study_id']})+'</section>'
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
        body+='<h2>Review rubric and deliverables</h2><ul><li>Correct happy path and observed durable state.</li><li>A reproduced failure with an independent assertion.</li><li>No unauthorized effects or duplicate operation identities.</li><li>Commands, environment, test output, architecture explanation and known limitations.</li></ul><p>A project passes review only when its behavior is demonstrated. Reading the reference alone is insufficient.</p>'
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
        for source in (ROOT/'labs').glob('*.html'):
            archive.write(source,'labs/'+source.name)
        if not (ROOT/'labs/__init__.py').exists():
            archive.writestr('labs/__init__.py','')
        for name in ('LICENSE','requirements-labs.txt','requirements-models.txt','requirements-advanced.txt','requirements-dev.txt'):
            archive.write(ROOT/name,name)
        archive.write(ROOT/'labs/README.md','README.md')
        archive.write(ROOT/'scripts/test_postgres_pilot.py','scripts/test_postgres_pilot.py')
        archive.write(ROOT/'scripts/test_kafka_recovery.py','scripts/test_kafka_recovery.py')
        for project in load_projects():
            for source,target in project_files(project['id']):archive.write(source,target)
    write('capstones.html','Connected local capstones','<p class="eyebrow">BUILD A SYSTEM · VERIFY ITS BOUNDARIES</p><h1>From cooperative tasks to durable effects.</h1><p><a href="'+url('examples/local-projects.zip')+'">Download all local project sources and tests as a ZIP</a></p><p>Work through the async engine, authorized task API, retrieval quality gate and recoverable agent effect ledger. Connect them only after each boundary passes its independent checks. The final integration uses the task API to admit work, bounded workers to execute it, retrieval evaluation to guard evidence quality, and the ledger to reconcile effects.</p><p><a href="'+url('examples/labs/fullstack_demo.py')+'">Download the connected local full-stack demo</a>. Its acceptance routine uses the PostgreSQL task API, bounded async engine, scoped retrieval and durable demo-effect ledger. See the lab README for setup; no server runs on Pages.</p>'+''.join(cards))
    (out/'questions/outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n')
    write('courses.html','Engineering courses','<p class="eyebrow">MECHANISMS WITH RUNNABLE EVIDENCE</p><h1>Build the foundations and defend the system.</h1><p>Start with <a href="programming-foundations.html">Programming foundations</a> and follow the main chapter journey. These companion courses expand its mechanisms and projects; check each unit’s prerequisites before skipping ahead.</p>'+''.join('<article class="map-card"><h2><a href="'+url('course-'+course['id']+'.html')+'">'+E(course['title'])+'</a></h2><p>'+E(course['description'])+'</p></article>' for course in courses)+'<p><a href="'+url('engineering-projects.html')+'">Cumulative projects and review packet</a> · <a href="'+url('capstones.html')+'">Continue to the connected capstones</a> · <a href="'+url('questions/outcomes.json')+'">Outcome-to-exercise map</a></p>')
    units=[unit for course in courses for unit in course['units']]
    return {'foundation_courses':sum(c['id'] in {'python-backend','math-models'} for c in courses),
            'engineering_courses':len(courses),'cumulative_projects':project_count,'course_units':len(units),
            'course_interviews':sum(len(unit['interviews']) for unit in units),
            'worked_cases':sum(len(unit['worked_examples']) for unit in units),
            'incident_walkthroughs':sum('incident' in unit for unit in units),'connected_capstones':len(projects)}
