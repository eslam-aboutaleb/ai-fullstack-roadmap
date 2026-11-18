<!-- chapter: classification -->

# How do logistic regression and softmax turn features into decisions, and what objective is optimized?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Start with a score and a loss.** Binary logistic regression computes a linear score from the features and maps it through a sigmoid. Multinomial logistic regression uses one score per class and a softmax to produce a normalized vector. Fitting minimizes a regularized negative log-likelihood, often described as cross-entropy loss. The coefficients define a linear boundary in the chosen feature space; nonlinear feature engineering can still change that space.

**Separate fitting from threshold selection.** A fitted probability estimate does not require a decision threshold of 0.5 in every application. Select thresholds using validation data and an explicit error-cost policy. In multiclass tasks an argmax always selects a known label unless you add a validated rejection rule. A high softmax value does not prove that an out-of-domain example belongs to the taxonomy.

**Control scale and leakage.** Fit scalers or text vocabularies using the training partition only, and tune regularization on a separate validation procedure. Inspect coefficient behavior and failure slices rather than equating a simple model with a weak baseline. Sparse word features plus a linear head can be competitive and cheap for many text tasks.

**Evaluate probabilities and labels independently.** Report per-class outcomes, log loss where meaningful, calibration and abstention behavior. The small gradient example illustrates one binary update; the optional lab fits an actual multiclass logistic-regression baseline on independent data.

## Why

A feature vector predicts the wrong class with high confidence. Cross-entropy penalizes that error strongly, but choosing another threshold cannot repair a representation that lacks the decisive feature.

## Worked Case

A feature vector predicts the wrong class with high confidence. Cross-entropy penalizes that error strongly, but choosing another threshold cannot repair a representation that lacks the decisive feature.

## Risk

Treating a softmax maximum as a universal correctness probability hides calibration and open-set failures.

## Trade-off

A linear model is fast and interpretable relative to its features, but it cannot invent missing nonlinear distinctions.

## Try This

Compute one sigmoid prediction and gradient update, then compare a lexical and an embedding linear model on the same held-out messages.

## Follow-ups

### Does regularization replace more data?

It limits or penalizes model complexity under an objective. It can improve generalization, but does not repair mislabeled targets, biased sampling or missing deployment cases.

### Can a linear classifier learn from embeddings?

Yes. The linear decision boundary then operates in the embedding space rather than in raw token features; the encoder may already express complex nonlinear structure.

## Citations

- https://scikit-learn.org/stable/modules/linear_model.html
- https://scikit-learn.org/stable/modules/calibration.html

# When is Naive Bayes a useful text classifier, and why can its confidence be misleading?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Use the representation-specific likelihood model.** Multinomial Naive Bayes commonly models nonnegative count-like text features. Bernoulli variants model occurrence indicators, while Gaussian variants assume feature likelihoods with a different form. The word naive refers to conditional feature-independence assumptions given the class, not to an absence of training.

**Compute in log space.** Combining priors and many feature likelihoods by direct multiplication can underflow. Add log probabilities and use smoothing to prevent one unseen token from zeroing a class likelihood. Decide how unknown tokens and empty documents are handled. A text vector with arbitrary negative coordinates is not automatically valid input for a multinomial count model.

**Treat it as a measured baseline.** Correlated words can cause overconfident outputs because the model effectively counts related evidence repeatedly. Calibration and held-out evaluation remain necessary. Complement variants can be useful comparisons for imbalanced text, but no variant removes the need for a representative split.

**Inspect failure cases.** Negation, rare identifiers, domain shift and label correlations can break simplistic likelihood assumptions. Compare to a most-frequent predictor and a regularized linear model before paying for a larger model. The optional lab runs a real count-feature Naive Bayes pipeline; the arithmetic example makes smoothing visible without claiming to be a complete language model.

## Why

A document contains an unseen term. Without smoothing one class likelihood becomes zero regardless of the remaining evidence; smoothing preserves a finite comparison rather than guaranteeing a correct label.

## Worked Case

A document contains an unseen term. Without smoothing one class likelihood becomes zero regardless of the remaining evidence; smoothing preserves a finite comparison rather than guaranteeing a correct label.

## Risk

A numerically normalized posterior may still be badly calibrated because the likelihood assumptions are wrong.

## Trade-off

Naive Bayes is inexpensive and often effective on sparse text; richer models can capture interactions at higher fitting and serving cost.

## Try This

Calculate smoothed token likelihoods for two classes and add a correlated phrase to inspect confidence changes.

## Follow-ups

### Can I feed any dense embedding to MultinomialNB?

