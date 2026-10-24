cases = [('en', True), ('en', True), ('ar', True), ('ar', False)]
report = []
for language in sorted({language for language, _ in cases}):
    outcomes = [ok for name, ok in cases if name == language]
    report.append((language, sum(outcomes)/len(outcomes), len(outcomes)))
print(report)
