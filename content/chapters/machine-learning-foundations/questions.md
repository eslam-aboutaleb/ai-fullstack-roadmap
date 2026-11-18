<!-- chapter: machine-learning-foundations -->

# How do supervised, unsupervised and reinforcement learning define different feedback?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: How do supervised, unsupervised and reinforcement learning define different feedback?
difficulty: interview
misconception_target: Missing the stated learning feedback boundary: A team uses clustering to infer whether a customer action is permitted. Similarity groups do not supply the authoritative policy label needed for that decision.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Supervised learning fits predictions against observed targets. Unsupervised methods find structure under objectives such as reconstruction or clustering without those target labels. Reinforcement learning uses interaction rewards under a sequential decision process. These are learning setups, not a ranking of intelligence or a guarantee that one method fits every product.

Engineering case: A team uses clustering to infer whether a customer action is permitted. Similarity groups do not supply the authoritative policy label needed for that decision.

Reasoning under a changed assumption: Its targets are constructed from data, such as masked or next-token values. The source and construction of supervision matter even when humans did not label each example.

## Spoken Summary

Supervised learning fits predictions against observed targets. Unsupervised methods find structure under objectives such as reconstruction or clustering without those target labels. Reinforcement learning uses interaction rewards under a sequential decision process. These are learning setups, not a ranking of intelligence or a guarantee that one method fits every product.

## Why

Supervised learning fits predictions against observed targets. Unsupervised methods find structure under objectives such as reconstruction or clustering without those target labels. Reinforcement learning uses interaction rewards under a sequential decision process. These are learning setups, not a ranking of intelligence or a guarantee that one method fits every product.

## Production Case

A team uses clustering to infer whether a customer action is permitted. Similarity groups do not supply the authoritative policy label needed for that decision.

## Risk

A team uses clustering to infer whether a customer action is permitted. Similarity groups do not supply the authoritative policy label needed for that decision.

## Trade-off

Its targets are constructed from data, such as masked or next-token values. The source and construction of supervision matter even when humans did not label each example.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Learning feedback**: Supervised learning fits predictions against observed targets.

## Alternatives

- Its targets are constructed from data, such as masked or next-token values. The source and construction of supervision matter even when humans did not label each example.

## Pitfalls

- A team uses clustering to infer whether a customer action is permitted. Similarity groups do not supply the authoritative policy label needed for that decision.

## Follow-ups

### Is self-supervised learning free of targets?

Its targets are constructed from data, such as masked or next-token values. The source and construction of supervision matter even when humans did not label each example.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A team uses clustering to infer whether a customer action is permitted. Similarity groups do not supply the authoritative policy label needed for that decision.",
  "decision": "Supervised learning fits predictions against observed targets"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# What makes a feature unavailable at prediction time even when it exists in the table?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: What makes a feature unavailable at prediction time even when it exists in the table?
difficulty: interview
misconception_target: Missing the stated prediction-time availability boundary: A model predicts ticket escalation using a column filled only when the ticket is finally escalated. Offline accuracy is excellent and deployment cannot reproduce it.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A feature can encode information recorded after the decision, such as a resolution code or future account state. Define an as-of timestamp for the prediction and reconstruct what was observable then. A random split does not remove this leakage because the feature itself contains forbidden future information.

Engineering case: A model predicts ticket escalation using a column filled only when the ticket is finally escalated. Offline accuracy is excellent and deployment cannot reproduce it.

Reasoning under a changed assumption: No. Derived fields, joins, duplicated entities and preprocessing can still encode target or future information indirectly.

## Spoken Summary

A feature can encode information recorded after the decision, such as a resolution code or future account state. Define an as-of timestamp for the prediction and reconstruct what was observable then. A random split does not remove this leakage because the feature itself contains forbidden future information.

## Why

A feature can encode information recorded after the decision, such as a resolution code or future account state. Define an as-of timestamp for the prediction and reconstruct what was observable then. A random split does not remove this leakage because the feature itself contains forbidden future information.

## Production Case

A model predicts ticket escalation using a column filled only when the ticket is finally escalated. Offline accuracy is excellent and deployment cannot reproduce it.

## Risk

A model predicts ticket escalation using a column filled only when the ticket is finally escalated. Offline accuracy is excellent and deployment cannot reproduce it.

## Trade-off

No. Derived fields, joins, duplicated entities and preprocessing can still encode target or future information indirectly.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Prediction-time availability**: A feature can encode information recorded after the decision, such as a resolution code or future account state.

## Alternatives

- No. Derived fields, joins, duplicated entities and preprocessing can still encode target or future information indirectly.

## Pitfalls

- A model predicts ticket escalation using a column filled only when the ticket is finally escalated. Offline accuracy is excellent and deployment cannot reproduce it.

## Follow-ups

### Does dropping the target column eliminate leakage?

No. Derived fields, joins, duplicated entities and preprocessing can still encode target or future information indirectly.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A model predicts ticket escalation using a column filled only when the ticket is finally escalated. Offline accuracy is excellent and deployment cannot reproduce it.",
  "decision": "A feature can encode information recorded after the decision, such as a resolution code or future account state"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do linear regression and logistic classification choose different outputs and losses?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: How do linear regression and logistic classification choose different outputs and losses?
