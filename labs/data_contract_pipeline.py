"""Synthetic CDC pipeline: atomic checkpoints, quarantine, versioning and deletion.

Run with Python 3.11+. SQLite is an executable transaction fixture, not a stream broker.
"""
from hashlib import sha256
import json
import sqlite3


def create_database() -> sqlite3.Connection:
    db = sqlite3.connect(':memory:')
    db.executescript('''
        CREATE TABLE receipts (owner TEXT, event_id TEXT, digest TEXT,
            PRIMARY KEY(owner, event_id));
        CREATE TABLE documents (owner TEXT, id TEXT, revision INTEGER, title TEXT,
            deleted INTEGER, PRIMARY KEY(owner,id));
        CREATE TABLE checkpoint (singleton INTEGER PRIMARY KEY CHECK(singleton=1), offset INTEGER);
        INSERT INTO checkpoint VALUES(1,0);
        CREATE TABLE quarantine (offset INTEGER PRIMARY KEY, reason TEXT);
        CREATE TABLE source_positions (offset INTEGER PRIMARY KEY, digest TEXT NOT NULL);
    ''')
    return db


def validate(event: dict) -> dict:
    if not isinstance(event, dict) or type(event.get('schema')) is not int or event.get('schema') not in (1, 2):
        raise ValueError('Unsupported envelope')
    for key in ('owner', 'event_id', 'document_id'):
        if not isinstance(event.get(key), str) or not 0 < len(event[key]) <= 100:
            raise ValueError('Invalid identity')
    if type(event.get('revision')) is not int or event['revision'] < 1:
        raise ValueError('Revision must be a positive integer')
    if event.get('operation') not in ('upsert', 'delete'):
        raise ValueError('Invalid operation')
    title = event.get('title') if event['schema'] == 2 else event.get('name')
    if event['operation'] != 'delete' and (not isinstance(title, str) or not 0 < len(title.strip()) <= 1000):
        raise ValueError('Missing document title')
    return {**event, 'title': '' if event['operation'] == 'delete' else title}


def ingest(db: sqlite3.Connection, offset: int, event: dict, crash: bool = False) -> str:
    """The fixture assumes one source partition and a contiguous integer cursor."""
    if type(offset) is not int or offset < 1:
        raise ValueError('Invalid offset')
    digest = sha256(json.dumps(event, sort_keys=True, allow_nan=False).encode()).hexdigest()
    try:
        normalized = validate(event)
    except ValueError as error:
        normalized, reason = None, str(error)
    with db:
        db.execute('BEGIN IMMEDIATE')
        cursor = db.execute('SELECT offset FROM checkpoint').fetchone()[0]
        if offset <= cursor:
            saved = db.execute('SELECT digest FROM source_positions WHERE offset=?', (offset,)).fetchone()
            if saved is None or saved[0] != digest:
                raise ValueError('Source offset reused with changed content')
            return 'already-checkpointed'
        if offset != cursor + 1:
            raise ValueError('Source offset gap; do not silently skip input')
        outcome = 'quarantined'
        if normalized is None:
            # Store a safe reason, not the potentially sensitive source body.
            db.execute('INSERT INTO quarantine VALUES(?,?)', (offset, reason))
        else:
            key = (normalized['owner'], normalized['event_id'])
            seen = db.execute('SELECT digest FROM receipts WHERE owner=? AND event_id=?', key).fetchone()
            if seen and seen[0] != digest:
                raise ValueError('Event identity reused with different content')
            if not seen:
                current = db.execute('SELECT revision,title,deleted FROM documents WHERE owner=? AND id=?',
                                     (normalized['owner'], normalized['document_id'])).fetchone()
                expected = (normalized['revision'], normalized['title'], int(normalized['operation'] == 'delete'))
                if current and current[0] == normalized['revision'] and current != expected:
                    raise ValueError('Document revision reused with changed content')
                db.execute('INSERT INTO receipts VALUES(?,?,?)', (*key, digest))
                db.execute('''INSERT INTO documents VALUES(?,?,?,?,?)
                    ON CONFLICT(owner,id) DO UPDATE SET revision=excluded.revision,
                    title=excluded.title, deleted=excluded.deleted
                    WHERE excluded.revision > documents.revision''',
                    (normalized['owner'], normalized['document_id'], normalized['revision'],
                     normalized['title'], int(normalized['operation'] == 'delete')))
            outcome = 'duplicate' if seen else 'applied'
        db.execute('INSERT INTO source_positions VALUES(?,?)', (offset, digest))
        if crash:
            raise RuntimeError('Injected failure before checkpoint commit')
        db.execute('UPDATE checkpoint SET offset=?', (offset,))
    return outcome


def event(identity: str, revision: int, **changes) -> dict:
    return {'schema': 1, 'owner': 'A', 'event_id': identity, 'document_id': 'policy',
            'revision': revision, 'operation': 'upsert', 'name': 'Synthetic policy', **changes}


def verify() -> None:
    with create_database() as db:
        try:
            ingest(db, 1, event('first', 1), crash=True)
        except RuntimeError:
            pass
        assert db.execute('SELECT count(*) FROM documents').fetchone()[0] == 0
        assert db.execute('SELECT offset FROM checkpoint').fetchone()[0] == 0
        assert ingest(db, 1, event('first', 1)) == 'applied'
        assert ingest(db, 1, event('first', 1)) == 'already-checkpointed'
        try:
            ingest(db, 1, event('first', 2))
        except ValueError:
            pass
        else:
            raise AssertionError('Changed source position accepted')
        assert ingest(db, 2, event('second', 3, schema=2, title='New schema')) == 'applied'
        ingest(db, 3, event('late', 2))  # Older revision cannot replace revision 3.
        assert db.execute('SELECT title FROM documents').fetchone()[0] == 'New schema'
        ingest(db, 4, {'schema': 99})
        assert db.execute('SELECT count(*) FROM quarantine').fetchone()[0] == 1
        ingest(db, 5, event('other-owner', 1, owner='B'))
        ingest(db, 6, event('deleted', 4, operation='delete'))
        assert db.execute('SELECT owner FROM documents WHERE deleted=0').fetchall() == [('B',)]
        try:
            ingest(db, 7, event('second', 9))
        except ValueError:
            pass
        else:
            raise AssertionError('Conflicting event identity accepted')
        assert db.execute('SELECT offset FROM checkpoint').fetchone()[0] == 6
        print('CDC: rollback/replay, schema adapter, stale revision, quarantine, tenant isolation and tombstone passed.')


if __name__ == '__main__':
    verify()
