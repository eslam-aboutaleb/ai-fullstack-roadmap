"""Demonstrate HTTP method safety, idempotency, and application-level Idempotency-Key headers."""

class HTTPMethodRegistry:
    # RFC 9110 definitions:
    # Safe: read-only, no server state mutation intended (GET, HEAD, OPTIONS)
    # Idempotent: repeating the request multiple times produces the identical side-effect as 1 request (GET, PUT, DELETE)
    # Non-Idempotent: repeating the request creates additional resources or modifies state multiple times (POST, PATCH)
    PROPERTIES = {
        "GET": {"safe": True, "idempotent": True},
        "HEAD": {"safe": True, "idempotent": True},
        "PUT": {"safe": False, "idempotent": True},
        "DELETE": {"safe": False, "idempotent": True},
        "POST": {"safe": False, "idempotent": False},
        "PATCH": {"safe": False, "idempotent": False}
    }

class ServerState:
    def __init__(self):
        self.documents = {}
        self.idempotency_cache = {}

    def handle_request(self, method, path, headers, body):
        prop = HTTPMethodRegistry.PROPERTIES[method]

        # 1. Idempotency-Key Handling for non-idempotent POST requests:
        idempotency_key = headers.get("Idempotency-Key")
        if idempotency_key and method == "POST":
            if idempotency_key in self.idempotency_cache:
                # Return cached result without re-executing business logic
                return 200, self.idempotency_cache[idempotency_key]

        # 2. Execution based on method semantics:
        if method == "PUT":
            # Idempotent replacement: setting doc_1 to 'content_A' multiple times has the exact same result
            doc_id = path.split("/")[-1]
            self.documents[doc_id] = body["content"]
            return 200, {"status": "updated", "id": doc_id}

        elif method == "DELETE":
            # Idempotent deletion: deleting doc_1 repeatedly leaves it deleted
            doc_id = path.split("/")[-1]
            self.documents.pop(doc_id, None)
            return 204, None

        elif method == "POST":
            # Non-idempotent resource creation:
            doc_id = f"doc_{len(self.documents) + 1}"
            self.documents[doc_id] = body["content"]
            result = {"status": "created", "id": doc_id}
            if idempotency_key:
                self.idempotency_cache[idempotency_key] = result
            return 201, result

server = ServerState()

# Non-Idempotent POST without key creates duplicate documents on retry:
s1, r1 = server.handle_request("POST", "/documents", {}, {"content": "Data 1"})
s2, r2 = server.handle_request("POST", "/documents", {}, {"content": "Data 1"})
assert r1["id"] != r2["id"], "Without key, POST created duplicate doc_1 and doc_2"

# Safe POST with Idempotency-Key returns identical response on network retry:
k_headers = {"Idempotency-Key": "req_unique_999"}
s3, r3 = server.handle_request("POST", "/documents", k_headers, {"content": "Payment"})
s4, r4 = server.handle_request("POST", "/documents", k_headers, {"content": "Payment"})
assert r3["id"] == r4["id"], "Idempotency key guaranteed exactly-one created document"

print(f"HTTP method semantics verified: duplicate_post={r2['id']}, idempotent_retried={r4['id']}")

