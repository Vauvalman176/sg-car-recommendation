#!/usr/bin/env python3
"""
Resume Scraper - Continues from where the previous run left off
Skips URLs that have already been scraped
"""

from tqdm import tqdm
from tools import collect_listing_links, extract_sgcarmart_car_details, get_or_append_carlist_df
import os
import pandas as pd
import time
from datetime import datetime

def get_scraped_urls(data_folder='data'):
    """Get set of URLs that have already been scraped"""
    csv_files = [f for f in os.listdir(data_folder) if f.startswith("carlist_") and f.endswith(".csv")]
    if not csv_files:
        return set()

    csv_files_sorted = sorted(
        csv_files,
        key=lambda fn: fn.split("_")[1].replace(".csv", ""),
        reverse=True
    )
    csv_path = os.path.join(data_folder, csv_files_sorted[0])
    df = pd.read_csv(csv_path)

    if 'url' in df.columns:
        return set(df['url'].dropna().tolist())
    return set()

def main():
    main_url = "https://www.sgcarmart.com/used_cars/listing.php"
    max_pages = 250

    start_time = datetime.now()

    # Get already scraped URLs
    scraped_urls = get_scraped_urls()
    print(f"Found {len(scraped_urls)} already scraped listings")

    print("="*80)
    print("RESUME SCRAPING - Singapore Used Car Data")
    print("="*80)
    print(f"URL: {main_url}")
    print(f"Max Pages: {max_pages}")
    print(f"Already scraped: {len(scraped_urls)}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\nCollecting listing links...")

    # Collect all listing links
    all_links = collect_listing_links(main_url, max_pages=max_pages)

    # Filter out already scraped
    remaining_links = [url for url in all_links if url not in scraped_urls]

    print(f"Total listings found: {len(all_links)}")
    print(f"Already scraped: {len(scraped_urls)}")
    print(f"Remaining to scrape: {len(remaining_links)}")
    print(f"Estimated time: {len(remaining_links) * 1.5 / 60:.1f} minutes\n")

    if not remaining_links:
        print("All listings have already been scraped!")
        return

    # Process remaining listings
    for car_url in tqdm(remaining_links, desc="Processing cars", unit="car"):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                details = extract_sgcarmart_car_details(car_url)
                if len(details) == 18:
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
            time.sleep(0.5)
        else:
            print(f"Warning: Could not extract details for {car_url}")
            continue

        get_or_append_carlist_df(details)

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "="*80)
    print("SCRAPING RESUMED AND COMPLETED!")
    print("="*80)
    print(f"Duration: {duration}")
    print(f"New listings scraped: {len(remaining_links)}")
    print("="*80)

if __name__ == "__main__":
    main()
