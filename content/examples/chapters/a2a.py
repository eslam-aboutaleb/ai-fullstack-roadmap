def public_state(remote_status):
    mapping = {"submitted": "waiting", "working": "running",
               "input-required": "needs_input", "completed": "complete",
               "failed": "failed", "canceled": "cancelled"}
    return mapping.get(remote_status, "unknown")
assert public_state("new-status") == "unknown"
# Implement actual wire messages with a pinned compatible A2A SDK.
