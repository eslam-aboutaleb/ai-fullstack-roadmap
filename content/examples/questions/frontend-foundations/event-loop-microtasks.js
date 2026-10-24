/**
 * Demonstrate the JavaScript Event Loop:
 * Call Stack -> Microtasks (Promises, queueMicrotask) -> Macrotasks (setTimeout) -> Render Phase
 */

const log = [];

function demonstrateEventLoopPhases() {
  log.push("1: Synchronous code on Call Stack");

  // Macrotask (Task Queue): Executed after current turn and pending microtasks complete
  setTimeout(() => {
    log.push("5: Macrotask (setTimeout 0ms)");
    verifyOrder();
  }, 0);

  // Microtask (Microtask Queue): Drained immediately after synchronous Call Stack before next macrotask or render!
  Promise.resolve().then(() => {
    log.push("3: Microtask 1 (Promise.then)");
  }).then(() => {
    log.push("4: Microtask 2 (Chained Promise)");
  });

  log.push("2: Synchronous code finishes");
}

function verifyOrder() {
  const expected = [
    "1: Synchronous code on Call Stack",
    "2: Synchronous code finishes",
    "3: Microtask 1 (Promise.then)",
    "4: Microtask 2 (Chained Promise)",
    "5: Macrotask (setTimeout 0ms)"
  ];
  
  const matches = JSON.stringify(log) === JSON.stringify(expected);
  if (!matches) throw new Error("Unexpected event loop execution order");
  console.log(`Event loop order verified: ${log.length} tasks executed in order`);
}

demonstrateEventLoopPhases();

