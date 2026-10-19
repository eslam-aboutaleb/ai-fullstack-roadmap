"""Build the independent, general-purpose AI learning roadmap with stdlib only."""
from pathlib import Path
import ast, html, json, re, shutil
from examples import EXAMPLES
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ESC = lambda value: html.escape(str(value), quote=True)
CHAPTERS = json.loads((HERE/'core.json').read_text())
for section in (HERE/'advanced.txt').read_text().split('## ')[1:]:
    header, *lines = section.strip().splitlines()
    slug, title, subtitle = header.split('|')
    questions = [dict(zip(('Q','A','Why','Risk','Trade','Try'), line.split(' || '))) for line in lines]
    assert len(questions) == 10 and all(len(line.split(' || ')) == 6 for line in lines)
    CHAPTERS.append(dict(slug=slug,title=title,subtitle=subtitle,questions=questions))
TOTAL = sum(len(c['questions']) for c in CHAPTERS)
assert TOTAL == 480 and len(CHAPTERS) == 48
assert set(EXAMPLES) == {c['slug'] for c in CHAPTERS}
GROUPS = [(0,14,'RAG and engineering foundations'),(14,20,'Application, data, and identity'),
          (20,30,'Frameworks, evaluation, and delivery'),(30,34,'Context and prompt engineering'),
          (34,40,'MCP, skills, orchestration, and harnesses'),(40,48,'Evaluation, streaming, and multimodal products')]
REFERENCES = json.loads((HERE/'references.json').read_text())
REFERENCES.update({
 'mcp-tools': ['MCP tools: versioned 2025-11-25 contract','https://modelcontextprotocol.io/specification/2025-11-25/server/tools'],
 'mcp-sdk': ['Official MCP Python SDK and version guidance','https://github.com/modelcontextprotocol/python-sdk'],
 'mcp-security': ['MCP security best practices','https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices'],
 'skills': ['Agent Skills specification','https://agentskills.io/specification'],
 'sse': ['MDN: using Server-Sent Events','https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events'],
 'websocket': ['MDN: WebSocket API','https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API'],
 'webrtc': ['MDN: WebRTC API','https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API'],
 'audio': ['MDN: Web Audio API','https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API'],
 'ocr': ['Tesseract OCR documentation','https://tesseract-ocr.github.io/tessdoc/'],
 'injection': ['OWASP: prompt injection prevention','https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html'],
 'attention': ['Attention Is All You Need','https://arxiv.org/abs/1706.03762'],
 'rag-paper': ['Retrieval-Augmented Generation paper','https://arxiv.org/abs/2005.11401'],
})
DOC_GROUP = {'context-engineering':['rag-paper','injection'], 'context-optimization':['attention'],
 'prompt-foundations':['injection'],'prompt-techniques':['injection'], 'mcp-foundations':['mcp-tools','mcp-security'],
 'mcp-server-engineering':['mcp-sdk','mcp-security'],'skills-layers':['skills'],
 'agent-orchestration':['lg-persistence'],'agent-patterns':['lg-thinking'],'agent-harness':['injection'],
 'evaluation-engineering':['adk-eval'] if 'adk-eval' in REFERENCES else ['rag-paper'],
 'backend-agents':['sqlalchemy'],'sse-streaming':['sse'],'websocket-streaming':['websocket'],
 'voice-agents':['webrtc','audio'],'ocr-document-ai':['ocr'],'live-agents':['websocket'],
 'portfolio-capstone':['rag-paper']}

def diagram_for(index):
    if index < 14: return 'context' if index in (0,2,3,4,5,6,7,8) else ('quality' if index in (9,11,12) else 'harness')
    if index in (26,): return 'quality'
    if index in (27,42,43,44,46): return 'streaming'
    if index in (30,31,32,33): return 'context'
    if index in (23,24,25,40,45,47): return 'quality'
    return 'harness'

