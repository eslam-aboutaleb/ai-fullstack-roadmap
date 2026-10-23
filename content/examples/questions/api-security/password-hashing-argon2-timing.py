"""Production password hashing architecture: Salt generation, work factor tuning, timing attack defenses, and rehash migration.

Demonstrates:
1. OWASP-compliant key derivation: PBKDF2-HMAC-SHA256 with 600,000 iterations and cryptographically random 16-byte salt.
2. Constant-time comparison (hmac.compare_digest) to eliminate timing side-channel attacks during authentication.
3. Work factor evolution & automatic rehashing: Transparently detecting obsolete iteration counts on successful login and upgrading to current security standards.
"""
from typing import Optional, Tuple
import hashlib
import hmac
import os

class PasswordSecurityManager:
    # OWASP 2024 recommended minimum for PBKDF2-HMAC-SHA256
    CURRENT_ITERATIONS = 600_000
    SALT_BYTES = 16
    KEY_LENGTH = 32

    @classmethod
    def hash_password(cls, password: str, iterations: Optional[int] = None) -> str:
        iters = iterations or cls.CURRENT_ITERATIONS
        salt = os.urandom(cls.SALT_BYTES)
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iters,
            dklen=cls.KEY_LENGTH
        )
        # Stored format: $pbkdf2-sha256$iterations$salt_hex$hash_hex
        return f"$pbkdf2-sha256${iters}${salt.hex()}${derived_key.hex()}"

    @classmethod
    def verify_password(cls, password: str, encoded_hash: str) -> bool:
        parts = encoded_hash.split("$")
        if len(parts) != 5 or parts[1] != "pbkdf2-sha256":
            return False

        iters = int(parts[2])
        salt = bytes.fromhex(parts[3])
        expected_key = bytes.fromhex(parts[4])

        computed_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iters,
            dklen=cls.KEY_LENGTH
        )

        # CRITICAL TIMING DEFENSE: hmac.compare_digest prevents timing side-channels!
        return hmac.compare_digest(computed_key, expected_key)

    @classmethod
    def needs_rehash(cls, encoded_hash: str) -> bool:
        """Checks if stored hash was created with an obsolete iteration count."""
        parts = encoded_hash.split("$")
        if len(parts) != 5:
            return True
        iters = int(parts[2])
        return iters < cls.CURRENT_ITERATIONS

if __name__ == "__main__":
    pwd_mgr = PasswordSecurityManager()
    plain_password = "CorrectHorseBatteryStaple#2024!"

    # 1. Hash generation with current work factor
    stored_hash = pwd_mgr.hash_password(plain_password)
    assert stored_hash.startswith(f"$pbkdf2-sha256${pwd_mgr.CURRENT_ITERATIONS}$")

    # 2. Successful verification with constant-time check
    assert pwd_mgr.verify_password(plain_password, stored_hash) is True

    # 3. Incorrect password fails
    assert pwd_mgr.verify_password("WrongPassword!", stored_hash) is False

    # 4. Hash does not need rehash when matching current iterations
    assert pwd_mgr.needs_rehash(stored_hash) is False

    # 5. Legacy password hash migration: User account created years ago with 100k iterations
    legacy_hash = pwd_mgr.hash_password(plain_password, iterations=100_000)
    assert pwd_mgr.verify_password(plain_password, legacy_hash) is True
    # System flags that legacy hash requires upgrade!
    assert pwd_mgr.needs_rehash(legacy_hash) is True

    # Automatic upgrade executed on successful login
    upgraded_hash = pwd_mgr.hash_password(plain_password)
    assert pwd_mgr.needs_rehash(upgraded_hash) is False
    assert pwd_mgr.verify_password(plain_password, upgraded_hash) is True

    print("Password hashing, timing attack defense, and rehash migration verified successfully.")
