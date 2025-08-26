#!/usr/bin/env python3
import sys

# Sum trips per company_id
current = None
total = 0

def flush(k, s):
    if k is not None:
        sys.stdout.write(f"{k}\t{s}\n")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    comp, v = line.split("\t", 1)
    v = int(v) if v.isdigit() else 0
    if current is None:
        current = comp
    if comp != current:
        flush(current, total)
        current = comp
        total = 0
    total += v

flush(current, total)
