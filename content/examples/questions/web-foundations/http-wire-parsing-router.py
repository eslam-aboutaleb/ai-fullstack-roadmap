"""Demonstrate raw HTTP/1.1 wire protocol stream parsing and routing into an ASGI scope."""

def parse_http_wire_request(raw_bytes):
    """
    Parses a raw TCP stream according to RFC 9112 HTTP/1.1 syntax:
    Request-Line = method SP request-target SP HTTP-version CRLF
    Headers = *(header-field CRLF) CRLF
    [message-body]
    """
    parts = raw_bytes.split(b"\r\n\r\n", 1)
    header_block = parts[0].decode("iso-8859-1")
    body = parts[1] if len(parts) > 1 else b""

    lines = header_block.split("\r\n")
    request_line = lines[0]
    method, path, version = request_line.split(" ")

    headers = {}
    for line in lines[1:]:
        if not line: continue
        name, val = line.split(":", 1)
        headers[name.strip().lower()] = val.strip()

    # Construct standard ASGI HTTP Scope dictionary (as used by Uvicorn and FastAPI):
    asgi_scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": version.split("/")[1],
        "method": method,
        "path": path.split("?")[0],
        "raw_path": path.split("?")[0].encode(),
        "query_string": path.split("?")[1].encode() if "?" in path else b"",
        "headers": [(k.encode(), v.encode()) for k, v in headers.items()]
    }

    return asgi_scope, body

# Raw HTTP stream bytes as received on a low-level OS socket:
raw_stream = (
    b"POST /api/v1/inference?stream=true HTTP/1.1\r\n"
    b"Host: api.example.com:8443\r\n"
    b"Authorization: Bearer test_token_xyz\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: 26\r\n"
    b"\r\n"
    b'{"prompt": "Generate plan"}'
)

scope, body_data = parse_http_wire_request(raw_stream)

assert scope["method"] == "POST"
assert scope["path"] == "/api/v1/inference"
assert scope["query_string"] == b"stream=true"
assert body_data == b'{"prompt": "Generate plan"}'

header_dict = dict(scope["headers"])
assert header_dict[b"authorization"] == b"Bearer test_token_xyz"

print(f"HTTP wire parsing verified: method={scope['method']}, path={scope['path']}, body_bytes={len(body_data)}")
