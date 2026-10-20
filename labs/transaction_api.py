"""Local FastAPI/PostgreSQL transaction capstone. Never hosted by Pages.

Set DATABASE_URL and distinct DEMO_TOKEN_A/DEMO_TOKEN_B (16+ characters).
Synthetic bearer tokens demonstrate identity boundaries; this is not a JWT issuer.
"""
import hashlib
import os
import secrets
from uuid import UUID, uuid4

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

app=FastAPI()
bearer=HTTPBearer(auto_error=False)


def identity(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    token_a=os.environ.get('DEMO_TOKEN_A','');token_b=os.environ.get('DEMO_TOKEN_B','')
    if len(token_a)<16 or len(token_b)<16 or secrets.compare_digest(token_a,token_b):
        raise HTTPException(503,'Configure distinct local demo tokens')
    if credentials is None:raise HTTPException(401,'Bearer token required')
    for token,owner in ((token_a,'A'),(token_b,'B')):
        if secrets.compare_digest(credentials.credentials,token):return owner
    raise HTTPException(401,'Invalid bearer token')


def connect():
    # Test harness creates a disposable local cluster; no production DSN default.
    return psycopg.connect(os.environ['DATABASE_URL'])


def initialize():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
          id UUID PRIMARY KEY, owner TEXT NOT NULL, operation_key TEXT NOT NULL,
          payload_hash TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','confirmed')),
          UNIQUE(owner,operation_key))''')
        db.execute('''CREATE TABLE IF NOT EXISTS outbox (
          task_id UUID PRIMARY KEY REFERENCES tasks(id), effect_key UUID UNIQUE NOT NULL,
          dispatched BOOLEAN NOT NULL DEFAULT FALSE)''')


class Request(BaseModel):
    message: str=Field(min_length=1,max_length=1000,pattern=r'\S')


@app.post('/tasks',status_code=202)
def accept(body:Request, owner:str=Depends(identity), operation_key:str=Header(alias='Idempotency-Key',min_length=1,max_length=100)):
    digest=hashlib.sha256(body.message.encode()).hexdigest()
    with connect() as db:
        row=db.execute('''INSERT INTO tasks VALUES(%s,%s,%s,%s,'pending')
            ON CONFLICT(owner,operation_key) DO NOTHING RETURNING id,status''',(uuid4(),owner,operation_key,digest)).fetchone()
        if row is None:
            row=db.execute('SELECT id,payload_hash,status FROM tasks WHERE owner=%s AND operation_key=%s',(owner,operation_key)).fetchone()
            if row[1]!=digest:raise HTTPException(409,'Key reused with different content')
            return {'task_id':str(row[0]),'status':row[2]}
        return {'task_id':str(row[0]),'status':row[1]}


@app.get('/tasks/{task_id}')
def status(task_id:UUID,owner:str=Depends(identity)):
    with connect() as db:
        row=db.execute('SELECT status FROM tasks WHERE id=%s AND owner=%s',(task_id,owner)).fetchone()
        if row is None:raise HTTPException(404,'Task not found')
        return {'task_id':str(task_id),'status':row[0]}


def confirm(task_id,owner,fail_before_commit=False):
    with connect() as db:
        row=db.execute('SELECT status FROM tasks WHERE id=%s AND owner=%s FOR UPDATE',(task_id,owner)).fetchone()
        if row is None:raise HTTPException(404,'Task not found')
        if row[0]=='pending':
            db.execute("UPDATE tasks SET status='confirmed' WHERE id=%s",(task_id,))
            db.execute('INSERT INTO outbox(task_id,effect_key) VALUES(%s,%s)',(task_id,uuid4()))
            if fail_before_commit:raise RuntimeError('Synthetic crash before commit')
        return {'task_id':str(task_id),'status':'confirmed'}


@app.post('/tasks/{task_id}/confirm')
def confirm_route(task_id:UUID,owner:str=Depends(identity)):
    return confirm(task_id,owner)


def verify():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from fastapi.testclient import TestClient
    initialize();client=TestClient(app)
    headers={'Authorization':'Bearer '+os.environ['DEMO_TOKEN_A'],'Idempotency-Key':'same-operation'}
    assert client.post('/tasks',json={'message':'test'}).status_code==401
    assert client.post('/tasks',headers=headers,json={'message':'   '}).status_code==422
    barrier=Barrier(2)
    def submit(_):
        barrier.wait(timeout=5)
        return client.post('/tasks',headers=headers,json={'message':'question'})
    with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(submit,range(2)))
    assert all(response.status_code==202 for response in responses)
    assert responses[0].json()['task_id']==responses[1].json()['task_id']
    task_id=responses[0].json()['task_id']
    assert client.post('/tasks',headers=headers,json={'message':'changed'}).status_code==409
    other={'Authorization':'Bearer '+os.environ['DEMO_TOKEN_B']}
    assert client.get('/tasks/'+task_id,headers=other).status_code==404
    assert client.post('/tasks/'+task_id+'/confirm',headers=other).status_code==404
    try:confirm(task_id,'A',fail_before_commit=True)
    except RuntimeError:pass
    else:raise AssertionError('Fault injection did not run')
    assert client.get('/tasks/'+task_id,headers=headers).json()['status']=='pending'
    barrier=Barrier(2)
    def commit(_):
        barrier.wait(timeout=5)
        return client.post('/tasks/'+task_id+'/confirm',headers=headers)
    with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(commit,range(2)))
    assert all(response.status_code==200 for response in responses)
    with connect() as db:
        assert db.execute('SELECT count(*) FROM tasks').fetchone()[0]==1
        assert db.execute('SELECT count(*) FROM outbox').fetchone()[0]==1
    print('PostgreSQL API: auth, validation, owner isolation, concurrent idempotency, payload conflict, rollback and one outbox effect passed.')


if __name__=='__main__':verify()
