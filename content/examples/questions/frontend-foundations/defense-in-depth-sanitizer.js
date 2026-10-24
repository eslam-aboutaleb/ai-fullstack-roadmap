/**
 * Implement defense-in-depth sanitization for untrusted HTML inputs and CSP nonce validation.
 */

function sanitizeHtml(untrustedInput) {
  // Strip <script> tags and contents
  let clean = untrustedInput.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");
  // Strip inline event handlers (e.g., onerror=, onclick=)
  clean = clean.replace(/\son\w+="[^"]*"/gi, "");
  clean = clean.replace(/\son\w+='[^']*'/gi, "");
  // Strip javascript: pseudo-protocols
  clean = clean.replace(/href=["']javascript:[^"']*["']/gi, 'href="#"');
  return clean;
}

function validateScriptNonce(scriptNonce, validRequestNonce) {
  return scriptNonce === validRequestNonce;
}

// 1. Sanitize malicious payload
const dirtyHtml = '<p>Welcome</p><script>alert("XSS")</script><img src="x" onerror="stealCookies()"><a href="javascript:attack()">Link</a>';
const safeHtml = sanitizeHtml(dirtyHtml);

const scriptsStripped = !safeHtml.includes("<script");
const handlersRemoved = !safeHtml.includes("onerror=");

// 2. Validate CSP nonce
const requestNonce = "nonce-4ae78f9c1";
const nonceValid = validateScriptNonce("nonce-4ae78f9c1", requestNonce);

console.log(
  `Frontend defense verified: script_tags_stripped=${scriptsStripped}, event_handlers_removed=${handlersRemoved}, nonce_valid=${nonceValid}`
);
