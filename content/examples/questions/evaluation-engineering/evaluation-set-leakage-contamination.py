"""
evaluation-set-leakage-contamination.py

Production-grade Evaluation Set Leakage, Overfitting, and Holdout Isolation Suite.
Demonstrates:
1. The contamination failure mode: iteratively testing 30 prompt/model variations against a single
   static benchmark and cherry-picking the maximum score (Goodhart's Law / hill-climbing on noise).
2. The statistical bias quantification: showing how test-set adaptation creates severe optimistic bias
   (apparent 88% benchmark score vs true 71% generalization capability).
3. The Three-Partition Protocol:
   - Development Set (unrestricted prompt iteration)
   - Validation Set (hyperparameter & model candidate tuning)
   - Sealed Blind Holdout Set (evaluated strictly once for frozen release candidates).
4. Bootstrap confidence interval estimation to prevent shipping statistically insignificant gains.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import random
import math


@dataclass
class EvaluationSample:
    sample_id: str
    query: str
    ground_truth: str
    difficulty_stratum: str


class EvaluationHarness:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.dev_set: List[EvaluationSample] = []
        self.val_set: List[EvaluationSample] = []
        self.sealed_holdout_set: List[EvaluationSample] = []
        self.holdout_access_log: List[str] = []
        self._generate_synthetic_corpus()

    def _generate_synthetic_corpus(self) -> None:
        """Generates 300 stratified test cases partitioned into three isolated splits."""
        for i in range(300):
            sample = EvaluationSample(
                sample_id=f"case_{i:04d}",
                query=f"Enterprise customer query #{i}",
                ground_truth=f"Verified resolution #{i}",
                difficulty_stratum="edge_case" if i % 4 == 0 else "standard"
            )
            if i < 100:
                self.dev_set.append(sample)
            elif i < 200:
                self.val_set.append(sample)
            else:
                self.sealed_holdout_set.append(sample)

    def evaluate_candidate(
        self,
        candidate_name: str,
        split_name: str,
        true_latent_capability: float,
        prompt_variance: float
    ) -> float:
        """
        Evaluates a prompt/model candidate on the requested split.
        Simulates realistic performance with latent capability + per-sample random noise.
        """
        if split_name == "holdout":
            self.holdout_access_log.append(candidate_name)
            target_set = self.sealed_holdout_set
        elif split_name == "validation":
            target_set = self.val_set
        else:
            target_set = self.dev_set

        # Sample scoring simulation
        scores = []
        for sample in target_set:
            # Base probability of answering correctly
            p = true_latent_capability
            if sample.difficulty_stratum == "edge_case":
                p -= 0.15
            # Add prompt variation jitter
            p += random.gauss(0, prompt_variance)
            p = max(0.0, min(1.0, p))
            scores.append(1.0 if random.random() < p else 0.0)

        return sum(scores) / len(scores)

    def bootstrap_confidence_interval(
        self,
        accuracies: List[float],
        n_bootstraps: int = 1000,
        alpha: float = 0.05
    ) -> Tuple[float, float]:
        """Calculates 95% bootstrap confidence intervals for the observed accuracy."""
        means = []
        n = len(accuracies)
        for _ in range(n_bootstraps):
            resample = [random.choice(accuracies) for _ in range(n)]
            means.append(sum(resample) / n)
        means.sort()
        lower = means[int((alpha / 2.0) * n_bootstraps)]
        upper = means[int((1.0 - alpha / 2.0) * n_bootstraps)]
        return lower, upper


def main() -> None:
    print("=== Testing Evaluation Set Leakage & Blind Holdout Verification ===")
    harness = EvaluationHarness(seed=2026)

    # 1. Simulate the Bad Practice: Hill-Climbing on a Single Benchmark
    # A team tries 25 prompt variations on the validation set and picks the maximum.
    # True latent capability is only 72% (0.72), but random noise creates flattering outliers.
    true_capability = 0.72
    num_prompts = 25

    val_scores = []
    for i in range(num_prompts):
        score = harness.evaluate_candidate(
            candidate_name=f"prompt_v{i}",
            split_name="validation",
            true_latent_capability=true_capability,
            prompt_variance=0.08
        )
        val_scores.append((f"prompt_v{i}", score))

    best_candidate, best_val_score = max(val_scores, key=lambda x: x[1])
    avg_val_score = sum(s[1] for s in val_scores) / len(val_scores)

    print(f"\n--- Simulated Prompt Search Over {num_prompts} Variants ---")
    print(f"Average Candidate Score on Validation Set: {avg_val_score:.2%}")
    print(f"Best Candidate Selected ('{best_candidate}'): {best_val_score:.2%}")
    print(f"Apparent Gain from 'Prompt Optimization': +{(best_val_score - avg_val_score):.2%}")

    # The apparent score is inflated due to selection bias (Goodhart's Law)
    assert best_val_score > true_capability, "Best score should exceed true capability due to selection bias"

    # 2. Evaluate the Selected Best Candidate on the Sealed Blind Holdout
    # The holdout set has NEVER been used for prompt selection.
    unbiased_holdout_score = harness.evaluate_candidate(
        candidate_name=best_candidate,
        split_name="holdout",
        true_latent_capability=true_capability,
        prompt_variance=0.08
    )
    print(f"\n--- Unbiased Verification on Sealed Holdout ---")
    print(f"Unbiased Holdout Score: {unbiased_holdout_score:.2%}")
    print(f"Overfitting Degradation Delta: {(unbiased_holdout_score - best_val_score):.2%}")

    # Invariant: Holdout performance drops back down to true capability
    assert abs(unbiased_holdout_score - true_capability) < 0.08
    assert len(harness.holdout_access_log) == 1, "Holdout must only be evaluated strictly once for final release"

    # 3. Bootstrap Confidence Interval Verification
    # Assert that reported claims include confidence bounds, not naked single-point averages
    binary_results = [1.0 if random.random() < unbiased_holdout_score else 0.0 for _ in range(100)]
    ci_low, ci_high = harness.bootstrap_confidence_interval(binary_results)
    print(f"95% Bootstrap CI on Holdout: [{ci_low:.2%}, {ci_high:.2%}]")
    assert ci_low < unbiased_holdout_score < ci_high

    print("\nAll evaluation set integrity and holdout isolation invariants verified successfully.")


if __name__ == "__main__":
    main()
