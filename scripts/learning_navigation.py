"""Small, progressively enhanced navigation for long interview-led chapters."""
import html
from interview_teaching import teaching_title

E = lambda value: html.escape(str(value), quote=True)


def question_finder(chapter, url):
    rows = []
    for group, label in (('lessons', 'Foundation'), ('questions', 'Deeper')):
        for question in chapter[group]:
            advanced = question.get('difficulty') == 'advanced design scenario'
            kind = 'Advanced scenario' if advanced else label
            title = teaching_title(question)
            rows.append(f'<li data-finder-kind="{kind}" data-finder-text="{E(title.lower())}"><a href="#q{question["id"]}">{E(title)}</a><small>{kind}</small></li>')
    return f'''<details class="question-finder" id="question-finder"><summary>Find a question in this chapter · {len(rows)} questions</summary><p>Start with foundations, then explain a design under constraints. Select a question to jump to its answer.</p><div class="finder-controls" hidden><label for="chapter-question-query">Search question titles<input id="chapter-question-query" type="search" placeholder="Try context, retry or metadata"></label><label for="chapter-question-kind">Question type<select id="chapter-question-kind"><option value="">All questions</option><option>Foundation</option><option>Deeper</option><option>Advanced scenario</option></select></label><button type="button" id="chapter-question-reset">Clear filters</button></div><p id="chapter-question-count" role="status">{len(rows)} questions</p><p id="chapter-question-empty" hidden>No matching questions. Try fewer words or clear the filters.</p><ul class="finder-results">{''.join(rows)}</ul><p><a href="{url('design-scenarios.html')}">Practice advanced system-design scenarios across chapters →</a></p></details>'''


def scenario_page(chapters, url):
    sections = []
    for chapter in chapters:
        questions = [q for q in chapter['questions'] if q.get('difficulty') == 'advanced design scenario']
        if questions:
            links = ''.join(f'<li><a href="{url(chapter["slug"]+".html")}#q{q["id"]}">{E(q["Q"])}</a></li>' for q in questions)
            sections.append(f'<section class="map-card"><h2>{E(chapter["title"])}</h2><ul>{links}</ul></section>')
    return '''<p class="eyebrow">ADVANCED INTERVIEW PRACTICE</p><h1>Design under real constraints.</h1><p class="subtitle">Work through context limits, large-file ingestion, permission-aware retrieval, bounded agents, atomic publication, job recovery, streaming durability, evaluation validity, entity identity, privacy and data contracts. Each scenario links to a detailed answer, a design diagram and a failure exercise in its chapter.</p><section class="prose"><h2>How to practice a design answer</h2><ol><li>State the input, scale, latency target and authorization boundary.</li><li>Draw the data path and calculate the tightest resource budget.</li><li>Trace a crash, retry, cancellation and stale result.</li><li>Explain the simplest design that meets the requirement and what evidence would justify more complexity.</li><li>Open the answer, compare assumptions, then implement the proposed failure exercise.</li></ol><p>These are worked engineering designs, not measured production benchmarks. Follow chapter prerequisites if a mechanism is unfamiliar.</p><h2>Which execution model fits?</h2><ul><li><strong>Known sequence:</strong> use a durable workflow for upload, parsing, embedding and publication.</li><li><strong>Adaptive investigation:</strong> consider one bounded agent for repository diagnosis or iterative evidence gathering.</li><li><strong>Independent investigations:</strong> compare ordinary parallel calls with specialist agents, including synthesis cost.</li><li><strong>Irreversible business effects:</strong> keep authorization and commitment in deterministic services, even if an agent proposes the action.</li></ul></section>''' + ''.join(sections)
