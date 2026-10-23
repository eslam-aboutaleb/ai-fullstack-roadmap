"""Demonstrate KV (Key-Value) cache prefix reuse and avoiding dynamic prefix cache-busting."""
import hashlib

class KVCacheSimulator:
    def __init__(self):
        # Simulated server-side attention KV cache keyed by SHA-256 prefix hash
        self.cached_prefixes = {}

    def process_prompt(self, system_prefix, dynamic_suffix):
        prefix_hash = hashlib.sha256(system_prefix.encode()).hexdigest()
        
        # Check if byte-identical prefix is already cached in GPU memory:
        if prefix_hash in self.cached_prefixes:
            cache_hit = True
            prefill_tokens_processed = len(dynamic_suffix.split()) # Only prefill dynamic suffix!
        else:
            cache_hit = False
            self.cached_prefixes[prefix_hash] = True
            prefill_tokens_processed = len(system_prefix.split()) + len(dynamic_suffix.split())

        return cache_hit, prefill_tokens_processed

kv_cache = KVCacheSimulator()

# 1. BEST PRACTICE: Static, byte-identical system prompt prefix
# Tools, system rules, and static few-shot examples placed in immutable prefix:
static_system_prefix = "You are an enterprise AI assistant. Rules: 1. Strict tenant isolation. 2. Output valid JSON."

# Dynamic user queries placed in suffix:
hit1, prefill1 = kv_cache.process_prompt(static_system_prefix, "User request A: summarize incident 401.")
assert hit1 is False, "First request warms the KV cache"

hit2, prefill2 = kv_cache.process_prompt(static_system_prefix, "User request B: summarize incident 402.")
assert hit2 is True, "Second request reuses cached prefix KV states!"
assert prefill2 < prefill1, "Prefill latency reduced because prefix was cached"

# 2. ANTI-PATTERN (Cache-Busting):
# Inserting dynamic timestamps or request IDs at the start of the prefix:
def bad_prefix_with_timestamp(timestamp_str):
    return f"Timestamp: {timestamp_str}\nYou are an enterprise AI assistant. Rules: 1. Strict tenant isolation."

hit_bad1, _ = kv_cache.process_prompt(bad_prefix_with_timestamp("14:00:01"), "Query 1")
hit_bad2, _ = kv_cache.process_prompt(bad_prefix_with_timestamp("14:00:02"), "Query 2")

assert hit_bad1 is False and hit_bad2 is False, "Dynamic timestamp destroyed KV cache reuse!"

print(f"KV cache prefix reuse verified: static_prefix_cached={hit2} (prefill={prefill2} tokens), dynamic_busted={hit_bad2}")
