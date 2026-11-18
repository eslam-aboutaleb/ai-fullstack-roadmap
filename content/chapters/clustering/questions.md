<!-- chapter: clustering -->

# How does Lloyd's K-means algorithm work, and when is its objective a poor fit?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**K-means alternates assignment and update.** Choose k centers, assign each point to its nearest center under squared Euclidean distance, then recompute each center as the mean of its assigned points. Repeat until a stopping condition. Each exact step does not increase that objective, but the procedure can converge to a local solution rather than a unique global optimum.

**Understand what the objective favors.** Compact roughly centroid-shaped groups fit it better than curved, strongly unequal-density or arbitrary-shaped structures. Scaling changes which features dominate squared distance. Outliers can move means substantially. Empty groups need an explicit implementation policy rather than division by zero.

**Treat initialization and k as choices.** Compare several starts or a validated initialization method and inspect both objective and usefulness. Reducing within-cluster inertia by adding centers is expected and is not proof of a better business grouping. Cluster numbers are arbitrary identifiers, not semantic class names.

**Keep geometry honest for embeddings.** Standard K-means uses Euclidean means. Normalized input can relate Euclidean and cosine distances between points, but ordinary mean updates do not by themselves implement every spherical K-means variant. The standard-library chapter file runs actual Lloyd updates on declared numeric data and checks the resulting partition without pretending those points are neural embeddings.

## Why

Two curved groups lie close to one another. A centroid partition can slice across the curves even while reducing squared distance, so a lower objective does not prove the desired shape was found.

## Worked Case

Two curved groups lie close to one another. A centroid partition can slice across the curves even while reducing squared distance, so a lower objective does not prove the desired shape was found.

## Risk

A deterministic seed makes a run reproducible, not necessarily correct or globally optimal.

## Trade-off

K-means is scalable and interpretable through centers, while density or graph methods can fit different shapes at greater operational cost.

## Try This

Run several initializations, inject one far outlier and explain changes in centers, objective and membership.

## Follow-ups

### Why is the mean the update for this objective?

For a fixed assignment, the arithmetic mean minimizes the sum of squared Euclidean distances within each group. A different distance or objective can require another representative.

### Can K-means discover the true number of categories?

Not automatically. It partitions for a supplied k under an objective; category meaning and selection require separate evidence.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# What do K-means++ initialization and MiniBatchKMeans change, and what do they leave unsolved?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Initialization influences the local solution.** K-means++ spreads initial centers according to a distance-weighted sampling strategy rather than picking every center independently without reference to existing ones. It can improve practical starts, but does not transform every dataset into compact spherical groups or prove the semantic meaning of k.

**Mini-batches change the optimization tradeoff.** MiniBatchKMeans updates centers using subsets to reduce per-step work and support larger datasets. Results can differ from full-batch fitting, and batch ordering, size, stopping rules and random seed matter. Monitor convergence and representative groups rather than comparing only training speed.

**Bound the whole pipeline.** Tokenization and embedding can dominate clustering cost. Process inputs in bounded batches, persist vector identity and separate fitting from representation generation. An algorithm that fits vectors incrementally does not automatically make an upstream document parser streaming or memory-bounded.

**Validate change sensitivity.** Compare full and mini-batch results on the same manageable slice, inspect low-support groups and repeat under several orderings. For a changing stream, decide whether old center updates remain meaningful as the source population changes. The optional lab executes real full and mini-batch estimators; it does not claim a production-scale benchmark.

## Why

A million vectors fit through mini-batch updates, but an earlier step first loads every raw document and embedding into one Python list. The optimization has not fixed the actual memory bottleneck.

## Worked Case

A million vectors fit through mini-batch updates, but an earlier step first loads every raw document and embedding into one Python list. The optimization has not fixed the actual memory bottleneck.

## Risk

A faster fitting phase can conceal a worse partition or a still-unbounded representation stage.

## Trade-off

Mini-batches reduce fitting cost while introducing approximation and ordering sensitivity that need evaluation.

## Try This

Compare full and mini-batch clusters on a fixed slice and report partition stability, noise assumptions and peak memory for the complete path.

## Follow-ups

### Does K-means++ remove the need for multiple starts?

It improves initialization but does not eliminate all local-solution sensitivity. Use the installed estimator's explicit initialization settings and evaluate variability.

### Can partial_fit handle a new semantic domain without review?

