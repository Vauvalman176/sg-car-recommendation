#!/usr/bin/env python3
"""Validate scraped data quality"""
import pandas as pd
import re

df = pd.read_csv('data/carlist_20260128.csv')

print('='*70)
print('📊 DATA COLLECTION SUMMARY')
print('='*70)
print(f'✅ Total Rows Collected: {len(df)}')
print(f'📋 Total Columns: {len(df.columns)}')
print()
print('📋 Column List:')
for i, col in enumerate(df.columns, 1):
    print(f'   {i:2d}. {col}')
print()
print('='*70)
print('🔍 SAMPLE DATA (First 5 Rows)')
print('='*70)
print(df.head()[['price', 'carmodel', 'mileage', 'coe', 'reg_date']].to_string())
print()
print('='*70)
print('📈 DATA QUALITY CHECKS')
print('='*70)
print(f'\nMissing Values:')
for col in df.columns:
    missing = df[col].isna().sum()
    if missing > 0 or df[col].astype(str).str.strip().eq('N.A.').sum() > 0:
        na_count = df[col].astype(str).str.strip().eq('N.A.').sum()
        total_missing = missing + na_count
        print(f'   {col}: {total_missing} ({total_missing/len(df)*100:.1f}%)')

if df['carmodel'].isna().sum() == 0:
    print('\n✅ No missing car models')

print(f'\n📊 Unique Values:')
print(f'   Car Models: {df["carmodel"].nunique()}')
print(f'   Dealers: {df["dealer"].nunique()}')
print(f'   Fuel Types: {df["fuel_type"].nunique()}')

print(f'\n💰 Price Analysis:')
# Clean price data
def clean_price(price_str):
    cleaned = re.sub(r'[^0-9.]', '', str(price_str))
    return float(cleaned) if cleaned else None

prices_numeric = df['price'].apply(clean_price).dropna()
print(f'   Valid Prices: {len(prices_numeric)}/{len(df)} ({len(prices_numeric)/len(df)*100:.1f}%)')
print(f'   Min: ${prices_numeric.min():,.0f}')
print(f'   Max: ${prices_numeric.max():,.0f}')
print(f'   Median: ${prices_numeric.median():,.0f}')
print(f'   Mean: ${prices_numeric.mean():,.0f}')

print(f'\n🚗 Mileage Analysis:')
mileage_numeric = pd.to_numeric(df['mileage'], errors='coerce').dropna()
print(f'   Valid Mileage: {len(mileage_numeric)}/{len(df)} ({len(mileage_numeric)/len(df)*100:.1f}%)')
print(f'   Min: {mileage_numeric.min():,.0f} km')
print(f'   Max: {mileage_numeric.max():,.0f} km')
print(f'   Median: {mileage_numeric.median():,.0f} km')

print(f'\n📅 Registration Date Analysis:')
print(f'   Sample dates: {df["reg_date"].head(3).tolist()}')

print('\n' + '='*70)
print('✅ DATA VALIDATION COMPLETE')
print('='*70)
print('\n⚠️  Note: Post-processing step failed (price format issue)')
print('   This will be fixed in the data cleaning module.')
print('='*70)
