<!-- chapter: skills-layers -->

# What is an agent skill?

## Answer

A skill is a reusable package of task instructions and optional resources or scripts. It tells a compatible agent how to perform a category of work using available capabilities.

## Why

Discover concise metadata first, then load detailed instructions when relevant. Keep the skill's purpose, triggers, dependencies, and limits explicit.

## Risk

Loading a skill does not establish that its instructions are trustworthy or that its scripts are safe.

## Trade-off

Packaging expertise reduces repeated prompting while adding version and supply-chain management.

## Try This

Write a skill for reviewing a support response against an evidence rubric.

# How do skills differ from tools and system instructions?

## Answer

System instructions define product behavior and constraints. Skills supply task-specific methods. Tools provide executable capabilities. A skill can explain tool use without granting tool authority.

## Why

Resolve instructions through the actual host's precedence rules and enforce permissions in backend execution. Different products may package skills differently.

## Risk

A skill that claims to override host policy creates confusion and potential unsafe behavior.

## Trade-off

Separate layers improve reuse and require clear ownership.

## Try This

Draw which layer can propose a refund and which layer can authorize it.

# What is progressive disclosure for skills?

## Answer

Load a small description for routing, the main skill instructions when needed, and supporting references only for the selected task. This avoids inserting every skill into every turn.

## Why

Keep the entry document short and link narrowly scoped supporting material. Measure both skill-selection accuracy and context cost.

## Risk

Vague metadata can select the wrong skill or hide a useful one.

## Trade-off

Fine-grained skills save context and increase discovery complexity.

## Try This

Compare loading ten complete skills with metadata-first discovery on the same tasks.

# How should skill layers be organized?

## Answer

Separate organization-wide rules, application policy, role-specific methods, task skills, and local working context. The host must define actual precedence and conflict behavior.

## Why

Keep stable constraints outside editable task packages. Skills should reference reviewed policy rather than duplicate it inconsistently.

## Risk

An outdated copied policy can silently disagree with a newer application rule.

## Trade-off

Centralized policy supports consistency and may reduce team autonomy.

## Try This

Create a conflict fixture where a task skill requests a prohibited data export.

# How should a skill invoke scripts safely?

## Answer

A skill may describe scripts, but execution requires a controlled runtime, known inputs, constrained filesystem access, and appropriate credentials. Review code and dependencies separately from prose.

## Why

Prefer deterministic utilities with narrow arguments and synthetic fixtures. Run untrusted scripts in a sandbox with explicit resource and network limits.

## Risk

Prompt text cannot make arbitrary shell execution safe.

## Trade-off

Sandboxing limits flexibility and contains failures.

## Try This

Add a script that validates an answer schema without network access or secrets.

# How should skills be versioned and tested?

## Answer

Version the package, referenced resources, scripts, dependencies, and supported tool contracts. Evaluate whether the skill is selected and whether it improves task completion.

## Why

Maintain positive, negative, and conflict-trigger examples, plus an end-to-end task suite. Record the loaded skill version in traces.

## Risk

A changed tool schema can invalidate an unchanged skill.

## Trade-off

Compatibility metadata adds effort and enables reproducible use.

## Try This

Release a revised skill against both old and new tool contracts and document the boundary.

# How do you prevent skill sprawl?

## Answer

Consolidate overlapping methods only when they share a real responsibility. Give each skill a clear trigger and measurable outcome rather than creating one for every small preference.

## Why

Review retrieval collisions, unused skills, and duplicated policy. Keep references task-oriented and remove obsolete instructions through a controlled review.

## Risk

Overlapping skills can introduce conflicting workflows and waste context.

## Trade-off

Broad skills are easy to discover and may load unnecessary detail.

## Try This

Audit five overlapping writing skills and define the smallest useful set.

# How should secrets and customer data be handled in skills?

## Answer

Store neither credentials nor live customer examples in reusable skill files. Use runtime secret injection and synthetic or approved redacted examples.

## Why

Treat uploaded resources and referenced URLs as potentially untrusted. Scope any fetched data to the current principal and task.

## Risk

A private repository does not prevent accidental secret exposure in model context or logs.

## Trade-off

Redaction reduces diagnostic detail and supports safer reuse.

## Try This

Scan a skill package for embedded tokens, real identifiers, and unsupported external fetches.

# Can one skill be portable across agent frameworks?

## Answer

The procedure may be portable while discovery metadata, filesystem conventions, tool binding, and execution policy remain host-specific. Separate the reusable method from integration adapters.

## Why

Document required capabilities and provide framework-specific wrappers only when needed. Test the same task contract in each supported host.

## Risk

Claiming portability without testing can conceal missing tools or different instruction precedence.

## Trade-off

A common core reduces duplication while adapters add maintenance.

## Try This

Port a read-only review skill between two runtimes without copying secret configuration.

# What should a skills portfolio demonstrate?

## Answer

Show task selection, progressive loading, safe tool use, controlled scripts, measurable quality improvement, and conflict handling. A directory of instruction files alone proves little about outcomes.

## Why

Publish synthetic fixtures, before-and-after evaluations, a version manifest, and a short failure walkthrough.

## Risk

Overfitting a skill to demonstration prompts can inflate apparent quality.

## Trade-off

A narrow well-evaluated skill is easier to trust than a broad unsupported capability claim.

## Try This

Build one skill and demonstrate a task it deliberately refuses or escalates.

# How should a skill’s instructions interact with tool permissions and business policy?