It can update numerical state, but the task meaning and representation drift still need a versioning and validation policy.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# How does DBSCAN distinguish core points, border points and noise?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Density replaces a fixed number of groups.** DBSCAN, Density-Based Spatial Clustering of Applications with Noise, identifies core points with sufficiently populated neighborhoods under a distance radius. Reachable core regions form groups, nearby border points can attach, and remaining points are labeled noise. The exact neighbor-count convention is part of the implementation contract.

**Select radius and minimum support together.** A small radius can mark most points as noise; a large one can merge distinct regions. Feature scale and distance determine what that radius means. Datasets with different densities can require tradeoffs one global radius cannot satisfy. Border assignments can depend on traversal or tie behavior, so test reproducibility where it matters.

**Do not equate noise with bad data.** An outlier may be a rare valid topic, a new issue, a parser defect or an irrelevant record. Preserve it for review rather than discarding it as an algorithmic error. Report the fraction of noise and group sizes alongside any internal quality score.

**Account for computation.** Neighborhood search can become expensive in high-dimensional spaces, and some implementations can consume substantial memory for dense neighborhoods. The local fixture computes exact neighborhoods for a tiny dataset; the optional lab runs the real estimator and compares shape behavior without making a scale claim.

## Why

A rare but valid issue has too few neighbors to be a core region. Its noise label signals unsupported local density, not proof that the issue should be deleted or ignored.

## Worked Case

A rare but valid issue has too few neighbors to be a core region. Its noise label signals unsupported local density, not proof that the issue should be deleted or ignored.

## Risk

Tuning for a visually attractive result can hide an unacceptable fraction of excluded records.

## Trade-off

Density methods support irregular shapes and explicit noise, while parameter selection and high-dimensional neighborhoods can be difficult.

## Try This

Vary radius and minimum support, inspect core/border/noise cases and report both partition quality and excluded coverage.

## Follow-ups

### Must I provide the number of groups?

Not directly for DBSCAN. Radius, minimum support, representation and distance jointly determine the result.

### Can the same radius work for every embedding model?

No. Distance distributions change with model, normalization and task. Revalidate parameters after a representation change.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# How does HDBSCAN use a density hierarchy, and why is a membership score not a class probability?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**HDBSCAN explores density structure at multiple levels.** Hierarchical Density-Based Spatial Clustering of Applications with Noise builds and selects groups from a density hierarchy using support and stability-related choices. It can handle varying density more flexibly than one fixed DBSCAN radius, but still relies on representation, distance and tuning assumptions.

**Choose implementation semantics explicitly.** Libraries can differ in parameters, supported distances, prediction extensions and neighborhood conventions. Do not transfer a configuration by name alone between implementations. Minimum group size and minimum support influence noise, coarse versus fine groups and the persistence selected as meaningful structure.

**Interpret output within the algorithm.** A membership strength or persistence statistic does not mean the probability that a human-defined topic label is true. Inspect real examples, noise and ambiguous boundaries. An LLM-generated name cannot turn this statistic into a calibrated business confidence.

**Plan serving separately.** Fitting a density hierarchy and assigning a new record are different operations. Some implementations provide approximate prediction extensions; others require a separately designed assignment rule or refit. The optional lab uses scikit-learn's actual HDBSCAN on declared numeric fixtures and reports cluster/noise counts. It does not assert a deployed online predictor.

## Why

A group has a high membership strength but mixes two operationally different issues that the embedding model placed near each other. Algorithmic cohesion does not validate the proposed business label.

## Worked Case

A group has a high membership strength but mixes two operationally different issues that the embedding model placed near each other. Algorithmic cohesion does not validate the proposed business label.

## Risk

A convenient probability-like field name can encourage unsupported confidence claims and automatic routing.

## Trade-off

Density hierarchies offer flexible discovery but can be less straightforward to maintain online than a fixed-centroid model.

## Try This

Compare density parameters on the same data and define how a newly arriving point would be handled without inventing a native predict method.

## Follow-ups

### Does HDBSCAN always outperform DBSCAN?

No. Compare them on the actual geometry, noise policy and operating constraints. Flexibility adds choices rather than universal superiority.

### Can a tiny high-quality group be removed by a support threshold?

