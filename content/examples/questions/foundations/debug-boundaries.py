expected_revision = 2
trace = [('fetch', 2), ('cache', 1), ('prompt', 1), ('answer', 1)]
first_wrong = next(stage for stage, revision in trace if revision != expected_revision)
print(first_wrong)
