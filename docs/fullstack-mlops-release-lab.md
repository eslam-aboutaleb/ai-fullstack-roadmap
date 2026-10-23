# Full-stack delivery, data and MLOps failure lab (issue #19)

Intro: production AI applications connect browser state, authenticated APIs,
data versioning and model/index deployments. Success at one layer does not
prove end-to-end correctness or safety.

1. `node labs/stream_session_reducer.cjs`: test a bounded streaming UI
state machine (new request epochs, late tokens, logout, citations). A real
React integration needs accessible rendering, AbortController, auth-scoped
server cache keys and browser E2E tests. Client-side gating is not auth.
2. `python3 -B labs/data_rollout_contract.py`: real local SQLite CDC
checkpoint atomicity, deduplication, gaps, tombstone preservation and owner
isolation, plus a **synthetic** digest/schema/error-budget release gate.

Real infrastructure continuation: pin Docker images and digest, run pipeline
source/target integration using Kafka or Beam as needed, validate migrations,
Kubernetes readiness vs liveness, perform actual rollout undo, measure task
quality/SLOs, check backup restore/tombstone high-water, cloud secrets
management and incident response. The offline release predicate is not a
Kubernetes rollout, and existing local browser tests do not prove auth.

Official reference: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