difficulty: interview
misconception_target: Missing the stated classification threshold boundary: A team reports a classifier’s probability as an automatically authorized business decision without choosing a threshold or considering error costs.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Linear regression predicts a numerical response and commonly minimizes squared residuals. Logistic classification transforms a score into a probability and uses a classification objective such as log loss. The decision threshold is a separate policy chosen from costs and validation data. A linear decision boundary can still be useful as a strong transparent baseline.

Engineering case: A team reports a classifier’s probability as an automatically authorized business decision without choosing a threshold or considering error costs.

Reasoning under a changed assumption: No. Assess calibration and distribution shift; high model confidence can accompany a wrong or unsupported prediction.

## Spoken Summary

Linear regression predicts a numerical response and commonly minimizes squared residuals. Logistic classification transforms a score into a probability and uses a classification objective such as log loss. The decision threshold is a separate policy chosen from costs and validation data. A linear decision boundary can still be useful as a strong transparent baseline.

## Why

Linear regression predicts a numerical response and commonly minimizes squared residuals. Logistic classification transforms a score into a probability and uses a classification objective such as log loss. The decision threshold is a separate policy chosen from costs and validation data. A linear decision boundary can still be useful as a strong transparent baseline.

## Production Case

A team reports a classifier’s probability as an automatically authorized business decision without choosing a threshold or considering error costs.

## Risk

A team reports a classifier’s probability as an automatically authorized business decision without choosing a threshold or considering error costs.

## Trade-off

No. Assess calibration and distribution shift; high model confidence can accompany a wrong or unsupported prediction.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Classification threshold**: Linear regression predicts a numerical response and commonly minimizes squared residuals.

## Alternatives

- No. Assess calibration and distribution shift; high model confidence can accompany a wrong or unsupported prediction.

## Pitfalls

- A team reports a classifier’s probability as an automatically authorized business decision without choosing a threshold or considering error costs.

## Follow-ups

### Does a probability near one prove the answer is correct?

No. Assess calibration and distribution shift; high model confidence can accompany a wrong or unsupported prediction.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A team reports a classifier’s probability as an automatically authorized business decision without choosing a threshold or considering error costs.",
  "decision": "Linear regression predicts a numerical response and commonly minimizes squared residuals"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do decision trees, random forests and boosting differ in how errors are controlled?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: How do decision trees, random forests and boosting differ in how errors are controlled?
difficulty: interview
misconception_target: Missing the stated ensemble bias and variance boundary: A deep tree memorizes training identities. Its perfect training accuracy collapses on new customers despite apparently interpretable rules.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A decision tree partitions features with learned rules and can overfit small samples. A random forest averages diverse trees, often reducing variance. Boosting adds learners sequentially against an objective, which can improve fit but requires careful regularization and validation. Compare with a simple baseline under the same split and resource budget.

Engineering case: A deep tree memorizes training identities. Its perfect training accuracy collapses on new customers despite apparently interpretable rules.

Reasoning under a changed assumption: No. A more powerful model can exploit leakage more effectively. Split integrity and prediction-time availability remain prerequisites.

## Spoken Summary

A decision tree partitions features with learned rules and can overfit small samples. A random forest averages diverse trees, often reducing variance. Boosting adds learners sequentially against an objective, which can improve fit but requires careful regularization and validation. Compare with a simple baseline under the same split and resource budget.

## Why

A decision tree partitions features with learned rules and can overfit small samples. A random forest averages diverse trees, often reducing variance. Boosting adds learners sequentially against an objective, which can improve fit but requires careful regularization and validation. Compare with a simple baseline under the same split and resource budget.

## Production Case

A deep tree memorizes training identities. Its perfect training accuracy collapses on new customers despite apparently interpretable rules.

## Risk

A deep tree memorizes training identities. Its perfect training accuracy collapses on new customers despite apparently interpretable rules.

## Trade-off

No. A more powerful model can exploit leakage more effectively. Split integrity and prediction-time availability remain prerequisites.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Ensemble bias and variance**: A decision tree partitions features with learned rules and can overfit small samples.

## Alternatives

- No. A more powerful model can exploit leakage more effectively. Split integrity and prediction-time availability remain prerequisites.

## Pitfalls

- A deep tree memorizes training identities. Its perfect training accuracy collapses on new customers despite apparently interpretable rules.

## Follow-ups

### Does an ensemble remove the need for feature timing checks?

No. A more powerful model can exploit leakage more effectively. Split integrity and prediction-time availability remain prerequisites.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A deep tree memorizes training identities. Its perfect training accuracy collapses on new customers despite apparently interpretable rules.",
  "decision": "A decision tree partitions features with learned rules and can overfit small samples"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# When can k-means or PCA help without becoming an unsupported business label?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: When can k-means or PCA help without becoming an unsupported business label?
difficulty: interview
misconception_target: Missing the stated clustering objective boundary: Customer records cluster mainly by an unscaled transaction amount. The team mistakes those magnitude groups for distinct support needs.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

K-means groups points under a distance-based objective and depends on scale, initialization and a chosen cluster count. PCA projects along training-data variance directions. Use them for a declared representation or exploratory purpose, inspect stability and validate downstream usefulness. A cluster identity or high-variance direction does not automatically correspond to a meaningful category.

Engineering case: Customer records cluster mainly by an unscaled transaction amount. The team mistakes those magnitude groups for distinct support needs.

Reasoning under a changed assumption: Use stability, reconstruction or task-specific evidence and human interpretation as appropriate. Be explicit that those criteria do not prove a supervised classification claim.

## Spoken Summary

