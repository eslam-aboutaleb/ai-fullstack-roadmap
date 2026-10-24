# Advanced asyncio and FastAPI production interview practice (#15)

The existing Python/backend course introduces foundations first, then uses
interview-style questions. This increment adds four **detailed** answers about
TaskGroup lifetime, API authorization, transactional outbox redelivery and
the test oracles for async failures. Companion course pages display the
complete `deep` answer directly; the legacy concise `spoken` metadata remains
available for source compatibility but is **not duplicated** in the learner UI.

Run `python3 -B labs/async_backend_failure.py`. It exercises a bounded
asyncio.Queue and TaskGroup, real SQLite uniqueness, lost response after
commit, identical retry, changed payload conflict, two owners and local
cancellation. The fixture models a single-process API; it does not prove
remote exactly-once effects, live PostgreSQL locks or multi-replica safety.

**Interview order:** define event-loop cooperative scheduling; walk a request
through FastAPI validation, trusted identity and an owner-scoped write;
explain the transaction-vs-socket timeline; reproduce the duplicate delivery;
then defend rollback/reconciliation, shutdown, monitoring and alternate
worker/queue systems under changed assumptions.

The existing `async_job_engine.py`, `transaction_api.py`, container workbench
and PostgreSQL tests remain core sources; this exercise adds another observed
failure boundary, not an invented claim that the entire backend syllabus is complete.
