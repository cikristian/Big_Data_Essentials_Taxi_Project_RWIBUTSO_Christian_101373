# Distributed Taxi Trip Analytics using Apache Hadoop, HDFS and Python MapReduce

**Author:** Christian Rwibutso (Reg. No. 101373)
**Course:** Big Data Essentials — AUCA MSc Big Data Analytics

A Hadoop-based analytics pipeline for NYC TLC Yellow Taxi trip data, built with HDFS for
distributed storage and Python (Hadoop Streaming) MapReduce jobs for distributed processing.
The pipeline ingests three months of real trip data (Aug–Oct 2023, ~9.19M raw records),
cleans it, and runs nine independent analyses plus a compulsory two-stage MapReduce job,
all documented and compared against an equivalent single-machine Pandas implementation.

## Repository Structure

```
├── mappers/                    # 10 Python mapper scripts
│   ├── mapper_hourly.py        # Hourly demand
│   ├── mapper_daily.py         # Day-of-week demand
│   ├── mapper_location.py      # Pickup zone trip counts
│   ├── mapper_revenue.py       # Revenue by pickup zone
│   ├── mapper_payment.py       # Payment method analysis
│   ├── mapper_distance.py      # Distance-based fare analysis
│   ├── mapper_route.py         # Pickup→dropoff route analysis
│   ├── mapper_duration.py      # Trip duration analysis
│   ├── mapper_anomaly.py       # Anomaly detection
│   └── mapper_top_revenue.py   # Stage 2 of multi-stage job (reads Stage 1 output)
├── reducers/                   # 10 matching Python reducer scripts
├── clean_taxi_data.py          # Data cleaning + quality report (Section 7)
├── convert_parquet_to_csv.py   # Converts raw TLC Parquet files to CSV
├── perf_compare_pandas.py      # Pandas-side performance benchmark
├── make_visualizations.py      # Generates the 7 required charts (matplotlib)
├── taxi_zone_lookup.csv        # TLC LocationID → zone name reference table
├── commands.txt                # Full HDFS + Hadoop Streaming command log
├── Taxi_Analytics_Report.pdf   # Full written report (~19 pages)
└── README.md                   # This file
```

## Dataset

NYC TLC Yellow Taxi Trip Records, August–October 2023, downloaded from the official
[TLC Trip Record Data page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

| Month | Raw Records | Cleaned Records |
|---|---|---|
| Aug 2023 | 2,824,209 | 2,626,459 (93.00%) |
| Sep 2023 | 2,846,722 | 2,602,789 (91.43%) |
| Oct 2023 | 3,522,285 | 3,241,120 (92.02%) |
| **Total** | **9,193,216** | **8,470,368 (92.14%)** |

TLC distributes data as Parquet; `convert_parquet_to_csv.py` converts it to CSV since
Hadoop Streaming with arbitrary Python scripts works most naturally on line-oriented text.

## Environment

- **Hadoop 3.5.0** — single-node pseudo-distributed cluster, native Windows install
- **Java (JDK) 1.8.0_202**
- HDFS: NameNode, DataNode, SecondaryNameNode
- YARN: ResourceManager, NodeManager
- Python 3 (mappers/reducers use only the standard library — no external dependencies
  needed on cluster nodes)

## Setup & Reproduction

1. **Install prerequisites**: Hadoop 3.5.0, JDK 8, Python 3, `pip install pandas pyarrow matplotlib`
2. **Start Hadoop daemons**:
   ```
   %HADOOP_HOME%\sbin\start-dfs.cmd
   %HADOOP_HOME%\sbin\start-yarn.cmd
   ```
3. **Download the dataset** from the TLC portal into `Data/` (Parquet format)
4. **Convert and clean**:
   ```
   python convert_parquet_to_csv.py
   python clean_taxi_data.py
   ```
5. **Create the HDFS structure and upload data** — see `commands.txt` for the full list,
   e.g.:
   ```
   hdfs dfs -mkdir -p /taxi_project/input/raw /taxi_project/input/cleaned
   hdfs dfs -put Data/csv/*.csv /taxi_project/input/raw/
   hdfs dfs -put Data/cleaned/*.csv /taxi_project/input/cleaned/
   ```
6. **Run each MapReduce job** (repeat per analysis — see `commands.txt` for all nine plus
   the multi-stage job):
   ```
   hadoop jar %HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.5.0.jar ^
     -input /taxi_project/input/cleaned ^
     -output /taxi_project/output/hourly ^
     -mapper "python mapper_hourly.py" -reducer "python reducer_hourly.py" ^
     -file mappers/mapper_hourly.py -file reducers/reducer_hourly.py
   ```
   Jobs that use `taxi_zone_lookup.csv` (locations, revenue, routes) need an additional
   `-file taxi_zone_lookup.csv` flag.
7. **Pull results and visualize**:
   ```
   hdfs dfs -getmerge /taxi_project/output/hourly Data/results_hourly.tsv   (repeat per job)
   python make_visualizations.py
   python perf_compare_pandas.py
   ```

## Analyses Implemented

1. Hourly taxi demand
2. Daily demand (weekday vs weekend)
3. Pickup location analysis (top/bottom zones)
4. Revenue by pickup location
5. Payment method analysis
6. Distance-based fare analysis
7. Busiest pickup–dropoff routes
8. Trip duration analysis
9. Anomaly detection
10. **Multi-stage job**: Stage 1 (revenue by zone) → Stage 2 reads Stage 1's HDFS output
    directly and ranks the top 10 revenue-generating zones

## Key Results

- **Busiest hour**: 18:00 (594,722 trips) — **quietest**: 04:00 (43,580 trips)
- **Top pickup zone**: JFK Airport (485,095 trips, $39.5M revenue — more than double the
  next-highest zone)
- **Payment**: Credit card accounts for 81% of trips and 85% of revenue
- **Anomalies**: 0.4% of cleaned records show an extreme fare-per-mile (>$50/mile)
- **Performance**: Pandas (~39 sec) outperformed the single-node Hadoop job (~139 sec) at
  this dataset size (~8.5M records fit comfortably in memory); see the full report for the
  discussion of when Hadoop's distributed model becomes the better choice as data scales
  beyond a single machine

## Known Limitations

- Single-node cluster — true multi-node parallelism and fault tolerance were not
  demonstrated, only inferred from the architecture
- Native Windows Hadoop introduced friction not typically seen on Linux (path-separator
  issues, shuffle-phase timeouts under load) — documented and resolved in the full report
- All reducers ran with the Hadoop Streaming default of one reducer task (no
  `-D mapreduce.job.reduces` override was set)

See `Taxi_Analytics_Report.pdf` for the complete write-up, including HDFS/YARN evidence
screenshots, the full performance comparison, and answers to all business questions.

