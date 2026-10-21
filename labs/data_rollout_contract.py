"""Transactional ETL/CDC replay and deployment gate for AI system designs.

This uses SQLite to exercise source ordering, tombstones and owner scope.
The 'deploy' check is an offline release-policy fixture, NOT Kubernetes.
"""
from dataclasses import dataclass
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
            owner TEXT, operation TEXT, sequence INTEGER, PRIMARY KEY(owner,operation))""")
        self.db.commit()
    def apply(self,e):
        if not e.owner or not e.operation or not e.document or e.sequence<1 or e.revision<1:
            raise ValueError("incomplete source event contract")
        with self.db:
            old=self.db.execute("SELECT sequence FROM progress WHERE owner=?",(e.owner,)).fetchone()
            last=old[0] if old else 0
            dedup=self.db.execute("SELECT sequence FROM consumed WHERE owner=? AND operation=?",
                                  (e.owner,e.operation)).fetchone()
            if dedup:
                if dedup[0]!=e.sequence:raise ValueError("reused operation at different offset")
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
            self.db.execute("INSERT INTO consumed VALUES(?,?,?)",(e.owner,e.operation,e.sequence))
            self.db.execute("""INSERT INTO progress(owner,sequence) VALUES(?,?)
                ON CONFLICT(owner) DO UPDATE SET sequence=excluded.sequence""",
                (e.owner,e.sequence))
        return True
    def visible(self,owner):
        return list(self.db.execute("SELECT document,payload FROM documents WHERE owner=? AND deleted=0",
                                    (owner,)).fetchall())

def release_gate(*, image_digest, schema_compatible, rollout_error_rate,
                 max_error_rate, recovery_drill_passed):
    if not image_digest.startswith("sha256:") or len(image_digest)!=71:
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
    digest="sha256:"+"a"*64
    assert release_gate(image_digest=digest,schema_compatible=True,
                        rollout_error_rate=.001,max_error_rate=.01,recovery_drill_passed=True)[0]
    assert not release_gate(image_digest=digest,schema_compatible=True,
                            rollout_error_rate=.2,max_error_rate=.01,recovery_drill_passed=True)[0]
    assert not release_gate(image_digest="latest",schema_compatible=True,
                            rollout_error_rate=0,max_error_rate=.01,recovery_drill_passed=True)[0]
    print("Data/MLOps: tenant CDC, idempotency, gap, tombstone and rollout gating PASS")
if __name__=="__main__":check()
