"""The exported trace must stay readable without becoming executable HTML."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def check():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT / '_site')))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.goto(f'http://127.0.0.1:{server.server_port}/examples/labs/agent_trace_reader.html')
            requests = []
            page.on('request', lambda request: requests.append(request.url))
            trace = {'trace': [{'seq': 1, 'kind': 'source', 'detail': {'text': '<img src=x onerror="window.traceExecuted=true">'}}]}
            page.locator('#trace').set_input_files({'name': 'trace.json', 'mimeType': 'application/json',
                                                  'buffer': json.dumps(trace).encode()})
            page.wait_for_function("document.querySelector('#status').textContent.startsWith('1 events')")
            assert '<img' in page.locator('#events pre').inner_text()
            assert page.locator('#events img').count() == 0
            assert not page.evaluate('Boolean(window.traceExecuted)') and requests == []
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.locator('#trace').set_input_files({'name': 'bad.json', 'mimeType': 'application/json', 'buffer': b'{}'})
            page.wait_for_function("document.querySelector('#status').textContent.includes('Expected')")
            assert page.locator('#events li').count() == 0
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(json.dumps({'trace_reader': 'pass', 'local_file_only': True, 'untrusted_text_escaped': True,
                      'mobile_wrapping': True, 'malformed_report_clears_old_trace': True}))


if __name__ == '__main__':
    check()
