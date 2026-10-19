# Optional integration labs

These files are educational and use synthetic data. They are not production applications.

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
