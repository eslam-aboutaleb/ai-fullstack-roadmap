"""Capacity, SLO and release-gate calculations using explicit synthetic assumptions."""
from math import ceil, isfinite


def replicas(arrivals_per_second: float, mean_seconds: float, slots: int, target_utilization: float) -> int:
    if not all(isfinite(v) for v in (arrivals_per_second, mean_seconds, target_utilization)):
        raise ValueError('Finite capacity assumptions required')
    if arrivals_per_second < 0 or mean_seconds < 0 or type(slots) is not int or slots < 1 or not 0 < target_utilization < 1:
        raise ValueError('Invalid capacity assumption')
    # Little's Law estimates mean in-flight work, not a tail-latency guarantee.
    return max(1, ceil(arrivals_per_second * mean_seconds / (slots * target_utilization)))


def release_allowed(baseline_quality: float, candidate_quality: float, p95_ms: float,
                    leaks: int, max_regression=0.01, latency_budget_ms=2000) -> bool:
    if not all(isfinite(v) for v in (baseline_quality, candidate_quality, p95_ms)):
        return False
    if not 0 <= baseline_quality <= 1 or not 0 <= candidate_quality <= 1 or p95_ms < 0:
        return False
    # Explicit tolerance avoids rejecting a decimal boundary such as 0.90-0.89
    # solely because binary floating-point subtraction rounds slightly upward.
    return leaks == 0 and baseline_quality - candidate_quality <= max_regression + 1e-12 and p95_ms <= latency_budget_ms


def safe_span(attributes: dict) -> dict:
    # Allowlisted low-cardinality attributes. No input/output text or user ID.
    result = {}
    if attributes.get('stage') in ('retrieve', 'model', 'tool'):
        result['stage'] = attributes['stage']
    if attributes.get('outcome') in ('success', 'timeout', 'denied', 'error'):
        result['outcome'] = attributes['outcome']
    return result


def verify() -> None:
    assert replicas(50, 2, 4, 0.7) == 36
    good_requests, total_requests, objective = 9980, 10000, 0.999
    allowed_bad = total_requests * (1 - objective)
    consumed_bad = total_requests - good_requests
    burn = (consumed_bad / total_requests) / (1 - objective)
    assert abs(allowed_bad - 10) < 1e-8 and abs(burn - 2) < 1e-8
    assert consumed_bad > allowed_bad
    assert release_allowed(0.90, 0.905, 1800, 0)
    assert release_allowed(0.90, 0.89, 2000, 0)
    assert not release_allowed(0.90, 0.889, 2000, 0)
    assert not release_allowed(0.90, 0.94, 1800, 1)
    assert not release_allowed(0.90, 0.905, 2500, 0)
    assert not release_allowed(0.90, float('nan'), 1000, 0)
    assert safe_span({'stage': 'model', 'outcome': 'timeout', 'prompt': 'synthetic secret', 'user_id': 'A'}) == {'stage': 'model', 'outcome': 'timeout'}
    print('Production scorecard: 36-replica mean-capacity estimate, 2x error-budget burn, leak/latency release gates and trace allowlist passed.')


if __name__ == '__main__':
    verify()
