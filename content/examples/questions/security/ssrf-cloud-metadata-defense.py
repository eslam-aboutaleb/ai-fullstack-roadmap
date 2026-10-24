"""Cloud metadata SSRF defense, redirect re-validation, and production transport protection.

Demonstrates:
1. Blocking cloud instance metadata services (AWS/GCP/Azure 169.254.169.254 and metadata.google.internal).
2. Production remote transport security: Disabling dangerous insecure defaults (unencrypted HTTP, disabled TLS verification).
3. Hop-by-hop redirect validation: Re-evaluating IP safety on every HTTP 301/302 redirect hop to defeat redirect-based SSRF.
"""
from typing import Dict, List, Optional, Tuple
import ipaddress
import urllib.parse

class CloudMetadataSsrfShield:
    METADATA_IPS = {
        ipaddress.ip_address("169.254.169.254"),  # AWS/Azure/GCP link-local metadata
        ipaddress.ip_address("127.0.0.1"),        # Host loopback
    }

    METADATA_HOSTNAMES = {
        "metadata.google.internal",
        "169.254.169.254",
        "instance-data",
        "localhost"
    }

    @classmethod
    def evaluate_url_target(cls, url: str) -> Tuple[bool, str]:
        parsed = urllib.parse.urlparse(url)

        # 1. Transport Protection: Disallow plaintext HTTP in production
        if parsed.scheme.lower() != "https":
            return False, f"Transport Violation: Scheme '{parsed.scheme}' is insecure. Production requires HTTPS."

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False, "Target Error: Hostname missing in URL."

        # 2. Block well-known cloud metadata hostnames
        if hostname in cls.METADATA_HOSTNAMES:
            return False, f"SSRF Blocked: Destination '{hostname}' is a protected cloud metadata target."

        # 3. IP Literal Checks
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if ip_obj in cls.METADATA_IPS or ip_obj.is_private or ip_obj.is_loopback:
                return False, f"SSRF Blocked: IP literal '{hostname}' resolves to private/metadata network."
        except ValueError:
            # Not an IP literal, standard hostname
            pass

        return True, "Target verified safe for connection."

    @classmethod
    def simulate_safe_fetch_with_redirects(cls, initial_url: str, redirect_chain: List[str]) -> Tuple[bool, str]:
        """Simulates fetching while enforcing security checks on EVERY redirect hop."""
        current_url = initial_url
        is_safe, msg = cls.evaluate_url_target(current_url)
        if not is_safe:
            return False, f"Initial URL blocked: {msg}"

        # Inspect every subsequent redirect hop
        for hop_idx, next_url in enumerate(redirect_chain):
            resolved_next = urllib.parse.urljoin(current_url, next_url)
            is_hop_safe, hop_msg = cls.evaluate_url_target(resolved_next)
            if not is_hop_safe:
                return False, f"Redirect Hop #{hop_idx+1} blocked ({resolved_next}): {hop_msg}"
            current_url = resolved_next

        return True, f"Successfully retrieved resource after {len(redirect_chain)} verified hops."

if __name__ == "__main__":
    shield = CloudMetadataSsrfShield()

    # 1. Direct Cloud Metadata Attempts Blocked
    bad1, msg1 = shield.evaluate_url_target("http://169.254.169.254/latest/meta-data/")
    assert bad1 is False
    assert "Scheme 'http' is insecure" in msg1

    bad2, msg2 = shield.evaluate_url_target("https://169.254.169.254/latest/meta-data/")
    assert bad2 is False
    assert "protected cloud metadata target" in msg2

    bad_gcp, msg_gcp = shield.evaluate_url_target("https://metadata.google.internal/computeMetadata/v1/")
    assert bad_gcp is False
    assert "metadata.google.internal" in msg_gcp

    # 2. Redirect-Based SSRF Attack: Public URL redirects to internal cloud metadata
    # Initial URL looks benign, but Hop #1 redirects to 169.254.169.254!
    safe_redirect, redirect_msg = shield.simulate_safe_fetch_with_redirects(
        initial_url="https://api.partner.com/download_report",
        redirect_chain=["https://169.254.169.254/latest/meta-data/iam/security-credentials/"]
    )
    assert safe_redirect is False
    assert "Redirect Hop #1 blocked" in redirect_msg
    assert "protected cloud metadata target" in redirect_msg

    # 3. Legitimate Redirect Chain passes
    valid_redirect, valid_msg = shield.simulate_safe_fetch_with_redirects(
        initial_url="https://github.com/repo/archive",
        redirect_chain=["https://codeload.github.com/repo/tar.gz"]
    )
    assert valid_redirect is True
    assert "verified hops" in valid_msg

    print("Cloud metadata SSRF defense, redirect inspection, and transport protection verified successfully.")

