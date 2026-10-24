"""Package only the public static site, excluding private authoring and Git data."""
from pathlib import Path
import shutil, json, html
root=Path(__file__).resolve().parent.parent
source=root/'_build'
content=root/'content'
out=root/'_site'
if out.exists(): shutil.rmtree(out)
out.mkdir()
for pattern in ('*.html','*.css','*.js','*.svg'):
    for path in source.glob(pattern): shutil.copy2(path,out/path.name)
for name in ('.nojekyll','LICENSE'):
    if (source/name).exists(): shutil.copy2(source/name,out/name)
if (source/'manifest.json').exists(): shutil.copy2(source/'manifest.json',out/'manifest.json')
else:
    out.joinpath('manifest.json').write_text(json.dumps({'note':'manifest not generated in this environment'},indent=2)+'\n')
for name in ('diagrams','examples','runtime','search','questions'):
    if (source/name).exists(): shutil.copytree(source/name,out/name)
# Track landing pages (built here so they persist in _site/)
curriculum = json.loads((content/'curriculum.json').read_text())
CURR = curriculum['chapters']
import sys
sys.path.insert(0, str(root/'scripts'))
from course_data import load
CHAPTERS = load()
BY = {c['slug']:c for c in CHAPTERS}
MAX_ID = max(json.loads((content/'shared/study_ids.json').read_text()).values())
E = lambda value: html.escape(str(value), quote=True)
def reading_minutes(c):
  words=sum(len(str(q.get(k,'')).split()) for q in c['lessons']+c['questions'] for k in ('Q','explain','example','takeaway','A','Why','Risk','Trade','Try'))
  return max(1,round(words/180))
(out/'tracks').mkdir(exist_ok=True)
for track in curriculum['tracks']:
  items=''
  for slug in track['chapters']:
    c=BY[slug];entry=CURR[slug];mins=reading_minutes(c)
    # Count lessons with full rigorous schema for progress
    has_rigorous = any(q.get('conceptual_narrative') for q in c.get('lessons', []))
    pre=''.join(f'<a href="../{p+".html"}">{E(BY[p]["title"])}</a>' for p in entry['prerequisites'])
    badge = '<span class="track-badge complete">Enriched lesson present</span>' if has_rigorous else '<span class="track-badge pending">Standard</span>'
    items+=f'<article class="track-chapter"><h2><a href="../{slug+".html"}">{E(c["title"])}</a></h2>{badge}<p>{E(c["goal"])}</p><p><span class="track-meta">{mins} min read · {len(c["lessons"])} lessons · {len(c["questions"])} practice</span></p><p><strong>Prerequisites:</strong> {pre or "None — start here"}</p><p class="track-meta">Competency: {E(entry["competency"])}</p></article>'
  track_page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(track["title"])} · AI Engineering Roadmap</title><link rel="icon" type="image/svg+xml" sizes="any" href="../favicon.svg"><link rel="stylesheet" href="../style.css"><script src="../highlight.js" defer></script><script src="../search-loader.js" defer></script><script src="../study-model.js" defer></script><script src="../study-store.js" defer></script><script src="../app.js" defer></script><script src="../course.js" defer></script></head><body data-question-count="{MAX_ID}"><a class="skip" href="#main">Skip to content</a><main id="main" tabindex="-1"><section class="track-page"><a href="../index.html">Learning journey</a> · <a href="../index.html#search">Search course</a><div class="track-header"><h1>{E(track["title"])}</h1><p class="track-level">{E(track["level"])} · {E(track["description"])}</p><p class="track-meta">Entry point: <a href="../{track['entry_point']+".html"}">{E(BY[track['entry_point']]["title"])}</a></p><p class="track-meta">Prerequisite-ordered track · {len(track['chapters'])} chapters</p></div><div class="track-chapters">{items}</div></section></main></body></html>'''
  (out/'tracks'/f'{track["id"]}.html').write_text(track_page)
print('Static Pages artifact ready')
