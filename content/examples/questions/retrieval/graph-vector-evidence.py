"""Combine vector-found entities with graph traversal while keeping edge provenance."""
EDGES = [
    ("CompanyA", "acquired", "CompanyB", {"source": "press-12", "verified": True}),
    ("CompanyB", "supplied_by", "SupplierX", {"source": "contract-7", "verified": True}),
    ("CompanyB", "supplied_by", "SupplierY", {"source": "llm-extraction-3", "verified": False}),
]


def neighbors(entity):
    return [(rel, dst, meta) for src, rel, dst, meta in EDGES if src == entity]


def affected_suppliers(seed_entities, allow_unverified=False):
    result = []
    for entity in seed_entities:
        for rel, company, meta in neighbors(entity):
            if rel != "acquired":
                continue
            for rel2, supplier, meta2 in neighbors(company):
                if rel2 == "supplied_by" and (meta2["verified"] or allow_unverified):
                    result.append({"supplier": supplier, "path": [entity, company],
                                   "sources": [meta["source"], meta2["source"]]})
    return result


seeds = ["CompanyA"]   # entities linked from vector-retrieved passages
strict = affected_suppliers(seeds)
loose = affected_suppliers(seeds, allow_unverified=True)
assert [r["supplier"] for r in strict] == ["SupplierX"]
assert len(loose) == 2
print(strict)
