# Web Scraping Guide - SGCarMart Data Collection

**Tool**: webscrap_sgcarmart by msamhz
**Purpose**: Collect Singapore used car listings for academic research

---

## ⚠️ Before You Start

### Ethical Scraping Checklist
- [ ] Data will be used for **academic purposes only**
- [ ] Will implement **rate limiting** (3+ second delays)
- [ ] Will limit **scope** (not scraping entire website)
- [ ] Will **cite the tool and data source** properly
- [ ] Understand this is **public data only** (no login bypass)

---

## 🚀 Quick Start

### Step 1: Navigate to Scraper Directory
```bash
cd ~/Downloads/bigdata_project/webscrap_sgcarmart
```

### Step 2: Run the Scraper
```bash
python3 main.py
```

### Step 3: Provide Inputs When Prompted

**Input 1 - URL:**
```
Enter the car listing URL:
https://www.sgcarmart.com/used_cars/listing.php
```

**Input 2 - Max Pages:**
```
Enter maximum pages to scrape: 100
```

**Calculation**:
- Typical page = ~40 listings
- 100 pages × 40 = ~4,000 listings
- For 10,000+ listings, run multiple times with different filters

---

## 📋 Scraping Strategies

### Strategy 1: Multiple Runs with Filters

**Run 1: Luxury Sedans**
```
URL: https://www.sgcarmart.com/used_cars/listing.php?CatID=1&AT=2
Pages: 50
Expected: ~2,000 luxury sedan listings
```

**Run 2: SUVs**
```
URL: https://www.sgcarmart.com/used_cars/listing.php?CatID=2
Pages: 50
Expected: ~2,000 SUV listings
```

**Run 3: Hatchbacks**
```
URL: https://www.sgcarmart.com/used_cars/listing.php?CatID=3
Pages: 50
Expected: ~2,000 hatchback listings
```

**Run 4: Sports Cars**
```
URL: https://www.sgcarmart.com/used_cars/listing.php?CatID=4
Pages: 30
Expected: ~1,200 sports car listings
```

**Run 5: MPVs**
```
URL: https://www.sgcarmart.com/used_cars/listing.php?CatID=5
Pages: 30
Expected: ~1,200 MPV listings
```

**Total**: ~10,000+ listings across all categories

---

### Strategy 2: Brand-Specific Scraping

**Popular Brands to Target**:
- Honda, Toyota (most listings)
- Mercedes, BMW (luxury segment)
- Hyundai, Mazda (mid-range)
- Volkswagen, Audi (European)

---

## 🔧 Configuration (params.yaml)

Before running, you can modify `params.yaml`:

```yaml
# Default configuration
scraping:
  delay_between_requests: 3  # seconds (be respectful!)
  max_retries: 2
  timeout: 30

data:
  output_folder: "data"
  file_prefix: "carlist"
```

**Recommended Changes for Ethical Scraping**:
```yaml
scraping:
  delay_between_requests: 5  # Increase to 5 seconds (safer)
  max_retries: 1             # Reduce retries
```

---

## 📊 Expected Output

### Raw CSV File
**Location**: `./carlist_YYYYMMDD_HHMMSS.csv`
**Format**: Raw scraped data (unprocessed)

### Processed CSV File
**Location**: `./data/processed_carlist_YYYYMMDD.csv`
**Format**: Cleaned and enriched data

### Sample Data Structure

| price | coe | arf | omv | mileage | reg_date | carmodel | type_of_vehicle |
|-------|-----|-----|-----|---------|----------|----------|-----------------|
| 185000 | 65000 | 42000 | 28000 | 45000 | 2019-08-25 | Mercedes C200 | Sedan |
| 88000 | 35000 | 18000 | 22000 | 65000 | 2018-03-15 | Honda Civic 1.6A | Sedan |

---

## ⏱️ Time Estimates

### Small Run (1,000 listings)
- **Scraping Time**: ~45-60 minutes
- **Processing Time**: ~2-3 minutes
- **Total**: ~1 hour

### Medium Run (5,000 listings)
- **Scraping Time**: ~3-4 hours
- **Processing Time**: ~5-7 minutes
- **Total**: ~4 hours

### Large Run (10,000 listings)
- **Scraping Time**: ~6-8 hours
- **Processing Time**: ~10-15 minutes
- **Total**: ~8 hours

**Tip**: Run overnight or in batches!

---

## 🐛 Common Issues & Solutions

### Issue 1: "Webdriver not found"
**Solution**:
```bash
pip3 install --upgrade webdriver-manager
```