def shell(title, body, active=''):
    nav=''.join(f'<a {"aria-current=page" if c["slug"]==active else ""} href="{c["slug"]}.html"><span>{i:02}</span>{ESC(c["title"])}</a>' for i,c in enumerate(CHAPTERS,1))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Learn AI full-stack engineering through 480 detailed interview questions, synthetic code examples, diagrams, and practical labs."><title>{ESC(title)} · AI Full-Stack Engineering Roadmap</title><link rel="stylesheet" href="style.css"><script src="search-index.js" defer></script><script src="app.js" defer></script></head>
<body data-page="{active}" data-question-count="{TOTAL}"><a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="brand" href="index.html"><span class="brand-icon">AI/</span> ROADMAP <small>FULL-STACK ENGINEERING</small></a><nav aria-label="Study pages"><a href="index.html">Overview & search</a><a href="roadmap.html">Learning path & 48 labs</a><a href="libraries.html">Frameworks & references</a><a href="examples.html">Code examples</a><a href="glossary.html">Glossary</a><a href="atlas.html">Concept map</a><a href="diagrams.html">Interactive diagrams</a><a href="provenance.html">Scope & learning method</a></nav><p class="nav-label">THE INTERVIEW CHAPTERS</p><nav class="chapters" aria-label="Chapters">{nav}</nav><div class="sidebar-foot"><span id="progress-label">Study at your pace</span><progress id="progress" max="{TOTAL}" value="0" aria-label="Questions learned"></progress><small>Build. Break. Explain. Improve.</small></div></aside><div class="workspace"><header class="toolbar"><a href="index.html#search">Search the roadmap <kbd>/</kbd></a><button id="theme" type="button">Change theme</button></header><main id="main" tabindex="-1">{body}</main><footer>AI Full-Stack Engineering Roadmap · 19 October 2026 · Fictional scenarios and synthetic examples. <a href="provenance.html">Scope & learning method</a></footer></div></body></html>'''

def write(name,title,body,active=''):
    (ROOT/name).write_text(shell(title,body,active),encoding='utf-8')

def example_panel(slug):
    e=EXAMPLES[slug]
    filename=slug+{'python':'.py','sql':'.sql','markdown':'.md'}[e['language']]
    return f'''<section class="panel example" id="{slug}"><h2>{ESC(next(c['title'] for c in CHAPTERS if c['slug']==slug))}: worked example</h2><p>{ESC(e['scope'])}</p><div class="code-panel"><button class="copy" type="button">Copy code</button><pre><code>{ESC(e['code'])}</code></pre></div><p><a href="examples/{filename}">Open the original teaching file</a> · <a href="{slug}.html">Read the chapter</a></p></section>'''

def question(q,number,chapter):
    references=f'<p class="reference"><a href="{ESC(q["reference"])}">Official documentation →</a></p>' if q.get('reference') else ''
    return f'''<article class="question" id="q{number}" data-question="{number}"><div class="q-meta"><span>QUESTION {number:03}</span><span>CONCEPT + REFERENCE CASE</span><a href="#q{number}" aria-label="Link to question {number}">#</a></div><details class="answer" open><summary><h2>{number}. {ESC(q['Q'])}</h2><span class="reveal">Read / reveal answer</span></summary><div class="answer-body"><p class="lead-answer">{ESC(q['A'])}</p><h3>Mechanism & explanation</h3><p>{ESC(q['Why'])}</p><h3>Risks & safeguards</h3><p>{ESC(q['Risk'])}</p><h3>Trade-offs</h3><p>{ESC(q['Trade'])}</p><div class="exercise"><h3>Apply it</h3><p>{ESC(q['Try'])}</p></div>{references}<p class="reference"><a href="#chapter-example">Use the chapter's synthetic example</a> · <a href="roadmap.html#lab-{chapter['slug']}">Complete the practical lab</a></p></div></details><div class="study-controls"><label><input type="checkbox" data-learned="{number}"> I can explain this</label><button type="button" class="bookmark" data-bookmark="{number}" aria-pressed="false">Bookmark</button></div><details class="notes"><summary>My explanation & notes</summary><label for="note-{number}">Explain the mechanism, failure case, and trade-off</label><textarea id="note-{number}" data-note="{number}" rows="4" placeholder="Write your own explanation before revealing the answer."></textarea></details></article>'''

