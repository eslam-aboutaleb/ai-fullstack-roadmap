/**
 * Demonstrate React state snapshots and stale closures vs functional state updates.
 */

// Simulated React Component State Engine
class ComponentSimulator {
  constructor(initialState) {
    this.state = initialState;
    this.pendingQueue = [];
  }

  // Naive update capturing current render snapshot:
  setStateDirect(newValue) {
    this.pendingQueue.push(() => newValue);
  }

  // Functional update receiving fresh committed state:
  setStateFunctional(updaterFn) {
    this.pendingQueue.push(updaterFn);
  }

  applyUpdates() {
    for (const update of this.pendingQueue) {
      this.state = update(this.state);
    }
    this.pendingQueue = [];
    return this.state;
  }
}

// 1. PITFALL: Stale Closure / Render Snapshot Overwrite
// In an event handler, 'count' is captured from the current render closure (count = 0).
// Two calls to setCount(count + 1) both pass (0 + 1 = 1):
const compA = new ComponentSimulator({ count: 0 });
const snapshotCount = compA.state.count; // 0
compA.setStateDirect(snapshotCount + 1);
compA.setStateDirect(snapshotCount + 1);
const resultA = compA.applyUpdates();
// Bug demonstrated: count is 1 instead of 2!
if (resultA.count !== 1) throw new Error("Expected stale snapshot result to be 1");

// 2. DEFENSE: Functional State Updates (setCount(prev => prev + 1))
// Each updater function receives the fresh accumulated state from the previous update in the batch:
const compB = new ComponentSimulator({ count: 0 });
compB.setStateFunctional(prev => ({ count: prev.count + 1 }));
compB.setStateFunctional(prev => ({ count: prev.count + 1 }));
const resultB = compB.applyUpdates();
// Correct accumulated count:
if (resultB.count !== 2) throw new Error("Expected functional update result to be 2");

console.log(`React state update verified: direct_stale=${resultA.count}, functional_accumulated=${resultB.count}`);
