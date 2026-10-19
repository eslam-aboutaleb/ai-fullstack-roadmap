from dataclasses import dataclass
@dataclass(frozen=True)
class Evidence:
    status: str
    passages: tuple[str, ...]
def route(evidence):
    if evidence.status == "unavailable": return "try_later"
    if not evidence.passages: return "clarify_or_abstain"
    return "generate_and_check_support"
assert route(Evidence("ok", ())) == "clarify_or_abstain"
