/**
 * Demonstrate React useEffect cleanup with AbortController to prevent race conditions and memory leaks.
 */

class MockAbortController {
  constructor() {
    this.signal = { aborted: false };
  }
  abort() {
    this.signal.aborted = true;
  }
}

async function simulateFetchUserData(userId, signal) {
  // Simulate network latency (userId 'usr_1' takes 50ms, userId 'usr_2' takes 10ms)
  const delay = userId === 'usr_1' ? 50 : 10;
  await new Promise(resolve => setTimeout(resolve, delay));
  
  if (signal.aborted) {
    const error = new Error("AbortError: Fetch request aborted by component cleanup");
    error.name = "AbortError";
    throw error;
  }
  return { id: userId, name: `User ${userId}` };
}

async function runEffectLifecycle() {
  let activeUser = null;
  let unhandledErrors = 0;

  // Render 1: User navigates to 'usr_1'
  let currentController = new MockAbortController();
  const fetchPromise1 = simulateFetchUserData('usr_1', currentController.signal)
    .then(data => { activeUser = data; })
    .catch(err => { if (err.name !== "AbortError") unhandledErrors++; });

  // Rapid Navigation: Before usr_1 completes, User navigates to 'usr_2'!
  // React executes the Effect cleanup function:
  currentController.abort(); // Cleans up previous subscription / aborts HTTP request

  // Render 2: Effect runs for 'usr_2'
  currentController = new MockAbortController();
  const fetchPromise2 = simulateFetchUserData('usr_2', currentController.signal)
    .then(data => { activeUser = data; })
    .catch(err => { if (err.name !== "AbortError") unhandledErrors++; });

  await Promise.allSettled([fetchPromise1, fetchPromise2]);

  // If cleanup was omitted, slow usr_1 would resolve AFTER usr_2 and overwrite the screen with stale data!
  // With AbortController cleanup, usr_1 is safely rejected and activeUser remains usr_2:
  if (activeUser.id !== 'usr_2') throw new Error(`Race condition bug! Active user is ${activeUser.id}`);
  console.log(`Effect cleanup verified: active_user=${activeUser.id}, unhandled_errors=${unhandledErrors}`);
}

runEffectLifecycle();

