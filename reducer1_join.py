#!/usr/bin/env python3
import sys

# For each taxi_id, we may see:
#   TAXI|<company_id>  (one)
#   TRIP|1             (many)
# Emit company_id \t 1 for each trip

current_taxi = None
company_id = None
trip_count_for_taxi = 0

def flush(taxi, comp, c):
    if not comp or c == 0:
        return
    for _ in range(c):
        sys.stdout.write(f"{comp}\t1\n")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    k, v = line.split("\t", 1)
    if current_taxi is None:
        current_taxi = k

    if k != current_taxi:
        flush(current_taxi, company_id, trip_count_for_taxi)
        current_taxi = k
        company_id = None
        trip_count_for_taxi = 0

    if v.startswith("TAXI|"):
        company_id = v.split("|", 1)[1]
    elif v.startswith("TRIP|"):
        trip_count_for_taxi += 1

# last key
flush(current_taxi, company_id, trip_count_for_taxi)