### Issue 2: "Connection timeout"
**Cause**: Website is blocking rapid requests
**Solution**:
- Increase delay in `params.yaml` to 5+ seconds
- Reduce max_pages per run

### Issue 3: "Empty CSV generated"
**Cause**: Website structure changed
**Solution**:
- Check if SGCarMart URL is accessible
- Verify website hasn't been redesigned
- Review `tools.py` for selector updates

### Issue 4: "Too few listings collected"
**Cause**: Filtering might be too restrictive
**Solution**:
- Use base URL without filters
- Try multiple smaller runs instead of one large run

---

## ✅ Data Validation Checklist

After scraping, verify:
- [ ] Total rows ≥ 10,000 (for project requirement)
- [ ] No excessive duplicates (< 5%)
- [ ] Price column has realistic values ($50k-$500k)
- [ ] COE values are non-zero (where applicable)
- [ ] Registration dates are valid (not in future)
- [ ] Mileage values are reasonable (< 500,000 km)

**Validation Command**:
```bash
cd ~/Downloads/bigdata_project
python3 -c "
import pandas as pd
df = pd.read_csv('webscrap_sgcarmart/data/processed_carlist.csv')
print(f'Total rows: {len(df)}')
print(f'Duplicates: {df.duplicated().sum()}')
print(f'Missing prices: {df[\"price\"].isna().sum()}')
print(f'Date range: {df[\"reg_date\"].min()} to {df[\"reg_date\"].max()}')
"
```

---

## 📁 Post-Collection Organization

### Move Files to Project Structure
```bash
# Navigate to project root
cd ~/Downloads/bigdata_project

# Copy raw data
cp webscrap_sgcarmart/carlist_*.csv data/raw/

# Copy processed data
cp webscrap_sgcarmart/data/processed_carlist_*.csv data/processed/

# Create combined dataset (if multiple runs)
python3 -c "
import pandas as pd
import glob

# Read all processed files
files = glob.glob('data/processed/processed_carlist_*.csv')
dfs = [pd.read_csv(f) for f in files]

# Combine and remove duplicates
combined = pd.concat(dfs, ignore_index=True)
combined = combined.drop_duplicates(subset=['url'])

# Save
combined.to_csv('data/processed/combined_carlist_final.csv', index=False)
print(f'Combined dataset: {len(combined)} unique listings')
"
```

---

## 📝 Documentation for Your Report

### Sample Methodology Section:

```
Data Collection Methodology

We collected Singapore used car listing data using the open-source
webscrap_sgcarmart tool (msamhz, 2025) from GitHub. The tool employs
Selenium for browser automation and BeautifulSoup for HTML parsing.

Scraping Parameters:
- Data Source: SGCarMart (www.sgcarmart.com)
- Collection Period: January 28-29, 2026
- Rate Limiting: 5-second delays between requests
- Scope: 10,234 unique vehicle listings
- Categories: Sedans, SUVs, Hatchbacks, Sports Cars, MPVs

Ethical Considerations:
We implemented responsible scraping practices including rate limiting
to minimize server load, limited scope to avoid excessive data collection,
and ensured data is used solely for academic research purposes.

Data Fields Extracted:
27 attributes per vehicle including pricing (price, COE, ARF, OMV),
specifications (engine capacity, power, transmission), registration
details (date, mileage, ownership history), and financial metrics
(depreciation estimates, deregistration values).

Data Quality Assurance:
Post-collection validation confirmed 10,234 unique listings with < 2%
duplicates, complete pricing information for 98.7% of records, and
valid date ranges (2008-2024 registration years).
```

---

## 🎯 Success Criteria

Your data collection is complete when:
✅ **Quantity**: 10,000+ unique listings
✅ **Quality**: < 5% missing values in critical fields
✅ **Variety**: Multiple vehicle categories represented
✅ **Documentation**: All files organized in project structure
✅ **Citation**: Tool and source properly attributed

---

## 🆘 Need Help?

1. **Check tool README**: `cat webscrap_sgcarmart/README.md`
2. **Review code**: `main.py` has inline comments
3. **Check logs**: Error messages provide debugging hints
4. **GitHub Issues**: https://github.com/msamhz/webscrap_sgcarmart/issues

---

## ⏭️ Next Steps After Collection

Once data collection is complete:
1. ✅ Validate data quality
2. ✅ Move files to proper project directories
3. ✅ Document collection parameters
4. ✅ Begin COE data download from data.gov.sg
5. ✅ Start PySpark ingestion module

---

**Last Updated**: January 28, 2026
**Tool Version**: Latest (October 2025)
**Maintained By**: Project Team
