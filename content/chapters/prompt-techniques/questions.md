<!-- chapter: prompt-techniques -->

# When should a task be decomposed into smaller prompts?

## Answer

Decompose when subtasks have different evidence, validation rules, or failure recovery. Extraction followed by validation and drafting is often easier to inspect than a single opaque request.

## Why

Pass typed intermediate results, not unbounded prose. Validate each boundary before invoking the next stage.

## Risk

Errors in an early stage can become authoritative inputs to later stages.

## Trade-off

Decomposition improves diagnosis and adds latency and orchestration cost.

## Try This

Split a support response into intent extraction, authorized evidence lookup, and answer generation.

# What is chain-of-thought prompting useful for, and what should users see?

## Answer

Some reasoning tasks benefit from structured intermediate work, but private internal reasoning is not a reliable audit record. Ask for concise conclusions, checkable calculations, evidence, or a plan when useful.

## Why

Verify the observable result using tools or deterministic checks. Use public explanations that cite the facts needed to assess the conclusion.

## Risk

A persuasive reasoning narrative can rationalize an incorrect result.

## Trade-off

Additional reasoning can improve some tasks while increasing cost and latency.

## Try This

Compare direct answers with a short checkable calculation and validate both against known outcomes.

# How does self-consistency work?

## Answer

Generate multiple candidate solutions and aggregate their observable results under a defined rule. Agreement can improve some tasks but does not establish truth when samples share a bias.

## Why

Normalize answers before aggregation and track the extra model cost. Require external evidence for factual questions.

## Risk

Five matching hallucinations are still wrong.

## Trade-off

Sampling increases compute and may be unnecessary for deterministic tool-backed tasks.

## Try This

Compare single-sample accuracy with majority voting on a bounded reasoning dataset.

# What is retrieval-grounded prompting?

## Answer

Supply task-relevant evidence and require answers to distinguish supported statements from unresolved gaps. The retrieval and citation contracts matter as much as the instruction.

## Why

Include source IDs, revisions, and applicability notes, then validate citations and critical facts after generation.

## Risk

A model can copy an irrelevant passage accurately and still answer the wrong question.

## Trade-off

Strong grounding improves traceability while limiting unsupported coverage.

## Try This

Add one irrelevant but plausible passage and check whether the answer cites the right source.

# What is plan-and-execute prompting?

## Answer

A planner proposes steps; an executor performs permitted actions and records outcomes. The plan is a hypothesis that may need revision when tools reveal new facts.

## Why

Validate steps against capability and permission constraints, set a budget, and checkpoint durable progress.

## Risk

Executing a model's plan without backend checks turns a reasoning error into a system action.

## Trade-off

Separate planning improves visibility but adds state and recovery complexity.

## Try This

Require a plan to pause before an irreversible action and resume after approval.

# When is a critique-and-revise loop helpful?

## Answer

Use it when a critic has a specific rubric, additional evidence, or a stronger verification method. Generic requests to improve the answer often produce stylistic churn.

## Why

Bound revision count and require each revision to address an identified defect. Re-evaluate against independent acceptance criteria.

## Risk

A critic can hallucinate errors or remove a correct qualification.

## Trade-off

Additional passes improve some outputs and consume latency and tokens.

## Try This

Give the critic a citation-support rubric and measure whether factual errors actually decrease.

# How should constrained decoding be distinguished from semantic validation?

## Answer

Constrained decoding can restrict output structure or allowed tokens. Semantic validation checks whether the selected values are true, authorized, and meaningful for the application.

## Why

Use both when integrating model output with software. Apply ownership checks, numeric constraints, and state-transition rules after parsing.

## Risk

A perfectly valid JSON object can still request an impermissible action.

## Trade-off

Strong output constraints simplify parsing and may limit model expressiveness.

## Try This

Produce valid JSON containing a nonexistent resource and ensure the domain layer rejects it.

# What is prompt chaining versus tool use?

## Answer

Prompt chaining connects model calls through application-controlled stages. Tool use lets a model request an external capability under host control. A workflow may combine both.

## Why

Keep a typed boundary between the proposed tool call and actual execution. Feed the operation outcome back as an observation.

