"""Check every reference catalog destination and where it is used in course content.

External HTTP is intentionally a manual/versioned audit, not a deterministic CI gate.
Run: python3 scripts/audit_references.py
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import argparse
from pathlib import Path
import json
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT/'content/shared/references.json'
OUT = ROOT/'docs/reference-link-audit.json'
CONTENT = ROOT/'content'


class PageHeadings(HTMLParser):
    def __init__(self):
        super().__init__(); self.capture = False; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('title', 'h1', 'h2'): self.capture = True
    def handle_endtag(self, tag):
        if tag in ('title', 'h1', 'h2'): self.capture = False
    def handle_data(self, data):
        if self.capture and sum(map(len, self.parts)) < 700: self.parts.append(data.strip())


def locations(identity, url):
    found = []
    for path in sorted(CONTENT.rglob('*.json')):
        if path == CATALOG: continue
        try: source = json.loads(path.read_text())
        except (UnicodeError, json.JSONDecodeError): continue
        def contains(value, parent_key=''):
            if isinstance(value, dict):
                return any(contains(child, key) for key, child in value.items())
            if isinstance(value, list):
                return any(contains(child, parent_key) for child in value)
            if not isinstance(value, str): return False
            if value == url or value == identity: return True
            return parent_key == 'links' and identity in {part.strip() for part in value.split(',')}
        if contains(source): found.append(str(path.relative_to(ROOT)))
    return found


def inspect(item):
    identity, (label, url) = item
    req = urllib.request.Request(url, headers={
        'User-Agent':'Mozilla/5.0 (compatible; roadmap-reference-audit/1.0)',
        'Accept':'text/html,application/xhtml+xml,*/*'})
    row = {'id':identity, 'label':label, 'url':url, 'content_uses':locations(identity,url),
           'checked_at_utc':datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            body = response.read(2_000_000)
            content_type = response.headers.get('Content-Type','')
            row.update(status=response.status, final_url=response.geturl(), content_type=content_type)
        if 'html' in content_type:
            parser=PageHeadings(); parser.feed(body.decode('utf-8','replace'))
            row['title_or_headings']=' '.join(filter(None,parser.parts))[:700]
        else: row['title_or_headings']=''
    except urllib.error.HTTPError as error:
        row.update(status=error.code, final_url=error.geturl(), error=str(error.reason))
    except Exception as error:
        row.update(status='ERROR', error=f'{type(error).__name__}: {error}')
    return row


def main():
    catalog=json.loads(CATALOG.read_text())
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retry-failed',action='store_true',help='Retry only rows not previously checked with a 200 response')
    args=parser.parse_args()
    previous={}
    if args.retry_failed and OUT.exists():
        saved=json.loads(OUT.read_text())
        previous={row['id']:{**row,'checked_at_utc':row.get('checked_at_utc',saved['checked_at_utc'])} for row in saved['references']}
    pending=[(key,value) for key,value in catalog.items()
             if not args.retry_failed or previous.get(key,{}).get('status') != 200 or previous.get(key,{}).get('url') != value[1]]
    with ThreadPoolExecutor(max_workers=12) as pool:
        checked=list(pool.map(inspect,pending))
    fresh={row['id']:row for row in checked}
    rows=[fresh.get(key,previous.get(key)) for key in catalog]
    if any(row is None for row in rows): raise ValueError('Retry mode is missing a result; run the full audit first')
    for row in rows:
        row['content_uses']=locations(row['id'],row['url'])
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'source':'content/shared/references.json', 'total':len(rows),
            'status_counts':{}, 'orphaned_references':[row['id'] for row in rows if not row['content_uses']],
            'references':rows}
    for row in rows:
        status=str(row['status']);report['status_counts'][status]=report['status_counts'].get(status,0)+1
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# Live reference-link audit','',
           f"Checked {report['checked_at_utc']} against content/shared/references.json.",
           f"{report['status_counts'].get('200',0)} of {report['total']} destinations have a successful HTTP 200 check. Per-reference timestamps in the JSON preserve earlier checks when retrying failures. Availability does not establish that a cited claim is supported.",'',
           '| ID | Reference | HTTP | Used by |','| --- | --- | ---: | --- |']
    for row in rows:
        uses=', '.join(row['content_uses']) or 'Catalog only'
        lines.append(f"| {row['id']} | [{row['label']}]({row.get('final_url',row['url'])}) | {row['status']} | {uses} |")
    lines += ['', '## Retrieved page titles and headings','',
              'The fetched titles/headings identify the page that responded; they do not replace checking the source against each claim.','']
    lines.extend(f"- {row['id']}: {row.get('title_or_headings') or row.get('error','No title available')}" for row in rows)
    lines += ['', '## Orphaned entries','',
              'An entry listed here has no exact ID or URL use in chapter/course content. Attach it to relevant teaching or remove it.','']
    lines.extend(f"- {identity}" for identity in report['orphaned_references'])
    (ROOT/'docs/reference-link-audit.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='references'},indent=2))


if __name__=='__main__': main()
