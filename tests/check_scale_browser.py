"""A real no-JS browser navigates 1,200 generated fixture records."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
import argparse
import html
import sys
import tempfile
import json
import shutil
from playwright.sync_api import sync_playwright
from check_browser import Handler

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from question_bank import pages


def check(base_path=''):
    with tempfile.TemporaryDirectory() as directory:
        out=Path(directory)
        shutil.copy2(ROOT/'assets/js/course.js',out/'course.js')
        rows=[{'id':100000+i,'Q':f'Fixture {i}: input {i}, expected {i*i%97}', 'A':str(i*i%97)} for i in range(1200)]
        def write(name,title,body,active=''):
            (out/name).write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+html.escape(title)+'</title></head><body><main>'+body+'<script src="course.js" defer></script></main></body></html>')
        def render(row):
            return f'<article id="q{row["id"]}" data-question="{row["id"]}"><h2>{html.escape(row["Q"])}</h2><p>{row["A"]}</p></article>'
        routes,count=pages('stress',rows,render,write,lambda path:base_path.rstrip('/')+'/'+path if base_path else path)
        write('stress.html','Original anchors',''.join(f'<p id="q{r["id"]}"><a data-topic-redirect href="{routes[r["id"]]}">{r["id"]}</a></p>' for r in rows))
        write('question-bank.html','Subjects','<h1>Subjects</h1>')
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(out)))
        Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_port}'+base_path.rstrip('/')
        try:
            with sync_playwright() as playwright:
                browser=playwright.chromium.launch();page=browser.new_page(java_script_enabled=False)
                page.goto(base+'/questions-stress-1.html')
                assert page.locator('article').count()==40
                page.locator('nav').first.get_by_role('link',name='30',exact=True).click()
                assert page.locator('article').count()==40
                assert page.locator('#q101199').count()==1
                page.goto(base+'/stress.html#q100999')
                page.locator('#q100999 a').click()
                assert page.locator('#q100999').count()==1
                assert page.locator('article').count()<=40
                scripted=browser.new_page()
                scripted.goto(base+'/stress.html?mode=practice#q100999')
                scripted.wait_for_url('**/questions-stress-25.html?mode=practice#q100999')
                assert scripted.locator('#q100999').count()==1
                browser.close()
        finally:server.shutdown();server.server_close()
    print(json.dumps({'scale_browser':'pass','records':1200,'pages':30,'max_expanded_answers':40,'javascript_required':False,'base_path':base_path or '/'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base-path',default='');check(parser.parse_args().base_path)
