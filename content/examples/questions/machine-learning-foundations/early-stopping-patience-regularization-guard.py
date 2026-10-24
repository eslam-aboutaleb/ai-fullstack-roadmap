#!/usr/bin/env python3
"""
Executable test suite demonstrating early stopping on validation loss trajectories
and guarding against test-set peeking and data contamination.

Addresses Interview Question 931:
"How should regularization and early stopping use validation data?"
"""

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EpochMetrics:
    epoch: int
    train_loss: float
    val_loss: float
    test_loss: float
    weights: float


class EarlyStoppingManager:
    """
    Monitors validation loss with patience window.
    Halts training when validation loss fails to improve for `patience` consecutive epochs.
    Restores weights corresponding strictly to the best validation checkpoint.
    """
    def __init__(self, patience: int = 3, min_delta: float = 1e-4) -> None:
        self.patience: int = patience
        self.min_delta: float = min_delta
        self.best_val_loss: float = float("inf")
        self.best_epoch: int = -1
        self.best_weights: Optional[float] = None
        self.wait: int = 0
        self.stopped_epoch: Optional[int] = None

    def step(self, epoch: int, val_loss: float, current_weights: float) -> bool:
        """Returns True if training should stop early."""
        if val_loss < (self.best_val_loss - self.min_delta):
            self.best_val_loss = val_loss
            self.best_epoch = epoch
            self.best_weights = current_weights
            self.wait = 0
            return False
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.stopped_epoch = epoch
                return True
            return False


def run_test_suite() -> None:
    # Simulated training trajectory:
    # Training loss continually falls towards zero (memorizing noise).
    # Validation loss reaches minimum at Epoch 4 and starts diverging (overfitting).
    # Test loss tracks validation distribution.
    history = [
        EpochMetrics(epoch=1, train_loss=0.85, val_loss=0.88, test_loss=0.89, weights=1.2),
        EpochMetrics(epoch=2, train_loss=0.62, val_loss=0.66, test_loss=0.67, weights=1.8),
        EpochMetrics(epoch=3, train_loss=0.45, val_loss=0.52, test_loss=0.54, weights=2.3),
        EpochMetrics(epoch=4, train_loss=0.32, val_loss=0.48, test_loss=0.50, weights=2.7), # Optimal val checkpoint
        EpochMetrics(epoch=5, train_loss=0.22, val_loss=0.51, test_loss=0.53, weights=3.1), # Overfitting begins
        EpochMetrics(epoch=6, train_loss=0.15, val_loss=0.56, test_loss=0.58, weights=3.5),
        EpochMetrics(epoch=7, train_loss=0.09, val_loss=0.64, test_loss=0.66, weights=3.9), # Patience 3 expires here
        EpochMetrics(epoch=8, train_loss=0.04, val_loss=0.75, test_loss=0.77, weights=4.3),
        EpochMetrics(epoch=9, train_loss=0.01, val_loss=0.88, test_loss=0.91, weights=4.8),
    ]

    # 1. Execute Early Stopping on Validation Metric:
    early_stopper = EarlyStoppingManager(patience=3)
    stopped = False

    for m in history:
        should_stop = early_stopper.step(m.epoch, m.val_loss, m.weights)
        if should_stop:
            stopped = True
            break

    # Early stopping correctly halted training at epoch 7 after 3 non-improving epochs:
    assert stopped is True
    assert early_stopper.stopped_epoch == 7
    # Optimal checkpoint correctly tracked epoch 4 with best validation loss 0.48:
    assert early_stopper.best_epoch == 4
    assert abs(early_stopper.best_val_loss - 0.48) < 1e-4
    assert early_stopper.best_weights == 2.7

    # 2. Guard against Test-Set Contamination:
    # Anti-pattern: Stopping at the epoch that minimized TEST loss directly.
    # While epoch 4 happens to be minimal for both here, using test loss for stopping
    # converts the test set into a validation set, destroying its uncompromised guarantee.
    # Invariant: The early stopping decision must be computationally independent of test_loss.
    best_test_eval = [m for m in history if m.epoch == early_stopper.best_epoch][0]
    final_overfitted_eval = history[-1]

    # Best early-stopped model dramatically outperforms the overfitted final epoch on test loss:
    assert best_test_eval.test_loss < final_overfitted_eval.test_loss * 0.6, (
        f"Early-stopped test loss {best_test_eval.test_loss} must beat overfitted {final_overfitted_eval.test_loss}"
    )

    print("All early stopping patience regularization guard assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