K-means groups points under a distance-based objective and depends on scale, initialization and a chosen cluster count. PCA projects along training-data variance directions. Use them for a declared representation or exploratory purpose, inspect stability and validate downstream usefulness. A cluster identity or high-variance direction does not automatically correspond to a meaningful category.

## Why

K-means groups points under a distance-based objective and depends on scale, initialization and a chosen cluster count. PCA projects along training-data variance directions. Use them for a declared representation or exploratory purpose, inspect stability and validate downstream usefulness. A cluster identity or high-variance direction does not automatically correspond to a meaningful category.

## Production Case

Customer records cluster mainly by an unscaled transaction amount. The team mistakes those magnitude groups for distinct support needs.

## Risk

Customer records cluster mainly by an unscaled transaction amount. The team mistakes those magnitude groups for distinct support needs.

## Trade-off

Use stability, reconstruction or task-specific evidence and human interpretation as appropriate. Be explicit that those criteria do not prove a supervised classification claim.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Clustering objective**: K-means groups points under a distance-based objective and depends on scale, initialization and a chosen cluster count.

## Alternatives

- Use stability, reconstruction or task-specific evidence and human interpretation as appropriate. Be explicit that those criteria do not prove a supervised classification claim.

## Pitfalls

- Customer records cluster mainly by an unscaled transaction amount. The team mistakes those magnitude groups for distinct support needs.

## Follow-ups

### How would you evaluate a representation without labeled categories?

Use stability, reconstruction or task-specific evidence and human interpretation as appropriate. Be explicit that those criteria do not prove a supervised classification claim.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Customer records cluster mainly by an unscaled transaction amount. The team mistakes those magnitude groups for distinct support needs.",
  "decision": "K-means groups points under a distance-based objective and depends on scale, initialization and a chosen cluster count"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How should regularization and early stopping use validation data?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: How should regularization and early stopping use validation data?
difficulty: interview
misconception_target: Missing the stated validation selection boundary: A learner stops at the epoch with maximum test accuracy and presents that same maximum as a fresh held-out result.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Regularization constrains or penalizes fitted parameters, while early stopping selects a training point from validation behavior. Both affect model choice. Fit preprocessing on training rows and keep the final test set outside those decisions. Repeated changes driven by test errors consume the test set as another validation source.

Engineering case: A learner stops at the epoch with maximum test accuracy and presents that same maximum as a fresh held-out result.

Reasoning under a changed assumption: No. Training loss can continue falling while the model fits noise or artifacts. Monitor the declared validation objective and investigate task-relevant slices.

## Spoken Summary

Regularization constrains or penalizes fitted parameters, while early stopping selects a training point from validation behavior. Both affect model choice. Fit preprocessing on training rows and keep the final test set outside those decisions. Repeated changes driven by test errors consume the test set as another validation source.

## Why

Regularization constrains or penalizes fitted parameters, while early stopping selects a training point from validation behavior. Both affect model choice. Fit preprocessing on training rows and keep the final test set outside those decisions. Repeated changes driven by test errors consume the test set as another validation source.

## Production Case

A learner stops at the epoch with maximum test accuracy and presents that same maximum as a fresh held-out result.

## Risk

A learner stops at the epoch with maximum test accuracy and presents that same maximum as a fresh held-out result.

## Trade-off

No. Training loss can continue falling while the model fits noise or artifacts. Monitor the declared validation objective and investigate task-relevant slices.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Validation selection**: Regularization constrains or penalizes fitted parameters, while early stopping selects a training point from validation behavior.

## Alternatives

- No. Training loss can continue falling while the model fits noise or artifacts. Monitor the declared validation objective and investigate task-relevant slices.

## Pitfalls

- A learner stops at the epoch with maximum test accuracy and presents that same maximum as a fresh held-out result.

## Follow-ups

### Can more training always improve generalization?

No. Training loss can continue falling while the model fits noise or artifacts. Monitor the declared validation objective and investigate task-relevant slices.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A learner stops at the epoch with maximum test accuracy and presents that same maximum as a fresh held-out result.",
  "decision": "Regularization constrains or penalizes fitted parameters, while early stopping selects a training point from validation behavior"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do precision, recall and PR metrics expose failure on an imbalanced task?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: How do precision, recall and PR metrics expose failure on an imbalanced task?
difficulty: interview
misconception_target: Missing the stated positive-class metrics boundary: A dataset has four negatives and one positive. An always-negative model achieves 80% accuracy but zero positive recall.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Precision asks how many predicted positives are correct; recall asks how many actual positives were found. Accuracy can favor a model that predicts only the frequent class. Threshold choice trades false positives against misses, so report counts, denominators and a cost-relevant view such as a precision-recall curve under the evaluated prevalence.

Engineering case: A dataset has four negatives and one positive. An always-negative model achieves 80% accuracy but zero positive recall.

Reasoning under a changed assumption: Their observed precision depends on the data distribution. Include the dataset and sampling design so the comparison has a defined meaning.

## Spoken Summary

Precision asks how many predicted positives are correct; recall asks how many actual positives were found. Accuracy can favor a model that predicts only the frequent class. Threshold choice trades false positives against misses, so report counts, denominators and a cost-relevant view such as a precision-recall curve under the evaluated prevalence.

## Why

Precision asks how many predicted positives are correct; recall asks how many actual positives were found. Accuracy can favor a model that predicts only the frequent class. Threshold choice trades false positives against misses, so report counts, denominators and a cost-relevant view such as a precision-recall curve under the evaluated prevalence.

