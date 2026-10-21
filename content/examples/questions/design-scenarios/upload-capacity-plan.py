"""Capacity arithmetic only: no object is uploaded and no memory is allocated."""
from math import ceil
MiB = 1024 ** 2
GiB = 1024 ** 3
file_bytes = 100_000_000_000  # decimal 100 GB
part_bytes = 64 * MiB
parts = ceil(file_bytes / part_bytes)
allocations_mib = dict(runtime=512, parser=256, embedding=128, network=256, queue=256)
reserved = sum(allocations_mib.values()) * MiB
headroom = 2 * GiB - reserved
assert parts == 1491
assert headroom == 640 * MiB
# This explicit reserve catches configuration growth before a load test.
assert headroom >= 512 * MiB
print("parts:", parts)
print("headroom MiB:", headroom // MiB)
