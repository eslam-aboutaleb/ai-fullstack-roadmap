"""Demonstrate the end-to-end HTTPS request lifecycle: DNS, TCP, TLS 1.3, and HTTP framing."""

class HTTPSRequestTracer:
    def __init__(self, target_url):
        self.target_url = target_url
        self.timeline = []

    def step_1_dns_resolution(self, domain):
        """Domain Name System: query recursive resolver -> authoritative DNS -> IP address."""
        # Cost: 0ms if cached in OS cache; 20-50ms if full DNS resolution required
        resolved_ip = "198.51.100.42"
        self.timeline.append({"phase": "DNS", "duration_ms": 12, "detail": f"{domain} -> {resolved_ip}"})
        return resolved_ip

    def step_2_tcp_handshake(self, ip, port=443):
        """Transmission Control Protocol: 3-way handshake SYN -> SYN-ACK -> ACK (1 Round Trip Time)."""
        # Establishes sequence numbers and window sizes
        self.timeline.append({"phase": "TCP_HANDSHAKE", "duration_ms": 28, "detail": f"SYN/ACK with {ip}:{port}"})

    def step_3_tls_handshake(self, domain):
        """TLS 1.3 Handshake: 1 RTT cryptographic key exchange."""
        # ClientHello (KeyShare + SNI) -> ServerHello (KeyShare + Encrypted Certificate + Finished) -> Client Finished
        cipher_suite = "TLS_AES_256_GCM_SHA384"
        self.timeline.append({"phase": "TLS_1_3", "duration_ms": 32, "detail": f"Negotiated {cipher_suite} via SNI {domain}"})

    def step_4_http_framing_and_response(self, path):
        """HTTP/2 Multiplexed framing: send HEADERS + DATA frame -> receive response headers -> TTFB."""
        request_headers = f"GET {path} HTTP/2\r\nHost: api.example.com\r\nAccept: application/json\r\n\r\n"
        ttfb_ms = 45 # Time To First Byte (gateway processing + backend application handler)
        self.timeline.append({"phase": "TTFB", "duration_ms": ttfb_ms, "detail": "HTTP/2 200 OK received"})

    def trace(self):
        domain = "api.example.com"
        path = "/v1/models"
        ip = self.step_1_dns_resolution(domain)
        self.step_2_tcp_handshake(ip)
        self.step_3_tls_handshake(domain)
        self.step_4_http_framing_and_response(path)
        
        total_latency = sum(step["duration_ms"] for step in self.timeline)
        return total_latency, self.timeline

tracer = HTTPSRequestTracer("https://api.example.com/v1/models")
total_time, steps = tracer.trace()

assert len(steps) == 4
assert total_time == 117
phases = [s["phase"] for s in steps]
assert phases == ["DNS", "TCP_HANDSHAKE", "TLS_1_3", "TTFB"]

print(f"HTTPS request trace verified: total_latency={total_time}ms, phases={phases}")

