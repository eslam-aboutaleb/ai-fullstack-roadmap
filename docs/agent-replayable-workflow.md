# Safe local research/support agent workflow (#18)

Introduction: an LLM can propose work; a trusted application harness decides
which tools are available, how permissions are checked and when effects commit.
A tool result is never an authorization grant. A model checkpoint or prose
summary is not an authoritative business ledger.

Run python3 -B labs/replayable_agent_workflow.py

The fixture uses SQLite on local disk, explicit approval, stable effect IDs,
request-body hashing, owner-scoped trace events and restart/replay assertions.
A synthetic retrieved page contains malicious text; tests ensure it cannot
turn a denied write into an approved write. Effects and trace event data
persist independently of the model's conversation.

This is a deterministic harness without a model, network connector, MCP
implementation or real UI approval. To finish the broader issue, add a local
real research agent with correctly pinned protocol SDK, authenticated
approved side effects, multi-process crash/fault injection, trajectory scoring,
streaming trace explorer and independent review. Static Pages never hosts
the agent backend; it documents and packages optional local exercises.
