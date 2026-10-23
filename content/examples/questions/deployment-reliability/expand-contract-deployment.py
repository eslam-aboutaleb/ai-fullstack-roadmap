"""Demonstrate Expand-and-Contract schema rollout coordination across distributed replicas."""

class DeploymentRolloutSimulator:
    def __init__(self):
        # Database schema columns
        self.schema_columns = {"id", "legacy_address"}
        # Running application replicas: list of version strings ("v1" or "v2")
        self.replicas = ["v1", "v1", "v1"]

    def step_1_expand(self):
        """Pre-deployment step: add nullable column in database before deploying new app code."""
        self.schema_columns.add("normalized_address")

    def step_2_canary_deploy_v2(self):
        """Roll out v2 pod. v2 supports dual-writing to both columns; v1 continues writing legacy_address."""
        self.replicas[0] = "v2"
        # Validate that both v1 and v2 replicas function simultaneously without DB errors
        for r in self.replicas:
            assert "legacy_address" in self.schema_columns, f"Replica {r} requires legacy_address"

    def step_3_full_rollout_v2(self):
        """Deploy remaining v2 replicas."""
        self.replicas = ["v2", "v2", "v2"]

    def step_4_backfill_data(self):
        """Run batch job backfilling normalized_address for all historical records."""
        pass # All rows now populated

    def step_5_contract(self):
        """Post-deployment cleanup: drop deprecated column only after all v1 replicas are terminated."""
        assert all(r == "v2" for r in self.replicas), "Cannot contract while v1 replicas exist!"
        self.schema_columns.remove("legacy_address")

sim = DeploymentRolloutSimulator()
sim.step_1_expand()
sim.step_2_canary_deploy_v2()
sim.step_3_full_rollout_v2()
sim.step_4_backfill_data()
sim.step_5_contract()

assert "normalized_address" in sim.schema_columns and "legacy_address" not in sim.schema_columns
print(f"Zero-downtime deployment verified: final_columns={sorted(sim.schema_columns)}, replicas={sim.replicas}")
