adr = {'decision': 'one API and one worker', 'reason': 'isolate slow indexing',
       'evidence': 'synthetic workload v1', 'revisit_when': 'queue age exceeds agreed budget'}
print(all(adr.get(key) for key in ('decision', 'reason', 'evidence', 'revisit_when')))
