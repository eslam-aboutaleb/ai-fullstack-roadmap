# AI Full-Stack Engineering Roadmap

A course that progresses from intermediate foundations to advanced AI systems through seven dependency-aware stages. Every chapter introduces a concrete use case, defines necessary terms, provides its own interactive diagram, explains ideas through examples, walks through code, and finishes with a practical experiment.

## Learning structure

Start with the guided explanations, inspect the step-through flow, and change its failure condition. The RAG chapter also includes an evidence-policy playground. Use deeper interview questions after the lesson, not as a substitute for learning the topic. Topic coverage determines chapter depth; there is no fixed number of questions per chapter.

The current content includes 223 guided explanations plus the earlier 480 interview questions. These are observed content counts, not authoring quotas. Existing study IDs, notes, and bookmarks remain compatible after chapter reordering. Notes and progress stay in browser storage and support export/import.

## Authoring

- `authoring/course.txt`: chapter goals, concrete cases, terminology, unique flow diagrams, and independently sized guided lessons.
- `authoring/course_data.py`: ordered stages, prerequisites, and content loading.
- `authoring/study_ids.json`: stable study identities; retain it when moving chapters or adding content.
- `authoring/core.json`, `authoring/advanced.txt`: deeper interview material.
- `authoring/code_notes.txt`, `authoring/examples.py`: code reading notes and original synthetic examples.
- `authoring/build.py`: standard-library static generator.
- `authoring/package.py`: packages public static files only.
- `course.js`, `app.js`: teaching interactions and browser-local study features.

Use Python 3.10+ for authoring checks and examples. Rebuild with `python3 -B authoring/build.py`, package with `python3 -B authoring/package.py`, and serve `_site` locally with `python3 -m http.server 8765 --bind 127.0.0.1 --directory _site`.

`python3 -B authoring/check.py` verifies generated links, study-ID compatibility, nonuniform topic depth, privacy boundaries, and executable synthetic examples. It requires the public artifact to be packaged first.

## Scope and deployment

This is fictional educational material. No private project source snapshots or live customer data are published. Interactive examples are deterministic simulations, not live model output. Optional framework sketches, SQL, and OCR examples state their limits. The synthetic backend lab illustrates HTTP tasks, SSE replay, cancellation, and WebSocket control using process-local state.

The repository remains private while GitHub Pages is public. Pushes to `main` rebuild and publish only the static artifact. Print controls are omitted.