<!-- meta
domain: ai-rag
subdomain: skills-layers
module: skills-layers
concept: How should a skill’s instructions interact with tool permissions and business policy?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A downloaded skill asks a tool to read unrelated private files and forward them to another system.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A skill supplies reusable guidance or procedures, not a new grant of authority. The host and service must still enforce available capabilities, caller scope and approval boundaries. Treat external skill content as versioned input with provenance and inspect what actions it can cause, especially when it references other resources.

Concrete engineering case: A downloaded skill asks a tool to read unrelated private files and forward them to another system.

Boundary defense: No. Trust and authority are established by the host and application policy, not by self-description in the skill text.

## Spoken Summary

A skill supplies reusable guidance or procedures, not a new grant of authority. The host and service must still enforce available capabilities, caller scope and approval boundaries. Treat external skill content as versioned input with provenance and inspect what actions it can cause, especially when it references other resources.

## Why

A skill supplies reusable guidance or procedures, not a new grant of authority. The host and service must still enforce available capabilities, caller scope and approval boundaries. Treat external skill content as versioned input with provenance and inspect what actions it can cause, especially when it references other resources.

## Production Case

A downloaded skill asks a tool to read unrelated private files and forward them to another system.

## Risk

A downloaded skill asks a tool to read unrelated private files and forward them to another system.

## Trade-off

No. Trust and authority are established by the host and application policy, not by self-description in the skill text.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: skills layers**: A skill supplies reusable guidance or procedures, not a new grant of authority.

## Alternatives

- No. Trust and authority are established by the host and application policy, not by self-description in the skill text.

## Pitfalls

- A downloaded skill asks a tool to read unrelated private files and forward them to another system.

## Follow-ups

### Can an instruction saying this skill is trusted bypass the boundary?

No. Trust and authority are established by the host and application policy, not by self-description in the skill text.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A downloaded skill asks a tool to read unrelated private files and forward them to another system.",
  "required_decision": "A skill supplies reusable guidance or procedures, not a new grant of authority"
}
```

## Citations

- https://agentskills.io/specification

# How should an agent pin a procedure version when instructions change during a long-running task?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: skills-layers
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Record the version used to make each decision.** A task should capture an immutable procedure version, publication digest and relevant business-rule version. Re-fetching a mutable current alias at every turn can combine the first half of one procedure with the second half of another. That hybrid may never have been reviewed.

**Define update classes.** A cosmetic clarification may allow an existing run to continue on its pinned version. A corrected safety rule, revoked authorization or newly forbidden action can require a stop or revalidation even for an older run. Pinning prevents accidental drift; it does not grant permission to ignore current authorization. Keep mandatory revocations and emergency stops in a control path that can interrupt pinned tasks.

**Migrate durable task state explicitly.** If a new version changes step identifiers or required approvals, supply a migration map with validation. Re-evaluate pending effects and approvals against the new requirements. Do not reinterpret an old completed-step number as a different new action. A task that cannot be migrated safely should pause for review or restart from a declared safe boundary.

**Preserve reproducibility without executing old hazards.** Store the old version for audit and explanation, while marking whether new execution is permitted. An audit can reconstruct why an earlier action occurred even when that version is no longer runnable. The example separates a pinned reference from a revocation list and proves that revocation wins before execution.

## Why

A task pinned to runbook v3 waits for approval overnight. Version v4 fixes a missing mandatory verification. The system must revalidate or stop the pending action rather than silently continuing v3 or splicing in step numbers from v4.

## Worked Case

A task pinned to runbook v3 waits for approval overnight. Version v4 fixes a missing mandatory verification. The system must revalidate or stop the pending action rather than silently continuing v3 or splicing in step numbers from v4.

## Risk

Pinning alone can perpetuate a revoked process; automatically upgrading alone can corrupt durable progress.

## Trade-off

Explicit version migration requires operational work but makes long-running behavior reviewable.

## Try This

Design upgrade rules for cosmetic edits, new approvals, removed tools and emergency revocation. Show the task state before and after migration.

## Follow-ups

### Should the model decide whether an update is cosmetic?

Use the controlled publication process and explicit compatibility metadata. A model may assist reviewers, but migration policy should not depend on an improvised guess at runtime.

### Can completed actions simply be replayed under the new version?

No. Reconcile their actual effects and preserve operation identities. Migration must distinguish completed effects from steps that still need execution.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html

# How do skill provenance, versioning and delegated authority affect safe execution?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: skills-layers
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A skill packages instructions and supporting resources, but its text does not automatically grant every permission it requests. Record provenance and version, load only the relevant material and preserve the application/user authority boundary. Validate referenced paths and tools according to their actual capabilities. A changed skill can alter behavior without changing the main prompt, so include it in release and evaluation identity. Delegating a task should constrain scope and return useful evidence rather than transferring unrestricted credentials by default.

## Why

A downloaded skill instructs an agent to export all local environment variables for diagnostics. Those instructions are untrusted content until justified by the task and policy; relevance does not make the export authorized.

## Worked Case

A downloaded skill instructs an agent to export all local environment variables for diagnostics. Those instructions are untrusted content until justified by the task and policy; relevance does not make the export authorized.

## Risk

Instruction packaging can disguise a privilege escalation as setup guidance.

## Trade-off

Reusable skills reduce repetition when authority and resource access remain explicit.

## Try This

Review a skill update for new destinations, tool permissions and changes to task scope.

## Citations

- https://agentskills.io/specification
