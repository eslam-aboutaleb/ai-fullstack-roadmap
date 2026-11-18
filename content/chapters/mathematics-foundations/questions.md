<!-- chapter: mathematics-foundations -->

# How do matrix shapes explain a linear model and expose a silent broadcasting bug?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: How do matrix shapes explain a linear model and expose a silent broadcasting bug?
difficulty: interview
misconception_target: Missing the stated matrix shape boundary: A target shaped batch is subtracted from predictions shaped batch by one, producing a batch-by-batch tensor instead of one residual per example.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

With X shaped batch by features and W shaped features by outputs, XW produces batch by outputs. Bias must broadcast over the declared output dimension. A result with an unexpected extra axis can still execute and produce a meaningless loss. Write shapes at each boundary and compare a tiny hand-computed example before trusting a framework expression.

Engineering case: A target shaped batch is subtracted from predictions shaped batch by one, producing a batch-by-batch tensor instead of one residual per example.

Reasoning under a changed assumption: No. A reshape changes interpretation and may hide a semantic mismatch. Identify which axis represents examples, features and outputs first.

## Spoken Summary

With X shaped batch by features and W shaped features by outputs, XW produces batch by outputs. Bias must broadcast over the declared output dimension. A result with an unexpected extra axis can still execute and produce a meaningless loss. Write shapes at each boundary and compare a tiny hand-computed example before trusting a framework expression.

## Why

With X shaped batch by features and W shaped features by outputs, XW produces batch by outputs. Bias must broadcast over the declared output dimension. A result with an unexpected extra axis can still execute and produce a meaningless loss. Write shapes at each boundary and compare a tiny hand-computed example before trusting a framework expression.

## Production Case

A target shaped batch is subtracted from predictions shaped batch by one, producing a batch-by-batch tensor instead of one residual per example.

## Risk

A target shaped batch is subtracted from predictions shaped batch by one, producing a batch-by-batch tensor instead of one residual per example.

## Trade-off

No. A reshape changes interpretation and may hide a semantic mismatch. Identify which axis represents examples, features and outputs first.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Matrix shape**: With X shaped batch by features and W shaped features by outputs, XW produces batch by outputs.

## Alternatives

- No. A reshape changes interpretation and may hide a semantic mismatch. Identify which axis represents examples, features and outputs first.

## Pitfalls

- A target shaped batch is subtracted from predictions shaped batch by one, producing a batch-by-batch tensor instead of one residual per example.

## Follow-ups

### Can reshape always fix the problem?

No. A reshape changes interpretation and may hide a semantic mismatch. Identify which axis represents examples, features and outputs first.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A target shaped batch is subtracted from predictions shaped batch by one, producing a batch-by-batch tensor instead of one residual per example.",
  "decision": "With X shaped batch by features and W shaped features by outputs, XW produces batch by outputs"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# When do dot product and cosine similarity disagree?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: When do dot product and cosine similarity disagree?
difficulty: interview
misconception_target: Missing the stated vector normalization boundary: Two candidates point similarly to a query, but a much larger vector dominates a raw dot-product rank despite lower directional alignment.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A dot product depends on vector direction and magnitude; cosine divides by both vector norms and compares direction. Normalizing vectors changes the ranking contract, and a zero vector has no defined cosine without an explicit policy. Use the metric expected by the model and index, then evaluate retrieval relevance rather than assuming one geometric metric is always best.

Engineering case: Two candidates point similarly to a query, but a much larger vector dominates a raw dot-product rank despite lower directional alignment.

Reasoning under a changed assumption: It changes them. For unit-normalized vectors there is a specific relation between squared Euclidean distance and cosine, but that does not hold unchanged for arbitrary norms.

## Spoken Summary

A dot product depends on vector direction and magnitude; cosine divides by both vector norms and compares direction. Normalizing vectors changes the ranking contract, and a zero vector has no defined cosine without an explicit policy. Use the metric expected by the model and index, then evaluate retrieval relevance rather than assuming one geometric metric is always best.

## Why

A dot product depends on vector direction and magnitude; cosine divides by both vector norms and compares direction. Normalizing vectors changes the ranking contract, and a zero vector has no defined cosine without an explicit policy. Use the metric expected by the model and index, then evaluate retrieval relevance rather than assuming one geometric metric is always best.

## Production Case

Two candidates point similarly to a query, but a much larger vector dominates a raw dot-product rank despite lower directional alignment.

