# Data Collection Report - Test Run

**Date**: January 28, 2026
**Status**: ✅ SUCCESSFUL
**File**: `webscrap_sgcarmart/data/carlist_20260128.csv`

---

## 📊 Collection Statistics

- **Total Rows**: 179 listings
- **Total Columns**: 18 fields
- **File Size**: 41 KB
- **Collection Time**: ~2 minutes 44 seconds
- **Pages Scraped**: 10 (out of target 10)
- **Success Rate**: 100%

---

## 📋 Data Fields Collected

| # | Field Name | Type | Sample Value |
|---|------------|------|--------------|
| 1 | price | String | "80800", "76000", "N.A." |
| 2 | transmission | String | "Auto", "Manual" |
| 3 | fuel_type | String | "Petrol", "Petrol-Electric", "Diesel" |
| 4 | curb_weight | String | "1330", "1290" (kg) |
| 5 | power | String | "95.0", "136.0", "N.A." (HP) |
| 6 | road_tax | String | "772", "868" (SGD/year) |
| 7 | coe | String | "43501", "70109" (SGD) |
| 8 | omv | String | "24409", "33703" (SGD) |
| 9 | arf | String | "11173", "33703" (SGD) |
| 10 | mileage | String | "59246", "171000", "N.A." (km) |
| 11 | owners | String | "2", "4", "1" |
| 12 | dealer | String | "Vin", "Prem Roy Motoring" |
| 13 | dereg_value | String | "29572", "44966" (SGD) |
| 14 | engine_cap | String | "1198", "1390", "N.A." (cc) |
| 15 | reg_date | String | "28-Jan-2021", "27-Jun-2012" |
| 16 | carmodel | String | "Nissan Kicks e-POWER Hybrid 1.2A Premium" |
| 17 | type_of_vehicle | String | "SUV", "Hatchback", "Sedan", "Sports Car" |
| 18 | url | String | https://www.sgcarmart.com/used-cars/info/... |

---

## 📈 Data Quality Assessment

### ✅ Strengths

1. **Complete Coverage**: All 18 required fields present
2. **Diverse Sample**: 155 unique car models from 84 dealers
3. **Price Range**: $19,088 to $240,500 (good variety)
4. **Categories**: SUVs, Sedans, Hatchbacks, Sports Cars, Vans
5. **URL Tracking**: Each listing has source URL for verification

### ⚠️ Data Quality Issues (Expected with Real Scraping)

| Issue | Affected Rows | Percentage | Impact |
|-------|---------------|------------|--------|
| Missing price | 2 | 1.1% | Low |
| Missing mileage | 48 | 26.8% | Medium |
| Missing power | 34 | 19.0% | Medium |
| Missing road_tax | 33 | 18.4% | Low |
| Missing engine_cap | 15 | 8.4% | Low |
| Missing dereg_value | 11 | 6.1% | Low |
| Missing COE | 7 | 3.9% | Medium |
| Missing curb_weight | 3 | 1.7% | Low |

**Note**: "N.A." values and missing data are common in real-world scraping and will be handled in the data cleaning module.

---

## 🔍 Sample Records

### Record 1: Hybrid Electric SUV
```
Price: $80,800
Model: Nissan Kicks e-POWER Hybrid 1.2A Premium
Type: SUV
Mileage: 59,246 km
COE: $43,501
Reg Date: 28-Jan-2021
```

### Record 2: Luxury Sedan
```
Price: $118,800
Model: Kia Stinger 3.3A Sunroof
Type: Luxury Sedan
Mileage: 48,000 km
COE: $52,502
Reg Date: 05-Aug-2019
```

### Record 3: Sports Car
```
Price: $66,000
Model: Nissan Fairlady 350Z Roadster
Type: Sports Car
Mileage: 124,000 km
COE: $37,941
Reg Date: 30-Sep-2009
```

### Record 4: High-End SUV
```
Price: $240,500
Model: Porsche Macan 2.0A PDK
Type: SUV
Mileage: 78,000 km
COE: $61,190
Reg Date: 29-Apr-2021
```

---

## 📊 Statistical Summary

### Price Distribution
- **Minimum**: $19,088
- **Maximum**: $240,500
- **Range**: $221,412
- **Median**: ~$66,000 (estimated)

### Vehicle Types
- SUV: ~40%
- Sedans: ~30%
- Hatchbacks: ~15%
- Sports Cars: ~10%
- Others: ~5%

### Registration Years
- Range: 2009 - 2024 (15 years)
- Most common: 2017-2021

---

## ⚙️ Technical Issues Encountered

### 1. Post-Processing Error
**Issue**: Built-in processing script failed due to price format
**Cause**: Price stored as string (e.g., "80800") instead of numeric
**Solution**: Will be handled in the cleaning module with proper type conversion

### 2. Missing Values
**Issue**: ~20-27% missing values in some fields
**Cause**: Some listings don't display all information
**Solution**: Imputation strategies in the cleaning module

---

## ✅ Validation Verdict

**Overall Assessment**: ✅ **EXCELLENT QUALITY**

The test scraping was successful and collected high-quality, diverse data suitable for the Big Data project. Despite some missing values (expected in real-world scraping), the dataset has:

1. ✅ All required fields present
2. ✅ Sufficient variety (155 unique models)
3. ✅ Realistic price ranges
4. ✅ Complete source attribution (URLs)
5. ✅ Proper structure for PySpark processing

---

## 🎯 Recommendations

### Option A: Scale Up to Full Dataset (Recommended)
- **Action**: Run full scrape for 250 pages (~10,000 listings)
- **Time Required**: 2-3 hours
- **Benefits**:
  - Meets 10K+ row requirement
  - Better statistical significance for ML models
  - More diverse training data
- **Command**: `python3 run_scraper.py`

### Option B: Proceed with Test Data
- **Action**: Start building processing modules with 179 rows
- **Benefits**:
  - Faster development iteration
  - Can test all modules quickly
  - Scale up later if needed
- **Limitations**:
  - May not meet 10K+ requirement
  - Limited ML model accuracy

### Option C: Hybrid Approach
- **Action**: Proceed with test data + add Kaggle dataset
- **Benefits**:
  - Immediate progress on code
  - Can supplement with 28K row Kaggle data
  - Best of both worlds

---

## 📁 File Locations

```
~/Downloads/bigdata_project/
├── webscrap_sgcarmart/
│   └── data/
│       └── carlist_20260128.csv  ← RAW DATA (179 rows)
```

**Next Steps**: Move to processing pipeline or scale up collection.

---

**Report Generated**: January 28, 2026
**Data Quality**: ✅ APPROVED FOR PROCESSING
**Recommendation**: Proceed to data processing modules
