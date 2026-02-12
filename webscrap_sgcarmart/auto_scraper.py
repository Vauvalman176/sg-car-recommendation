#!/usr/bin/env python3
"""
Automated Full Scraper - No user input required
Automatically starts scraping 250 pages for 10K+ listings
"""

from tqdm import tqdm
from tools import collect_listing_links, extract_sgcarmart_car_details, get_or_append_carlist_df
import os
import pandas as pd
import numpy as np
import re
import yaml
from datetime import datetime
import time

def main():
    # Configuration
    main_url = "https://www.sgcarmart.com/used_cars/listing.php"
    max_pages = 250  # Target: ~10,000 listings

    start_time = datetime.now()

    print("="*80)
    print("🚀 FULL SCRAPING RUN - Singapore Used Car Data")
    print("="*80)
    print(f"📍 URL: {main_url}")
    print(f"📊 Max Pages: {max_pages}")
    print(f"📈 Expected Listings: ~{max_pages * 40:,}")
    print(f"⏱️  Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n🔄 Collecting listing links...")

    # Collect all listing links
    list_of_cars = collect_listing_links(main_url, max_pages=max_pages)

    print(f"✅ Found {len(list_of_cars)} car listings to process")
    print(f"⏱️  Estimated time: {len(list_of_cars) * 1.5 / 60:.1f} minutes\n")

    # Process each listing
    for cars in tqdm(list_of_cars, desc="Processing cars", unit="car"):
        max_retries = 5
        for attempt in range(max_retries):
            details = extract_sgcarmart_car_details(cars)
            if len(details) == 18:
                break
            time.sleep(1)
        else:
            print(f"Warning: Details for {cars} could not be extracted properly after {max_retries} attempts. Got: {details}")

        get_or_append_carlist_df(details)

    print("\n" + "="*80)
    print("📝  Note: Raw data may contain duplicate entries!")
    print("✨  Preprocessing will automatically remove duplicates from the dataset.")
    print("="*80)

    # Processing function
    def process_carlist_data(data_folder='data', params_path='params.yaml'):
        print(f"\n🔄 Processing collected data...")

        # Get most recent carlist CSV
        csv_files = [f for f in os.listdir(data_folder) if f.startswith("carlist_") and f.endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError("No carlist CSV files found.")
        csv_files_sorted = sorted(
            csv_files,
            key=lambda fn: fn.split("_")[1].replace(".csv", ""),
            reverse=True
        )
        csv_path = os.path.join(data_folder, csv_files_sorted[0])
        print(f"📁 Processing: {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"📊 Raw rows: {len(df)}")

        # Filter out rows with null transmission
        df = df[~df['transmission'].isnull()].copy(deep=True)

        # Parse registration date
        df['reg_date'] = pd.to_datetime(df['reg_date'], format='mixed', dayfirst=True, errors='coerce')

        today = pd.Timestamp(datetime.today().date())

        def years_months_left(reg_date, lifespan_years=10):
            if pd.isna(reg_date):
                return "Expired"
            end_date = reg_date + pd.DateOffset(years=lifespan_years)
            delta = end_date - today
            if delta.days < 0:
                return "Expired"
            years = delta.days // 365
            months = (delta.days % 365) // 30
            return f"{years} yr {months} mth"

        df['years_months_left'] = df['reg_date'].apply(years_months_left)

        # Parse money values
        def parse_money(x):
            x = re.sub(r"[^0-9.]", "", str(x)) if pd.notna(x) else ""
            return float(x) if x else np.nan

        # Load PQP params
        with open(params_path, "r") as f:
            params = yaml.safe_load(f)

        default_cat = params["pqp"].get("default_cat", "A")
        PQP10 = float(params["pqp"]["categories"][default_cat]["ten_year"])
        PQP5 = float(params["pqp"]["categories"][default_cat]["five_year"])

        # Calculate values
        df["ARF_val"] = df["arf"].apply(parse_money)
        df["dereg_val_at_10y"] = (df["ARF_val"] * 0.5).round(0)
        df["pqp_est_10y"] = PQP10
        df["pqp_est_5y"] = PQP5
        df["extend_net_value_10y"] = df["dereg_val_at_10y"] - df["pqp_est_10y"]
        df["extend_net_value_5y"] = df["dereg_val_at_10y"] - df["pqp_est_5y"]

        # Parse price and calculate cost_minus_dereg
        df["price_numeric"] = df["price"].apply(parse_money)
        df['cost_minus_dereg'] = df['price_numeric'] - df['dereg_val_at_10y']

        # Monthly consumption worth
        def months_left_string_to_int(x):
            if x == "Expired":
                return np.nan
            try:
                parts = x.split()
                return int(parts[0]) * 12 + int(parts[2])
            except Exception:
                return np.nan

        months_left = df['years_months_left'].apply(months_left_string_to_int)
        df['monthly_consumption_worth'] = df['cost_minus_dereg'] / months_left

        # Sort and remove duplicates
        df = df.sort_values('extend_net_value_10y', ascending=False).reset_index(drop=True)
        df = df.drop_duplicates().reset_index(drop=True)

        # Save processed file
        processed_csv_path = csv_path.replace(".csv", "_processed.csv")
        df.to_csv(processed_csv_path, index=False)

        print(f"✅ Processed data saved: {processed_csv_path}")
        print(f"📊 Final rows (after deduplication): {len(df)}")

        return df

    # Process the data
    try:
        df_processed = process_carlist_data()

        end_time = datetime.now()
        duration = end_time - start_time

        print("\n" + "="*80)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"⏱️  End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration}")
        print(f"📊 Total rows collected: {len(df_processed):,}")
        print(f"📋 Unique models: {df_processed['carmodel'].nunique():,}")
        print("="*80)

    except Exception as e:
        print(f"\n⚠️  Processing error: {e}")
        print("   Raw data has been saved, processing can be done separately.")

if __name__ == "__main__":
    main()
