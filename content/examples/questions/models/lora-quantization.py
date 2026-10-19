rows, columns, rank = 64, 64, 4
full = rows*columns
adapter = rank*(rows+columns)
print(full, adapter, full*16//8, full*4//8)
