/* Pure study-record rules; browser storage is implemented separately. */
(function (root) {
  'use strict';
  const FIELDS = new Set(['learned', 'bookmarks', 'notes', 'confidence', 'reviews', 'theme', 'distractionFree']);
  const topicId = value => /^[1-9]\d*$/.test(String(value)) && Number.isSafeInteger(Number(value));
  const object = value => value && typeof value === 'object' && !Array.isArray(value);
  function eventValid(event) {
    if (!object(event) || typeof event.id !== 'string' || event.id.length > 200 || !Number.isSafeInteger(event.time) || event.time < 0) return false;
    if (event.kind === 'reset') return true;
    if (event.id === '__study-reset__') return false;
    if (event.kind === 'attempt') {
      const a = event.value;
      return object(a) && topicId(a.topic) && typeof a.assessment === 'string' && a.assessment.length <= 100 &&
        ['quiz', 'debugging', 'coding', 'self-review'].includes(a.kind) && [true, false, null].includes(a.passed) &&
        typeof a.independent === 'boolean' && typeof a.hintsUsed === 'boolean' && typeof a.summary === 'string' && a.summary.length <= 2000;
    }
    if (event.kind !== 'set' || !FIELDS.has(event.field)) return false;
    const v = event.value;
    if (event.field === 'theme') return event.topic === 'global' && ['light', 'warm', 'dark'].includes(v);
    if (event.field === 'distractionFree') return event.topic === 'global' && typeof v === 'boolean';
    if (!topicId(event.topic)) return false;
    if (['learned', 'bookmarks'].includes(event.field)) return typeof v === 'boolean';
    if (event.field === 'notes') return typeof v === 'string' && v.length <= 20000;
    if (event.field === 'confidence') return Number.isInteger(v) && v >= 1 && v <= 5;
    return object(v) && Number.isFinite(v.interval) && v.interval >= 0 && v.interval <= 3650 &&
      Number.isSafeInteger(v.reps) && v.reps >= 0 && Number.isFinite(v.nextReview) && v.nextReview >= 0;
  }
  function merge(...collections) {
    const events = new Map();
    for (const list of collections) for (const event of list || []) {
      if (!eventValid(event)) continue;
      // Conflicting copies of an event ID cannot depend on import order.
      const previous = events.get(event.id);
      if (!previous || event.time > previous.time || event.time === previous.time && JSON.stringify(event) > JSON.stringify(previous)) events.set(event.id, event);
    }
    return [...events.values()].sort((a, b) => a.time - b.time || a.id.localeCompare(b.id));
  }
  function compact(events) {
    const ordered = merge(events);
    let start = 0;
    ordered.forEach((event,index) => { if (event.kind === 'reset') start = index; });
    return ordered.slice(start);
  }
  function reduce(events) {
    let state;
    const clear = () => ({learned: {}, bookmarks: {}, notes: {}, confidence: {}, reviews: {}, theme: 'light', distractionFree: false, attempts: []});
    state = clear();
    for (const event of merge(events)) {
      if (event.kind === 'reset') { state = clear(); continue; }
      if (event.kind === 'attempt') {
        state.attempts.push({...event.value, id: event.id, time: event.time});
      } else if (event.topic === 'global') state[event.field] = event.value;
      else state[event.field][event.topic] = event.value;
    }
    return state;
  }
  function legacy(input, namespace = 'v1') {
    if (!object(input)) return [];
    const records = [];
    for (const field of FIELDS) {
      if (['theme', 'distractionFree'].includes(field)) {
        const event = {id: `migration-${namespace}-${field}`, time: 0, kind: 'set', topic: 'global', field, value: input[field]};
        if (eventValid(event)) records.push(event);
        continue;
      }
      if (!object(input[field])) continue;
      for (const [topic, value] of Object.entries(input[field])) {
        const event = {id: `migration-${namespace}-${field}-${topic}`, time: 0, kind: 'set', topic, field, value};
        if (eventValid(event)) records.push(event);
      }
    }
    return records;
  }
  function schedule(previous, passed, now) {
    const interval = !passed ? 1 : !previous?.interval ? 1 : previous.interval < 3 ? 3 : Math.min(90, previous.interval * 2);
    return {interval, reps: passed ? (previous?.reps || 0) + 1 : 0, nextReview: now + interval * 86400000};
  }
  function mastery(state, topic) {
    const attempts = state.attempts.filter(a => String(a.topic) === String(topic));
    const graded = attempts.filter(a => a.kind !== 'self-review' && a.passed !== null);
    const passes = graded.filter(a => a.passed);
    const independent = passes.filter(a => a.independent && !a.hintsUsed);
    const latest = graded.at(-1);
    let stage = state.learned[topic] || attempts.length ? 'Familiar' : 'Not started';
    if (passes.length) stage = 'Practiced';
    if (independent.length && latest?.passed) stage = 'Independent';
    if (latest?.passed && independent.some(a => independent.some(b => a.assessment !== b.assessment && Math.abs(a.time - b.time) >= 86400000))) stage = 'Mastered';
    return {stage, attempts: attempts.length, passes: passes.length, independent: independent.length, latest};
  }
  function seeded(items, seed) {
    const out = [...items]; let value = Number(seed) >>> 0 || 1;
    for (let i = out.length - 1; i > 0; i--) {
      value ^= value << 13; value ^= value >>> 17; value ^= value << 5;
      const j = (value >>> 0) % (i + 1);
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }
  const api = Object.freeze({eventValid, merge, compact, reduce, legacy, schedule, mastery, seeded});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.GuideStudyModel = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
