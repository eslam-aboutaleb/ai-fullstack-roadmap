<!-- chapter: programming-foundations -->

# Why can appending to one Python list change another variable?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: Why can appending to one Python list change another variable?
difficulty: interview
misconception_target: Missing the stated reference aliasing boundary: A request template contains a nested tags list. A shallow outer copy is modified for one customer and changes the next customer’s defaults.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Assignment binds names to objects; it does not recursively copy them. If a and b refer to the same list, appending through either name changes that shared object. A shallow copy makes a new outer list while nested mutable elements can still be shared. Choose ownership explicitly instead of copying every object indiscriminately.

Engineering case: A request template contains a nested tags list. A shallow outer copy is modified for one customer and changes the next customer’s defaults.

Reasoning under a changed assumption: No. A tuple can contain a mutable list. Tuple immutability prevents replacing its element references, not mutation of a referenced object.

## Spoken Summary

Assignment binds names to objects; it does not recursively copy them. If a and b refer to the same list, appending through either name changes that shared object. A shallow copy makes a new outer list while nested mutable elements can still be shared. Choose ownership explicitly instead of copying every object indiscriminately.

## Why

Assignment binds names to objects; it does not recursively copy them. If a and b refer to the same list, appending through either name changes that shared object. A shallow copy makes a new outer list while nested mutable elements can still be shared. Choose ownership explicitly instead of copying every object indiscriminately.

## Production Case

A request template contains a nested tags list. A shallow outer copy is modified for one customer and changes the next customer’s defaults.

## Risk

A request template contains a nested tags list. A shallow outer copy is modified for one customer and changes the next customer’s defaults.

## Trade-off

No. A tuple can contain a mutable list. Tuple immutability prevents replacing its element references, not mutation of a referenced object.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Reference aliasing**: Assignment binds names to objects; it does not recursively copy them.

## Alternatives

- No. A tuple can contain a mutable list. Tuple immutability prevents replacing its element references, not mutation of a referenced object.

## Pitfalls

- A request template contains a nested tags list. A shallow outer copy is modified for one customer and changes the next customer’s defaults.

## Follow-ups

### Does an immutable tuple guarantee recursively immutable data?

No. A tuple can contain a mutable list. Tuple immutability prevents replacing its element references, not mutation of a referenced object.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A request template contains a nested tags list. A shallow outer copy is modified for one customer and changes the next customer’s defaults.",
  "decision": "Assignment binds names to objects; it does not recursively copy them"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# What goes wrong with a mutable default argument in Python?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: What goes wrong with a mutable default argument in Python?
difficulty: interview
misconception_target: Missing the stated mutable default argument boundary: A helper called append_tag stores one request’s tag in a default list. The next request inherits that tag despite providing no prior history.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Default argument expressions are evaluated when the function is defined. A default list can therefore retain additions across calls. Use None as the sentinel and create a new list inside the function when a fresh collection is intended. Sometimes persistent shared state is deliberate, but it should be explicit and synchronized if accessed concurrently.

Engineering case: A helper called append_tag stores one request’s tag in a default list. The next request inherits that tag despite providing no prior history.

Reasoning under a changed assumption: Only if the function treats it as immutable input and builds the required output separately. The correct fix follows the ownership and mutation contract, not a mechanical syntax replacement.

## Spoken Summary

Default argument expressions are evaluated when the function is defined. A default list can therefore retain additions across calls. Use None as the sentinel and create a new list inside the function when a fresh collection is intended. Sometimes persistent shared state is deliberate, but it should be explicit and synchronized if accessed concurrently.

## Why

Default argument expressions are evaluated when the function is defined. A default list can therefore retain additions across calls. Use None as the sentinel and create a new list inside the function when a fresh collection is intended. Sometimes persistent shared state is deliberate, but it should be explicit and synchronized if accessed concurrently.

## Production Case

A helper called append_tag stores one request’s tag in a default list. The next request inherits that tag despite providing no prior history.

## Risk

A helper called append_tag stores one request’s tag in a default list. The next request inherits that tag despite providing no prior history.

## Trade-off

Only if the function treats it as immutable input and builds the required output separately. The correct fix follows the ownership and mutation contract, not a mechanical syntax replacement.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Mutable default argument**: Default argument expressions are evaluated when the function is defined.

## Alternatives

- Only if the function treats it as immutable input and builds the required output separately. The correct fix follows the ownership and mutation contract, not a mechanical syntax replacement.

## Pitfalls

- A helper called append_tag stores one request’s tag in a default list. The next request inherits that tag despite providing no prior history.

## Follow-ups

### Is using an empty tuple as the default always a complete fix?

Only if the function treats it as immutable input and builds the required output separately. The correct fix follows the ownership and mutation contract, not a mechanical syntax replacement.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A helper called append_tag stores one request’s tag in a default list. The next request inherits that tag despite providing no prior history.",
  "decision": "Default argument expressions are evaluated when the function is defined"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# How do Python return values, exceptions and None describe different outcomes?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: How do Python return values, exceptions and None describe different outcomes?
difficulty: interview
misconception_target: Missing the stated error contract boundary: A parser returns None for both a missing optional field and invalid JSON. The caller treats corrupted input as a valid empty record and persists it.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A return value communicates a normal result; an exception communicates a failure outside that normal contract. None can be a valid absence value only if callers know how to distinguish it from failure. Do not catch every exception and return None, because that erases whether a record is absent, malformed or unavailable.

Engineering case: A parser returns None for both a missing optional field and invalid JSON. The caller treats corrupted input as a valid empty record and persists it.

Reasoning under a changed assumption: Translate it when crossing a boundary with a clearer public contract. Preserve the original cause for diagnosis and avoid exposing sensitive raw payloads in the public error.

## Spoken Summary

A return value communicates a normal result; an exception communicates a failure outside that normal contract. None can be a valid absence value only if callers know how to distinguish it from failure. Do not catch every exception and return None, because that erases whether a record is absent, malformed or unavailable.

## Why

A return value communicates a normal result; an exception communicates a failure outside that normal contract. None can be a valid absence value only if callers know how to distinguish it from failure. Do not catch every exception and return None, because that erases whether a record is absent, malformed or unavailable.

## Production Case

A parser returns None for both a missing optional field and invalid JSON. The caller treats corrupted input as a valid empty record and persists it.

## Risk

A parser returns None for both a missing optional field and invalid JSON. The caller treats corrupted input as a valid empty record and persists it.

## Trade-off

Translate it when crossing a boundary with a clearer public contract. Preserve the original cause for diagnosis and avoid exposing sensitive raw payloads in the public error.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Error contract**: A return value communicates a normal result; an exception communicates a failure outside that normal contract.

## Alternatives

- Translate it when crossing a boundary with a clearer public contract. Preserve the original cause for diagnosis and avoid exposing sensitive raw payloads in the public error.

## Pitfalls

- A parser returns None for both a missing optional field and invalid JSON. The caller treats corrupted input as a valid empty record and persists it.

## Follow-ups

### When should a lower-level exception be translated?

Translate it when crossing a boundary with a clearer public contract. Preserve the original cause for diagnosis and avoid exposing sensitive raw payloads in the public error.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A parser returns None for both a missing optional field and invalid JSON. The caller treats corrupted input as a valid empty record and persists it.",
  "decision": "A return value communicates a normal result; an exception communicates a failure outside that normal contract"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# When should a Python interface use an iterator instead of constructing a list?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: When should a Python interface use an iterator instead of constructing a list?