Not automatically. Its nonnegative feature requirements and likelihood interpretation differ from arbitrary signed semantic vectors. Choose a compatible head and validate its assumptions.

### Why keep a simple baseline after adding an encoder?

It reveals whether semantic modeling actually improves the task and provides a low-cost comparison under vocabulary or provider failures.

## Citations

- https://scikit-learn.org/stable/modules/naive_bayes.html

# How do decision trees, random forests and gradient-boosted trees differ as classifiers?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A tree partitions feature space through conditional splits.** Classification trees often choose splits using impurity reduction, such as Gini impurity or entropy. Depth, leaf size and pruning influence overfitting. A single tree can express interactions and provide a traceable path, but small data changes can change its structure substantially.

**Distinguish ensemble mechanisms.** A random forest averages diverse trees trained with randomized data or features to reduce variance. Gradient boosting adds models sequentially to improve an objective based on previous errors or gradients. Learning rate, tree complexity and number of iterations interact; a larger ensemble is not automatically better.

**Choose features and validation for the deployment question.** Trees are often strong on structured tabular features. Very high-dimensional sparse text may favor a linear baseline, while dense embeddings can be evaluated as another input representation. Feature importance can be biased or correlated; it is not a causal explanation of what makes a category true.

**Measure serving implications.** Compare memory, fitting cost, tail latency and probability calibration in addition to average accuracy. Fit any target-dependent preprocessing inside training folds. The local lab uses real forest and linear baselines on the bundled wine dataset, while the miniature impurity calculation isolates what a candidate split optimizes.

## Why

A deep tree perfectly memorizes training records but misclassifies a changed source format. Adding more leaves improves training impurity without demonstrating generalization.

## Worked Case

A deep tree perfectly memorizes training records but misclassifies a changed source format. Adding more leaves improves training impurity without demonstrating generalization.

## Risk

Leaking target information into features can make any tree ensemble appear excellent on an invalid split.

## Trade-off

Ensembles improve robustness for some feature regimes but reduce the simplicity of a single decision path.

## Try This

Compare a shallow tree, forest and boosted baseline under the same split, and inspect an error rather than only aggregate importance.

## Follow-ups

### Does a random forest need feature scaling?

Its split rules usually do not need the same scaling as distance-based methods, but preprocessing, missing-value behavior and feature construction still need a clear contract.

### Does high feature importance prove causation?

No. It reflects a model and measurement method under correlations and sampling assumptions. Use separate causal reasoning for interventions.

## Citations

- https://scikit-learn.org/stable/modules/tree.html
- https://scikit-learn.org/stable/modules/ensemble.html

# How do support vector machines and nearest neighbors compare with probabilistic linear models?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A support vector machine optimizes a margin-related objective.** A linear support vector classifier can be effective for sparse text; a kernel method can create nonlinear boundaries through pairwise similarity without explicitly listing every transformed feature. Kernel choice and regularization change the geometry and fitting cost. A margin score is not itself a calibrated probability.

**Nearest neighbors makes a local decision.** It stores reference examples and votes or weights labels from nearby training points under a chosen distance. Scaling, irrelevant dimensions, duplicate examples and class imbalance all affect that neighborhood. Prediction cost grows with the reference set unless an appropriate index or reduction is used, and approximate neighbors introduce another source of error.

**Keep comparison fair.** Evaluate logistic regression, support vector and neighbor methods on the same held-out examples with training-only preprocessing. If probabilities are required, calibrate margin-based scores using a leakage-safe procedure and inspect the calibration rather than applying a sigmoid by intuition.

**Match the deployment constraints.** A neighbor model can offer actual reference examples for review, but those examples need authorization before disclosure. A compact linear model has predictable serving cost; nonlinear kernels and large neighbor stores can be more expensive. The optional lab executes real SVC and nearest-neighbor classifiers on bundled data.

## Why

A feature measured in thousands dominates another measured between zero and one in Euclidean nearest-neighbor voting. The chosen label reflects units rather than the intended semantic relation.

## Worked Case

A feature measured in thousands dominates another measured between zero and one in Euclidean nearest-neighbor voting. The chosen label reflects units rather than the intended semantic relation.

## Risk

Reporting a margin or a neighbor vote as a correctness probability can overstate uncertainty quality.

## Trade-off

Local reference methods help inspect examples; compact trained heads are often cheaper to serve at large scale.

## Try This

Scale only on training data, then compare linear, kernel and neighbor models with both classification metrics and prediction cost.

## Follow-ups

### Can approximate neighbor search change classification accuracy?

