"""Static transcripts with optional step controls, derived from tested state models."""
from pathlib import Path
import html
import json

ROOT=Path(__file__).resolve().parent.parent
FIXTURES=json.loads((ROOT/'content/simulations.json').read_text())
E=lambda value:html.escape(str(value),quote=True)
CHAPTERS={'sources':'asyncio','database-concurrency':'locking','foundations':'retrieval','agent-evaluation':'retries'}


def panel(identity,url):
    fixture=next(item for item in FIXTURES if item['id']==identity)
    transcript=''.join('<li><strong>'+E(step['label'])+'</strong>: '+E(step['detail'])+'</li>' for step in fixture['normal']['steps'])
    return f'''<section class="practice-card simulation" data-simulation="{identity}"><p class="eyebrow">DETERMINISTIC STATE SIMULATION</p><h2>Step through {E(identity)}</h2><p>A teaching model with explicit state transitions, not a running backend.</p><label>Scenario <select data-sim-scenario><option value="normal">Normal path</option><option value="failure">Failure or recovery path</option></select></label><label>Step <input type="range" data-sim-step min="0" max="{len(fixture['normal']['steps'])-1}" value="0"></label><div class="lab-actions"><button type="button" data-sim-prev>Previous</button><button type="button" data-sim-next>Next</button><button type="button" data-sim-reset>Reset</button></div><svg viewBox="0 0 600 80" role="img" aria-label="Current simulation transition"><rect x="5" y="5" width="590" height="70" rx="12" fill="var(--panel2)" stroke="var(--line)"/><text x="24" y="45" fill="var(--text)" data-sim-svg>{E(fixture['normal']['steps'][0]['label'])}</text></svg><div aria-live="polite"><h3 data-sim-label>{E(fixture['normal']['steps'][0]['label'])}</h3><p data-sim-detail>{E(fixture['normal']['steps'][0]['detail'])}</p></div><pre><code data-sim-state>{E(json.dumps(fixture['normal']['steps'][0]['state'],indent=2))}</code></pre><details><summary>Complete text transcript</summary><ol>{transcript}</ol><h3>Failure and recovery variant</h3><ol>{''.join('<li><strong>'+E(step['label'])+'</strong>: '+E(step['detail'])+'</li>' for step in fixture['failure']['steps'])}</ol></details></section><script src="{url('simulation-model.js')}" defer></script><script src="{url('simulation.js')}" defer></script>'''


def build(write,url):
    write('simulations.html','Deterministic system visualizers','<p class="eyebrow">SCHEDULE · LOCK · RETRIEVE · RECONCILE</p><h1>Follow state, not just arrows.</h1><p>All controls are keyboard operable. Motion is not required: step, reset, or read the complete transcripts without JavaScript. Failure variants change the model’s transitions.</p>'+''.join(panel(item['id'],url) for item in FIXTURES))