difficulty: interview
misconception_target: Missing the stated iterator lifecycle boundary: A file reader yields records, but a caller calls list(reader) before filtering. Peak memory still grows with the full input.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

An iterator yields values as they are requested and can avoid retaining the entire result. It may be single-use and can defer errors until iteration. A list supports repeated traversal and indexed access but retains its elements. Streaming is useful only when downstream consumers do not immediately materialize the whole iterator.

Engineering case: A file reader yields records, but a caller calls list(reader) before filtering. Peak memory still grows with the full input.

Reasoning under a changed assumption: Yes. If its lifecycle owns an open resource, partial iteration can delay cleanup. Make resource ownership explicit with context managers or a caller-owned file handle.

## Spoken Summary

An iterator yields values as they are requested and can avoid retaining the entire result. It may be single-use and can defer errors until iteration. A list supports repeated traversal and indexed access but retains its elements. Streaming is useful only when downstream consumers do not immediately materialize the whole iterator.

## Why

An iterator yields values as they are requested and can avoid retaining the entire result. It may be single-use and can defer errors until iteration. A list supports repeated traversal and indexed access but retains its elements. Streaming is useful only when downstream consumers do not immediately materialize the whole iterator.

## Production Case

A file reader yields records, but a caller calls list(reader) before filtering. Peak memory still grows with the full input.

## Risk

A file reader yields records, but a caller calls list(reader) before filtering. Peak memory still grows with the full input.

## Trade-off

Yes. If its lifecycle owns an open resource, partial iteration can delay cleanup. Make resource ownership explicit with context managers or a caller-owned file handle.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Iterator lifecycle**: An iterator yields values as they are requested and can avoid retaining the entire result.

## Alternatives

- Yes. If its lifecycle owns an open resource, partial iteration can delay cleanup. Make resource ownership explicit with context managers or a caller-owned file handle.

## Pitfalls

- A file reader yields records, but a caller calls list(reader) before filtering. Peak memory still grows with the full input.

## Follow-ups

### Can a generator silently keep a file open?

Yes. If its lifecycle owns an open resource, partial iteration can delay cleanup. Make resource ownership explicit with context managers or a caller-owned file handle.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A file reader yields records, but a caller calls list(reader) before filtering. Peak memory still grows with the full input.",
  "decision": "An iterator yields values as they are requested and can avoid retaining the entire result"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# What does a Python type annotation guarantee at runtime?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: What does a Python type annotation guarantee at runtime?
difficulty: interview
misconception_target: Missing the stated runtime type checking boundary: A function annotated amount: int receives the string "10" from JSON. Later arithmetic concatenates strings or raises at an unrelated line.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

An ordinary annotation documents and supports static analysis of a value; Python does not automatically enforce it when a function is called. Validate untrusted data at input boundaries and use internal types to express the checked representation. Avoid repeated conversions throughout the program that make the authoritative representation unclear.

Engineering case: A function annotated amount: int receives the string "10" from JSON. Later arithmetic concatenates strings or raises at an unrelated line.

Reasoning under a changed assumption: Usually validate at trust boundaries and keep a clear checked internal representation. Revalidate when data crosses a new independent boundary or its invariants may have changed.

## Spoken Summary

An ordinary annotation documents and supports static analysis of a value; Python does not automatically enforce it when a function is called. Validate untrusted data at input boundaries and use internal types to express the checked representation. Avoid repeated conversions throughout the program that make the authoritative representation unclear.

## Why

An ordinary annotation documents and supports static analysis of a value; Python does not automatically enforce it when a function is called. Validate untrusted data at input boundaries and use internal types to express the checked representation. Avoid repeated conversions throughout the program that make the authoritative representation unclear.

## Production Case

A function annotated amount: int receives the string "10" from JSON. Later arithmetic concatenates strings or raises at an unrelated line.

## Risk

A function annotated amount: int receives the string "10" from JSON. Later arithmetic concatenates strings or raises at an unrelated line.

## Trade-off

Usually validate at trust boundaries and keep a clear checked internal representation. Revalidate when data crosses a new independent boundary or its invariants may have changed.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Runtime type checking**: An ordinary annotation documents and supports static analysis of a value; Python does not automatically enforce it when a function is called.

## Alternatives

- Usually validate at trust boundaries and keep a clear checked internal representation. Revalidate when data crosses a new independent boundary or its invariants may have changed.

## Pitfalls

- A function annotated amount: int receives the string "10" from JSON. Later arithmetic concatenates strings or raises at an unrelated line.

## Follow-ups

### Should every internal operation repeat JSON validation?

Usually validate at trust boundaries and keep a clear checked internal representation. Revalidate when data crosses a new independent boundary or its invariants may have changed.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A function annotated amount: int receives the string \"10\" from JSON. Later arithmetic concatenates strings or raises at an unrelated line.",
  "decision": "An ordinary annotation documents and supports static analysis of a value; Python does not automatically enforce it when a function is called"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# How do you write a regression test that actually detects the reported Python defect?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: How do you write a regression test that actually detects the reported Python defect?
difficulty: interview
misconception_target: Missing the stated behavioral regression boundary: A money total rounds each line incorrectly. The regression uses decimal input strings and an independently calculated expected invoice total.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Start with a minimal input reproducing the user-visible failure and assert the observable contract. Demonstrate that the test fails on the broken implementation and passes with the repair. Avoid asserting private helper calls or duplicating the same calculation as the implementation, because both can preserve the same error.

Engineering case: A money total rounds each line incorrectly. The regression uses decimal input strings and an independently calculated expected invoice total.

Reasoning under a changed assumption: No. Coverage records execution. A useful assertion must distinguish correct from incorrect behavior under the relevant boundary conditions.

## Spoken Summary

Start with a minimal input reproducing the user-visible failure and assert the observable contract. Demonstrate that the test fails on the broken implementation and passes with the repair. Avoid asserting private helper calls or duplicating the same calculation as the implementation, because both can preserve the same error.

## Why

Start with a minimal input reproducing the user-visible failure and assert the observable contract. Demonstrate that the test fails on the broken implementation and passes with the repair. Avoid asserting private helper calls or duplicating the same calculation as the implementation, because both can preserve the same error.

## Production Case

A money total rounds each line incorrectly. The regression uses decimal input strings and an independently calculated expected invoice total.

## Risk

A money total rounds each line incorrectly. The regression uses decimal input strings and an independently calculated expected invoice total.

## Trade-off

No. Coverage records execution. A useful assertion must distinguish correct from incorrect behavior under the relevant boundary conditions.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Behavioral regression**: Start with a minimal input reproducing the user-visible failure and assert the observable contract.

## Alternatives

- No. Coverage records execution. A useful assertion must distinguish correct from incorrect behavior under the relevant boundary conditions.

## Pitfalls

- A money total rounds each line incorrectly. The regression uses decimal input strings and an independently calculated expected invoice total.

## Follow-ups

### Is full line coverage evidence that the regression is useful?

No. Coverage records execution. A useful assertion must distinguish correct from incorrect behavior under the relevant boundary conditions.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A money total rounds each line incorrectly. The regression uses decimal input strings and an independently calculated expected invoice total.",
  "decision": "Start with a minimal input reproducing the user-visible failure and assert the observable contract"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# How should Git and dependency locks support a reproducible learning project?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: How should Git and dependency locks support a reproducible learning project?
difficulty: interview
misconception_target: Missing the stated reproducible source state boundary: A classmate can build the source but gets another model score because the dataset revision and random split were never recorded.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Commit source, configuration and dependency locks, keep credentials and generated caches out, and document a clean-start command. A lockfile identifies resolved dependencies but does not capture the entire operating system, toolchain or external dataset. Record those inputs when they affect the result and inspect the diff before committing.

