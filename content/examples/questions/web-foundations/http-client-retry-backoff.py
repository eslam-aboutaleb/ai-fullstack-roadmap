"""Demonstrate HTTP client retry policies: Retry-After headers, exponential backoff, and non-retriable errors."""
import random
import time

class MockHTTPResponse:
    def __init__(self, status_code, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body or {}

def execute_http_request_with_retry(endpoint_fn, max_attempts=4, deadline_sec=5.0):
    start_time = time.time()
    attempts = 0

    while True:
        attempts += 1
        elapsed = time.time() - start_time
        if elapsed >= deadline_sec:
            raise TimeoutError(f"HTTP request exceeded deadline budget of {deadline_sec}s")

        response = endpoint_fn(attempts)

        # 1. Success:
        if response.status_code < 400:
            return response, attempts

        # 2. Non-Retriable Client Errors: Fail fast immediately!
        # Retrying a 400 Bad Request, 401 Unauthorized, 403 Forbidden, or 404 Not Found
        # will never succeed without client credential or payload changes.
        if response.status_code in [400, 401, 403, 404, 422]:
            return response, attempts

        # 3. Retriable Server / Rate Limit Errors (429, 502, 503, 504):
        if response.status_code in [429, 502, 503, 504]:
            if attempts >= max_attempts:
                return response, attempts # Return last failure when budget exhausted

            # Check for Retry-After header:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                backoff = float(retry_after)
            else:
                # Exponential backoff with full jitter:
                base = 0.05
                max_sleep = min(1.0, base * (2 ** (attempts - 1)))
                backoff = random.uniform(0.01, max_sleep)

            # Check if backoff fits within remaining deadline:
            if (time.time() - start_time) + backoff >= deadline_sec:
                raise TimeoutError("Remaining deadline insufficient for retry backoff")
                
            time.sleep(backoff)

# Test 1: Transient 429 Too Many Requests with Retry-After header:
def rate_limited_endpoint(attempt):
    if attempt < 3:
        return MockHTTPResponse(429, headers={"Retry-After": "0.02"})
    return MockHTTPResponse(200, body={"data": "success"})

resp1, total1 = execute_http_request_with_retry(rate_limited_endpoint)
assert resp1.status_code == 200 and total1 == 3

# Test 2: Permanent 401 Unauthorized fails immediately on attempt 1 without wasteful retries:
def unauthorized_endpoint(attempt):
    return MockHTTPResponse(401, body={"error": "Invalid token"})

resp2, total2 = execute_http_request_with_retry(unauthorized_endpoint)
assert resp2.status_code == 401 and total2 == 1

print(f"HTTP retry client verified: retried_429_succeeded={resp1.status_code} in {total1} tries; 401_fail_fast={resp2.status_code} in {total2} try")

