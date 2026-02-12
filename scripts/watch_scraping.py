#!/usr/bin/env python3
"""
Dynamic Real-Time Progress Monitor for Web Scraping
Updates every 5 seconds with live statistics
"""

import os
import pandas as pd
import time
import sys
from datetime import datetime, timedelta

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def get_scraping_stats():
    """Get current scraping statistics"""
    csv_path = "../webscrap_sgcarmart/data/carlist_20260128.csv"

    if not os.path.exists(csv_path):
        return None

    try:
        df = pd.read_csv(csv_path)
        file_size = os.path.getsize(csv_path) / 1024  # KB

        stats = {
            'rows': len(df),
            'unique_models': df['carmodel'].nunique(),
            'unique_dealers': df['dealer'].nunique() if 'dealer' in df.columns else 0,
            'file_size_kb': file_size,
            'timestamp': datetime.now()
        }

        return stats
    except Exception as e:
        return None

def format_time(seconds):
    """Format seconds to readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds//60)}m {int(seconds%60)}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"

def create_progress_bar(percentage, length=50):
    """Create visual progress bar"""
    filled = int(percentage * length / 100)
    empty = length - filled
    bar = '█' * filled + '░' * empty
    return bar

def main():
    """Main monitoring loop"""

    print("\n🚀 Starting Real-Time Scraping Monitor...\n")
    time.sleep(2)

    target_rows = 10000
    start_time = datetime.now()
    last_row_count = 0
    last_check_time = start_time
    collection_rate_history = []

    try:
        iteration = 0
        while True:
            iteration += 1
            clear_screen()

            # Header
            print("╔" + "="*78 + "╗")
            print("║" + " "*20 + "🔄 LIVE SCRAPING MONITOR" + " "*34 + "║")
            print("║" + " "*15 + "Singapore Used Car Data Collection" + " "*28 + "║")
            print("╚" + "="*78 + "╝")
            print()

            # Get current stats
            stats = get_scraping_stats()

            if stats is None:
                print("⏳ Waiting for scraper to start...")
                print("   (Data file not found yet)")
                time.sleep(5)
                continue

            # Calculate metrics
            current_rows = stats['rows']
            progress = (current_rows / target_rows) * 100
            elapsed = (datetime.now() - start_time).total_seconds()

            # Calculate collection rate
            time_since_last = (datetime.now() - last_check_time).total_seconds()
            if time_since_last > 0:
                current_rate = (current_rows - last_row_count) / time_since_last * 60  # rows/min
                collection_rate_history.append(current_rate)
                if len(collection_rate_history) > 10:
                    collection_rate_history.pop(0)
                avg_rate = sum(collection_rate_history) / len(collection_rate_history)
            else:
                avg_rate = 0

            last_row_count = current_rows
            last_check_time = datetime.now()

            # Estimate time remaining
            if avg_rate > 0:
                remaining_rows = target_rows - current_rows
                remaining_seconds = (remaining_rows / avg_rate) * 60
                eta_time = datetime.now() + timedelta(seconds=remaining_seconds)
            else:
                remaining_seconds = 0
                eta_time = None

            # Display stats
            print("📊 CURRENT STATUS")
            print("━" * 80)
            print(f"   Status:        {'🟢 ACTIVE' if iteration % 2 == 0 else '🟢 ACTIVE '}")
            print(f"   Rows:          {current_rows:,} / {target_rows:,}")
            print(f"   Progress:      {progress:.1f}%")
            print(f"   File Size:     {stats['file_size_kb']:.1f} KB")
            print()

            # Progress bar
            bar = create_progress_bar(progress, 60)
            print(f"   [{bar}] {progress:.1f}%")
            print()

            # Performance metrics
            print("⚡ PERFORMANCE")
            print("━" * 80)
            print(f"   Collection Rate:  {avg_rate:.1f} rows/min")
            print(f"   Time Elapsed:     {format_time(elapsed)}")
            if eta_time:
                print(f"   Time Remaining:   {format_time(remaining_seconds)}")
                print(f"   Est. Completion:  {eta_time.strftime('%I:%M %p')}")
            print()

            # Data quality
            print("📈 DATA QUALITY")
            print("━" * 80)
            print(f"   Unique Models:    {stats['unique_models']:,}")
            print(f"   Unique Dealers:   {stats['unique_dealers']:,}")
            print(f"   Avg Models/Row:   {stats['unique_models']/max(current_rows,1):.2f}")
            print()

            # Milestones
            print("🎯 MILESTONES")
            print("━" * 80)
            milestones = [
                (1000, "1K"),
                (2500, "2.5K"),
                (5000, "5K"),
                (7500, "7.5K"),
                (10000, "10K")
            ]

            for milestone, label in milestones:
                if current_rows >= milestone:
                    status = "✅"
                elif current_rows >= milestone * 0.9:
                    status = "🔄"
                else:
                    status = "⏳"
                percentage_to_milestone = min(100, (current_rows / milestone) * 100)
                print(f"   {status} {label:>6s}  {percentage_to_milestone:>5.1f}%")
            print()

            # Footer
            print("━" * 80)
            print(f"   Last Updated: {datetime.now().strftime('%I:%M:%S %p')} | Refresh: Every 5s | Press Ctrl+C to exit")
            print("━" * 80)

            # Check if complete
            if current_rows >= target_rows:
                print()
                print("🎉" * 40)
                print()
                print("   ✅ SCRAPING COMPLETE!")
                print(f"   📊 Final Count: {current_rows:,} rows")
                print(f"   ⏱️  Total Time: {format_time(elapsed)}")
                print()
                print("🎉" * 40)
                break

            # Wait before next update
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitor stopped by user")
        print(f"   Last count: {current_rows:,} rows")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
