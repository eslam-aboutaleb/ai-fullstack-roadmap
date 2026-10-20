"""End-to-end evidence, storage recovery and disposable Worker execution."""
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import argparse
import json
import sys
from playwright.sync_api import sync_playwright
from check_browser import Handler

ROOT = Path(__file__).resolve().parent.parent


def check(base_path=''):
    server = ThreadingHTTPServer(('127.0.0.1',0), partial(Handler,directory=str(ROOT/'_site')))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'+base_path.rstrip('/')
    def visit(page,path):
        page.goto(base+'/'+path)
        page.wait_for_function('window.GuideAppReady === true')
    def snapshot(page):
        return page.evaluate('window.GuideStudy.store.snapshot')
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            context=browser.new_context()
            page=context.new_page(); page.set_default_timeout(10000)
            errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
            remote=[]; context.on('request',lambda request:remote.append(request.url) if not request.url.startswith('http://127.0.0.1:') and not request.url.startswith('blob:') else None)
            context.add_init_script("""if (!sessionStorage.getItem('seeded')) {
              localStorage.setItem('ragnor-learning-v1',JSON.stringify({learned:{2:true},notes:{2:'old note'}}));
              localStorage.setItem('ai-fullstack-roadmap-v1',JSON.stringify({learned:{1:true},notes:{1:'newer note'}}));
              sessionStorage.setItem('seeded','yes');
            }""")
            requests=[]; page.on('request',lambda request:requests.append(request.url))
            visit(page,'assessments.html')
            assert not any('/search/' in url for url in requests), 'Search shards loaded before a search'
            page.locator('#practice-order').select_option('seeded'); page.locator('#practice-seed').fill('123')
            page.locator('#order-practice').click()
            first_order=page.locator('[data-assessment]').evaluate_all('(cards)=>cards.map(card=>card.dataset.assessment)')
            page.locator('#order-practice').click()
            assert page.locator('[data-assessment]').evaluate_all('(cards)=>cards.map(card=>card.dataset.assessment)')==first_order
            assert page.evaluate('window.GuideStudy.store.status.backend')=='IndexedDB'
            assert snapshot(page)['notes']=={'1':'newer note','2':'old note'}
            assert page.evaluate('window.GuideStudyModel.mastery(window.GuideStudy.store.snapshot,1).stage')=='Familiar'
            card=page.locator('[data-assessment="cross-tenant-read"]')
            card.locator('input[value="1"]').check(); card.locator('[data-grade]').click()
            page.wait_for_function('window.GuideStudy.store.snapshot.attempts.length === 1 && window.GuideStudy.store.snapshot.reviews[181] !== undefined')
            assert 'Not yet' in card.locator('[data-feedback]').inner_text()
            assert snapshot(page)['reviews']['181']['interval']==1
            card.locator('input[value="2"]').check(); card.locator('[data-grade]').click()
            page.wait_for_function('window.GuideStudy.store.snapshot.attempts.length === 2')
            assert page.evaluate('window.GuideStudyModel.mastery(window.GuideStudy.store.snapshot,181).stage')=='Independent'
            page.evaluate('window.GuideStudy.store.flush()')
            # Two tabs edit separate fields simultaneously; refresh reads both from IDB.
            second=context.new_page(); visit(second,'study.html')
            page.evaluate("window.GuideStudy.store.set('notes','7','tab A')")
            second.evaluate("window.GuideStudy.store.set('bookmarks','8',true)")
            page.wait_for_function("window.GuideStudy.store.snapshot.bookmarks[8] === true")
            second.wait_for_function("window.GuideStudy.store.snapshot.notes[7] === 'tab A'")
            visit(page,'study.html'); assert snapshot(page)['notes']['7']=='tab A'; assert snapshot(page)['bookmarks']['8']
            assert 'cross-tenant-read' in page.locator('#study-history').inner_text()
            # Export/import preserves attempts and event identity, including on another device/profile.
            exported=page.evaluate('window.GuideStudy.store.export()')
            portable=browser.new_context(); imported_page=portable.new_page(); visit(imported_page,'study.html')
            imported_page.evaluate('value => window.GuideStudy.store.import(value)',exported)
            assert snapshot(imported_page)==snapshot(page)
            imported_page.reload(); imported_page.wait_for_function('window.GuideAppReady === true')
            assert snapshot(imported_page)==snapshot(page)
            portable.close()
            # The JS reference solution passes in a worker; an infinite loop is terminated.
            visit(page,'coding-labs.html')
            lab=page.locator('[data-lab="rrf-ranking"]')
            solution=page.evaluate("window.GUIDE_PRACTICE.labs.find(l=>l.id==='rrf-ranking').solution")
            lab.locator('textarea').fill(solution); lab.locator('[data-run]').click()
            page.wait_for_function("document.querySelector('[data-lab=rrf-ranking] [data-lab-status]').textContent.startsWith('Passed:')")
            assert '4/4' in lab.locator('[data-lab-status]').inner_text()
            lab.locator('textarea').fill('function solve() { while (true) {} }');lab.locator('[data-run]').click()
            page.wait_for_function("document.querySelector('[data-lab=rrf-ranking] [data-lab-status]').textContent.startsWith('Time limit')")
            assert lab.locator('[data-run]').is_enabled()
            lab.locator('textarea').fill('console.log("x".repeat(6000)); function solve() { return []; }');lab.locator('[data-run]').click()
            page.wait_for_function("document.querySelector('[data-lab=rrf-ranking] [data-lab-status]').textContent.startsWith('Not yet:')")
            assert 'output truncated' not in lab.locator('[data-lab-output]').inner_text()
            lab.locator('textarea').fill('function solve() { console.log("x".repeat(50000)); return []; }');lab.locator('[data-run]').click()
            page.wait_for_function("document.querySelector('[data-lab=rrf-ranking] [data-lab-status]').textContent.startsWith('Not yet:')")
            assert len(lab.locator('[data-lab-output]').inner_text())<16000
            assert 'output truncated' in lab.locator('[data-lab-output]').inner_text()
            lab.locator('textarea').fill('function solve() { while(true){} }');lab.locator('[data-run]').click();lab.locator('[data-stop]').click()
            assert lab.locator('[data-lab-status]').inner_text().startswith('Stopped')
            lab.locator('[data-reset]').click();assert 'Return the fused' in lab.locator('textarea').input_value()
            # Hints prevent independent evidence even if all tests pass.
            auth=page.locator('[data-lab="authorized-confirmation"]')
            auth.locator('[data-hint] summary').click()
            auth.locator('textarea').fill(page.evaluate("window.GUIDE_PRACTICE.labs.find(l=>l.id==='authorized-confirmation').solution"))
            auth.locator('[data-run]').click()
            page.wait_for_function("document.querySelector('[data-lab=authorized-confirmation] [data-lab-status]').textContent.startsWith('Passed:')")
            assert 'Assisted' in auth.locator('[data-lab-status]').inner_text()
            # Real self-hosted Pyodide, not a mocked Python result.
            for identity in ('retrieval-metrics','attention-weights'):
                python=page.locator(f'[data-lab="{identity}"]')
                python.locator('textarea').fill(page.evaluate('id => window.GUIDE_PRACTICE.labs.find(l=>l.id===id).solution',identity))
                python.locator('[data-run]').click()
                page.wait_for_function('id => document.querySelector(`[data-lab="${id}"] [data-lab-status]`).textContent.startsWith("Passed:")',arg=identity,timeout=35000)
            # A denied import returns a useful failure, without attempting pip or network.
            python=page.locator('[data-lab="retrieval-metrics"]')
            python.locator('textarea').fill('import socket\ndef solve(data): return {}')
            python.locator('[data-run]').click()
            page.wait_for_function("document.querySelector('[data-lab=retrieval-metrics] [data-lab-status]').textContent.startsWith('Execution failed')",timeout=35000)
            assert 'allows only' in python.locator('[data-lab-output]').inner_text()
            # Corrupt legacy data recovers other valid history; blocked IDB uses localStorage.
            fallback=browser.new_context()
            fallback.add_init_script("indexedDB.open=()=>{throw new Error('blocked')}; localStorage.setItem('ai-fullstack-roadmap-v1','bad JSON');")
            fallback_page=fallback.new_page();visit(fallback_page,'study.html')
            fallback_page.evaluate("window.GuideStudy.store.set('notes','1','fallback survives')")
            fallback_page.reload();fallback_page.wait_for_function('window.GuideAppReady === true')
            assert snapshot(fallback_page)['notes']['1']=='fallback survives'
            assert fallback_page.evaluate('window.GuideStudy.store.status.backend')=='localStorage'
            # Importing an older copy of the same event must not regress fallback
            # persistence, even though the in-memory merge already chose the new one.
            fallback_page.evaluate('''async () => {
                const event={id:'fallback-conflict',kind:'set',field:'notes',topic:'2',time:Date.now(),value:'new copy'};
                await window.GuideStudy.store.import({version:3,events:[event]});
                await window.GuideStudy.store.import({version:3,events:[{...event,time:event.time-1,value:'old copy'}]});
            }''')
            fallback_page.reload();fallback_page.wait_for_function('window.GuideAppReady === true')
            assert snapshot(fallback_page)['notes']['2']=='new copy'
            fallback.close()
            visit(page,'simulations.html')
            locking=page.locator('[data-simulation=locking]')
            locking.locator('[data-sim-scenario]').select_option('failure')
            locking.locator('input[type=range]').focus(); page.keyboard.press('End')
            assert '"created": 2' in locking.locator('[data-sim-state]').inner_text()
            locking.locator('[data-sim-reset]').click()
            assert 'Step 1/' in locking.locator('[data-sim-label]').inner_text()
            visit(page,'course-python-values.html')
            course_id=page.locator('[data-note]').first.get_attribute('data-note')
            page.locator('.notes summary').first.click(); page.locator('[data-note]').first.fill('new course unit note')
            page.evaluate('window.GuideStudy.store.flush()')
            page.reload();page.wait_for_function('window.GuideAppReady === true')
            assert snapshot(page)['notes'][course_id]=='new course unit note'
            stale=next(event for event in page.evaluate('window.GuideStudy.store.export().events') if event.get('field')=='notes')
            page.evaluate('window.GuideStudy.store.clear()')
            page.evaluate('window.GuideStudy.store.flush()')
            exported_after=page.evaluate('window.GuideStudy.store.export()')
            assert len(exported_after['events'])==1 and exported_after['events'][0]['kind']=='reset'
            assert page.evaluate("localStorage.getItem('ai-fullstack-roadmap-v1')") is None
            second.wait_for_function('Object.keys(window.GuideStudy.store.snapshot.notes).length === 0')
            second.evaluate('event => window.GuideStudy.store.import({version:3,events:[event]})',stale)
            assert not snapshot(second)['notes']
            stored=page.evaluate("""() => new Promise((resolve,reject) => {
                const request=indexedDB.open('ai-fullstack-study',3);
                request.onsuccess=()=>{const db=request.result;const read=db.transaction('events').objectStore('events').getAll();read.onsuccess=()=>{resolve(read.result);db.close();};};request.onerror=()=>reject(request.error);
            })""")
            assert len(stored)==1 and stored[0]['kind']=='reset',stored
            assert not remote,remote
            assert not errors,errors
            context.close();browser.close()
    finally:
        server.shutdown();server.server_close()
    print(json.dumps({'learning_browser':'pass','base_path':base_path or '/', 'storage':'IndexedDB + localStorage fallback', 'two_tab_merge':'pass','portable_attempts':'pass','javascript_worker':'pass','python_wasm':'pass','timeout_stop_output_limits':'pass','evidence_mastery':'pass'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base-path',default='');check(parser.parse_args().base_path)
