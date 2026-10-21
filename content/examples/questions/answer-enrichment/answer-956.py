def parse_count(value):
    if value is None:
        return None
    if not isinstance(value, str) or not value.isdecimal():
        raise ValueError("count must be decimal text")
    return int(value)
assert parse_count(None) is None
assert parse_count("0") == 0
try:
    parse_count("zero")
except ValueError:
    print("absent=None; valid=0; invalid=ValueError")
else:
    raise AssertionError("invalid input was accepted")
