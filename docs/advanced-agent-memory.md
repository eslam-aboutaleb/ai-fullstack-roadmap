# Advanced agent memory — interview-driven reference (#44)

**Introduction: Why memory is not just a longer prompt.** A conversation
window is transient input to a model; durable memory is an independently
authorized and versioned application record. Working memory holds in-flight
task state; *episodic memory* describes observed events and their provenance;
*semantic memory* stores consolidated claims derived from those events;
preferences are user-controlled temporal facts, not claims invented by a model.

The runnable CPU-only `labs/agent_memory_lifecycle.py` uses SQLite and a
trusted Principal. It demonstrates explicit consent, idempotent facts, validity
time versus recording time, source citations, late preference corrections,
expiry, tenant filtering **before** selection and local deletion. Run:

```bash
python3 -B labs/agent_memory_lifecycle.py
```

Do not confuse the local deletion test with a production right-to-erasure
implementation: real caches, backups, vector projections, connectors and
replicas must propagate and verify deletion requests. A query-specific summary
is a derived view; it cannot override a confirmed source event or committed
business side effect.

## Interview learning map

1. What distinguishes current prompt context, in-progress task state,
   episodic event memory and semantic fact memory? Trace one correction.
2. Why do *valid time* and *recorded time* differ, and how do late arrivals
   change what was known at a historical decision point?
3. Why is a summary not automatically a verified source? How should
   consolidation deal with contradictory and untrusted claims?
4. How does an index enforce an owner's retrieval policy before ranking,
   especially if a vector DB returns approximate neighbors?
5. How do consent, expiration and deletion travel through derived storage,
   and what evidence is needed to claim they finished?

A deep answer must discuss the exact boundary, SQL query, failure path and
the changed assumption (late correction, revoked consent, replay after crash,
expired data or another user's similar embedding). Do not claim all these
production integration boundaries are implemented by the SQLite lab.
