#!/usr/bin/env python3
"""
Full Web Scraper - Collect 10,000+ Singapore Used Car Listings
Target: 250 pages × ~40 listings/page = ~10,000 rows
Estimated time: 2-3 hours
"""

import subprocess
import sys
import os
from datetime import datetime

def run_full_scraper():
    """Run full scraper for 10K+ listings"""

    url = "https://www.sgcarmart.com/used_cars/listing.php"
    max_pages = 250  # Target: ~10,000 listings

    print("="*80)
    print("🚀 FULL SCRAPING RUN - Singapore Used Car Data Collection")
    print("="*80)
    print(f"\n📊 Configuration:")
    print(f"   URL: {url}")
    print(f"   Pages: {max_pages}")
    print(f"   Expected Listings: ~{max_pages * 40:,}")
    print(f"   Estimated Time: {max_pages * 3 // 60} hours {max_pages * 3 % 60} minutes")
    print(f"   Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)
    print("⚠️  This will take 2-3 hours. The process will run continuously.")
    print("   Progress will be saved incrementally to CSV.")
    print("   You can check progress anytime with: ./check_progress.sh")
    print("="*80)
    print()

    # Create input string
    inputs = f"{url}\n{max_pages}\n"

    # Log start
    log_file = f"scraping_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"📝 Logging output to: {log_file}\n")

    try:
        # Run main.py with inputs
        with open(log_file, 'w') as log:
            log.write(f"Full Scraping Run Started: {datetime.now()}\n")
            log.write(f"Target: {max_pages} pages\n")
            log.write(f"Expected: ~{max_pages * 40} listings\n")
            log.write("="*80 + "\n\n")

            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Send inputs and stream output
            print("🔄 Scraping in progress...")
            print("   (Press Ctrl+C to stop)\n")

            for line in process.communicate(input=inputs)[0].splitlines():
                print(line)
                log.write(line + "\n")

        if process.returncode == 0:
            print("\n" + "="*80)
            print("✅ FULL SCRAPING COMPLETED SUCCESSFULLY!")
            print("="*80)

            # Check output
            data_folder = os.path.join(os.getcwd(), "data")
            if os.path.exists(data_folder):
                csv_files = [f for f in os.listdir(data_folder)
                            if f.startswith("carlist_") and f.endswith(".csv")]
                if csv_files:
                    latest = sorted(csv_files)[-1]
                    print(f"\n📁 Output file: data/{latest}")

                    # Quick stats
                    import pandas as pd
                    df = pd.read_csv(os.path.join(data_folder, latest))
                    print(f"📊 Total rows collected: {len(df):,}")
                    print(f"📋 Unique car models: {df['carmodel'].nunique():,}")

                    # Check for processed file
                    processed = latest.replace(".csv", "_processed.csv")
                    if os.path.exists(os.path.join(data_folder, processed)):
                        df_proc = pd.read_csv(os.path.join(data_folder, processed))
                        print(f"✨ Processed file: data/{processed}")
                        print(f"   Rows after deduplication: {len(df_proc):,}")

            print("\n" + "="*80)
            print("🎉 Data collection complete!")
            print(f"⏱️  End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
        else:
            print(f"\n⚠️  Process exited with code: {process.returncode}")
            print(f"Check log file: {log_file}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        print(f"📁 Partial data may be available in data/ folder")
        process.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Check log file: {log_file}")

if __name__ == "__main__":
    print()
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "FULL DATA COLLECTION RUN" + " "*34 + "║")
    print("║" + " "*15 + "Singapore Used Car Market Dataset" + " "*29 + "║")
    print("║" + " "*20 + "Target: 10,000+ Listings" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    print()

    print("⚠️  WARNING: This will take 2-3 hours to complete.")
    print("   Make sure your computer won't sleep during this time.")
    print()

    confirm = input("Start full scraping run? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        run_full_scraper()
    else:
        print("\n❌ Scraping cancelled by user")
        print("   To run later, use: python3 full_scraper.py")
