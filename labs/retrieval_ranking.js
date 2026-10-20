// Local deterministic RRF lab. Run with Node.js or paste into a browser console.
(() => {
  function assert(condition, message) { if (!condition) throw new Error(message); }
  function reciprocalRankFusion(rankings, k = 60) {
    if (!Number.isFinite(k) || k < 0) throw new RangeError('k must be finite and nonnegative');
    const scores = new Map();
    for (const ranking of rankings) {
      const seen = new Set();
      ranking.forEach((doc, index) => {
        if (seen.has(doc)) throw new Error('A ranking must contain unique document IDs');
        seen.add(doc);
        scores.set(doc, (scores.get(doc) || 0) + 1 / (k + index + 1));
      });
    }
    return [...scores].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([doc]) => doc);
  }
  const dense = ['doc-7', 'doc-2', 'doc-9', 'doc-1', 'doc-4'];
  const lexical = ['doc-2', 'doc-5', 'doc-7', 'doc-3', 'doc-1'];
  const fused = reciprocalRankFusion([dense, lexical]);
  // doc-2 is second + first; doc-7 is first + third. The union has 7 IDs.
  assert(fused[0] === 'doc-2', 'doc-2 should rank highest');
  assert(fused.length === 7, 'Return all seven unique documents');
  assert(reciprocalRankFusion([]).length === 0, 'Empty rankings stay empty');
  assert(reciprocalRankFusion([['__proto__', 'constructor']]).length === 2, 'IDs are data');
  let rejected = false;
  try { reciprocalRankFusion([['same', 'same']]); } catch { rejected = true; }
  assert(rejected, 'Duplicate IDs within a ranking must be rejected');
  console.log('RRF:', fused.join(', '));
  console.log('All assertions passed. Try k=1 and explain how rank changes affect scores.');
})();
