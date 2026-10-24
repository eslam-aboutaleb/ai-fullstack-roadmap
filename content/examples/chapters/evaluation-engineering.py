def gate(report):
    return (report["unauthorized_effects"] == 0
            and report["duplicate_writes"] == 0
            and report["completed_tasks"] / report["tasks"] >= 0.9
            and report["p95_ms"] <= 5000)
assert not gate({"unauthorized_effects": 1, "duplicate_writes": 0,
                 "completed_tasks": 100, "tasks": 100, "p95_ms": 100})
# Thresholds are toy values: derive real gates from product requirements.
