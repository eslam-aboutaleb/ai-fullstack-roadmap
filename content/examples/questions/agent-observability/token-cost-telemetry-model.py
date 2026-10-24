# /// script
# dependencies = []
# ///
"""
Multi-Model Token Usage and Dynamic Pricing Telemetry Engine.

Demonstrates:
1. Ground truth immutable recording of raw tokens (input, output, cached).
2. Cost calculation for models with registered price tables.
3. Graceful handling of unknown or experimental models: records exact token counts,
   marks cost as None, and sets pricing status to PENDING_REGISTRATION rather
   than fabricating a misleading $0.00 cost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ModelPriceRate:
    price_per_million_input: float
    price_per_million_output: float
    price_per_million_cached: float = 0.0


@dataclass
class UsageTelemetryRecord:
    model_name: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    calculated_cost_usd: Optional[float] = None
    pricing_status: str = "CALCULATED"


class TokenCostAccounting:
    def __init__(self) -> None:
        self.pricing_table: Dict[str, ModelPriceRate] = {
            "gemini-1.5-flash": ModelPriceRate(
                price_per_million_input=0.075,
                price_per_million_output=0.30,
                price_per_million_cached=0.01875,
            ),
            "claude-3-5-sonnet": ModelPriceRate(
                price_per_million_input=3.00,
                price_per_million_output=15.00,
            ),
        }

    def record_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> UsageTelemetryRecord:
        rate = self.pricing_table.get(model_name)

        if rate is None:
            # UNKNOWN PRICING: Do not fabricate $0.00!
            # Record exact raw tokens and mark cost as None with explicit pending status.
            return UsageTelemetryRecord(
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                calculated_cost_usd=None,
                pricing_status="PENDING_TIER_REGISTRATION",
            )

        # Calculate exact cost using high-precision floats
        cost = (
            (input_tokens / 1_000_000.0) * rate.price_per_million_input
            + (output_tokens / 1_000_000.0) * rate.price_per_million_output
            + (cached_tokens / 1_000_000.0) * rate.price_per_million_cached
        )

        return UsageTelemetryRecord(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            calculated_cost_usd=round(cost, 6),
            pricing_status="CALCULATED",
        )


def main() -> None:
    accounting = TokenCostAccounting()

    # --- Scenario 1: Known Model (Gemini 1.5 Flash) ---
    rec_known = accounting.record_usage(
        model_name="gemini-1.5-flash",
        input_tokens=100_000,   # 0.1M * $0.075 = $0.0075
        output_tokens=20_000,   # 0.02M * $0.30 = $0.0060
        cached_tokens=50_000,   # 0.05M * $0.01875 = $0.000938
    )
    assert rec_known.calculated_cost_usd is not None
    assert abs(rec_known.calculated_cost_usd - 0.0144375) < 1e-5
    assert rec_known.pricing_status == "CALCULATED"
    known_model_cost_calculated = True

    # --- Scenario 2: Newly Deployed Model with Unknown Pricing ---
    rec_unknown = accounting.record_usage(
        model_name="experimental-agentic-model-v9",
        input_tokens=500_000,
        output_tokens=150_000,
    )
    # Critical Invariant: Must NOT report $0.00!
    assert rec_unknown.calculated_cost_usd is None, "Cost must be None for unknown model"
    assert rec_unknown.pricing_status == "PENDING_TIER_REGISTRATION"
    unknown_model_cost_null = True

    # Invariant: Raw token metrics are accurately preserved in both cases
    assert rec_known.input_tokens == 100_000
    assert rec_unknown.input_tokens == 500_000
    raw_tokens_preserved = True

    print(
        f"Token cost telemetry verified: known_model_cost_calculated={known_model_cost_calculated}, "
        f"unknown_model_cost_null={unknown_model_cost_null}, "
        f"raw_tokens_preserved={raw_tokens_preserved}"
    )


if __name__ == "__main__":
    main()