Yes. Missing or replacing nearby reference points can change the vote. Evaluate index recall and end-task label outcomes together.

### Is an SVM always nonlinear?

No. A linear SVM is a common baseline. Nonlinearity depends on the chosen kernel or feature transformation.

## Citations

- https://scikit-learn.org/stable/modules/svm.html
- https://scikit-learn.org/stable/modules/neighbors.html

# How do you split classification data when messages, users or documents are correlated?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Define the generalization claim first.** Random row splitting can measure performance on new rows from a similar population, but not necessarily on new users, source documents or time periods. Put related variants, near-duplicates and shared source groups on one side of a split when the deployment claim requires independence across those groups.

**Keep every learned preprocessing step inside the training procedure.** Token vocabularies, feature selection, imputation and scaling can leak information when fitted on all rows. Hyperparameter and prompt selection use validation, while the final test set remains a frozen report boundary. A pipeline prevents some accidental fitting leaks but cannot choose a valid grouping policy for you.

**Treat embedding preparation explicitly.** Encoding held-out text with a frozen publicly pretrained model is different from fine-tuning that encoder on the test labels. If adapting the encoder, constructing class prototypes or selecting examples, use only the allowed training and validation partitions. Record the encoder revision and deduplication policy.

**Inspect unexpectedly perfect results.** Look for copied templates, labels in the input, future-derived features and repeated test-driven tuning. Report split identifiers and population limitations with the result. The miniature split check verifies disjoint group identifiers; it does not prove a dataset represents future production traffic.

## Why

Two paraphrases of the same template land in training and test. A high score may measure template recognition rather than generalization to genuinely new messages.

## Worked Case

Two paraphrases of the same template land in training and test. A high score may measure template recognition rather than generalization to genuinely new messages.

## Risk

Stratification preserves class proportions but does not by itself separate correlated groups or prevent temporal leakage.

## Trade-off

Stricter group or time splits can reduce available training data but support a more meaningful deployment claim.

## Try This

Construct repeated-source messages and show the difference between row-based and group-based evaluation.

## Follow-ups

### Should every split be stratified?

Only when compatible with the deployment and grouping constraints. Group independence and chronological validity may take priority over matching class proportions exactly.

### Can I tune prompts on the test set if I never train weights?

That still uses test feedback to choose the system. Prompt, threshold and taxonomy changes are model-selection decisions too.

## Citations

- https://scikit-learn.org/stable/modules/cross_validation.html

# How do you evaluate an imbalanced classifier without hiding minority-class failures?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Start with the confusion matrix and denominators.** Accuracy can be high when most examples belong to one class. Precision measures the fraction of predicted positives that are correct; recall measures the fraction of actual positives recovered. F1 combines precision and recall under a particular harmonic mean, but does not encode every business cost.

**Choose aggregation deliberately.** Macro averaging gives each class equal weight in the reported mean, while micro averaging aggregates counts and can be dominated by common labels. Weighted averages reflect the evaluated class support. For multilabel tasks, exact-set accuracy and per-label metrics answer different questions. Report class supports so a rare-category estimate is not mistaken for a stable conclusion.

**Handle imbalance during training without contaminating evaluation.** Class weights, resampling and additional labeling can change the fit. Apply resampling inside the training folds only, and evaluate on a representative untouched distribution. Synthetic examples can add useful stress tests but do not establish the real prevalence of a class.

**Tie threshold choices to operational capacity.** A high-recall system can overload review queues with false positives. Report precision-recall tradeoffs, abstention coverage and cost per useful decision. The local arithmetic example makes a majority predictor's failure visible, and the optional lab reports macro-F1 rather than celebrating training accuracy.

## Why

A classifier predicts the majority class for 99 of 100 records and never finds the one urgent minority case. Its accuracy looks strong while its urgent-case recall is zero.

## Worked Case

A classifier predicts the majority class for 99 of 100 records and never finds the one urgent minority case. Its accuracy looks strong while its urgent-case recall is zero.

## Risk

One aggregate score can hide a class with no correctly handled examples or an unusably noisy review queue.

## Trade-off

Weighting rare classes can improve recall while lowering precision or calibration, so validate the actual operating point.

## Try This

Compare majority and learned baselines using per-class precision, recall, support and macro-F1.

## Follow-ups

### Is ROC-AUC enough for a rare positive class?

It summarizes ranking under one definition, but may obscure the precision attainable at the needed recall. Inspect precision-recall behavior and actual workload at candidate thresholds.

### What if a class has no test examples?

