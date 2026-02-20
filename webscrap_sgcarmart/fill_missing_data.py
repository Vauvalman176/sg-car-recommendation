#!/usr/bin/env python3
"""
Fill Missing Data - Re-scrape URLs with N.A. values to get missing info
"""

import pandas as pd
from tqdm import tqdm
from tools import extract_sgcarmart_car_details
import time

def main():
    print("Loading dataset...")
    df = pd.read_csv('data/carlist_20260128.csv')

    # Columns to check for N.A.
    cols_to_check = ['price', 'curb_weight', 'power', 'road_tax', 'coe',
                     'mileage', 'dereg_value', 'engine_cap', 'omv', 'arf']

    # Find rows with any N.A. values
    has_na = df[cols_to_check].apply(lambda x: x == 'N.A.').any(axis=1)
    na_indices = df[has_na].index.tolist()

    print(f"Found {len(na_indices)} rows with N.A. values to re-scrape")
    print("="*60)

    filled_count = 0
    failed_count = 0

    for idx in tqdm(na_indices, desc="Re-scraping", unit="url"):
        url = df.loc[idx, 'url']

        # Get current row's N.A. columns
        na_cols = [col for col in cols_to_check if df.loc[idx, col] == 'N.A.']

        max_retries = 3
        for attempt in range(max_retries):
            try:
                details = extract_sgcarmart_car_details(url)

                # Update only the N.A. fields with new data
                updated = False
                for col in na_cols:
                    if col in details and details[col] and str(details[col]) != 'N.A.' and str(details[col]).strip():
                        df.loc[idx, col] = details[col]
                        updated = True

                if updated:
                    filled_count += 1
                break

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    failed_count += 1

        # Small delay to be nice to the server
        time.sleep(0.3)

    # Save updated dataset
    output_path = 'data/carlist_20260128_filled.csv'
    df.to_csv(output_path, index=False)

    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    print(f"URLs processed: {len(na_indices)}")
    print(f"Rows with data filled: {filled_count}")
    print(f"Failed to scrape: {failed_count}")
    print(f"Saved to: {output_path}")

    # Show remaining N.A. counts
    print("\nRemaining N.A. values:")
    for col in cols_to_check:
        na_count = (df[col] == 'N.A.').sum()
        print(f"  {col}: {na_count}")

if __name__ == "__main__":
    main()
