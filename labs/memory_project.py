"""Versioned local episodic/fact memory, scoped retrieval and erasure project.

Python 3.11+, standard library. The caller supplies trusted local owner identity;
this CLI is not a network authentication service. Hashed character vectors are
an executable retrieval baseline, not learned semantic embeddings or an LLM.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import sqlite3
import tempfile

from agent_memory_lifecycle import Memory, Principal


def features(text):
    text = ' '.join(re.findall(r'\w+', text.casefold()))
    return Counter(text[i:i + 3] for i in range(max(0, len(text) - 2)))


def cosine(left, right):
    norm = math.sqrt(sum(v * v for v in left.values()) * sum(v * v for v in right.values()))
    return sum(value * right.get(key, 0) for key, value in left.items()) / norm if norm else 0.0


class MemoryProject(Memory):
    def __init__(self, connection, principal):
        super().__init__(connection, principal)
        self.db.execute('''CREATE TABLE IF NOT EXISTS projections (
            owner TEXT NOT NULL, key TEXT NOT NULL, fact_id INTEGER NOT NULL,
            text TEXT NOT NULL, vector TEXT NOT NULL, PRIMARY KEY(owner,key))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS epochs (
            owner TEXT PRIMARY KEY, generation INTEGER NOT NULL)''')
        self.db.commit()

    def _refresh(self, key):
        owner = self.principal.owner
        row = self.db.execute('''SELECT id,value FROM facts WHERE owner=? AND key=?
            ORDER BY valid_at DESC,recorded_at DESC,id DESC LIMIT 1''', (owner, key)).fetchone()
        if row:
            text = key + ' ' + row[1]
            self.db.execute('''INSERT INTO projections VALUES (?,?,?,?,?)
                ON CONFLICT(owner,key) DO UPDATE SET fact_id=excluded.fact_id,
                text=excluded.text,vector=excluded.vector''', (owner, key, row[0], text, json.dumps(features(text))))
        else:
            self.db.execute('DELETE FROM projections WHERE owner=? AND key=?', (owner, key))
        self.db.execute('''INSERT INTO epochs VALUES (?,1) ON CONFLICT(owner)
            DO UPDATE SET generation=generation+1''', (owner,))
        self.db.commit()

    def remember(self, key, value, **kwargs):
        inserted = super().remember(key, value, **kwargs)
        if inserted:
            self._refresh(key)
        return inserted

    def correct(self, key, value, **kwargs):
        if not self.db.execute('SELECT 1 FROM facts WHERE owner=? AND key=?', (self.principal.owner, key)).fetchone():
            raise ValueError('correction requires an existing owner-scoped fact')
        return self.remember(key, value, **kwargs)

    def recall(self, key, *, valid_at, known_at):
        # Select the latest eligible version BEFORE checking expiry; an expired
        # correction must not resurrect an older preference.
        row = self.db.execute('''SELECT value,source,valid_at,recorded_at,expires_at FROM facts
            WHERE owner=? AND key=? AND valid_at<=? AND recorded_at<=?
            ORDER BY valid_at DESC,recorded_at DESC,id DESC LIMIT 1''',
            (self.principal.owner, key, valid_at, known_at)).fetchone()
        if not row or (row[4] is not None and row[4] <= valid_at):
            return None
        return dict(zip(('value', 'source', 'valid_at', 'recorded_at'), row[:4]))

    def search(self, query, *, valid_at, known_at, mode='hybrid', limit=5):
        if mode not in {'recency', 'exact', 'lexical', 'hybrid'} or not 1 <= limit <= 100:
            raise ValueError('unsupported retrieval mode or result limit')
        # Do not search a global top-k and post-filter. Candidate membership and
        # current version come from this trusted owner and the two query clocks.
        keys = [row[0] for row in self.db.execute('SELECT DISTINCT key FROM facts WHERE owner=?', (self.principal.owner,))]
        eligible = []
        words = set(re.findall(r'\w+', query.casefold()))
        for key in keys:
            fact = self.recall(key, valid_at=valid_at, known_at=known_at)
            if fact is None:
                continue
            text = key + ' ' + fact['value']
            lexical = len(words & set(re.findall(r'\w+', text.casefold())))
            dense = cosine(features(query), features(text))
            if mode == 'exact':
                if query != key:
                    continue
            elif mode != 'recency' and lexical == 0 and (mode == 'lexical' or dense < 0.18):
                continue
            eligible.append({'key': key, **fact, 'lexical': lexical, 'character_cosine': dense})
        if mode == 'recency':
            return sorted(eligible, key=lambda row: (-row['valid_at'], -row['recorded_at'], row['key']))[:limit]
        if mode == 'hybrid':
            lexical_rank = {row['key']: rank for rank, row in enumerate(sorted(eligible, key=lambda x: (-x['lexical'], x['key'])), 1)}
            dense_rank = {row['key']: rank for rank, row in enumerate(sorted(eligible, key=lambda x: (-x['character_cosine'], x['key'])), 1)}
            for row in eligible:
                row['fusion'] = 1 / (60 + lexical_rank[row['key']]) + 1 / (60 + dense_rank[row['key']])
        eligible.sort(key=lambda row: (-row.get('fusion', row['lexical']), -row['character_cosine'], row['key']))
        return eligible[:limit]

    def forget(self, key, *, recorded_at):
        owner = self.principal.owner
        # Authoritative rows, derived text/vectors and the revocation epoch share
        # one SQLite transaction. A process interruption cannot commit half an
        # erasure and leave a recoverable private projection behind.
        with self.db:
            count = self.db.execute('SELECT COUNT(*) FROM facts WHERE owner=? AND key=?', (owner, key)).fetchone()[0]
            self.db.execute('DELETE FROM facts WHERE owner=? AND key=?', (owner, key))
            self.db.execute('DELETE FROM projections WHERE owner=? AND key=?', (owner, key))
            self.db.execute('INSERT INTO deletions(owner,count,recorded_at) VALUES (?,?,?)', (owner, count, recorded_at))
            self.db.execute('''INSERT INTO epochs VALUES (?,1) ON CONFLICT(owner)
                DO UPDATE SET generation=generation+1''', (owner,))
        assert self.db.execute('SELECT 1 FROM projections WHERE owner=? AND key=?', (self.principal.owner, key)).fetchone() is None
        return count

    def expire(self, now):
        keys = [row[0] for row in self.db.execute('SELECT DISTINCT key FROM facts WHERE owner=?', (self.principal.owner,))]
        expired = []
        for key in keys:
            row = self.db.execute('''SELECT expires_at FROM facts WHERE owner=? AND key=? AND valid_at<=?
                ORDER BY valid_at DESC,recorded_at DESC,id DESC LIMIT 1''', (self.principal.owner, key, now)).fetchone()
            if row and row[0] is not None and row[0] <= now:
                self.forget(key, recorded_at=now)
                expired.append(key)
        return expired

    def export(self, *, valid_at, known_at):
        events = []
        for row in self.db.execute('''SELECT key,value,valid_at,recorded_at,expires_at,source,request_id
            FROM facts WHERE owner=? AND recorded_at<=? ORDER BY id''', (self.principal.owner, known_at)):
            events.append(dict(zip(('key', 'value', 'valid_at', 'recorded_at', 'expires_at', 'source', 'request_id'), row)))
        keys = sorted({event['key'] for event in events})
        facts = {key: self.recall(key, valid_at=valid_at, known_at=known_at) for key in keys}
        generation = self.db.execute('SELECT generation FROM epochs WHERE owner=?', (self.principal.owner,)).fetchone()
        return {'version': 1, 'owner': self.principal.owner, 'generation': generation[0] if generation else 0,
                'episodic_events': events, 'semantic_facts': {key: value for key, value in facts.items() if value}}


def check():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'memory.sqlite'
        with sqlite3.connect(path) as db:
            a, b = MemoryProject(db, Principal('A')), MemoryProject(db, Principal('B'))
            args = dict(valid_at=10, recorded_at=10, source='explicit preference', request_id='first', consent=True)
            assert a.remember('language', 'English', **args)
            assert not a.remember('language', 'English', **args)
            a.correct('language', 'Arabic', valid_at=15, recorded_at=17, source='explicit correction', request_id='second', expires_at=30, consent=True)
            assert a.recall('language', valid_at=16, known_at=16)['value'] == 'English'
            assert a.recall('language', valid_at=16, known_at=18)['value'] == 'Arabic'
            assert a.recall('language', valid_at=30, known_at=30) is None
            assert b.search('language', valid_at=20, known_at=20) == []
            try:
                b.correct('language', 'stolen', **args)
            except ValueError:
                pass
            else:
                raise AssertionError('cross-owner correction accepted')
            a.remember('editor', 'Vim keyboard editing', valid_at=11, recorded_at=11, source='explicit preference', request_id='editor', consent=True)
            b.remember('private', 'owner B secret phrase', valid_at=12, recorded_at=12, source='explicit preference', request_id='secret', consent=True)
            # Independent answer key: source facts established above, not model labels.
            gold = [('language', 'language'), ('Arabic explanations', 'language'), ('keyboard editing', 'editor'), ('unrelated galaxy plutonium', None)]
            scores = {}
            for mode in ('recency', 'exact', 'lexical', 'hybrid'):
                correct = false_recall = 0
                for query, expected in gold:
                    hits = a.search(query, valid_at=20, known_at=20, mode=mode)
                    observed = hits[0]['key'] if hits else None
                    correct += observed == expected
                    false_recall += expected is None and bool(hits)
                    assert 'secret' not in json.dumps(hits)
                scores[mode] = {'correct': correct, 'cases': len(gold), 'false_recall': false_recall}
            assert scores['hybrid']['correct'] == 4 and scores['hybrid']['false_recall'] == 0, scores
            assert scores['recency'] == {'correct': 2, 'cases': 4, 'false_recall': 1}, scores
            exported = a.export(valid_at=20, known_at=20)
            assert len(exported['episodic_events']) == 3 and len(exported['semantic_facts']) == 2
            generation = exported['generation']
            assert a.expire(30) == ['language']
            assert a.export(valid_at=30, known_at=30)['generation'] > generation
            assert a.search('Arabic', valid_at=30, known_at=30) == []
            assert 'Arabic' not in json.dumps(a.export(valid_at=30, known_at=30))
            db.execute('''CREATE TRIGGER fail_projection_delete BEFORE DELETE ON projections
                BEGIN SELECT RAISE(ABORT, 'injected projection failure'); END''')
            db.commit()
            try:
                a.forget('editor', recorded_at=31)
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError('injected erasure failure was ignored')
            assert a.recall('editor', valid_at=31, known_at=31) is not None
            assert db.execute('SELECT 1 FROM projections WHERE owner=? AND key=?', ('A', 'editor')).fetchone()
            db.execute('DROP TRIGGER fail_projection_delete'); db.commit()
            assert a.forget('editor', recorded_at=31) == 1
            assert a.export(valid_at=31, known_at=31)['episodic_events'] == []
            assert b.recall('private', valid_at=31, known_at=31)['value'] == 'owner B secret phrase'
        with sqlite3.connect(path) as db:
            assert MemoryProject(db, Principal('A')).search('language', valid_at=32, known_at=32) == []
        print(json.dumps({'memory_project': 'PASS', 'retrieval_comparison': scores,
                          'projections_erased': True, 'restart': 'pass', 'corpus': 'original synthetic preferences',
                          'limits': 'four local oracle cases; no learned embedding or production erasure claim'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'append', 'correct', 'query', 'expire', 'export', 'delete'])
    parser.add_argument('--database', default='memory.sqlite')
    parser.add_argument('--owner', default='learner')
    parser.add_argument('--key'); parser.add_argument('--value')
    parser.add_argument('--source', default='explicit local user')
    parser.add_argument('--request'); parser.add_argument('--at', type=int, default=0)
    parser.add_argument('--observed', type=int); parser.add_argument('--expires', type=int)
    parser.add_argument('--consent', action='store_true')
    parser.add_argument('--mode', choices=['recency', 'exact', 'lexical', 'hybrid'], default='hybrid')
    args = parser.parse_args()
    if args.command == 'check':
        check(); return
    with sqlite3.connect(args.database) as db:
        memory = MemoryProject(db, Principal(args.owner))
        if args.command in {'append', 'correct'}:
            if not args.key or args.value is None or not args.request:
                parser.error('append/correct require --key, --value and --request')
            result = getattr(memory, 'remember' if args.command == 'append' else 'correct')(
                args.key, args.value, valid_at=args.at, recorded_at=args.observed if args.observed is not None else args.at,
                source=args.source, request_id=args.request, expires_at=args.expires, consent=args.consent)
        elif args.command == 'query':
            if not args.key: parser.error('query requires --key (query text)')
            result = memory.search(args.key, valid_at=args.at, known_at=args.observed if args.observed is not None else args.at, mode=args.mode)
        elif args.command == 'expire': result = memory.expire(args.at)
        elif args.command == 'export': result = memory.export(valid_at=args.at, known_at=args.observed if args.observed is not None else args.at)
        else:
            if not args.key: parser.error('delete requires --key')
            result = memory.forget(args.key, recorded_at=args.at)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
