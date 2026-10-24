def can_read(principal, record):
    return (principal["tenant"] == record["tenant"]
            and record["owner"] == principal["user"])
principal = {"tenant": "t1", "user": "u1"}
assert not can_read(principal, {"tenant": "t2", "owner": "u1"})
# A real principal comes from verified authentication, never model arguments.