Yes. Minimum support encodes a resolution preference. Inspect whether rare topics matter before tuning them away.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# How do agglomerative clustering and linkage choices create a hierarchy?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Agglomerative clustering merges groups progressively.** Begin with individual points or initial groups, repeatedly merge according to a linkage rule, and obtain a hierarchy that can be cut at a distance or group count. The hierarchy reveals relationships at several resolutions, but its merge rule defines what close means between groups.

**Linkages have different failure modes.** Single linkage can connect groups through a thin chain. Complete linkage emphasizes farthest pair distances and can favor tighter groups. Average linkage aggregates pairwise distances. Ward linkage targets an increase in within-group variance and has Euclidean assumptions; it is not a generic option for every precomputed cosine matrix.

**Choose the cut using the use case.** A dendrogram is useful for review, but a dramatic visual gap does not establish a true taxonomy. Evaluate stability, support, useful granularity and whether the hierarchy tracks a relevant task distinction. Constraints or sparse connectivity can reduce computation and change which merges are allowed.

**Plan resource and update behavior.** Pairwise structures can be costly at large n, and adding new data may require refitting rather than extending a fixed history transparently. Preserve model and corpus versions if users refer to groups. The optional lab runs Ward agglomeration on scaled numeric fixtures; a local linkage calculation illustrates why single-link chaining can differ from complete-link compactness.

## Why

A chain of bridge points connects two dense regions. Single linkage may merge them at a small distance even when their farthest members are far apart.

## Worked Case

A chain of bridge points connects two dense regions. Single linkage may merge them at a small distance even when their farthest members are far apart.

## Risk

Choosing Ward with an incompatible distance or interpreting a hierarchy as causal structure gives misleading results.

## Trade-off

Hierarchies support exploration at multiple resolutions but can cost more memory and complicate online updates.

## Try This

Compare single, complete, average and Ward on a bridged fixture, documenting distance compatibility and the chosen cut.

## Follow-ups

### Are the integer group labels stable across cuts?

No. They are implementation identifiers under a specific cut and fit. Preserve versioned membership or match groups explicitly across runs.

### Can a dendrogram replace evaluation labels?

It supports inspection, not an independent truth standard. Use reviewed task criteria and stability evidence for the intended purpose.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# What does a Gaussian mixture model optimize, and how do soft assignments differ from K-means?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A mixture is a probabilistic density model.** A Gaussian mixture model, or GMM, describes observations using weighted Gaussian components. Expectation-maximization alternates computing responsibilities under current parameters and updating component weights, means and covariances. A responsibility is conditional membership under the fitted model, not proof of a real-world category.

**Covariance changes the geometry and cost.** Spherical, diagonal, tied or full covariance assumptions give different flexibility and parameter counts. Poor initialization, too many components or near-singular covariance can create unstable solutions. Regularization and representative data are necessary for fitting and interpretation.

**Select complexity and inspect assumptions.** Information criteria such as AIC, Akaike Information Criterion, or BIC, Bayesian Information Criterion, compare fitted density models under their assumptions and parameter penalties. They do not certify semantic topic quality. A component can split one human topic into several density modes or mix topics with similar representations.

**Evaluate uncertainty in scope.** Soft assignment can represent overlapping density explanations, while hard K-means picks one nearest center. Neither automatically handles unknown business categories. The local probability calculation normalizes declared component likelihoods; the optional lab fits a real regularized mixture and records its selected grouping without claiming a semantic posterior.

## Why

One elongated population is split into two components because that improves density fit. Counting components as the true number of user intents would confuse a statistical approximation with a task taxonomy.

## Worked Case

One elongated population is split into two components because that improves density fit. Counting components as the true number of user intents would confuse a statistical approximation with a task taxonomy.

## Risk

A responsibility near one can be confident under a misspecified mixture while still wrong for the intended interpretation.

## Trade-off

Mixtures model soft density membership with more parameter and fitting complexity than a simple centroid partition.

## Try This

Fit several covariance choices, inspect singularity sensitivity and compare information criteria with actual representative examples.

## Follow-ups

### Is GMM equivalent to K-means?

They are related under restrictive equal spherical-covariance and hard-assignment limits, but a general fitted mixture has a different objective and uncertainty model.

### Does BIC choose the correct business labels?

No. It compares density-model fit and complexity under assumptions, not whether the resulting groups match product concepts.

## Citations

- https://scikit-learn.org/stable/modules/mixture.html

