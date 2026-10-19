confidences, correctness = [0.9, 0.9], [True, False]
accuracy = sum(correctness)/len(correctness)
coverage = sum(value >= 0.8 for value in confidences)/len(confidences)
print(accuracy, coverage)
