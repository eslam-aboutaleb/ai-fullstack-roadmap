"""Package optional local projects without dependencies, builds or private files."""
from pathlib import Path
import html
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def load():
    rows = json.loads((ROOT/'content/projects.json').read_text())
    references = json.loads((ROOT/'content/shared/references.json').read_text())
    seen = set()
    for row in rows:
        identity = row['id']
        if not re.fullmatch('[a-z][a-z0-9-]+',identity) or identity in seen:
            raise ValueError('Invalid or duplicate local project identity')
        seen.add(identity)
        if not (ROOT/'projects'/identity/'README.md').is_file():
            raise ValueError('Project README missing')
        if not row['title'] or not row['description'] or not row['sections']:
            raise ValueError('Project teaching metadata missing')
        for section in row['sections']:
            if not section['title'] or not section['text']:
                raise ValueError('Incomplete project section')
        if any(key not in references for key in row['references']):
            raise ValueError('Unknown project reference')
    return rows


def files(identity):
    directory = ROOT/'projects'/identity
    allowed = {'.py','.ts','.tsx','.css','.json','.html','.md','.yaml'}
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory)
        if any(part in {'node_modules','dist','__pycache__','.git'} for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink() and (path.suffix in allowed or path.name in {'Dockerfile','.dockerignore'}):
            yield path, 'projects/'+identity+'/'+relative.as_posix()


def build(out, write, url):
    references = json.loads((ROOT/'content/shared/references.json').read_text())
    destination = out/'examples/projects'; destination.mkdir(parents=True,exist_ok=True)
    cards=[]
    for row in load():
        identity=row['id']; escape=lambda value:html.escape(value,quote=True)
        with zipfile.ZipFile(destination/(identity+'.zip'),'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for source,target in files(identity):
                archive.write(source,target)
            archive.write(ROOT/'LICENSE','LICENSE')
            if identity=='evidence-workbench':archive.write(ROOT/'requirements-dev.txt','requirements-dev.txt')
        body='<p class="eyebrow">OPTIONAL LOCAL PROJECT</p><h1>'+escape(row['title'])+'</h1><p>'+escape(row['description'])+'</p>'
        body+='<p><a href="'+url('examples/projects/'+identity+'.zip')+'">Download complete project source</a>. Extract the ZIP and read the included README for commands, milestones and review criteria. It runs locally; no application backend runs on GitHub Pages.</p>'
        for section in row['sections']:
            body+='<section class="prose"><h2>'+escape(section['title'])+'</h2><p>'+escape(section['text'])+'</p></section>'
        body+='<h2>Primary context</h2><ul>'+''.join('<li><a href="'+escape(references[key][1])+'">'+escape(references[key][0])+'</a></li>' for key in row['references'])+'</ul>'
        write('project-'+identity+'.html',row['title'],body)
        cards.append('<article class="map-card"><h2><a href="'+url('project-'+identity+'.html')+'">'+escape(row['title'])+'</a></h2><p>'+escape(row['description'])+'</p></article>')
    write('engineering-projects.html','Cumulative engineering projects','<h1>Build, break and defend the system.</h1><p>Use these projects alongside the engineering practicum. Save observed behavior and complete the independent milestones before requesting review.</p>'+''.join(cards))
    return len(cards)