Its performance is unmeasured in that split. Do not convert the absence of evidence into a perfect class score.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do calibration, decision thresholds and out-of-domain rejection solve different problems?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Calibration describes a population-level relationship.** Among cases assigned a probability near a value, a calibrated model should be correct at the corresponding frequency under the evaluated event definition. This is distinct from classification accuracy and from ranking quality. A model can rank well while its reported probabilities are too confident.

**A threshold defines an action policy.** Select it using validation data, error costs and review capacity. A cost-sensitive threshold formula relies on probabilities and assumptions that must actually hold. A single global threshold may be inappropriate for classes with different costs or data support. Keep the final test set out of calibration fitting and threshold tuning.

**Rejection needs its own evaluation.** Low maximum probability or a small top-two margin can be useful signals, but a closed-set model may assign high confidence to unfamiliar inputs. Include out-of-domain examples, ambiguous messages and conflicting evidence. Measure false rejection on answerable inputs as well as incorrect acceptance of unknowns.

**Record policy with the model.** Deploy class order, calibrator, thresholds and unknown behavior as one versioned contract. Monitor changes in class prevalence and input representation. The threshold fixture demonstrates that the same score can lead to different actions under explicit policies; it does not claim to calibrate an actual model.

## Why

A message about an unsupported product gets a high softmax score because the model must compare only three familiar classes. Raising the threshold may still accept it incorrectly.

## Worked Case

A message about an unsupported product gets a high softmax score because the model must compare only three familiar classes. Raising the threshold may still accept it incorrectly.

## Risk

Treating cosine similarity or a softmax maximum as a universal confidence measure can defeat the unknown route.

## Trade-off

More rejection can reduce incorrect accepted decisions while lowering useful coverage; evaluate both sides.

## Try This

Plot held-out reliability and precision-recall slices, then add unknown messages and measure accepted-case error plus coverage.

## Follow-ups

### Does temperature scaling fix every distribution shift?

No. It adjusts score calibration under a fitted procedure; it does not create missing features, correct labels or guarantee calibration after a new shift.

### Can two systems share one threshold?

Only if score semantics and validation justify that policy. Different encoders and heads can produce incomparable score distributions.

## Citations

- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do you build multilabel and hierarchical classifiers when one input can have several valid labels?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Represent the target contract explicitly.** Multiclass labels are mutually exclusive under a chosen taxonomy; multilabel outputs can include several categories. A hierarchy adds parent-child relationships and may permit a broad parent label when a specific leaf cannot be justified. These are different constraints from simply returning several free-text strings.

**Choose the training and decoding design together.** Independent binary heads provide a straightforward multilabel baseline, but label correlations and mutually exclusive combinations may need further modeling or constrained decoding. Select thresholds per label where justified, and ensure a child prediction satisfies required parent rules. Do not silently discard a secondary intent just because a downstream API expects one label.

**Evaluate the appropriate unit.** Exact-set accuracy requires the whole predicted set to match and can be harsh when many labels exist. Per-label precision/recall, macro averages and hierarchical error categories reveal different weaknesses. Split correlated records safely and account for sparse labels that have too few examples for stable estimates.

**Define abstention and user experience.** A router may ask which of two valid intents to handle first, while a tagging service may retain both. An LLM can propose a structured label list, but the application still validates allowed labels and hierarchy rules. The example decodes synthetic per-label scores and enforces a parent relationship without pretending those scores are calibrated probabilities.

## Why

A message reports both an incorrect invoice and a locked account. Returning only billing loses a real support issue; returning an unsupported free-text label breaks the routing contract.

## Worked Case

A message reports both an incorrect invoice and a locked account. Returning only billing loses a real support issue; returning an unsupported free-text label breaks the routing contract.

## Risk

Forcing multilabel data into a single-label target can produce apparent evaluation errors that are actually taxonomy errors.

## Trade-off

Independent heads are simple but need explicit treatment of label dependencies and invalid combinations.

## Try This

Write a taxonomy with two parents and several leaves. Test multi-intent input, unsupported labels and a child without its required parent.

## Follow-ups

### Should a hierarchy always use separate models at each level?

Not necessarily. Compare a flat head with constrained decoding, staged models and a joint design under the same task metrics and error costs.

### Can I reuse multiclass softmax for independent labels?

A softmax forces competition with a sum-to-one constraint. Independent labels usually need a different objective or decoding design.

## Citations

- https://scikit-learn.org/stable/supervised_learning.html
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How can class descriptions or labeled examples turn embeddings into a zero-shot or few-shot classifier?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**An encoder supplies vectors; a decision rule supplies labels.** Embed an input and compare it with vectors for class descriptions or representative labeled examples using a consistent model and preprocessing. Selecting the nearest description is a zero-shot-style prototype method; averaging labeled training vectors per class gives a simple few-shot prototype baseline.

