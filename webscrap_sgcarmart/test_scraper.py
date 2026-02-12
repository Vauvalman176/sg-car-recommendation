#!/usr/bin/env python3
"""
Test Web Scraper - Small Sample
Quick test with 10 pages (~400 listings) to verify functionality
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test_scraper():
    """Run a small test scrape"""

    url = "https://www.sgcarmart.com/used_cars/listing.php"
    max_pages = 10  # Small test: ~400 listings

    print("="*70)
    print("🧪 TESTING SGCarMart Web Scraper")
    print("="*70)
    print(f"📍 URL: {url}")
    print(f"📊 Test Pages: {max_pages}")
    print(f"📈 Expected: ~{max_pages * 40} listings")
    print(f"⏱️  Estimated Time: ~{max_pages * 3 // 60 + 1} minutes")
    print("="*70)
    print()
    print("This is a TEST RUN to verify the scraper works correctly.")
    print("After successful test, you can run a full scrape for 10K+ listings.")
    print()

    # Create input string
    inputs = f"{url}\n{max_pages}\n"

    try:
        # Run main.py with inputs
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Send inputs and capture output
        output, _ = process.communicate(input=inputs, timeout=600)  # 10 min timeout

        # Print output
        print(output)

        if process.returncode == 0:
            print("\n" + "="*70)
            print("✅ TEST SCRAPING SUCCESSFUL!")
            print("="*70)

            # Check if data was created
            data_folder = os.path.join(os.getcwd(), "data")
            if os.path.exists(data_folder):
                csv_files = [f for f in os.listdir(data_folder)
                            if f.startswith("carlist_") and f.endswith(".csv")]
                if csv_files:
                    latest = sorted(csv_files)[-1]
                    print(f"\n📁 Output file: data/{latest}")

                    # Quick validation
                    import pandas as pd
                    df = pd.read_csv(os.path.join(data_folder, latest))
                    print(f"📊 Rows collected: {len(df)}")
                    print(f"📋 Columns: {len(df.columns)}")
                    print(f"\n✨ Sample data (first 3 rows):")
                    print(df.head(3)[['price', 'carmodel', 'reg_date']].to_string())

            print("\n" + "="*70)
            print("🎯 NEXT STEPS:")
            print("   1. Check the data quality above")
            print("   2. If looks good, run full scrape with 250 pages")
            print("   3. Use: python3 run_scraper.py")
            print("="*70)
        else:
            print("\n❌ Test failed with exit code:", process.returncode)

    except subprocess.TimeoutExpired:
        print("\n⚠️  Test timed out (took > 10 minutes)")
        process.kill()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        process.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "TEST RUN - Web Scraper" + " "*26 + "║")
    print("║" + " "*15 + "Small Sample (10 pages)" + " "*29 + "║")
    print("╚" + "═"*68 + "╝")
    print()

    run_test_scraper()
