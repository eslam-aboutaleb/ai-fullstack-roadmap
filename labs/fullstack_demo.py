"""Local connected application: task API, bounded analysis, retrieval and durable demo effects.

Run `uvicorn labs.fullstack_demo:app --host 127.0.0.1 --port 8000` from the repo.
Configure DATABASE_URL, DEMO_TOKEN_A/B and DEMO_LEDGER_PATH. Synthetic data only.
"""
import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from . import transaction_api as api
from .async_job_engine import run_jobs
from .rag_evaluation import retrieve, DOCS
from .durable_agent import initialize as initialize_ledger, execute


@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(api.initialize)
    yield


app=FastAPI(lifespan=lifespan)
app.include_router(api.app.router)
admission=asyncio.Semaphore(4)


@app.post('/questions',status_code=202)
async def question(body:api.Request,owner:str=Depends(api.identity),operation_key:str=Header(alias='Idempotency-Key',min_length=1,max_length=100)):
    async with admission:
        accepted=await asyncio.to_thread(api.accept,body,owner,operation_key)
        async def handler(job):
            ids=retrieve(job['message'],owner)
            passages=[document for document in DOCS if document['id'] in ids and document['owner']==owner]
            return {'action':'cite' if passages else 'abstain','sources':passages}
        result=await run_jobs([{'id':accepted['task_id'],'message':body.message}],handler,workers=1,capacity=1)
        return {**accepted,'analysis':result[accepted['task_id']]}


@app.post('/effects/{task_id}/confirm')
async def effect(task_id:UUID,owner:str=Depends(api.identity)):
    await asyncio.to_thread(api.status,task_id,owner)  # Reject another owner before any fixture effect.
    filename=os.environ.get('DEMO_LEDGER_PATH')
    if not filename:raise HTTPException(503,'Set a local DEMO_LEDGER_PATH for the optional effect fixture')
    path=Path(filename);path.parent.mkdir(parents=True,exist_ok=True)
    await asyncio.to_thread(initialize_ledger,path)
    await asyncio.to_thread(api.confirm,task_id,owner)
    # The explicit authorized POST supplies approval. No model decides permission.
    result=await asyncio.to_thread(execute,path,str(task_id),owner,'demo-confirmation:'+str(task_id),True)
    return {'task_id':str(task_id),'effect':result}


@app.get('/',response_class=HTMLResponse)
def index():
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local evidence assistant</title><style>body{font:18px system-ui;max-width:760px;margin:40px auto;padding:20px}label,input,textarea,button{display:block;margin:12px 0}input,textarea{width:95%;padding:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere}button{padding:10px}</style></head><body><h1>Local evidence assistant</h1><p>Synthetic documents and a scripted retrieval policy. No model provider. Tasks and effect intent use PostgreSQL; the demo provider uses a local ledger.</p><form id="form"><label for="token">Your local demo bearer token</label><input id="token" type="password" required autocomplete="off"><label for="question">Question</label><textarea id="question" required maxlength="1000">sale items exchange</textarea><button>Ask with evidence</button></form><button id="confirm" disabled>Approve one demo effect</button><pre id="result" role="status"></pre><script>
let key=crypto.randomUUID(), task;
const output=document.querySelector('#result'),confirm=document.querySelector('#confirm');
document.querySelector('#question').addEventListener('input',()=>{key=crypto.randomUUID();task=undefined;confirm.disabled=true;});
async function request(path,body){const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+document.querySelector('#token').value,'Idempotency-Key':key},body:body?JSON.stringify(body):undefined});const data=await response.json();if(!response.ok)throw new Error(JSON.stringify(data));return data;}
document.querySelector('#form').addEventListener('submit',async event=>{event.preventDefault();try{const data=await request('/questions',{message:document.querySelector('#question').value});task=data.task_id;output.textContent=JSON.stringify(data,null,2);confirm.disabled=false;}catch(error){output.textContent=error.message;}});
confirm.addEventListener('click',async()=>{try{output.textContent=JSON.stringify(await request('/effects/'+task+'/confirm'),null,2);}catch(error){output.textContent=error.message;}});
</script></body></html>'''


def verify():
    from fastapi.testclient import TestClient
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        os.environ['DEMO_LEDGER_PATH']=str(Path(folder)/'provider.db')
        with TestClient(app) as client:
            assert '<h1>Local evidence assistant</h1>' in client.get('/').text
            headers={'Authorization':'Bearer '+os.environ['DEMO_TOKEN_A'],'Idempotency-Key':'fullstack-query'}
            response=client.post('/questions',headers=headers,json={'message':'sale items exchange'})
            assert response.status_code==202,response.text
            body=response.json();task_id=body['task_id']
            assert body['analysis']['value']['action']=='cite'
            assert [source['id'] for source in body['analysis']['value']['sources']]==['sale']
            assert client.post('/questions',headers=headers,json={'message':'sale items exchange'}).json()['task_id']==task_id
            assert client.post('/effects/'+task_id+'/confirm',headers={'Authorization':'Bearer '+os.environ['DEMO_TOKEN_B']}).status_code==404
            for _ in range(2):assert client.post('/effects/'+task_id+'/confirm',headers=headers).json()['effect']=='done'
            headers['Idempotency-Key']='fullstack-abstain'
            assert client.post('/questions',headers=headers,json={'message':'unknown warranty coverage'}).json()['analysis']['value']['action']=='abstain'
    print('Connected app: local UI, durable task identity, bounded retrieval, abstention, cross-owner denial and repeat-safe demo effect passed.')


if __name__=='__main__':verify()
