# Intelligent Car Discovery & Financial Feasibility Platform

**University Big Data Project** | January 2026

---

## Project Overview

An intelligent platform to help Singaporean drivers navigate complex vehicle ownership costs — calculates trade-in values, predicts fair market prices using ML, and recommends replacement cars within budget constraints.

**Key Features**:
- Scrap value calculator (PARF + COE rebates)
- ML-based price prediction (PySpark MLlib)
- Content-based recommender system (cosine similarity)
- Financial feasibility analysis (loan, depreciation, upgrade cost)

---

## Pipeline

| Phase | Description |
|-------|-------------|
| 1 - Data Collection | 5,089 car listings scraped + 1,900 COE records from API |
| 2 - Data Ingestion | PySpark ingestion, schema validation, profiling |
| 3 - ML Pipeline | Feature engineering, model training (LR, RF, GBT) |
| 4 - Recommender | Content-based recommendation engine |

---

## Project Structure

```
sg-car-recommendation/
├── data/
│   ├── raw/                     # Raw scraped CSVs
│   ├── coe/                     # COE API data
│   ├── processed/               # Cleaned Parquet files + profiles
│   ├── pbda_output/             # Models, predictions, reports
│   └── rcs_output/              # Recommendation reports
│
├── src/
│   ├── bead/                    # Data ingestion & profiling
│   │   ├── ingest.py
│   │   ├── profiler.py
│   │   ├── schema.py
│   │   └── utils.py
│   ├── pbda/                    # Feature engineering & ML
│   │   ├── features.py
│   │   ├── financial.py
│   │   ├── model.py
│   │   └── evaluate.py
│   └── rcs/                     # Recommender engine
│       ├── filters.py
│       ├── similarity.py
│       └── recommender.py
│
├── webscrap_sgcarmart/          # Web scraper (see Acknowledgements)
│   ├── auto_scraper.py
│   └── tools.py
│
├── scripts/
│   └── download_coe_data.py     # COE data downloader
│
└── docs/
    ├── PHASE_DOCUMENTATION.md
    ├── CITATIONS.md
    └── WEB_SCRAPING_GUIDE.md
```

---

## Quick Start

### Prerequisites

```bash
pip3 install pyspark==3.5.3 pandas numpy setuptools selenium beautifulsoup4

# Java 11+ required for PySpark
java -version
```

### Run the Pipeline

```bash
cd src/

# Step 1: Data ingestion & profiling
python3 -m bead.run_bead

# Step 2: Feature engineering & ML training
python3 -m pbda.run_pbda

# Step 3: Recommendations
python3 -m rcs.run_rcs
```

### View Reports

```bash
open data/processed/car_profile_report.html        # Data quality
open data/pbda_output/model_comparison_report.html  # ML results
open data/rcs_output/recommendation_report.html     # Recommendations
```

---

## Data Sources

### Car Listings (SGCarMart)
- **Records**: 5,089 used car listings
- **Fields**: price, transmission, fuel_type, power, mileage, coe, omv, arf, reg_date, carmodel, type_of_vehicle, etc.
- **Collection**: Web scraping using [webscrap_sgcarmart](https://github.com/msamhz/webscrap_sgcarmart) by msamhz

### COE Bidding Data (data.gov.sg)
- **Records**: 1,900 (2010-01 to 2026-01)
- **Fields**: month, vehicle_class, premium, quota, bids_received
- **Source**: [LTA COE Bidding Results API](https://data.gov.sg/datasets/d_69b3380ad7e51aff3a7dcc84eba52b8a/view)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Data Processing | PySpark 3.5.3 |
| ML Models | PySpark MLlib (Linear Regression, Random Forest, GBT) |
| Recommender | Cosine Similarity (NumPy) |
| Data Collection | Selenium, BeautifulSoup |
| Language | Python 3.9+ |

---

## ML Results

**Best Model**: Linear Regression (best generalization on 5K dataset)

| Model | Test R2 | Test RMSE | 5-Fold CV RMSE |
|-------|---------|-----------|----------------|
| **Linear Regression** | **0.8741** | **$63,397** | **$44,424** |
| Random Forest | 0.8260 | $74,507 | $52,115 |
| GBT | 0.7475 | $89,768 | $71,065 |

**Features used**: engine_cap, power, curb_weight, mileage, coe, omv, arf, road_tax, owners, car_age_years, coe_months_left + 3 engineered + 3 categorical (OHE)

---

## Example Use Case

**Scenario**: User owns a 2019 Honda Vezel (6 years old, 48 months COE left).

**Output**:
1. **Trade-in Value**: $29,750 (PARF: $9,750 + COE rebate: $20,000)
2. **Candidates**: 1,094 cars matching constraints (COE > 5yrs, < $1,500/month)
3. **Top Match**: Opel Crossland 1.2A at $79,800 (similarity: 0.9994)
4. **Net Cost**: $50,050 after trade-in
5. **Luxury Option**: Mercedes-Benz A200 at $116,688

---

## Acknowledgements

- **Web scraping tool**: [webscrap_sgcarmart](https://github.com/msamhz/webscrap_sgcarmart) by [msamhz](https://github.com/msamhz) — used for data collection from SGCarMart. The scraper handles pagination, data extraction, and basic preprocessing of car listing pages.
- **COE data**: [Singapore Land Transport Authority](https://data.gov.sg) via the data.gov.sg open data API.
- **Financial formulas**: Based on LTA's official PARF rebate schedule and MAS loan regulations.

---

## Documentation

- [Phase Documentation](docs/PHASE_DOCUMENTATION.md) — detailed guide for each phase
- [Citations](docs/CITATIONS.md) — full data source attributions
- [Project Summary](PROJECT_SUMMARY.md) — architecture overview
