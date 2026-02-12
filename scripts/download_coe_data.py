#!/usr/bin/env python3
"""
Download COE Bidding Results from data.gov.sg API
Official Singapore Government Open Data
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time

def download_coe_data():
    """Download COE bidding results from data.gov.sg API"""

    print("="*80)
    print("📊 Downloading COE Data from data.gov.sg")
    print("="*80)
    print()

    # API endpoint
    base_url = "https://data.gov.sg/api/action/datastore_search"
    resource_id = "d_69b3380ad7e51aff3a7dcc84eba52b8a"

    print("📍 API Endpoint: data.gov.sg")
    print(f"📂 Dataset: COE Bidding Results / Prices")
    print(f"🔑 Resource ID: {resource_id}")
    print()

    all_records = []
    offset = 0
    limit = 1000  # Max records per request
    total_records = None

    print("🔄 Fetching data...")

    while True:
        # Build request URL
        url = f"{base_url}?resource_id={resource_id}&limit={limit}&offset={offset}"

        try:
            # Make API request
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check if request was successful
            if not data.get('success'):
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                break

            # Extract records
            result = data.get('result', {})
            records = result.get('records', [])

            if total_records is None:
                total_records = result.get('total', 0)
                print(f"📊 Total records available: {total_records:,}")
                print()

            if not records:
                break

            all_records.extend(records)
            offset += len(records)

            # Progress update
            progress = (len(all_records) / total_records * 100) if total_records else 0
            print(f"   Downloaded: {len(all_records):,} / {total_records:,} ({progress:.1f}%)", end='\r')

            # Check if we've got all records
            if len(all_records) >= total_records:
                break

            # Rate limiting - be respectful to the API
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Network error: {e}")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

    print()
    print()

    if all_records:
        # Convert to DataFrame
        df = pd.DataFrame(all_records)

        print("✅ Download Complete!")
        print("="*80)
        print(f"📊 Records Downloaded: {len(df):,}")
        print(f"📋 Columns: {len(df.columns)}")
        print()

        # Show column names
        print("📋 Available Fields:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        print()

        # Data preview
        print("="*80)
        print("🔍 Sample Data (First 5 Records)")
        print("="*80)
        print(df.head().to_string())
        print()

        # Date range
        if 'month' in df.columns:
            print("📅 Date Range:")
            print(f"   Earliest: {df['month'].min()}")
            print(f"   Latest: {df['month'].max()}")
            print()

        # Categories
        if 'vehicle_class' in df.columns or 'bidding_no' in df.columns:
            print("🚗 Vehicle Categories:")
            if 'vehicle_class' in df.columns:
                for cat in df['vehicle_class'].unique()[:10]:
                    count = len(df[df['vehicle_class'] == cat])
                    print(f"   {cat}: {count} records")
            print()

        # Save to CSV
        output_file = "../data/coe/coe_bidding_results.csv"
        df.to_csv(output_file, index=False)

        print("="*80)
        print(f"💾 Data Saved To: {output_file}")
        print("="*80)
        print()

        # Also save metadata
        metadata = {
            "download_date": datetime.now().isoformat(),
            "source": "data.gov.sg",
            "dataset": "COE Bidding Results / Prices",
            "resource_id": resource_id,
            "total_records": len(df),
            "columns": list(df.columns),
            "date_range": {
                "earliest": str(df['month'].min()) if 'month' in df.columns else None,
                "latest": str(df['month'].max()) if 'month' in df.columns else None
            }
        }

        with open("../data/coe/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print("📝 Metadata saved to: ../data/coe/metadata.json")
        print()

        return df
    else:
        print("❌ No data downloaded")
        return None

if __name__ == "__main__":
    df = download_coe_data()

    if df is not None:
        print("="*80)
        print("✅ COE DATA DOWNLOAD COMPLETE")
        print("="*80)
        print()
        print("🎯 Next Steps:")
        print("   1. Use this data to enrich car listings")
        print("   2. Calculate historical COE trends")
        print("   3. Merge with scraped data in PBDA module")
        print("="*80)
