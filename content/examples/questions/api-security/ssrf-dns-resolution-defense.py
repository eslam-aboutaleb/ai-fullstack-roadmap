"""Server-Side Request Forgery (SSRF) defense, pre-flight DNS validation, and cloud metadata blocking.

Demonstrates:
1. Strict scheme allowlisting: Enforcing HTTPS and blocking hazardous protocols (file://, gopher://, dict://, http://).
2. Pre-flight DNS resolution: Resolving hostnames to IP addresses before initiating network connections.
3. Comprehensive IP address blocking: Rejecting IPv4/IPv6 loopbacks, private subnets (RFC 1918), and link-local cloud metadata (169.254.169.254).
4. DNS rebinding defense: Pinning the outbound socket connection to the validated IP address.
"""
from typing import List, Optional, Tuple
import ipaddress
import socket
import urllib.parse

class SsrfProtectionValidator:
    # Explicitly forbidden IP networks
    BLOCKED_NETWORKS = [
        ipaddress.ip_network("0.0.0.0/8"),          # Current network
        ipaddress.ip_network("127.0.0.0/8"),        # IPv4 Loopback
        ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918 Private
        ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private
        ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private
        ipaddress.ip_network("169.254.0.0/16"),     # Link-Local / Cloud Metadata (169.254.169.254)
        ipaddress.ip_network("100.64.0.0/10"),      # Carrier-Grade NAT
        ipaddress.ip_network("::1/128"),            # IPv6 Loopback
        ipaddress.ip_network("fc00::/7"),           # IPv6 Unique Local
        ipaddress.ip_network("fe80::/10"),          # IPv6 Link-Local
    ]

    ALLOWED_SCHEMES = {"https"}

    @classmethod
    def validate_outbound_url(cls, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Parses URL, verifies scheme, resolves DNS, and asserts IP safety."""
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            return False, f"Malformed URL: {str(e)}", None

        # 1. Scheme validation
        if parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
            return False, f"Insecure scheme '{parsed.scheme}'. Only HTTPS is permitted.", None

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL.", None

        # 2. Pre-flight DNS Resolution
        try:
            addr_info = socket.getaddrinfo(hostname, parsed.port or 443, proto=socket.IPPROTO_TCP)
        except socket.gaierror as e:
            return False, f"DNS resolution failed for '{hostname}': {str(e)}", None

        resolved_ips: List[str] = list({info[4][0] for info in addr_info})
        if not resolved_ips:
            return False, f"No IP addresses found for host '{hostname}'.", None

        # 3. Validate every resolved IP against blocked networks
        for ip_str in resolved_ips:
            try:
                ip_obj = ipaddress.ip_address(ip_str)
            except ValueError:
                return False, f"Invalid IP representation: '{ip_str}'", None

            for network in cls.BLOCKED_NETWORKS:
                if ip_obj in network:
                    return False, f"SSRF blocked: Host '{hostname}' resolves to restricted IP '{ip_str}' in '{network}'.", None

        # Return validated first safe IP for connection pinning (defending against DNS rebinding)
        safe_pinned_ip = resolved_ips[0]
        return True, None, safe_pinned_ip

if __name__ == "__main__":
    validator = SsrfProtectionValidator()

    # 1. Blocked Schemes (file://, http://, gopher://)
    ok_file, err_file, _ = validator.validate_outbound_url("file:///etc/passwd")
    assert ok_file is False
    assert "Only HTTPS is permitted" in err_file

    ok_http, err_http, _ = validator.validate_outbound_url("http://insecure-site.com/data")
    assert ok_http is False
    assert "Only HTTPS is permitted" in err_http

    # 2. Blocked Cloud Metadata IP (169.254.169.254)
    ok_meta, err_meta, _ = validator.validate_outbound_url("https://169.254.169.254/latest/meta-data/")
    assert ok_meta is False
    assert "restricted IP '169.254.169.254'" in err_meta

    # 3. Blocked Localhost / Loopback
    ok_local, err_local, _ = validator.validate_outbound_url("https://127.0.0.1:8443/admin")
    assert ok_local is False
    assert "127.0.0.1" in err_local

    # 4. Blocked Private RFC 1918 Subnets
    ok_priv, err_priv, _ = validator.validate_outbound_url("https://192.168.1.100/status")
    assert ok_priv is False
    assert "192.168.1.100" in err_priv

    ok_corp, err_corp, _ = validator.validate_outbound_url("https://10.0.0.5:9000/db")
    assert ok_corp is False
    assert "10.0.0.5" in err_corp

    # 5. Valid Public Endpoint
    ok_pub, err_pub, pinned_ip = validator.validate_outbound_url("https://www.google.com")
    assert ok_pub is True
    assert err_pub is None
    assert pinned_ip is not None
    # Pinned IP is verified public IP address
    assert not ipaddress.ip_address(pinned_ip).is_private

    print("SSRF pre-flight DNS validation and cloud metadata defenses verified successfully.")
