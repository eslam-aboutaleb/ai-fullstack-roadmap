# Optional integration labs

These files are educational and use synthetic data. They are not production applications.

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
