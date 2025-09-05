#!/usr/bin/env python3
import sys

# Reducer sees keys in ascending order (thanks to TotalOrderPartitioner + comparators).
# We just re-emit "company_id \t total_count" in the same order.
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    # expected: COUNT_PADDED \t company_id \t count
    if len(parts) >= 3:
        _, comp, cnt = parts[0], parts[1], parts[2]
        sys.stdout.write(f"{comp}\t{cnt}\n")
