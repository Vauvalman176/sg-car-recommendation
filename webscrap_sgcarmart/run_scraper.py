#!/usr/bin/env python3
"""
Automated Web Scraper Runner
Runs the SGCarMart scraper with pre-configured inputs
"""

import subprocess
import sys

def run_scraper(url, max_pages):
    """
    Run the main.py scraper with automated inputs

    Args:
        url: SGCarMart listing URL
        max_pages: Number of pages to scrape
    """
    print("="*70)
    print("🚀 Starting SGCarMart Web Scraper")
    print("="*70)
    print(f"📍 URL: {url}")
    print(f"📊 Max Pages: {max_pages}")
    print(f"📈 Expected Listings: ~{max_pages * 40}")
    print("="*70)
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

        # Send inputs and stream output
        for line in process.communicate(input=inputs)[0].splitlines():
            print(line)

        if process.returncode == 0:
            print("\n" + "="*70)
            print("✅ Scraping completed successfully!")
            print("="*70)
        else:
            print("\n" + "="*70)
            print(f"⚠️  Process exited with code: {process.returncode}")
            print("="*70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        process.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Configuration
    SCRAPE_URL = "https://www.sgcarmart.com/used_cars/listing.php"
    MAX_PAGES = 250  # ~10,000 listings (250 pages × 40 listings/page)

    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " "*10 + "Singapore Used Car Data Collection" + " "*23 + "║")
    print("║" + " "*15 + "Academic Research Project" + " "*27 + "║")
    print("╚" + "═"*68 + "╝")
    print()

    # Ask user to confirm
    print(f"About to scrape {MAX_PAGES} pages from SGCarMart")
    print(f"Estimated time: {MAX_PAGES * 3 // 60} hours (with 3-second delays)")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        run_scraper(SCRAPE_URL, MAX_PAGES)
    else:
        print("❌ Scraping cancelled by user")
