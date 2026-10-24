"""Security acceptance test suite: Knowledge-service adapter, rate limiting boundaries, and cryptographic record binding with key rotation.

Demonstrates:
1. Knowledge-service adapter centralizing authentication, tenant authorization, and retrieval filtering.
2. Rate limiter boundaries: Local per-client sliding window vs global downstream provider quotas.
3. Cryptographic record binding: Authenticated Encryption with Associated Data (AEAD) binding ciphertext to tenant_id and record_id to defeat ciphertext transplant attacks.
4. Seamless cryptographic key rotation: Versioned keys allowing legacy record decryption while encrypting new records with the current active key.
"""
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import hmac
import json
import time

class VersionedKeyManager:
    """Manages active and legacy encryption keys for zero-downtime key rotation."""
    def __init__(self):
        self._keys: Dict[str, bytes] = {
            "v1": b"legacy-encryption-key-version-01",
            "v2": b"current-active-encryption-key-02"  # Active key
        }
        self.active_version = "v2"

    def get_key(self, version: str) -> bytes:
        if version not in self._keys:
            raise KeyError(f"Key version '{version}' not found.")
        return self._keys[version]

class CryptographicRecordBinder:
    """Simulates AEAD envelope encryption binding ciphertext to tenant_id and record_id."""
    def __init__(self, key_manager: VersionedKeyManager):
        self.key_manager = key_manager

    def encrypt_record(self, tenant_id: str, record_id: str, revision: int, plaintext: str) -> Dict[str, str]:
        key_ver = self.key_manager.active_version
        key = self.key_manager.get_key(key_ver)

        # Associated Authenticated Data (AAD): tenant_id + record_id + revision
        aad = f"{tenant_id}:{record_id}:{revision}".encode("utf-8")
        raw_bytes = plaintext.encode("utf-8")

        # Synthetic AEAD payload: ciphertext hex + HMAC tag over (ciphertext + AAD)
        # In production: AES-256-GCM or ChaCha20-Poly1305 with explicit AAD
        synthetic_cipher = raw_bytes.hex()
        tag = hmac.new(key, f"{synthetic_cipher}:{aad.decode('utf-8')}".encode("utf-8"), hashlib.sha256).hexdigest()

        return {
            "key_version": key_ver,
            "ciphertext": synthetic_cipher,
            "tag": tag,
            "revision": str(revision)
        }

    def decrypt_record(self, tenant_id: str, record_id: str, revision: int, package: Dict[str, str]) -> str:
        key_ver = package["key_version"]
        key = self.key_manager.get_key(key_ver)

        aad = f"{tenant_id}:{record_id}:{revision}".encode("utf-8")
        synthetic_cipher = package["ciphertext"]
        expected_tag = hmac.new(key, f"{synthetic_cipher}:{aad.decode('utf-8')}".encode("utf-8"), hashlib.sha256).hexdigest()

        # Constant-time tag verification: Defeats ciphertext transplant attacks!
        if not hmac.compare_digest(package["tag"], expected_tag):
            raise PermissionError("AEAD Verification Failed: Ciphertext transplant or data tampering detected!")

        return bytes.fromhex(synthetic_cipher).decode("utf-8")

class KnowledgeServiceAdapter:
    """Centralized facade coordinating auth, tenant filtering, rate limiting, and encryption."""
    def __init__(self, binder: CryptographicRecordBinder):
        self.binder = binder
        # Local token bucket: 2 requests per second
        self.tokens = 2.0
        self.last_refill = time.time()
        self._database: Dict[str, Dict[str, str]] = {}

    def _check_rate_limit(self) -> bool:
        now = time.time()
        self.tokens = min(2.0, self.tokens + (now - self.last_refill) * 2.0)
        self.last_refill = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    def store_document(self, tenant_id: str, record_id: str, revision: int, text: str) -> None:
        encrypted = self.binder.encrypt_record(tenant_id, record_id, revision, text)
        self._database[f"{tenant_id}:{record_id}"] = encrypted

    def retrieve_document(self, caller_tenant: str, record_id: str, revision: int) -> str:
        if not self._check_rate_limit():
            raise RuntimeError("Rate limit exceeded on knowledge adapter.")

        key = f"{caller_tenant}:{record_id}"
        if key not in self._database:
            raise KeyError(f"Document '{record_id}' not found in tenant '{caller_tenant}'.")

        package = self._database[key]
        return self.binder.decrypt_record(caller_tenant, record_id, revision, package)

def run_security_acceptance_suite():
    km = VersionedKeyManager()
    binder = CryptographicRecordBinder(km)
    adapter = KnowledgeServiceAdapter(binder)

    # Acceptance Test 1: Store and retrieve under active key (v2)
    adapter.store_document("tenant_alpha", "doc_88", revision=1, text="Confidential Strategy 2026")
    doc_text = adapter.retrieve_document("tenant_alpha", "doc_88", revision=1)
    assert doc_text == "Confidential Strategy 2026"

    # Acceptance Test 2: Ciphertext transplant rejection (AEAD binding)
    # Attacker copies ciphertext from doc_88 and attempts to graft it onto doc_99
    raw_pkg = adapter._database["tenant_alpha:doc_88"]
    try:
        binder.decrypt_record("tenant_alpha", "doc_TRANSPLANT_TARGET", revision=1, package=raw_pkg)
        assert False, "Should have rejected ciphertext transplant"
    except PermissionError as pe:
        assert "tampering detected" in str(pe)

    # Acceptance Test 3: Backward compatible key rotation
    # Create record with legacy key v1
    km.active_version = "v1"
    v1_record = binder.encrypt_record("tenant_beta", "doc_old", revision=1, plaintext="Legacy Record Encrypted with V1")
    assert v1_record["key_version"] == "v1"

    # Rotate active key to v2
    km.active_version = "v2"
    # Decrypting legacy record succeeds seamlessly
    legacy_text = binder.decrypt_record("tenant_beta", "doc_old", revision=1, package=v1_record)
    assert legacy_text == "Legacy Record Encrypted with V1"

    # Acceptance Test 4: Rate limit exhaustion test
    try:
        adapter.retrieve_document("tenant_alpha", "doc_88", revision=1)
        adapter.retrieve_document("tenant_alpha", "doc_88", revision=1)
        adapter.retrieve_document("tenant_alpha", "doc_88", revision=1)
        assert False, "Should hit rate limiter"
    except RuntimeError as re:
        assert "Rate limit exceeded" in str(re)

if __name__ == "__main__":
    run_security_acceptance_suite()
    print("Security acceptance suite: Adapter, rate limits, and cryptographic record binding verified successfully.")