## Risk

Two candidates point similarly to a query, but a much larger vector dominates a raw dot-product rank despite lower directional alignment.

## Trade-off

It changes them. For unit-normalized vectors there is a specific relation between squared Euclidean distance and cosine, but that does not hold unchanged for arbitrary norms.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Vector normalization**: A dot product depends on vector direction and magnitude; cosine divides by both vector norms and compares direction.

## Alternatives

- It changes them. For unit-normalized vectors there is a specific relation between squared Euclidean distance and cosine, but that does not hold unchanged for arbitrary norms.

## Pitfalls

- Two candidates point similarly to a query, but a much larger vector dominates a raw dot-product rank despite lower directional alignment.

## Follow-ups

### Does normalization preserve Euclidean distances?

It changes them. For unit-normalized vectors there is a specific relation between squared Euclidean distance and cosine, but that does not hold unchanged for arbitrary norms.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Two candidates point similarly to a query, but a much larger vector dominates a raw dot-product rank despite lower directional alignment.",
  "decision": "A dot product depends on vector direction and magnitude; cosine divides by both vector norms and compares direction"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# Why does conditional probability matter when a rare-event classifier looks accurate?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: Why does conditional probability matter when a rare-event classifier looks accurate?
difficulty: interview
misconception_target: Missing the stated conditional probability boundary: Among 10,000 cases, 100 are positive. Detecting 90 of them while falsely flagging 99 negatives yields 90 true positives out of 189 alerts, not 90% alert precision.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A high sensitivity does not directly give the probability that a positive alert is correct. That posterior also depends on the base rate and false-positive rate. Work with a population table or Bayes’ rule and state the sampling assumptions. Accuracy can look strong when the frequent class dominates.

Engineering case: Among 10,000 cases, 100 are positive. Detecting 90 of them while falsely flagging 99 negatives yields 90 true positives out of 189 alerts, not 90% alert precision.

Reasoning under a changed assumption: Not necessarily. Sensitivity and false-positive behavior may transfer differently, and posterior precision changes with prevalence even when those conditional rates stay fixed.

## Spoken Summary

A high sensitivity does not directly give the probability that a positive alert is correct. That posterior also depends on the base rate and false-positive rate. Work with a population table or Bayes’ rule and state the sampling assumptions. Accuracy can look strong when the frequent class dominates.

## Why

A high sensitivity does not directly give the probability that a positive alert is correct. That posterior also depends on the base rate and false-positive rate. Work with a population table or Bayes’ rule and state the sampling assumptions. Accuracy can look strong when the frequent class dominates.

## Production Case

Among 10,000 cases, 100 are positive. Detecting 90 of them while falsely flagging 99 negatives yields 90 true positives out of 189 alerts, not 90% alert precision.

## Risk

Among 10,000 cases, 100 are positive. Detecting 90 of them while falsely flagging 99 negatives yields 90 true positives out of 189 alerts, not 90% alert precision.

## Trade-off

Not necessarily. Sensitivity and false-positive behavior may transfer differently, and posterior precision changes with prevalence even when those conditional rates stay fixed.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Conditional probability**: A high sensitivity does not directly give the probability that a positive alert is correct.

## Alternatives

- Not necessarily. Sensitivity and false-positive behavior may transfer differently, and posterior precision changes with prevalence even when those conditional rates stay fixed.

## Pitfalls

- Among 10,000 cases, 100 are positive. Detecting 90 of them while falsely flagging 99 negatives yields 90 true positives out of 189 alerts, not 90% alert precision.

## Follow-ups

### Will the same alert precision hold after the base rate changes?

Not necessarily. Sensitivity and false-positive behavior may transfer differently, and posterior precision changes with prevalence even when those conditional rates stay fixed.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Among 10,000 cases, 100 are positive. Detecting 90 of them while falsely flagging 99 negatives yields 90 true positives out of 189 alerts, not 90% alert precision.",
  "decision": "A high sensitivity does not directly give the probability that a positive alert is correct"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# What do expectation, variance and correlation tell you about an evaluation average?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: What do expectation, variance and correlation tell you about an evaluation average?
difficulty: interview
misconception_target: Missing the stated dependent sampling boundary: One source document produces one hundred nearly identical evaluation questions. Treating all of them as independent exaggerates certainty.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Expectation describes a distributional mean, variance describes spread, and correlation describes a form of dependence rather than causation. An empirical average estimates a target mean only under its sampling design. Repeated near-duplicate cases can overstate the effective amount of independent evidence and make ordinary confidence intervals optimistic.

