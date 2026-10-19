SAFE = {"task_id", "tool", "outcome", "latency_ms", "prompt_version"}
def safe_attributes(attributes):
    return {key: value for key, value in attributes.items() if key in SAFE}
assert "customer_text" not in safe_attributes({"task_id": "demo", "customer_text": "private"})
# IDs and retained metadata still require privacy review and access control.
