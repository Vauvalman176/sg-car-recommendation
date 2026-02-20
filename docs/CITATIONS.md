# Data Source Citations & Attribution

**Project**: Intelligent Car Discovery & Financial Feasibility Platform
**Date**: January 2026

---

## Primary Data Source: Singapore Used Car Listings

### Web Scraping Tool
**Tool Name**: webscrap_sgcarmart
**Author**: msamhz
**Repository**: https://github.com/msamhz/webscrap_sgcarmart
**Release Date**: October 2025
**License**: No explicit license (used for academic purposes)

**Full Citation**:
```
msamhz. (2025). webscrap_sgcarmart: Web scraping tool for Singapore
car market data [Computer software]. GitHub.
https://github.com/msamhz/webscrap_sgcarmart
```

**Usage Statement**:
> We utilized the webscrap_sgcarmart tool (msamhz, 2025) to collect
> publicly available car listing data from SGCarMart for academic research
> purposes. The tool was configured with ethical scraping practices
> including rate limiting (3-second delays) and limited scope (10,000
> listings). All data collection complies with academic fair use principles.

---

### Data Source: SGCarMart
**Website**: https://www.sgcarmart.com/used_cars/listing.php
**Type**: Public car listing platform
**Data Collected**:
- Vehicle specifications (make, model, engine, transmission)
- Pricing information (list price, COE, ARF, OMV)
- Registration details (date, mileage, ownership)
- Financial metrics (depreciation, deregistration value)

**Ethical Considerations**:
- Data scraped from publicly accessible pages only
- No login bypass or paywall circumvention
- Rate limiting implemented (3 seconds between requests)
- Academic use only (non-commercial)
- Limited scope to minimize server load

---

## Secondary Data Source: LTA COE Data

### Official Government Data
**Source**: Singapore Land Transport Authority (LTA)
**Platform**: data.gov.sg
**Dataset**: COE Bidding Results / Prices
**Dataset ID**: d_69b3380ad7e51aff3a7dcc84eba52b8a
**API Endpoint**: https://data.gov.sg/api/action/datastore_search?resource_id=d_69b3380ad7e51aff3a7dcc84eba52b8a
**License**: Singapore Open Data License
**Access**: Free API access
**Update Frequency**: Bi-weekly (after each COE bidding exercise)

**Full Citation**:
```
Land Transport Authority. (2025). COE Bidding Results / Prices
[Dataset]. Singapore Government Data Portal.
https://data.gov.sg/datasets/d_69b3380ad7e51aff3a7dcc84eba52b8a/view
```

**Data Fields Used**:
- Bidding date
- Vehicle category (A, B, C, E)
- Premium (quota premium price)
- Quota available
- Bids received

---

## Supplementary Data Sources

### Car Population Statistics
**Source**: Singapore Land Transport Authority (LTA)
**Dataset**: Annual Car Population by Make
**URL**: https://data.gov.sg/datasets/d_20d3fc7f08caa581c5586df51a8993c5/view
**License**: Singapore Open Data License

**Citation**:
```
Land Transport Authority. (2024). Annual Car Population by Make
[Dataset]. Singapore Government Data Portal.
```

### New Car Registrations
**Source**: Singapore Land Transport Authority (LTA)
**Dataset**: Monthly New Registration of Cars by Make
**URL**: https://data.gov.sg/dataset/monthly-new-registration-of-cars-by-make
**License**: Singapore Open Data License

---

## Software & Libraries Used

### Data Collection
- **Python**: 3.13.5
- **Selenium**: 4.40.0 (browser automation)
- **BeautifulSoup4**: 4.14.3 (HTML parsing)
- **Pandas**: 3.0.0 (data manipulation)

### Data Processing (To be used)
- **PySpark**: 3.x (distributed data processing)
- **Spark MLlib**: ML model implementation

### Development Environment
- **Operating System**: macOS 14.6.0
- **IDE**: VS Code
- **Version Control**: Git

---

## Academic Integrity Statement

This project uses the webscrap_sgcarmart tool for **data acquisition only**,
representing approximately 10% of the total project scope. The remaining 90%
consists of original work including:

- Data cleaning and preprocessing pipelines
- Financial calculation algorithms
- Machine learning model implementation
- Recommender system design and implementation
- Analysis, interpretation, and documentation

All code beyond data collection is original and developed specifically
for this university project.

---

## Usage in Academic Reports

### For Methods Section:
```
Data Collection:
We collected Singapore used car listing data using the open-source
webscrap_sgcarmart tool (msamhz, 2025) configured with ethical scraping
parameters. The dataset was enriched with official COE pricing data from
Singapore's Land Transport Authority via the data.gov.sg API. Our final
dataset comprises 10,000+ used car listings with 27+ attributes per vehicle.
```

### For References Section:
```
msamhz. (2025). webscrap_sgcarmart [Computer software]. GitHub.
https://github.com/msamhz/webscrap_sgcarmart

Land Transport Authority. (2025). COE Bidding Results / Prices [Dataset].
Singapore Government Data Portal.
https://data.gov.sg/datasets/d_69b3380ad7e51aff3a7dcc84eba52b8a/view
```

---

## Data Availability Statement

**For Academic Publication**:
> The raw dataset used in this study was collected from publicly available
> sources (SGCarMart listings and LTA government data) using automated
> scraping tools. Due to ethical considerations and potential Terms of
> Service restrictions, we cannot redistribute the raw scraped data.
> However, the data collection methodology is fully reproducible using
> the cited open-source tools and government APIs. Processed datasets
> with aggregated statistics can be made available upon reasonable request
> to the corresponding author.

---

## Contact for Data Inquiries

**Project Lead**: [Your Name]
**University**: [Your Institution]
**Course**: Big Data Engineering & Analytics
**Date**: January 2026

For questions about data sources or methodology, please refer to:
- PROJECT_SUMMARY.md (project overview)
- PROJECT_SETUP.md (technical setup)
- docs/methodology.md (research methodology)

---

**Last Updated**: January 28, 2026
