"""JS and no-JS browsers read 1,200 answers on their canonical chapter page."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import argparse
import html
import json
import shutil
import sys
import tempfile

from playwright.sync_api import sync_playwright
from check_browser import Handler

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from question_data import build


def check(base_path=''):
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory)
        shutil.copy2(ROOT / 'assets/js/course.js', out / 'course.js')
        rows = [{'id': 100000 + i, 'Q': f'Fixture {i}: input {i}, expected {i*i%97}', 'A': str(i*i%97)} for i in range(1200)]
        build(out, [{'slug': 'stress', 'questions': rows}])
        body = ''.join(f'<article id="q{r["id"]}" data-question="{r["id"]}"><h2>{html.escape(r["Q"])}</h2><details class="answer"><summary>View answer</summary><p>{r["A"]}</p></details></article>' for r in rows)
        links = '<nav><a href="#q100999">Question 1000</a><a href="#q101199">Question 1200</a></nav>'
        (out / 'stress.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Scale fixture</title></head><body><main><h1>All answers in the chapter</h1>' + links + body + '</main><script src="course.js" defer></script></body></html>')
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(out)))
        Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}' + base_path.rstrip('/')
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                for scripted in (False, True):
                    page = browser.new_page(java_script_enabled=scripted)
                    page.goto(base + '/stress.html')
                    assert page.locator('article').count() == 1200
                    page.get_by_role('link', name='Question 1200', exact=True).click()
                    assert page.url.endswith('/stress.html#q101199')
                    last = page.locator('#q101199 details')
                    if not last.evaluate('(node)=>node.open'):
                        last.locator('summary').click()
                    assert last.locator('p').inner_text() == str(1199*1199%97)
                    page.goto(base + '/stress.html?mode=practice#q100999')
                    assert page.url.endswith('/stress.html?mode=practice#q100999')
                    assert page.locator('#q100999').count() == 1
                    page.close()
                browser.close()
        finally:
            server.shutdown(); server.server_close()
    print(json.dumps({'scale_browser': 'pass', 'records': 1200, 'canonical_chapter_pages': 1,
                      'javascript_and_no_js': 'pass', 'base_path': base_path or '/'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--base-path', default='')
    check(parser.parse_args().base_path)
