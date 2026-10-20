"""Chromium smoke tests against the generated static artifact (no runtime APIs)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import argparse
import json
import html

from playwright.sync_api import sync_playwright
from check_quote_fidelity import SOURCE_FIXTURES

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT/'_site'
KEY = 'ai-fullstack-roadmap-v1'


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/ai-fullstack-roadmap/'):
            self.path = self.path[len('/ai-fullstack-roadmap'):]
        super().do_GET()

    def log_message(self, *_):
        pass


def check(base_path=''):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    base = origin + base_path
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()
            page.set_default_timeout(8000)
            errors, failed_requests = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('response', lambda response: failed_requests.append(response.url) if response.status >= 400 else None)
            page.goto(base+'/index.html')
            page.wait_for_function("window.GuideAppReady === true")
            seed = {'learned': {'1': True}, 'bookmarks': {'2': True}, 'notes': {'3': 'keep my explanation'},
                    'reviews': {'1': {'interval': 3, 'reps': 2, 'nextReview': 1}},
                    'confidence': {'1': 4}, 'theme': 'warm', 'distractionFree': False}
            page.evaluate('([key, value]) => localStorage.setItem(key, JSON.stringify(value))', [KEY, seed])
            page.goto(base+'/tracks/backend.html')
            page.wait_for_function("window.GuideAppReady === true")
            page.keyboard.press('/')
            page.locator('#modal-query').fill('transaction')
            first = page.locator('#modal-results .result').first
            first.wait_for()
            assert first.get_attribute('href').startswith(base+'/'), first.get_attribute('href')
            assert '/tracks/' not in first.get_attribute('href')
            page.keyboard.press('Shift+Tab')
            assert page.evaluate("document.activeElement.closest('.search-modal') !== null")
            page.keyboard.press('Escape')
            page.goto(base+'/foundations.html')
            page.wait_for_function("window.GuideAppReady === true")
            page.locator('.notes summary').first.click()
            page.locator('[data-note]').first.fill('new note')
            saved = page.evaluate('window.GuideStudy.store.snapshot')
            for field in ('learned', 'bookmarks', 'reviews', 'confidence'):
                assert saved[field] == seed[field], (field, saved[field])
            # Active rating state must update at the clicked article, not a missing selector.
            rating = page.locator('[data-rating="5"]').first
            rating_id = rating.evaluate("el => el.closest('[data-question]').dataset.question")
            rating.click()
            assert 'active' in rating.get_attribute('class')
            # Compare source before and after executing the actual JS tokenizer in a real DOM.
            for fixture in SOURCE_FIXTURES:
                actual = page.evaluate('''source => {
                    const block = document.createElement('code');
                    block.textContent = source;
                    window.GuideCode.highlight(block);
                    window.GuideCode.highlight(block); // Idempotence.
                    if (block.querySelector('script')) throw new Error('Source became executable HTML');
                    return block.textContent;
                }''', fixture)
                assert actual == fixture, (fixture, actual)
            fixture_page = context.new_page()
            fixture_page.route('**/quote-fixture.html', lambda route: route.fulfill(
                content_type='text/html', body=f'<html><head><meta charset="utf-8"></head><body><div class="code-panel"><button class="copy">Copy code</button><pre><code>{html.escape(current_fixture)}</code></pre></div><script src="{base}/highlight.js"></script><script src="{base}/study-model.js"></script><script src="{base}/study-store.js"></script><script src="{base}/app.js"></script></body></html>'))
            for current_fixture in SOURCE_FIXTURES:
                fixture_page.goto(base+'/quote-fixture.html')
                fixture_page.wait_for_function('window.GuideAppReady === true')
                assert fixture_page.locator('code').text_content() == current_fixture, (repr(current_fixture), repr(fixture_page.locator('code').text_content()))
                fixture_page.locator('.copy').click()
                assert fixture_page.evaluate('navigator.clipboard.readText()') == current_fixture
            fixture_page.close()
            expected = page.locator('.code-panel code').first.text_content()
            page.locator('.copy').first.click()
            assert page.evaluate('navigator.clipboard.readText()') == expected
            # Modal traps Tab and restores focus to its opener.
            opener = page.locator('.toolbar a[href$="#search"]')
            opener.click()
            assert page.locator('#modal-query').evaluate('(el) => el === document.activeElement')
            # Lazy results can change the last tabbable control while loading.
            # Exercise wrapping after the initial result set has arrived.
            page.locator('#modal-results .result').first.wait_for()
            page.keyboard.press('Shift+Tab')
            page.keyboard.press('Tab')
            assert page.locator('#modal-query').evaluate('(el) => el === document.activeElement')
            focused_result = page.locator('#modal-results .result').first
            focused_result.focus()
            old_node = focused_result.element_handle()
            focused_href = focused_result.get_attribute('href')
            page.locator('#modal-query').dispatch_event('input')
            page.wait_for_function('(node) => !node.isConnected', arg=old_node)
            assert page.evaluate('document.activeElement.href') == focused_href
            page.keyboard.press('Escape')
            assert opener.evaluate('(el) => el === document.activeElement')
            page.goto(base+'/index.html')
            page.wait_for_function("window.GuideAppReady === true")
            with page.expect_download() as download:
                page.locator('#export').click()
            exported = json.loads(Path(download.value.path()).read_text())
            exported_snapshot = page.evaluate('events => window.GuideStudyModel.reduce(events)', exported['events'])
            assert exported_snapshot['reviews'] == seed['reviews']
            assert exported_snapshot['confidence'][rating_id] == 5
            page.locator('#import').set_input_files({'name': 'progress.json', 'mimeType': 'application/json', 'buffer': json.dumps(exported).encode()})
            page.wait_for_function("document.querySelector('#storage-status').textContent.includes('imported')")
            imported = page.evaluate('window.GuideStudy.store.snapshot')
            assert imported == exported_snapshot
            page.once('dialog', lambda dialog: dialog.dismiss())
            page.locator('#reset-progress').click()
            assert page.evaluate('window.GuideStudy.store.snapshot') == imported
            for malformed in ({'version':1, 'learned':None, 'notes':{}}, {'version':42}):
                page.locator('#import').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(malformed).encode()})
                page.wait_for_function("document.querySelector('#storage-status').textContent.startsWith('Import failed')")
                assert page.evaluate('window.GuideStudy.store.snapshot') == imported
            # Null schedules and blocked storage must not disable all interactions.
            page.evaluate('(key) => localStorage.setItem(key, JSON.stringify({reviews:null,confidence:null}))', KEY)
            page.reload()
            page.wait_for_function("window.GuideAppReady === true")
            page.locator('#theme').click()
            page.once('dialog', lambda dialog: dialog.accept())
            page.locator('#reset-progress').click()
            cleared = page.evaluate('window.GuideStudy.store.snapshot')
            assert not any(cleared[field] for field in ('learned', 'notes', 'bookmarks', 'reviews', 'confidence'))
            blocked = browser.new_context()
            blocked.add_init_script("Storage.prototype.getItem = Storage.prototype.setItem = () => { throw new DOMException('blocked'); }; indexedDB.open = () => { throw new DOMException('blocked'); };")
            blocked_page = blocked.new_page()
            blocked_page.goto(base+'/index.html')
            blocked_page.wait_for_function('window.GuideAppReady === true')
            blocked_page.locator('#theme').click()
            assert 'unavailable' in blocked_page.locator('#storage-status').inner_text()
            blocked.close()
            # Core rich reading, diagram captions, and complete flow transcript survive no JS.
            no_js = browser.new_context(java_script_enabled=False, viewport={'width':390,'height':844})
            reader = no_js.new_page()
            reader.goto(base+'/database-concurrency.html')
            assert reader.locator('.textbook-content').count() == 1
            assert reader.locator('figure figcaption').count() > 0
            assert 'conflict' in reader.locator('.textbook-content').inner_text()
            reader.get_by_text('Read the complete walkthrough transcript', exact=True).click()
            assert reader.locator('details[open]').count() > 0
            assert reader.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Mobile horizontal overflow'
            no_js.close()
            assert not errors, errors
            assert not failed_requests, failed_requests
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(json.dumps({'browser':'chromium', 'base_path':base_path or '/', 'source_fixtures':len(SOURCE_FIXTURES),
                      'storage_roundtrip':'pass','track_progress_preservation':'pass','clipboard':'pass',
                      'search_focus':'pass','mobile_no_js':'pass','console_errors':0}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-path', default='')
    check(parser.parse_args().base_path.rstrip('/'))