Engineering case: One source document produces one hundred nearly identical evaluation questions. Treating all of them as independent exaggerates certainty.

Reasoning under a changed assumption: Resample or split at the relevant group level and define the target population. The grouping must reflect the dependency, not merely make intervals wider.

## Spoken Summary

Expectation describes a distributional mean, variance describes spread, and correlation describes a form of dependence rather than causation. An empirical average estimates a target mean only under its sampling design. Repeated near-duplicate cases can overstate the effective amount of independent evidence and make ordinary confidence intervals optimistic.

## Why

Expectation describes a distributional mean, variance describes spread, and correlation describes a form of dependence rather than causation. An empirical average estimates a target mean only under its sampling design. Repeated near-duplicate cases can overstate the effective amount of independent evidence and make ordinary confidence intervals optimistic.

## Production Case

One source document produces one hundred nearly identical evaluation questions. Treating all of them as independent exaggerates certainty.

## Risk

One source document produces one hundred nearly identical evaluation questions. Treating all of them as independent exaggerates certainty.

## Trade-off

Resample or split at the relevant group level and define the target population. The grouping must reflect the dependency, not merely make intervals wider.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Dependent sampling**: Expectation describes a distributional mean, variance describes spread, and correlation describes a form of dependence rather than causation.

## Alternatives

- Resample or split at the relevant group level and define the target population. The grouping must reflect the dependency, not merely make intervals wider.

## Pitfalls

- One source document produces one hundred nearly identical evaluation questions. Treating all of them as independent exaggerates certainty.

## Follow-ups

### How would you estimate uncertainty for document-level correlated cases?

Resample or split at the relevant group level and define the target population. The grouping must reflect the dependency, not merely make intervals wider.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "One source document produces one hundred nearly identical evaluation questions. Treating all of them as independent exaggerates certainty.",
  "decision": "Expectation describes a distributional mean, variance describes spread, and correlation describes a form of dependence rather than causation"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# How do you derive a scalar squared-error gradient before using autograd?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: How do you derive a scalar squared-error gradient before using autograd?
difficulty: interview
misconception_target: Missing the stated chain rule boundary: An implementation averages a loss in the forward pass but sums its derivative, making effective learning rate grow with batch size.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

For prediction wx and loss (wx-y)², the chain rule gives derivative 2(wx-y)x with respect to w. At w=1, x=2 and y=5, the derivative is -12. A gradient-descent step with learning rate 0.1 gives w=2.2. State whether the loss includes a one-half or averaging factor because those change the gradient scale.

Engineering case: An implementation averages a loss in the forward pass but sums its derivative, making effective learning rate grow with batch size.

Reasoning under a changed assumption: Perturb the parameter symmetrically and compare the numerical slope with the analytic/autograd result. Choose a step and precision that avoid domination by truncation or rounding.

## Spoken Summary

For prediction wx and loss (wx-y)², the chain rule gives derivative 2(wx-y)x with respect to w. At w=1, x=2 and y=5, the derivative is -12. A gradient-descent step with learning rate 0.1 gives w=2.2. State whether the loss includes a one-half or averaging factor because those change the gradient scale.

## Why

For prediction wx and loss (wx-y)², the chain rule gives derivative 2(wx-y)x with respect to w. At w=1, x=2 and y=5, the derivative is -12. A gradient-descent step with learning rate 0.1 gives w=2.2. State whether the loss includes a one-half or averaging factor because those change the gradient scale.

## Production Case

An implementation averages a loss in the forward pass but sums its derivative, making effective learning rate grow with batch size.

## Risk

An implementation averages a loss in the forward pass but sums its derivative, making effective learning rate grow with batch size.

## Trade-off

Perturb the parameter symmetrically and compare the numerical slope with the analytic/autograd result. Choose a step and precision that avoid domination by truncation or rounding.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Chain rule**: For prediction wx and loss (wx-y)², the chain rule gives derivative 2(wx-y)x with respect to w.

## Alternatives

- Perturb the parameter symmetrically and compare the numerical slope with the analytic/autograd result. Choose a step and precision that avoid domination by truncation or rounding.

## Pitfalls

- An implementation averages a loss in the forward pass but sums its derivative, making effective learning rate grow with batch size.

## Follow-ups

### How does a finite-difference check help?

