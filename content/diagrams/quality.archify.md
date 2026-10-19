# Evaluate the whole task and preserve the evidence
A useful agent completes authorized work, cites applicable sources, and recovers from failures within a declared budget.

@answer scope="Synthetic portfolio example · measured gates required in your implementation"
@meta locale=en

## From document to release decision
@workflow id=quality-flow title="Evidence and evaluation lifecycle"
| upload | Validate and isolate upload | backend |
| extract | OCR and layout extraction | backend |
| index | Build versioned index | backend |
| run | Run bounded agent task | backend |
| evaluate | Evaluate and review | backend |
| release | Release or revise | backend |
| upload > extract | Approved artifact |
| extract > index | Validated structure |
| index > run | Applicable evidence |
| run > evaluate | Versioned run record |
| evaluate > release | Reviewed measurements |

## Independent checks prevent hidden failures
| Check | Example failure |
| --- | --- |
| Retrieval | Necessary exception missing |
| Answer | Citation does not support statement |
| Trajectory | Unauthorized read |
| Effect | Duplicate business write |
| Recovery | Stale result published after correction |