## Production Case

A dataset has four negatives and one positive. An always-negative model achieves 80% accuracy but zero positive recall.

## Risk

A dataset has four negatives and one positive. An always-negative model achieves 80% accuracy but zero positive recall.

## Trade-off

Their observed precision depends on the data distribution. Include the dataset and sampling design so the comparison has a defined meaning.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Positive-class metrics**: Precision asks how many predicted positives are correct; recall asks how many actual positives were found.

## Alternatives

- Their observed precision depends on the data distribution. Include the dataset and sampling design so the comparison has a defined meaning.

## Pitfalls

- A dataset has four negatives and one positive. An always-negative model achieves 80% accuracy but zero positive recall.

## Follow-ups

### Can two thresholds be compared without stating prevalence?

Their observed precision depends on the data distribution. Include the dataset and sampling design so the comparison has a defined meaning.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A dataset has four negatives and one positive. An always-negative model achieves 80% accuracy but zero positive recall.",
  "decision": "Precision asks how many predicted positives are correct; recall asks how many actual positives were found"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# Why can an accurate ranking still produce poorly calibrated probabilities?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: Why can an accurate ranking still produce poorly calibrated probabilities?
difficulty: interview
misconception_target: Missing the stated probability calibration boundary: Two models order all alerts identically, but one calls almost every alert 99% likely. Only about 70% of that bin is positive.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Ranking compares ordering, while calibration compares predicted probabilities with empirical frequencies. A monotonic score transformation can preserve ranking and change probability meaning. Evaluate discrimination, reliability and support per bin separately. A lower proper scoring loss reflects more than calibration alone.

Engineering case: Two models order all alerts identically, but one calls almost every alert 99% likely. Only about 70% of that bin is positive.

Reasoning under a changed assumption: Use data separated from the final test decision, such as a properly designed validation or cross-validation calibration procedure. Never fit it on the same final labels used to claim its quality.

## Spoken Summary

Ranking compares ordering, while calibration compares predicted probabilities with empirical frequencies. A monotonic score transformation can preserve ranking and change probability meaning. Evaluate discrimination, reliability and support per bin separately. A lower proper scoring loss reflects more than calibration alone.

## Why

Ranking compares ordering, while calibration compares predicted probabilities with empirical frequencies. A monotonic score transformation can preserve ranking and change probability meaning. Evaluate discrimination, reliability and support per bin separately. A lower proper scoring loss reflects more than calibration alone.

## Production Case

Two models order all alerts identically, but one calls almost every alert 99% likely. Only about 70% of that bin is positive.

## Risk

Two models order all alerts identically, but one calls almost every alert 99% likely. Only about 70% of that bin is positive.

## Trade-off

Use data separated from the final test decision, such as a properly designed validation or cross-validation calibration procedure. Never fit it on the same final labels used to claim its quality.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Probability calibration**: Ranking compares ordering, while calibration compares predicted probabilities with empirical frequencies.

## Alternatives

- Use data separated from the final test decision, such as a properly designed validation or cross-validation calibration procedure. Never fit it on the same final labels used to claim its quality.

## Pitfalls

- Two models order all alerts identically, but one calls almost every alert 99% likely. Only about 70% of that bin is positive.

## Follow-ups

### Where should a calibrator be fitted?

Use data separated from the final test decision, such as a properly designed validation or cross-validation calibration procedure. Never fit it on the same final labels used to claim its quality.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Two models order all alerts identically, but one calls almost every alert 99% likely. Only about 70% of that bin is positive.",
  "decision": "Ranking compares ordering, while calibration compares predicted probabilities with empirical frequencies"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do you distinguish covariate shift, target prevalence shift and concept drift?

<!-- meta
domain: ml
subdomain: machine-learning-foundations
module: machine-learning-foundations
concept: How do you distinguish covariate shift, target prevalence shift and concept drift?
difficulty: interview
misconception_target: Missing the stated distribution change boundary: A form change alters missing-value patterns, and later labels reveal worse performance for one customer segment. Retraining before fixing collection would preserve a corrupted pipeline.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Input distributions, label prevalence and the relationship between inputs and outcomes can change in different ways. Monitor observable inputs and delayed quality labels, investigate collection changes and compare slices. A distribution alert alone does not prove a quality regression, while stable inputs do not prove the target relationship is unchanged.

Engineering case: A form change alters missing-value patterns, and later labels reveal worse performance for one customer segment. Retraining before fixing collection would preserve a corrupted pipeline.

Reasoning under a changed assumption: No. The defect may be schema, label timing, policy or feature availability. Define the cause and compare a frozen candidate with a valid post-change evaluation set.

## Spoken Summary

Input distributions, label prevalence and the relationship between inputs and outcomes can change in different ways. Monitor observable inputs and delayed quality labels, investigate collection changes and compare slices. A distribution alert alone does not prove a quality regression, while stable inputs do not prove the target relationship is unchanged.

## Why

Input distributions, label prevalence and the relationship between inputs and outcomes can change in different ways. Monitor observable inputs and delayed quality labels, investigate collection changes and compare slices. A distribution alert alone does not prove a quality regression, while stable inputs do not prove the target relationship is unchanged.

## Production Case

A form change alters missing-value patterns, and later labels reveal worse performance for one customer segment. Retraining before fixing collection would preserve a corrupted pipeline.

## Risk

