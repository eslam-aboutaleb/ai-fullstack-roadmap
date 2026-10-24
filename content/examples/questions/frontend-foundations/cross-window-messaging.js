/**
 * Simulate secure cross-window postMessage and multi-tab BroadcastChannel coordination.
 */

const TRUSTED_ORIGINS = new Set(["https://dashboard.example.com"]);

function handlePostMessage(eventOrigin, eventData) {
  // Strict origin verification
  if (!TRUSTED_ORIGINS.has(eventOrigin)) {
    return { accepted: false, reason: "unauthorized_origin" };
  }
  return { accepted: true, payload: eventData };
}

// 1. Check unauthorized vs authorized origins
const untrustedAttempt = handlePostMessage("https://malicious-site.attacker.com", { token: "stolen" });
const trustedAttempt = handlePostMessage("https://dashboard.example.com", { type: "AUTH_REFRESH" });

// 2. BroadcastChannel multi-tab sync simulation
class MockBroadcastChannel {
  constructor(channelName) {
    this.name = channelName;
    this.listeners = [];
  }
  postMessage(message) {
    this.listeners.forEach((fn) => fn(message));
  }
  onmessage(fn) {
    this.listeners.push(fn);
  }
}

const authChannel = new MockBroadcastChannel("auth_sync");
let multiTabSynced = false;
authChannel.onmessage((msg) => {
  if (msg.action === "LOGOUT") {
    multiTabSynced = true;
  }
});
authChannel.postMessage({ action: "LOGOUT", timestamp: Date.now() });

console.log(
  `Cross-window messaging verified: unauthorized_origin_blocked=${!untrustedAttempt.accepted}, multi_tab_synced=${multiTabSynced}`
);
