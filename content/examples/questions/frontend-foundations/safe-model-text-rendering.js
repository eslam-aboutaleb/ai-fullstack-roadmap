/**
 * Demonstrate rendering untrusted model text safely: HTML entity escaping vs dangerouslySetInnerHTML.
 */

function escapeHtml(unsafeText) {
  // Safe default: convert untrusted text into harmless text nodes by escaping HTML delimiters
  return String(unsafeText)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderChatBubble(untrustedModelOutput, renderMode) {
  if (renderMode === "dangerouslySetInnerHTML") {
    // VULNERABILITY: Raw HTML insertion executes inline scripts and onerror event handlers!
    return `<div class="bubble">${untrustedModelOutput}</div>`;
  } else {
    // SECURE: Escaping converts executable tags into plain text representations
    return `<div class="bubble" style="overflow-wrap: anywhere;">${escapeHtml(untrustedModelOutput)}</div>`;
  }
}

// Untrusted payload containing XSS injection from prompt injection:
const maliciousModelOutput = '<img src="x" onerror="stealSessionCookie()"> Click here for info';

const insecureHtml = renderChatBubble(maliciousModelOutput, "dangerouslySetInnerHTML");
const secureHtml = renderChatBubble(maliciousModelOutput, "safeEscaped");

// Verify that the secure output contains no raw '<img' tags:
if (secureHtml.includes('<img')) {
  throw new Error("XSS vulnerability: unescaped HTML tag present");
}

if (!secureHtml.includes('&lt;img')) {
  throw new Error("Expected escaped entity &lt;img");
}

console.log(`Model text rendering verified: unescaped_tag_present=${secureHtml.includes('<img')}, safe_entity_present=${secureHtml.includes('&lt;img')}`);
