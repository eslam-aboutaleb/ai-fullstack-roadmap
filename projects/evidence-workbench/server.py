"""Loopback-only teaching API and built React assets. No external provider or real login."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import time

ROOT = Path(__file__).resolve().parent
TOKENS = {'demo-a': 'a', 'demo-b': 'b'}
DOCUMENTS = {'a': 'Café sale policy: refunds within 14 days. <b>Keep markup inert.</b>',
             'b': 'Owner B private sale policy: refunds within 30 days.'}


class Handler(SimpleHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *_):
        pass  # Do not log query strings, credentials or synthetic answer bodies.

    def json_response(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/health':
            return self.json_response(200, {'status': 'ready'})
        if urlsplit(self.path).path.startswith('/api/'):
            return self.json_response(404, {'error': 'Not found'})
        super().do_GET()

    def do_POST(self):
        if self.path != '/api/answer':
            return self.json_response(404, {'error': 'Not found'})
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            return self.json_response(403, {'error': 'Origin denied'})
        owner = TOKENS.get(self.headers.get('Authorization', '').removeprefix('Bearer '))
        if owner is None:
            return self.json_response(401, {'error': 'Demo identity required'})
        if self.headers.get('Content-Type') != 'application/json':
            return self.json_response(415, {'error': 'JSON required'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if self.headers.get('Transfer-Encoding') or not 0 < length <= 4096:
                return self.json_response(413, {'error': 'Request size limit'})
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict) or set(value) != {'query', 'requestId', 'scenario'}:
                raise ValueError('Unexpected fields')
            query, request_id, scenario = value['query'], value['requestId'], value['scenario']
            if not isinstance(query, str) or not query.strip() or len(query) > 500:
                raise ValueError('Invalid query')
            if not isinstance(request_id, str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,64}', request_id):
                raise ValueError('Invalid request identity')
            if scenario not in ('normal', 'slow', 'disconnect', 'malformed'):
                raise ValueError('Invalid fixture')
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.json_response(400, {'error': 'Invalid request contract'})
        # Scope before constructing any result. Caller cannot choose another owner.
        supported = 'policy' in query.lower() or 'refund' in query.lower()
        answer = DOCUMENTS[owner] if supported else 'No supported answer in the permitted documents.'
        self.send_response(200)
        self.send_header('Content-Type', 'application/x-ndjson; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        try:
            for seq, start in enumerate(range(0, len(answer), 12), 1):
                if scenario == 'slow':
                    time.sleep(0.12)
                event = {'requestId': request_id, 'seq': seq, 'type': 'delta', 'text': answer[start:start+12]}
                self.wfile.write((json.dumps(event, ensure_ascii=False)+'\n').encode()); self.wfile.flush()
                if scenario == 'malformed':
                    self.wfile.write(b'{invalid}\n'); self.wfile.flush(); return
            if scenario != 'disconnect':
                self.wfile.write((json.dumps({'requestId': request_id, 'seq': seq+1, 'type': 'done',
                    'citations': [owner+'-policy@1'] if supported else [], 'abstain': not supported})+'\n').encode())
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # Client cancellation stops presentation; no business effect exists.


def server(port=8787, host='127.0.0.1'):
    return ThreadingHTTPServer((host, port), partial(Handler, directory=str(ROOT/'dist')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--port', type=int, default=8787)
    parser.add_argument('--host', choices=['127.0.0.1','0.0.0.0'], default='127.0.0.1')
    args = parser.parse_args()
    with server(args.port, args.host) as httpd:
        print(f'Evidence workbench: http://127.0.0.1:{httpd.server_port}', flush=True)
        httpd.serve_forever()
