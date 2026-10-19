def validate_answer(value):
    if not isinstance(value, dict): raise ValueError("object required")
    if set(value) != {"answer", "source_ids", "status"}: raise ValueError("fields")
    if value["status"] not in {"supported", "needs_input", "unavailable"}: raise ValueError("status")
    if not isinstance(value["answer"], str): raise ValueError("answer type")
    if not isinstance(value["source_ids"], list) or not all(isinstance(x, str) for x in value["source_ids"]):
        raise ValueError("source IDs")
    if value["status"] == "supported" and not value["source_ids"]: raise ValueError("evidence")
    return value
assert validate_answer({"answer": "Need a date", "source_ids": [], "status": "needs_input"})
# Validate factual support and source ownership separately.
