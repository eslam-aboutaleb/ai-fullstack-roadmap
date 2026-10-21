from dataclasses import dataclass, field
@dataclass
class Batch:
    records: list = field(default_factory=list)
a, b = Batch(), Batch()
a.records.append("R1")
assert b.records == [] and a.records is not b.records
print("default_factory creates independent lists")
