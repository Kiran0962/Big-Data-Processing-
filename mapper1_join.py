#!/usr/bin/env python3
import os, sys

# Reduce-side join on taxi_id
# Taxis.txt: taxi_id \t company_id
# Trips.txt: ... contains taxi_id (assumed 2nd col: trip_id \t taxi_id \t ...)
# Mapper tags records so reducer can join.

def emit(k, v):
    sys.stdout.write(f"{k}\t{v}\n")

infile = os.environ.get("mapreduce_map_input_file", "")
is_taxis = infile.endswith("/Taxis.txt") or infile.endswith("Taxis.txt")
is_trips = infile.endswith("/Trips.txt") or infile.endswith("Trips.txt")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    if is_taxis:
        if len(parts) < 2:  # must be taxi_id, company_id
            continue
        taxi_id, company_id = parts[0].strip(), parts[1].strip()
        if taxi_id and company_id:
            emit(taxi_id, f"TAXI|{company_id}")
    elif is_trips:
        # assume trip_id \t taxi_id \t ...
        if len(parts) >= 2:
            taxi_id = parts[1].strip()
        else:
            continue
        if taxi_id:
            emit(taxi_id, "TRIP|1")
    else:
        # Fallback: guess by column counts if someone concatenated inputs
        # Prefer treat as Taxis if exactly 2 cols, otherwise Trips if >=2
        if len(parts) == 2:
            taxi_id, company_id = parts[0].strip(), parts[1].strip()
            if taxi_id and company_id:
                emit(taxi_id, f"TAXI|{company_id}")
        elif len(parts) >= 2:
            taxi_id = parts[1].strip()
            if taxi_id:
                emit(taxi_id, "TRIP|1")