Perturb the parameter symmetrically and compare the numerical slope with the analytic/autograd result. Choose a step and precision that avoid domination by truncation or rounding.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "An implementation averages a loss in the forward pass but sums its derivative, making effective learning rate grow with batch size.",
  "decision": "For prediction wx and loss (wx-y)², the chain rule gives derivative 2(wx-y)x with respect to w"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# Why subtract the maximum before computing softmax?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: Why subtract the maximum before computing softmax?
difficulty: interview
misconception_target: Missing the stated numerically stable softmax boundary: A training run produces NaN after a confident prediction because it computes exp on very large logits and then divides infinite values.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Exponentiating large logits can overflow even though the normalized probabilities are finite. Subtracting the same constant leaves the softmax ratios unchanged. For logits 1000 and 1001, exponentiating 0 and 1 yields approximately 0.268941 and 0.731059 after normalization. Stable log-sum-exp also avoids taking the logarithm of a rounded zero probability.

Engineering case: A training run produces NaN after a confident prediction because it computes exp on very large logits and then divides infinite values.

Reasoning under a changed assumption: No. Check input finiteness, masks, invalid operations, mixed precision and exploding gradients. Numerical stabilization addresses one mechanism rather than all possible failures.

## Spoken Summary

Exponentiating large logits can overflow even though the normalized probabilities are finite. Subtracting the same constant leaves the softmax ratios unchanged. For logits 1000 and 1001, exponentiating 0 and 1 yields approximately 0.268941 and 0.731059 after normalization. Stable log-sum-exp also avoids taking the logarithm of a rounded zero probability.

## Why

Exponentiating large logits can overflow even though the normalized probabilities are finite. Subtracting the same constant leaves the softmax ratios unchanged. For logits 1000 and 1001, exponentiating 0 and 1 yields approximately 0.268941 and 0.731059 after normalization. Stable log-sum-exp also avoids taking the logarithm of a rounded zero probability.

## Production Case

A training run produces NaN after a confident prediction because it computes exp on very large logits and then divides infinite values.

## Risk

A training run produces NaN after a confident prediction because it computes exp on very large logits and then divides infinite values.

## Trade-off

No. Check input finiteness, masks, invalid operations, mixed precision and exploding gradients. Numerical stabilization addresses one mechanism rather than all possible failures.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Numerically stable softmax**: Exponentiating large logits can overflow even though the normalized probabilities are finite.

## Alternatives

- No. Check input finiteness, masks, invalid operations, mixed precision and exploding gradients. Numerical stabilization addresses one mechanism rather than all possible failures.

## Pitfalls

- A training run produces NaN after a confident prediction because it computes exp on very large logits and then divides infinite values.

## Follow-ups

### Can subtracting the maximum fix every NaN?

No. Check input finiteness, masks, invalid operations, mixed precision and exploding gradients. Numerical stabilization addresses one mechanism rather than all possible failures.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A training run produces NaN after a confident prediction because it computes exp on very large logits and then divides infinite values.",
  "decision": "Exponentiating large logits can overflow even though the normalized probabilities are finite"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# What does SVD or PCA preserve, and why is unsupervised preprocessing still a leakage risk?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: What does SVD or PCA preserve, and why is unsupervised preprocessing still a leakage risk?
difficulty: interview
misconception_target: Missing the stated principal directions boundary: A pipeline computes PCA on the full dataset before cross-validation, letting each fold influence the feature representation used to evaluate itself.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

SVD factors a matrix into singular directions and magnitudes. PCA typically applies a related decomposition to centered training data to retain high-variance directions. High variance need not be predictive or fair. Fitting centering or principal directions on a held-out set exposes information from that set even without its labels.

Engineering case: A pipeline computes PCA on the full dataset before cross-validation, letting each fold influence the feature representation used to evaluate itself.

Reasoning under a changed assumption: No. Noise and signal can occupy overlapping directions, and useful low-variance features can be discarded. Choose dimensions with a validation design tied to the actual task.

## Spoken Summary

SVD factors a matrix into singular directions and magnitudes. PCA typically applies a related decomposition to centered training data to retain high-variance directions. High variance need not be predictive or fair. Fitting centering or principal directions on a held-out set exposes information from that set even without its labels.

## Why

SVD factors a matrix into singular directions and magnitudes. PCA typically applies a related decomposition to centered training data to retain high-variance directions. High variance need not be predictive or fair. Fitting centering or principal directions on a held-out set exposes information from that set even without its labels.

