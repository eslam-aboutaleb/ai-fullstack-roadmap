"""Fair, offline portable task contract for AI-framework comparisons.

Named vendor SDK adapters are NOT imported by this fixture. The three named
local strategies below are reference implementations, not LangChain, ADK,
Agents SDK or LlamaIndex benchmark results.
"""
from dataclasses import dataclass
from time import perf_counter

@dataclass(frozen=True)
class Task:
    owner: str
    question: str
    allowed_tools: frozenset

@dataclass(frozen=True)
class Outcome:
    answer: str
    sources: tuple
    attempted_tools: tuple
    side_effects: int

DOCUMENTS={
    "A":[("a1","Returns within 30 days with proof of purchase.")],
    "B":[("b1","Unrelated private warranty entitlement.")]
}

class DirectSDKReference:
    name="direct-reference-not-vendor-sdk"
    def run(self,task):
        if "search" not in task.allowed_tools:
            return Outcome("cannot search",(),(),0)
        docs=DOCUMENTS.get(task.owner,[])
        if not docs:return Outcome("insufficient evidence",(),("search",),0)
        return Outcome(docs[0][1],(docs[0][0],),("search",),0)

class GraphReference:
    name="graph-reference-not-langgraph"
    def run(self,task):
        # Node decision -> tool call -> render, with no additional permission.
        if "search" not in task.allowed_tools:
            return Outcome("cannot search",(),(),0)
        evidence=DOCUMENTS.get(task.owner,[])
        return Outcome(evidence[0][1],(evidence[0][0],),("search",),0) if evidence else Outcome("insufficient evidence",(),("search",),0)

class RetrievalReference:
    name="retrieval-reference-not-llamaindex"
    def run(self,task):
        return DirectSDKReference().run(task)

def compare(task,adapters,expected):
    outcomes={}
    for adapter in adapters:
        start=perf_counter()
        result=adapter.run(task)
        elapsed_ms=(perf_counter()-start)*1000
        if not isinstance(result,Outcome):
            raise TypeError("adapter returned noncanonical outcome")
        if result.side_effects:raise AssertionError("unexpected side effect")
        if not set(result.attempted_tools)<=task.allowed_tools:
            raise AssertionError("tool policy violated")
        if any(source.startswith("b") for source in result.sources) and task.owner=="A":
            raise AssertionError("cross-tenant source")
        outcomes[adapter.name]={"answer":result.answer,"sources":result.sources,
                                "attempted_tools":result.attempted_tools,
                                "elapsed_ms":elapsed_ms,"matches_fixture":result==expected}
    return outcomes

def check():
    adapters=[DirectSDKReference(),GraphReference(),RetrievalReference()]
    task=Task("A","Can I return an item?",frozenset({"search"}))
    oracle=Outcome(DOCUMENTS["A"][0][1],("a1",),("search",),0)
    results=compare(task,adapters,oracle)
    assert len(results)==3 and all(r["matches_fixture"] for r in results.values())
    assert all(r["elapsed_ms"]>=0 for r in results.values())
    denied=Task("A",task.question,frozenset())
    outcomes=compare(denied,adapters,Outcome("cannot search",(),(),0))
    assert all(r["matches_fixture"] for r in outcomes.values())
    class Unsafe:
        name="unsafe-test"
        def run(self,task):return Outcome("sent",(),("write",),1)
    try:compare(task,[Unsafe()],oracle)
    except AssertionError:pass
    else:raise AssertionError("effectful incompatible adapter accepted")
    print("Framework contract: paired answer, scope, tools, side effects and denial PASS")
if __name__=="__main__":check()
