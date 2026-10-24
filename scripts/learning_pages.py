"""Build static assessment, coding-lab and study pages with progressive enhancement."""
import html
import json
from course_pages import load as load_courses
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = lambda value: html.escape(str(value), quote=True)


def load_practice(chapters):
    topics = {q['id']: c['slug'] for c in chapters for q in c['lessons'] + c['questions']}
    topics.update({unit['study_id']:'course-'+unit['id'] for course in load_courses() for unit in course['units']})
    assessments = json.loads((ROOT/'content/assessments.json').read_text())['items']
    labs = json.loads((ROOT/'content/browser-labs.json').read_text())['labs']
    seen = set()
    for item in assessments + labs:
        if item['id'] in seen or not __import__('re').fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item['id']):
            raise ValueError('Duplicate or invalid practice ID: '+item['id'])
        seen.add(item['id'])
        if topics.get(item['topic']) != item['chapter']:
            raise ValueError('Practice topic does not belong to chapter: '+item['id'])
        for field in ('title', 'objective', 'references', 'hints'):
            if not item.get(field): raise ValueError(f'Missing {field}: {item["id"]}')
        if 'cases' in item:
            if item['language'] not in ('javascript', 'python') or not item.get('starter') or not item.get('solution') or not item['cases']:
                raise ValueError('Incomplete coding lab: '+item['id'])
            if any(not {'name','input','expected'} <= set(case) for case in item['cases']):
                raise ValueError('Incomplete lab test: '+item['id'])
        elif item['kind'] == 'self-review':
            if not item.get('rubric') or not item.get('model_answer'): raise ValueError('Missing design rubric')
        elif item['kind'] in ('quiz','debugging'):
            ids = [option['id'] for option in item['options']]
            if len(ids) != len(set(ids)) or len(ids) < 2 or item['correct'] not in ids or any(not o.get('feedback') for o in item['options']):
                raise ValueError('Invalid answer choices: '+item['id'])
        else: raise ValueError('Unknown assessment kind')
    return assessments, labs


def config(out, name, variable, data):
    encoded = json.dumps(data, ensure_ascii=False, separators=(',',':')).replace('<', '\\u003c')
    (out/name).write_text(f'window.{variable}={encoded};\n')