A form change alters missing-value patterns, and later labels reveal worse performance for one customer segment. Retraining before fixing collection would preserve a corrupted pipeline.

## Trade-off

No. The defect may be schema, label timing, policy or feature availability. Define the cause and compare a frozen candidate with a valid post-change evaluation set.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Distribution change**: Input distributions, label prevalence and the relationship between inputs and outcomes can change in different ways.

## Alternatives

- No. The defect may be schema, label timing, policy or feature availability. Define the cause and compare a frozen candidate with a valid post-change evaluation set.

## Pitfalls

- A form change alters missing-value patterns, and later labels reveal worse performance for one customer segment. Retraining before fixing collection would preserve a corrupted pipeline.

## Follow-ups

### Will retraining always repair drift?

No. The defect may be schema, label timing, policy or feature availability. Define the cause and compare a frozen candidate with a valid post-change evaluation set.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A form change alters missing-value patterns, and later labels reveal worse performance for one customer segment. Retraining before fixing collection would preserve a corrupted pipeline.",
  "decision": "Input distributions, label prevalence and the relationship between inputs and outcomes can change in different ways"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# Why do substring classifiers fail on short skill names, and how should a rule baseline abstain?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: machine-learning-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A substring rule is a matching policy with predictable counterexamples.** Testing whether a short token occurs anywhere in text can classify an unrelated word as a programming skill. A title containing a seniority keyword can trigger a proficiency label even when the sentence says the person is not senior. These failures are properties of the rule, not evidence that every such task requires a large language model.

**Start with a bounded vocabulary and explicit matching semantics.** Normalize known phrases, use exact or token-aware matching where appropriate, and maintain reviewed aliases for punctuation-sensitive labels such as C++ or C#. Word-boundary regular expressions are not automatically correct for every language, tokenization rule or symbol-containing term. Preserve the original phrase for review.

**Make unknown a legitimate output.** If no rule applies or multiple rules conflict, return unknown or review-required rather than a default confident category. Hints supplied by a user can help, but they should not silently override verified evidence or turn arbitrary text into an authoritative label. Record which rule fired and which dictionary version it used.

**Evaluate against the actual alternative.** Compare a simple rule baseline, a statistical model and any model-assisted enrichment using the same held-out labels. Include short tokens, negation, mixed languages, misspellings and ambiguous phrases. Report coverage as well as precision among accepted cases. The example deliberately uses a tiny exact vocabulary to avoid substring false positives and abstains on unsupported phrases.

## Why

A substring check for the language Go matches the word ongoing. An exact vocabulary leaves ongoing unknown while recognizing an explicitly listed Go value; broader natural-language phrases require a separate policy.

## Worked Case

A substring check for the language Go matches the word ongoing. An exact vocabulary leaves ongoing unknown while recognizing an explicitly listed Go value; broader natural-language phrases require a separate policy.

## Risk

A default category can conceal unsupported classification and contaminate downstream recommendations.

## Trade-off

Exact matching has lower recall but a clearer error surface; richer matching needs evaluated disambiguation rules.

## Try This

Build negative examples containing short labels inside unrelated words. Compare false positives and abstention coverage before adding fuzzy matching.

## Follow-ups

### Would adding word boundaries solve every case?

No. Symbols, compounds, languages without spaces and contextual negation still require task-specific handling. Evaluate the rule on representative data instead of assuming a regular expression establishes semantics.

### When should a model replace this baseline?

When measured task value and held-out error reduction justify its latency, cost and maintenance. Keep the baseline as a comparison and retain an uncertainty path.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://docs.python.org/3/library/unicodedata.html

# How do classification, regression, clustering and anomaly detection define different tasks?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Classification predicts a category under a label contract, regression predicts a numeric target, clustering groups observations under a similarity objective, and anomaly detection scores unusual behavior relative to a reference. Their outputs and evaluation requirements differ. An unusual event is not automatically fraudulent, and a discovered cluster is not automatically a business category. Define the unit of prediction, available inputs, action taken and cost of mistakes before selecting an algorithm. Some tasks can be reformulated, but that changes assumptions and acceptance criteria.

## Why

Predicting an invoice amount and deciding whether to review it are different tasks. A high predicted amount is not itself evidence of fraud, and a review classifier needs a reviewed label and threshold policy.

## Worked Case

Predicting an invoice amount and deciding whether to review it are different tasks. A high predicted amount is not itself evidence of fraud, and a review classifier needs a reviewed label and threshold policy.

## Risk

Choosing an algorithm before defining the decision can optimize an irrelevant target.

## Trade-off

Simple task definitions and baselines make later complexity easier to justify.

## Try This

Specify prediction time, target, action and error costs for one proposed model.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://scikit-learn.org/stable/modules/calibration.html

# How do bias, variance, underfitting and overfitting guide model selection?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Bias concerns systematic limitations of a modeling procedure, while variance concerns sensitivity to training samples. Underfitting and overfitting are diagnosed through task-relevant training and held-out behavior, not model size alone. More flexible models may fit training data better without improving unseen outcomes. Learning curves, regularization and representative validation help distinguish insufficient capacity from scarce or misleading data. The classical bias–variance decomposition has assumptions and does not describe every modern model regime with a simple monotonic curve.

## Why

A deep tree can memorize training rows and fail on a later time period. Compare a constrained tree and a simple baseline using a split reflecting deployment rather than concluding that training accuracy establishes progress.

## Worked Case

