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

## Complete local project and independent exercise

The chapter now contains seven additional graduated memory interviews (study IDs
1217–1223), three explanatory state/timeline diagrams, six automatically checked
adverse-case assessments and a separately graded architecture/replay project.
The original question 305 and all prior bookmarks retain their identities.

Use Python 3.11+; no packages, model, account or website backend are needed:

```sh
python3 -B labs/memory_project.py check
python3 -B labs/memory_project.py append --database memory.sqlite --owner learner --key language --value English --request p1 --at 10 --consent
python3 -B labs/memory_project.py correct --database memory.sqlite --owner learner --key language --value Arabic --request p2 --at 15 --observed 17 --expires 30 --consent
python3 -B labs/memory_project.py query --database memory.sqlite --owner learner --key language --at 16 --observed 16 --mode exact
python3 -B labs/memory_project.py query --database memory.sqlite --owner learner --key language --at 16 --observed 18 --mode exact
python3 -B labs/memory_project.py export --database memory.sqlite --owner learner --at 20
python3 -B labs/memory_project.py expire --database memory.sqlite --owner learner --at 30
python3 -B labs/memory_project.py delete --database memory.sqlite --owner learner --key language --at 31
```

The historical query returns English; the reconstructed later view returns
Arabic; the expiry removes every retained version and derived projection for
that preference. `check` creates and removes its own temporary database and
asserts owner isolation, replay conflict, both clocks, latest-expiry behavior,
export, local projection erasure and restart. On the original four-case oracle,
exact key lookup is correct on 2/4, lexical on 4/4 and hybrid on 4/4, with zero
false recalls for the single unknown case. These are executed fixture counts,
not an embedding/model benchmark. Hybrid uses lexical plus character-vector
cosine reciprocal ranks. It is not measured to beat lexical search here.

The event rows are attributed observations; the exported semantic fact projection
is their current interpretation. The CLI's `--owner` is trusted local host input,
not a remote authentication mechanism. Deleting fact rows, derived text/vectors
and the owner generation shares one local transaction. Logical erasure does not
prove secure physical wiping, backup deletion or external cache propagation.
The scratch CLI file can be removed after practice; do not use personal secrets.

For the capstone, author eight new gold histories before running the retriever.
Compare recency-only, exact and hybrid strategies; report correct target recall,
false recall, corrected-preference consistency, growth and actual elapsed query
time. A cross-owner candidate, stale deleted source or invented effect fails
regardless of average score. Submit histories, oracle, commands, outputs, a
restore/deletion demonstration and the design defense in the chapter assessment.
This subjective project requires explicit rubric review and cannot auto-pass.

Source/review method: the project was authored and executed locally; timestamps,
ranking and transaction expectations are explicit fixture contracts. Technical
review is performed by Technical curriculum review under the maintainer's delegation, not claimed
as independent human review. Primary references remain linked in each answer.

## Fixed adversarial histories — 23 October 2026

Run `python3 -B labs/memory_adversarial.py --output memory-adversarial.json`.
The authored gold suite has eight independent histories: late correction, lost
confirmation with exact replay and changed-payload rejection, malicious source
and value text, stale derived summary, actor swap, consent refusal, deletion
and expiry without resurrecting an older preference. Across exact, lexical and
hybrid modes it checks 27 expected outcomes and records actual query durations.
Gold values are source-authored constants, not retriever-generated labels.
`docs/evidence/memory-adversarial.json` preserves observed outputs.

The poisoning case checks parameterized SQL and preservation of data as data;
it does not run an LLM or prove prompt-injection resistance. Actor identity is
trusted local host input, not remote authentication. The suite asserts current
owner facts, no private sentinel disclosure, atomic local deletion and correct
bitemporal selection. Physical wiping, remote cache/backup deletion, learned
semantic quality and representative latency are outside its evidence.

The existing four-query recency/exact/lexical/hybrid comparison remains separate.
The learner must still author new gold histories rather than memorizing these
cases. Full procedural/extraction/confidence/conflict and long-horizon curriculum
coverage and outcome/rubric mapping remain open requirements for issue #44.
