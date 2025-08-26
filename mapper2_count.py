#!/usr/bin/env python3
import sys

# Pass-through and sanitize: input = company_id \t 1
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) >= 2:
        comp, one = parts[0].strip(), parts[1].strip()
        if comp and one.isdigit():
            sys.stdout.write(f"{comp}\t{one}\n")
