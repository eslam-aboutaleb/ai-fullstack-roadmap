def route(intent):
    routes = {"known_record": "exact_lookup", "knowledge": "retrieve_evidence",
              "write_request": "prepare_then_review"}
    return routes.get(intent, "clarify")
assert route("unrecognized") == "clarify"
# Intent may be model-assisted. Route permissions remain deterministic.
