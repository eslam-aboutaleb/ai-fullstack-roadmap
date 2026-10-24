"""Demonstrate hashable key contracts and dictionary collision resolution."""


class MetricKey:

    def __init__(self, tenant: str, metric: str):
        self.tenant = tenant
        self.metric = metric

    def __hash__(self) -> int:
        return hash((self.tenant, self.metric))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetricKey) and (self.tenant, self.metric) == (other.tenant, other.metric)


lookup = {MetricKey("tenant_a", "latency"): 42.5}
assert lookup[MetricKey("tenant_a", "latency")] == 42.5

# Mutable dict cannot be used as key
try:
    bad_dict = {{}: 1}  # type: ignore
    assert False, "Should have raised TypeError"
except TypeError:
    pass

print("Hash table dictionary key contract verified successfully.")

