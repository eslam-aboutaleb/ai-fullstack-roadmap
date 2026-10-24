# Mechanism-first mathematics, ML and transformers interview labs (#16)

**Introduction.** Learning a formula is not enough for AI systems engineering:
state the underlying event/tensor dimensions, compute a small case by hand,
test an implementation, and explain which assumptions fail in deployment.

This increment adds five extensive interview answers to existing companion
units covering Bayesian base rates and classification precision; analytic vs
finite-difference gradients; grouped/time-aware data leakage; stable, masked
attention; and an explicit GPU KV-cache memory calculation. Each has a
changed-assumption answered follow-up and a practical debugging objective.

Run `python3 -B labs/math_interview_mechanics.py`. Its standard-library
assertions check a rare-event Bayesian classifier example, one gradient-descent
step vs finite differences, numerically stable and causally masked softmax,
attention shape validations and invalid all-masked rows. The source uses a
tiny deterministic CPU fixture, not a trained foundation model or GPU benchmark.

The existing scikit-learn digits study, NumPy–PyTorch bridge and tiny LoRA
adapter remain useful for model-training practice. This PR does not claim
to finish the whole deep-learning syllabus, validate foundation-model SFT
or independently review every legacy equation and diagram.

**Interview answer pattern:** define variables and shapes → derive the formula
step by step → compute with explicit numbers → run or trace code → explain a
counterexample/leakage/precision failure → defend the trade-off in a real
pipeline → answer a changed-assumption follow-up.
