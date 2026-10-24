from datetime import date
def applicable(event_date, start, end):
    return start <= event_date and (end is None or event_date < end)
assert applicable(date(2026, 1, 1), date(2026, 1, 1), date(2027, 1, 1))
assert not applicable(date(2027, 1, 1), date(2026, 1, 1), date(2027, 1, 1))
# Actual domain applicability rules must be specified and reviewed separately.