## Risk

Treating tool-call text as execution proof creates false success.

## Trade-off

Chaining is predictable; tool selection is flexible and harder to evaluate exhaustively.

## Try This

Draw one fixed extraction chain and one agent loop for the same task.

# How should prompt injection be evaluated?

## Answer

Use direct and indirect attacks that attempt data exfiltration, permission escalation, instruction replacement, and false completion. Evaluate resulting actions as well as response wording.

## Why

Include attacks inside retrieved documents, OCR text, remote tool metadata, and conversation history. Verify the backend rejects forbidden operations.

## Risk

Passing a few known jailbreak strings does not establish general resistance.

## Trade-off

Adversarial coverage costs maintenance and exposes high-impact gaps.

## Try This

Add one injection fixture per untrusted input channel and define an invariant for each.

# When should you stop optimizing the prompt?

## Answer

Stop when the dominant failures require better evidence, a reliable tool, changed product scope, or model capability rather than clearer instructions. Optimize the full system against a release target.

## Why

Categorize remaining failures and estimate the expected value of the next intervention. Keep a simple baseline for comparison.

## Risk

Prompt complexity can grow while task reliability remains flat.

## Trade-off

Backend improvements take engineering effort but often provide durable guarantees.

## Try This

Rank your ten largest failures by whether a prompt change could plausibly resolve them.

# How does grammar-guided constrained decoding guarantee 100% JSON Schema adherence compared to post-hoc validation?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: prompt-techniques
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Grammar-guided constrained decoding enforces schema adherence at the neural logit level during token generation, preventing syntax errors before they occur.** In traditional agent pipelines, developers use post-hoc validation: prompting an LLM to 'respond in valid JSON matching schema X', then parsing the output string with Pydantic or `json.loads()`. When the model drops a closing brace, hallucinates an invalid enum, or outputs markdown chatter (`Here is the JSON:`), the parser fails, requiring expensive and slow retry loops.\n\n**Logit masking via finite state machines (FSM).** Constrained decoding engines (such as Outlines, Guidance, and vLLM) compile the target JSON Schema or Pydantic model into a Context-Free Grammar (CFG) or deterministic Finite State Machine (FSM).

At every single autoregressive decoding step, the FSM determines the exact set of valid subsequent tokens in the model's vocabulary that can legally follow the current prefix. The engine constructs a dynamic logit mask, setting the logits of all invalid tokens to -infinity (probability zero).\n\n**Zero retry overhead and guaranteed structure.** Because invalid tokens have zero mathematical probability of being sampled, the model is physically incapable of generating malformed JSON, unclosed quotes, or illegal enum keys. This achieves: (1) 100% deterministic schema conformance on the very first generation attempt; (2) Zero latency spent on JSON syntax error retries; and (3) Elimination of preamble conversational filler, accelerating Time-To-First-Token.

## Why

An agent calls a banking API requiring enum `["CHECKING", "SAVINGS"]`. Under standard prompting, the model occasionally outputs `"checking_account"`, crashing the API. Grammar-guided decoding constrains sampling so only the exact enum strings can physically be generated.

## Worked Case

An agent calls a banking API requiring enum ["CHECKING", "SAVINGS"]. Under standard prompting, the model occasionally outputs "checking_account", crashing the API. Grammar-guided decoding constrains sampling so only the exact enum strings can physically be generated.

## Risk

Over-constraining decoding on open-ended text fields can artificially truncate creative reasoning if the regex or grammar is overly rigid.

## Trade-off

Grammar compilation adds a one-time startup latency (50–200ms) to build the FSM index, but completely eliminates runtime retry costs and API schema failures.

## Try This

Compile a JSON schema requiring an integer age and an enum status into a regex FSM. Verify that invalid characters receive -inf logit masks during simulated token selection.

## Follow-ups

### Does constrained decoding guarantee semantic correctness of the data?

No. Constrained decoding guarantees strict structural and syntactic conformance (e.g. valid JSON, correct types, valid enums), but does not verify whether the factual content is true.

## Citations