# When does spectral clustering help, and what risks come from the similarity graph?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Spectral methods use graph structure.** Build an affinity graph between examples, derive a graph-Laplacian representation and cluster a spectral embedding. This can reveal nonconvex relationships that a simple Euclidean centroid partition misses. The graph construction is part of the model, not an incidental preprocessing detail.

**Control neighbors and affinity scale.** Too few edges can disconnect related regions; too many or overly broad similarities can wash away meaningful separation. A dense n-by-n matrix can become the memory bottleneck before eigensolving begins. Sparse neighbor graphs help, but approximation and graph connectivity need evaluation.

**Respect mathematical conventions.** Affinity and distance matrices are not interchangeable. Symmetry, nonnegative weights and normalization choices matter for the selected formulation. Negative cosine values or asymmetric approximate-neighbor edges may require a deliberate transformation rather than being passed blindly as an affinity.

**Match the algorithm to scale and use.** Spectral clustering can be valuable for moderate-sized structures where graph connectivity captures the task, while minibatch centroid or density methods may be easier to operate for very large streams. New-point assignment is not automatically provided by a fit-time spectral partition. The optional lab executes a real spectral estimator on a small numeric fixture; it does not claim scalable graph processing.

## Why

Two interleaving curved groups are separable by local connectivity. A graph with shortcuts between the curves destroys that signal even though the spectral solver runs successfully.

## Worked Case

Two interleaving curved groups are separable by local connectivity. A graph with shortcuts between the curves destroys that signal even though the spectral solver runs successfully.

## Risk

A visually compelling partition can be an artifact of the graph bandwidth or neighbor count rather than a stable grouping.

## Trade-off

Graph methods capture rich connectivity while adding memory, affinity and serving-design choices.

## Try This

Vary neighbor count on a curved fixture and inspect connected components, quality and memory before choosing the spectral approach.

## Follow-ups

### Can I use a distance matrix as a precomputed affinity?

Not without a valid conversion. Large distances mean dissimilarity, while strong affinities usually mean connection; reversing that interpretation corrupts the graph.

### Does the spectral step automatically choose k?

Not in general. Many practical estimators still require a supplied group count or a separate selection procedure.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html

# How do you cluster sentence embeddings without confusing cosine geometry, normalization and topic meaning?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Record the exact representation contract.** Encoder revision, input truncation, pooling, prompts and normalization determine vector meaning. A general sentence-similarity model may group writing style or broad subject instead of the task distinction. Use actual encoder output and inspect examples rather than treating hand-written vectors as evidence of semantic model performance.

**Choose geometry deliberately.** Cosine compares direction and ignores vector magnitude after normalization. Squared Euclidean distance between unit vectors has a fixed relationship to cosine similarity, but algorithm updates and group prototypes can change that relationship. Do not assume ordinary K-means on normalized inputs implements every spherical objective.

**Validate the grouping at several levels.** Check invalid vectors, duplicates and truncation first. Compare group representatives, boundaries, noise and stability under seeds or reasonable representation changes. If audit labels exist, withhold them from unsupervised fitting and report external agreement separately from internal geometry metrics.

**Keep model limits visible.** The optional local lab uses a pinned English sentence encoder with its declared sequence limit and real 384-dimensional outputs. It compares lexical and semantic methods on a tiny synthetic support corpus. Those results demonstrate execution, not a broad multilingual or production clustering claim. Unknown topics and long inputs remain explicit learner extensions.

## Why

Two messages share most vocabulary but differ in a decisive negation. A broad similarity encoder can place them together even when the intended analysis needs separate outcomes.

## Worked Case

Two messages share most vocabulary but differ in a decisive negation. A broad similarity encoder can place them together even when the intended analysis needs separate outcomes.

## Risk

A cluster named by an LLM can look semantically authoritative while reflecting an unsuitable embedding geometry.

## Trade-off

General encoders are convenient; task-adapted embeddings may improve distinctions but require reviewed training pairs and full revalidation.

## Try This

Inspect token truncation and compare lexical, general semantic and task-adapted representations using the same reviewed grouping question.

## Follow-ups

### Can I mix old and new embeddings in one fit?

Not just because dimensions match. Use compatible representation versions or recompute the affected vectors.

### Does normalization always improve clustering?

No. It discards magnitude, which may or may not carry useful information. Choose it based on the intended similarity and validate the result.

## Citations

- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- https://scikit-learn.org/stable/modules/clustering.html

