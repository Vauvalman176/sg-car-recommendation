# Intelligent Car Discovery & Financial Feasibility Platform

**University Big Data Project** | January 2026
**Location**: `~/Downloads/bigdata_project/`

---

## Project Overview

This project develops an intelligent platform to assist Singaporean drivers in navigating complex vehicle ownership costs by calculating trade-in values and recommending alternative vehicles within budget constraints.

**Key Features**:
- Scrap value calculator (PARF + COE rebates)
- ML-based price prediction (PySpark MLlib)
- Content-based recommender system (cosine similarity)
- Financial feasibility analysis

---

## Current Status

| Phase | Module | Status | Description |
|-------|--------|--------|-------------|
| 1 | Data Collection | ✅ Complete | 5,089 car listings + 1,900 COE records |
| 2 | BEAD | ✅ Complete | Data ingestion, validation, profiling |
| 3 | PBDA | ✅ Complete | Feature engineering, ML training (LR, RF, GBT) |
| 4 | RCS | ✅ Complete | Recommendation engine with cosine similarity |

**Progress**: 100% Complete

---

## Project Structure

```
bigdata_project/
├── README.md                    # This file
├── PROJECT_SUMMARY.md           # Architecture overview
│
├── data/
│   ├── raw/                     # Raw scraped data
│   ├── coe/                     # COE API data (1,900 records)
│   ├── processed/               # BEAD output: Parquet files & profiles
│   │   ├── cars.parquet         # Spark-optimized car data
│   │   ├── coe.parquet          # Spark-optimized COE data
│   │   └── *_profile_report.html # Data quality dashboards
│   ├── pbda_output/             # PBDA output: Models & predictions
│   │   ├── models/              # 3 trained ML models + feature pipeline
│   │   ├── predictions.parquet  # 5,033 cars with predicted prices
│   │   └── model_comparison_report.html
│   └── rcs_output/              # RCS output: Recommendations
│       ├── recommendation_report.html
│       └── recommendation_results.json
│
├── docs/
│   ├── PHASE_DOCUMENTATION.md   # Complete phase guide
│   ├── CITATIONS.md             # Data source citations
│   └── WEB_SCRAPING_GUIDE.md    # Scraping instructions
│
├── src/
│   ├── bead/                    # Phase 2: Ingestion ✅
│   │   ├── ingest.py            # Data loading & Spark session
│   │   ├── profiler.py          # Data quality profiling
│   │   ├── schema.py            # Schema definitions
│   │   └── utils.py             # Shared utilities
│   ├── pbda/                    # Phase 3: Processing & ML ✅
│   │   ├── features.py          # Feature engineering pipeline
│   │   ├── financial.py         # PARF, COE, loan calculations
│   │   ├── model.py             # LR, RF, GBT training
│   │   └── evaluate.py          # Metrics & cross-validation
│   └── rcs/                     # Phase 4: Recommender ✅
│       ├── filters.py           # Constraint filtering
│       ├── similarity.py        # Cosine similarity engine
│       └── recommender.py       # Recommendation orchestration
│
├── webscrap_sgcarmart/          # Phase 1: Data collection ✅
│   ├── data/                    # Scraped CSV files (5,089 records)
│   ├── auto_scraper.py          # Main scraper
│   └── tools.py                 # Scraping utilities
│
└── scripts/
    └── download_coe_data.py     # COE API downloader
```

---

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip3 install pyspark==3.5.3 pandas numpy setuptools selenium beautifulsoup4

# Verify Java (needs 11+)
java -version
```

### Run Full Pipeline

```bash
cd /Users/jai/Downloads/bigdata_project/src

# Phase 2: BEAD (Data Ingestion & Profiling)
python3 -m bead.run_bead

# Phase 3: PBDA (Feature Engineering & ML)
python3 -m pbda.run_pbda

# Phase 4: RCS (Recommendations)
python3 -m rcs.run_rcs
```

### View Reports

```bash
# Data quality profiles
open data/processed/car_profile_report.html

