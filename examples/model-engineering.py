def selective_report(samples, threshold):
    chosen = [s for s in samples if s["score"] >= threshold]
    return {"coverage": len(chosen) / len(samples) if samples else 0,
            "accuracy": sum(s["correct"] for s in chosen) / len(chosen) if chosen else None}
assert selective_report([], 0.5)["accuracy"] is None
# Scores require task-specific calibration before thresholds become meaningful.