A deep tree can memorize training rows and fail on a later time period. Compare a constrained tree and a simple baseline using a split reflecting deployment rather than concluding that training accuracy establishes progress.

## Risk

A random split can hide the time-dependent failure mistaken for ordinary overfitting.

## Trade-off

Additional flexibility is useful only when validated against the actual target distribution.

## Try This

Plot training and validation outcomes as sample size or regularization changes.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do cross-validation, grouped splits and time-based splits prevent misleading estimates?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Cross-validation repeatedly fits on a training portion and evaluates on another portion to assess a selection procedure. The split must respect dependence and information availability. Grouped splits keep related entities such as patients or documents together; time-based splits prevent future information entering past predictions. Preprocessing and feature selection must fit inside each training fold. Keep a final untouched test for the selected procedure, and use nested selection when an unbiased estimate of a tuned search process is required.

## Why

Near-duplicate documents in training and validation can make a retrieval model appear to generalize. Group them by source family before splitting so the held-out portion tests genuinely unseen sources.

## Worked Case

Near-duplicate documents in training and validation can make a retrieval model appear to generalize. Group them by source family before splitting so the held-out portion tests genuinely unseen sources.

## Risk

A pipeline can leak through preprocessing even when final model fitting uses the correct rows.

## Trade-off

More folds improve data reuse at additional compute cost and do not repair an invalid split.

## Try This

Build a split with group overlap checks and a training-only preprocessing step.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do missing values, scaling and categorical encoding affect a learned pipeline?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Missingness may carry information or reflect data collection failures; choose a policy consistent with deployment. Fit imputation, scaling and category mappings on training data only, then apply the same learned transformations to future rows. Unknown categories need an explicit fallback or rejection policy. Scaling affects distance-based and regularized models differently from many tree models. Target encoding can leak labels unless constructed with appropriate training-only or cross-fitted discipline. Store the complete transformation with the model.

## Why

A test-only category must not trigger an accidental column shift or a newly fitted encoding. Preserve the training feature order and route the category through the documented unknown-value behavior.

## Worked Case

A test-only category must not trigger an accidental column shift or a newly fitted encoding. Preserve the training feature order and route the category through the documented unknown-value behavior.

## Risk

Re-fitting preprocessing during prediction changes the feature space beneath fixed model weights.

## Trade-off

Model-specific preprocessing avoids both unnecessary transformations and hidden representation changes.

## Try This

Test missing values and an unseen category using a fitted pipeline without refitting it.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do precision, recall, F1 and confusion matrices expose different failure costs?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Start with a declared **positive class** and the confusion-matrix counts. TP means true positive, FP false positive, FN false negative and TN true negative.

| Metric | Formula | Question it answers |
| --- | --- | --- |
| Precision | `TP / (TP + FP)` | Of the predicted positives, how many were positive? |
| Recall | `TP / (TP + FN)` | Of the actual positives, how many were detected? |
| F1 | `2 * precision * recall / (precision + recall)` | What is their harmonic-mean balance? |
| Accuracy | `(TP + TN) / total` | What proportion of all classifications was correct? |

**State zero-denominator behavior** instead of silently inventing a perfect score. Explain how class averaging and sample weights affect the reported result.

For 10 real unsafe cases, 8 detections and 40 total alerts imply recall `8/10 = 0.8` and precision `8/40 = 0.2`. A high recall can therefore create a large review workload. A majority-negative classifier can also have high accuracy while missing every unsafe case.

Choose a **decision threshold** against explicit error costs and review capacity on validation data. Raising it generally changes the confusion counts even if the underlying scores and ranking remain unchanged. Freeze selection before using the final held-out test.

## Why

Of 10 genuine unsafe cases, detecting 8 with 40 total alerts gives recall 0.8 and precision 0.2. A team must consider missed incidents and review capacity rather than celebrating only one metric.

## Worked Case

Of 10 genuine unsafe cases, detecting 8 with 40 total alerts gives recall 0.8 and precision 0.2. A team must consider missed incidents and review capacity rather than celebrating only one metric.

## Risk

A threshold tuned on the test set makes the reported test result part of selection.

## Trade-off

Choose metrics that match consequences and operational capacity.

## Try This

Compute all confusion counts and explain how raising a threshold changes review workload.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://scikit-learn.org/stable/modules/calibration.html

# How do probability calibration and decision thresholds differ?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Calibration asks whether predicted probabilities correspond to observed frequencies for a defined population and slice. A threshold turns scores into actions according to costs and constraints. Ranking quality can be strong while probability estimates are poor. Calibration should use data separate from fitting as appropriate and be evaluated without leaking final labels. A deployment shift can alter calibration or the optimal action threshold. An apparently confident score should not bypass safety rules or authorize an effect.

## Why

A score of 0.8 should not be interpreted as an 80 percent outcome rate without calibration evidence. Even calibrated probabilities may require different review thresholds for actions with different false-negative costs.

## Worked Case

A score of 0.8 should not be interpreted as an 80 percent outcome rate without calibration evidence. Even calibrated probabilities may require different review thresholds for actions with different false-negative costs.

## Risk

Good overall calibration can hide poor calibration in an important subgroup.

## Trade-off

Calibrated estimates support decisions; thresholds still encode a policy choice.

## Try This

Compare reliability bins and select an action threshold under explicit error costs.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://scikit-learn.org/stable/modules/calibration.html

