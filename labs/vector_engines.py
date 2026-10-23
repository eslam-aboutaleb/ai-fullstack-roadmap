"""Execute the same scoped CRUD contract through three currently enabled local vector SDKs.

Original two-dimensional vectors isolate storage/filter semantics from embedding
quality. Qdrant local mode is not a distributed Qdrant server. FAISS is an index
library: this adapter constructs eligible partitions before native search.
"""
import argparse
from copy import deepcopy
import importlib.metadata
import json
from pathlib import Path
import tempfile
import time

QUERY = [1.0, 0.0]
ROWS = [dict(id=1, owner='A', profile='v1', deleted=False, vector=[0.9, 0.1]),
        dict(id=2, owner='A', profile='v1', deleted=False, vector=[0.0, 1.0]),
        dict(id=3, owner='B', profile='v1', deleted=False, vector=[1.0, 0.0]),
        dict(id=4, owner='A', profile='v1', deleted=True, vector=[1.0, 0.0]),
        dict(id=5, owner='A', profile='v0', deleted=False, vector=[1.0, 0.0])]


class Qdrant:
    def __init__(self, folder):
        from qdrant_client import QdrantClient, models
        self.client, self.models = QdrantClient(path=str(folder)), models
        if not self.client.collection_exists('contract'):
            self.client.create_collection('contract', vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE))

    def upsert(self, rows):
        self.client.upsert('contract', points=[self.models.PointStruct(id=r['id'], vector=r['vector'], payload={k:v for k,v in r.items() if k!='vector'}) for r in rows], wait=True)

    def query(self, owner, profile, limit=1):
        models = self.models
        conditions = [models.FieldCondition(key=key, match=models.MatchValue(value=value)) for key,value in {'owner':owner, 'profile':profile, 'deleted':False}.items()]
        return [point.id for point in self.client.query_points('contract', query=QUERY, query_filter=models.Filter(must=conditions), limit=limit).points]

    def delete(self, identity, owner):
        predicate=self.models.Filter(must=[self.models.HasIdCondition(has_id=[identity]),
            self.models.FieldCondition(key='owner', match=self.models.MatchValue(value=owner))])
        self.client.delete('contract', points_selector=self.models.FilterSelector(filter=predicate), wait=True)

    def close(self): self.client.close()


class Faiss:
    def __init__(self, folder):
        import faiss
        import numpy as np
        self.faiss,self.np=faiss,np
        self.path=Path(folder)/'records.json';self.path.parent.mkdir(parents=True,exist_ok=True)
        self.rows=json.loads(self.path.read_text()) if self.path.exists() else []

    def upsert(self, rows):
        indexed={r['id']:r for r in self.rows};indexed.update({r['id']:r for r in rows})
        self.rows=list(indexed.values());self.path.write_text(json.dumps(self.rows))

    def query(self, owner, profile, limit=1):
        eligible=[r for r in self.rows if r['owner']==owner and r['profile']==profile and not r['deleted']]
        if not eligible:return []
        vectors=self.np.asarray([r['vector'] for r in eligible],dtype='float32')
        self.faiss.normalize_L2(vectors)
        index=self.faiss.IndexFlatIP(2);index.add(vectors)
        query=self.np.asarray([QUERY],dtype='float32');self.faiss.normalize_L2(query)
        _,positions=index.search(query,min(limit,len(eligible)))
        return [eligible[position]['id'] for position in positions[0]]

    def delete(self, identity, owner):
        self.rows=[row for row in self.rows if not (row['id']==identity and row['owner']==owner)];self.path.write_text(json.dumps(self.rows))

    def close(self): pass


class Lance:
    def __init__(self, folder):
        import lancedb
        self.db=lancedb.connect(str(folder));self.table=None
        if 'contract' in self.db.table_names():self.table=self.db.open_table('contract')

    def upsert(self, rows):
        if self.table is None:self.table=self.db.create_table('contract',rows)
        else:self.table.merge_insert('id').when_matched_update_all().when_not_matched_insert_all().execute(rows)

    def query(self, owner, profile, limit=1):
        # Values are fixed, host-established fixture identities, never SQL text
        # supplied by a user. Reject unknown values before composing predicates.
        if owner not in {'A','B','missing'} or profile not in {'v0','v1','v2'}:
            raise ValueError('unknown trusted fixture identity/profile')
        predicate=f"owner = '{owner}' AND profile = '{profile}' AND deleted = false"
        return [row['id'] for row in self.table.search(QUERY).distance_type('cosine').where(predicate,prefilter=True).limit(limit).to_list()]

    def delete(self, identity, owner):
        if not isinstance(identity,int) or owner not in {'A','B','missing'}:raise ValueError('known owner and integer ID required')
        self.table.delete(f"id = {identity} AND owner = '{owner}'")

    def close(self): pass


ENGINES={'qdrant':(Qdrant,'qdrant-client'),'faiss':(Faiss,'faiss-cpu'),'lance':(Lance,'lancedb')}


def run(selected, output=None):
    if 'chroma' in selected:
        raise ValueError('ChromaDB disabled pending a verified advisory-fixed release; do not install 1.5.9')
    results=[]
    for name in selected:
        factory,package=ENGINES[name]
        with tempfile.TemporaryDirectory() as folder:
            started=time.perf_counter();engine=factory(Path(folder)/name)
            try:
                engine.upsert(deepcopy(ROWS));build_seconds=time.perf_counter()-started
                observed=engine.query('A','v1')
                assert observed==[1],(name,'owner/revision/tombstone prefilter',observed)
                assert engine.query('missing','v1')==[],name
                assert engine.query('B','v1')==[3],name
                engine.delete(3,'A')
                assert engine.query('B','v1')==[3],(name,'cross-owner delete')
                assert engine.query('A','v0')==[5],name
                timings=[]
                for _ in range(10):
                    started=time.perf_counter();assert engine.query('A','v1')==[1]
                    timings.append(time.perf_counter()-started)
                # Repeated upsert and changed embedding profile must not leave a
                # stale duplicate in the old profile. Gold IDs are fixed above.
                changed={**ROWS[0],'profile':'v2'}
                engine.upsert([changed]);engine.upsert([changed])
                assert 1 not in engine.query('A','v1',10),name
                assert engine.query('A','v2')==[1],name
                engine.delete(1,'A')
                assert engine.query('A','v2')==[],name
                engine.delete(1,'A')
                assert engine.query('B','v1')==[3],name
                results.append({'engine':name,'sdk_version':importlib.metadata.version(package),'contract':'PASS','gold_target':1,
                                'build_seconds':build_seconds,'query_samples_seconds':timings,
                                'scope':'actual local SDK and original five-record synthetic vectors; no distributed/cloud or learned-embedding benchmark'})
            finally:engine.close()
    report={'vector_engines':'PASS','results':results,'not_executed':['ChromaDB disabled: unresolved critical dependency advisories','Pinecone managed service','Weaviate server','PostgreSQL pgvector server'],
            'limits':'10 tiny warm queries per engine are raw observations, not representative tail-latency or HNSW tuning evidence'}
    if output:Path(output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',action='append',choices=ENGINES);parser.add_argument('--output')
    args=parser.parse_args();run(args.engine or list(ENGINES),args.output)
