/**
 * Demonstrate token storage trust boundaries: localStorage (XSS vulnerable) vs HttpOnly cookies.
 */

// Simulated Browser Storage Context
const mockLocalStorage = {};
const mockCookieJar = {
  httpOnlyCookies: {},
  documentCookies: {}
};

function demonstrateStorageVulnerabilities() {
  // ANTI-PATTERN: Storing bearer token in localStorage or document.cookie
  mockLocalStorage["access_token"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secret_jwt_token";

  // Simulate an injected third-party script or XSS vulnerability:
  function maliciousScript() {
    // Malicious JavaScript running in page origin reads localStorage:
    return mockLocalStorage["access_token"];
  }

  const stolenToken = maliciousScript();
  if (!stolenToken) throw new Error("Expected localStorage token to be readable by script");

  // BEST PRACTICE: Session token stored in HttpOnly; Secure; SameSite=Strict cookie
  // The browser sends this cookie automatically on API requests, but JavaScript CANNOT read it!
  mockCookieJar.httpOnlyCookies["session_id"] = "durable_secure_session_token_xyz";

  function maliciousScriptCookieAttempt() {
    // Ordinary document.cookie reads only non-HttpOnly cookies
    return mockCookieJar.documentCookies["session_id"] || null;
  }

  const cookieTheft = maliciousScriptCookieAttempt();
  if (cookieTheft !== null) throw new Error("HttpOnly cookie must be inaccessible to JavaScript");

  console.log(`Token security boundary verified: localStorage_readable_by_js=true (vulnerable), httpOnly_cookie_readable_by_js=false (safe)`);
}

demonstrateStorageVulnerabilities();

