# Data integrity and private-data interview additions

Added 16 main questions, 32 detailed follow-ups, 16 answer diagrams and 16 code examples across eight topics. Public answers and examples use generic records, entities, fields and tasks, with no references to another application's implementation or repository.

| Topic | Chapter placement | Coverage |
| --- | --- | --- |
| Entity resolution | Data engineering foundations | Source versus entity identity, false merges/splits, reversible links, alias drift and collision audits |
| Unicode and canonical keys | Programming foundations; Sources | Raw preservation, canonical/compatibility normalization, case folding, multilingual collisions, URL semantics and bounded hash suffixes |
| Authenticated encryption | Security | Record/tenant context, nonce and key requirements, tag verification, direct rotation, envelope key concepts and compromise boundaries |
| Loss-aware migrations | Data engineering foundations; Database modeling | Explicit unknowns, quarantine, nested validation, replay, revision guards and concurrent edits |
| Serialization contracts | Programming foundations; Web foundations | Enum codecs, JSON boundaries, version dispatch, unsupported values and rolling compatibility |
| Version and fact provenance | Database modeling; Data engineering foundations | Schema version, record revision, source version, inferred versus confirmed data and correction propagation |
| Heuristic classification | Machine learning foundations; Evaluation engineering | Short-token failures, reviewed vocabularies, abstention, selective accuracy, coverage and confidence limitations |
| Immutable domain models | Programming foundations; Computer science foundations | Frozen versus nested mutable state, ownership, runtime invariants, total versus partial order and unsupported comparisons |

Each question contains a direct detailed answer, a worked failure case, a tradeoff, an exercise, two follow-up answers, a diagram and a runnable code example. Existing study identities remain unchanged. Newly introduced cryptographic and Unicode acronyms have in-answer definitions and glossary entries.

## Code execution

Fourteen examples use the Python standard library and are executed by the normal example checks. Two of those execute actual SQLite statements for guarded updates. The other fixtures isolate normalization, codecs, identity features, inference policies, metrics and ownership behavior. They do not claim distributed concurrency or measured model accuracy.

Two complete examples use `cryptography==50.0.2` and are labeled with their optional dependency in the answer. They execute real AES-GCM operations using ephemeral random keys and synthetic values. They test round-trip decryption, tampered ciphertext, record-context substitution and direct re-encryption under another key. They do not implement a production key-management service, backup key custody or concurrent rotation jobs.

Run their pinned local checks separately:

```sh
python3.11 -m venv /tmp/roadmap-crypto-check
/tmp/roadmap-crypto-check/bin/python -m pip install -r requirements-crypto.txt
/tmp/roadmap-crypto-check/bin/python tests/check_crypto_examples.py
```

The static website does not import this dependency. Core checks syntax-check and preserve the optional examples; the dedicated check executes them against their declared expected outputs. The rendered dependency label and execution instructions distinguish these examples from standard-library fixtures.

## Primary references

Authoring checked official Python Unicode, dataclass, enum and JSON documentation and the cryptography library's authenticated-encryption and key-derivation documentation. SQLite transaction and model-evaluation references support the relevant existing mechanisms. Domain matching policies, migration decisions and synthetic metric examples are original worked designs, not claims about a production application.

Independent technical review remains pending under the existing authoring contract.

Validation passed: `make check` (203 pages, 22,764 internal links, 1,135 chapter answers, 998 code associations), rebuilt formatter/example/source checks, dedicated crypto execution with cryptography 50.0.2, root Chromium navigation including the new dependency-labeled encryption answer, and 31 automated accessibility checks. Existing stable IDs and root/subpath packaging remain valid.
