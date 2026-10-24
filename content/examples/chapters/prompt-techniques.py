ALLOWED = {"search", "read_source", "draft"}
def validate_plan(plan, limit=4):
    if not 1 <= len(plan) <= limit: raise ValueError("step budget")
    for step in plan:
        if step["action"] not in ALLOWED: raise PermissionError("unavailable action")
    return plan
assert validate_plan([{"action": "search"}, {"action": "draft"}])
# No side effects occur here. Each actual tool call needs its own policy check.
