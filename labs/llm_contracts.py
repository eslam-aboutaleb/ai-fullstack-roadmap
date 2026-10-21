"""Mock model client with bounded retries, explicit budgets and output validation.

No provider credentials, HTTP calls or fabricated benchmark results.
"""
from dataclasses import dataclass
import json


class RateLimited(Exception):
    pass


class BudgetExhausted(Exception):
    pass


@dataclass
class Budget:
    remaining_tokens: int
    attempts: int = 0

    def __post_init__(self) -> None:
        if type(self.remaining_tokens) is not int or self.remaining_tokens < 0:
            raise ValueError('Budget requires a nonnegative integer allowance')

    def reserve(self, tokens: int) -> None:
        if type(tokens) is not int or tokens <= 0 or tokens > self.remaining_tokens:
            raise BudgetExhausted('Insufficient reserved token capacity')
        self.remaining_tokens -= tokens
        self.attempts += 1


def context_fits(input_tokens: int, reserved_output: int, limit: int) -> bool:
    values = (input_tokens, reserved_output, limit)
    return all(type(v) is int and v >= 0 for v in values) and input_tokens + reserved_output <= limit


def validate_answer(raw: str, permitted_sources: set[str]) -> dict:
    if len(raw) > 8000:
        raise ValueError('Response size cap')
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON field')
            result[key] = value
        return result
    parsed = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(parsed, dict) or set(parsed) != {'answer', 'citations', 'abstain'}:
        raise ValueError('Unexpected answer structure')
    if not isinstance(parsed['answer'], str) or type(parsed['abstain']) is not bool:
        raise ValueError('Invalid answer types')
    citations = parsed['citations']
    if not isinstance(citations, list) or any(not isinstance(c, str) for c in citations):
        raise ValueError('Invalid citation types')
    if any(c not in permitted_sources for c in citations):
        raise ValueError('Source is outside the caller-scoped candidate set')
    if parsed['abstain'] and citations or not parsed['abstain'] and not citations:
        raise ValueError('Answer/abstention evidence contract violated')
    if not parsed['abstain'] and not parsed['answer'].strip():
        raise ValueError('Non-abstaining answer must contain text')
    # Membership is deliberately not a proof that the citation entails the answer.
    return parsed


def call_model(transport, budget: Budget, input_tokens: int, output_limit: int,
               sources: set[str], wait=lambda seconds: None) -> dict:
    if not context_fits(input_tokens, output_limit, 128):
        raise ValueError('Context budget exceeded before invocation')
    for attempt in range(3):
        budget.reserve(input_tokens + output_limit)  # Conservative charge for every attempt.
        try:
            raw = transport()
        except RateLimited:
            if attempt == 2:
                raise
            wait(min(2, 0.25 * (2 ** attempt)))
            continue
        return validate_answer(raw, sources)  # Do not blindly retry invalid/unauthorized output.
    raise AssertionError('Unreachable')


def verify() -> None:
    calls, delays = [], []
    response = json.dumps({'answer': 'Sale policy applies.', 'citations': ['sale@3'], 'abstain': False})
    def temporary_failure():
        calls.append('call')
        if len(calls) == 1:
            raise RateLimited()
        return response
    budget = Budget(100)
    assert call_model(temporary_failure, budget, 10, 20, {'sale@3'}, delays.append)['citations'] == ['sale@3']
    assert budget.remaining_tokens == 40 and delays == [0.25]
    bad = json.dumps({'answer': 'A private exception', 'citations': ['tenant-B@1'], 'abstain': False})
    for raw in ('not JSON', bad, '{"answer":0,"citations":[],"abstain":false}',
                '{"answer":"one","answer":"two","citations":["sale@3"],"abstain":false}'):
        try:
            call_model(lambda: raw, Budget(100), 10, 20, {'sale@3'})
        except (ValueError, json.JSONDecodeError):
            pass
        else:
            raise AssertionError('Invalid answer accepted')
    tight = Budget(30)
    def always_limited():
        raise RateLimited()
    try:
        call_model(always_limited, tight, 10, 20, set())
    except BudgetExhausted:
        pass
    else:
        raise AssertionError('Retry exceeded budget')
    assert tight.attempts == 1
    assert context_fits(100, 28, 128) and not context_fits(100, 29, 128)
    print('Model contract: preflight context cap, bounded retry, per-attempt budget and scoped output validation passed.')


if __name__ == '__main__':
    verify()
