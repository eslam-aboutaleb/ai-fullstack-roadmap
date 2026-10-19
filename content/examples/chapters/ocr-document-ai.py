from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class Field:
    raw: str
    value: Decimal
    page: int
    bbox: tuple[float, float, float, float]
    source_revision: str
field = Field("12.50", Decimal("12.50"), 1, (0.1, 0.2, 0.3, 0.25), "demo-r1")
assert field.value == Decimal("12.50")
# Calibration, locale resolution, and domain review are separate from OCR extraction.
