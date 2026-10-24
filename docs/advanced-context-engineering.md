# Advanced context engineering — interview progression (#45)

**Introduction.** Context engineering decides which material a model may see,
how it is attributed and when it must be refreshed. A prompt is not automatically
a trustworthy knowledge store. A large context window is a capacity limit, not
proof that important text near its middle is recalled correctly.

**Mechanism.** Build a context manifest containing separately labeled system
instructions, tool signatures, authenticated task state, retrieved evidence and
memory. Reserve output tokens before packing evidence. Reject missing mandatory
instructions rather than reducing output reserve silently. Scope candidates
to the authenticated owner **before** ranking; data from a document or MCP tool
must never become higher-priority instructions. Maintain document revisions and
source spans.

**Practical exercise.** Run `python3 -B labs/context_packet_policy.py`. Vary
budget, document order and principals. The program reports selected and
excluded items, budget accounting, citations and revision-aware cache keys.
It is **not** an actual tokenizer benchmark; token counts are declared fixture
values. An optional provider comparison must pin actual tokenizer version.

**Test questions.** What stays outside context because of trust? What
happens when a source is revised or permissions revoked? Why must an exception
survive a tool-response summary? How does a lossy dialogue compaction differ
from an authoritative tool-effects ledger? How would you evaluate relevant
evidence moved to the beginning, middle and end of a long prompt?

For each answer, explain the actual failure path, expected invariant, one
contradictory source, a changed assumption and a measurable offline oracle.
A long-context model can be wrong even if this deterministic packet builder
passes its unit tests. Human, task-specific model evaluation remains separate.
