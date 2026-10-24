"""Exact cosine + tenant-scoped, versioned migration reference, not provider integrations."""
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Record:
    id: str
    owner: str
    values: tuple
    revision: int
    deleted: bool = False
    model: str = "v1"

def cosine(a,b):
    if len(a)!=len(b) or not a: raise ValueError("vector dimension mismatch")
    den=sqrt(sum(x*x for x in a))*sqrt(sum(y*y for y in b))
    if den==0: raise ValueError("cosine undefined for zero vector")
    return sum(x*y for x,y in zip(a,b))/den

def search(rows, principal, query, k, model="v1", minimum_revision=0):
    if not principal or k<1: raise ValueError("invalid principal or k")
    # Restrict candidate set BEFORE nearest-neighbor scoring.
    eligible=(r for r in rows if r.owner==principal and not r.deleted
              and r.model==model and r.revision>=minimum_revision)
    return [r.id for _,r in sorted(((cosine(r.values,query),r) for r in eligible),
                                    key=lambda z:(-z[0],z[1].id))[:k]]

class Migration:
    def __init__(self, old):
        self.old=list(old);self.next=[];self.ack=set();self.active=False
    def apply(self, r, vector):
        if r.id in self.ack: raise ValueError("duplicate backfill ID")
        self.ack.add(r.id)
        if not r.deleted:
            self.next.append(Record(r.id,r.owner,tuple(vector),r.revision,model="v2"))
    def cutover(self, expected_ids):
        if self.ack!=set(expected_ids):raise ValueError("incomplete or unexpected backfill")
        self.active=True
    def query(self, principal, old_vector, new_vector, k):
        return search(self.next if self.active else self.old,principal,
                      new_vector if self.active else old_vector,k,
                      model="v2" if self.active else "v1")
def check():
    rows=[Record("a","A",(1.,0.),1),Record("b","B",(1.,0.),1),
          Record("c","A",(0.,1.),2),Record("removed","A",(1.,0.),4,True)]
    assert search(rows,"A",(1.,0.),3)==["a","c"]
    assert search(rows,"B",(1.,0.),3)==["b"]
    assert search(rows,"A",(0.,1.),3,minimum_revision=2)==["c"]
    m=Migration(rows)
    for r,v in zip(rows,[(.9,.1),(1.,0.),(0.,1.),(0.,0.)]):m.apply(r,v)
    try:m.cutover(["a","b","c"])
    except ValueError:pass
    else:raise AssertionError("partial backfill allowed")
    m.cutover(["a","b","c","removed"])
    assert m.query("A",(1.,0.),(1.,0.),3)==["a","c"]
    assert "removed" not in [r.id for r in m.next]
    try:search(rows,"A",(1.,),1)
    except ValueError:pass
    else:raise AssertionError("dimension mismatch accepted")
    print("Vector oracle: tenant filter, revision, deletion and fail-closed cutover PASS")
if __name__=="__main__":check()
