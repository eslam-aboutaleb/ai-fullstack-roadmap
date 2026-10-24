from dataclasses import dataclass, asdict
import json
@dataclass(frozen=True)
class Experiment:
    dataset: str
    prompt: str
    model: str
    context_policy: str
    application_release: str
run = Experiment("synthetic-v1", "support-v2", "injected-model", "budget-v1", "demo-v1")
assert json.loads(json.dumps(asdict(run)))["dataset"] == "synthetic-v1"
# Add measured outcomes and environment metadata after running the experiment.