def build(out, write, chapters, url):
    assessments, labs = load_practice(chapters)
    config(out, 'practice-data.js', 'GUIDE_PRACTICE', {'assessments':assessments,'labs':labs})
    catalogue = [dict(id=q['id'], title=q['Q'], chapter=c['title'], url=c['slug']+'.html#q'+str(q['id'])) for c in chapters for q in c['lessons']+c['questions']]
    catalogue += [dict(id=unit['study_id'],title=unit['title'],chapter=course['title'],url='course-'+unit['id']+'.html#q'+str(unit['study_id'])) for course in load_courses() for unit in course['units']]
    config(out, 'study-catalogue.js', 'GUIDE_TOPICS', catalogue)
    scripts = f'<script src="{url("practice-data.js")}" defer></script><script src="{url("practice.js")}" defer></script>'
    cards = []
    for item in assessments:
        identity = item['id']
        options = ''
        if item['kind'] != 'self-review':
            options = '<fieldset><legend>Choose the best answer</legend>'+''.join(f'<label class="assessment-option"><input type="radio" name="answer-{identity}" value="{E(o["id"])}"> {E(o["text"])}</label>' for o in item['options'])+'</fieldset>'
            action = '<button type="button" data-grade disabled>Check my answer</button>'
            solution = E(item['explanation'])
        else:
            options = f'<label for="design-{identity}">Write your design and trade-offs</label><textarea id="design-{identity}" data-design rows="6"></textarea><h3>Self-review rubric</h3><ul>'+''.join('<li>'+E(point)+'</li>' for point in item['rubric'])+'</ul>'
            action = '<button type="button" data-grade disabled>Record my self-review</button>'
            solution = E(item['model_answer'])
        hints = ''.join('<li>'+E(hint)+'</li>' for hint in item['hints'])
        cards.append(f'''<article class="practice-card" id="a-{identity}" data-assessment="{identity}" data-topic="{item['topic']}"><p class="eyebrow">{E(item['kind'])} · {E(item['difficulty'])}</p><h2>{E(item['title'])}</h2><p>{E(item['scenario'])}</p><p><small>Learning outcome: {E(item['objective'])}</small></p>{options}<details data-hint><summary>Show a hint</summary><ul>{hints}</ul></details>{action}<p role="status" data-feedback></p><details data-solution><summary>Explanation and answer key</summary><p>{solution}</p></details><p><a href="{url(item['chapter']+'.html')}#q{item['topic']}">Review the lesson</a> · <a href="{E(item['references'][0])}">Primary reference</a></p></article>''')
    write('assessments.html','Practice with evidence','''<p class="eyebrow">RECALL · DEBUG · DEFEND</p><h1>Test the decision, not your confidence.</h1><p>Quizzes and debugging checks are graded against explicit fixtures. Design responses use a self-review rubric and are never automatically marked correct. Your attempts stay in this browser. Progress estimates come from recorded practice attempts.</p><noscript><p>Enable JavaScript to grade and save attempts. Every scenario, rubric and answer key below is readable without it.</p></noscript><div class="practice-tools"><label for="practice-order">Order</label><select id="practice-order"><option value="recommended">Recommended: failed and due first</option><option value="seeded">Seeded shuffle</option></select><label for="practice-seed">Shuffle seed</label><input id="practice-seed" type="number" min="1" max="4294967295" value="42"><button type="button" id="order-practice">Apply order</button></div><div id="assessment-cards">'''+''.join(cards)+'</div>'+scripts)
    cards=[]
    for item in labs:
        identity=item['id']; language=item['language']
        hints=''.join('<li>'+E(hint)+'</li>' for hint in item['hints'])
        fixtures=''.join('<tr><th scope="row">'+E(case['name'])+'</th><td><code>'+E(json.dumps(case['input']))+'</code></td><td><code>'+E(json.dumps(case['expected']))+'</code></td></tr>' for case in item['cases'])
        cards.append(f'''<article class="practice-card coding-lab" id="lab-{identity}" data-lab="{identity}"><p class="eyebrow">{E(language)} · LOCAL BROWSER EXECUTION</p><h2>{E(item['title'])}</h2><p>{E(item['instructions'])}</p><label for="editor-{identity}">Your {E(language)} source</label><textarea class="lab-editor" id="editor-{identity}" spellcheck="false" autocapitalize="off" autocomplete="off" rows="10">{E(item['starter'])}</textarea><div class="lab-actions"><button type="button" data-run disabled>Run tests</button><button type="button" data-stop disabled>Stop</button><button type="button" data-reset>Reset starter</button></div><p role="status" data-lab-status>Tests run only when you press Run. {'Python loads the optional self-hosted runtime (about 12 MB) on demand; allow up to 30 seconds on a slow device.' if language=='python' else 'JavaScript executes in a disposable Worker, never in the page.'}</p><pre class="lab-output" tabindex="0" role="region" aria-label="Test results and program output"><code data-lab-output></code></pre><details data-hint><summary>Hints</summary><ul>{hints}</ul></details><details data-solution><summary>Reference solution</summary><pre><code>{E(item['solution'])}</code></pre></details><details><summary>Test fixtures and expected results</summary><div class="table-scroll"><table><caption>{E(item['title'])} fixtures</caption><thead><tr><th>Case</th><th>Input</th><th>Expected</th></tr></thead><tbody>{fixtures}</tbody></table></div></details><p><a href="{url('examples/browser-labs/'+identity+('.py' if language=='python' else '.js'))}">Download the reference source</a> · <a href="{url(item['chapter']+'.html')}#q{item['topic']}">Review the lesson</a></p></article>''')
        folder=out/'examples/browser-labs';folder.mkdir(parents=True,exist_ok=True)
        (folder/(identity+('.py' if language=='python' else '.js'))).write_text(item['solution']+'\n')
    write('coding-labs.html','Browser coding labs','''<p class="eyebrow">IMPLEMENT · RUN · EXPLAIN</p><h1>Small programs. Observable results.</h1><p>Practice JavaScript and Python locally in this browser. A fresh Worker is terminated after the time limit or when you press Stop. Output is capped at 12,000 characters and source at 64,000 characters. A passing test is fixture evidence, not proof of general correctness.</p><aside class="failure-note"><strong>Execution limits:</strong> Workers keep the page responsive but are not a hardened security boundary. Run code you understand. Browsers impose their own memory limits; a large allocation can still exhaust memory. No server, credentials, package installation or external API is used. Python allows math, json, statistics, collections, itertools and functools imports. Real databases, network services, Docker and FastAPI run in downloadable local labs.</aside><noscript><p>JavaScript is required to run tests. Starters, solutions, fixtures and downloadable files remain readable below.</p></noscript><p>Python is optional and loaded from this site's runtime folder. If a downloaded copy omits it, use the local source downloads; core reading and JavaScript labs still work. <a href="runtime/NOTICE.txt">Runtime notices</a>.</p>'''+''.join(cards)+scripts)
    write('study.html','Your study evidence','''<p class="eyebrow">BROWSER-LOCAL STUDY RECORD</p><h1>Evidence guides your next review.</h1><p>No account, analytics, server sync or background reminders. IndexedDB stores a versioned event journal; localStorage is the fallback. Export before clearing browser data or switching devices. Private browsing may discard this record.</p><div class="practice-card"><h2>How the estimate works</h2><dl><dt><strong>Familiar</strong></dt><dd>A topic with recorded study activity.</dd><dt><strong>Practiced</strong></dt><dd>At least one passed deterministic check.</dd><dt><strong>Independent</strong></dt><dd>A recorded independent debugging or coding pass without hints, with a passing latest graded result.</dd><dt><strong>Mastered</strong></dt><dd>Two distinct independent checks passed at least 24 hours apart, and the latest graded result passed.</dd></dl><p>These are local estimates. An answer key or hints used in a session prevents that attempt from counting as independent. Subjective self-review never grants a graded pass. Failed checks schedule a review in one day; successful reviews use 1, 3, then doubled intervals capped at 90 days.</p></div><section class="practice-card"><h2>Your record</h2><p id="study-summary" role="status">Loading local evidence…</p><div id="study-due"></div><div id="study-history"></div><button id="export" type="button">Export progress</button><label class="import-label">Import progress<input id="import" type="file" accept="application/json,.json"></label><button id="reset-progress" type="button">Clear study record</button><p id="storage-status" role="status"></p></section><noscript><p>Your record is private browser data; JavaScript is required to access it. Continue reading chapters using the course menu.</p></noscript>'''+scripts+f'<script src="{url("study-catalogue.js")}" defer></script>')
    return {'assessments':len(assessments), 'browser_labs':len(labs)}
