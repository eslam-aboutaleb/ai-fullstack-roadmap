"""Demonstrate time-ordered UUIDv7 internal surrogate keys vs decoupled public external IDs."""
import time
import os
import secrets
import string

def generate_uuidv7():
    """Simulate RFC 9562 UUIDv7: 48-bit millisecond timestamp + version + sequence/random bits."""
    timestamp_ms = int(time.time() * 1000)
    # 48 bits timestamp (12 hex digits)
    time_hex = f"{timestamp_ms:012x}"
    # Random 74 bits
    rand_bytes = os.urandom(10)
    rand_hex = rand_bytes.hex()
    
    # Format as 8-4-4-4-12 UUID format with version 7 and variant 10xx
    part1 = time_hex[:8]
    part2 = time_hex[8:12]
    part3 = "7" + rand_hex[:3] # version 7
    part4 = "8" + rand_hex[3:6] # variant 1
    part5 = rand_hex[6:18]
    return f"{part1}-{part2}-{part3}-{part4}-{part5}"

def generate_public_id(prefix="req"):
    """Generate high-entropy opaque public ID with prefix (TypeID style) preventing enumeration attacks."""
    alphabet = string.ascii_lowercase + string.digits
    entropy = ''.join(secrets.choice(alphabet) for _ in range(21))
    return f"{prefix}_{entropy}"

# 1. Monotonic ordering of internal UUIDv7 (preserves B-Tree index locality):
ids = [generate_uuidv7() for _ in range(5)]
assert ids == sorted(ids), "UUIDv7 keys are time-ordered and insert monotonically into B-Tree"

# 2. Decoupled public ID:
# Never expose internal database surrogate keys to HTTP clients.
# Sequential integers or time-based IDs leak velocity and invite scraping/enumeration.
public_id = generate_public_id("doc")

database_row = {
    "internal_pk": ids[0],          # Used for foreign keys, joins, and B-Tree indexing
    "public_id": public_id,         # Exposed in REST API / URLs (e.g. /api/v1/documents/doc_9a7b2...)
    "owner_id": "usr_42",
    "title": "Architecture Specification"
}

print(f"Decoupled keys: internal_pk={database_row['internal_pk']} (UUIDv7), public_id={database_row['public_id']}")