# Should you reduce embedding dimensions with PCA or UMAP before clustering?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Separate compression from visualization.** Principal Component Analysis, or PCA, learns linear directions that explain variance under its fit. Uniform Manifold Approximation and Projection, or UMAP, constructs a nonlinear low-dimensional representation with neighborhood-related objectives. A two-dimensional view optimized for visualization is not automatically the best feature space for clustering.

**Fit and evaluate the complete pipeline.** For an inductive assignment task, fit learned transforms on the allowed training reference set and apply compatible transforms to new data where supported. For transductive exploratory analysis, state that the fit uses the complete analyzed corpus and do not claim independent future prediction. Record transform configuration and random state.

**Inspect distortion.** Dimensionality reduction can remove noise or make computation cheaper, but can also merge rare distinctions or create visually convincing islands. Compare neighborhoods and cluster stability in original and reduced spaces. A higher silhouette after projection may reflect the projection's geometry rather than a more useful semantic grouping.

**Preserve the serving artifact.** Keep the encoder, reducer and clusterer together; refitting a reducer changes the coordinate system. The optional lab includes a real PCA-based numeric comparison, while UMAP is a documented extension requiring its own dependency and validation. No executed UMAP or two-dimensional semantic truth claim is implied.

## Why

A projection makes three islands in a plot, but the original vectors show a continuous topic transition. Selecting three business categories from the picture alone overstates what the representation proves.

## Worked Case

A projection makes three islands in a plot, but the original vectors show a continuous topic transition. Selecting three business categories from the picture alone overstates what the representation proves.

## Risk

Using the visualization as an unquestioned clustering input can make an arbitrary display layout drive product decisions.

## Trade-off

Reduction lowers dimension and sometimes noise, at the cost of information loss and another fitted artifact.

## Try This

Compare original vectors, several PCA dimensions and a separately installed UMAP configuration with stability and source-example review.

## Follow-ups

### Should PCA preserve the highest-variance directions for every task?

High variance is not necessarily high task relevance. A low-variance direction can encode a rare but important distinction.

### Can I refit the reducer while retaining old cluster centers?

Not safely unless compatibility is established. The centers belong to the old coordinate system.

## Citations

- https://scikit-learn.org/stable/modules/decomposition.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do you choose the number of clusters without treating an elbow or silhouette peak as ground truth?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Selection reflects an intended resolution.** More groups reduce K-means inertia even if they fragment one useful topic into tiny pieces. An elbow is a heuristic interpretation of diminishing objective improvement, not a theorem establishing the true number of categories.

**Use several kinds of evidence.** Silhouette compares within-group and nearest-other-group distances under a selected geometry. It favors some shapes and requires a valid partition with enough distinct groups. Noise handling, singleton groups and sample selection affect the interpretation. Density methods may not accept k directly, but their parameters still determine effective resolution.

**Include stability and usefulness.** Repeat fitting under seeds, perturbations and reasonable sampling changes. Inspect whether group membership and representatives persist, not whether integer identifiers match. Review small and rare topics and whether the grouping supports an actual decision or exploration task.

**Avoid selecting on audit labels and claiming unsupervision.** If human labels help choose k or tune distance, that is a supervised model-selection input and should be reported. Preserve an independent audit set or use reviewed criteria without pretending the fit discovered an objective universal taxonomy. The local silhouette calculation illustrates its denominator and the optional lab reports diagnostic metrics only on valid partitions.

## Why

A dataset with two broad topics and several subtopics can support k=2 or k=6 for different analysis needs. One geometric score cannot decide the required product granularity by itself.

## Worked Case

A dataset with two broad topics and several subtopics can support k=2 or k=6 for different analysis needs. One geometric score cannot decide the required product granularity by itself.

## Risk

A single optimal-looking score can hide unstable memberships, tiny groups or lost rare topics.

## Trade-off

A smaller partition is easier to review; a finer one can reveal useful subtopics while increasing ambiguity and maintenance.

## Try This

Compare candidate resolutions using inertia, valid silhouette, stability, group support and a written usefulness criterion.

## Follow-ups

### Can silhouette be computed when everything belongs to one group?

A meaningful standard silhouette needs at least two groups and fewer groups than points. Report an undefined diagnostic rather than inventing a score.

### Should noise be counted as one real topic?

