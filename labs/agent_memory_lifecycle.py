"""Agent memory: scoped, consented, bitemporal facts with local SQLite.

Educational reference, not an encrypted production memory service. Owner identity
comes from the trusted host, never from the retrieved text or a user-supplied tool
payload. Forgotten source rows are removed here; external backups and replicas
must implement separate deletion policies.
"""
from dataclasses import dataclass
import hashlib
import json
import sqlite3

@dataclass(frozen=True)
class Principal:
    owner: str
    def __post_init__(self):
        if not self.owner or not self.owner.strip():
            raise ValueError("trusted owner required")

class Memory:
    def __init__(self, connection, principal):
        if not isinstance(principal, Principal):
            raise TypeError("a host-established Principal is required")
        self.db, self.principal = connection, principal
        self.db.execute("""CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY, owner TEXT NOT NULL, key TEXT NOT NULL,
            value TEXT NOT NULL, valid_at INTEGER NOT NULL,
            recorded_at INTEGER NOT NULL, expires_at INTEGER,
            source TEXT NOT NULL, request_id TEXT NOT NULL,
            digest TEXT NOT NULL, UNIQUE(owner, request_id)
        )""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS deletions (
            id INTEGER PRIMARY KEY, owner TEXT NOT NULL,
            count INTEGER NOT NULL, recorded_at INTEGER NOT NULL
        )""")
        self.db.commit()

    def remember(self, key, value, *, valid_at, recorded_at, source,
                 request_id, expires_at=None, consent=False):
        if not consent:
            raise PermissionError("long-term memory requires explicit consent")
        if not key or not source or not request_id or not isinstance(value, str):
            raise ValueError("key, textual value, source and request ID required")
        if expires_at is not None and expires_at <= valid_at:
            raise ValueError("memory expiry must follow its valid time")
        if recorded_at < valid_at:
            raise ValueError("cannot record a fact before its effective time in this example")
        payload = json.dumps([key,value,valid_at,recorded_at,source,expires_at],
                             ensure_ascii=False, separators=(",",":"))
        digest = hashlib.sha256(payload.encode()).hexdigest()
        owner = self.principal.owner
        previous = self.db.execute(
            "SELECT digest FROM facts WHERE owner=? AND request_id=?", (owner, request_id)).fetchone()
        if previous:
            if previous[0] != digest:
                raise ValueError("request ID replay with changed payload")
            return False
        with self.db:
            self.db.execute("""INSERT INTO facts
                (owner,key,value,valid_at,recorded_at,expires_at,source,request_id,digest)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (owner,key,value,valid_at,recorded_at,expires_at,source,request_id,digest))
        return True

    def recall(self, key, *, valid_at, known_at):
        # Two clocks: when the fact applied and when the agent knew about it.
        # Scope by principal before ranking. A vector-search adapter must obey
        # the same server-enforced eligibility predicate, not a top-k post-filter.
        row = self.db.execute("""SELECT value, source, valid_at, recorded_at FROM facts
            WHERE owner=? AND key=? AND valid_at<=? AND recorded_at<=?
              AND (expires_at IS NULL OR expires_at>?)
            ORDER BY valid_at DESC, recorded_at DESC, id DESC LIMIT 1""",
            (self.principal.owner,key,valid_at,known_at,valid_at)).fetchone()
        return None if row is None else dict(zip(("value","source","valid_at","recorded_at"),row))

    def forget(self, key, *, recorded_at):
        with self.db:
            count = self.db.execute(
                "SELECT COUNT(*) FROM facts WHERE owner=? AND key=?",
                (self.principal.owner,key)).fetchone()[0]
            self.db.execute("DELETE FROM facts WHERE owner=? AND key=?",
                            (self.principal.owner,key))
            # Do not retain the deleted key or value in this audit entry.
            self.db.execute("INSERT INTO deletions(owner,count,recorded_at) VALUES(?,?,?)",
                            (self.principal.owner,count,recorded_at))
        return count


def check():
    db=sqlite3.connect(":memory:")
    a=Memory(db,Principal("tenant-A"))
    b=Memory(db,Principal("tenant-B"))
    assert a.remember("language","English",valid_at=10,recorded_at=11,source="explicit user",
                      request_id="a-1",consent=True)
    assert not a.remember("language","English",valid_at=10,recorded_at=11,source="explicit user",
                          request_id="a-1",consent=True)
    assert b.recall("language",valid_at=20,known_at=20) is None
    assert a.remember("language","Arabic",valid_at=15,recorded_at=17,source="explicit correction",
                      request_id="a-2",consent=True)
    assert a.recall("language",valid_at=16,known_at=16)["value"]=="English"
    assert a.recall("language",valid_at=16,known_at=18)["value"]=="Arabic"
    assert a.recall("language",valid_at=12,known_at=20)["value"]=="English"
    assert a.remember("theme","dark",valid_at=21,recorded_at=21,expires_at=30,
                      source="user choice",request_id="a-3",consent=True)
    assert a.recall("theme",valid_at=29,known_at=29)["value"]=="dark"
    assert a.recall("theme",valid_at=30,known_at=30) is None
    try:a.remember("secret","x",valid_at=20,recorded_at=20,
                   source="untrusted web",request_id="bad",consent=False)
    except PermissionError:pass
    else:raise AssertionError("unconsented memory committed")
    try:a.remember("language","spoof",valid_at=10,recorded_at=11,
                   source="explicit user",request_id="a-1",consent=True)
    except ValueError:pass
    else:raise AssertionError("idempotency collision not rejected")
    assert a.forget("language",recorded_at=31)==2
    assert a.recall("language",valid_at=15,known_at=31) is None
    assert b.forget("theme",recorded_at=31)==0
    assert a.recall("theme",valid_at=29,known_at=31)["value"]=="dark"
    print("Scoped bitemporal memory: consent, revision, expiry, replay, isolation, deletion PASS")


if __name__=="__main__":
    check()