Engineering case: A classmate can build the source but gets another model score because the dataset revision and random split were never recorded.

Reasoning under a changed assumption: No. Record immutable data/model artifacts and declared external versions or provide a deterministic local fixture. Source identity is only one part of reproducibility.

## Spoken Summary

Commit source, configuration and dependency locks, keep credentials and generated caches out, and document a clean-start command. A lockfile identifies resolved dependencies but does not capture the entire operating system, toolchain or external dataset. Record those inputs when they affect the result and inspect the diff before committing.

## Why

Commit source, configuration and dependency locks, keep credentials and generated caches out, and document a clean-start command. A lockfile identifies resolved dependencies but does not capture the entire operating system, toolchain or external dataset. Record those inputs when they affect the result and inspect the diff before committing.

## Production Case

A classmate can build the source but gets another model score because the dataset revision and random split were never recorded.

## Risk

A classmate can build the source but gets another model score because the dataset revision and random split were never recorded.

## Trade-off

No. Record immutable data/model artifacts and declared external versions or provide a deterministic local fixture. Source identity is only one part of reproducibility.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Reproducible source state**: Commit source, configuration and dependency locks, keep credentials and generated caches out, and document a clean-start command.

## Alternatives

- No. Record immutable data/model artifacts and declared external versions or provide a deterministic local fixture. Source identity is only one part of reproducibility.

## Pitfalls

- A classmate can build the source but gets another model score because the dataset revision and random split were never recorded.

## Follow-ups

### Does checking out a commit reproduce every remote service?

No. Record immutable data/model artifacts and declared external versions or provide a deterministic local fixture. Source identity is only one part of reproducibility.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A classmate can build the source but gets another model score because the dataset revision and random split were never recorded.",
  "decision": "Commit source, configuration and dependency locks, keep credentials and generated caches out, and document a clean-start command"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# When is a Python class useful compared with a function and a dictionary?

<!-- meta
domain: foundations
subdomain: programming-foundations
module: programming-foundations
concept: When is a Python class useful compared with a function and a dictionary?
difficulty: interview
misconception_target: Missing the stated object lifecycle boundary: A connection wrapper owns open/close state and must reject operations after close. A class with an explicit context-manager lifecycle exposes that invariant.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A function is often sufficient for an independent transformation. A class is useful when behavior must preserve an object’s invariants across a lifecycle. A dictionary is flexible but does not by itself prevent invalid state transitions. Choose the smallest representation that makes ownership and invalid states clear; inheritance is not a requirement for extensibility.

Engineering case: A connection wrapper owns open/close state and must reject operations after close. A class with an explicit context-manager lifecycle exposes that invariant.

Reasoning under a changed assumption: No. Plain dictionaries, typed records or dataclasses may fit. Introduce behavior and lifecycle boundaries because they protect a concrete invariant, not because the project might grow.

## Spoken Summary

A function is often sufficient for an independent transformation. A class is useful when behavior must preserve an object’s invariants across a lifecycle. A dictionary is flexible but does not by itself prevent invalid state transitions. Choose the smallest representation that makes ownership and invalid states clear; inheritance is not a requirement for extensibility.

## Why

A function is often sufficient for an independent transformation. A class is useful when behavior must preserve an object’s invariants across a lifecycle. A dictionary is flexible but does not by itself prevent invalid state transitions. Choose the smallest representation that makes ownership and invalid states clear; inheritance is not a requirement for extensibility.

## Production Case

A connection wrapper owns open/close state and must reject operations after close. A class with an explicit context-manager lifecycle exposes that invariant.

## Risk

A connection wrapper owns open/close state and must reject operations after close. A class with an explicit context-manager lifecycle exposes that invariant.

## Trade-off

No. Plain dictionaries, typed records or dataclasses may fit. Introduce behavior and lifecycle boundaries because they protect a concrete invariant, not because the project might grow.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Object lifecycle**: A function is often sufficient for an independent transformation.

## Alternatives

- No. Plain dictionaries, typed records or dataclasses may fit. Introduce behavior and lifecycle boundaries because they protect a concrete invariant, not because the project might grow.

## Pitfalls

- A connection wrapper owns open/close state and must reject operations after close. A class with an explicit context-manager lifecycle exposes that invariant.

## Follow-ups

### Should every data record become a class?

No. Plain dictionaries, typed records or dataclasses may fit. Introduce behavior and lifecycle boundaries because they protect a concrete invariant, not because the project might grow.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A connection wrapper owns open/close state and must reject operations after close. A class with an explicit context-manager lifecycle exposes that invariant.",
  "decision": "A function is often sufficient for an independent transformation"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# How do Unicode normalization, case folding and transliteration affect multilingual identity keys?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: programming-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Preserve the original value first.** Text that looks identical can have different code-point sequences, while text that normalizes similarly can still represent different entities. Keep the original spelling for display and provenance, and build purpose-specific comparison fields rather than overwriting it with an ASCII slug.

**Choose transformations intentionally.** Canonical normalization such as NFC, Normalization Form C, can bring canonically equivalent composed and decomposed sequences into a consistent representation. Compatibility normalization such as NFKC, Normalization Form KC, additionally folds some presentation distinctions. Case folding supports caseless comparison but can expand characters and is not a complete locale-specific identity policy. Transliteration or dropping non-ASCII characters is another lossy transformation, not a substitute for Unicode normalization.

**Use normalized text as evidence.** An Arabic or Chinese name can become empty under ASCII-only filtering; unrelated names may then share the same fallback key. Even a nonempty transliteration can collide. Use a stable record identifier, keep the normalized comparison field separately, and retain the transformation version. Do not assume a changed Unicode database version leaves every derived key unchanged.

**Test invariants and adversarial inputs.** Cover composed/decomposed accents, mixed scripts, combining marks, empty input and scripts outside the Latin alphabet. Verify normalization idempotence under the pinned rule and that source text survives a serialization round trip. The example demonstrates equivalent accent sequences and preserved non-Latin text; it does not claim that canonical equivalence establishes entity identity.

## Why

A profile imported with a composed accented name and another with decomposed accents should compare consistently under a chosen rule. Two different Arabic names must not both become the same empty identity after ASCII filtering.

## Worked Case

A profile imported with a composed accented name and another with decomposed accents should compare consistently under a chosen rule. Two different Arabic names must not both become the same empty identity after ASCII filtering.

## Risk

Lossy conversion can erase identifying information and disproportionately increase matching errors for unsupported languages.

## Trade-off

A permissive search field may improve recall; an identity decision needs stronger evidence and a more conservative transformation policy.

## Try This

Create equivalent Unicode spellings and distinct non-Latin names. Check raw preservation, comparison behavior and empty-key rejection.

## Follow-ups

### Should search and primary-key normalization use the same policy?

Usually separate them. Search can maintain multiple lossy matching views while primary identity remains stable and collision-aware. Record how each derived field was produced.

### Does case folding solve mixed-script spoofing?

No. Caseless comparison and visually confusable characters are different problems. Apply a context-appropriate display and identifier policy without assuming all mixed-script text is malicious.

## Citations

- https://docs.python.org/3/library/unicodedata.html

# Why can a dataclass dictionary fail JSON serialization, and how do you reconstruct nested types safely?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: programming-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A dictionary is not automatically a wire contract.** Dataclass conversion recursively creates ordinary containers, but values such as enumeration members, dates and bytes may still require explicit encoding. Even if encoding succeeds, the decoder receives JSON types rather than your original domain objects. A string named approved is not necessarily an instance of the application's status enumeration.

