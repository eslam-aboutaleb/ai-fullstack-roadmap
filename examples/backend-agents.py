def read_request(principal, request_id, repository):
    record = repository.get(request_id)
    if record is None or record["owner"] != principal["user"]:
        raise PermissionError("not accessible")
    return {"id": request_id, "status": record["status"]}
records = {"r1": {"owner": "u1", "status": "accepted"}}
assert read_request({"user": "u1"}, "r1", records)["status"] == "accepted"
# Replace the synthetic repository with a scoped query and trusted identity.
