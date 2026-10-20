"""Automated WCAG-oriented template smoke checks; manual review remains separate."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import argparse
import json
from playwright.sync_api import sync_playwright
from check_browser import Handler

ROOT=Path(__file__).resolve().parent.parent


def check(base_path=''):
    axe=ROOT/'node_modules/axe-core/axe.min.js'
    if not axe.exists():raise RuntimeError('Run npm ci to install the pinned test-only accessibility tool')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'_site')))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'+base_path.rstrip('/')
    violations=[];checked=0
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch();page=browser.new_page()
            paths=['index.html','foundations.html','assessments.html','coding-labs.html','study.html','simulations.html','questions-foundations-1.html','tracks/backend.html','course-gradients-optimization.html','capstone-transaction-api.html','curriculum-map.html','design-system.html']
            for path in paths:
                page.goto(base+'/'+path);page.wait_for_function('window.GuideAppReady === true')
                page.add_script_tag(path=str(axe))
                for theme in ('light','dark','warm') if path=='index.html' else ('light',):
                    page.evaluate("theme => window.GuideStudy.store.set('theme','global',theme)",theme)
                    result=page.evaluate("async () => (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations")
                    checked+=1
                    for item in result:
                        violations.append({'page':path,'theme':theme,'rule':item['id'],'impact':item['impact'],'nodes':[{'target':n['target'],'reason':n.get('failureSummary','')} for n in item['nodes'][:5]]})
            browser.close()
    finally:server.shutdown();server.server_close()
    if violations:
        print(json.dumps(violations,indent=2));raise AssertionError(f'{len(violations)} accessibility rule failures')
    print(json.dumps({'automated_accessibility':'pass','template_theme_checks':checked,'rules':'WCAG 2 A/AA, 2.1 AA, 2.2 AA','manual_screen_reader_review':'pending'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base-path',default='');check(parser.parse_args().base_path)