**Define a schema-specific codec.** Encode each field using a documented representation: enumeration values as approved strings, timestamps with explicit timezone semantics, bytes using an agreed encoding and nested objects using their declared schemas. Avoid a catch-all string conversion that turns unsupported objects into plausible but irreversible text. Reject nonfinite numeric values when the wire contract requires strict JSON.

**Validate decoding before construction.** Check the schema version, required fields, allowed enumeration values and nested shapes. Decide how unknown fields are handled to support compatibility without silently accepting misspellings in safety-relevant input. Do not assume type annotations perform runtime validation. Convert primitive wire values into domain types deliberately and enforce cross-field invariants afterward.

**Specify the round-trip property.** For supported domain values, decoding an encoded value should recover equivalent meaning. Exact byte equality may be unnecessary because key order or whitespace can change. Include negative fixtures for unknown enums, missing fields and unsupported types. The example shows a normal dataclass dictionary failing direct serialization, followed by an explicit codec that restores an actual enum member.

## Why

A record has an enum-valued status. Converting its dataclass to a dictionary leaves the enum object inside. A generic JSON encoder rejects it; converting everything to strings would instead hide the missing wire-format design.

## Worked Case

A record has an enum-valued status. Converting its dataclass to a dictionary leaves the enum object inside. A generic JSON encoder rejects it; converting everything to strings would instead hide the missing wire-format design.

## Risk

Loose conversion can make a serialized record look valid while losing type meaning or silently accepting unsupported states.

## Trade-off

Explicit codecs require maintenance but make compatibility and validation visible to reviewers.

## Try This

Round-trip a nested record with enum values, then reject an unknown status and an unsupported schema version.

## Follow-ups

### Does using StrEnum remove the need for a codec?

It may simplify encoding, but decoding still needs schema and allowed-value validation. A string-compatible enum does not validate every incoming primitive automatically.

### Should unknown enum values be mapped to a default?

Only if the contract explicitly defines that behavior and preserves uncertainty. Silently mapping an unknown state to an actionable default can change business meaning.

## Citations

- https://docs.python.org/3/library/dataclasses.html
- https://docs.python.org/3/library/enum.html
- https://docs.python.org/3/library/json.html

# Why does a frozen dataclass not guarantee deeply immutable or validated domain state?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: programming-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Frozen controls attribute assignment, not every object reachable through an attribute.** A frozen record can still contain a mutable list or dictionary. Code holding that nested object can change its contents, altering the record's apparent value without assigning a new top-level field. Slots reduce some object-layout flexibility; they do not add deep immutability or business validation.

**Choose immutable ownership boundaries.** Convert caller-owned mutable collections into tuples or other deliberately immutable representations when constructing a value object. Validate each nested value, not only the outer container. If elements contain mutable objects, a tuple alone does not freeze those elements. Decide whether the model is a true value object or an entity with controlled state transitions.

**Enforce invariants at construction and update boundaries.** Dataclass type annotations generally do not validate runtime values. Reject empty required values, unsupported types and contradictory fields explicitly or through a schema validator. A default factory that constructs an invalid nested object makes ordinary construction fail unexpectedly; prefer required constructor arguments when no truthful default exists.

**Test aliasing and reconstruction.** Mutate the caller's original list after construction and verify a value object does not change. Attempt unsupported nested types, invalid defaults and round-trip decoding. Use controlled replacement to create a new valid instance rather than bypassing validation with internal attribute assignment. The example contrasts shallow frozen ownership with an explicitly copied immutable boundary and checks that later caller mutation cannot change the latter.

## Why

A frozen record stores a caller's list of tags. Another function appends a tag to that same list, changing the record despite its frozen declaration. Copying to a tuple at construction prevents this particular aliasing path.

## Worked Case

A frozen record stores a caller's list of tags. Another function appends a tag to that same list, changing the record despite its frozen declaration. Copying to a tuple at construction prevents this particular aliasing path.

## Risk

Assuming frozen means deeply immutable can break caching, hashing assumptions, concurrent reasoning and audit snapshots.

## Trade-off

Immutable values simplify reasoning but require new instances for updates and deliberate treatment of large nested structures.

## Try This

Construct a record from a mutable list, mutate the original and test the result. Repeat with nested mutable elements and explain the remaining ownership boundary.

## Follow-ups

### Can every frozen dataclass be used safely as a dictionary key?

No. Hashing depends on the field values and generated hash policy. Mutable or unhashable nested values can make hashing invalid or impossible; choose stable immutable value semantics deliberately.

### Is object.__setattr__ a safe general update API?

No. It can bypass frozen enforcement. In this example it is confined to initialization to establish the invariant; ordinary updates should create a new validated value.

## Citations

- https://docs.python.org/3/library/dataclasses.html

# What happens when Python executes an assignment and evaluates an expression?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Python evaluates the right-hand expression first, then binds the target name to the resulting object. Assignment does not declare a permanent type or copy the object. Operators dispatch according to operand types, so addition may add numbers or concatenate strings. Evaluation order and precedence affect the result; parentheses make intent explicit. A name must be bound before it is read in the relevant scope. Start debugging by writing down the value and type of every intermediate expression, rather than guessing from the variable name.

## Why

For price='12' and count=3, price*count produces '121212'. Convert and validate the representation before performing a monetary calculation; repeating a string is valid Python but incorrect business behavior.

## Worked Case

For price='12' and count=3, price*count produces '121212'. Convert and validate the representation before performing a monetary calculation; repeating a string is valid Python but incorrect business behavior.

## Risk

A valid language operation can still implement the wrong requirement.

## Trade-off

Prefer explicit parsing at boundaries over scattered implicit assumptions.

## Try This

Predict the values and types of '3'*2, 3*2 and int('3')*2, then run them.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do integers, floating-point numbers and Decimal differ?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Integers represent whole numbers exactly within available memory. Binary floating point approximates many decimal fractions, so 0.1+0.2 need not equal the literal 0.3. Decimal supports decimal arithmetic with an explicit context and rounding policy; constructing it from a string preserves the intended decimal input. A numerical type alone does not define units, currency, allowed range or when rounding occurs. Use approximate comparisons for measured floating-point quantities and exact domain rules for amounts that must reconcile.

## Why

Two invoice lines of Decimal('0.10') and Decimal('0.20') add to Decimal('0.30'). Constructing Decimal from the float 0.1 instead imports its binary approximation.

## Worked Case

Two invoice lines of Decimal('0.10') and Decimal('0.20') add to Decimal('0.30'). Constructing Decimal from the float 0.1 instead imports its binary approximation.

## Risk

Rounding each line and rounding a total can produce different totals.

## Trade-off

Floating point suits many scientific calculations; decimal arithmetic suits specified decimal accounting rules.

## Try This

Compare both representations and specify whether tax rounds per line or per invoice.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do truthiness, comparisons and short-circuit evaluation work?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Truthiness is a language rule, not a complete domain model.** Empty containers, numeric zero and `None` are false; many other objects are true. A valid zero can still have a different meaning from missing input.

- Use `value is None` when checking the absence sentinel.
- Use `value == 0` when checking numeric equality with zero.
- Use a domain-specific condition when an empty string or collection is invalid.

The `and` and `or` operators **short-circuit and return an operand**, not necessarily a boolean. An expression such as `supplied or 3` chooses 3 for both missing input and a supplied zero. That loses the distinction if zero means “never retry.”