- https://arxiv.org/abs/2307.09702
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How does Self-Consistency with majority voting improve multi-step algorithmic reasoning, and how do you detect consensus failure?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: prompt-techniques
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Self-Consistency improves complex multi-step reasoning by sampling diverse reasoning trajectories and selecting the marginal consensus answer.** In standard greedy decoding (temperature T = 0), an LLM generates a single deterministic Chain-of-Thought (CoT) reasoning path. If the model makes a single calculation error or logical misstep early in the trajectory, the entire downstream chain derails, resulting in an incorrect final answer.\n\n**Sampling diverse reasoning paths at non-zero temperature.** Self-Consistency (Wang et al.) replaces single greedy decoding with stochastic sampling. The system samples N parallel generation paths (e.g., N = 5 to 10 at T = 0.7) from the identical prompt.

Because temperature introduces stochasticity, the model explores diverse reasoning strategies, decomposition steps, and linguistic formulations to solve the problem. Despite exploring different intermediate paths, correct mathematical, logical, and code solutions naturally converge toward the identical final outcome.\n\n**Consensus aggregation and failure detection.** The pipeline parses the terminal answer from each path and applies majority voting: (1) High confidence consensus: if 8 of 10 sampled paths agree on answer X, the system returns X with high calibrated confidence; (2) Consensus failure detection: if the 10 paths produce a flat, uniform distribution of divergent answers (e.g., 2 for A, 2 for B, 2 for C, and 4 unique values), the system detects high model uncertainty. Rather than emitting a low-confidence guess, the architecture triggers automated human-in-the-loop escalation or routes the task to a larger frontier reasoning model.

## Why

A financial calculation question is processed by greedy decoding, which makes a subtraction error in step 2 and outputs $4,200. Self-Consistency samples 7 paths: 5 paths take different calculation routes and converge on $3,800, successfully outvoting the erroneous path.

## Worked Case

A financial calculation question is processed by greedy decoding, which makes a subtraction error in step 2 and outputs $4,200. Self-Consistency samples 7 paths: 5 paths take different calculation routes and converge on $3,800, successfully outvoting the erroneous path.

## Risk

If a question contains a common deceptive cognitive trap, majority voting can select a universally shared misconception if the model family shares systematic pretraining bias.

## Trade-off

Sampling N parallel reasoning paths multiplies inference token cost and GPU compute by N, making it best suited for high-stakes financial, medical, or legal decisions.

## Try This

Run a multi-step arithmetic problem through an LLM 5 times at T=0.7. Extract the final numerical answers and compute the consensus vote and variance.

## Follow-ups

### How do you apply majority voting when answers are natural language explanations rather than numbers?

Use semantic clustering: embed the generated answers into vector space and select the centroid of the densest semantic cluster as the consensus representative.

## Citations

- https://arxiv.org/abs/2203.11171
- https://scikit-learn.org/stable/modules/model_evaluation.html

# Why do LLMs frequently fail negative constraints and how must prompts and systems be architected to enforce them?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: prompt-techniques
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**The failure of negative constraints in large language models stems directly from the associative mechanics of causal self-attention.** When a developer writes a negative instruction (e.g., 'Do NOT mention the competitor Acme Corp' or 'Do not use technical jargon'), the forbidden token strings ('Acme Corp', 'technical jargon') are explicitly introduced into the prompt context. Because transformer attention heads compute bidirectional associations across all in-context tokens, the representation of the forbidden concepts is strongly activated in the model's working memory, increasing the probability of sampling tokens associated with those exact prohibited concepts (the classic 'pink elephant' phenomenon).\n\n**Prompt reframing: positive behavioral directives.** To dramatically improve adherence, prompt engineers reframe negative restrictions into explicit positive instructions: (1) Instead of 'Do not mention price', instruct: 'Focus exclusively on product features, architecture, and deployment options'; (2) Instead of 'Do not apologize', instruct: 'Respond directly, objectively, and concisely without conversational preambles'.

