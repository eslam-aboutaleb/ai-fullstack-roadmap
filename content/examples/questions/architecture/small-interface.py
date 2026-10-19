from typing import Protocol
class Searcher(Protocol):
    def search(self, query: str) -> list[str]: ...
class MemorySearch:
    def search(self, query: str) -> list[str]:
        return ['policy']
def retrieve(store: Searcher):
    return store.search('sale')
print(retrieve(MemorySearch()))