Prefer `3 if supplied is None else supplied` when only absence should select the default. Validate a negative limit separately. Explicit parsing preserves three outcomes: an absent optional value, a valid zero, and an invalid representation.

## Why

A retry limit of zero may mean 'never retry'. Writing limit = supplied or 3 silently replaces that valid policy. Use an explicit None check for a missing value.

## Worked Case

A retry limit of zero may mean 'never retry'. Writing limit = supplied or 3 silently replaces that valid policy. Use an explicit None check for a missing value.

## Risk

Truthiness can collapse distinct business states into the same branch.

## Trade-off

Concise boolean expressions help only when the operand contract is unambiguous.

## Try This

Write a parser that treats None, 0 and an invalid negative retry limit differently.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do if, for, while, break and continue control program execution?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An if statement chooses a branch from a condition. A for loop requests items from an iterable until exhaustion, while a while loop repeats while a condition remains true. Continue skips to the next iteration; break exits the innermost loop. State the loop invariant and termination condition before introducing retries or nested loops. A loop's else suite runs when it finishes without break, which can express an exhausted search. Code after a loop should not assume the loop ran at least once.

## Why

Searching an empty list for an approved record must return an explicit missing result. A local variable assigned only inside the loop will otherwise be unbound when the list is empty.

## Worked Case

Searching an empty list for an approved record must return an explicit missing result. A local variable assigned only inside the loop will otherwise be unbound when the list is empty.

## Risk

A missing state update can make a while loop run forever.

## Trade-off

Prefer direct iteration for finite collections; use while for a genuine evolving condition.

## Try This

Implement a bounded search and test empty input, first-item match and no match.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# When should you use a list, tuple, set or dictionary?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Choose a collection from its **ownership and access contract**, rather than from which syntax looks shortest.

| Collection | What it preserves | Useful operations | Important boundary |
| --- | --- | --- | --- |
| `list` | Order and duplicate occurrences | Indexed access, append, traversal | Mutable; a front insertion can move many references |
| `tuple` | A fixed sequence of references | Positional records, unpacking | A nested list can still mutate; not every tuple is hashable |
| `set` | Distinct hashable values | Membership and set operations | Removes duplicate occurrences and does not define a business order |
| `dict` | Key-to-value association and insertion order | Key lookup and keyed updates | Keys need stable hashing/equality; insertion order is not a priority rule |

**Model the meaning before choosing the container.** Two identical purchases may need to remain two separate events in a list. Repeated permission names may intentionally collapse into a set. Entity records often belong in a dictionary keyed by a stable identifier.

Do not replace an event log with a set merely to remove apparent duplication. Repeated deliveries and genuinely repeated business events need an explicit identity policy, not a container conversion that silently discards history.

## Why

A shopping list may contain two identical purchases that must both be counted. A set of those purchases would hide the duplicate, whereas a set of permitted category names intentionally removes repetition.

## Worked Case

A shopping list may contain two identical purchases that must both be counted. A set of those purchases would hide the duplicate, whereas a set of permitted category names intentionally removes repetition.

## Risk

Hashability and uniqueness do not imply immutability of an entire object graph.

## Trade-off

Use a mapping for key lookup and a sequence when position or repetition carries meaning.

## Try This

Model an ordered event log, a permission set and an entity lookup with appropriate collections.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do slicing, comprehensions and unpacking affect readability and memory?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A slice selects part of a sequence; a list slice creates a new outer list but retains references to its elements. A comprehension expresses a transformation with optional filtering, usually more clearly than mutation hidden in a loop. Starred unpacking collects remaining elements into a list and needs sufficient memory. None of these constructs guarantees deep copies or bounded memory. Use a simple loop when error handling, multiple state changes or resource ownership would make a comprehension difficult to understand.

## Why

Copying records with records[:] protects the outer list from append operations, but changing copied[0]['status'] still changes the shared first dictionary.

## Worked Case

Copying records with records[:] protects the outer list from append operations, but changing copied[0]['status'] still changes the shared first dictionary.

## Risk

A shallow copy can preserve the alias responsible for a defect.

## Trade-off

Favor a comprehension for a clear pure transformation and explicit iteration for complex control flow.

## Try This

Demonstrate a shallow-copy mutation and decide which nested values actually need independent ownership.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do strings, bytes and Unicode differ when reading external data?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A Python string contains Unicode text; bytes contain numeric byte values. Decoding converts bytes using a character encoding, and encoding performs the reverse conversion. The same visible text may have different Unicode representations, and character count is not encoded byte count. Choose an explicit encoding at an external boundary and define what happens on invalid data. Silently ignoring decoding errors can alter identifiers or evidence. Unicode normalization is a domain decision, especially for user names and security-sensitive comparisons.

## Why

The accented character é occupies more than one byte in UTF-8. A network read may split its encoded bytes, so decoding each chunk independently can fail even though the complete stream is valid.

## Worked Case

The accented character é occupies more than one byte in UTF-8. A network read may split its encoded bytes, so decoding each chunk independently can fail even though the complete stream is valid.

## Risk

Text length, byte length and model-token length are different measurements.

## Trade-off

Strict decoding surfaces corruption; replacement decoding may be acceptable for a visibly marked preview.

## Try This

Encode a multilingual string, split inside a character and recover it with an incremental decoder.

## Citations

- https://docs.python.org/3/tutorial/inputoutput.html

# How should functions define inputs, defaults and return contracts?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A function should make accepted inputs, observable effects and return behavior clear. Positional-only and keyword-only parameters can protect an interface from accidental misuse. Default expressions are evaluated when the function is defined, so mutable defaults can persist across calls. Returning None should have a documented meaning rather than stand in for every failure. Small functions with explicit dependencies are easier to test than functions reading and mutating hidden globals. Type annotations communicate the intended contract but do not enforce external data validity.

## Why

A parser may return a validated record, return None for a deliberately absent optional record, or raise ValueError for malformed content. Combining these outcomes into an empty dictionary loses useful information.

## Worked Case

A parser may return a validated record, return None for a deliberately absent optional record, or raise ValueError for malformed content. Combining these outcomes into an empty dictionary loses useful information.

## Risk

Hidden global state makes two otherwise identical calls behave differently.

## Trade-off

Use explicit parameters where changing dependencies or reproducing behavior matters.

## Try This

Define a parse_count function that distinguishes absence, invalid syntax and a valid zero.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# What do local, enclosing, global and built-in scopes mean?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Python resolves ordinary names through local, enclosing function, module-global and built-in scopes. Assigning to a name inside a function generally makes it local unless declared global or nonlocal. A closure retains access to an enclosing binding, not necessarily a frozen copy of its earlier value. This matters when callbacks are created in loops: they may all read the final value later. Prefer passing values explicitly or deliberately binding a default when a snapshot is required. Avoid naming variables after built-ins such as list or sum.

## Why

Three callbacks capturing a loop variable may all report the last item. Binding item=item in each callback's parameters captures that current reference, although a referenced mutable object can still change.

## Worked Case

Three callbacks capturing a loop variable may all report the last item. Binding item=item in each callback's parameters captures that current reference, although a referenced mutable object can still change.

## Risk

A closure can outlive the request state it was expected to represent.

## Trade-off

Closures are useful for small factories; explicit objects clarify longer-lived state.

## Try This

Create three callbacks and verify that each reports the intended distinct value.

## Citations

- https://docs.python.org/3/tutorial/classes.html

