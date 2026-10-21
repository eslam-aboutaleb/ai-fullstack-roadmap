"""Synthetic selective accuracy and coverage; scores are not calibration evidence."""
rows = [('A', 'A', 0.95), ('B', 'A', 0.40), ('B', 'B', 0.90)]
threshold = 0.8
accepted = [(truth, prediction) for truth, prediction, score in rows if score >= threshold]
accuracy = sum(truth == prediction for truth, prediction in accepted) / len(accepted) if accepted else None
coverage = len(accepted) / len(rows)
assert accuracy == 1.0 and len(accepted) == 2
assert abs(coverage - 2 / 3) < 1e-12
empty = [row for row in rows if row[2] >= 1.0]
assert not empty
print('accepted accuracy: 1.0; coverage: 2/3; empty acceptance is unmeasured')
