from io import StringIO
handle = StringIO("first\nsecond\n")
try:
    with handle:
        assert next(handle).strip() == "first"
        raise ValueError("stop during consumption")
except ValueError:
    pass
assert handle.closed
print("resource closed after consumer failure")
