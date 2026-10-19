cases = [('C1', True, True), ('C2', False, True), ('C3', False, False)]
agreement = sum(human == judge for _, human, judge in cases)/len(cases)
print(round(agreement, 6), [name for name, human, judge in cases if human != judge])
