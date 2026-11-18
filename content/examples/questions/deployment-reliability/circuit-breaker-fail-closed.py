"""Degrade optional stages with a circuit breaker; never degrade authorization into allow-all."""


class Breaker:
    def __init__(self, threshold=2, reset_after=30.0, clock=lambda: 0.0):
        self.threshold, self.reset_after, self.clock = threshold, reset_after, clock
        self.failures, self.opened_at = 0, None

    def allow(self):
        if self.opened_at is None:
            return True
        if self.clock() - self.opened_at >= self.reset_after:
            return True            # half-open probe
        return False

    def record(self, ok):
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = self.clock()


class AuthorizationUnavailable(Exception):
    pass


def authorize(candidates, authz_up):
    if not authz_up:
        raise AuthorizationUnavailable("fail closed")
    return [c for c in candidates if c["tenant"] == "t1"]


def pipeline(candidates, breaker, reranker_up, authz_up=True):
    allowed = authorize(candidates, authz_up)          # always runs first
    if breaker.allow():
        try:
            if not reranker_up:
                raise TimeoutError
            breaker.record(True)
            return sorted(allowed, key=lambda c: -c["score"]), "reranked"
        except TimeoutError:
            breaker.record(False)
    return allowed, "first-stage"


now = [0.0]
breaker = Breaker(clock=lambda: now[0])
docs = [{"id": 1, "tenant": "t1", "score": 0.2}, {"id": 2, "tenant": "t2", "score": 0.9}, {"id": 3, "tenant": "t1", "score": 0.8}]
modes = [pipeline(docs, breaker, reranker_up=False)[1] for _ in range(3)]
try:
    pipeline(docs, breaker, reranker_up=True, authz_up=False)
    denied = False
except AuthorizationUnavailable:
    denied = True
assert breaker.opened_at is not None and denied
print(modes, "breaker_open", breaker.opened_at is not None, "authz_fail_closed", denied)
