cases = [{'condition': 'clear', 'expected': 200, 'actual': 200},
         {'condition': 'blurred', 'expected': 200, 'actual': 250}]
correct = lambda case: case['expected'] == case['actual']
blurred = [case for case in cases if case['condition'] == 'blurred']
print(sum(map(correct, cases))/len(cases), sum(map(correct, blurred))/len(blurred))
