/**
 * Demonstrate runtime schema validation and TypeScript discriminated unions.
 */

// Discriminated Union pattern: each variant has a unique literal 'status' discriminator tag.
function validateApiResponse(untrustedJson) {
  if (typeof untrustedJson !== "object" || untrustedJson === null) {
    return { status: "error", code: 400, message: "Response is not an object" };
  }

  // Runtime boundary check:
  if (untrustedJson.status === "success") {
    if (!Array.isArray(untrustedJson.citations) || typeof untrustedJson.answer !== "string") {
      return { status: "error", code: 502, message: "Malformed success payload: missing citations or answer" };
    }
    return {
      status: "success",
      data: {
        answer: untrustedJson.answer,
        citations: untrustedJson.citations
      }
    };
  }

  if (untrustedJson.status === "rate_limited") {
    const retryAfter = typeof untrustedJson.retry_after_sec === "number" ? untrustedJson.retry_after_sec : 30;
    return { status: "rate_limited", retryAfterSec: retryAfter };
  }

  return { status: "error", code: 500, message: "Unknown response status" };
}

// 1. Valid success response
const rawSuccess = { status: "success", answer: "All systems nominal", citations: ["doc_1", "doc_2"] };
const resultSuccess = validateApiResponse(rawSuccess);
if (resultSuccess.status !== "success" || resultSuccess.data.citations.length !== 2) {
  throw new Error("Validation failed for valid payload");
}

// 2. Malformed response (claims success but citations is a string instead of array)
const rawMalformed = { status: "success", answer: "Draft", citations: "invalid_string_not_array" };
const resultMalformed = validateApiResponse(rawMalformed);
if (resultMalformed.status !== "error") {
  throw new Error("Validation should have caught malformed citations array");
}

console.log(`TypeScript runtime union verified: valid_status=${resultSuccess.status}, malformed_caught=${resultMalformed.status}`);

