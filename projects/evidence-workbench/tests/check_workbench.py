"""Actual HTTP and Chromium acceptance flows against the compiled React application."""
from pathlib import Path
from threading import Thread
import importlib.util
import json
import time
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workbench_server', ROOT/'server.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def check():
    assert (ROOT/'dist/index.html').is_file(), 'Run npm ci && npm run build in the project first'
    with module.server(0) as httpd:
        thread = Thread(target=httpd.serve_forever, daemon=True); thread.start()
        origin = f'http://127.0.0.1:{httpd.server_port}'
        def request(body, token='demo-a', extra=None):
            headers = {'Content-Type':'application/json','Authorization':'Bearer '+token, **(extra or {})}
            req = urllib.request.Request(origin+'/api/answer', data=json.dumps(body).encode(), headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    return response.status, response.read().decode()
            except urllib.error.HTTPError as error:
                return error.code, error.read().decode()
        valid = {'query':'refund policy','requestId':'fixture-1','scenario':'normal'}
        status, body = request(valid)
        assert status == 200 and 'a-policy@1' in body and 'Owner B private' not in body
        assert request(valid, 'invalid')[0] == 401
        assert request({**valid,'owner':'b'})[0] == 400
        assert request({**valid,'query':'x'*501})[0] == 400
        assert request(valid, extra={'Origin':'https://untrusted.example'})[0] == 403
        assert 'b-policy@1' in request(valid,'demo-b')[1]
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={'width':390,'height':844})
            errors = []; page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(origin)
            page.get_by_role('button',name='Ask question').click()
            page.get_by_role('status').filter(has_text='Complete: evidence received.').wait_for()
            assert '<b>' in page.locator('#answer').inner_text()
            assert page.locator('#answer b').count() == 0
            page.locator('#scenario').select_option('slow')
            page.get_by_role('button',name='Ask question').click()
            page.wait_for_function("document.querySelector('#answer').textContent.length > 0")
            page.locator('#owner').select_option('b')
            assert page.locator('#answer').inner_text() == ''
            # A new identity owns later results; an older generation cannot reappear.
            page.locator('#scenario').select_option('normal')
            page.get_by_role('button',name='Ask question').click()
            page.get_by_role('status').filter(has_text='Complete: evidence received.').wait_for()
            assert '30 days' in page.locator('#answer').inner_text()
            assert '14 days' not in page.locator('#answer').inner_text()
            for scenario in ('disconnect','malformed'):
                page.locator('#scenario').select_option(scenario)
                page.get_by_role('button',name='Ask question').click()
                page.get_by_role('status').filter(has_text='Failed:').wait_for()
            page.locator('#scenario').select_option('slow')
            page.get_by_role('button',name='Ask question').click()
            page.wait_for_function("document.querySelector('#answer').textContent.length > 0")
            page.get_by_role('button',name='Cancel',exact=True).click()
            assert page.get_by_role('status').inner_text().startswith('Cancelled locally')
            page.locator('#scenario').select_option('normal')
            page.locator('#query').fill('unrelated unknown question')
            page.get_by_role('button',name='Ask question').click()
            page.get_by_role('status').filter(has_text='Complete: no supported answer.').wait_for()
            assert page.get_by_role('listitem').count() == 0
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            axe = ROOT.parents[1]/'node_modules/axe-core/axe.min.js'
            axe_checked=False
            if axe.is_file():
                page.add_script_tag(path=str(axe))
                result = page.evaluate("axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
                axe_checked=True
                assert not result['violations'], [(v['id'],v['description']) for v in result['violations']]
            # Keyboard controls remain usable after failure/cancel and responsive layout.
            page.locator('#owner').focus(); page.keyboard.press('Tab')
            assert page.locator('#query').evaluate('node => node === document.activeElement')
            page.screenshot(path='/tmp/roadmap-workbench-mobile.png',full_page=True)
            assert not errors, errors
            browser.close()
        httpd.shutdown(); thread.join(timeout=5)
    print(json.dumps({'workbench':'pass','typescript_compiled':True,'real_http':True,'owner_scope':'pass',
        'identity_switch':'pass','automated_accessibility':'pass' if axe_checked else 'not installed','failure_cancel_abstention':'pass','mobile_keyboard':'pass'}))


if __name__ == '__main__':
    check()