**Treat descriptions as model inputs.** A vague class name may not express the actual inclusion and exclusion rules. Compare reviewed descriptions and multiple examples on validation data, keep their versions and avoid choosing them by test performance. Normalize only according to the intended cosine or dot-product geometry, and reject invalid or zero vectors.

**Do not reinterpret similarity as probability.** A top class can still be wrong or outside scope. Evaluate top-score and margin thresholds using known, ambiguous and unknown cases. A multimodal class can require several prototypes because one mean vector may fall between distinct subgroups. More examples can help only if their labels and representativeness are sound.

**Compare to learned heads.** A lightweight supervised classifier on frozen vectors can outperform description matching when labeled data is available. The optional lab encodes actual synthetic messages with a pinned sentence-transformer and evaluates a learned head and description matching separately; the miniature prototype calculation uses declared numeric vectors to explain the rule, not fabricated neural output.

## Why

Two descriptions both mention payment, but one includes failed charges and the other refunds. A semantically broad encoder may need more explicit descriptions or labeled examples to separate the task boundary.

## Worked Case

Two descriptions both mention payment, but one includes failed charges and the other refunds. A semantically broad encoder may need more explicit descriptions or labeled examples to separate the task boundary.

## Risk

A nearest-description method always returns one known label unless its unknown policy is implemented and validated.

## Trade-off

Prototype methods are easy to extend with new labels, while supervised heads can better fit existing task boundaries with representative labels.

## Try This

Compare label names, detailed descriptions and training-only class prototypes on the same held-out and unknown messages.

## Follow-ups

### Is zero-shot classification necessarily a generative LLM call?

No. Description matching can use an embedding encoder; another approach uses natural-language inference; a generative model can also choose labels from a prompt. Their mechanisms and costs differ.

### Can one class have several prototypes?

Yes. Several reviewed prototypes can represent submodes, but their aggregation and thresholds need validation to avoid favoring a class merely because it has more prototypes.

## Citations

- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# When should you train a supervised classifier on frozen embeddings instead of fine-tuning the encoder?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A frozen encoder is a representation service.** Compute versioned training vectors and fit a small head such as logistic regression or a linear support vector classifier. This can be efficient when labels distinguish concepts the representation already separates. Keep the mapping from row identifiers to vectors and labels auditable, and never mix incompatible encoder revisions in one feature matrix.

**Evaluate data efficiency and serving cost.** Reusing cached vectors reduces repeated encoding during head tuning, but the cache key must include the exact input and representation contract. Fit the head only on training labels; select regularization and thresholds on validation. Measure encoding and head latency separately, since a tiny head does not eliminate encoder cost.

**Fine-tune only for a demonstrated gap.** If the frozen representation consistently confuses task-critical distinctions, supervised adaptation may help. It also adds optimization choices, overfitting risk and a new embedding version requiring downstream rebuilds. With few labels, compare simple heads, prototypes and parameter-efficient or contrastive methods instead of assuming full fine-tuning is necessary.

**Keep deployment compatible.** Ship the encoder revision, normalization policy, feature dimension, head coefficients, class order and thresholds as one artifact. A head trained on one vector space cannot safely consume another merely because their dimensions match. The optional lab fits an actual head on real encoder outputs; it does not fine-tune the encoder.

## Why

A classifier trained on encoder A receives vectors from encoder B with the same dimension. Shape checks pass while label quality collapses because the coordinate meanings changed.

## Worked Case

A classifier trained on encoder A receives vectors from encoder B with the same dimension. Shape checks pass while label quality collapses because the coordinate meanings changed.

## Risk

Dimension equality is not representation compatibility, and cached vectors can silently preserve obsolete preprocessing.

## Trade-off

A frozen head is cheap to retrain; encoder adaptation can improve task geometry while increasing training and migration work.

## Try This

Change the encoder revision or preprocessing fingerprint and verify the serving layer rejects an incompatible head/vector pair.

## Follow-ups

### Can I fit PCA before splitting embedding rows?

That uses held-out distribution information in the fitted transform. Fit learned transforms inside the declared training procedure unless a transductive evaluation explicitly permits otherwise.

### Does using a pretrained encoder avoid every leakage concern?

No. Pretraining contamination may be unknown, and task-specific tuning, label descriptions and duplicate data can still leak evaluation information.

## Citations

- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- https://scikit-learn.org/stable/modules/linear_model.html

# What do contrastive fine-tuning and SetFit change compared with training only a classification head?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Contrastive learning adapts representation geometry.** It trains embeddings so selected related examples become closer and selected different examples become more separable under a loss. Positive and negative pair construction defines what related means; bad pairs can teach the wrong distinction even when the training loss decreases.

**SetFit combines representation adaptation with a classifier.** Its approach uses a sentence-transformer representation, task-derived contrastive examples and a classification stage. It is not the same as merely embedding a label name, nor is every implementation equivalent to full generative-LLM fine-tuning. Check the actual library version and training configuration before interpreting results.

**Evaluate under a realistic label budget.** Use held-out groups, repeated seeds and a fixed sampling policy when comparing few-shot methods. Keep test labels out of pair mining, prompt selection and representation training. Compare against frozen prototypes and a frozen-vector linear head using the same available labeled examples.

**Plan representation changes.** Adaptation changes vectors, so previously cached prototypes, indexes and heads may need regeneration. Record base revision, pair/mining policy, training data version and resulting artifact. The chapter's executed lab demonstrates frozen representations only; fine-tuning is an explicit extension rather than an unmeasured result claimed by that lab.

## Why

A pair miner labels two negated and non-negated statements as similar based only on shared vocabulary. Fine-tuning can make a task-critical error more systematic while improving its own pair loss.

## Worked Case

A pair miner labels two negated and non-negated statements as similar based only on shared vocabulary. Fine-tuning can make a task-critical error more systematic while improving its own pair loss.

## Risk

A tiny few-shot benchmark can be highly sensitive to which labeled examples and negative pairs were sampled.

## Trade-off

Task-specific geometry can improve accuracy but increases artifact management, overfitting checks and re-encoding cost.

## Try This

Specify positive/negative pair rules for a negation-sensitive task, then design an equal-label-budget comparison with frozen baselines.

## Follow-ups

### Is a lower contrastive loss enough to select the deployed model?

No. Select using held-out task metrics and failure slices, not only the optimization objective.

### Can adapted embeddings continue to share the old vector index?

Only if compatibility is explicitly established, which should not be assumed. Normally version and rebuild the affected representations.

## Citations

- https://huggingface.co/docs/setfit/index
- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html

# How do generative LLM classification and natural-language-inference classification differ from embedding matching?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Generative classification asks a model to produce a label.** Provide an explicit taxonomy, examples, unknown behavior and a constrained output contract. The model may still emit an unsupported label or explanation. Parse and validate its output, bound retries and treat untrusted input text as data rather than instructions.

**Natural-language-inference classification scores entailment-like relations.** An input is paired with a hypothesis derived from a candidate label. Template wording and label competition affect the decision. This is not the same as cosine matching of independently encoded texts, even when a large pretrained transformer is involved.

**Compare whole systems.** Hold label definitions and test cases constant across generative, inference-based, embedding and lexical approaches. Count latency, token cost, invalid outputs, refusal behavior and evidence-sensitive errors. A generated explanation can sound persuasive without establishing that the label follows the task rules. Verbal confidence is not a calibrated probability.

**Constrain authority.** A routing label should select only permitted downstream behavior. A model saying admin or urgent cannot grant privileges. Include injection attempts and unsupported topics in the evaluation. The executable output validator checks an application contract using synthetic responses; the lab does not call a hosted generative model or claim measured generative accuracy.

## Why

An input includes a sentence telling the classifier to output a privileged label. A structured JSON result can be syntactically valid while violating the allowed taxonomy and authorization policy.

## Worked Case

An input includes a sentence telling the classifier to output a privileged label. A structured JSON result can be syntactically valid while violating the allowed taxonomy and authorization policy.

## Risk

Constrained formatting reduces some parsing errors but does not guarantee correct semantics or safe routing.

## Trade-off

Generative models can follow rich definitions with little task training, at potentially higher latency and per-request cost.

## Try This

Write a label prompt and validator, then compare methods on ambiguous, negated, unknown and instruction-injection cases.

## Follow-ups

### Can JSON schema replace a held-out classification test?

No. Schema validation checks shape and allowed values; correctness needs independent expected decisions.

### Should the model return a long chain of reasoning for every label?

Request only useful, bounded output such as a label and short evidence span when appropriate. Evaluate the decision independently of explanatory verbosity.

## Citations

- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- https://huggingface.co/docs/setfit/index

