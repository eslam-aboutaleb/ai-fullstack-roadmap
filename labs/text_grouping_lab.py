"""CPU classification and clustering: classical models and optional real embeddings.

Classical: install numpy==2.0.2 scikit-learn==1.9.1, then run this file.
Embeddings: install requirements-text-models.txt and add --embeddings.
The embedding mode downloads a pinned public encoder on its first run.
Fixtures are tiny and synthetic; results are execution evidence, not benchmarks.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.cluster import (AgglomerativeClustering, DBSCAN, HDBSCAN,
                             KMeans, MiniBatchKMeans, SpectralClustering)
from sklearn.datasets import load_wine, make_blobs, make_moons
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, f1_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

ENCODER = 'sentence-transformers/all-MiniLM-L6-v2'
REVISION = '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
# Labels define this fixture only. No label enters a clustering fit call.
TRAIN = {
    'billing': ['The invoice contains a duplicate charge', 'Please refund the extra payment',
                'I was billed twice for one purchase', 'The payment amount on my bill is incorrect',
                'There is an unexpected fee on the invoice', 'Please correct the charge on my account'],
    'access': ['I cannot log in to my account', 'My password reset link expired',
               'The sign in page rejects my password', 'My account is locked and I need access',
               'I forgot my login password', 'I cannot complete account authentication'],
    'delivery': ['The shipment has not arrived', 'Please track my missing package',
                 'My parcel was delivered to the wrong address', 'The courier lost my shipment',
                 'The delivery is late and tracking has stopped', 'When will my package reach my address']}
TEST = [('I see two payments for the same order', 'billing'), ('Please remove the incorrect fee', 'billing'),
        ('My bill has a charge I did not expect', 'billing'), ('I forgot how to sign in', 'access'),
        ('Please unlock my account', 'access'), ('The reset password page does not work', 'access'),
        ('The courier has not brought my parcel', 'delivery'), ('Where is my shipment now', 'delivery'),
        ('My package is still missing', 'delivery')]
DESCRIPTIONS = ['A payment, invoice, refund or incorrect charge problem',
                'A login, password, authentication or account access problem',
                'A parcel, courier, shipment, tracking or delivery problem']
CLASSES = list(TRAIN)
TEXTS = [text for label in CLASSES for text in TRAIN[label]]
LABELS = np.array([label for label in CLASSES for _ in TRAIN[label]])
TEST_TEXTS, TEST_LABELS = zip(*TEST)


def partition_metrics(x, labels, audit):
    """Keep excluded noise visible; undefined silhouette stays null."""
    labels = np.asarray(labels)
    keep = labels != -1
    groups = len(set(labels[keep]))
    sil = float(silhouette_score(x[keep], labels[keep])) if 1 < groups < int(keep.sum()) else None
    return dict(groups=groups, noise=int((~keep).sum()), silhouette_without_noise=sil,
                audit_ari_including_noise=float(adjusted_rand_score(audit, labels)))


def classical():
    wine = load_wine()
    train, test = train_test_split(np.arange(len(wine.target)), test_size=0.3,
                                   stratify=wine.target, random_state=17)
    classifiers = {
        'logistic': make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=17)),
        'forest': RandomForestClassifier(n_estimators=80, max_depth=5, random_state=17),
        'svc': make_pipeline(StandardScaler(), SVC(C=1.0)),
        'neighbors': make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))}
    scores = {}
    for name, model in classifiers.items():
        model.fit(wine.data[train], wine.target[train])
        pred = model.predict(wine.data[test])
        scores[name] = float(f1_score(wine.target[test], pred, average='macro'))
    # All vocabulary learning happens inside the training-only pipeline.
    lexical = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=1000, random_state=17))
    nb = make_pipeline(CountVectorizer(), MultinomialNB(alpha=1.0))
    for name, model in [('tfidf_logistic', lexical), ('count_nb', nb)]:
        model.fit(TEXTS, LABELS)
        scores[name] = float(f1_score(TEST_LABELS, model.predict(TEST_TEXTS), average='macro'))
    x, audit = make_blobs(n_samples=120, centers=3, cluster_std=0.55, random_state=17)
    # Unsupervised fits receive x only. Audit labels are used afterward.
    algorithms = {'kmeans': KMeans(n_clusters=3, n_init=10, random_state=17),
                  'minibatch': MiniBatchKMeans(n_clusters=3, n_init=3, batch_size=30, random_state=17),
                  'dbscan': DBSCAN(eps=0.65, min_samples=4),
                  'hdbscan': HDBSCAN(min_cluster_size=8),
                  'ward': AgglomerativeClustering(n_clusters=3),
                  'gmm': GaussianMixture(n_components=3, reg_covar=1e-6, random_state=17),
                  'spectral': SpectralClustering(n_clusters=3, affinity='nearest_neighbors', n_neighbors=12, random_state=17)}
    partitions = {name: partition_metrics(x, estimator.fit_predict(x), audit)
                  for name, estimator in algorithms.items()}
    curved, curve_audit = make_moons(n_samples=160, noise=0.05, random_state=17)
    partitions['moons_dbscan'] = partition_metrics(curved, DBSCAN(eps=0.22, min_samples=5).fit_predict(curved), curve_audit)
    reduced = PCA(n_components=2).fit_transform(StandardScaler().fit_transform(wine.data))
    partitions['wine_pca_kmeans'] = partition_metrics(reduced, KMeans(n_clusters=3, n_init=10, random_state=17).fit_predict(reduced), wine.target)
    assert all(np.isfinite(value) for value in scores.values())
    return dict(wine_train=len(train), wine_test=len(test), classification_macro_f1=scores, clustering=partitions)


def semantic():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(ENCODER, revision=REVISION, device='cpu', trust_remote_code=False)
    # Explicit truncation contract; this English fixture contains short texts.
    model.max_seq_length = 256
    def encode(texts):
        vectors = model.encode(list(texts), normalize_embeddings=True, batch_size=8,
                               show_progress_bar=False, convert_to_numpy=True)
        assert vectors.shape == (len(texts), 384) and np.isfinite(vectors).all()
        assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-4)
        return vectors
    train_x, test_x = encode(TEXTS), encode(TEST_TEXTS)
    head = LogisticRegression(max_iter=1000, random_state=17).fit(train_x, LABELS)
    pred = head.predict(test_x)
    prototypes = encode(DESCRIPTIONS)
    described = np.array(CLASSES)[(test_x @ prototypes.T).argmax(axis=1)]
    # The unknown similarities are diagnostics; no threshold is tuned on test labels.
    unknown = encode(['Explain the orbital mechanics of a distant planet'])
    all_x = np.vstack([train_x, test_x])
    groups = KMeans(n_clusters=3, n_init=10, random_state=17).fit_predict(all_x)
    audit = list(LABELS) + list(TEST_LABELS)
    representatives = {}
    all_texts = TEXTS + list(TEST_TEXTS)
    for group in sorted(set(groups)):
        idx = np.flatnonzero(groups == group)
        mean = all_x[idx].mean(axis=0)
        representative = idx[np.linalg.norm(all_x[idx] - mean, axis=1).argmin()]
        representatives[str(group)] = all_texts[int(representative)]
    assert set(pred) <= set(CLASSES)
    return dict(model=ENCODER, revision=REVISION, dimension=384, max_sequence_tokens=256,
                train=len(TEXTS), test=len(TEST_TEXTS),
                frozen_head_macro_f1=float(f1_score(TEST_LABELS, pred, average='macro')),
                description_match_macro_f1=float(f1_score(TEST_LABELS, described, average='macro')),
                predictions=list(map(str, pred)), unknown_description_similarities=unknown[0].dot(prototypes.T).tolist(),
                clustering=partition_metrics(all_x, groups, audit), representatives=representatives,
                scope='Tiny synthetic English fixture; frozen encoder; no fine-tuning or generative LLM calls. Clustering is transductive over these 27 messages; audit labels never enter fit.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--embeddings', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        result = dict(classical=classical())
        if args.embeddings:
            result['semantic'] = semantic()
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
