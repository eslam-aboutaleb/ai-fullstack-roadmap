# Safety beyond authorization — hands-on lesson (#43)

Introduction: a production AI system must address **harmful outputs,
privacy, fairness, prompt injection, data poisoning and model supply-chain
risk**, each at a different trust boundary. A safe instruction prompt is not a
policy engine. A high overall moderation score does not establish per-group
fairness, and a hash does not establish publisher identity.

Run python3 -B labs/ai_safety_release_gate.py to calculate confusion matrices
and per-slice true-positive and false-positive rates, test an intentionally
introduced false negative, reject inadequate sample sizes, and detect
altered source bytes or source-role escalation.

Fixture counts are deliberately tiny for teaching; do not infer deployment
fairness or moderation efficacy. A real deployment needs human-labeled,
representative safety datasets, applicable policy and jurisdiction analysis,
privacy and data retention audit, prompt-injection tool permission tests,
artifact signature/publisher verification, documented risk thresholds and
post-release incident/appeal workflows.
