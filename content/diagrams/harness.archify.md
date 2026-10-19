# Keep the model inside a controlled runtime
The agent can propose an action; trusted backend policy and business services decide whether it executes.

@answer scope="Illustrative runtime · no provider or production claims"
@meta locale=en

## One bounded tool cycle
@sequence id=agent-cycle title="Policy before effects"
| actor user | User | frontend |
| actor runtime | Agent harness | backend |
| actor model | Model | backend |
| actor gate | Policy gate | backend |
| actor service | Business service | database |
| user | runtime | Submit authenticated task |
| runtime | model | Bounded context and permitted tools |
| model | runtime | Propose tool call | return |
| runtime | gate | Validate identity, arguments, approval |
| gate | service | Execute allowed operation |
| service | runtime | Authoritative result and operation ID | return |
| runtime | user | Safe result or explicit unresolved state | return |

## Recover without repeating effects
| Boundary | Durable record | Recovery action |
| --- | --- | --- |
| Task | Run ID and budget | Resume or stop |
| Approval | Exact operation revision | Revalidate |
| Business effect | Operation key and result | Query status |
| Downstream work | Outbox item | Idempotent retry |
