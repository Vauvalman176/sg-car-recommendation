# Project Phase Documentation

## Singapore Car Recommendation System - Technical Documentation

This document provides a comprehensive overview of all project phases, their purposes, and how to run each module.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Phase Summary](#phase-summary)
3. [Phase 1: Data Collection](#phase-1-data-collection)
4. [Phase 2: Data Ingestion](#phase-2-data-ingestion)
5. [Phase 3: Processing & ML](#phase-3-processing--ml)
6. [Phase 4: Recommender](#phase-4-recommender)
7. [Quick Start Guide](#quick-start-guide)
8. [Data Flow Diagram](#data-flow-diagram)

---

## Project Overview

### Objective
Build an intelligent platform to help Singaporean drivers find affordable replacement cars by:
1. Calculating trade-in/scrap value of current vehicle
2. Predicting fair market prices using ML
3. Recommending similar vehicles within budget constraints

### Tech Stack

| Component | Technology |
|-----------|------------|
| Data Collection | Selenium, BeautifulSoup, Requests |
| Data Processing | PySpark 3.5.3, Pandas |
| ML Models | PySpark MLlib (LinearRegression, RandomForest, GBT) |
| Recommender | Cosine Similarity (NumPy) |
| Language | Python 3.9+ |

---

## Phase Summary

| Phase | Module | Status | Description |
|-------|--------|--------|-------------|
| 1 | Data Collection | ✅ Complete | Web scraping SGCarMart + COE API |
| 2 | Data Ingestion | ✅ Complete | Data ingestion, validation, profiling |
| 3 | Processing & ML | ✅ Complete | Feature engineering, ML training, price prediction |
| 4 | Recommender | ✅ Complete | Recommendation engine with cosine similarity |

---

## Phase 1: Data Collection

### Purpose
Collect raw data from external sources for analysis.

### Data Sources

| Source | Type | Records | Method |
|--------|------|---------|--------|
| SGCarMart | Car Listings | 5,089 | Web Scraping (Selenium) |
| data.gov.sg | COE Bidding | 1,900 | REST API |

### Key Scripts

```
webscrap_sgcarmart/
├── auto_scraper.py      # Full automated scraper
├── resume_scraper.py    # Resume interrupted scrapes
├── fill_missing_data.py # Re-scrape N.A. values
├── clean_dataset.py     # Data cleaning pipeline
└── tools.py             # Scraping utilities

scripts/
└── download_coe_data.py # COE API downloader
```

### How to Run

```bash
# Scrape car listings (full run)
cd webscrap_sgcarmart
python3 auto_scraper.py

# Download COE data
cd scripts
python3 download_coe_data.py
```

### Output Files

| File | Location | Description |
|------|----------|-------------|
| `carlist_20260128.csv` | `webscrap_sgcarmart/data/` | Raw scraped data |
| `carlist_20260128_cleaned.csv` | `webscrap_sgcarmart/data/` | Cleaned data |
| `carlist_20260128_with_loan_info.csv` | `webscrap_sgcarmart/data/` | Enriched with loan analysis |
| `coe_bidding_results.csv` | `data/coe/` | COE historical data |

### Data Cleaning Applied

1. **Duplicates removed**: 46 duplicate URLs
2. **N.A. → null**: Converted string "N.A." to proper nulls
3. **Type conversion**: Strings → numeric/date types
4. **Whitespace trimmed**: Text columns cleaned
5. **Invalid data fixed**: owners=0 → null

### Enrichment Added

- `coe_expiry`: Calculated COE expiry date
- `coe_months_left`: Months remaining on COE
- `max_loan_months`: Maximum loan tenure
- `min_downpayment_pct`: 30% or 40% based on OMV
- `can_loan_full_coe`: Boolean flag

---

## Phase 2: Data Ingestion

### Purpose
Load cleaned data into PySpark, validate schemas, profile data quality, and save in optimized Parquet format.

### Module Location
```
src/bead/
├── __init__.py      # Module exports
├── schema.py        # Schema definitions
├── ingest.py        # Data loading functions
├── profiler.py      # Data quality profiler
├── utils.py         # Helper functions (shared across modules)
├── run_bead.py      # Pipeline runner
└── README.md        # Detailed documentation
```

### How to Run

```bash
cd /Users/jai/Downloads/bigdata_project/src
python3 -m bead.run_bead
```

### Input Files

| File | Records | Source |
|------|---------|--------|
| `carlist_20260128_with_loan_info.csv` | 5,089 | Phase 1 |
| `coe_bidding_results.csv` | 1,900 | Phase 1 |

### Output Files

| File | Format | Description |
|------|--------|-------------|
| `cars.parquet` | Parquet | Spark-optimized car data |
| `coe.parquet` | Parquet | Spark-optimized COE data |
| `car_profile_report.html` | HTML | Interactive quality dashboard |
| `coe_profile_report.html` | HTML | Interactive quality dashboard |
| `car_profile.json` | JSON | Profile metadata |
| `coe_profile.json` | JSON | Profile metadata |

### Data Quality Findings

| Column | Null % | Action |
|--------|--------|--------|
| mileage | 20% | Imputed in Phase 3 |
| power | 12.8% | Imputed in Phase 3 |
| road_tax | 12.2% | Imputed in Phase 3 |
| engine_cap | 7.4% | Imputed in Phase 3 |

---

## Phase 3: Processing & ML

### Purpose
Feature engineering, financial calculations, and ML model training for price prediction.

### Module Location
```
src/pbda/
├── __init__.py      # Module exports
├── features.py      # Feature engineering (StringIndexer/OHE/VectorAssembler/Scaler)
├── financial.py     # PARF rebate, COE rebate, loan calculations
├── model.py         # LinearRegression, RandomForest, GBT training
├── evaluate.py      # Metrics, cross-validation, HTML/JSON reports
├── run_pbda.py      # Pipeline runner
└── README.md        # Detailed documentation
```

### How to Run

```bash
cd /Users/jai/Downloads/bigdata_project/src
python3 -m pbda.run_pbda
```

### Input Files

| File | Records | Source |
|------|---------|--------|
| `cars.parquet` | 5,089 | Phase 2 |
| `coe.parquet` | 1,900 | Phase 2 |

### Output Files

| File | Format | Description |
|------|--------|-------------|
| `models/linearregression_model/` | PySpark ML | Best performing model |
| `models/randomforest_model/` | PySpark ML | Random Forest model |
| `models/gbt_model/` | PySpark ML | Gradient Boosted Trees model |
| `models/feature_pipeline/` | PySpark ML | Fitted feature engineering pipeline |
| `predictions.parquet` | Parquet | 5,033 cars with predicted prices + anomaly flags |
| `model_comparison_report.html` | HTML | Visual model comparison dashboard |
| `model_comparison.json` | JSON | Machine-readable metrics |
| `feature_importance.json` | JSON | Feature rankings for all models |

### Feature Engineering Pipeline

1. **Filtering**: Removed 36 invalid records (null/zero price, negative age)
2. **Imputation**: Median-by-vehicle-type for mileage, power, road_tax, engine_cap, curb_weight, coe
3. **COE Join**: Linked Category B COE premium at time of registration (410 used median fallback)
4. **Engineered Features**: mileage_per_year, power_to_weight, arf_double
5. **ML Pipeline**: StringIndexer → OneHotEncoder → VectorAssembler → StandardScaler

### ML Features

- **Numeric (11)**: engine_cap, power, curb_weight, mileage, coe, omv, arf, road_tax, owners, car_age_years, coe_months_left
- **Engineered (3)**: mileage_per_year, power_to_weight, coe_premium_at_reg
- **Categorical (3, One-Hot Encoded)**: transmission, fuel_type, type_of_vehicle
- **Target**: price

### Financial Calculations

| Calculation | Formula |
|-------------|---------|
| PARF Rebate | ARF × age_percentage (75% at <5yrs to 0% at >10yrs) |
| COE Rebate | COE × max(coe_months_left, 0) / 120 |
| Scrap Value | PARF rebate + COE rebate |
| Loan Amount | price × (70% if OMV ≤ $20K, else 60%) |
| Monthly Installment | (loan × (1 + 0.0278 × 7)) / 84 |
| Monthly Depreciation | (price - scrap_value) / coe_months_left |

### Model Results

| Model | Test R2 | Test RMSE | Test MAE | 5-Fold CV RMSE |
|-------|---------|-----------|----------|----------------|
| **Linear Regression** | **0.8741** | **$63,397** | **$30,374** | **$44,424** |
| Random Forest | 0.8260 | $74,507 | $22,141 | $52,115 |
| GBT | 0.7475 | $89,768 | $24,814 | $71,065 |

**Best Model**: Linear Regression (best test R2 and lowest CV RMSE; tree models overfit on 5K samples)

### Anomaly Detection

Cars flagged based on +/-15% deviation from predicted price:
- **Overpriced** (1,419 cars): Listed > 15% above predicted
- **Fair** (2,038 cars): Within +/- 15%
- **Underpriced** (1,576 cars): Listed > 15% below predicted (good deals)

---

## Phase 4: Recommender

### Purpose
Content-based recommendation system to suggest similar cars within user constraints, with trade-in value calculation and deal detection.

### Module Location
```
src/rcs/
├── __init__.py      # Module exports
├── filters.py       # Hard constraint filtering
├── similarity.py    # Cosine similarity engine (min-max normalization)
├── recommender.py   # Recommendation orchestration + HTML/JSON reports
├── run_rcs.py       # Pipeline runner with demo use cases
└── README.md        # Detailed documentation
```

### How to Run

```bash
cd /Users/jai/Downloads/bigdata_project/src
python3 -m rcs.run_rcs
```

### Input Files

| File | Records | Source |
|------|---------|--------|
| `predictions.parquet` | 5,033 | Phase 3 |

### Output Files

| File | Format | Description |
|------|--------|-------------|
| `recommendation_report.html` | HTML | General recommendations report |
| `recommendation_results.json` | JSON | Machine-readable results |
| `recommendation_report_luxury.html` | HTML | Luxury sedan recommendations |
| `recommendation_results_luxury.json` | JSON | Luxury sedan results |

### Recommendation Pipeline

1. **Trade-in Calculation**: PARF rebate + COE rebate for user's current car
2. **Hard Constraint Filtering**:
   - Vehicle type (optional)
   - COE remaining ≥ 60 months (5 years)
   - Monthly budget limit
   - Maximum price
3. **Cosine Similarity Scoring**: On normalized features (engine_cap, power, curb_weight, mileage, car_age_years)
4. **Top-K Selection**: 5 most similar candidates
5. **Net Upgrade Cost**: new_price - user_scrap_value
6. **Deal Detection**: Uses ML anomaly flags (underpriced = good deal)

### Demo Results (Honda Vezel Use Case)

**User's Car**: Honda Vezel 1.5A (6 years old, 48 months COE left)
- Trade-in: $29,750 (PARF: $9,750 + COE: $20,000)

**Demo 1 - Any Type** (1,094 candidates → top 5):

| Rank | Car | Price | Similarity | Net Cost | Monthly |
|------|-----|-------|-----------|----------|---------|
| 1 | Opel Crossland 1.2A X Turbo | $79,800 | 0.9994 | $50,050 | $794 |
| 2 | Peugeot 2008 1.2A PureTech | $90,800 | 0.9993 | $61,050 | $775 |
| 3 | Suzuki Vitara 1.4A GLX | $89,800 | 0.9992 | $60,050 | $766 |
| 4 | Honda Vezel Hybrid 1.5A | $93,800 | 0.9990 | $64,050 | $800 |
| 5 | MINI Cooper Clubman 1.5A | $118,800 | 0.9989 | $89,050 | $1,014 |

**Demo 2 - Luxury Sedans** (193 candidates → top 5):

| Rank | Car | Price | Similarity | Net Cost | Monthly |
|------|-----|-------|-----------|----------|---------|
| 1 | Mercedes-Benz A200 Sport | $116,688 | 0.9941 | $86,938 | $996 |
| 2 | BMW 218i Gran Coupe | $117,800 | 0.9932 | $88,050 | $1,005 |
| 3 | Mercedes-Benz A180 Saloon | $142,000 | 0.9926 | $112,250 | $1,212 |

---

## Quick Start Guide

### 1. Environment Setup

```bash
# Install dependencies
pip3 install pyspark==3.5.3 pandas numpy setuptools selenium beautifulsoup4

# Verify Java version (needs 11+)
java -version
```

### 2. Run Complete Pipeline

```bash
cd /Users/jai/Downloads/bigdata_project/src

# Phase 2: Data Ingestion & Profiling
python3 -m bead.run_bead

# Phase 3: Feature Engineering & ML
python3 -m pbda.run_pbda

# Phase 4: Recommendations
python3 -m rcs.run_rcs
```

### 3. View Reports

```bash
# Data quality profiles
open data/processed/car_profile_report.html

# ML model comparison
open data/pbda_output/model_comparison_report.html

# Car recommendations
open data/rcs_output/recommendation_report.html
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1: DATA COLLECTION                                               │
│  ┌──────────────┐    ┌──────────────┐                                  │
│  │  SGCarMart   │    │  data.gov.sg │                                  │
│  │  (Selenium)  │    │  (REST API)  │                                  │
│  └──────┬───────┘    └──────┬───────┘                                  │
│         │                    │                                          │
│         ▼                    ▼                                          │
│  ┌──────────────┐    ┌──────────────┐                                  │
│  │ carlist.csv  │    │   coe.csv    │                                  │
│  │  (5,089)     │    │   (1,900)    │                                  │
│  └──────┬───────┘    └──────┬───────┘                                  │
│         └────────┬───────────┘                                          │
│                  ▼                                                       │
│  PHASE 2: DATA INGESTION ✅                                              │
│  ┌─────────────────────────────────┐                                   │
│  │  • Load into PySpark            │                                   │
│  │  • Schema validation            │                                   │
│  │  • Data profiling               │                                   │
│  │  • Save as Parquet              │                                   │
│  └──────────────┬──────────────────┘                                   │
│                  ▼                                                       │
│  PHASE 3: PROCESSING & ML ✅                                             │
│  ┌─────────────────────────────────┐                                   │
│  │  • Feature engineering          │                                   │
│  │  • Financial calculations       │                                   │
│  │  • PySpark MLlib training       │                                   │
│  │  • Price prediction             │                                   │
│  │  • Anomaly detection            │                                   │
│  └──────────────┬──────────────────┘                                   │
│                  ▼                                                       │
│  PHASE 4: RECOMMENDER ✅                                                 │
│  ┌─────────────────────────────────┐                                   │
│  │  • Trade-in calculation         │                                   │
│  │  • Constraint filtering         │                                   │
│  │  • Cosine similarity            │                                   │
│  │  • Top-K recommendations        │                                   │
│  │  • Net cost analysis            │                                   │
│  └──────────────┬──────────────────┘                                   │
│                  ▼                                                       │
│  ┌──────────────────────────────────┐                                  │
│  │  USER OUTPUT:                    │                                  │
│  │  • Trade-in value: $29,750       │                                  │
│  │  • Top 5 recommendations         │                                  │
│  │  • Net upgrade cost              │                                  │
│  │  • Value flags (good deal?)      │                                  │
│  └──────────────────────────────────┘                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

**Last Updated**: February 12, 2026
**Status**: All 4 Phases Complete
