#!/usr/bin/env bash
set -euo pipefail

# Paths
STREAM_JAR="./hadoop-streaming-3.1.4.jar"
JOIN_OUT="/tmp/task3_join"
COUNT_OUT="/tmp/task3_count"
SORT_IN="$COUNT_OUT"
SORT_OUT="/Output/Task3"
PARTITIONS="/tmp/task3_partitions.lst"

# Clean old runs
hadoop fs -rm -r -f "$JOIN_OUT" || true
hadoop fs -rm -r -f "$COUNT_OUT" || true
hadoop fs -rm -r -f "$SORT_OUT" || true
hadoop fs -rm -f "$PARTITIONS" || true

echo "=== Job 1: Join Trips with Taxis (3 reducers) ==="
hadoop jar "$STREAM_JAR" \
  -D mapreduce.job.name="Task3-Job1-Join" \
  -D mapreduce.job.reduces=3 \
  -D stream.num.map.output.key.fields=1 \
  -D mapreduce.partition.keycomparator.options="-k1,1" \
  -input /Input/Trips.txt \
  -input /Input/Taxis.txt \
  -output "$JOIN_OUT" \
  -mapper mapper1_join.py \
  -reducer reducer1_join.py \
  -file mapper1_join.py \
  -file reducer1_join.py

echo "=== Job 2: Count trips per company (3 reducers) ==="
hadoop jar "$STREAM_JAR" \
  -D mapreduce.job.name="Task3-Job2-Count" \
  -D mapreduce.job.reduces=3 \
  -D stream.num.map.output.key.fields=1 \
  -D mapreduce.partition.keycomparator.options="-k1,1" \
  -input "$JOIN_OUT" \
  -output "$COUNT_OUT" \
  -mapper mapper2_count.py \
  -reducer reducer2_count.py \
  -file mapper2_count.py \
  -file reducer2_count.py

echo "=== Build partition file for global ascending sort (3 reducers) ==="
# We are NOT sorting the final output with bash. We only compute split points
# to configure TotalOrderPartitioner so that the MapReduce job produces
# globally sorted output across 3 reducers.
# Steps:
#   - Extract counts (2nd field),
#   - Sort numerically to find 33% and 66% split boundaries,
#   - Write them (zero-padded) into PARTITIONS as required.

PAD=12
TMP_LOCAL="$(mktemp)"
hadoop fs -cat "$COUNT_OUT/part-"* | awk -F'\t' '{print $2}' | grep -E '^[0-9]+$' | sort -n > "$TMP_LOCAL"

N=$(wc -l < "$TMP_LOCAL" | tr -d ' ')
if [ "$N" -eq 0 ]; then
  echo "No records to sort. Creating empty output."
  hadoop fs -mkdir -p "$SORT_OUT"
  exit 0
fi

# Compute 2 split indices for 3 reducers
# floor( N/3 ) and floor( 2N/3 ), clamp to [1..N]
i1=$(( (N + 2) / 3 ))       # ~33%
i2=$(( (2*N + 2) / 3 ))     # ~66%
if [ "$i1" -lt 1 ]; then i1=1; fi
if [ "$i2" -lt 1 ]; then i2=1; fi
if [ "$i1" -gt "$N" ]; then i1="$N"; fi
if [ "$i2" -gt "$N" ]; then i2="$N"; fi

b1=$(sed -n "${i1}p" "$TMP_LOCAL")
b2=$(sed -n "${i2}p" "$TMP_LOCAL")

printf "%012d\n%012d\n" "$b1" "$b2" > /tmp/task3_partitions.lst
rm -f "$TMP_LOCAL"
hadoop fs -put -f /tmp/task3_partitions.lst "$PARTITIONS"
rm -f /tmp/task3_partitions.lst

echo "=== Job 3: Global ascending sort by total trips (3 reducers, TotalOrderPartitioner) ==="
hadoop jar "$STREAM_JAR" \
  -D mapreduce.job.name="Task3-Job3-Sort" \
  -D mapreduce.job.reduces=3 \
  -D stream.num.map.output.key.fields=1 \
  -D mapreduce.partition.keycomparator.options="-k1,1" \
  -D mapreduce.totalorderpartitioner.natural.order=true \
  -D mapreduce.totalorderpartitioner.path="$PARTITIONS" \
  -partitioner org.apache.hadoop.mapreduce.lib.partition.TotalOrderPartitioner \
  -input "$SORT_IN" \
  -output "$SORT_OUT" \
  -mapper mapper3_sort.py \
  -reducer reducer3_sort.py \
  -file mapper3_sort.py \
  -file reducer3_sort.py

echo "=== Final merged preview ==="
hadoop fs -getmerge "$SORT_OUT/part-"* Task3_output.txt
head Task3_output.txt
echo "Done. Final HDFS output: $SORT_OUT"
