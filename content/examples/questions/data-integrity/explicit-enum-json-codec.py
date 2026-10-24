"""A domain-to-wire codec restores enum meaning explicitly."""
import json
from dataclasses import asdict, dataclass
from enum import Enum
class Status(Enum):
    APPROVED = 'approved'
@dataclass(frozen=True)
class Record:
    status: Status
record = Record(Status.APPROVED)
try:
    json.dumps(asdict(record))
except TypeError:
    pass
else:
    raise AssertionError('raw Enum unexpectedly serialized')
payload = json.dumps(dict(schema_version=1, status=record.status.value), allow_nan=False)
wire = json.loads(payload)
if wire['schema_version'] != 1:
    raise ValueError('unsupported schema')
restored = Record(Status(wire['status']))
assert restored == record and restored.status is Status.APPROVED
print('raw enum rejected; explicit codec round trip restored domain type')
