# /// script
# dependencies = []
# ///
"""
Privacy-Preserving Trace Span Redaction and Timeout Diagnostics.

Demonstrates:
1. Redacting raw cleartext prompts and PII from distributed traces.
2. Generating a salted SHA-256 fingerprint for deduplication without privacy breach.
3. Capturing stage durations (tokenization, retrieval, model inference, tool execution)
   and retry counts to diagnose tool timeouts cleanly without data disclosure.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DiagnosticSpan:
    trace_id: str
    span_id: str
    tool_name: str
    stage_durations_ms: Dict[str, float] = field(default_factory=dict)
    retry_count: int = 0
    error_code: Optional[str] = None
    prompt_fingerprint: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)


class PrivacyPreservingSpanProcessor:
    """Interceps tool calls, redacting confidential cleartext while retaining diagnostic metadata."""

    def __init__(self, tenant_salt: str) -> None:
        self.salt = tenant_salt.encode("utf-8")

    def process_tool_timeout(
        self,
        trace_id: str,
        span_id: str,
        tool_name: str,
        raw_prompt_with_pii: str,
        stage_timings: Dict[str, float],
        retry_count: int,
        error_type: str,
    ) -> DiagnosticSpan:
        # 1. Compute salted one-way hash of prompt (cannot be reversed)
        hasher = hashlib.sha256(self.salt)
        hasher.update(raw_prompt_with_pii.encode("utf-8"))
        fingerprint = f"sha256:{hasher.hexdigest()[:16]}"

        # 2. Build sanitized diagnostic span
        # INVARIANT: raw_prompt_with_pii is NEVER included in attributes!
        span = DiagnosticSpan(
            trace_id=trace_id,
            span_id=span_id,
            tool_name=tool_name,
            stage_durations_ms=stage_timings,
            retry_count=retry_count,
            error_code=error_type,
            prompt_fingerprint=fingerprint,
            attributes={
                "tool.sanitized_name": tool_name,
                "input_token_estimate": len(raw_prompt_with_pii.split()),
                "timeout_phase": "EXTERNAL_SOCKET_READ",
            },
        )
        return span


def main() -> None:
    processor = PrivacyPreservingSpanProcessor(tenant_salt="k_cluster_salt_9981")

    # Confidential input containing PII and banking info
    sensitive_user_prompt = (
        "Customer SSN: 000-12-3456. Check balance on confidential account #88192-X "
        "and summarize recent wires."
    )

    stage_timings_ms = {
        "prompt_tokenization": 12.0,
        "vector_retrieval": 140.0,
        "external_tool_network_wait": 10005.0,  # 10s socket timeout!
    }

    # Simulate tool timing out on retry attempt 2
    sanitized_span = processor.process_tool_timeout(
        trace_id="tr_489102",
        span_id="sp_9921",
        tool_name="banking_balance_lookup",
        raw_prompt_with_pii=sensitive_user_prompt,
        stage_timings=stage_timings_ms,
        retry_count=2,
        error_type="TIMEOUT_SOCKET_READ",
    )

    # Invariant 1: Zero cleartext prompt or PII in span attributes
    span_str = str(sanitized_span)
    assert "000-12-3456" not in span_str, "CRITICAL: PII leaked in trace span!"
    assert "confidential account" not in span_str, "CRITICAL: Cleartext prompt leaked in span!"
    prompt_cleartext_leaked = False

    # Invariant 2: Full diagnostic visibility for timeout analysis
    assert sanitized_span.stage_durations_ms["external_tool_network_wait"] >= 10000.0
    stage_latency_captured = True

    # Invariant 3: Retry count recorded
    assert sanitized_span.retry_count == 2
    retry_count_recorded = sanitized_span.retry_count

    # Invariant 4: Salted fingerprint preserved for grouping identical queries
    assert sanitized_span.prompt_fingerprint.startswith("sha256:")

    print(
        f"Sanitized trace redaction verified: prompt_cleartext_leaked={prompt_cleartext_leaked}, "
        f"stage_latency_captured={stage_latency_captured}, "
        f"retry_count_recorded={retry_count_recorded}"
    )


if __name__ == "__main__":
    main()