## Production Case

A pipeline computes PCA on the full dataset before cross-validation, letting each fold influence the feature representation used to evaluate itself.

## Risk

A pipeline computes PCA on the full dataset before cross-validation, letting each fold influence the feature representation used to evaluate itself.

## Trade-off

No. Noise and signal can occupy overlapping directions, and useful low-variance features can be discarded. Choose dimensions with a validation design tied to the actual task.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Principal directions**: SVD factors a matrix into singular directions and magnitudes.

## Alternatives

- No. Noise and signal can occupy overlapping directions, and useful low-variance features can be discarded. Choose dimensions with a validation design tied to the actual task.

## Pitfalls

- A pipeline computes PCA on the full dataset before cross-validation, letting each fold influence the feature representation used to evaluate itself.

## Follow-ups

### Can a small number of components remove every noisy feature?

No. Noise and signal can occupy overlapping directions, and useful low-variance features can be discarded. Choose dimensions with a validation design tied to the actual task.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A pipeline computes PCA on the full dataset before cross-validation, letting each fold influence the feature representation used to evaluate itself.",
  "decision": "SVD factors a matrix into singular directions and magnitudes"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# What does a 95% confidence interval actually justify for a measured proportion?

<!-- meta
domain: mathematics
subdomain: mathematics-foundations
module: mathematics-foundations
concept: What does a 95% confidence interval actually justify for a measured proportion?
difficulty: interview
misconception_target: Missing the stated interval coverage boundary: A model gets 98 of 100 examples right. The Wilson interval is approximately 0.9300 to 0.9945 rather than certainty at exactly 0.98.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Under the procedure’s assumptions, repeated samples produce intervals with their stated coverage behavior. The interval is not a promise for every subgroup or future distribution. A Wilson interval remains within feasible probability bounds and is useful for small error counts, but it does not repair dependence, label errors or selection on the test set.

Engineering case: A model gets 98 of 100 examples right. The Wilson interval is approximately 0.9300 to 0.9945 rather than certainty at exactly 0.98.

Reasoning under a changed assumption: Selection changes the evaluation interpretation. Keep model choice in validation and evaluate the frozen decision under an appropriate fresh protocol.

## Spoken Summary

Under the procedure’s assumptions, repeated samples produce intervals with their stated coverage behavior. The interval is not a promise for every subgroup or future distribution. A Wilson interval remains within feasible probability bounds and is useful for small error counts, but it does not repair dependence, label errors or selection on the test set.

## Why

Under the procedure’s assumptions, repeated samples produce intervals with their stated coverage behavior. The interval is not a promise for every subgroup or future distribution. A Wilson interval remains within feasible probability bounds and is useful for small error counts, but it does not repair dependence, label errors or selection on the test set.

## Production Case

A model gets 98 of 100 examples right. The Wilson interval is approximately 0.9300 to 0.9945 rather than certainty at exactly 0.98.

## Risk

A model gets 98 of 100 examples right. The Wilson interval is approximately 0.9300 to 0.9945 rather than certainty at exactly 0.98.

## Trade-off

Selection changes the evaluation interpretation. Keep model choice in validation and evaluate the frozen decision under an appropriate fresh protocol.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Interval coverage**: Under the procedure’s assumptions, repeated samples produce intervals with their stated coverage behavior.

## Alternatives

- Selection changes the evaluation interpretation. Keep model choice in validation and evaluate the frozen decision under an appropriate fresh protocol.

## Pitfalls

- A model gets 98 of 100 examples right. The Wilson interval is approximately 0.9300 to 0.9945 rather than certainty at exactly 0.98.

## Follow-ups

### Can you select the best of many models and reuse an ordinary interval without qualification?

Selection changes the evaluation interpretation. Keep model choice in validation and evaluate the frozen decision under an appropriate fresh protocol.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A model gets 98 of 100 examples right. The Wilson interval is approximately 0.9300 to 0.9945 rather than certainty at exactly 0.98.",
  "decision": "Under the procedure’s assumptions, repeated samples produce intervals with their stated coverage behavior"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- https://scikit-learn.org/stable/modules/cross_validation.html

# How do scalars, vectors, matrices and tensors describe model data?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A scalar is one value; a vector has one indexed axis; a matrix has two; a tensor generalizes this to more axes. Shape specifies axis lengths but not their meaning. An image tensor might represent batch, channel, height and width, while a text tensor uses batch, position and feature axes. A shape-compatible operation can still be semantically wrong if axes are swapped. Write axis meanings and units alongside dimensions before multiplying or broadcasting arrays.

