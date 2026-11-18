"""Run independent subqueries concurrently and dependent subqueries by dependency level."""
import asyncio

CALLS = []


async def retrieve(name, **context):
    CALLS.append(name)
    await asyncio.sleep(0.05)
    facts = {
        "acquired_company": "PayCo",
        "industry": "payments",
        "jurisdiction": "EU",
        "rules": f"rules for {context.get('industry')} in {context.get('jurisdiction')}",
    }
    return facts[name]


PLAN = {
    "acquired_company": [],
    "industry": ["acquired_company"],
    "jurisdiction": ["acquired_company"],
    "rules": ["industry", "jurisdiction"],
}


def levels(plan):
    done, result = set(), []
    while len(done) < len(plan):
        ready = sorted(n for n, deps in plan.items() if n not in done and set(deps) <= done)
        if not ready:
            raise ValueError("cycle or missing dependency")
        result.append(ready)
        done.update(ready)
    return result


async def run(plan):
    state = {}
    for level in levels(plan):
        values = await asyncio.gather(*(retrieve(name, **state) for name in level))
        state.update(dict(zip(level, values)))
    return state


state = asyncio.run(run(PLAN))
assert state["rules"] == "rules for payments in EU"
print(levels(PLAN), state["rules"])