# How do exceptions, else and finally support reliable cleanup?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Raise an exception when ordinary return values cannot represent a failure clearly. Catch the narrow exception types the caller can meaningfully handle, and preserve the original cause when translating errors. A try statement's else suite runs only if its protected block succeeds; finally runs while leaving the protected operation, including on many exceptional paths. Cleanup must not accidentally replace the original failure with a second exception. Use context managers for resource acquisition and release when possible, and do not convert every error into a successful empty response.

## Why

If parsing succeeds but writing fails, report the write failure rather than returning an empty success. Keep parsing and persistence in separate narrow blocks so their different errors remain diagnosable.

## Worked Case

If parsing succeeds but writing fails, report the write failure rather than returning an empty success. Keep parsing and persistence in separate narrow blocks so their different errors remain diagnosable.

## Risk

A return inside finally can suppress an exception and hide a failed operation.

## Trade-off

Translate errors at a boundary while retaining causes needed for diagnosis.

## Try This

Write a file-processing function whose handle closes after both successful and failed parsing.

## Citations

- https://docs.python.org/3/tutorial/errors.html

# How do modules, packages and the main guard structure a Python project?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A module is an importable unit of Python code. Packages group modules under a namespace, and imports execute module-level code as a module is initialized. Keep network calls, destructive writes and long-running jobs out of import-time execution. The if __name__ == '__main__' guard makes script entry behavior explicit while allowing functions to be imported for testing. Separate reusable domain logic from command-line parsing and process setup. Import cycles often indicate that responsibilities or dependency directions need reconsideration.

## Why

A test importing a pricing function should not start a web server or connect to a production database. Put that startup behavior in a main function and invoke it only through the intended entry point.

## Worked Case

A test importing a pricing function should not start a web server or connect to a production database. Put that startup behavior in a main function and invoke it only through the intended entry point.

## Risk

Import side effects can make tests order-dependent and deployment startup unpredictable.

## Trade-off

Small cohesive modules improve reuse without introducing a layer for every function.

## Try This

Refactor a script so its transformation can be imported without reading files.

## Citations

- https://docs.python.org/3/tutorial/modules.html

# What does a class add beyond a dictionary and a collection of functions?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A class groups state with operations and can enforce invariants through its construction and methods. Instance attributes belong to an instance; mutable class attributes are shared unless deliberately shadowed. Methods receive the instance explicitly as self. A dictionary is often enough for a simple transport record, while a class can express behavior and ownership more clearly. Encapsulation in Python relies on conventions and interface discipline rather than making every internal attribute inaccessible. Avoid classes whose only purpose is wrapping a single stateless function.

## Why

If every cart instance appends to a class-level items list, customers share one list. Initialize self.items inside the constructor when each cart needs independent ownership.

## Worked Case

If every cart instance appends to a class-level items list, customers share one list. Initialize self.items inside the constructor when each cart needs independent ownership.

## Risk

Object-oriented syntax does not automatically provide validation or thread safety.

## Trade-off

Use classes for meaningful state and behavior; keep simple transformations as functions.

## Try This

Implement two independent carts and test that adding an item to one leaves the other unchanged.

## Citations

- https://docs.python.org/3/tutorial/classes.html

# When is composition better than inheritance, and what is duck typing?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Composition supplies a collaborating object, such as a clock or storage adapter, instead of inheriting its implementation. Duck typing means using the operations an object supports rather than requiring a particular inheritance tree. An interface should describe meaningful behavior, including errors and effects, rather than only matching method names. Inheritance is appropriate when substitutability truly holds; a subclass that rejects operations promised by its base type breaks callers' assumptions. Test the same behavioral contract against alternative collaborators.

## Why

A report service can accept either local-file or in-memory storage through a small write contract. Neither storage class needs to inherit the report service or gain access to its internal state.

## Worked Case

A report service can accept either local-file or in-memory storage through a small write contract. Neither storage class needs to inherit the report service or gain access to its internal state.

## Risk

Matching a method signature does not prove matching durability or authorization behavior.

## Trade-off

Composition makes dependencies replaceable; inheritance can reuse a stable, valid behavioral hierarchy.

## Try This

Substitute an in-memory adapter and verify the same public success and failure outcomes.

## Citations

- https://docs.python.org/3/tutorial/classes.html

# What do dataclasses provide, and what do they leave to the application?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A dataclass generates common methods such as initialization, representation and equality from annotated fields. It reduces repetition for value-like records but does not automatically validate ranges, external JSON or authorization. A frozen dataclass prevents normal assignment to its fields, not mutation of every nested object. Equality and hashing need deliberate treatment when records become dictionary keys. Use default_factory for per-instance mutable collections. Keep domain validation at construction or an explicit boundary rather than assuming annotations enforce it.

## Why

A frozen request record containing a list can still expose mutable list contents. Store immutable tuples when stable nested values matter, and reject invalid counts before accepting the record.

## Worked Case

A frozen request record containing a list can still expose mutable list contents. Store immutable tuples when stable nested values matter, and reject invalid counts before accepting the record.

## Risk

A generated repr can disclose sensitive fields in logs.

## Trade-off

Dataclasses suit internal records; boundary-validation tools handle untrusted representations.

## Try This

Build a record with a per-instance collection and prove two instances do not share it.

## Citations

- https://docs.python.org/3/tutorial/classes.html

# How do decorators work, and why can their ordering change behavior?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A decorator receives a function or callable and returns the callable bound to its name. Multiple decorators are applied from the closest one outward, so order changes which behavior surrounds which operation. A wrapper may alter timing, exceptions, identity, retries or authorization. Preserve useful metadata with functools.wraps and keep arguments and return contracts compatible. Retrying a function that performs an external effect requires more than a convenient wrapper: it needs an explicit operation identity and recovery policy.

## Why

With caching outside authorization, a cached result might return without executing an inner permission check. Authorize the current caller before returning scoped cached data, regardless of how decorators are arranged.

## Worked Case

With caching outside authorization, a cached result might return without executing an inner permission check. Authorize the current caller before returning scoped cached data, regardless of how decorators are arranged.

## Risk

A decorator can silently broaden an effect boundary or bypass validation.

## Trade-off

Decorators help with stable cross-cutting behavior; explicit calls can make sensitive control flow clearer.

## Try This

Draw the call order of two wrappers and test it with a recorded sequence of events.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# What is the difference between an iterable, iterator and generator?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An iterable can supply an iterator. An iterator supplies successive items and eventually raises StopIteration; it usually cannot be restarted from the beginning. A generator is one way to implement an iterator using suspended execution and yield. Creating a generator does not execute its entire body, so exceptions and resource acquisition can be delayed until consumption. Use a new iterator when replay is required, and distinguish a replayable source from a consumed stream in a function contract.

## Why

Calling list on a generator consumes it. A second call may return an empty list, which is not evidence that the original source contained no records.

## Worked Case

Calling list on a generator consumes it. A second call may return an empty list, which is not evidence that the original source contained no records.

## Risk

A second consumer can see no items or steal items expected by another consumer.

## Trade-off

Lazy iteration bounds storage but complicates replay and lifetime reasoning.

## Try This

Consume the same generator twice, then replace it with a factory producing fresh iterators.

## Citations

- https://docs.python.org/3/tutorial/classes.html

# How do you read and write files safely with explicit encodings?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Open text files with an explicit encoding and a context manager so the handle closes predictably. Text mode decodes characters and handles text conventions, while binary mode preserves bytes. Writing a file directly can leave a partial artifact if the process fails. For a local replaceable snapshot, write a temporary file, flush according to the durability requirement and replace it using filesystem-supported atomic replacement. Atomic visibility and survival after power loss are different guarantees, and behavior depends on the filesystem.

