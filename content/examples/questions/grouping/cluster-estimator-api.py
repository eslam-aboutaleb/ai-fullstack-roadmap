"""Requires numpy==2.0.2 and scikit-learn==1.9.1; actual local estimators."""
import numpy as np
from sklearn.cluster import HDBSCAN,MiniBatchKMeans,SpectralClustering
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
from threadpoolctl import threadpool_limits
x,_ = make_blobs(n_samples=60,centers=3,cluster_std=0.2,random_state=17)
with threadpool_limits(limits=1):
    models=[MiniBatchKMeans(n_clusters=3,n_init=3,random_state=17),HDBSCAN(min_cluster_size=5),SpectralClustering(n_clusters=3,random_state=17)]
    for model in models:
        labels=model.fit_predict(x)
        assert labels.shape==(60,)
    reduced=PCA(n_components=1).fit_transform(x)
    assert reduced.shape==(60,1) and np.isfinite(reduced).all()
print('mini-batch, density hierarchy, spectral and PCA fits executed')
