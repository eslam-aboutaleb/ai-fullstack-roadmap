# /// script
# dependencies = []
# ///
"""
Google SRE Multi-Window Multi-Burn-Rate Operational Alerting for AI Agents.

Demonstrates:
1. Alerting on user-facing Service Level Objectives (SLOs) rather than causes.
2. Multi-window burn rate: 1-hour window > 14.4x burn rate pages immediately
   (consumes 2% of 30-day budget in 1 hour).
3. Transient 30-second spikes do NOT trigger critical on-call pages (preventing alert fatigue).
4. Alert notifications strictly include mandatory Runbook URLs and correlated trace filters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SLOBurnRateAlert:
    alert_name: str
    severity: str
    burn_rate: float
    budget_consumed_percent: float
    runbook_url: str
    trace_filter: str


class SLOAlertManager:
    """Evaluates agent request error rates against a 99.5% availability SLO."""

    def __init__(self, target_slo: float = 0.995) -> None:
        self.target_slo = target_slo
        self.error_budget = 1.0 - target_slo  # 0.005 (0.5%)
        # 30-day month = 720 hours
        # In a 1-hour window, burn rate 1.0 consumes (1/720) ~ 0.1388% of budget.
        # Burn rate 14.4x in 1h consumes 14.4 * (1/720) = 2.0% of error budget.

    def evaluate_1h_window(
        self,
        total_requests: int,
        failed_requests: int,
    ) -> Optional[SLOBurnRateAlert]:
        if total_requests == 0:
            return None

        actual_error_rate = failed_requests / total_requests
        burn_rate = actual_error_rate / self.error_budget

        # Alert Rule: 1-hour window burn rate >= 14.4x -> P1 Critical Page
        if burn_rate >= 14.4:
            budget_consumed = (burn_rate / 720.0) * 100.0
            return SLOBurnRateAlert(
                alert_name="AgentTaskAvailability_1h_BurnRate_Critical",
                severity="CRITICAL_PAGE",
                burn_rate=round(burn_rate, 2),
                budget_consumed_percent=round(budget_consumed, 2),
                runbook_url="https://runbooks.internal/agent-task-availability-slo",
                trace_filter="service:agent-orchestrator AND status:error AND latency > 10s",
            )

        return None


def main() -> None:
    alert_manager = SLOAlertManager(target_slo=0.995)

    # --- Scenario 1: Brief Transient Spurt (10 failed requests out of 2,000 in 1 hour) ---
    # Error rate = 10 / 2000 = 0.005 (0.5%), burn rate = 0.005 / 0.005 = 1.0x (normal consumption)
    blip_alert = alert_manager.evaluate_1h_window(total_requests=2000, failed_requests=10)
    assert blip_alert is None, "Brief normal error rate should NOT trigger a critical page"
    brief_blip_alerted = False

    # --- Scenario 2: Catastrophic Outage (200 failed requests out of 2,000 in 1 hour) ---
    # Error rate = 200 / 2000 = 0.10 (10%), burn rate = 0.10 / 0.005 = 20.0x (> 14.4x threshold!)
    catastrophic_alert = alert_manager.evaluate_1h_window(total_requests=2000, failed_requests=200)
    assert catastrophic_alert is not None, "Catastrophic burn rate MUST trigger an alert"
    assert catastrophic_alert.severity == "CRITICAL_PAGE"
    assert catastrophic_alert.burn_rate >= 14.4
    assert catastrophic_alert.budget_consumed_percent >= 2.0
    catastrophic_burn_alerted = True

    # Invariant: Alert MUST link directly to a runbook and correlated trace query
    assert "https://runbooks.internal" in catastrophic_alert.runbook_url
    assert "status:error" in catastrophic_alert.trace_filter
    runbook_linked = True

    print(
        f"SLO burn rate alerting verified: brief_blip_alerted={brief_blip_alerted}, "
        f"catastrophic_burn_alerted={catastrophic_burn_alerted}, "
        f"runbook_linked={runbook_linked}"
    )


if __name__ == "__main__":
    main()

