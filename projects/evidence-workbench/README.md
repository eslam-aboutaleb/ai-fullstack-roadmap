# Evidence workbench: cumulative browser/API project

Build a typed interface that can explain why an answer is complete, incomplete or
unsupported. The reference compiles React/TypeScript and speaks to a real local
Python HTTP server; documents and identities are synthetic. No model account,
cloud deployment or database is required. Use Node 22.12+ and Python 3.11+.

```sh
cd projects/evidence-workbench
npm ci --ignore-scripts
npm run build
python3 server.py
```

Open http://127.0.0.1:8787. Development alternative: run the same API and
`npm run dev` in a second terminal; Vite proxies `/api` to the local API.
The browser app is an optional local learning project. It is not loaded into the
roadmap's static reading pages. From a checkout, acceptance checks run with:

```sh
python projects/evidence-workbench/tests/check_workbench.py
```

Install the repository's `requirements-dev.txt` and Chromium first, and build the
project. Both source ZIPs include the requirements file at their extraction root;
from that root run `python -m pip install -r requirements-dev.txt` and
`python -m playwright install chromium`. Then run the checker from the extraction
root as shown above. The optional axe check uses the root `npm ci` installation when present.
CI installs that dependency and runs the check against real HTTP and Chromium.

## Read the system before changing it

`src/App.tsx` owns form state and one active request generation. `Answer` receives
presentation data. `contracts.ts` accepts unknown runtime input, narrows it into a
discriminated union, decodes fragmented UTF-8 and bounds frames. TypeScript only
checks compiled code: it cannot make an HTTP body conform to a declared type.
The Python handler validates input independently and chooses the document from
the authenticated fixture identity before constructing a response. There is no
caller-provided owner field and no frontend-only authorization filter.

The protocol is NDJSON, not SSE: each newline completes one JSON event. Sequence
and request identity are checked, identical replay is ignored and conflicting
replay is rejected. EOF without a final frame is failure. All answer text renders
through React text children, including the literal `<b>` payload. A complete
citation is still only membership evidence; semantic support requires review.

Submission belongs in the form event handler. An Effect cleans up when the
component unmounts; it does not send an answer request just because rendering
occurred. An identity switch increments the generation, aborts the old fetch and
clears retained text. The generation check also protects against callbacks that
were delivered before cancellation. Cancelling presentation cannot undo a remote
payment; this project makes no external business effect.

## Independent implementation milestones

1. Start with a blank `src/App.tsx`, preserve the public request/response contract,
   and draw the form → scoped API → stream parser → answer sequence yourself.
2. Implement normal completion and unsupported-question abstention. Save network
   evidence proving Owner A never receives Owner B's document.
3. Reproduce slow-response identity switching, malformed JSON and missing final
   events. Disable identity-switch invalidation deliberately: show a failing test before
   restoring it. Add a conflicting replay fixture and an overlong frame case.
4. Add actual SSE as a separate endpoint and parser using the linked MDN grammar.
   Demonstrate that byte chunks are not events and document reconnect semantics.
5. Add a real session provider as a separate extension. Replace public demo tokens,
   define issuer/audience/expiry handling and a CSRF policy if using cookies. Add
   object-level authorization and logout cache invalidation acceptance evidence.
6. Measure first response and final response separately, with device, browser,
   bundle size, update count and fixture size. Do not infer concurrent capacity
   from this small single-user timing.

Deliver source, lockfile, build output, failing/passing acceptance evidence,
architecture, threat model and a short incident report. A reference run alone
does not satisfy the independent implementation milestone.

## Container and cluster recovery extension

The Dockerfile builds the frontend and runs the API as a non-root process. The
image tags are exercise inputs; record actual image digests, dependency locks and
build provenance before production promotion. On a machine with Docker:

```sh
docker build -t evidence-workbench:local projects/evidence-workbench
docker run --rm -p 127.0.0.1:8787:8787 evidence-workbench:local
```

Use a disposable local kind cluster, not an existing shared cluster. Load the
image, apply the manifest, then inspect availability before port forwarding:

```sh
kind create cluster --name roadmap-practice
kind load docker-image evidence-workbench:local --name roadmap-practice
kubectl --context kind-roadmap-practice apply -f projects/evidence-workbench/deploy/workbench.yaml
kubectl --context kind-roadmap-practice rollout status deployment/evidence-workbench --timeout=150s
kubectl --context kind-roadmap-practice port-forward service/evidence-workbench 8787:8787
```

In a separate terminal, deliberately set an unavailable image. Inspect events,
ReplicaSets and the Progressing condition. A progress deadline reports a stalled
rollout; Kubernetes does not automatically roll it back. Undo explicitly:

```sh
kubectl --context kind-roadmap-practice set image deployment/evidence-workbench workbench=evidence-workbench:missing
kubectl --context kind-roadmap-practice rollout status deployment/evidence-workbench --timeout=150s
kubectl --context kind-roadmap-practice describe deployment evidence-workbench
kubectl --context kind-roadmap-practice rollout undo deployment/evidence-workbench
kubectl --context kind-roadmap-practice rollout status deployment/evidence-workbench --timeout=150s
kind delete cluster --name roadmap-practice
```

Save timestamps and HTTP health checks before/during/after the failure. Readiness
removes an unready instance from Service endpoints; liveness restarts an unhealthy
process. This stateless reference uses the same shallow endpoint for both; a real
readiness contract may include critical dependencies, while liveness should not
restart every replica because a remote provider is temporarily down. Container
and kind commands are learner instructions until their output is recorded; they
have not been executed in the current authoring environment.

## Review and interview defense

- Why is `as Answer` insufficient for `response.json()`? Explain the runtime boundary.
- How can an old owner's text appear after logout even when the UI was cleared?
  Trace ownership through queued callbacks, cache keys and generation changes.
- A stream ends after plausible prose. Which evidence permits Complete? Show a
  final frame and explain the remaining gap between citation membership and support.
- Which event becomes authoritative if cancellation races completion? State a
  presentation policy and separate it from durable backend operation status.
- Does a failed rollout imply old replicas are unavailable? Inspect desired,
  available and updated replicas and explain maxUnavailable/maxSurge costs.

## Primary context

- https://react.dev/learn/synchronizing-with-effects (events, cleanup, stale results)
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html (runtime narrowing)
- https://vite.dev/guide/ (compiler/build contract and Node requirements)
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ (rollout status and rollback limits)
- https://www.w3.org/WAI/test-evaluate/preliminary/ (manual accessibility review scope)

The loopback server is a teaching server with public fixture credentials, an
in-memory corpus and per-request threads. It is not a production authentication,
admission-control or model-serving implementation.
