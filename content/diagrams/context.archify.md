# Build the context before asking for an answer
A reliable answer needs authorized, applicable evidence inside a measured context budget.

@answer scope="Fictional support platform · illustrative design"
@meta locale=en

## Assemble useful information
@workflow id=context-flow title="Context assembly"
| intent | Resolve user intent | backend |
| scope | Bind trusted identity | backend |
| retrieve | Retrieve applicable evidence | backend |
| budget | Select and budget context | backend |
| answer | Generate and validate | backend |
| intent > scope | Task contract |
| scope > retrieve | Authorized query |
| retrieve > budget | Evidence envelope |
| budget > answer | Versioned context manifest |

## Measure each responsibility
| Layer | Check | Failure response |
| --- | --- | --- |
| Identity | Required resource scope | Deny or authenticate |
| Evidence | Applicability and completeness | Clarify or abstain |
| Context | Budget and provenance | Reassemble |
| Output | Support and schema | Reject or revise |