Not automatically. Declare whether it is excluded from the metric and report noise coverage separately.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do adjusted Rand index, cluster stability and human review answer different evaluation questions?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**External agreement compares against labels.** Adjusted Rand Index, or ARI, compares pairwise partition agreement with a chance adjustment and is invariant to arbitrary cluster-number permutations. It requires a reference partition; agreement with a human label set measures that relationship, not the discovery of universal truth.

**Internal scores evaluate geometry.** Silhouette and related diagnostics do not need label names, but depend on the representation and shape assumptions. They cannot tell whether a compact group corresponds to the task's desired category. Report whether noise and singletons are included and whether the diagnostic is defined.

**Stability evaluates sensitivity.** Compare partitions on common examples across seeds, resamples, time windows or representations using suitable matching or permutation-invariant measures. Group numbers can switch while membership is unchanged. A stable partition can still be consistently useless, so stability is supporting evidence rather than task validation.

**Human review adds meaning and limits.** Inspect actual representatives, boundary cases, duplicate-heavy groups and outliers with a clear review rubric. Keep audit labels separate from unsupervised fitting and parameter selection where claiming independent evaluation. The local pairwise fixture checks permutation invariance; the optional lab computes actual adjusted Rand index from estimator outputs and withholds synthetic audit labels until after fitting.

## Why

One run calls a group 0 and another calls it 2, but every point has the same co-membership. Comparing raw identifier equality incorrectly reports instability.

## Worked Case

One run calls a group 0 and another calls it 2, but every point has the same co-membership. Comparing raw identifier equality incorrectly reports instability.

## Risk

A good internal score or stable grouping can still follow source formatting instead of a useful semantic distinction.

## Trade-off

External labels add task grounding but can bias selection if reused repeatedly; human review costs time and needs a consistent rubric.

## Try This

Relabel a partition with permuted IDs, compute ARI and inspect one stable but semantically irrelevant grouping.

## Follow-ups

### Can ARI be negative?

Yes. Its chance-adjusted interpretation allows values below zero for agreement worse than the reference chance model.

### Does a high ARI certify a topic name?

No. It measures partition agreement under given labels. Naming and evidence support require separate checks.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How should an LLM name or summarize clusters without changing membership or inventing a theme?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Use the model as a bounded description stage.** Fit the grouping first, choose representative source examples and provide an explicit naming task. Ask for a short theme, supporting identifiers and an ambiguous or mixed option. The model should not silently rewrite memberships to make its name look coherent.

**Select representatives beyond the nearest center.** Include central examples, meaningful variation, boundary cases and any exceptions. A single prototype can hide a mixed group. Limit context and redact or authorize private fields before disclosure. Retrieved text and embedded messages remain untrusted data; instructions inside them cannot redefine the naming task.

**Validate the returned artifact.** Check schema, allowed group identity, evidence references and whether cited examples actually support the proposed theme. Retain the model/prompt version and representative set. A plausible title is not an independent validation of the clustering algorithm, and repeated naming can produce different strings for the same membership.

**Preserve review and uncertainty.** Allow a reviewer to reject a misleading title or split a mixed group through a separate versioned workflow. Never turn a generated cluster name directly into an authorization or eligibility rule. The optional lab selects actual messages nearest their cluster mean as a representative heuristic, not as a guarantee of medoid optimality or complete coverage. The naming-output validator uses synthetic responses rather than claiming live LLM quality.

## Why

A group contains mostly access problems but also several payment failures. A model given only one central access example names the entire group account access and hides the mixture.

## Worked Case

A group contains mostly access problems but also several payment failures. A model given only one central access example names the entire group account access and hides the mixture.

## Risk

Fluent summaries can make an unstable or heterogeneous cluster appear authoritative.

## Trade-off

Generated names reduce review effort when evidence is representative, but need provenance and a mixed/unknown outcome.

## Try This

Choose central and boundary messages, request a constrained name and reject a response citing an example outside the group.

## Follow-ups

### Should generated titles determine the next fit labels?

Only under an explicit reviewed labeling process. Recycling unreviewed titles as truth can amplify an early grouping mistake.

### Can the LLM cluster every raw record directly?

Small exploratory tasks may permit it, but context limits, cost, reproducibility and unstable pair decisions need comparison with algorithmic baselines.

## Citations

- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- https://scikit-learn.org/stable/modules/clustering.html

# How do must-link constraints, cannot-link constraints and metric learning change unsupervised discovery?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Constraints introduce information about the desired grouping.** A must-link says selected examples should share a group; a cannot-link says they should not. They can represent reviewed domain evidence, but may conflict or become impossible under a chosen k. A general unconstrained estimator does not enforce them merely because you mention them in a prompt.

