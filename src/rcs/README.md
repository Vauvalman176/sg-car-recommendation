# Recommender Engine

## Overview

A content-based car recommendation engine. Given a user's current car, it calculates trade-in value, filters candidates by constraints, ranks by cosine similarity, and outputs top-K recommendations with net upgrade costs and deal flags.

**Input**: `data/pbda_output/predictions.parquet` (from the ML pipeline)
**Output**: HTML report + JSON results in `data/rcs_output/`

---

## How to Run

```bash
cd /Users/jai/Downloads/bigdata_project/src
python3 -m rcs.run_rcs
```

---

## Module Structure

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `filters.py` | Hard constraint filtering (vehicle type, COE, budget, price) |
| `similarity.py` | Cosine similarity engine with min-max normalization |
| `recommender.py` | Main orchestration: scrap value + filter + similarity + output |
| `run_rcs.py` | Pipeline runner with demo use cases |

---

## Pipeline Steps

1. Load predictions.parquet (5,033 cars with prices, predictions, financial data)
2. Calculate user's car trade-in value (PARF rebate + COE rebate)
3. Apply hard constraints (vehicle type, COE remaining, budget, price range)
4. Normalize features (min-max scaling to [0,1])
5. Compute cosine similarity between user's car and candidates
6. Return top K most similar cars
7. Calculate net upgrade cost for each recommendation
8. Generate HTML report and JSON results

---

## Recommendation Algorithm

### Hard Constraints (filters.py)

| Constraint | Column | Default |
|------------|--------|---------|
| Vehicle type | `type_of_vehicle` | Any |
| COE remaining | `coe_months_left` | >= 60 months (5 years) |
| Monthly budget | `monthly_installment` | No limit |
| Price range | `price` | No limit |

### Similarity Features (similarity.py)

| Feature | Description | Why |
|---------|-------------|-----|
| `engine_cap` | Engine capacity (cc) | Core mechanical spec |
| `power` | Engine power (bhp) | Performance indicator |
| `curb_weight` | Vehicle weight (kg) | Size/class indicator |
| `mileage` | Odometer reading (km) | Wear indicator |
| `car_age_years` | Years since registration | Depreciation indicator |

### Cosine Similarity Formula

```
similarity = dot(user_vector, car_vector) / (||user|| * ||car||)
```

Both vectors are min-max normalized to [0,1] before computation.

---

## Trade-in Value Calculation

### PARF Rebate

| Car Age | Rebate % of ARF |
|---------|-----------------|
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

### Net Upgrade Cost

```
net_upgrade_cost = new_car_price - user_scrap_value
```

---

## Output Files

```
data/rcs_output/
├── recommendation_report.html          # General recommendations (visual)
├── recommendation_results.json         # General recommendations (machine-readable)
├── recommendation_report_luxury.html   # Luxury sedan recommendations
└── recommendation_results_luxury.json  # Luxury sedan recommendations
```

---

## Deal Detection

Cars are flagged using ML predictions from Phase 3:
- **UNDERPRICED**: Listed > 15% below predicted price (good deal)
- **FAIR**: Within +/- 15% of predicted price
- **OVERPRICED**: Listed > 15% above predicted price (bad deal)
