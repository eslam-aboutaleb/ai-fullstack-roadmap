# Classification and clustering chapters

Two chapters now follow model and prompting fundamentals and precede RAG. Their prerequisite links include machine-learning and model foundations; clustering additionally builds on classification and mathematics. Earlier study identifiers and chapter URLs are preserved.

The chapters contain four foundation questions, 32 detailed main questions and 64 follow-up answers. All 36 topics have assigned code examples across 22 new recipes, including an optional executable scikit-learn example. Each main question also has an answer-specific diagram. There is no authoring question-count cap.

## Classification

Covers binary/multiclass/multilabel/open-set contracts; logistic regression and softmax; Naive Bayes; trees, forests and boosting; support vector and nearest-neighbor methods; group/time leakage; imbalance and metrics; calibration, thresholds and rejection; hierarchical targets; embedding descriptions and prototypes; frozen-vector heads; contrastive adaptation and SetFit; generative and natural-language-inference labeling; active learning and weak labels; serving drift; fair system comparisons; and explanation fidelity.

## Clustering

Covers task and geometry definitions; Lloyd updates; K-means++ and mini-batches; DBSCAN core/border/noise; HDBSCAN and membership semantics; agglomerative linkages; Gaussian mixtures and responsibilities; spectral graph assumptions; neural embedding geometry; PCA/UMAP boundaries; choosing resolution; silhouette, adjusted Rand index and stability; LLM naming and representative selection; pair constraints; online assignment and novelty; scale, drift and group identity; and choosing discovery versus classification, retrieval or agents.

An embedding model encodes text. It does not choose labels or discover useful groups without a separate decision rule and evaluation. Generative LLM classification and cluster naming are explained with bounded output/evidence contracts; no hosted model calls or encoder fine-tuning are claimed.

## Executed lab

`labs/text_grouping_lab.py` has two modes:

```sh
python3.12 -m venv /tmp/roadmap-text-models
/tmp/roadmap-text-models/bin/python -m pip install -r requirements-text-models.txt
/tmp/roadmap-text-models/bin/python labs/text_grouping_lab.py
/tmp/roadmap-text-models/bin/python tests/check_text_models.py --embeddings
```

The optional embedding mode downloads a pinned public model on first use. It uses no provider credentials. The static site does not import these dependencies or download model weights.

Classical mode runs actual scikit-learn logistic, forest, support-vector and neighbor classifiers on the bundled 178-row wine dataset; lexical TF-IDF/logistic and count/Naive-Bayes pipelines on synthetic messages; and actual K-means, mini-batch, DBSCAN, HDBSCAN, Ward, Gaussian-mixture, spectral and PCA calculations on declared numeric datasets. Learned text vocabularies and supervised preprocessing use training data only.

Embedding mode uses `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, with CPU execution, normalized 384-dimensional vectors and an explicit 256-token limit. It fits a frozen-vector logistic head on 18 synthetic messages and evaluates nine separate messages. Description matching uses three separately encoded class descriptions. Clustering fits over all 27 message vectors without passing audit labels to the estimator; its agreement score is a transductive fixture diagnostic.

Recorded execution in `labs/text_grouping_result.json` reports lexical macro-F1 about 0.886, frozen-head and description-match macro-F1 of 1.0, and text-cluster audit ARI of 1.0. The corpus is tiny, synthetic, English and intentionally separable; these values do not establish production accuracy, statistical superiority, multilingual quality or out-of-domain detection. The unknown example records similarities without claiming an evaluated rejection threshold. The result is downloadable beside the lab in each chapter's practice section.

The pinned environment is NumPy 2.0.2, scikit-learn 1.9.1, PyTorch 2.14.1, Sentence Transformers 6.2.0 and Transformers 5.20.2. Optional checks execute the complete lab and estimator snippet. Core checks execute the standard-library miniatures, validate all declared identities and preserve downloadable source exactly. Independent technical review remains pending.

Validation passed: `make check` (58 chapters, 207 pages, 23,956 internal links, 1,171 chapter topics), final formatter/source/example checks, the pinned real-embedding lab and estimator example, root Chromium ordering/navigation/download checks and 33 automated accessibility checks.
