"""Uncapped topic banks with bounded static pages, shards and coverage reports."""
from collections import Counter
from pathlib import Path
import html
import json
import math
import re

E = lambda value: html.escape(str(value), quote=True)
PAGE_SIZE = 40


def pages(slug, rows, render, write, url=lambda path:path):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Invalid bank slug')
    count=max(1,math.ceil(len(rows)/PAGE_SIZE))
    routes={row['id']:f'questions-{slug}-{i//PAGE_SIZE+1}.html#q{row["id"]}' for i,row in enumerate(rows)}
    for page in range(count):
        subset=rows[page*PAGE_SIZE:(page+1)*PAGE_SIZE]
        nav='<nav class="bank-pages" aria-label="Question pages">'+''.join(f'<a href="{url(f"questions-{slug}-{number}.html")}"'+(' aria-current="page"' if number==page+1 else '')+f'>{number}</a>' for number in range(1,count+1))+'</nav>'
        body=f'<p class="eyebrow">QUESTION BANK · {E(slug)}</p><h1>Questions: {E(slug.replace("-"," "))}</h1><p>{len(rows)} questions · page {page+1}/{count} · up to {PAGE_SIZE} full answers per page</p><p><a href="{url(slug+".html")}">Return to the chapter</a> · <a href="{url("question-bank.html")}">All subjects</a></p>'+nav
        body+='<label for="bank-filter">Filter this page by question or facet</label><input id="bank-filter" type="search" placeholder="Try debugging or authorization"><p id="bank-filter-status" role="status"></p><section aria-labelledby="bank-section-title"><h2 id="bank-section-title">Questions on this page</h2><div id="bank-items">'
        for row in subset:
            facets=' '.join(str(row.get(key,'')) for key in ('Q','domain','subdomain','difficulty','concept'))
            body+=f'<div data-bank-text="{E(facets.lower())}">'+render(row)+'</div>'
        body+='</div></section>'+nav
        write(f'questions-{slug}-{page+1}.html',f'{slug}: questions page {page+1}',body,slug)
    return routes, count


def build(out, chapters, render, write, url):
    routes={};counts={};coverage=[];seen={};duplicates=[]
    for chapter in chapters:
        mapped,count=pages(chapter['slug'],chapter['questions'],render,write,url)
        routes.update(mapped);counts[chapter['slug']]=count
        for row in chapter['questions']:
            normalized=re.sub(r'\W+',' ',row['Q'].casefold()).strip()
            if normalized in seen: duplicates.append([seen[normalized],row['id']])
            seen[normalized]=row['id']
        coverage.append({'chapter':chapter['slug'],'questions':len(chapter['questions']),'pages':count,
                         'facets':dict(Counter(q.get('difficulty','unclassified') for q in chapter['questions'])),
                         'enriched':sum('spoken' in q or q.get('answer_format')=='conceptual' for q in chapter['questions'])})
    (out/'questions').mkdir(exist_ok=True)
    for chapter in chapters:
        for index in range(0,len(chapter['questions']),PAGE_SIZE):
            (out/'questions'/f'{chapter["slug"]}-{index//PAGE_SIZE+1}.json').write_text(json.dumps(chapter['questions'][index:index+PAGE_SIZE],ensure_ascii=False)+'\n')
    report={'page_size':PAGE_SIZE,'total_questions':sum(len(c['questions']) for c in chapters),'subjects':coverage,'exact_duplicate_ids':duplicates}
    (out/'questions/coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    cards=''.join(f'<article class="map-card"><h2><a href="{url("questions-"+c["slug"]+"-1.html")}">{E(c["title"])}</a></h2><p>{len(c["questions"])} questions · {counts[c["slug"]]} pages · {sum("spoken" in q for q in c["questions"])} enriched answers</p></article>' for c in chapters)
    write('question-bank.html','Question bank','<p class="eyebrow">DISTINCT QUESTIONS · STABLE STUDY IDS</p><h1>Explore one subject at a time.</h1><p>This optional browser contains the deeper interview questions. Each chapter page includes its foundation questions and all deeper answers together. Counts come from source. Each bank page contains at most 40 full answers; no subject has a question-count cap. Legacy entries without calibrated facets are labeled unclassified in the coverage report. Search across subjects using the course search, or follow the static page links without JavaScript.</p><p><a href="'+url('questions/coverage.json')+'">Download the coverage report</a></p>'+cards)
    return routes, sum(counts.values())


def search_shards(out, entries, curriculum):
    directory=out/'search';directory.mkdir(exist_ok=True)
    tracks={slug:track['id'] for track in curriculum['tracks'] for slug in track['chapters']}
    shards=[]
    for track in [*curriculum['tracks'], {'id':'courses'}]:
        group=[entry for entry in entries if tracks.get(entry['slug'],entry.get('track'))==track['id']]
        for index in range(0,len(group),60):
            subset=group[index:index+60]
            # Metadata and searchable text, never whole expanded answer DOMs.
            name=f'{track["id"]}-{index//60+1}.json'
            (directory/name).write_text(json.dumps(subset,ensure_ascii=False,separators=(',',':'))+'\n')
            shards.append({'url':'search/'+name,'track':track['id'],'chapters':sorted({r['slug'] for r in subset}),'count':len(subset)})
    if sum(shard['count'] for shard in shards)!=len(entries):raise ValueError('Search entries contain an unmapped subject')
    (directory/'manifest.json').write_text(json.dumps({'version':1,'count':len(entries),'shards':shards},separators=(',',':'))+'\n')
