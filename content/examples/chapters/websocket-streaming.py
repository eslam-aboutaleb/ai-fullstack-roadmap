class Session:
    def __init__(self):
        self.seen = set()
    def accept(self, message):
        if message["id"] in self.seen: return "duplicate"
        if message["type"] not in {"input", "cancel"}: raise ValueError("type")
        self.seen.add(message["id"])
        return "accepted"
s = Session()
assert s.accept({"id": "m1", "type": "cancel"}) == "accepted"
assert s.accept({"id": "m1", "type": "cancel"}) == "duplicate"
# Real command effects and deduplication must share durable atomic semantics.
