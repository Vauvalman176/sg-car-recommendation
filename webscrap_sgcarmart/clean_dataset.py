#!/usr/bin/env python3
"""
Clean Dataset - Full data cleaning pipeline
"""

import pandas as pd
import numpy as np

def clean_dataset():
    print("="*60)
    print("CLEANING DATASET")
    print("="*60)

    # Load the filled dataset
    df = pd.read_csv('data/carlist_20260128_filled.csv')
    print(f"Loaded: {len(df)} rows")

    # 1. Remove duplicates by URL
    print("\n1. Removing duplicates...")
    before = len(df)
    df = df.drop_duplicates(subset=['url'], keep='first')
    print(f"   Removed {before - len(df)} duplicates -> {len(df)} rows")

    # 2. Convert N.A. to null
    print("\n2. Converting 'N.A.' to null...")
    na_cols = ['price', 'curb_weight', 'power', 'road_tax', 'coe', 'omv',
               'mileage', 'dereg_value', 'engine_cap']
    for col in na_cols:
        na_count = (df[col] == 'N.A.').sum()
        df[col] = df[col].replace('N.A.', np.nan)
        if na_count > 0:
            print(f"   {col}: {na_count} N.A. -> null")

    # 3. Convert to numeric types
    print("\n3. Converting to numeric types...")
    numeric_cols = ['price', 'curb_weight', 'power', 'road_tax', 'coe', 'omv',
                    'mileage', 'dereg_value', 'engine_cap']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"   {col} -> numeric")

    # 4. Parse reg_date to datetime
    print("\n4. Parsing reg_date to datetime...")
    df['reg_date'] = pd.to_datetime(df['reg_date'], format='mixed', dayfirst=True, errors='coerce')
    null_dates = df['reg_date'].isnull().sum()
    print(f"   Parsed {len(df) - null_dates} dates, {null_dates} null")

    # 5. Trim whitespace in text columns
    print("\n5. Trimming whitespace...")
    text_cols = ['transmission', 'fuel_type', 'type_of_vehicle', 'dealer', 'carmodel']
    for col in text_cols:
        df[col] = df[col].str.strip()
    print(f"   Trimmed {len(text_cols)} text columns")

    # 6. Fix invalid owners=0
    print("\n6. Fixing invalid owners=0...")
    invalid_owners = (df['owners'] == 0).sum()
    df.loc[df['owners'] == 0, 'owners'] = np.nan
    print(f"   Set {invalid_owners} owners=0 to null")

    # 7. Summary stats
    print("\n" + "="*60)
    print("CLEANING COMPLETE")
    print("="*60)
    print(f"Final rows: {len(df)}")
    print(f"\nNull counts:")
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            pct = null_count / len(df) * 100
            print(f"   {col}: {null_count} ({pct:.1f}%)")

    print(f"\nData types:")
    for col in df.columns:
        print(f"   {col}: {df[col].dtype}")

    # Save cleaned dataset
    output_path = 'data/carlist_20260128_cleaned.csv'
    df.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")

    return df

if __name__ == "__main__":
    clean_dataset()
