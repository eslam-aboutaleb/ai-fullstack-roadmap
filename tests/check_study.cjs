'use strict';
const assert = require('node:assert/strict');
const model = require('../assets/js/study-model.js');
const event = (id, time, kind, data) => ({id, time, kind, ...data});
const attempt = (id, time, assessment, passed = true, hintsUsed = false) =>
  event(id, time, 'attempt', {value: {topic: 1, assessment, kind: 'coding', passed, hintsUsed, independent: true, summary: 'fixture'}});
const stageOf = (events, topic = 1) => model.mastery(model.reduce(events), topic).stage;
const old = model.legacy({learned: {1: true}, notes: {1: 'explain'}, reviews: null, confidence: null});
const pass = attempt('a', 1000, 'alpha');

for (const [events, expected] of [
  [old, 'Familiar'],
  [[pass], 'Independent'],
  [[attempt('hint', 1000, 'alpha', true, true)], 'Practiced'],
  [[pass, attempt('b', 2000, 'beta')], 'Independent'],
  [[pass, attempt('b', 86402000, 'beta')], 'Mastered'],
  [[pass, attempt('b', 86402000, 'alpha')], 'Independent'],
  [[pass, attempt('b', 86402000, 'beta'), attempt('c', 86403000, 'beta', false)], 'Practiced'],
]) {
  assert.equal(stageOf(events), expected);
}

const changes = [event('note', 10, 'set', {field: 'notes', topic: '1', value: 'A'}), event('bookmark', 10, 'set', {field: 'bookmarks', topic: '2', value: true})];
assert.deepEqual(model.reduce(model.merge(changes, [pass])), model.reduce(model.merge([pass], [...changes].reverse())));
assert.equal(model.reduce(model.merge(changes, changes)).notes[1], 'A');
assert.equal(model.reduce([...old, event('reset', 100, 'reset', {})]).notes[1], undefined);
assert.equal(model.reduce([event('reset', 100, 'reset', {}), event('new', 101, 'set', {field: 'notes', topic: '1', value: 'new'})]).notes[1], 'new');
assert.equal(model.eventValid(event('bad', 0, 'set', {field: 'notes', topic: '__proto__', value: 'bad'})), false);
assert.equal(model.eventValid(attempt('bad', -1, 'alpha')), false);
assert.equal(model.schedule(undefined, true, 1000).nextReview, 86401000);
for (const [prev, ok, field, expected] of [
  [{interval: 1, reps: 1}, true, 'interval', 3],
  [{interval: 90, reps: 20}, true, 'interval', 90],
  [{interval: 30, reps: 3}, false, 'interval', 1],
]) {
  assert.equal(model.schedule(prev, ok, 0)[field], expected);
}
assert.deepEqual(model.seeded([1, 2, 3, 4, 5], 42), model.seeded([1, 2, 3, 4, 5], 42));
assert.deepEqual([...model.seeded([1, 2, 3, 4, 5], 42)].sort(), [1, 2, 3, 4, 5]);
console.log('Study model: migration, evidence thresholds, merge order, reset, scheduling, and seeded shuffle passed.');

const cleared = model.compact([...old, event('__study-reset__', 100, 'reset', {})]);
assert.equal(cleared.length, 1);
assert.equal(cleared[0].kind, 'reset');
