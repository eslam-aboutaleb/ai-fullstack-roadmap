"""Build and navigate 1,200 fixture entries without publishing filler content."""
from pathlib import Path
from html.parser import HTMLParser
import html
import json
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from question_bank import pages, search_shards, PAGE_SIZE


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.links=[];self.answers=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        fields=dict(attrs)
        if fields.get('data-question'):self.ids.append(int(fields['data-question']))
        if tag=='article':self.answers+=1
        if fields.get('href'):self.links.append(fields['href'])


def check():
    # Distinct identity and input/output cases test delivery, not editorial depth.
    rows=[{'id':100000+i,'Q':f'Scale fixture {i}: compute {i} squared modulo 97?', 'A':str(i*i%97)} for i in range(1200)]
    for base in ('','/ai-fullstack-roadmap/'):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory); (out/'stress.html').write_text('<h1>Legacy chapter</h1>')
            (out/'question-bank.html').write_text('<h1>Subjects</h1>')
            def write(name,title,body,active=''):
                (out/name).write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+html.escape(title)+'</title></head><body><main>'+body+'</main></body></html>')
            def render(row):
                return f'<article id="q{row["id"]}" data-question="{row["id"]}"><h2>{html.escape(row["Q"])}</h2><p>{row["A"]}</p></article>'
            routes,count=pages('stress',rows,render,write,lambda path:base+path)
            assert count==30 and len(routes)==1200
            all_ids=[]
            for path in out.glob('questions-stress-*.html'):
                page=Page(path.read_text());all_ids.extend(page.ids)
                assert page.answers<=PAGE_SIZE
                assert path.stat().st_size<150000,('fixture page budget',path)
                for link in page.links:
                    local=link[len(base):] if base and link.startswith(base) else link
                    assert (out/local.split('#')[0]).is_file(),link
            assert set(all_ids)=={r['id'] for r in rows} and len(all_ids)==len(set(all_ids))
            for row in rows:
                filename,anchor=routes[row['id']].split('#')
                assert f'id="{anchor}"' in (out/filename).read_text()
            entries=[{'id':row['id'],'slug':'stress','title':row['Q'],'text':row['Q'],'href':routes[row['id']]} for row in rows]
            search_shards(out,entries,{'tracks':[{'id':'stress-track','chapters':['stress']}]})
            manifest=json.loads((out/'search/manifest.json').read_text())
            assert manifest['count']==1200 and len(manifest['shards'])==20
            assert all(len(json.loads((out/s['url']).read_text()))<=60 for s in manifest['shards'])
    print(json.dumps({'question_bank_stress_entries':1200,'pages':30,'search_shards':20,'page_size':40,'stable_routes':'pass','root_and_pages_base':'pass'}))


if __name__=='__main__':check()