**Validate consistency and authority.** Must-link relationships can create transitive components. A cannot-link within one such component is a contradiction that must be resolved, not silently ignored. Keep source, reviewer and version metadata for each constraint and distinguish task knowledge from privacy or permission boundaries.

**Choose an actual constrained algorithm or adapt the representation.** Some methods modify assignment or optimization; metric learning changes the geometry using labeled pairs or triplets. That makes the resulting procedure supervised or semi-supervised in a meaningful sense. Keep training and audit evidence separated and evaluate whether the new geometry generalizes beyond the supplied pairs.

**Avoid fairness and identity shortcuts.** A constraint expressing one useful operational difference should not become an unreviewed rule for protected or unrelated attributes. Review what the model is being taught to separate and why. The local consistency fixture detects a direct contradiction in a tiny must-link component; it does not pretend ordinary K-means enforces a full constraint system.

## Why

Reviewed evidence says A must group with B, while another rule says A cannot group with B. No optimizer can satisfy both exactly without changing or rejecting one constraint.

## Worked Case

Reviewed evidence says A must group with B, while another rule says A cannot group with B. No optimizer can satisfy both exactly without changing or rejecting one constraint.

## Risk

Silent constraint violations or leaked audit pairs can produce a misleading claim of controlled unsupervised discovery.

## Trade-off

Domain constraints can improve useful separation while adding labeling effort, consistency checks and algorithm requirements.

## Try This

Create compatible and conflicting pair constraints, then state whether your selected estimator can enforce them or only use them for evaluation.

## Follow-ups

### Is constrained clustering still completely unsupervised?

No. It uses supervision in the constraints or learned representation. Describe the source and amount of that information explicitly.

### Can a cannot-link guarantee data access isolation?

No. Authorization needs an independent application boundary. Numerical cluster membership is not a security mechanism.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html
- https://huggingface.co/docs/setfit/index

# How do you assign new records to discovered clusters and detect a genuinely new topic?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Fit-time clustering and serving are separate contracts.** A centroid model can assign a new vector to a nearest center. A density or hierarchical method may lack the same native prediction rule, and an approximate prediction extension can have different semantics from refitting with the new point included.

**Add an unsupported path.** Nearest-center assignment always has a winner, even for a distant point. Validate a distance, support or other rejection criterion using known and novelty examples. One global radius may be inappropriate for groups with different spread. A rejected point is a candidate new topic or bad input, not automatically a new meaningful category.

**Collect and review novelty evidence.** Buffer rejected records under bounded retention, deduplicate them and inspect whether a persistent dense region emerges. Avoid creating a new topic for every unusual phrasing. A refit can split or merge old groups, so maintain a versioned mapping and communicate which historic assignments are fixed or recomputed.

**Preserve representation compatibility.** New vectors must come from the expected encoder and reducer. Detect missing or nonfinite features rather than assigning them to a default group. The code fixture implements an explicit nearest-center rejection policy on numeric points; the optional semantic lab reports description-based unknown scores without claiming a production novelty detector.

## Why

A message about an unsupported scientific topic is closest to one support cluster only because every known cluster is far away. A forced nearest-center assignment would misrepresent novelty as a familiar issue.

## Worked Case

A message about an unsupported scientific topic is closest to one support cluster only because every known cluster is far away. A forced nearest-center assignment would misrepresent novelty as a familiar issue.

## Risk

Blind assignment can hide emerging topics, while overly sensitive rejection creates an unmanageable novelty queue.

## Trade-off

Stable fixed centers simplify serving; refitting adapts to changes but can disrupt group identity and downstream consumers.

## Try This

Add known, boundary, distant and incompatible-representation examples. Specify accepted, rejected and refit-trigger outcomes.

## Follow-ups

### Does a new point change K-means centers automatically at predict time?

No. Prediction and fitting are distinct. Incremental updates require a chosen update method and can change the serving model.

### Can I call predict on every clustering estimator?

No. Check the actual estimator API and define an assignment design instead of assuming every fit result has the same online semantics.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html
- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html

# How do you operate clustering over millions of records while tracking drift and cluster identity?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Budget representation and fitting separately.** Stream or batch document extraction and encoding with explicit memory bounds, persist versioned vectors and choose a fitting method with acceptable complexity. Dense pairwise matrices can dominate memory at large n. Approximate graphs, mini-batch centers or representative sampling change the result and need evaluated tradeoffs.

