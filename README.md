# Task 3 (COSC2637) — 3-Job Hadoop Streaming Pipeline

**Goal:** Count number of trips per taxi company and produce **globally ascending** results by trip count using **three MapReduce jobs** (join → count → sort). Each job runs with **exactly 3 reducers**.

## HDFS I/O
- Inputs (case sensitive):
  - `/Input/Trips.txt`
  - `/Input/Taxis.txt`  (format: `taxi_id\tcompany_id`)
- Final output:
  - `/Output/Task3`  (assessed)

## Jobs
1. **Join** (reduce-side) on `taxi_id` → outputs `company_id\t1` per trip  
   Output: `/tmp/task3_join`
2. **Count** by `company_id` → outputs `company_id\tTOTAL`  
   Output: `/tmp/task3_count`
3. **Sort** globally ascending by `TOTAL` using **TotalOrderPartitioner** with a computed partition file  
   Output: `/Output/Task3`

> We do **not** sort the final output using bash. The bash step only computes partition split points to configure **TotalOrderPartitioner**.

## Run
