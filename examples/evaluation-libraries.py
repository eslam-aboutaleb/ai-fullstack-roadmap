from dataclasses import dataclass
@dataclass(frozen=True)
class Measurement:
    metric: str
    implementation_version: str
    judge: str | None
    dataset_version: str
    score: float | None
result = Measurement("support_rubric", "v1", None, "synthetic-v1", 1.0)
assert result.dataset_version == "synthetic-v1"