# How should active learning and LLM-generated labels improve a classifier without contaminating evaluation?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Treat generated labels as proposals.** A model can cheaply suggest labels or identify ambiguous examples, but its mistakes can be correlated and confident. Preserve label source, model/prompt version and review state. Do not silently mix weak labels with independently verified targets and then report all of them as ground truth.

**Select examples intentionally.** Active learning can prioritize uncertainty, model disagreement, uncovered classes or representative regions. Uncertainty sampling alone may overselect malformed noise and miss confident systematic errors. Reserve a random or coverage-oriented audit stream to observe what the selection policy ignores.

**Keep the evaluation boundary independent.** Human-reviewed active-learning examples become training or validation data under a defined policy. A frozen test set should not become a queue of examples repeatedly relabeled and tuned against until scores improve. Measure performance on a fresh independent slice and record the effective label budget, including review cost.

**Use distillation carefully.** A smaller classifier trained on a larger model's outputs learns that teacher's behavior, including its biases and blind spots. Compare the student against independent task labels and relevant error costs, not only agreement with the teacher. The code fixture tracks label provenance and blocks an inferred label from replacing a reviewed one; no automatic labeling quality is asserted.

## Why

A teacher model labels every unfamiliar category as the majority class. A student trained on those labels agrees with the teacher but fails real minority examples that neither system reviewed.

## Worked Case

A teacher model labels every unfamiliar category as the majority class. A student trained on those labels agrees with the teacher but fails real minority examples that neither system reviewed.

## Risk

Teacher agreement and training loss can improve while actual task quality remains unchanged or worse.

## Trade-off

Weak labels reduce initial annotation cost but require audit, filtering and independent quality checks.

## Try This

Design an acquisition batch combining uncertain, disagreement and random examples. Record review effort and an untouched evaluation plan.

## Follow-ups

### Can model disagreement identify every error?

No. Models sharing data or representations can agree on the same incorrect label. Independent sampling and reviewed task evidence remain necessary.

### Should a human correction overwrite the original weak label?

Preserve its history and mark the current reviewed target. This supports audits and avoids losing information about systematic labeling failures.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://scikit-learn.org/stable/supervised_learning.html

# How do you serve and monitor a classifier when labels, embeddings or class prevalence change?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Version the decision bundle.** Keep taxonomy, representation, model/head, calibrator, thresholds and unknown policy compatible. A label rename can break downstream consumers even when the numerical predictor is unchanged. A new class may require new training data, label descriptions, thresholds and routing behavior, not only a configuration string.

**Separate input drift from performance evidence.** Changes in vector distributions or class proportions are diagnostic signals. They do not prove that accuracy changed without trustworthy labels. Monitor invalid inputs, unknown rates, latency, class frequencies and delayed reviewed outcomes, including minority slices and source changes.

**Roll out with reconciliation.** Shadow or canary a candidate, compare paired outcomes and preserve a rollback artifact. Keep per-record representation identities so cached vectors cannot silently feed the wrong head. If retraining uses new labeled feedback, preserve time and group boundaries and avoid turning old tests into training data while still calling them held out.

**Design an actionable fallback.** Use manual review, a simpler baseline or a bounded unsupported response according to the task. An unavailable encoder should not fabricate zero vectors and return a confident default class. The compatibility fixture demonstrates a version guard, while real throughput and drift response remain deployment exercises.

## Why

An embedding service upgrades its model alias while the classifier head remains unchanged. Predictions still return valid label strings, so only a representation contract check or outcome monitoring reveals the mismatch.

## Worked Case

An embedding service upgrades its model alias while the classifier head remains unchanged. Predictions still return valid label strings, so only a representation contract check or outcome monitoring reveals the mismatch.

## Risk

A silent fallback can preserve apparent availability while systematically routing messages to the wrong workflow.

## Trade-off

Strict compatibility checks may reject traffic during an incomplete rollout, motivating atomic artifact promotion and a deliberate fallback.

## Try This

Deploy a mismatched head/encoder fixture and verify rejection, then design a canary dashboard with delayed-label metrics.

## Follow-ups

### Does a class-prior shift always require a new encoder?

No. Depending on the task, recalibration, threshold changes or head retraining may be enough. Diagnose the changed assumption before rebuilding every layer.

### Can the system automatically retrain on all user ratings?

Ratings may reflect satisfaction, latency or an unwanted correct decision. Review label meaning and sampling before treating feedback as supervised truth.

## Citations

- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do you compare classification algorithms under an equal quality, latency and labeling budget?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Choose a baseline ladder based on the task.**

