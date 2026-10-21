"""1,200 distinct fixture records retain bounded data and direct chapter anchors."""
from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from question_data import build, search_shards, SHARD_SIZE


def check():
    rows = [{'id': 100000 + i, 'Q': f'Scale fixture {i}: compute {i} squared modulo 97?', 'A': str(i * i % 97)} for i in range(1200)]
    for base in ('', '/ai-fullstack-roadmap/'):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            assert build(out, [{'slug': 'stress', 'questions': rows}]) == 30
            chunks = list((out / 'questions').glob('stress-*.json'))
            assert all(len(json.loads(path.read_text())) <= SHARD_SIZE for path in chunks)
            actual = [row for path in chunks for row in json.loads(path.read_text())]
            assert {row['id'] for row in actual} == {row['id'] for row in rows}
            assert len(actual) == len(rows)
            entries = [{'id': row['id'], 'slug': 'stress', 'title': row['Q'], 'text': row['Q'],
                        'href': 'stress.html#q' + str(row['id'])} for row in rows]
            search_shards(out, entries, {'tracks': [{'id': 'stress-track', 'chapters': ['stress']}]})
            manifest = json.loads((out / 'search/manifest.json').read_text())
            assert manifest['count'] == 1200 and len(manifest['shards']) == 20
            indexed = [row for shard in manifest['shards'] for row in json.loads((out / shard['url']).read_text())]
            assert all(row['href'] == 'stress.html#q' + str(row['id']) for row in indexed)
            assert not list(out.glob('*.html')), 'Metadata generation must not recreate duplicate answer pages'
    print(json.dumps({'question_data_stress_entries': 1200, 'data_shards': 30, 'search_shards': 20,
                      'direct_chapter_routes': 'pass', 'duplicate_answer_pages': 0}))


if __name__ == '__main__':
    check()
