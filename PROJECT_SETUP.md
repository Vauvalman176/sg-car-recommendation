# Big Data Project - Setup & Structure

**Project Title**: Intelligent Car Discovery & Financial Feasibility Platform
**Date Created**: January 28, 2026
**Location**: `/Users/jai/Downloads/bigdata_project/`

---

## 📁 Project Structure

```
bigdata_project/
├── PROJECT_SUMMARY.md           # Project overview and architecture
├── PROJECT_SETUP.md            # This file - setup instructions
├── webscrap_sgcarmart/         # Web scraping tool (GitHub: msamhz)
│   ├── main.py                 # Main scraping script
│   ├── tools.py                # Helper functions
│   ├── params.yaml             # Configuration parameters
│   ├── requirements.txt        # Python dependencies
│   ├── data/                   # Output folder for scraped data
│   └── README.md              # Tool documentation
├── data/                       # Project datasets (to be created)
│   ├── raw/                    # Raw scraped data
│   ├── processed/              # Cleaned datasets
│   └── coe/                    # Government COE data
├── notebooks/                  # Jupyter notebooks (to be created)
│   ├── 01_data_exploration.ipynb
│   ├── 02_bead_ingestion.ipynb
│   ├── 03_pbda_processing.ipynb
│   └── 04_rcs_recommender.ipynb
├── src/                        # Source code (to be created)
│   ├── bead/                   # BEAD module
│   ├── pbda/                   # PBDA module
│   └── rcs/                    # RCS module
└── docs/                       # Documentation (to be created)
    ├── citations.md            # Data source citations
    └── methodology.md          # Research methodology
```

---

## ✅ Completed Setup Steps

- [x] Created project directory: `~/Downloads/bigdata_project/`
- [x] Copied PROJECT_SUMMARY.md to project folder
- [x] Cloned web scraping repository from GitHub
- [x] Installed Python dependencies (selenium, pandas, beautifulsoup4, etc.)

---

## 🔧 System Information

**Python Version**: 3.13.5
**Operating System**: macOS (Darwin 24.6.0)
**Project Path**: `/Users/jai/Downloads/bigdata_project/`

---

## 📦 Installed Dependencies

### Web Scraping Tools:
- `selenium==4.40.0` - Browser automation
- `webdriver-manager==4.0.2` - WebDriver management
- `beautifulsoup4==4.14.3` - HTML parsing
- `pandas==3.0.0` - Data manipulation
- `tqdm==4.67.1` - Progress bars
- `PyYAML==6.0.3` - Configuration files

### Supporting Libraries:
- `ipykernel==7.1.0` - Jupyter notebook support
- `numpy==2.4.1` - Numerical computing

---

## 🎯 Next Steps

### Phase 1: Data Collection (CURRENT)
1. Run web scraper to collect Singapore used car data
2. Download COE data from data.gov.sg API
3. Validate data quality (target: 10,000+ rows)

### Phase 2: Data Organization
1. Create additional project directories
2. Move scraped data to `data/raw/`
3. Document data sources in `docs/citations.md`

### Phase 3: BEAD Module
1. Set up PySpark environment
2. Build data ingestion pipeline
3. Simulate HDFS/Sqoop operations

### Phase 4: PBDA Module
1. Data cleaning and preprocessing
2. Financial calculator implementation
3. ML model training (Linear, RF, GBT)

### Phase 5: RCS Module
1. Feature vectorization
2. Cosine similarity recommender
3. Budget filtering logic

---

## 📝 Data Source Attribution

### Primary: SGCarMart Listings
- **Tool Used**: msamhz/webscrap_sgcarmart (GitHub)
- **Repository**: https://github.com/msamhz/webscrap_sgcarmart
- **License**: Used for academic purposes (no explicit license)
- **Citation**:
  ```
  msamhz. (2025). webscrap_sgcarmart: Web scraping tool for
  Singapore car market data. GitHub repository.
  https://github.com/msamhz/webscrap_sgcarmart
  ```

### Secondary: Government Data
- **Source**: data.gov.sg (LTA Official Data)
- **API**: COE Bidding Results
- **License**: Singapore Open Data License
- **URL**: https://data.gov.sg/datasets/d_69b3380ad7e51aff3a7dcc84eba52b8a/view

---

## ⚠️ Important Notes

### Ethical Data Collection
1. **Rate Limiting**: Use 3-second delays between requests
2. **Scope**: Limit to 10,000-15,000 listings (don't scrape entire site)
3. **Purpose**: Academic use only (non-commercial)
4. **Attribution**: Always cite data sources

### Academic Integrity
- The web scraping tool is used for **data acquisition only** (~10% of project)
- All **analysis, ML models, and recommender system** are original work (~90%)
- Properly cited in all documentation and reports

---

## 🚀 Quick Start Guide

### Running the Web Scraper

```bash
# Navigate to scraper directory
cd ~/Downloads/bigdata_project/webscrap_sgcarmart

# Run the main script
python3 main.py

# When prompted, enter:
# URL: https://www.sgcarmart.com/used_cars/listing.php
# Max pages: 100 (adjust based on your needs)
```

### Expected Output
- Raw CSV: `carlist_YYYYMMDD.csv`
- Processed CSV: `data/processed_carlist.csv`
- Fields: 27+ columns including price, COE, ARF, mileage, etc.

---

## 📊 Data Fields Collected

| Field Name | Description |
|------------|-------------|
| price | Listing price (SGD) |
| coe | Certificate of Entitlement paid |
| arf | Additional Registration Fee |
| omv | Open Market Value |
| dereg_value | Deregistration value estimate |
| mileage | Distance traveled (km) |
| engine_cap | Engine capacity (cc) |
| power | Horsepower output |
| reg_date | Registration date |
| type_of_vehicle | Category (Sedan, SUV, etc.) |
| ... | (27+ fields total) |

---

## 📚 Resources

### Documentation
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
- [Web Scraper README](webscrap_sgcarmart/README.md) - Tool usage guide

### External Links
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [data.gov.sg API](https://data.gov.sg/)
- [Singapore LTA DataMall](https://datamall.lta.gov.sg/)

---

## ✅ Status Tracking

**Current Phase**: Data Collection
**Progress**: 30% Complete

**Completed**:
- ✅ Project setup and organization
- ✅ Web scraping tool installation
- ✅ Environment configuration

**In Progress**:
- 🔄 Running web scraper
- 🔄 Collecting 10K+ car listings

**Pending**:
- ⏳ COE data download
- ⏳ BEAD module implementation
- ⏳ PBDA module implementation
- ⏳ RCS module implementation
- ⏳ Testing and evaluation
- ⏳ Final documentation

---

**Last Updated**: January 28, 2026
**Maintained By**: Jai (University Big Data Project)
