#!/usr/bin/env python3
import sys

# Map: company_id \t total_count  →  (key=COUNT_PADDED, value=company_id \t COUNT)
# We pad counts so lexical sort == numeric sort.
PAD = 12  # supports counts up to ~10^12

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) < 2:
        continue
    comp, cnt = parts[0].strip(), parts[1].strip()
    if not cnt.isdigit():
        continue
    cnt_i = int(cnt)
    key = str(cnt_i).zfill(PAD)
    # value carries both fields so reducer can output in required format
    sys.stdout.write(f"{key}\t{comp}\t{cnt_i}\n")
