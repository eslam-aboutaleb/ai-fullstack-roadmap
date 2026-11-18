"""Select the policy version applicable at a business date, optionally as known at a past time."""
from datetime import date

VERSIONS = [
    {"id": "policy-2025", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "known_at": date(2024, 12, 20), "notice_days": 15},
    {"id": "policy-2026", "valid_from": date(2026, 1, 1), "valid_to": date(2026, 12, 31), "known_at": date(2025, 11, 30), "notice_days": 30},
]


def applicable(as_of, known_at=None):
    return [v["id"] for v in VERSIONS
            if v["valid_from"] <= as_of <= v["valid_to"]
            and (known_at is None or v["known_at"] <= known_at)]


assert applicable(date(2025, 6, 15)) == ["policy-2025"]
assert applicable(date(2026, 6, 15)) == ["policy-2026"]
assert applicable(date(2026, 6, 15), known_at=date(2025, 6, 1)) == []
print(applicable(date(2025, 6, 15)), applicable(date(2026, 6, 15)), applicable(date(2026, 6, 15), date(2025, 6, 1)))
