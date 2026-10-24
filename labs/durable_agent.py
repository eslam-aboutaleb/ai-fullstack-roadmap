"""Local agent-effect capstone. Scripted policy, SQLite ledger and idempotent provider fixture."""
from contextlib import closing
from pathlib import Path
import hashlib
import sqlite3
import tempfile


def initialize(path):
    with closing(sqlite3.connect(path)) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS operations(
          key TEXT PRIMARY KEY, owner TEXT NOT NULL, payload_hash TEXT NOT NULL,
          state TEXT NOT NULL CHECK(state IN ('approved','done')));
          CREATE TABLE IF NOT EXISTS provider_effects(key TEXT PRIMARY KEY, payload TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS trace(id INTEGER PRIMARY KEY, key TEXT NOT NULL, event TEXT NOT NULL);''')
        db.commit()


def execute(path,key,owner,payload,approved,fail_after_effect=False):
    digest=hashlib.sha256(payload.encode()).hexdigest()
    with closing(sqlite3.connect(path)) as db:
        with db:
            db.execute('BEGIN IMMEDIATE')
            existing=db.execute('SELECT owner,payload_hash,state FROM operations WHERE key=?',(key,)).fetchone()
            if existing:
                if existing[0]!=owner:raise PermissionError('Operation belongs to another owner')
                if existing[1]!=digest:raise ValueError('Operation key content conflict')
                if existing[2]=='done':return 'done'
            else:
                if not approved:raise PermissionError('Approval required before effects')
                db.execute("INSERT INTO operations VALUES(?,?,?,'approved')",(key,owner,digest))
                db.execute("INSERT INTO trace(key,event) VALUES(?,'approved')",(key,))
        # Provider fixture commits independently. A SQL rollback cannot undo it.
        with db:
            db.execute('INSERT INTO provider_effects VALUES(?,?) ON CONFLICT(key) DO NOTHING',(key,payload))
            db.execute("INSERT INTO trace(key,event) VALUES(?,'provider-call')",(key,))
        if fail_after_effect:raise RuntimeError('Crash after provider effect, before local acknowledgment')
        with db:
            db.execute("UPDATE operations SET state='done' WHERE key=?",(key,))
            db.execute("INSERT INTO trace(key,event) VALUES(?,'acknowledged')",(key,))
    return 'done'


def verify():
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'ledger.db';initialize(path)
        try:execute(path,'op1','A','refund-42',approved=False)
        except PermissionError:pass
        else:raise AssertionError('Unapproved action accepted')
        try:execute(path,'op1','A','refund-42',approved=True,fail_after_effect=True)
        except RuntimeError:pass
        else:raise AssertionError('Crash not injected')
        assert execute(path,'op1','A','refund-42',approved=False)=='done'
        assert execute(path,'op1','A','refund-42',approved=False)=='done'
        for owner,payload,error in [('B','refund-42',PermissionError),('A','changed',ValueError)]:
            try:execute(path,'op1',owner,payload,approved=True)
            except error:pass
            else:raise AssertionError('Conflicting operation accepted')
        with closing(sqlite3.connect(path)) as db:
            assert db.execute('SELECT count(*) FROM provider_effects').fetchone()[0]==1
            events=[row[0] for row in db.execute('SELECT event FROM trace ORDER BY id')]
            assert events==['approved','provider-call','provider-call','acknowledged']
        print('Durable agent: approval, crash recovery, stable effect identity, one provider effect, and owner/content conflicts passed.')


if __name__=='__main__':verify()
