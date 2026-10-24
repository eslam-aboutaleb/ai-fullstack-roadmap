"""Data quality quarantine and circuit breaker for streaming ingestion.

Demonstrates avoiding the 'silent dead-letter trap' in streaming data pipelines:
1. The silent dead-letter trap: routing malformed records to a Dead-Letter Queue (DLQ) while blindly
   advancing message offsets can mask a catastrophic breaking schema change. Pipeline throughput
   metrics look green, but 100% of events are dumped to quarantine, starving destination projections.
2. Dual-threshold quarantine policy:
   - Sporadic anomalies (e.g. < 5% error rate): isolate records into an auditable DLQ with error reasons
     while continuing pipeline progress for healthy data.
   - Systemic failures (e.g. > 20% error rate or consecutive failure threshold): trip an automated
     circuit breaker that halts offset advancement to prevent unrecoverable data loss.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


class PipelineHaltedException(RuntimeError):
    """Raised when quarantine error rate exceeds circuit-breaker threshold."""
    pass


@dataclass(frozen=True)
class IngestionRecord:
    offset: int
    payload: Dict[str, Any]


@dataclass(frozen=True)
class QuarantinedRecord:
    offset: int
    payload: Dict[str, Any]
    error_reason: str


class QuarantineCircuitBreakerPipeline:
    """Manages data quality validation with circuit-breaker protection."""

    def __init__(self, max_consecutive_failures: int = 3, max_error_rate: float = 0.20) -> None:
        self.max_consecutive_failures = max_consecutive_failures
        self.max_error_rate = max_error_rate
        self.processed_records: List[IngestionRecord] = []
        self.dead_letter_queue: List[QuarantinedRecord] = []
        self.last_committed_offset: int = -1

    def process_batch(self, batch: List[IngestionRecord]) -> Tuple[int, int]:
        """Processes a batch, quarantining errors or halting the pipeline."""
        batch_failures = 0
        consecutive_failures = 0

        for record in batch:
            # Rule: Record must contain non-empty 'user_id' and numeric 'amount'
            p = record.payload
            is_valid = bool(p.get("user_id")) and isinstance(p.get("amount"), (int, float))

            if is_valid:
                self.processed_records.append(record)
                consecutive_failures = 0
                self.last_committed_offset = record.offset
            else:
                batch_failures += 1
                consecutive_failures += 1
                self.dead_letter_queue.append(
                    QuarantinedRecord(
                        offset=record.offset,
                        payload=p,
                        error_reason="Missing user_id or invalid amount type",
                    )
                )

                # Circuit breaker check on consecutive systemic failures
                if consecutive_failures >= self.max_consecutive_failures:
                    raise PipelineHaltedException(
                        f"CIRCUIT BREAKER TRIPPED: {consecutive_failures} consecutive failures. "
                        f"Halting offset advancement at offset {self.last_committed_offset}."
                    )

        # Rate check across batch
        if batch:
            error_rate = batch_failures / len(batch)
            if error_rate > self.max_error_rate:
                raise PipelineHaltedException(
                    f"CIRCUIT BREAKER TRIPPED: Batch error rate {error_rate:.1%} exceeds allowed {self.max_error_rate:.1%}."
                )

        return len(self.processed_records), len(self.dead_letter_queue)


def run_test_suite() -> None:
    # 1. Test sporadic anomaly quarantine (1 corrupted record out of 5):
    pipeline = QuarantineCircuitBreakerPipeline(max_consecutive_failures=3, max_error_rate=0.25)

    batch_sporadic = [
        IngestionRecord(offset=100, payload={"user_id": "u1", "amount": 10.0}),
        IngestionRecord(offset=101, payload={"user_id": "u2", "amount": 20.0}),
        IngestionRecord(offset=102, payload={"user_id": "", "amount": "invalid"}),  # Malformed
        IngestionRecord(offset=103, payload={"user_id": "u3", "amount": 30.0}),
        IngestionRecord(offset=104, payload={"user_id": "u4", "amount": 40.0}),
    ]

    processed_cnt, dlq_cnt = pipeline.process_batch(batch_sporadic)
    # 4 records succeeded, 1 went to DLQ, pipeline progressed cleanly:
    assert processed_cnt == 4
    assert dlq_cnt == 1
    assert pipeline.dead_letter_queue[0].offset == 102
    assert pipeline.last_committed_offset == 104

    # 2. Test systemic breaking schema change:
    # Upstream deployed breaking rename: 'user_id' renamed to 'account_uuid'
    batch_breaking = [
        IngestionRecord(offset=105, payload={"account_uuid": "uuid-1", "amount": 10.0}),
        IngestionRecord(offset=106, payload={"account_uuid": "uuid-2", "amount": 20.0}),
        IngestionRecord(offset=107, payload={"account_uuid": "uuid-3", "amount": 30.0}),
    ]

    tripped = False
    try:
        pipeline.process_batch(batch_breaking)
    except PipelineHaltedException as exc:
        tripped = True
        assert "CIRCUIT BREAKER TRIPPED" in str(exc)

    # Circuit breaker must trip to prevent silent DLQ swallowing and offset burning:
    assert tripped is True
    # Committed offset must NOT have advanced past the last healthy record:
    assert pipeline.last_committed_offset == 104

    print("All data quality quarantine circuit breaker assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