**Version group identity.** Integer labels from one fit are not persistent business identifiers. Match old and new groups using overlap on common records, representative similarity and reviewed split/merge rules. One old group can become several new groups; forcing a one-to-one rename conceals that structural change.

**Monitor meaning as well as counts.** Track source mix, group sizes, noise, rejected assignments, representative drift and reviewed task usefulness. Distribution drift alone does not prove semantic deterioration. A model or reducer upgrade requires another representation generation rather than mixing incompatible coordinates.

**Define publication and rollback.** Build a candidate grouping, validate it and promote its manifest with compatible encoder, reducer and membership data. Preserve in-flight and historic references as required. The lab uses small local fixtures and does not establish million-record throughput; scaling and live drift response are explicit implementation exercises.

## Why

A refit swaps group numbers and splits one large group. A dashboard treating integer 2 as a permanent topic silently combines different meanings across time.

## Worked Case

A refit swaps group numbers and splits one large group. A dashboard treating integer 2 as a permanent topic silently combines different meanings across time.

## Risk

Comparing raw group IDs or mixing representation generations can create false trends and misleading operational alerts.

## Trade-off

Frequent refits adapt faster while increasing compute, identity reconciliation and review work.

## Try This

Design a candidate-generation manifest, memory budget and split/merge reconciliation procedure for an incrementally arriving corpus.

## Follow-ups

### Can I use only the largest clusters to monitor quality?

That can miss rare important issues and growing noise. Include support-aware review of small and novel regions.

### Does a cheaper approximate fit need a separate evaluation?

Yes. Compare its membership and usefulness with a manageable reference slice and report which approximation changed the result.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html
- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html

# How do you choose between classification, clustering, retrieval and an agentic workflow for a text task?

<!-- meta
answer_format: conceptual
domain: clustering
subdomain: clustering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Begin with the required output.**

| Need | Starting approach | Evidence needed |
| --- | --- | --- |
| Predict reviewed labels | Classification | Independent labeled evaluation |
| Discover recurring unknown themes | Clustering | Geometry, stability and representative review |
| Find passages for a query | Retrieval | Eligible evidence recall and answer support |
| Adaptively investigate with tools | Bounded agent | Verified outcomes and justified autonomy |

**Combine stages only when each has a role.** A discovery workflow can cluster an unlabeled corpus, ask reviewers or a bounded LLM to name representative groups, then create a labeled classification task for stable online routing. That transition needs a reviewed taxonomy and independent labels; raw cluster IDs should not automatically become production truth.

**Compare simple alternatives.** A lexical baseline may outperform semantic vectors on exact identifiers. An embedding head may be cheaper and more consistent than repeated generative calls for a stable taxonomy. A deterministic batch pipeline is often appropriate for encoding and fitting because the steps and retry rules are known.

**Define evidence for extra complexity.** Measure useful grouping or label quality, coverage, latency, annotation effort and operational cost. Keep authorization, data retention and irreversible effects outside model discretion. The local lab demonstrates algorithmic discovery and classification under separate contracts; it does not invoke an autonomous agent to choose labels or clustering parameters.

## Why

A team wants a dashboard of emerging complaints, not immediate routing. Clustering with review can explore that need, while a classifier would require a taxonomy that may not yet exist.

## Worked Case

A team wants a dashboard of emerging complaints, not immediate routing. Clustering with review can explore that need, while a classifier would require a taxonomy that may not yet exist.

## Risk

Using an agent to improvise every routine batch step increases uncertainty without necessarily improving the required outcome.

## Trade-off

A discovery-to-taxonomy-to-classifier path needs review work but separates exploration from repeatable serving.

## Try This

For routing, topic exploration, evidence search and repository diagnosis, choose the simplest execution model and state when you would change it.

## Follow-ups

### Can discovered clusters provide training labels directly?

They can supply weak-label candidates, but review and independent evaluation are needed before treating them as task truth.

### When would multiple agents help this workflow?

Potentially for independent investigations or review scopes with clear contracts. Parallel embedding workers are ordinary data processing and do not require autonomous agents.

## Citations

- https://scikit-learn.org/stable/modules/clustering.html
- https://scikit-learn.org/stable/supervised_learning.html
- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
