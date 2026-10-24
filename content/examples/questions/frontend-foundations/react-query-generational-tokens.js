/**
 * Demonstrate generational query tokens and user session isolation in frontend state.
 */

class UserScopedDataStore {
  constructor() {
    this.currentOwner = null;
    this.currentGeneration = 0;
    this.data = null;
  }

  login(user) {
    this.currentOwner = user;
    this.currentGeneration += 1;
    this.data = null; // Clear previous user state
    return { owner: this.currentOwner, generation: this.currentGeneration };
  }

  logout() {
    this.currentOwner = null;
    this.currentGeneration += 1; // Invalidate any in-flight requests from the logged-out user
    this.data = null;
  }

  // Handle incoming API response tagged with the generation at dispatch time:
  commitResponse(dispatchOwner, dispatchGeneration, responsePayload) {
    // Stale check: If the user changed or a newer generation started, discard the response!
    if (dispatchOwner !== this.currentOwner || dispatchGeneration !== this.currentGeneration) {
      return { accepted: false, reason: "Stale generation or owner mismatch" };
    }
    this.data = responsePayload;
    return { accepted: true, data: this.data };
  }
}

const store = new UserScopedDataStore();

// Scenario: Alice logs in and dispatches a slow request
const tokenAlice = store.login("alice");

// While Alice's request is still in-flight over the network, Alice logs out and Bob logs in:
store.logout();
const tokenBob = store.login("bob");

// Alice's delayed response finally arrives:
const aliceResult = store.commitResponse(tokenAlice.owner, tokenAlice.generation, { privateNotes: "Alice's secrets" });
if (aliceResult.accepted) throw new Error("Security leak! Stale response accepted into new session");

// Bob's response arrives:
const bobResult = store.commitResponse(tokenBob.owner, tokenBob.generation, { privateNotes: "Bob's dashboard" });
if (!bobResult.accepted) throw new Error("Bob's fresh response was rejected");

console.log(`Generational token verified: alice_stale_accepted=${aliceResult.accepted}, bob_active_accepted=${bobResult.accepted}`);

