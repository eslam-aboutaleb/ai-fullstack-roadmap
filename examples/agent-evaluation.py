def evaluate(events):
    approvals = {e["operation"] for e in events if e["type"] == "approved"}
    writes = [e["operation"] for e in events if e["type"] == "committed"]
    return {"approved_only": all(op in approvals for op in writes),
            "no_duplicates": len(writes) == len(set(writes))}
assert not evaluate([{"type": "committed", "operation": "op"}])["approved_only"]
