parameters = 7_000_000_000
fp16, int4 = parameters*16//8, parameters*4//8
cache_bytes = 1_000_000_000
print(fp16, int4, int4+cache_bytes)