## Why

A matrix of 32 examples by 10 features multiplied by 10 features by 3 outputs produces 32 by 3 predictions. Swapping the example and feature axes changes the intended operation even if another compatible matrix happens to make it run.

## Worked Case

A matrix of 32 examples by 10 features multiplied by 10 features by 3 outputs produces 32 by 3 predictions. Swapping the example and feature axes changes the intended operation even if another compatible matrix happens to make it run.

## Risk

Broadcasting can hide a misplaced axis by producing a plausible but incorrect shape.

## Trade-off

Explicit shapes improve review and debugging at little runtime cost.

## Try This

Annotate each axis and derive the output shape of a batched linear layer.

## Citations

- https://mml-book.github.io/

# What do a dot product, matrix multiplication and vector norm measure?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A dot product sums products of aligned coordinates and depends on both magnitude and direction. Matrix multiplication applies these weighted combinations to rows and columns. A norm measures size under its chosen definition; the Euclidean norm is the square root of the sum of squared coordinates. Cosine similarity divides the dot product by both norms, removing magnitude for nonzero vectors. These operations acquire meaning from the representation and task, not from the formula alone. A zero vector requires an explicit cosine policy.

## Why

Vectors [2,0] and [1,0] have dot product 2 and cosine 1. A larger dot product does not mean a higher probability, and rescaling an unnormalized representation can change rankings.

## Worked Case

Vectors [2,0] and [1,0] have dot product 2 and cosine 1. A larger dot product does not mean a higher probability, and rescaling an unnormalized representation can change rankings.

## Risk

Normalization can discard a magnitude signal the model intentionally learned.

## Trade-off

Follow the representation's metric contract and evaluate task outcomes.

## Try This

Calculate dot product, lengths and cosine for two nonzero vectors and one zero-vector edge case.

## Citations

- https://mml-book.github.io/

# How do eigenvectors, SVD and PCA connect to dimensionality reduction?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An eigenvector keeps its direction under a square linear transformation, scaled by an eigenvalue. Singular value decomposition factors a matrix into orthogonal input/output directions and nonnegative singular values. Principal component analysis uses high-variance directions of centered data to build a lower-dimensional representation. Fit centering and component selection using training data only. High variance does not guarantee target relevance, fairness or preserved rare signals, so assess downstream performance rather than treating explained variance as the final quality metric.

## Why

A rare fraud signal can contribute little overall variance and disappear when only the largest components are retained. A high explained-variance percentage can therefore coexist with worse detection of the important minority case.

## Worked Case

A rare fraud signal can contribute little overall variance and disappear when only the largest components are retained. A high explained-variance percentage can therefore coexist with worse detection of the important minority case.

## Risk

Fitting components on held-out data leaks its distribution into the pipeline.

## Trade-off

Lower dimensions save work but may discard task-relevant information.

## Try This

Fit a projection on training data and inspect reconstruction and minority-class errors separately.

## Citations

- https://mml-book.github.io/

# How do conditional probability, independence and Bayes' rule differ?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Conditional probability measures an event within a stated conditioning population. Independence means conditioning on one event does not change the probability of the other under the model; it is an assumption to justify, not a default property. Bayes' rule relates a reversed conditional through the prior and evidence probability. Confusing the probability of a positive test given disease with disease given a positive test ignores prevalence. Use a contingency table when denominators are easy to confuse, especially for rare-event classifiers.

## Why

With 100 truly positive cases among 10,000, 90 detections and 99 false alerts produce precision 90/189 even though sensitivity is 90/100. The two probabilities answer different operational questions.

## Worked Case

With 100 truly positive cases among 10,000, 90 detections and 99 false alerts produce precision 90/189 even though sensitivity is 90/100. The two probabilities answer different operational questions.

## Risk

A changing deployment prevalence can change positive predictive value without changing sensitivity.

## Trade-off

Tables clarify denominators; probability models generalize when assumptions are stated.

## Try This

Recalculate alert precision after reducing prevalence while keeping the test rates fixed.

## Citations

- https://mml-book.github.io/