## Why

A reader must not load half of a newly written configuration. Publishing a completed temporary file through replacement avoids exposing the partially written path, while permission and durability checks still remain necessary.

## Worked Case

A reader must not load half of a newly written configuration. Publishing a completed temporary file through replacement avoids exposing the partially written path, while permission and durability checks still remain necessary.

## Risk

A successful close does not establish an entire distributed backup guarantee.

## Trade-off

Streaming reads use less memory; whole-file reads simplify small, bounded inputs.

## Try This

Save a Unicode configuration and simulate a failure before the final replace step.

## Citations

- https://docs.python.org/3/tutorial/inputoutput.html

# How should JSON parsing, validation and serialization be separated?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Parsing checks whether text conforms to JSON syntax and produces language values. Validation checks allowed fields, types, ranges and relationships. Authorization decides whether the authenticated caller may act on those valid values. Serialization converts accepted values back to a transport representation and can accidentally expose internal fields if not constrained. Define how missing values differ from explicit null, reject ambiguous coercions where they change meaning, and impose payload-size limits before retaining an unbounded input.

## Why

The valid JSON object {"amount":"twelve"} is still invalid for an operation requiring a decimal amount. A valid owner identifier also does not establish permission to act for that owner.

## Worked Case

The valid JSON object {"amount":"twelve"} is still invalid for an operation requiring a decimal amount. A valid owner identifier also does not establish permission to act for that owner.

## Risk

Successful parsing is frequently mistaken for a trusted or authorized request.

## Trade-off

Explicit boundary schemas cost authoring effort but localize invalid-data handling.

## Try This

Test malformed syntax, wrong type, missing field, explicit null and a forbidden owner.

## Citations

- https://docs.python.org/3/tutorial/inputoutput.html

# Why should paths and environment configuration be treated as external inputs?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A filesystem path can be absolute, relative or contain parent traversal. A server must resolve an allowed resource within its intended root rather than trusting string concatenation. Environment variables are strings supplied by deployment context; parse and validate them before use. Distinguish a required secret from an optional setting, and fail clearly when startup configuration is invalid. Do not log secret values or commit them into example configuration. Resolve configuration once where appropriate instead of allowing unrelated modules to interpret it differently.

## Why

A download request for ../../private.key must not escape a public directory. Resolve the final path and verify containment under the allowed root, considering symlink policy as part of the design.

## Worked Case

A download request for ../../private.key must not escape a public directory. Resolve the final path and verify containment under the allowed root, considering symlink policy as part of the design.

## Risk

Prefix string checks can accept sibling paths that are outside the intended directory.

## Trade-off

Explicit configuration objects make tests reproducible and deployment errors easier to diagnose.

## Try This

Validate a port, a required credential presence and a path containing parent segments.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do virtual environments, dependency constraints and lockfiles improve reproducibility?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A virtual environment isolates installed Python packages from other projects, but it does not pin their versions by itself. Dependency constraints define acceptable versions; a lock records a particular resolution for a given tooling and platform contract. Reproducing execution also requires a compatible Python version, operating-system libraries and documented commands. Keep local environment directories out of version control. Update dependencies deliberately and run the behavior checks that exercise affected integrations, rather than assuming a successful install proves compatibility.

## Why

A project may install a newer transitive package on a clean machine even though the author's existing environment still works. A resolved dependency record and clean install reveal that hidden dependency difference.

## Worked Case

A project may install a newer transitive package on a clean machine even though the author's existing environment still works. A resolved dependency record and clean install reveal that hidden dependency difference.

## Risk

A lock for one platform may not establish availability of native wheels on another.

## Trade-off

Tight pins aid reproduction; scheduled updates prevent pins from becoming permanent neglect.

## Try This

Create a clean environment from the recorded inputs and run the smallest useful smoke check.

## Citations

- https://docs.python.org/3/tutorial/venv.html

# How do unit, integration and end-to-end tests answer different questions?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A unit test isolates a small behavior such as a deterministic transformation. An integration test checks a real collaboration, for example an application transaction against its database. An end-to-end test exercises a user-visible path through several components. These categories describe scope, not inherent quality. Choose the least expensive test that can catch the relevant failure and use realistic boundaries where mocks would hide the contract. Assertions should concern observable results and important effects, not incidental internal function calls.

## Why

A mocked database returning a row cannot reveal a uniqueness constraint race. A real database concurrency check is needed for that invariant, while a pure amount parser can be tested without a browser.

## Worked Case

A mocked database returning a row cannot reveal a uniqueness constraint race. A real database concurrency check is needed for that invariant, while a pure amount parser can be tested without a browser.

## Risk

A large passing test count can miss the actual failure boundary.

## Trade-off

Broad tests provide confidence across components at greater setup and feedback cost.

## Try This

Match a parser defect, a transaction race and a broken submit button to suitable test scopes.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do you debug an exception using a minimal reproduction and traceback?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A traceback identifies the active call chain and failing operation, not necessarily the original source of bad state. Read the exception type and message, inspect the relevant inputs, and reduce the case until it retains the defect with minimal unrelated setup. Form a falsifiable hypothesis, change one assumption and observe the result. Preserve a regression case once repaired. Avoid suppressing an exception merely to make a test green, and avoid logging sensitive payloads when inspecting state.

## Why

A KeyError during formatting may originate from an earlier parser that accepted a record without a required field. Validate the boundary rather than adding a blanket exception around the entire response.

## Worked Case

A KeyError during formatting may originate from an earlier parser that accepted a record without a required field. Validate the boundary rather than adding a blanket exception around the entire response.

## Risk

Fixing only the final symptom can preserve corrupt state upstream.

## Trade-off

A minimal reproduction speeds reasoning; retain a representative integration case when context matters.

## Try This

Reduce a failing nested-record transformation to its smallest invalid input and write the expected outcome.

## Citations

- https://docs.python.org/3/tutorial/errors.html

# When should you measure with a profiler instead of changing the algorithm immediately?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Begin with an observed performance target, representative input and a reproducible measurement. A profiler attributes execution cost to call paths; elapsed time also includes waits, setup and contention. Separate cold-start work from steady-state requests, and compare repeated measurements before trusting a small difference. Once the bottleneck is identified, choose between an algorithmic change, reduced repeated work or better I/O behavior. Preserve correctness and memory measurements while optimizing. A microbenchmark of one operation does not establish complete service capacity.

## Why

A slow endpoint may spend most time waiting for an external service. Replacing a small local loop with a clever expression barely affects its end-to-end latency.

## Worked Case

A slow endpoint may spend most time waiting for an external service. Replacing a small local loop with a clever expression barely affects its end-to-end latency.

## Risk

Benchmark noise can be larger than the claimed improvement.

## Trade-off

Algorithm changes can improve scaling; instrumentation identifies whether they address the real bottleneck.

## Try This

Measure a CPU-heavy transform and a simulated I/O wait separately and explain their different remedies.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How does logging differ from printing and raising an exception?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Logging records an observation for later diagnosis; raising an exception changes control flow; printing emits text without a structured operational policy. Use appropriate severity, stable event names and contextual identifiers. Record enough to connect an event to a request while avoiding credentials, raw private documents and unnecessarily identifying data. Expensive formatting and large payloads can affect the program being observed. An error log is not a substitute for returning a correct failure contract or recording an authoritative business outcome.

## Why

A failed payment needs an appropriate API outcome and durable operation state. A log line saying 'payment failed' cannot decide whether a provider already accepted the charge.

