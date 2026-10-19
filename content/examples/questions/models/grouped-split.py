rows = [('A', 'first'), ('A', 'second'), ('B', 'third')]
train = [row for row in rows if row[0] == 'A']
test = [row for row in rows if row[0] == 'B']
separate = {row[0] for row in train}.isdisjoint(row[0] for row in test)
print(len(train), len(test), separate)
