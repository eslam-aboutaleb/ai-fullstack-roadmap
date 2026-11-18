"""Accept a standalone rewrite only when protected identifiers and negations survive."""
import re

IDENTIFIER = re.compile(r"\b[A-Z]{1,5}-\d+\b")
NEGATIONS = {"not", "no", "never", "without", "except"}


def protected(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    return set(IDENTIFIER.findall(text)), words & NEGATIONS


def validate_rewrite(history_text, original, rewrite):
    ids_needed = protected(history_text + " " + original)[0]
    negations_needed = protected(original)[1]
    ids_seen, negations_seen = protected(rewrite)
    problems = []
    if ids_needed - ids_seen:
        problems.append("missing " + ",".join(sorted(ids_needed - ids_seen)))
    if ids_seen - ids_needed:
        problems.append("invented " + ",".join(sorted(ids_seen - ids_needed)))
    if negations_needed - negations_seen:
        problems.append("dropped negation")
    return problems


history = "Explain the coverage limits of Policy P-102."
follow_up = "Which items are not covered?"
good = "Which items are not covered by Policy P-102?"
bad_id = "Which items are not covered by Policy P-120?"
bad_negation = "Which items are covered by Policy P-102?"

assert validate_rewrite(history, follow_up, good) == []
assert validate_rewrite(history, follow_up, bad_id) == ["missing P-102", "invented P-120"]
assert validate_rewrite(history, follow_up, bad_negation) == ["dropped negation"]
print(validate_rewrite(history, follow_up, good), validate_rewrite(history, follow_up, bad_id), validate_rewrite(history, follow_up, bad_negation))