def build():
    # This repository previously published project snapshots. Remove only its old
    # generated site trees; authoring sources and the independent .git remain.
    for directory in ('sources','diagrams','examples'):
        path=ROOT/directory
        if path.exists(): shutil.rmtree(path)
        path.mkdir()
    for file in ROOT.glob('*.html'): file.unlink()
    for stem in ('context','harness','streaming','quality'):
        diagram=(HERE/'diagrams'/f'{stem}.html').read_text()
        # Preserve validated diagram content while adapting its public reader:
        # remove the requested print option and local authoring path metadata.
        diagram=re.sub(r'<button\b[^>]*\bdata-print\b[^>]*>.*?</button>', '', diagram, flags=re.S)
        diagram=diagram.replace("item=>item.matches('[data-print]') ? window.print() : exportImage(item.dataset.exportImage)", "item=>exportImage(item.dataset.exportImage)")
        diagram=re.sub(r'"sourcePath":"[^"]*"', '"sourcePath":"authoring/diagrams/'+stem+'.archify.md"', diagram)
        diagram=re.sub(r'"baseDir":"[^"]*"', '"baseDir":"authoring/diagrams"', diagram)
        (ROOT/'diagrams'/f'{stem}.html').write_text(diagram)
    search=[];number=0
    for index,c in enumerate(CHAPTERS):
        first=number+1;articles=[]
        for q in c['questions']:
            number+=1; articles.append(question(q,number,c))
            search.append(dict(id=number,slug=c['slug'],chapter=c['title'],title=q['Q'],text=' '.join(q.get(k,'') for k in ('Q','A','Why','Risk','Trade','Try'))))
        refkeys=DOC_GROUP.get(c['slug'],[])
        refs=''.join(f'<li><a href="{ESC(REFERENCES[key][1])}">{ESC(REFERENCES[key][0])}</a></li>' for key in refkeys if key in REFERENCES)
        prior=f'<a href="{CHAPTERS[index-1]["slug"]}.html">← Previous chapter</a>' if index else '<a href="index.html">← Overview</a>'
        following=f'<a href="{CHAPTERS[index+1]["slug"]}.html">Next chapter →</a>' if index+1<len(CHAPTERS) else '<a href="roadmap.html">Build the capstone →</a>'
        diagram=diagram_for(index)
        premise='These answers discuss a fictional multi-tenant support platform and reusable reference-design choices. They do not describe a particular company, repository, or deployed implementation. Framework examples are alternatives; they are not all required in one stack.'
        body=f'''<p class="eyebrow">CHAPTER {index+1:02} / QUESTIONS {first}–{number}</p><h1>{ESC(c['title'])}</h1><p class="subtitle">{ESC(c['subtitle'])}</p><div class="chapter-tools"><button id="practice" aria-pressed="false" type="button">Practice: hide answers</button><button id="expand" type="button">Reveal all answers</button><a href="#chapter-example">Jump to code</a></div><details class="case-note"><summary>Reference case and scope</summary><p>{premise}</p></details><section class="diagram-panel"><h2>Explore the design</h2><a href="diagrams/{diagram}.html">Open the interactive {diagram} diagram ↗</a><iframe title="Interactive {diagram} design explainer" src="diagrams/{diagram}.html" loading="lazy"></iframe></section>{''.join(articles)}<div id="chapter-example">{example_panel(c['slug'])}</div>{f'<section class="panel"><h2>Further reading</h2><ul>{refs}</ul></section>' if refs else ''}<nav class="pager" aria-label="Chapter navigation">{prior}{following}</nav>'''
        write(c['slug']+'.html',c['title'],body,c['slug'])
    (ROOT/'search-index.js').write_text('window.GUIDE_SEARCH = '+json.dumps(search,ensure_ascii=False,separators=(',',':'))+';\n')
    shutil.copytree(HERE/'labs', ROOT/'examples'/'labs')
    (ROOT/'examples'/'__init__.py').write_text('')
    (ROOT/'examples'/'labs'/'__init__.py').write_text('')
    for slug,e in EXAMPLES.items():
        extension={'python':'.py','sql':'.sql','markdown':'.md'}[e['language']]
        (ROOT/'examples'/(slug+extension)).write_text(e['code'])
        if e['language']=='python': ast.parse(e['code'],filename=slug)
    options=''.join(f'<option value="{c["slug"]}">{i:02} · {ESC(c["title"])}</option>' for i,c in enumerate(CHAPTERS,1))
    cards=''.join(f'<a class="chapter-card" href="{c["slug"]}.html"><span>{i:02} / {"FOUNDATIONS" if i<=30 else "ADVANCED PRACTICE"}</span><h2>{ESC(c["title"])}</h2><p>{ESC(c["subtitle"])}</p><small>10 detailed questions · Q{10*i-9}–{10*i} →</small></a>' for i,c in enumerate(CHAPTERS,1))
    path_cards=''.join(f'<a class="path-card" href="roadmap.html#stage-{n}"><span>STAGE {n}</span><strong>{label}</strong><small>Chapters {start+1}–{end} →</small></a>' for n,(start,end,label) in enumerate(GROUPS,1))
    write('index.html','Learn AI full-stack engineering',f'''<p class="eyebrow">A PUBLIC LEARNING ROADMAP / CONCEPTS INTO WORKING SYSTEMS</p><h1>Build useful AI.<br><em>Understand every layer.</em></h1><p class="subtitle">A practical journey through RAG, agents, context and prompts, MCP, skills, databases, evaluation, streaming, voice, and document AI. Learn the mechanism, reproduce a failure, and defend the trade-off.</p><div class="stats"><div><strong>{TOTAL}</strong><span>interview questions & answers</span></div><div><strong>48</strong><span>chapters & practical labs</span></div><div><strong>48</strong><span>synthetic code examples</span></div><div><strong>6</strong><span>connected learning stages</span></div></div><section class="panel"><h2>Choose a route, then build something</h2><p>Start with foundations or continue with context engineering, MCP, skills, agent harnesses, realtime delivery, voice, and OCR. Every chapter connects explanations to a practical lab and original teaching code.</p><a class="primary" href="foundations.html">Start the foundations →</a> <a href="context-engineering.html">Explore the advanced journey</a></section><div class="path-grid">{path_cards}</div><section class="panel"><h2>Test your understanding</h2><p>Practice hides answers until you reveal them. Save your own explanation, bookmark difficult questions, and mark a topic learned after you can implement and explain it.</p><button type="button" id="random">Give me a practice question</button></section><section id="search" class="search-panel"><h2>Search the complete roadmap</h2><label for="query">Find a concept, failure case, framework, or interview question</label><input id="query" type="search" placeholder="Try context budget, MCP, interruption, or transaction"><div class="search-options"><label>Chapter<select id="chapter-filter"><option value="">All chapters</option>{options}</select></label><label>Study status<select id="status-filter"><option value="all">All questions</option><option value="unlearned">Not learned yet</option><option value="learned">Learned</option><option value="bookmarked">Bookmarked</option></select></label></div><p id="search-count" role="status"></p><div id="results"></div></section><div class="section-heading"><h2>Your curriculum</h2><a href="roadmap.html">Follow the learning path →</a></div><div class="chapter-grid">{cards}</div><section class="panel"><h2>Keep your learning record</h2><p>Your progress and notes stay in your browser. Export a backup before switching devices. Nothing is sent to a backend.</p><button id="export" type="button">Export progress</button> <label class="import-label">Import progress<input id="import" type="file" accept="application/json,.json"></label><p id="storage-status" role="status"></p></section>''')
    stages=[]
    for n,(start,end,label) in enumerate(GROUPS,1):
        labs=[]
        for index in range(start,end):
            c=CHAPTERS[index];qs=c['questions']
            steps=''.join(f'<li>{ESC(qs[i]["Try"])}</li>' for i in (0,4,9))
            labs.append(f'''<article class="panel lab" id="lab-{c['slug']}"><p class="eyebrow">LAB {index+1:02}</p><h3>{ESC(c['title'])}</h3><p>{ESC(c['subtitle'])}</p><ol>{steps}</ol><h4>Acceptance evidence</h4><ul><li>Demonstrate the required behavior using synthetic fixtures and record the actual outcome.</li><li>Reproduce this failure boundary: {ESC(qs[4]['Risk'])}</li><li>Defend this trade-off with a baseline or a documented constraint: {ESC(qs[9]['Trade'])}</li></ul><details><summary>Solution outline</summary><p>{ESC(qs[0]['Why'])}</p><p>{ESC(qs[4]['Why'])}</p><a href="examples.html#{c['slug']}">Start with the synthetic chapter example</a></details><a href="{c['slug']}.html">Study chapter {index+1} →</a></article>''')
        stages.append(f'<section id="stage-{n}"><p class="eyebrow">STAGE {n}</p><h2>{label}</h2>{"".join(labs)}</section>')
    write('roadmap.html','Learning path and practical labs','''<p class="eyebrow">SIX STAGES / 48 PRACTICAL LABS</p><h1>Learn by building.<br><em>Prove it by breaking it.</em></h1><p class="subtitle">Complete each stage with a small implementation, a failure demonstration, and a clear explanation. The path is flexible: use your actual gaps to choose depth.</p><section class="panel"><h2>One fictional capstone throughout</h2><p>Build a multi-tenant support platform with versioned knowledge, customer-owned service requests, approved business actions, and a recoverable task lifecycle. Start text-only. Add voice and document processing when their chapters become relevant.</p><p>Suggested sequence: backend and data → retrieval and evidence → agent tools → context and prompts → MCP and skills → durable orchestration → evaluation → streaming and multimodal delivery.</p></section>'''+''.join(stages))
    integration='<section class="panel" id="integration-labs"><h2>Connect the pieces: optional integration labs</h2><p>Use a complete synthetic FastAPI service to study HTTP tasks, SSE replay, cancellation, and authenticated WebSocket control. Add injected voice adapters or optional local OCR extraction.</p><ul><li><a href="examples/labs/README.md">Setup, endpoints, dependencies, and limits</a></li><li><a href="examples/labs/streaming_app.py">FastAPI streaming service</a></li><li><a href="examples/labs/voice_pipeline.py">Injected voice pipeline</a></li><li><a href="examples/labs/ocr_extract.py">Optional local OCR extraction</a></li></ul></section>'
    write('examples.html','Synthetic code examples','<p class="eyebrow">48 ORIGINAL TEACHING EXAMPLES</p><h1>Study the boundary.<br><em>Then implement the adapter.</em></h1><p class="subtitle">Examples use synthetic data. Standard-library Python is executable; optional framework examples are syntax-checked sketches requiring compatible dependencies. SQL and skill examples are unexecuted teaching fragments. Each scope label states the limit.</p>'+integration+''.join(example_panel(c['slug']) for c in CHAPTERS))
    glossary=json.loads((HERE/'glossary.json').read_text())
    glossary.extend([
      ('Context engineering','Selecting, organizing, validating, and budgeting information available to a model at a decision point.'),
      ('Context compaction','Reducing working history while preserving verified facts, unresolved questions, and operation identity.'),
      ('Prompt caching','Provider-supported reuse of computation for compatible repeated prompt material; distinct from reusing an application answer.'),
      ('Agent harness','The runtime that manages model calls, tools, policy, state, budgets, events, observability, and recovery.'),
      ('Agent skill','A reusable task procedure with metadata and optional resources or scripts; it grants no backend authority by itself.'),
      ('Progressive disclosure','Loading a small capability description first and detailed instructions or references only when needed.'),
      ('ASR — Automatic Speech Recognition','Recognizing speech as text; also called speech-to-text in many systems.'),
      ('TTS — Text-to-Speech','Generating spoken audio from text, with voice, language, and timing considerations.'),
      ('VAD — Voice Activity Detection','Detecting acoustic speech activity; it does not by itself prove user intent or task completion.'),
      ('Barge-in','A user interruption that requires coordinated playback stopping and handling of obsolete generation.'),
      ('WebRTC — Web Real-Time Communication','Browser and platform APIs supporting realtime media and related data communication.'),
      ('Backpressure','A policy for slowing producers or controlling work when consumers or downstream services cannot keep up.'),
      ('Generation ID','An identifier used to reject stale output after an interruption or newer user input.'),
      ('Document intelligence','Interpreting text, fields, layout, tables, and relationships from document artifacts.'),
      ('CER — Character Error Rate','A text-recognition error measure; it does not directly measure downstream task success.'),
      ('WER — Word Error Rate','A recognition error measure at word level; intent-critical errors need separate evaluation.'),
    ])
    seen={};
    for term,meaning in glossary: seen.setdefault(term,meaning)
    glossary_cards=''.join(f'<article class="panel" data-term="{ESC((term+" "+meaning).lower())}"><h2>{ESC(term)}</h2><p>{ESC(meaning)}</p></article>' for term,meaning in sorted(seen.items()))
    write('glossary.html','AI and backend glossary',f'<p class="eyebrow">{len(seen)} TERMS</p><h1>Name the concept.<br><em>Explain the mechanism.</em></h1><label for="term-search">Filter the glossary</label><input type="search" id="term-search"><div class="glossary-grid">{glossary_cards}</div>')
    rows=[('Google ADK','Agent runtime','Session, tool, model, and evaluation integration'),('LangChain','Agent and model interfaces','Tool schemas, middleware, and structured outputs'),('LangGraph','Stateful orchestration','Reducers, checkpoints, interrupts, and replay boundaries'),('MCP','AI-facing integration protocol','Capability compatibility and resource authorization'),('A2A','Remote agent task protocol','Task ownership, delegation, and cancellation'),('Ragas','RAG evaluation components','Required context, references, judge calibration'),('DeepEval','Model evaluation and testing','Metric contract and judge reproducibility'),('Promptfoo','Configuration-driven evaluation','Assertions, providers, and experiment configuration'),('LangSmith','Tracing and evaluation workflows','Export privacy, run lineage, and framework adapters'),('Phoenix','Observability and evaluation','Trace schema, deployment, and retention'),('TruLens','Evaluation and observability','Feedback definitions and application recording'),('OpenTelemetry','Vendor-neutral telemetry','Safe attributes, context propagation, and sampling'),('PostgreSQL / SQLAlchemy','Persistence and transactions','Isolation, pool capacity, and transaction ownership')]
    table=''.join(f'<tr><th scope="row">{ESC(name)}</th><td>{ESC(role)}</td><td>{ESC(boundary)}</td></tr>' for name,role,boundary in rows)
    links=''.join(f'<li><a href="{ESC(url)}">{ESC(title)}</a></li>' for title,url in REFERENCES.values())
    write('libraries.html','Frameworks and primary references',f'<p class="eyebrow">CHOOSE BY RESPONSIBILITY</p><h1>Build a coherent stack.</h1><p class="subtitle">These technologies are alternatives and complementary layers. They are not a mandatory dependency list. Pin versions, read the actual contract, and measure whether an addition solves your problem.</p><div class="table-scroll"><table><caption>Tools, responsibilities, and integration boundaries</caption><thead><tr><th>System</th><th>Responsibility</th><th>Check before adoption</th></tr></thead><tbody>{table}</tbody></table></div><section class="panel" id="official-docs"><h2>Primary references</h2><p>Live documentation changes. Version-specific examples state their scope; follow the compatible release documentation rather than assuming the newest API is installed.</p><ul>{links}</ul></section>')
    diag_cards=''.join(f'<section class="panel"><h2>{title}</h2><p>{description}</p><a href="diagrams/{slug}.html">Explore the interactive diagram →</a></section>' for slug,title,description in [('context','Context and evidence','From intent and identity to bounded evidence and validated output.'),('harness','Agent runtime and business authority','A tool proposal crosses policy checks before causing an effect.'),('streaming','Streaming and voice delivery','Typed public events, persistence, and terminal state.'),('quality','Documents and evaluation','From isolated uploads and OCR to measured release gates.')])
    write('diagrams.html','Interactive design diagrams','<p class="eyebrow">FOUR GENERALIZED DESIGN EXPLAINERS</p><h1>Follow the boundaries.</h1><p class="subtitle">These are fictional reference designs. Their diagrams explain responsibilities and message order; they are not production deployment maps or measured timing charts.</p>'+diag_cards)
    write('atlas.html','Concept and responsibility map','<p class="eyebrow">CONCEPTS / CONTRACTS / FAILURE BOUNDARIES</p><h1>See the whole system.</h1><p class="subtitle">Use this map to connect concepts to responsibilities. Each chapter supplies a synthetic example and a practical exercise rather than a private source-code snapshot.</p>'+''.join(f'<section class="panel"><h2>{label}</h2><ul>'+''.join(f'<li><a href="{c["slug"]}.html">{ESC(c["title"])}</a> — {ESC(c["subtitle"])}</li>' for c in CHAPTERS[start:end])+'</ul></section>' for start,end,label in GROUPS))
    write('provenance.html','Scope and learning method','''<p class="eyebrow">GENERALIZED PUBLIC EDITION</p><h1>Learn reusable engineering.</h1><section class="panel"><h2>Reference design, not production claims</h2><p>The roadmap uses a fictional support platform with versioned knowledge and customer-owned service requests. Design descriptions are illustrative assumptions and counterexamples. They do not report a particular repository, company, deployment, or benchmark.</p><p>Project names, commit references, repository links, exact source excerpts, and complete frozen source pages from the earlier edition have been removed. Code examples are original synthetic teaching material. Frameworks are presented by responsibility, with optional integrations clearly scoped.</p></section><section class="panel"><h2>How to study</h2><p>Explain the mechanism, implement the example, reproduce a failure, and defend a trade-off. Use practice mode before revealing answers. A learned checkbox is a personal signal, not certification.</p><p>Q1–300 retain their identifiers in the generalized edition; Q301–480 add context, prompts, MCP, skills, harnesses, evaluation engineering, streaming, voice, OCR, and live agents. Earlier browser progress is migrated when available. Revisit older notes against the revised wording.</p></section><section class="panel"><h2>Examples and verification limits</h2><p>Python examples are syntax checked. Standard-library examples are exercised locally using synthetic data. Optional agent-framework integrations are not installed or called against live providers. The synthetic FastAPI lab was exercised for authentication, owner checks, task completion, SSE replay, cancellation, and WebSocket control. SQL fragments require a reviewed disposable schema and are not executed. Security and production-readiness claims require evidence from your own implementation.</p><p>The handbook has no backend or model calls. Search, theme, notes, bookmarks, and progress run in your browser. Export your study record before switching browsers or devices.</p></section><section class="panel"><h2>References</h2><p>Primary documentation supports protocol and framework learning. APIs and supported features change; pin compatible dependencies and evaluate upgrades. <a href="libraries.html#official-docs">Open the primary reference catalog</a>.</p></section>''')
    write('coverage-audit.html','Curriculum coverage','<p class="eyebrow">THE GENERALIZED EDITION</p><h1>From foundations to live AI.</h1><p>The first 300 question IDs are retained in a generalized reference case. The 180 additional questions extend the roadmap into context, prompts, MCP, skills, harnesses, evaluation, streaming, voice, OCR, and live-agent delivery.</p><a href="atlas.html">Browse all learning responsibilities →</a>')
    # Old chapter entry URLs remain usable; their source archive does not.
    for old,new in [('insurance-system','application-architecture'),('insurance-decisions','evidence-applicability')]:
        write(old+'.html','Chapter moved',f'<h1>This chapter has moved.</h1><p><a href="{new}.html">Continue to the generalized chapter →</a></p><script>location.replace("{new}.html"+location.search+location.hash)</script>')
    manifest=dict(edition='generalized-public-v2',title='AI Full-Stack Engineering Roadmap',questions=TOTAL,chapters=len(CHAPTERS),labs=len(CHAPTERS),examples=len(EXAMPLES),glossary_terms=len(seen),source_snapshots=0,diagrams=4,optional_integration_labs=3,answer_words=sum(len(q[k].split()) for c in CHAPTERS for q in c['questions'] for k in ('A','Why','Risk','Trade','Try')))
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__': build()
