# Intelligent Car Discovery & Financial Feasibility Platform
**Singapore Used Car Recommendation System**

---

## 🎯 Project Objective
Help Singaporean drivers find affordable replacement cars by calculating trade-in value and recommending similar vehicles within budget constraints.

---

## 📖 Process Summary
**End-to-End Pipeline:**
1. **Ingest** real Singapore car listings (Kaggle) + government COE data (data.gov.sg API)
2. **Clean** messy string data and parse complex fields (COE remaining, prices)
3. **Enrich** with financial metrics (loan amounts, monthly installments, PARF/COE rebates)
4. **Train** ML models (Linear, Random Forest, GBT) to predict fair market prices
5. **Calculate** user's current car scrap value using Singapore's PARF/COE regulations
6. **Filter** available cars by hard constraints (category, COE remaining, budget)
7. **Recommend** top 5 similar cars using cosine similarity on normalized features
8. **Display** upgrade options with net cost analysis (new price - trade-in value)

---

## 🏗️ Architecture

### **BEAD (Ingestion)**
- Load Kaggle Singapore used car dataset
- Load data.gov.sg COE historical data
- Simulate HDFS/Sqoop ingestion using PySpark

### **PBDA (Processing & ML)**
**Data Cleaning:**
- Clean price, depreciation, COE fields
- Parse "4yrs 5mths" → months
- Impute missing mileage per model group

**Financial Logic:**
- Max loan: 70% if OMV ≤ $20k, else 60%
- Monthly installment: `(Loan × (1 + 0.0278 × 7)) / 84`
- Scrap value: `PARF rebate + COE rebate`

**ML Models:**
1. Linear Regression (baseline)
2. Random Forest Regressor (main model)
3. Gradient Boosted Trees (comparison)

**Predictions:**
- Fair market price
- Scrap/resale value
- Price anomaly detection (overpriced/underpriced)

### **RCS (Recommender)**
- Content-based filtering (cosine similarity)
- Multi-stage filtering:
  1. Hard constraints (category, COE > 5yrs, budget)
  2. Feature similarity (engine, power, specs)
  3. Financial optimization (net upgrade cost)

---

## 📊 Datasets

**Primary:**
- [Kaggle: Singapore Used Car](https://www.kaggle.com/datasets/jiantay33/singapore-used-car) (~10k listings)

**Secondary:**
- [data.gov.sg: COE Bidding Results](https://data.gov.sg/datasets/d_69b3380ad7e51aff3a7dcc84eba52b8a/view) (API)

**Simulated:**
- PARF rebate table (age-based)

---

## 💡 Key Features

1. **Scrap Value Calculator**: Estimate trade-in value using PARF + COE rebates
2. **Constraint-Based Search**: Filter by category, COE remaining, monthly budget
3. **Similarity Recommender**: Find cars matching user's mechanical preferences
4. **Upgrade Cost Analysis**: Calculate net cost after trade-in

---

## 🛠️ Tech Stack

- **Framework**: PySpark (MLlib, SQL)
- **ML Libraries**: LinearRegression, RandomForestRegressor, GBTRegressor
- **Feature Engineering**: StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
- **Similarity**: Cosine similarity via normalized vectors
- **Environment**: VS Code (local) / Google Colab

---

## 📝 Example Use Case

**User Input:**
- Current car: Honda Vezel (COE ending soon)
- Budget: $1,200/month max
- Preference: Luxury sedan, COE > 5 years

**System Output:**
1. Scrap value: "Your Vezel = $12,125"
2. Top 5 recommendations (Mercedes C200, BMW 320i, etc.)
3. Net upgrade cost (New price - Scrap - Down payment)
4. Similarity scores + financial metrics

---

## 🎬 Case Study Example

**Scenario:** Jane owns a 2019 Honda Vezel (OMV: $22k, ARF: $15k, COE: 3 months left). The system calculates her scrap value at $12,125 (PARF: $11,250 + COE rebate: $875). She wants a luxury sedan under $1,200/month with fresh COE (>5 years). The ML model identifies her Vezel's fair value would be $85k if renewed, but scrapping is optimal. The recommender filters 2,400 listings → 47 luxury sedans → ranks by similarity to her Vezel's specs (150hp, 1.5L engine). Top recommendation: Mercedes C200 at $185k with 7yrs 8mths COE, monthly installment $1,150, net upgrade cost $127,375 after her $12k trade-in and 30% down payment. The system flags this as 8% underpriced vs ML prediction, marking it a "good deal."

---

## ✅ Implementation Status
- [x] Architecture designed
- [x] Datasets identified
- [x] ML models selected
- [x] Phase 1: Data Collection (5,089 listings + 1,900 COE records)
- [x] Phase 2: BEAD - Data ingestion, profiling, Parquet storage
- [x] Phase 3: PBDA - Feature engineering, 3 ML models (LR best, R2=0.87), anomaly detection
- [x] Phase 4: RCS - Cosine similarity recommender with constraint filtering
- [x] Testing & evaluation (5-fold CV, train/test split)
- [x] Documentation (README, phase docs, module READMEs)
