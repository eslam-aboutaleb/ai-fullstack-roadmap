"""Load independently sized chapters with stable study IDs and explicit prerequisites."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
STAGES=[
 ('Understand a model-assisted application','Core concepts','What information a model needs and where the application takes control.', ['foundations','models','prompt-foundations','prompt-techniques','application-architecture','architecture']),
 ('Build the data and safety foundation','Intermediate','Protect identity, records, document processing, and repeatable background work.', ['database-modeling','api-security','database-security','database-concurrency','security','sources','ocr-document-ai','chunking','embeddings','storage','ingestion','coordination']),
 ('Retrieve, assemble, and evaluate knowledge','Intermediate','Find applicable evidence and explain what the model receives.', ['retrieval','evidence','evidence-applicability','context-engineering','context-optimization','evaluation']),
 ('Design controlled agents','Advanced','Choose tools, state, skills, and orchestration from a defined task.', ['agent-harness','adk-agents','langchain','agent-patterns','agent-orchestration','langgraph','skills-layers']),
 ('Connect agents across boundaries','Advanced','Build compatible capabilities and remote tasks without losing authority.', ['mcp-foundations','mcp-server-engineering','a2a','backend-agents']),
 ('Deliver realtime and multimodal experiences','Advanced','Preserve meaning through streams, interruption, speech, and changing state.', ['product-delivery','sse-streaming','websocket-streaming','voice-agents','live-agents']),
 ('Prove, operate, and defend the system','Advanced practice','Make quality, failure recovery, and engineering decisions observable.', ['agent-evaluation','evaluation-engineering','evaluation-libraries','agent-observability','model-engineering','deployment-reliability','fullstack','portfolio-capstone'])]

def load():
 legacy=json.loads((HERE/'core.json').read_text())
 for section in (HERE/'advanced.txt').read_text().split('## ')[1:]:
  header,*lines=section.strip().splitlines();slug,title,subtitle=header.split('|')
  rows=[]
  for line in lines:
   values=line.split(' || ')
   if len(values)!=6:raise ValueError('Malformed answer in '+slug)
   rows.append(dict(zip(('Q','A','Why','Risk','Trade','Try'),values)))
  legacy.append(dict(slug=slug,title=title,subtitle=subtitle,questions=rows))
 by={c['slug']:c for c in legacy}
 ids_path=HERE/'study_ids.json'
 ids=json.loads(ids_path.read_text()) if ids_path.exists() else {}
 for number,(slug,q) in enumerate(((c['slug'],q) for c in legacy for q in c['questions']),1):
  key='interview/'+slug+'/'+q['Q'];ids.setdefault(key,number);q['id']=ids[key]
 next_id=max(ids.values(),default=0)+1
 for section in (HERE/'course.txt').read_text().split('## ')[1:]:
  header,*lines=section.strip().splitlines();slug,goal,intro=header.split('|',2)
  c=by[slug];c.update(goal=goal,intro=intro,lessons=[],terms=[],flow=[],case=[])
  for line in lines:
   if line.startswith('@terms '):c['terms']=[x.split('=',1) for x in line[7:].split('; ')]
   elif line.startswith('@flow '):c['flow']=[x.split('=>',1) for x in line[6:].split('||')]
   elif line.startswith('@case '):c['case']=line[6:].split('||')
   elif line.startswith('? '):
    values=line[2:].split(' || ')
    if len(values)!=4:raise ValueError('Malformed lesson in '+slug)
    q=dict(zip(('Q','explain','example','takeaway'),values))
    key='lesson/'+slug+'/'+q['Q']
    if key not in ids:ids[key]=next_id;next_id+=1
    q['id']=ids[key];c['lessons'].append(q)
  if not c['lessons'] or not c['flow'] or len(c['case'])!=3:raise ValueError('Missing teaching material: '+slug)
 ordered=[]
 for stage,(title,level,summary,slugs) in enumerate(STAGES,1):
  for slug in slugs:
   c=by[slug];c.update(stage=stage,level=level);ordered.append(c)
 if set(by)!={c['slug'] for c in ordered}:raise ValueError('Every chapter needs a learning stage')
 ids_path.write_text(json.dumps(ids,indent=2,ensure_ascii=False)+'\n')
 return ordered
