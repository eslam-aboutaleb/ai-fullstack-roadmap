/**
 * Implement defense-in-depth client security: safe sink text mapping, protocol allowlisting, and CSP nonce checking.
 */

const ALLOWED_PROTOCOLS = new Set(["https:", "http:"]);

function sanitizeNavigationUrl(untrustedUrl) {
  try {
    const parsed = new URL(untrustedUrl, "https://example.com");
    if (!ALLOWED_PROTOCOLS.has(parsed.protocol)) {
      return "#blocked";
    }
    return parsed.href;
  } catch {
    return "#blocked";
  }
}

function validateScriptNonce(elementNonce, activeCspNonce) {
  return typeof elementNonce === "string" && elementNonce === activeCspNonce;
}

function renderSafeTextSink(untrustedString) {
  // Safe sink: encode all HTML entities so browser parsers never execute injected tags
  return String(untrustedString)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// 1. Protocol allowlist blocks javascript: pseudo-protocol XSS
const maliciousLink = "javascript:stealCredentials()";
const safeLink = sanitizeNavigationUrl(maliciousLink);
const protocolBlocked = safeLink === "#blocked";

// 2. Safe sink escapes script tags into non-executable entities
const payload = '<script>alert("XSS")</script><img src=x onerror=steal()>';
const safeEscaped = renderSafeTextSink(payload);
const scriptTagsEscaped = !safeEscaped.includes("<script") && safeEscaped.includes("&lt;script&gt;");

// 3. CSP Nonce verification
const sessionCspNonce = "nonce-8f2a1b9c7";
const isAuthorizedScript = validateScriptNonce("nonce-8f2a1b9c7", sessionCspNonce);
const isUntrustedScript = validateScriptNonce("malicious-injected-nonce", sessionCspNonce);

console.log(
  `Frontend defense verified: protocol_blocked=${protocolBlocked}, script_tags_escaped=${scriptTagsEscaped}, nonce_valid=${isAuthorizedScript && !isUntrustedScript}`
);
