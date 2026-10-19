from typing import Protocol
class SearchStore(Protocol):
    def search(self, query: str, tenant: str) -> list[str]: ...
class DemoStore:
    def search(self, query, tenant):
        return ["demo passage"] if tenant == "demo" else []
def retrieve(store: SearchStore, query: str, tenant: str):
    return store.search(query, tenant)
assert retrieve(DemoStore(), "hours", "other") == []