Providing positive operational guardrails gives the model active token paths to pursue rather than asking it to suppress activated vocabulary.\n\n**Architectural verification firewalls.** For mission-critical negative constraints (such as legal compliance, brand safety, or privacy), prompt instructions must never serve as the sole enforcement mechanism. Production architectures deploy automated output verification filters: (1) Deterministic regex and keyword blocklists that intercept generated streaming tokens; (2) Semantic boundary classifiers (e.g., NeMo Guardrails or Llama Guard) that scan output text; and (3) Automated stream cancellation that truncates response streams immediately upon detecting a prohibited token.

## Why

A customer bot is prompted: 'Do not discuss discounts under any circumstances'. A user asks: 'What discounts do you have?'. The bot responds: 'Regarding discounts, we do not offer discounts, but our special promotional rate is...'. Reframing to: 'State that all pricing is fixed as displayed' eliminates the discount discussion.

## Worked Case

A customer bot is prompted: 'Do not discuss discounts under any circumstances'. A user asks: 'What discounts do you have?'. The bot responds: 'Regarding discounts, we do not offer discounts, but our special promotional rate is...'. Reframing to: 'State that all pricing is fixed as displayed' eliminates the discount discussion.

## Risk

Relying purely on negative prompt instructions for safety or regulatory compliance invites frequent policy breaches due to attention activation leaks.

## Trade-off

Reframing prompts requires thoughtful instructional design, and deploying automated post-generation verification filters adds sub-5ms output latency but guarantees strict negative policy enforcement.

## Try This

Compare a negative prompt ('Do not mention dogs') vs a positive prompt ('Write exclusively about felines and aquatic animals') across 20 creative story completions. Measure the frequency of forbidden mentions.

## Follow-ups

### Can logit biasing enforce negative constraints?

Yes. Logit biasing can set the bias of specific forbidden token IDs to -100, mathematically preventing the model from outputting those exact tokens.

## Citations

- https://arxiv.org/abs/2305.14818
- https://genai.owasp.org/llm-top-10/

# When does automatic prompt optimization outperform manual prompt engineering, and what are its limits?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: prompt-techniques
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Automatic prompt optimization replaces subjective, trial-and-error prompt tweaking with principled algorithmic search over prompt program parameter spaces.** In traditional workflows, developers manually rewrite system instructions and hand-pick few-shot examples through ad-hoc testing.

This approach is labor-intensive, un-reproducible, and brittle: tweaking a prompt to fix an edge case on one query frequently introduces subtle regressions across dozens of other queries.\n\n**Algorithmic optimization frameworks (DSPy and MIPROv2).** Frameworks like DSPy (Declarative Self-improving Python) and MIPROv2 treat prompt engineering as a machine learning optimization problem: (1) Declarative modules: separating task logic (signatures defining inputs and outputs) from execution prompts; (2) Bootstrap few-shot teleprompters: automatically evaluating candidate few-shot exemplars across a training dataset, retaining only effective multi-step demonstrations; and (3) Bayesian prompt search: exploring variations of instructional phrasing, task guidelines, and reasoning exemplars to maximize a quantitative domain reward metric (e.g., accuracy, citation faithfulness, schema compliance).\n\n**Operational boundaries and limitations.** Automatic prompt optimization decisively outperforms manual authoring on complex multi-stage pipelines (multi-hop RAG, agentic tool routing). However, it has clear operational limits: (1) It requires a high-quality labeled validation dataset with a deterministic evaluation metric; (2) The optimization loop executes hundreds of LLM calls, consuming substantial token budgets during compilation; and (3) An optimized prompt is overfitted to the specific target model family: swapping from GPT-4o to Claude 3.5 Sonnet requires re-running the optimization.

## Why

A team spends two weeks manually tweaking a 5-step RAG prompt, achieving 76% accuracy. Using DSPy with a 200-sample training set, the MIPROv2 optimizer explores candidate instructions and few-shot pairs, boosting accuracy to 89% in 45 minutes of automated execution.

## Worked Case

A team spends two weeks manually tweaking a 5-step RAG prompt, achieving 76% accuracy. Using DSPy with a 200-sample training set, the MIPROv2 optimizer explores candidate instructions and few-shot pairs, boosting accuracy to 89% in 45 minutes of automated execution.

## Risk

Optimizing prompts on a small or unrepresentative dataset will overfit to idiosyncratic quirks in the training split, leading to poor generalization in production.