# ML model comparison
open data/pbda_output/model_comparison_report.html

# Car recommendations
open data/rcs_output/recommendation_report.html
```

---

## Data Summary

### Car Listings (SGCarMart)

| Metric | Value |
|--------|-------|
| Total Records | 5,089 |
| Columns | 28 |
| Date Range | 1965 - 2026 |
| Source | Web scraping |

**Key Fields**: price, transmission, fuel_type, power, mileage, coe, omv, arf, dereg_value, reg_date, carmodel, type_of_vehicle

### COE Data (data.gov.sg)

| Metric | Value |
|--------|-------|
| Total Records | 1,900 |
| Date Range | 2010-01 to 2026-01 |
| Source | REST API |

**Key Fields**: month, vehicle_class, premium, quota, bids_received

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Data Collection | Selenium, BeautifulSoup, Requests |
| Data Processing | PySpark 3.5.3, Pandas |
| ML Models | PySpark MLlib (LinearRegression, RandomForest, GBT) |
| Recommender | Cosine Similarity (NumPy) |
| Language | Python 3.9+ |
| Java | JDK 11+ |

---

## ML Model Results

**Best Model**: Linear Regression (best generalization on 5K samples)

| Model | Test R2 | Test RMSE | 5-Fold CV RMSE |
|-------|---------|-----------|----------------|
| **Linear Regression** | **0.8741** | **$63,397** | **$44,424** |
| Random Forest | 0.8260 | $74,507 | $52,115 |
| GBT | 0.7475 | $89,768 | $71,065 |

**Features**: engine_cap, power, curb_weight, mileage, coe, omv, arf, road_tax, owners, car_age_years, coe_months_left + 3 engineered + 3 categorical (OHE)

**Anomaly Detection**: Cars flagged as overpriced/underpriced/fair based on +/-15% deviation from predicted price.

---

## Example Use Case

**Scenario**: Jane owns a 2019 Honda Vezel (6 years old, 48 months COE left).

**System Output**:
1. **Trade-in Value**: $29,750 (PARF: $9,750 + COE rebate: $20,000)
2. **Candidates**: 1,094 cars matching constraints (COE > 5yrs, < $1,500/month)
3. **Top Match**: Opel Crossland 1.2A at $79,800 (similarity: 0.9994)
4. **Net Cost**: $50,050 after trade-in
5. **Luxury Option**: Mercedes-Benz A200 at $116,688 (similarity: 0.9941)

---

## Academic Modules

### BEAD (Big Data Engineering & Analytics) ✅
- Data ingestion from multiple sources (CSV, API)
- PySpark DataFrame processing with schema validation
- Automated data profiling with HTML dashboards
- Parquet file generation for optimized storage

### PBDA (Processing Big Data Analytics) ✅
- Feature engineering pipeline (StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler)
- Financial calculations (PARF rebate, COE rebate, loan details, depreciation)
- 3 ML models trained with 5-fold cross-validation
- Price prediction and anomaly detection (overpriced/underpriced flags)

### RCS (Recommender & Consumer System) ✅
- Content-based filtering with cosine similarity
- Multi-constraint optimization (vehicle type, COE, budget, price)
- Budget-aware recommendations with net upgrade cost
- ML-powered deal detection (underpriced = good deal)

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/PHASE_DOCUMENTATION.md](docs/PHASE_DOCUMENTATION.md) | Complete phase-by-phase guide |
| [src/bead/README.md](src/bead/README.md) | BEAD module documentation |
| [src/pbda/README.md](src/pbda/README.md) | PBDA module documentation |
| [src/rcs/README.md](src/rcs/README.md) | RCS module documentation |
| [docs/CITATIONS.md](docs/CITATIONS.md) | Data source attributions |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Architecture overview |

---

**Last Updated**: February 12, 2026
**Version**: 3.0
**Status**: All 4 Phases Complete