| Approach | Useful starting point | Main concern to measure |
| --- | --- | --- |
| Reviewed rules | Exact, stable patterns | Coverage and maintenance |
| Sparse lexical classifier | Known text labels with sufficient examples | Vocabulary and source drift |
| Frozen embedding head | Semantic paraphrases under a stable taxonomy | Encoder cost and representation fit |
| Adapted encoder | Task-critical distinctions missed by frozen features | Label budget, overfitting and migration |
| Generative LLM | Rich label definitions and examples | Invalid output, latency and cost |

**Freeze the comparison contract.** Use the same taxonomy, split, known/unknown cases and independent scoring. Count label creation and prompt tuning as part of the budget. A generative system with extensive hand-written examples is not fairly described as having no task-development cost compared with a small trained model.

**Measure end-to-end serving.** Include encoding, tokenization, retrieval of examples, validation and fallback rather than timing only the final decision head. Report batch and single-request behavior separately, warm-up conditions and resource limits. A local tiny-fixture duration cannot justify a production service-level target.

**Make the tradeoff reviewable.** Report per-class quality, calibration, abstention coverage, invalid-output rate, update cost and operational dependencies. Use paired cases and uncertainty estimates where appropriate. The accompanying lab supplies reproducible classical and frozen-embedding comparisons; hosted LLM and fine-tuning costs are deliberately unmeasured until a learner runs that extension.

## Why

A team compares a cached embedding head with an uncached generative call and omits encoder latency from the first system. The resulting speed claim compares different serving boundaries.

## Worked Case

A team compares a cached embedding head with an uncached generative call and omits encoder latency from the first system. The resulting speed claim compares different serving boundaries.

## Risk

Benchmarking mismatched splits, label budgets or timing scopes can favor the preferred architecture without evidence.

## Trade-off

A more expensive model is justified only when its measured task improvement is valuable under actual constraints.

## Try This

Create a comparison table with label effort, macro-F1, accepted error, coverage, p95 latency and per-request cost for each candidate.

## Follow-ups

### Should the best average score always win?

No. Hard constraints such as unsupported-class handling, authorized data access, update latency or error cost can rule out an otherwise high average.

### What if a simple lexical model wins?

Deploying the simpler measured solution is a valid result. Keep semantic methods as evaluated alternatives rather than assuming a newer representation must outperform it.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html

# How do you explain a classifier decision without confusing feature attribution with supporting evidence?

<!-- meta
answer_format: conceptual
domain: classification
subdomain: classification
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Separate three explanation questions.** Which computation influenced this model output? Which source information supports the intended label? Which change would alter the decision? Coefficients, tree paths, retrieved neighbors and attribution methods can help answer parts of these questions, but none automatically proves the label is true or causally justified.

**Choose a faithful explanation boundary.** A linear model can expose feature contributions under its exact preprocessing, while a nearest-neighbor model can show authorized reference examples. Embedding coordinates are not usually individually named concepts. A generative model can write a plausible story for any supplied label, so test whether its claimed evidence actually occurs in the input and relates to the taxonomy.

**Investigate errors with controlled changes.** Compare original and minimally changed examples, including negation, missing fields, unfamiliar phrasing and irrelevant text. Sensitivity can reveal brittle behavior but is not a general causal estimate. Preserve the model, representation and threshold versions so a decision can be reproduced rather than explained using a newer model.

**Respect privacy and uncertainty.** Do not disclose a training neighbor or private source merely because it makes the explanation convincing. Offer a bounded reason, relevant evidence and a correction or review path. An attribution artifact and a calibrated probability have different meanings. The output-validation fixture checks allowed labels and evidence identifiers; no generated explanation is treated as an independent oracle.

## Why

A model predicts delivery, then a generated explanation cites a sentence that was never present. The label may even be correct, but the explanation still fails its evidence contract.

## Worked Case

A model predicts delivery, then a generated explanation cites a sentence that was never present. The label may even be correct, but the explanation still fails its evidence contract.

## Risk

A fluent post-hoc explanation can hide unsupported assumptions or reveal private reference examples.

## Trade-off

Detailed diagnostics help debugging; user-facing explanations should remain relevant, authorized and honest about uncertainty.

## Try This

Compare an input and a negated variant, inspect model behavior and reject explanations containing unsupported evidence references.

## Follow-ups

### Does an attribution score show a feature caused the real-world outcome?

No. It describes a model under a particular method and input baseline. Causal claims require a separate intervention and identification design.

### Can explanations replace accuracy evaluation?

No. A model can explain a consistently wrong rule clearly. Evaluate decisions, probabilities, evidence and explanation fidelity separately.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html
- https://scikit-learn.org/stable/modules/linear_model.html
