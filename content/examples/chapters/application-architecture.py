from dataclasses import dataclass
@dataclass(frozen=True)
class Result:
    operation_id: str
    status: str
    record_id: str | None = None
def completed(result):
    return result.status == "complete" and result.record_id is not None
assert not completed(Result("op-demo", "accepted"))