# How do regularization, early stopping and hyperparameter search control model flexibility?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Regularization penalizes or constrains aspects of the fitted model; early stopping chooses when to stop iterative training using a validation rule. Hyperparameters such as penalty strength, depth and learning rate are selected outside ordinary fitted parameter updates. Every tried configuration consumes selection information from validation data. Record the search space, budget, seed policy and selection metric, then evaluate the frozen choice on held-out data. An arbitrary early-stopping epoch is not a universal safeguard against leakage or drift.

## Why

Trying 100 depths and reporting the best validation score overstates what a fresh model is likely to achieve. Preserve a final test or evaluate the complete search through a suitable outer split.

## Worked Case

Trying 100 depths and reporting the best validation score overstates what a fresh model is likely to achieve. Preserve a final test or evaluate the complete search through a suitable outer split.

## Risk

Repeated manual tuning can overfit the validation set without any code-level training leak.

## Trade-off

Search breadth competes with compute budget and confidence in the selected estimate.

## Try This

Specify a bounded search and freeze selection before opening final test labels.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do drift, delayed labels and retraining change production monitoring?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Data drift changes input distributions, concept drift changes relationships to outcomes, and label distribution changes can alter prevalence. These can overlap but require different evidence. Monitor input quality and prediction behavior promptly, then evaluate outcome quality when labels arrive with their actual delay and selection bias. A distribution alert is a diagnosis trigger, not proof that retraining will help. Version the model, preprocessing and training data, and compare a candidate against the current release before promotion.

## Why

If only manually reviewed alerts receive labels, measured precision describes that selected population. It cannot directly establish performance on all unreviewed traffic or recall over incidents that were never observed.

## Worked Case

If only manually reviewed alerts receive labels, measured precision describes that selected population. It cannot directly establish performance on all unreviewed traffic or recall over incidents that were never observed.

## Risk

Automatic retraining can reinforce faulty labels or a broken ingestion process.

## Trade-off

Monitor multiple signals and require a defined promotion and rollback policy.

## Try This

Design monitoring with a seven-day label delay and document which metrics are unavailable immediately.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do nearest-neighbor models choose predictions, and why does scaling matter?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A nearest-neighbor method retains reference examples and predicts from nearby examples under a defined distance and weighting rule. The number of neighbors changes smoothing and sensitivity to noise. Features with large numerical scale can dominate a distance unless representation and scaling are chosen deliberately. Missing values, sparse inputs and high dimensionality require explicit handling. Prediction can be expensive because it searches reference data, so include index construction and query cost when comparing a simple training phase with other models.

## Why

A distance using income in thousands and age in years can weight the axes unintentionally. Fit any scaling on training data, then evaluate the same transformation and distance on held-out examples.

## Worked Case

A distance using income in thousands and age in years can weight the axes unintentionally. Fit any scaling on training data, then evaluate the same transformation and distance on held-out examples.

## Risk

A nearby example is not necessarily a valid causal or policy precedent.

## Trade-off

Neighbors provide a useful local baseline while retaining storage and query costs.

## Try This

Compare several neighbor counts with training-only scaling and a fixed validation split.

## Citations

- https://scikit-learn.org/stable/modules/neighbors.html

# How do support vector machines use margins, kernels and regularization?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A support vector machine seeks a separating decision boundary under a margin and error trade-off. A kernel permits an implicit feature-space comparison without explicitly constructing every transformed feature. Regularization strength and kernel parameters influence fit and generalization, and feature scaling can be crucial. A kernel method can become costly on large training sets, while linear variants suit different scales. Classification scores are not automatically calibrated probabilities; evaluate that separately if downstream decisions require probability interpretation.

## Why

A radial-basis kernel can fit a curved boundary, but an extreme parameter choice can memorize local noise. Compare it against a linear baseline through the same leakage-safe validation pipeline.

## Worked Case

A radial-basis kernel can fit a curved boundary, but an extreme parameter choice can memorize local noise. Compare it against a linear baseline through the same leakage-safe validation pipeline.

## Risk

Kernel flexibility can overfit and increase compute without improving deployment outcomes.

## Trade-off

Use the simplest boundary that meets measured quality and resource requirements.

## Try This

Tune a bounded parameter grid inside training/validation and preserve the final test set.

## Citations

- https://scikit-learn.org/stable/modules/svm.html

# Why can Naive Bayes work even when its conditional independence assumption is imperfect?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Naive Bayes combines a class prior with feature likelihoods under conditional independence given the class. This strong modeling assumption simplifies estimation and can produce an effective baseline, especially for some sparse text tasks. Select the variant to match feature semantics, such as counts or continuous measurements. Smoothing avoids certain zero-probability failures. A classifier can rank or classify usefully while its probability estimates are poorly calibrated, so empirical task performance does not prove that the assumed data-generating model is literally correct.

## Why

Two correlated words can cause evidence to be counted more than once under the independence approximation. The predicted class may remain useful while confidence becomes too extreme.

## Worked Case

Two correlated words can cause evidence to be counted more than once under the independence approximation. The predicted class may remain useful while confidence becomes too extreme.

## Risk

Good classification accuracy does not validate probability calibration.

## Trade-off

A fast interpretable baseline exposes whether a more expensive model offers practical value.

## Try This

Fit a count-based text baseline and inspect both classification errors and calibration.

## Citations

- https://scikit-learn.org/stable/modules/naive_bayes.html

