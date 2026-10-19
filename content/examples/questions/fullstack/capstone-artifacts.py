required = {'explanation', 'implementation', 'failure_reproduction', 'tradeoff'}
provided = {'explanation', 'implementation', 'tradeoff'}
print(sorted(required-provided))
