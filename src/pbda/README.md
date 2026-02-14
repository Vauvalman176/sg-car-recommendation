# Feature Engineering & ML Pipeline

## Overview

This module handles feature engineering, financial calculations, ML model training, and price prediction for the Singapore car recommendation system.

**Input**: Parquet files from ingestion phase (`cars.parquet`, `coe.parquet`)
**Output**: Trained models, predictions with anomaly flags, comparison reports

---

## How to Run

```bash
cd /Users/jai/Downloads/bigdata_project/src
python3 -m pbda.run_pbda
```

---

## Module Structure

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `financial.py` | PARF rebate, COE rebate, loan, depreciation calculations |
| `features.py` | Imputation, COE join, ML pipeline (StringIndexer/OHE/VectorAssembler/Scaler) |
| `model.py` | Train LinearRegression, RandomForest, GBT models |
| `evaluate.py` | Metrics (RMSE/MAE/R2), 5-fold CV, HTML+JSON reports |
| `run_pbda.py` | Pipeline orchestrator |

---

## Pipeline Steps

1. Load Parquet data (from ingestion output)
2. Calculate financial metrics (PARF, COE rebate, loan, depreciation)
3. Feature engineering (filter, impute, join COE premium, engineer features)
4. Build ML pipeline (StringIndexer -> OneHotEncoder -> VectorAssembler -> StandardScaler)
5. Train/test split (80/20, seed=42)
6. Train 3 models (LinearRegression, RandomForest, GBT)
7. Evaluate on train + test sets
8. 5-fold cross-validation
9. Compare models, select best by test R2
10. Generate predictions with anomaly flags
11. Save all outputs

---

## Financial Formulas

### PARF Rebate (based on vehicle age)

| Age | Rebate % of ARF |
|-----|-----------------|
| < 5 years | 75% |
| 5-6 years | 70% |
| 6-7 years | 65% |
| 7-8 years | 60% |
| 8-9 years | 55% |
| 9-10 years | 50% |
| > 10 years | 0% |

### COE Rebate

```
coe_rebate = coe_premium * max(coe_months_left, 0) / 120
```

### Loan Calculation

```
loan_pct = 70% if OMV <= $20,000, else 60%
loan_amount = price * loan_pct
monthly_installment = (loan_amount * (1 + 0.0278 * 7)) / 84
```

### Monthly Depreciation

```
monthly_depreciation = (price - scrap_value) / coe_months_left
```

---

## ML Features

**Numeric (11)**: engine_cap, power, curb_weight, mileage, coe, omv, arf, road_tax, owners, car_age_years, coe_months_left

**Engineered (3)**: mileage_per_year, power_to_weight, coe_premium_at_reg

**Categorical (3, One-Hot Encoded)**: transmission, fuel_type, type_of_vehicle

**Target**: price

---

## Output Files

```
data/pbda_output/
├── models/
│   ├── linearregression_model/    # PySpark ML model directory
│   ├── randomforest_model/        # PySpark ML model directory
│   ├── gbt_model/                 # PySpark ML model directory
│   └── feature_pipeline/          # Fitted feature pipeline
├── predictions.parquet            # All cars with predicted_price + anomaly flags
├── model_comparison_report.html   # Visual HTML report
├── model_comparison.json          # Machine-readable metrics
└── feature_importance.json        # Feature rankings for all models
```

---

## Anomaly Detection

Cars are flagged based on deviation between predicted and actual price:
- **Overpriced**: actual > predicted + 15%
- **Underpriced**: actual < predicted - 15% (good deal)
- **Fair**: within +/- 15%