# How do bagging, random forests and gradient boosting reduce different errors?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Bagging fits models on resampled data and aggregates their predictions, often reducing variance. A random forest adds feature randomness to diversify trees. Gradient boosting builds models sequentially to improve the current objective, commonly by fitting information related to loss gradients. Their depth, learning rate and ensemble size have different interactions. More trees do not repair leakage, label errors or a mismatched target. Compare full preprocessing, tuning and resource costs rather than treating all ensembles as interchangeable complexity upgrades.

## Why

A deep tree that varies strongly across training samples may benefit from averaging diverse trees. A sequential boosting model instead changes each new learner in response to the current fit and needs its own validation and regularization policy.

## Worked Case

A deep tree that varies strongly across training samples may benefit from averaging diverse trees. A sequential boosting model instead changes each new learner in response to the current fit and needs its own validation and regularization policy.

## Risk

Correlated errors reduce the benefit of averaging.

## Trade-off

Ensemble choice follows observed errors and operational constraints, not a universal ranking.

## Try This

Compare a constrained tree, forest and boosting baseline under one consistent split.

## Citations

- https://scikit-learn.org/stable/modules/ensemble.html

# How should imbalanced data, class weighting and resampling be evaluated?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Class imbalance changes how aggregate accuracy relates to useful behavior. Weighting changes the training objective; resampling changes the examples presented to it; threshold selection changes the action policy. None guarantees appropriate deployment calibration. Apply resampling only within training folds and avoid duplicate leakage into validation. Evaluate minority-class outcomes, review capacity and prevalence-sensitive metrics on representative held-out data. Distinguish genuine rare outcomes from a biased labeling process that hides cases the system never investigated.

## Why

Oversampling a rare class before splitting can put duplicated versions of one example into training and validation. The apparent improvement may reflect memorization rather than better rare-case detection.

## Worked Case

Oversampling a rare class before splitting can put duplicated versions of one example into training and validation. The apparent improvement may reflect memorization rather than better rare-case detection.

## Risk

A balanced training set can produce misleading probabilities for an imbalanced deployment population.

## Trade-off

Choose weighting and thresholds from decision costs and validate their complete pipeline.

## Try This

Compare weighted training and threshold changes without resampling held-out data.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do permutation importance, correlated features and causal claims differ?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Permutation importance measures the change in a chosen score when one feature is shuffled under a specified dataset and model. It describes that model's dependence under that perturbation, not an intrinsic causal importance of the feature. Correlated alternatives can conceal importance, while shuffling can create unrealistic feature combinations. Compute it on a suitable evaluation set and compare meaningful groups or domain-informed interventions where needed. A predictive association does not establish what will happen if a business changes the associated input.

## Why

Two near-duplicate location features can substitute for each other. Shuffling only one may barely affect the model even though location information is central to its predictions.

## Worked Case

Two near-duplicate location features can substitute for each other. Shuffling only one may barely affect the model even though location information is central to its predictions.

## Risk

Low individual importance can be mistaken for irrelevant information.

## Trade-off

Interpretability tools support diagnosis when their perturbation assumptions are stated.

## Try This

Analyze a correlated-feature pair and explain why its importance is model- and dataset-specific.

## Citations

- https://scikit-learn.org/stable/modules/permutation_importance.html

# How do K-means, density-based clustering and hierarchical clustering differ?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

K-means minimizes a within-cluster squared-distance objective around centroids and needs a chosen cluster count. Density-based methods group dense regions and can label sparse observations as noise, with sensitivity to distance scale and density parameters. Hierarchical methods build nested groups under a linkage rule. Different objectives produce different valid partitions; an unsupervised group is not automatically a true label. Check stability, scale and downstream usefulness rather than selecting a visually attractive plot as proof of meaningful categories.

## Why

K-means can divide two curved groups poorly because its centroid-based geometry favors another partition. A density-based method may recover those shapes but fail when densities vary or parameters are inappropriate.

## Worked Case

K-means can divide two curved groups poorly because its centroid-based geometry favors another partition. A density-based method may recover those shapes but fail when densities vary or parameters are inappropriate.

## Risk

A silhouette or visual separation score alone does not establish business validity.

## Trade-off

Choose the grouping assumption from the task and inspect sensitivity to representation.

## Try This

Compare cluster assignments under scaling and parameter changes without using hidden labels for tuning.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# How does reinforcement learning differ from supervised prediction in an application decision loop?

<!-- meta
answer_format: conceptual
domain: ml
subdomain: machine-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Reinforcement learning models actions that influence future state and reward, so feedback can be delayed and data depends on the policy collecting it. A supervised predictor maps observed inputs to targets without necessarily solving that sequential control problem. Exploration, reward specification and safe evaluation introduce additional risks. A reward proxy can be optimized while the real user outcome worsens. Before using online learning, establish a suitable baseline, constrain actions and evaluate policy assumptions and data support through an appropriate controlled design.

## Why

Optimizing immediate clicks can repeatedly recommend sensational content while harming longer-term satisfaction. That outcome reflects the reward and horizon, not merely the model's classification accuracy.

## Worked Case

Optimizing immediate clicks can repeatedly recommend sensational content while harming longer-term satisfaction. That outcome reflects the reward and horizon, not merely the model's classification accuracy.

## Risk

Unconstrained exploration can cause real effects while collecting feedback.

## Trade-off

Use a sequential learning approach only when its decision and evaluation requirements are justified.

## Try This

Specify state, action, reward, horizon and prohibited actions for one proposed learning loop.

## Citations

- https://www.davidsilver.uk/teaching/