# How do expectation, variance and covariance describe uncertain quantities?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Expectation is a probability-weighted mean, variance measures squared deviation around that mean, and covariance captures how two quantities vary together. Covariance depends on scale; correlation normalizes it under nonzero finite variances. Zero correlation does not generally prove independence, and correlation does not establish causation. Distinguish variability among individual observations from uncertainty in an estimated mean. For operational data, dependent observations and changing conditions can invalidate simple independent-sample uncertainty calculations.

## Why

Repeated requests from one customer can be strongly related. Treating each as an independent sample may make an estimate seem more precise than a customer-level analysis supports.

## Worked Case

Repeated requests from one customer can be strongly related. Treating each as an independent sample may make an estimate seem more precise than a customer-level analysis supports.

## Risk

Averages can hide multimodal or high-tail behavior.

## Trade-off

Summary statistics are useful when paired with distribution and sampling context.

## Try This

Compare per-request and per-customer summaries for a dataset with repeated customers.

## Citations

- https://mml-book.github.io/

# How do derivatives, partial derivatives and the chain rule produce gradients?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A derivative describes local sensitivity to one input. A partial derivative changes one coordinate while holding the others fixed, and a gradient collects those partial derivatives for a scalar objective. The chain rule propagates sensitivity through composed operations, which is the basis of backpropagation. A gradient is local information, not a guarantee that a large step improves the objective. Check shapes, nondifferentiable points and numerical scale, and compare a small analytic result with a finite-difference approximation where appropriate.

## Why

For loss (w*x-y)^2, the derivative with respect to w is 2*(w*x-y)*x. With x=2, y=3 and w=1, the derivative is -4; a sufficiently small positive learning-rate update increases w.

## Worked Case

For loss (w*x-y)^2, the derivative with respect to w is 2*(w*x-y)*x. With x=2, y=3 and w=1, the derivative is -4; a sufficiently small positive learning-rate update increases w.

## Risk

Large finite-difference steps and floating-point cancellation can both mislead gradient checks.

## Trade-off

Analytic or automatic derivatives scale; finite differences help validate small smooth cases.

## Try This

Derive one scalar gradient and compare it with a centered finite difference.

## Citations

- https://mml-book.github.io/

# Why do conditioning, numerical stability and log-space calculations matter?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A well-defined formula can still be numerically fragile. Conditioning describes sensitivity of a problem's output to input changes, while numerical stability concerns how an algorithm amplifies finite-precision effects. Exponentiating large logits can overflow even though softmax probabilities are finite; subtracting the largest logit preserves the mathematical distribution while improving computation. Very small probabilities can underflow when multiplied, so log-space accumulation is often useful. State precision and tolerance instead of expecting every mathematically equivalent expression to compute identically.

## Why

Softmax of logits 1000 and 1001 can overflow with direct exponentials. Subtracting 1001 yields logits -1 and 0 with the same probabilities and finite intermediate values.

## Worked Case

Softmax of logits 1000 and 1001 can overflow with direct exponentials. Subtracting 1001 yields logits -1 and 0 with the same probabilities and finite intermediate values.

## Risk

Clipping every unusual value can conceal a faulty model or data pipeline.

## Trade-off

Stable algorithms preserve intended calculations without claiming arbitrary precision.

## Try This

Compare naive and stabilized softmax on large logits and verify probabilities sum approximately to one.

## Citations

- https://mml-book.github.io/

# How do confidence intervals, hypothesis tests and effect sizes answer different questions?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: mathematics-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A confidence interval describes an estimation procedure's repeated-sampling coverage under its assumptions; it is not generally a probability that a fixed parameter lies in one observed interval. A hypothesis test evaluates data against a specified null model. Effect size describes the magnitude of a difference, which may matter more operationally than a small p-value. Account for paired observations, clustering, multiple comparisons and selection. Repeatedly checking and stopping when a result looks favorable can invalidate an ordinary fixed-sample interpretation.

## Why

Two models evaluated on the same examples create paired outcomes. Comparing independent unpaired summaries throws away that structure, while searching dozens of models and reporting only the best can exaggerate improvement.

## Worked Case

Two models evaluated on the same examples create paired outcomes. Comparing independent unpaired summaries throws away that structure, while searching dozens of models and reporting only the best can exaggerate improvement.

## Risk

Statistical significance does not guarantee useful size or relevance to deployment.

## Trade-off

Use a design matching the decision and report uncertainty with practical thresholds.

## Try This

Compare paired model errors and state a useful minimum improvement before inspecting the result.

## Citations

- https://mml-book.github.io/
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
