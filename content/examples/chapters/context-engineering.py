from dataclasses import dataclass
@dataclass(frozen=True)
class Block:
    purpose: str
    origin: str
    trust: str
    text: str
blocks = [Block("instructions", "app-policy-v1", "trusted", "Answer from evidence."),
          Block("evidence", "doc-demo:r2", "untrusted", "Office hours are 9–5.")]
assert all(b.origin and b.purpose for b in blocks)
# Trust labels explain handling; backend policy still enforces permissions.
