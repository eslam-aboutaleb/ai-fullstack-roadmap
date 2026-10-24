"""Restore a real SQLite backup, quantify lost writes and reapply deletion intent.

Single-machine exercise only. A PostgreSQL PITR plan also needs WAL retention,
recovery targets, roles, extension compatibility and an isolated restore test.
"""
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
import hashlib
import json
import sqlite3


def verify():
    with TemporaryDirectory(prefix='roadmap-restore-') as folder:
        directory = Path(folder)
        live, backup, restored = (directory/name for name in ('live.db','backup.db','restored.db'))
        with closing(sqlite3.connect(live)) as source:
            source.execute('CREATE TABLE docs(id TEXT PRIMARY KEY, owner TEXT, text TEXT)')
            source.executemany('INSERT INTO docs VALUES(?,?,?)', [('d1','a','Public policy'),('d2','a','Erase this fixture')])
            source.commit()
            with closing(sqlite3.connect(backup)) as destination:
                source.backup(destination)
            digest = hashlib.sha256(backup.read_bytes()).hexdigest()
            source.execute("INSERT INTO docs VALUES('d3','a','New after backup')")
            source.execute("DELETE FROM docs WHERE id='d2'")
            source.commit()
        # Separate authoritative deletion intent must outlive a restored old snapshot.
        deletion_ledger = {'d2'}
        started = perf_counter()
        assert hashlib.sha256(backup.read_bytes()).hexdigest() == digest
        with closing(sqlite3.connect(backup)) as snapshot, closing(sqlite3.connect(restored)) as destination:
            snapshot.backup(destination)
            assert destination.execute("SELECT COUNT(*) FROM docs WHERE id='d2'").fetchone()[0] == 1
            destination.executemany('DELETE FROM docs WHERE id=?', [(identity,) for identity in deletion_ledger])
            destination.commit()
            assert destination.execute('PRAGMA integrity_check').fetchone() == ('ok',)
            rows = destination.execute('SELECT id FROM docs ORDER BY id').fetchall()
            assert rows == [('d1',)], rows
        elapsed = perf_counter()-started
        print(json.dumps({'restore':'pass','backup_sha256':digest,'restored_visible_ids':['d1'],
            'lost_post_backup_insert_ids':['d3'],'deletion_intent_reapplied':['d2'],
            'measured_restore_seconds':elapsed,'rpo':'one known post-backup insert lost; not a wall-clock RPO measurement',
            'rto_scope':'local copy, integrity check and tombstone replay only; not end-to-end service recovery'}))


if __name__ == '__main__':
    verify()
