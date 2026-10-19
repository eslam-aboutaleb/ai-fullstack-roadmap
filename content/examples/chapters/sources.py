from dataclasses import dataclass
@dataclass(frozen=True)
class Scan:
    complete: bool
    ids: frozenset[str]
def removed(previous, scan):
    if not scan.complete:
        raise ValueError("source state is unknown")
    return previous - scan.ids
assert removed({"a", "b"}, Scan(True, frozenset({"b"}))) == {"a"}
