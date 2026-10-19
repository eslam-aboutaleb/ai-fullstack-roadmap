# AI Full-Stack Engineering Roadmap

A general-purpose interactive learning website with **480 detailed questions across 48 chapters**, 48 practical labs, 48 original synthetic code examples, and four interactive diagram explainers.

The journey covers RAG, databases, concurrency, authentication, agent frameworks, evaluation, observability, context engineering and optimization, prompt techniques, MCP server creation, agent skills, orchestration patterns, harnesses, backend integration, SSE, WebSockets, voice, OCR, and live agents.

## Learning approach

Use the search, practice mode, bookmarks, notes, and progress tracking. Every answer explains mechanisms, risks, safeguards, trade-offs, and a practical exercise. Browser study data stays local and can be exported.

The case is a fictional support platform. No private repository snapshots or project-specific source excerpts are published. Examples use synthetic data, and optional framework integrations state their execution limits.

## Rebuild and preview

Requires Python 3.10+ for authoring and stdlib examples. Rebuild with `python3 -B authoring/build.py`. Serve this directory with `python3 -m http.server 8765 --bind 127.0.0.1` and open `http://localhost:8765`. No backend or model provider is needed to read and use the website.

`authoring/core.json` contains the first 300 generalized questions. `authoring/advanced.txt` contains 180 advanced questions. `authoring/examples.py` contains original teaching examples. `authoring/diagrams/` holds finalized diagram assets. `authoring/build.py` creates the static pages and search index; `authoring/package.py` packages only public files.

## Deployment

The repository remains private; GitHub Pages is public. Pushes to `main` rebuild and deploy via `.github/workflows/pages.yml`. The published artifact contains HTML, CSS, JavaScript, examples, diagrams, and the manifest. Authoring files and Git history are excluded.
