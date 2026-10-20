# Optional integration labs

These files are educational and use synthetic data. They are not production applications.

## Browser-based JavaScript labs

The following labs run directly in a browser console (paste the contents) or with
Node.js. No installation, provider keys, or network access are needed.

- `labs/retrieval_ranking.js` — Reciprocal Rank Fusion: combine dense and lexical search results into one ranked list.
- `labs/agent_state_machine.js` — Controlled agent loop with stop conditions, tool policy, and failure injection.
- `labs/rate_limiter.js` — Token bucket rate limiter: burst capacity and refill for API/tool calls.

Run a lab with `node labs/<file>.js`, or open the file in a browser and paste its
contents into the console. Each lab includes embedded assertions and "try it yourself"
prompts to explore failure modes.

## Python labs (downloadable scripts)

The following labs run locally with Python 3.10+ and the standard library only.
Save the file and run `python labs/<file>.py`.

## Source and generated copies

Contributors edit this `labs/` folder. From the repository root, the source
service can be started as `uvicorn labs.streaming_app:app --host 127.0.0.1 --port 8000`
after installing its optional dependencies and setting `DEMO_API_TOKEN`.
Run the offline source bridge with `python labs/foundation_bridge.py`.

The build also publishes lab copies under `_site/examples/labs/`. The commands
below use that generated layout: run them from `_site/`, or download the public
example package while preserving its `examples/labs/` structure.

## HTTP, SSE, and WebSocket service

In an isolated environment install compatible FastAPI and Uvicorn versions. Set `DEMO_API_TOKEN` to a local test secret and run:

```sh
uvicorn examples.labs.streaming_app:app --host 127.0.0.1 --port 8000
```

Authenticate HTTP requests with `Authorization: Bearer <your local test secret>`.

1. `POST /tasks` with JSON `{"message":"hello"}` returns an accepted task ID.
2. `GET /tasks/{task_id}/events` returns SSE; `after` or `Last-Event-ID` resumes retained events.
3. `GET /tasks/{task_id}` returns the authoritative status **within this one process**.
4. `POST /tasks/{task_id}/cancel` requests cancellation.
5. `/control` is a WebSocket. The first JSON frame is `{"token":"<your local test secret>"}`; later frames can request `{"type":"status","task_id":"..."}`.

The output is scripted, not model-generated. The store disappears on restart, identity is a single synthetic user, and admission is limited to 100 retained tasks. The demo does not implement fleet-wide durability, real tenant auth, production origin policy, or a full resource-control policy. Add those for the associated labs. A browser fetch client can supply authorization headers; standard EventSource cannot supply arbitrary custom headers.

## Voice pipeline

`python examples/labs/voice_pipeline.py` runs injected synthetic STT, agent, and TTS adapters. Its bytes are deliberately not real audio. Implement real capture, utterance finalization, generation IDs, interruption, deadlines, and privacy before substituting providers.

## OCR

The optional OCR example needs Pillow, pytesseract, and a local Tesseract installation. It accepts an approved synthetic PNG and emits recognized text with page and bounding-box metadata. It has not been run against a document or OCR engine for this edition. Run parsers in an isolated environment for untrusted uploads; the example's size checks are not a complete isolation boundary.

## Foundation bridge: offline calculations and SQL

Run `python examples/labs/foundation_bridge.py` with Python 3.10+; no packages,
provider keys, or network access are needed. It walks through a gradient update,
cosine similarity, retrieval metrics, and parameterized SQL over synthetic rows.
Expected values include weight 2.6, loss 0.64, cosine about 0.707107, precision
1/3, recall 1/2, and one authorized revision-2 row. The embedded assertions
check those worked examples and reject invalid vector comparisons.

Change the learning rate, ranking, or owner and predict the result before running.
SQLite is used only to make the SQL exercise self-contained; use the separate
PostgreSQL labs for roles, row security, query planning, and concurrency semantics.

## Reviewed pilot labs

- `reservation_race.py`: Python 3.10+, standard library. Two separate SQLite
  connections contend for one primary key in a temporary database; both outcomes
  and the committed row count are asserted. This is not a PostgreSQL isolation test.
- `effect_oracle.py`: Python 3.10+, standard library. Checks authorized fixture
  events, approval/eligibility before write, and exact final state; includes negative
  cases. A real integration needs a trusted complete ledger.
- `request_lifecycle.py`: optional FastAPI/Pydantic and httpx packages, pinned in
  `requirements-dev.txt`. Run the script for TestClient checks or serve
  `uvicorn labs.request_lifecycle:app` locally. It demonstrates validation and a
  synthetic 202 response, without persisting or scheduling jobs.

The JavaScript source files remain downloadable console/Node exercises. The site
also includes an in-page Worker-backed coding workbench and optional self-hosted
Pyodide runtime. Source assertions throw on failure and run in ordinary content CI.

## Executable foundational pilots and connected projects

- `async_job_engine.py` (Python 3.11+, standard library): bounded producer/worker
  flow, job exceptions, timeouts, cancellation propagation and cleanup.
- `model_training.py` (standard library): 2→4→1 network, independent finite-difference
  checks for all 17 parameters, fixed training/validation/test splits and measured
  loss. Its tiny synthetic accuracy is not a real-world model-quality claim.
- `attention_math.py` (standard library): numerical attention, prefix K/V reuse,
  byte-token roundtrips and an int8 error-bound fixture.
- `rag_evaluation.py` (standard library): scoped retrieval, independent relevance
  labels, abstention and a deliberately broken index that the metrics reject.
- `durable_agent.py` (standard library): approval before dispatch, independently
  committed provider fixture, lost acknowledgment and stable effect identity.
- `transaction_api.py` (optional local PostgreSQL/FastAPI): server-established
  owners, guarded transactions, concurrent idempotency, payload conflicts and outbox.
- `fullstack_demo.py`: connects the task API, bounded analysis, scoped retrieval
  and durable fixture effects with a local form UI. No LLM provider is involved.
- `numpy_torch_bridge.py` (optional Python 3.14+, requirements-models.txt): batched
  NumPy arrays, PyTorch gradients compared with the scalar implementation, numerical
  gradcheck, CPU training and held-out fixture evaluation.

All referenced files and sibling imports are included in the generated
`examples/local-projects.zip`, with license and dependency instructions.

For the connected app, use an isolated environment and a new disposable PostgreSQL
database. Install `requirements-labs.txt`. Configure `DATABASE_URL`, two distinct
random local tokens `DEMO_TOKEN_A`/`DEMO_TOKEN_B` of at least 16 characters, and a
local `DEMO_LEDGER_PATH`, then run:

```sh
uvicorn labs.fullstack_demo:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` and enter the local token. The browser keeps the token
only in the form, and repeats a question submission with the same operation key
until the question is edited. Confirmation requires an explicit authorized POST.
The provider is a SQLite fixture, not a payment processor or external connector.

From a full repository checkout, `python scripts/test_postgres_pilot.py` performs
the complete disposable-cluster integration test. macOS/Linux need local PostgreSQL
tools on PATH (the harness also detects common Linux package paths). On Windows,
add PostgreSQL’s bin directory to PATH and use `py -3.11 scripts/test_postgres_pilot.py`.
The harness omits Unix sockets on Windows; this platform path has not been executed
in the current macOS verification environment.
Run the tensor bridge from a checkout with `python -m labs.numpy_torch_bridge`.
