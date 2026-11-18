"""Index enriched text for retrieval, but keep the original passage as generation evidence."""
import re

CHUNK = "The threshold is reduced to 10 seconds in fast mode."
CONTEXT = "AUTOSAR Watchdog Driver Specification, section Watchdog Modes: describes watchdog timeout behavior."


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def overlap(query, text):
    return len(tokens(query) & tokens(text))


QUERY = "watchdog fast mode timeout threshold"
record = {
    "original": CHUNK,                      # shown to the generator and cited
    "index_text": CONTEXT + " " + CHUNK,    # embedded or lexically indexed
    "context_origin": "heading-derived",    # generated context is never source evidence
}
before = overlap(QUERY, record["original"])
after = overlap(QUERY, record["index_text"])
assert after > before and record["original"] == CHUNK
print("overlap_before", before, "overlap_after", after, record["context_origin"])
