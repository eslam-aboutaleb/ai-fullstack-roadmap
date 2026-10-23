"""Transactional ETL/CDC replay and deployment gate for AI system designs.

This uses SQLite to exercise source ordering, tombstones and owner scope.
The 'deploy' check is an offline release-policy fixture, NOT Kubernetes.
"""
from dataclasses import dataclass
from dataclasses import asdict
from hashlib import sha256
import json
import re
import sqlite3

@dataclass(frozen=True)
class Event:
    owner: str
    sequence: int
    operation: str
    document: str
    revision: int
    payload: str
    deleted: bool = False

class Projection:
    def __init__(self,conn):
        self.db=conn
        self.db.execute("""CREATE TABLE IF NOT EXISTS progress (
            owner TEXT PRIMARY KEY, sequence INTEGER NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS documents (
            owner TEXT, document TEXT, revision INTEGER,
            payload TEXT, deleted INTEGER, PRIMARY KEY(owner,document))""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS consumed (
            owner TEXT, operation TEXT, sequence INTEGER, digest TEXT, PRIMARY KEY(owner,operation))""")
        # Old local lab databases cannot prove payload equality for old events.
        # Retain their history, but fail closed on an unverifiable replay.
        if 'digest' not in {r[1] for r in self.db.execute('PRAGMA table_info(consumed)')}:
            self.db.execute('ALTER TABLE consumed ADD COLUMN digest TEXT')
        self.db.commit()
    def apply(self,e):
        if (any(not isinstance(value,str) or not value for value in (e.owner,e.operation,e.document))
                or type(e.sequence) is not int or type(e.revision) is not int
                or e.sequence<1 or e.revision<1 or not isinstance(e.payload,str) or type(e.deleted) is not bool):
            raise ValueError("incomplete source event contract")
        digest=sha256(json.dumps(asdict(e),sort_keys=True,separators=(',',':')).encode()).hexdigest()
        with self.db:
            old=self.db.execute("SELECT sequence FROM progress WHERE owner=?",(e.owner,)).fetchone()
            last=old[0] if old else 0
            dedup=self.db.execute("SELECT sequence,digest FROM consumed WHERE owner=? AND operation=?",
                                  (e.owner,e.operation)).fetchone()
            if dedup:
                if dedup!=(e.sequence,digest):raise ValueError("reused operation with changed/unverifiable material event")
                return False
            if e.sequence!=last+1:
                raise ValueError("CDC gap, out-of-order event or unregistered replay")
            prior=self.db.execute("SELECT revision,payload,deleted FROM documents WHERE owner=? AND document=?",
                                  (e.owner,e.document)).fetchone()
            if prior:
                if prior[2] and not e.deleted:
                    # Tombstones remain authoritative even if replay contains stale source.
                    raise PermissionError("restore requires independently approved source reconciliation")
                if e.revision==prior[0] and (e.payload!=prior[1] or int(e.deleted)!=prior[2]):
                    raise ValueError("same revision with conflicting content")
            if prior is None or e.revision>prior[0]:
                self.db.execute("""INSERT INTO documents(owner,document,revision,payload,deleted)
                    VALUES (?,?,?,?,?) ON CONFLICT(owner,document)
                    DO UPDATE SET revision=excluded.revision,payload=excluded.payload,
                                  deleted=excluded.deleted""",
                    (e.owner,e.document,e.revision,e.payload,int(e.deleted)))
            self.db.execute("INSERT INTO consumed VALUES(?,?,?,?)",(e.owner,e.operation,e.sequence,digest))
            self.db.execute("""INSERT INTO progress(owner,sequence) VALUES(?,?)
                ON CONFLICT(owner) DO UPDATE SET sequence=excluded.sequence""",
                (e.owner,e.sequence))
        return True
    def visible(self,owner):
        return list(self.db.execute("SELECT document,payload FROM documents WHERE owner=? AND deleted=0",
                                    (owner,)).fetchall())

def release_gate(*, image_digest, schema_compatible, rollout_error_rate,
                 max_error_rate, recovery_drill_passed):
    if not isinstance(image_digest,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',image_digest):
        return False,"immutable container digest required"
    if not schema_compatible:return False,"incompatible schema"
    if not recovery_drill_passed:return False,"missing recovery evidence"
    if not (0<=rollout_error_rate<=1 and 0<=max_error_rate<=1):
        raise ValueError("invalid proportions")
    return (rollout_error_rate<=max_error_rate,
            "healthy fixture" if rollout_error_rate<=max_error_rate else "rollback threshold exceeded")

def check():
    conn=sqlite3.connect(":memory:")
    app=Projection(conn)
    assert app.apply(Event("A",1,"op-a1","policy-1",1,"refunds 30d"))
    assert not app.apply(Event("A",1,"op-a1","policy-1",1,"refunds 30d"))
    try:app.apply(Event("A",1,"op-a1","policy-1",1,"changed payload"))
    except ValueError:pass
    else:raise AssertionError("same-offset changed-payload replay accepted")
    assert app.apply(Event("B",1,"op-b1","policy-1",1,"private"))
    assert app.visible("A")==[("policy-1","refunds 30d")]
    assert app.visible("B")==[("policy-1","private")]
    assert app.apply(Event("A",2,"op-a2","policy-1",3,"",True))
    assert app.visible("A")==[]
    try:app.apply(Event("A",3,"op-a3","policy-1",2,"stale restore"))
    except PermissionError:pass
    else:raise AssertionError("resurrected deleted revision")
    try:app.apply(Event("A",4,"op-a4","policy-2",1,"out of order"))
    except ValueError:pass
    else:raise AssertionError("gap accepted")
    assert conn.execute("SELECT sequence FROM progress WHERE owner='A'").fetchone()[0]==2
    conn.execute("CREATE TRIGGER fail_checkpoint BEFORE INSERT ON progress WHEN NEW.owner='C' BEGIN SELECT RAISE(ABORT,'checkpoint unavailable'); END")
    conn.commit()
    try:app.apply(Event("C",1,"op-c1","policy-1",1,"must roll back"))
    except sqlite3.IntegrityError:pass
    else:raise AssertionError("checkpoint fault not injected")
    assert not app.visible('C')
    assert conn.execute("SELECT COUNT(*) FROM consumed WHERE owner='C'").fetchone()[0]==0
    digest="sha256:"+"a"*64
    assert release_gate(image_digest=digest,schema_compatible=True,
                        rollout_error_rate=.001,max_error_rate=.01,recovery_drill_passed=True)[0]
    assert not release_gate(image_digest=digest,schema_compatible=True,
                            rollout_error_rate=.2,max_error_rate=.01,recovery_drill_passed=True)[0]
    assert not release_gate(image_digest="latest",schema_compatible=True,
                            rollout_error_rate=0,max_error_rate=.01,recovery_drill_passed=True)[0]
    assert not release_gate(image_digest="sha256:"+"z"*64,schema_compatible=True,
                            rollout_error_rate=0,max_error_rate=.01,recovery_drill_passed=True)[0]
    print("Data/MLOps: tenant CDC, idempotency, gap, tombstone and rollout gating PASS")
if __name__=="__main__":check()
