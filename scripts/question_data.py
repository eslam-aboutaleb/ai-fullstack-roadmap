"""Static question metadata shards and lazy search; answers live in chapters."""
from collections import Counter
import json
import re

SHARD_SIZE = 40


def build(out, chapters):
    directory=out/'questions';directory.mkdir(exist_ok=True)
    coverage=[];seen={};duplicates=[];shards=0
    for chapter in chapters:
        rows=chapter['questions']
        for row in rows:
            key=re.sub(r'\W+',' ',row['Q'].casefold()).strip()
            if key in seen:duplicates.append([seen[key],row['id']])
            seen[key]=row['id']
        count=0
        for index in range(0,len(rows),SHARD_SIZE):
            (directory/f"{chapter['slug']}-{index//SHARD_SIZE+1}.json").write_text(json.dumps(rows[index:index+SHARD_SIZE],ensure_ascii=False)+'\n')
            count+=1
        shards+=count
        coverage.append({'chapter':chapter['slug'],'questions':len(rows),'shards':count,'facets':dict(Counter(q.get('difficulty','unclassified') for q in rows)),'enriched':sum('spoken' in q or q.get('answer_format')=='conceptual' for q in rows)})
    report={'shard_size':SHARD_SIZE,'total_questions':sum(len(c['questions']) for c in chapters),'subjects':coverage,'exact_duplicate_ids':duplicates}
    (directory/'coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    return shards

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
