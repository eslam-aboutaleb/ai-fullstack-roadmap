"""Explicit numeric decision policy, not probability calibration."""
def decide(top_score, margin, minimum, min_margin):
    return 'accept' if top_score >= minimum and margin >= min_margin else 'review'
assert decide(0.8,0.1,0.7,0.05) == 'accept'
assert decide(0.8,0.1,0.9,0.05) == 'review'
assert decide(0.8,0.01,0.7,0.05) == 'review'
print('score and ambiguity policy determine acceptance; unknown detection still needs evaluation')