## Trade-off

Automated prompt optimization requires building golden evaluation datasets and spending upfront LLM tokens during optimization, but delivers significantly higher, measurable accuracy and repeatability.

## Try This

Set up a simple DSPy pipeline for a classification task. Compare the baseline zero-shot accuracy against a BootstrapFewShot optimized pipeline over a 50-example validation split.

## Follow-ups

### Can DSPy optimize prompts for local models running on Ollama or vLLM?

Yes. DSPy communicates with any provider supporting chat completion APIs, allowing automated prompt compilation directly against local open-weight models.

## Citations

- https://arxiv.org/abs/2310.03714
- https://arxiv.org/abs/2406.11695

# When does requesting intermediate reasoning make an application less reliable?

<!-- meta
domain: ai-rag
subdomain: prompt-techniques
module: prompt-techniques
concept: When does requesting intermediate reasoning make an application less reliable?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An answer contains a persuasive multi-step explanation but applies a policy exception to the wrong product.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Extra reasoning text can increase latency, expose sensitive input or create an unsupported appearance of certainty. Evaluate whether a structured plan, decomposition or tool call improves the actual outcome. Request concise decisions and verifiable evidence where possible, and avoid treating generated reasoning as proof that the underlying claim is correct.

Concrete engineering case: An answer contains a persuasive multi-step explanation but applies a policy exception to the wrong product.

Boundary defense: A reproducible input, authorized source revision, explicit decision criteria and independently checked output or effect state.

## Spoken Summary

Extra reasoning text can increase latency, expose sensitive input or create an unsupported appearance of certainty. Evaluate whether a structured plan, decomposition or tool call improves the actual outcome. Request concise decisions and verifiable evidence where possible, and avoid treating generated reasoning as proof that the underlying claim is correct.

## Why

Extra reasoning text can increase latency, expose sensitive input or create an unsupported appearance of certainty. Evaluate whether a structured plan, decomposition or tool call improves the actual outcome. Request concise decisions and verifiable evidence where possible, and avoid treating generated reasoning as proof that the underlying claim is correct.

## Production Case

An answer contains a persuasive multi-step explanation but applies a policy exception to the wrong product.

## Risk

An answer contains a persuasive multi-step explanation but applies a policy exception to the wrong product.

## Trade-off

A reproducible input, authorized source revision, explicit decision criteria and independently checked output or effect state.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: prompt techniques**: Extra reasoning text can increase latency, expose sensitive input or create an unsupported appearance of certainty.

## Alternatives

- A reproducible input, authorized source revision, explicit decision criteria and independently checked output or effect state.

## Pitfalls

- An answer contains a persuasive multi-step explanation but applies a policy exception to the wrong product.

## Follow-ups

### What is a better review artifact than persuasive prose?

A reproducible input, authorized source revision, explicit decision criteria and independently checked output or effect state.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An answer contains a persuasive multi-step explanation but applies a policy exception to the wrong product.",
  "required_decision": "Extra reasoning text can increase latency, expose sensitive input or create an unsupported appearance of certainty"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html

# When do multiple samples, critique loops and decomposition make answers worse?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: prompt-techniques
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Repeated generation can reinforce a shared mistake because the samples are correlated, not independent sources of truth. A critique model can prefer persuasive wording over correctness, and decomposition can propagate a wrong intermediate assumption through every later step. Use these techniques when a verifiable intermediate contract and budget justify them. Check observable outputs and external evidence rather than treating a longer explanation as proof. Stop when additional rounds no longer improve validated outcomes or exceed the allowed latency and cost.

## Why

Five samples can agree on the same outdated policy because all read the same wrong passage. Majority vote does not repair missing evidence; source selection and applicability need correction first.

## Worked Case

Five samples can agree on the same outdated policy because all read the same wrong passage. Majority vote does not repair missing evidence; source selection and applicability need correction first.

## Risk

Self-agreement can be mistaken for independently verified confidence.

## Trade-off

Additional inference is useful only when measured improvement exceeds its cost and risk.

## Try This

Construct a shared-evidence error and compare voting with an independent source check.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
