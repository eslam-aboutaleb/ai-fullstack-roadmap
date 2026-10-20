/* Deterministic small-state teaching models; no backend execution. */
(function(root) {
  'use strict';
  function simulate(kind, failure=false) {
    const steps=[];
    const add=(label,detail,state)=>steps.push({label,detail,state:structuredClone(state)});
    if (kind==='asyncio') {
      const state={A:'ready',B:'ready',queue:[]};
      add('Ready queue','Both tasks are scheduled. Only one Python task executes on this event-loop thread at a time.',state);
      for (const task of ['A','B']) {
        state[task]='running';add(task+' starts','Run until an operation actually suspends; awaiting an already-complete result need not yield.',state);
        state[task]='waiting';add(task+' yields','I/O is pending; another ready task can run.',state);
      }
      for (const task of ['A','B']) {
        state[task]=failure&&task==='A'?'cancelled':'done';
        add(task+' resumes',failure&&task==='A'?'Cancellation propagates after cleanup; it does not undo committed effects.':'I/O became ready; the coroutine resumes and completes.',state);
      }
      return {steps,final:{A:state.A,B:state.B}};
    }
    if (kind==='locking') {
      const state={quota:1,created:0,lock:null,A:null,B:null};
      add('Initial state','One unit of quota is available.',state);
      if (failure) {
        state.A=state.quota;add('A reads','An unguarded snapshot says quota=1.',state);
        state.B=state.quota;add('B reads','B also reads quota=1 before either write.',state);
        for(const task of ['A','B']) {state.quota=state[task]-1;state.created++;add(task+' writes','Both callers believe they won. Final quota hides the duplicated effect.',state);}
      } else {
        for(const task of ['A','B']) {
          state.lock=task;add(task+' locks','A row-level lock serializes the read and guarded write.',state);
          if(state.quota>0){state.quota--;state.created++;add(task+' reserves','The authoritative predicate permits one effect.',state);}
          else add(task+' rejects','No quota remains. This caller cannot create another effect.',state);
          state.lock=null;add(task+' commits','Release the lock after the transaction boundary.',state);
        }
      }
      return {steps,final:{quota:state.quota,created:state.created,invariant:state.created<=1}};
    }
    if (kind==='retrieval') {
      const rankings=[['policy','shipping'],['policy','private']],scores=new Map();
      add('Candidates','Dense and lexical fixtures return ranked candidates; one private result belongs to another tenant.',{rankings});
      for(const ranking of rankings) ranking.forEach((id,i)=>scores.set(id,(scores.get(id)||0)+1/(60+i+1)));
      const fused=[...scores].sort((a,b)=>b[1]-a[1]).map(([id])=>id);
      add('Fuse ranks','Sum reciprocal ranks; ranking is not an authorization or applicability decision.',{fused});
      const authorized=fused.filter(id=>id!=='private');add('Authorize','Remove the other tenant’s result before exposing content.',{authorized});
      const applicable=authorized.filter(id=>id==='policy'&&!failure);add('Check applicability',failure?'The policy was dropped. Shipping text cannot support a refund claim.':'The policy covers the requested rule and exception.',{applicable});
      add('Answer boundary',applicable.length?'Cite the applicable policy.':'Abstain or retrieve again; do not invent a rule.',{action:applicable.length?'cite':'abstain'});
      return {steps,final:{action:applicable.length?'cite':'abstain',privateExposed:false}};
    }
    if(kind==='retries') {
      const state={calls:0,effects:0,approved:true,acknowledged:false,key:'operation-1'};
      add('Approve','Record approval before dispatch and retain one stable operation identity.',state);
      state.calls++;state.effects++;add('Provider commits','The provider fixture deduplicates by the operation key.',state);
      if(failure){add('Acknowledgment lost','Local state cannot tell whether the provider committed; reuse the same key.',state);state.calls++;add('Retry same key','The provider returns the prior effect instead of creating a second one.',state);}
      state.acknowledged=true;add('Reconcile','Call count and business-effect count are separate facts.',state);
      return {steps,final:{calls:state.calls,effects:state.effects,acknowledged:true}};
    }
    throw new Error('Unknown simulation');
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={simulate};else root.GuideSimulations=Object.freeze({simulate});
})(globalThis);
