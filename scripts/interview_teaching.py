"""Question headings and in-answer terminology for interview-led chapter reading."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
ACRONYMS = json.loads((ROOT/'content/shared/acronyms.json').read_text())
TITLES = {
 'Trace an HTTPS request from a browser address to an application response.':'How does an HTTPS request travel from a browser address to an application response?',
 'Trace query, key and value shapes through one attention head.':'How do query, key and value shapes flow through one attention head?',
 'Values, identity and the data model':'How do Python values, object identity and the data model work?',
 'Iteration, resource lifetimes and types':'How do Python iteration, resource lifetimes and type boundaries work?',
 'Testing, profiling and reliable delivery':'How do you test, debug and deliver a reproducible Python program?',
 'Complexity, processes and the network boundary':'How do complexity, processes and network boundaries affect a program?',
 'Structured asyncio, cancellation and deadlines':'How do structured concurrency, cancellation and deadlines work in asyncio?',
 'Follow an ordinary HTTP request before choosing a framework':'What happens during an ordinary HTTP request before a framework handles it?',
 'FastAPI parsing, validation and authorization':'How does FastAPI separate parsing, validation and authorization?',
 'Semantic HTML, responsive layout and accessible interaction':'How do semantic HTML, responsive layout and accessible interaction fit together?',
 'JavaScript promises, TypeScript boundaries and React snapshots':'How do promises, TypeScript boundaries and React state snapshots affect a UI?',
 'Browser trust boundaries, authentication UX and measured performance':'How do browser trust boundaries affect authentication and measured performance?',
 'Data contracts, SQL constraints and schema evolution':'How do data contracts, SQL constraints and schema evolution work together?',
 'Incremental ingestion, CDC and atomic checkpoints':'How do incremental ingestion, CDC and atomic checkpoints recover safely?',
 'Event time, late data, windows and backpressure':'How do event time, late data, windows and backpressure affect streaming results?',
 'Lineage, deletion, data quality and safe index promotion':'How do lineage, deletion and data quality control safe index promotion?',
 'Vectors, probability and statistical reasoning':'How do vectors, probability and statistics support model decisions?',
 'Calculate conditional probability and inspect sampling assumptions':'How do you calculate conditional probability and check sampling assumptions?',
 'Gradients and optimization from a numerical update':'How does a gradient produce a numerical optimization update?',
 'Learning tasks, baselines and leakage':'How do you define a learning task, choose a baseline and prevent leakage?',
 'Choose linear, tree and unsupervised baselines by their objective':'How do linear, tree and unsupervised model objectives differ?',
 'Model selection, leakage, uncertainty and a measured CPU baseline':'How do you select a model and measure uncertainty against a CPU baseline?',
 'A neural network and backpropagation you can inspect':'How does a small neural network learn through backpropagation?',
 'Compare convolution, recurrence and attention before selecting an architecture':'How do convolution, recurrence and attention guide architecture selection?',
 'From scalar derivatives to NumPy and PyTorch':'How do scalar derivatives connect to NumPy and PyTorch autograd?',
 'Tokenization, attention and tensor dimensions':'How do tokenization and tensor dimensions determine attention computation?',
 'Training objectives, decoding and cached inference':'How do training objectives, decoding and cached inference interact?',
 'Quantization, LoRA, distillation and model evaluation':'How do quantization, LoRA and distillation change model evaluation?',
 'Sequence structures: lists, tuples and slicing mechanics':'How do Python lists, tuples and slicing mechanics operate under the memory model?',
 'Hash tables: dictionaries, sets and collision resolution':'How do Python dictionaries and sets handle hashing and collision resolution?',
 'Queueing, heaps and specialized container algorithms':'How do deques, heaps and specialized containers optimize queueing algorithms?',
 'Two Pointers, partitioning and in-place array transformations':'How do two pointers and in-place partitioning optimize array algorithms?',
 'Sliding Window dynamics and monotonic boundary contraction':'How do sliding windows and monotonic boundaries optimize contiguous subarray algorithms?',
 'Hash table frequency indexing, prefix sums and complements':'How do hash tables, prefix sums and complements optimize lookup algorithms?',
 'Binary search invariants, monotonicity and range reduction':'How do binary search invariants and range reductions guarantee logarithmic search?',
}


def teaching_title(record):
    return TITLES.get(record['Q'], record['Q'])


def answer_acronyms(record):
    # Only narrative prose: SQL keywords, code identifiers and URL fragments are
    # not learner acronyms. Nested follow-up explanations are included.
    keys=('Q','A','Why','Risk','Trade','Try','spoken','explain','example','takeaway',
          'conceptual_narrative','production_case','complexity','worked_case',
          'execution_timeline','follow_ups','underlying_mechanics')
    def prose(value):
        if isinstance(value,str): return value
        if isinstance(value,list): return ' '.join(prose(item) for item in value)
        if isinstance(value,dict): return ' '.join(prose(v) for k,v in value.items() if k not in ('code','output'))
        return ''
    text=' '.join(prose(record.get(key,'')) for key in keys)
    return [(key,definition) for key,definition in ACRONYMS.items()
            if re.search(r'(?<![\w])'+re.escape(key)+r'(?:s)?(?![\w])',text)]


def answer_terms(record):
    terms=answer_acronyms(record)
    if not terms:return ''
    escape=html.escape
    return '<aside class="answer-terms"><h4>Acronyms in this answer</h4><dl>'+''.join(
        '<dt>'+escape(term)+'</dt><dd>'+escape(definition)+'</dd>' for term,definition in terms)+'</dl></aside>'