## Worked Case

A failed payment needs an appropriate API outcome and durable operation state. A log line saying 'payment failed' cannot decide whether a provider already accepted the charge.

## Risk

Sensitive data copied into logs can outlive deletion from primary storage.

## Trade-off

Structured logs support filtering; avoid high-volume detail that obscures actionable events.

## Try This

Replace an unstructured print with a safe event containing operation identity and failure category.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do Git commits, branches and code review support reliable collaboration?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A commit records a coherent snapshot and its ancestry. A branch is a movable reference, not a private copy of shared external services. Keep unrelated changes separate enough for review and rollback, inspect the diff before committing, and document why behavior changed. Resolve merge conflicts by preserving intended contracts rather than merely removing conflict markers. A review should assess correctness, maintenance cost, compatibility and verification evidence. Secrets, caches and machine-specific paths do not belong in a public commit.

## Why

Two branches can both add a migration number or change the same API field in incompatible ways even when Git reports no textual conflict. Review the resulting behavior after integration.

## Worked Case

Two branches can both add a migration number or change the same API field in incompatible ways even when Git reports no textual conflict. Review the resulting behavior after integration.

## Risk

A clean merge is not proof of a compatible design.

## Trade-off

Small coherent changes reduce review burden while keeping dependent changes understandable.

## Try This

Review a diff and identify its behavior change, test evidence and rollback boundary.

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# What is an async function, and why must its coroutine be awaited or scheduled?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Calling an async function creates a coroutine object; its body runs when the event loop drives it through awaiting or scheduling. Await suspends the current task while its awaited operation can make progress. It does not turn every operation into nonblocking work: synchronous file access or expensive Python computation can still block the loop. Keep task ownership explicit so exceptions, cancellation and completion are observed. Use structured task lifetimes rather than starting work and losing its handle.

## Why

Creating send_report() without awaiting it may produce no report at all. Scheduling it without retaining ownership may hide a failure until shutdown or leave work running after the request ends.

## Worked Case

Creating send_report() without awaiting it may produce no report at all. Scheduling it without retaining ownership may hide a failure until shutdown or leave work running after the request ends.

## Risk

Unobserved tasks can leak resources and lose errors.

## Trade-off

Async fits concurrent waiting; separate processes or suitable native work address CPU parallelism.

## Try This

Compare an unawaited coroutine with an awaited call and a deliberately owned concurrent task.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do shallow copies, deep copies and immutable values change ownership?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A shallow copy creates a new outer container while sharing nested references. A deep copy recursively copies supported objects, but it is not a universal way to duplicate external resources, locks or database identities. Immutable values simplify ownership when the entire referenced structure is stable, not merely its outer wrapper. Choose the smallest copying boundary that preserves the intended invariant. Avoid deep-copying huge data merely to conceal uncertainty about which component owns it. Document whether a function may mutate its input.

## Why

Copying a list of dictionaries still shares the dictionaries. For an independent status update, create a new record for the changed item or deliberately copy the mutable nested structure that must diverge.

## Worked Case

Copying a list of dictionaries still shares the dictionaries. For an independent status update, create a new record for the changed item or deliberately copy the mutable nested structure that must diverge.

## Risk

Deep copying can be costly and still fail to reproduce resource semantics.

## Trade-off

Immutable records reduce accidental mutation; in-place updates can save memory under explicit exclusive ownership.

## Try This

Build a nested structure and demonstrate exactly which references differ after each copying strategy.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# Why do equality, hashing and ordering need consistent contracts?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Equality defines when two values compare the same. Hash-based containers require equal keys to have equal hashes, and a key's effective hash/equality behavior must remain stable while stored. Ordering is a separate contract: two values can be comparable for equality without having a meaningful less-than relation. Custom objects used as keys need careful field selection, especially when fields can mutate. Do not use an object's in-process hash as a durable cross-process content digest.

## Why

If a dictionary key's identity fields mutate after insertion, later lookups may not find it reliably. Use a stable immutable key and keep changing workflow attributes in the associated value.

## Worked Case

If a dictionary key's identity fields mutate after insertion, later lookups may not find it reliably. Use a stable immutable key and keep changing workflow attributes in the associated value.

## Risk

Hash collisions are possible; hash equality is not proof of content equality.

## Trade-off

Stable keys simplify lookups; full content digests serve different persistence and verification purposes.

## Try This

Design an immutable composite key and explain why a runtime hash is unsuitable for persisted integrity checks.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# What should a command-line program communicate through arguments, output and exit status?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A command-line interface separates configuration inputs, machine-readable results, human diagnostics and success or failure status. Parse arguments before performing effects and validate mutually dependent options together. Put diagnostics on standard error when standard output is part of a data pipeline. Return a nonzero exit status for a failed required operation, even if a friendly message was printed. Bound stdin and file input where it may be untrusted, and make destructive defaults explicit.

## Why

A JSON-producing command that prints a progress banner to standard output breaks its downstream parser. Send progress to standard error and reserve standard output for the promised representation.

## Worked Case

A JSON-producing command that prints a progress banner to standard output breaks its downstream parser. Send progress to standard error and reserve standard output for the promised representation.

## Risk

A zero exit code after partial failure can make CI publish invalid artifacts.

## Trade-off

Machine-readable output supports composition; human diagnostics should not corrupt that contract.

## Try This

Write a small command with an invalid-input exit status and independently parse its successful output.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How do you handle dates, time zones and durations without mixing meanings?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A date identifies a calendar day; a timestamp identifies an instant under a defined time-zone interpretation; a duration measures elapsed time. Use timezone-aware values for external instants and normalize storage deliberately. Local times can be ambiguous or nonexistent during daylight-saving transitions. Use a monotonic clock for local elapsed-time deadlines, since wall clocks can jump. A business rule based on an event's local date may need its original zone even when the underlying instant is stored in UTC.

## Why

A request before midnight UTC may already belong to the next calendar day in Cairo. Comparing only UTC dates can apply the wrong daily cutoff if the policy is explicitly local.

## Worked Case

A request before midnight UTC may already belong to the next calendar day in Cairo. Comparing only UTC dates can apply the wrong daily cutoff if the policy is explicitly local.

## Risk

Mixing naive and aware timestamps can produce errors or silent policy mistakes.

## Trade-off

UTC simplifies instant comparison; preserve business-zone context for calendar rules.

## Try This

Test a local cutoff, a timezone conversion and an elapsed timeout after a simulated wall-clock change.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html

# How should a small program grow without premature abstraction?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: programming-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Start with a clear input/output contract and a few cohesive functions. Separate external I/O from deterministic transformations so behavior can be tested and reused. Introduce an abstraction when it captures a real invariant or a second concrete implementation, rather than anticipating every possible future provider. Keep dependency direction understandable and delete obsolete paths when a design changes. Good structure reduces the number of places a rule can disagree; adding more classes does not guarantee that result.

## Why

A single validation rule copied into a CLI and HTTP handler can drift. Put that rule in one domain function while allowing each interface to translate its own inputs and errors.

## Worked Case

A single validation rule copied into a CLI and HTTP handler can drift. Put that rule in one domain function while allowing each interface to translate its own inputs and errors.

## Risk

Overgeneralized helpers can hide important differences behind a misleading common interface.

## Trade-off

Share stable domain behavior and keep genuinely different boundary policies explicit.

## Try This

Refactor two duplicated validation paths into one tested rule without coupling their transport code.

## Citations

- https://docs.python.org/3/tutorial/controlflow.html
