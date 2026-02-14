# Data Ingestion & Profiling Module

## Overview

This module handles data ingestion, schema validation, and profiling for the Singapore Car Recommendation System. It loads raw data from CSV files, validates schemas, generates quality reports, and saves data in Parquet format for efficient downstream processing.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Module Structure](#module-structure)
3. [Data Flow](#data-flow)
4. [How to Run](#how-to-run)
5. [Input/Output](#inputoutput)
6. [Schema Definitions](#schema-definitions)
7. [Data Profiling](#data-profiling)
8. [Dependencies](#dependencies)
9. [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION MODULE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Raw CSV     │───>│  PySpark     │───>│  Parquet     │      │
│  │  Files       │    │  DataFrame   │    │  Files       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   ▼                   │               │
│         │           ┌──────────────┐            │               │
│         │           │  Data        │            │               │
│         └──────────>│  Profiler    │<───────────┘               │
│                     └──────────────┘                            │
│                           │                                      │
│                           ▼                                      │
│                   ┌──────────────┐                              │
│                   │  HTML/JSON   │                              │
│                   │  Reports     │                              │
│                   └──────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
src/bead/
├── __init__.py      # Module exports and public API
├── schema.py        # PySpark schema definitions for car & COE data
├── ingest.py        # Data loading and transformation functions
├── profiler.py      # Data quality profiling and report generation
├── utils.py         # Helper utilities
├── run_bead.py      # Main pipeline runner script
└── README.md        # This documentation file
```

### File Descriptions

| File | Purpose |
|------|---------|
| `__init__.py` | Exposes public functions: `load_car_data`, `load_coe_data`, `create_spark_session`, `profile_dataframe`, `generate_profile_report` |
| `schema.py` | Defines `CAR_SCHEMA` and `COE_SCHEMA` using PySpark StructType. Contains column descriptions for documentation. |
| `ingest.py` | Core ingestion logic - reads CSVs, applies transformations, calculates derived fields (car age, COE remaining), saves Parquet. |
| `profiler.py` | Generates data quality statistics - null counts, distinct values, min/max, percentiles. Outputs HTML and JSON reports. |
| `utils.py` | Helper functions for directory creation, formatting, logging. |
| `run_bead.py` | Orchestrates the complete pipeline - can be run standalone. |

---

## Data Flow

```
INPUT FILES:
├── webscrap_sgcarmart/data/carlist_20260128_with_loan_info.csv  (5,089 rows)
└── data/coe/coe_bidding_results.csv                              (1,900 rows)

          │
          ▼ Step 1: Load into PySpark

SPARK DATAFRAMES:
├── car_df (28 columns)
└── coe_df (11 columns)

          │
          ▼ Step 2: Transform & Enrich

TRANSFORMATIONS APPLIED:
├── Parse reg_date → date type
├── Calculate car_age_years
├── Calculate coe_months_left
├── Cast numeric columns to DoubleType
├── Add data_source identifier
└── Add ingestion_timestamp

          │
          ▼ Step 3: Profile & Validate

PROFILING:
├── Null counts per column
├── Distinct value counts
├── Min/Max/Mean for numerics
├── Percentiles (25th, 50th, 75th)
└── Top values for categoricals

          │
          ▼ Step 4: Save Outputs

OUTPUT FILES:
├── data/processed/cars.parquet          # Optimized car data
├── data/processed/coe.parquet           # Optimized COE data
├── data/processed/car_profile.json      # Car profile metadata
├── data/processed/coe_profile.json      # COE profile metadata
├── data/processed/car_profile_report.html   # Interactive HTML report
└── data/processed/coe_profile_report.html   # Interactive HTML report
```

---

## How to Run

### Prerequisites

```bash
# Ensure PySpark is installed
pip3 install pyspark==3.5.3

# Ensure Java 11+ is installed
java -version
```

### Run the Pipeline

```bash
# From the project root directory
cd /Users/jai/Downloads/bigdata_project/src

# Run as module
python3 -m bead.run_bead
```

### Run Programmatically

```python
from bead import create_spark_session, load_car_data, load_coe_data
from bead import profile_dataframe, generate_profile_report

# Initialize Spark
spark = create_spark_session("MyApp")

# Load data
car_df = load_car_data(spark, "path/to/carlist.csv")
coe_df = load_coe_data(spark, "path/to/coe.csv")

# Profile data
profile = profile_dataframe(car_df, "Car Listings")
generate_profile_report(profile, "output/report.html")

# Save as Parquet
car_df.write.parquet("output/cars.parquet")
```

---

## Input/Output

### Input Files

| File | Description | Records | Source |
|------|-------------|---------|--------|
| `carlist_20260128_with_loan_info.csv` | Scraped car listings with loan analysis | 5,089 | SGCarMart |
| `coe_bidding_results.csv` | COE bidding results from 2010-2026 | 1,900 | data.gov.sg |

### Output Files

| File | Format | Description |
|------|--------|-------------|
| `cars.parquet` | Parquet | Spark-optimized car data, partitioned for efficient queries |
| `coe.parquet` | Parquet | Spark-optimized COE data |
| `car_profile_report.html` | HTML | Interactive data quality dashboard |
| `coe_profile_report.html` | HTML | Interactive data quality dashboard |
| `car_profile.json` | JSON | Machine-readable profile for automation |
| `coe_profile.json` | JSON | Machine-readable profile for automation |

---

## Schema Definitions

### Car Listings Schema (28 columns)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| price | Double | Yes | Listed selling price (SGD) |
| transmission | String | Yes | Auto / Manual |
| fuel_type | String | Yes | Petrol, Diesel, Electric, Hybrid |
| curb_weight | Double | Yes | Vehicle weight (kg) |
| power | Double | Yes | Engine power (bhp) |
| road_tax | Double | Yes | Annual road tax (SGD) |
| coe | Double | Yes | COE paid at registration (SGD) |
| omv | Double | Yes | Open Market Value (SGD) |
| arf | Integer | Yes | Additional Registration Fee (SGD) |
| mileage | Double | Yes | Odometer reading (km) |
| owners | Double | Yes | Number of previous owners |
| dealer | String | Yes | Dealer/seller name |
| dereg_value | Double | Yes | Deregistration value (SGD) |
| engine_cap | Double | Yes | Engine capacity (cc) |
| reg_date | String | Yes | First registration date |
| carmodel | String | Yes | Make and model name |
| type_of_vehicle | String | Yes | Category (SUV, Sedan, etc.) |
| url | String | Yes | Source listing URL |
| coe_expiry | String | Yes | COE expiry date |
| coe_months_left | Double | Yes | Months remaining on COE |
| max_loan_months | Double | Yes | Maximum loan tenure |
| min_downpayment_pct | Integer | Yes | Minimum downpayment % |
| max_loan_pct | Integer | Yes | Maximum loan-to-value % |
| can_loan_full_coe | Boolean | Yes | Can loan cover full COE period |
| reg_date_parsed | Date | Yes | Parsed registration date |
| car_age_years | Double | Yes | Vehicle age in years |
| data_source | String | No | Source identifier |
| ingestion_timestamp | Date | No | Ingestion date |

### COE Schema (11 columns)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| _id | Integer | Yes | Record ID |
| month | String | Yes | Bidding month (YYYY-MM) |
| bidding_no | Integer | Yes | Bidding round (1 or 2) |
| vehicle_class | String | Yes | Category A/B/C/D/E |
| quota | Integer | Yes | COEs available |
| bids_success | String | Yes | Successful bids |
| bids_received | String | Yes | Total bids |
| premium | Integer | Yes | COE premium (SGD) |
| coe_year | Integer | Yes | Extracted year |
| coe_month | Integer | Yes | Extracted month |
| ingestion_timestamp | Date | No | Ingestion date |

---

## Data Profiling

### Profile Metrics Collected

| Metric | Description | Applies To |
|--------|-------------|------------|
| null_count | Number of null/NaN values | All |
| null_percentage | Percentage of nulls | All |
| distinct_count | Approximate unique values | All |
| mean | Average value | Numeric |
| stddev | Standard deviation | Numeric |
| min | Minimum value | Numeric |
| max | Maximum value | Numeric |
| percentile_25 | 25th percentile | Numeric |
| percentile_50 | Median | Numeric |
| percentile_75 | 75th percentile | Numeric |
| top_values | Most common values (top 5) | String |

### Data Quality Summary (Car Listings)

| Column | Null % | Status |
|--------|--------|--------|
| mileage | 19.98% | ⚠️ High |
| power | 12.77% | ⚠️ High |
| road_tax | 12.22% | ⚠️ High |
| engine_cap | 7.35% | ⚠️ Medium |
| dereg_value | 5.17% | ⚠️ Medium |
| coe | 3.83% | ✅ Low |
| Others | <2% | ✅ Good |

---

## Dependencies

```
pyspark==3.5.3      # Spark SQL and DataFrames
py4j==0.10.9.7      # Python-Java bridge (auto-installed)
```

### System Requirements

- **Java**: JDK 11 or higher
- **Python**: 3.9+
- **Memory**: 4GB+ recommended
- **Disk**: ~500MB for Parquet output

---

## Troubleshooting

### Common Issues

#### 1. Java Version Error

```
UnsupportedClassVersionError: class file version 61.0
```

**Solution**: PySpark 4.x requires Java 17+. Either:
- Install Java 17: `brew install openjdk@17`
- Or use PySpark 3.5.x: `pip3 install pyspark==3.5.3`

#### 2. Spark Session Already Exists

```
Cannot run multiple SparkContexts at once
```

**Solution**: Stop existing session first:
```python
spark.stop()
```

#### 3. Memory Issues

```
Java heap space error
```

**Solution**: Increase driver memory in `create_spark_session()`:
```python
.config("spark.driver.memory", "8g")
```

#### 4. File Not Found

```
Path does not exist
```

**Solution**: Ensure you're running from the correct directory and input files exist.

---

## Next Phase

After ingestion completes, proceed to the ML pipeline:
- Feature engineering
- Financial calculations (PARF, depreciation)
- CatBoost model training

See: `src/pbda/README.md`

---

## Author

- **Module**: Data Ingestion
- **Project**: Singapore Car Recommendation System
- **Date**: January 2026
