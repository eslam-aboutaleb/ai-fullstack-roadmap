"""Optional CPU execution checks for the classification/clustering teaching lab."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def check(embeddings=False):
    for line in (ROOT/'requirements-text-models.txt').read_text().splitlines():
        if line and not line.startswith('#'):
            name, expected = line.split('==')
            assert importlib.metadata.version(name) == expected, name
    with tempfile.TemporaryDirectory(prefix='text-model-check-') as workspace:
        result = Path(workspace)/'result.json'
        command = [sys.executable, str(ROOT/'labs/text_grouping_lab.py'), '--output', str(result)]
        if embeddings:
            command.append('--embeddings')
        completed = subprocess.run(command, capture_output=True, text=True, timeout=300,
                                   env=dict(os.environ, OMP_NUM_THREADS='1'), check=True)
        report = json.loads(result.read_text())
        classical = report['classical']
        assert classical['wine_train'] + classical['wine_test'] == 178
        assert set(classical['classification_macro_f1']) == {'logistic','forest','svc','neighbors','tfidf_logistic','count_nb'}
        assert all(0 <= value <= 1 for value in classical['classification_macro_f1'].values())
        assert {'kmeans','minibatch','dbscan','hdbscan','ward','gmm','spectral'} <= set(classical['clustering'])
        if embeddings:
            semantic = report['semantic']
            assert semantic['revision'] == '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
            assert semantic['dimension'] == 384 and semantic['train'] == 18 and semantic['test'] == 9
            assert len(semantic['predictions']) == 9 and len(semantic['representatives']) == 3
            assert 0 <= semantic['frozen_head_macro_f1'] <= 1
            assert 0 <= semantic['description_match_macro_f1'] <= 1
        catalog = ROOT/'content/examples/questions/grouping/catalog.json'
        optional = [entry for entry in json.loads(catalog.read_text()) if entry.get('dependencies') == ['numpy','scikit-learn']]
        for example in optional:
            output = subprocess.run([sys.executable, '-I', str(catalog.parent/example['filename'])],
                                    capture_output=True, text=True, timeout=30, check=True)
            assert output.stdout.strip() == example['expect']
    print(json.dumps(dict(text_model_lab='pass', real_embeddings=embeddings,
                         optional_examples=len(optional), provider_calls=0,
                         scope='Tiny CPU fixtures; no encoder fine-tuning, hosted generative model or production benchmark')))


if __name__ == '__main__':
    check(embeddings='--embeddings' in sys.argv)
