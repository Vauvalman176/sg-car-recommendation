#!/bin/bash
# Monitor full scraping progress

echo "========================================================================"
echo "📊 FULL SCRAPING PROGRESS MONITOR"
echo "========================================================================"
echo

# Check if scraper is running
if pgrep -f "full_scraper.py\|main.py" > /dev/null; then
    echo "✅ Status: SCRAPER IS RUNNING"
    echo

    # Show process info
    echo "🔍 Process Details:"
    ps aux | grep -E "full_scraper|main.py" | grep -v grep | head -2
    echo
else
    echo "⏸️  Status: SCRAPER IS NOT RUNNING"
    echo
fi

# Check latest CSV file
echo "📁 Latest Data File:"
if [ -f "data/carlist_$(date +%Y%m%d).csv" ]; then
    latest_file="data/carlist_$(date +%Y%m%d).csv"
    file_size=$(ls -lh "$latest_file" | awk '{print $5}')
    row_count=$(wc -l < "$latest_file")
    echo "   File: $latest_file"
    echo "   Size: $file_size"
    echo "   Rows: $((row_count - 1)) (excluding header)"
    echo

    # Calculate progress
    target_rows=10000
    current_rows=$((row_count - 1))
    progress=$((current_rows * 100 / target_rows))
    echo "📈 Progress: $current_rows / $target_rows rows ($progress%)"

    # Progress bar
    bar_length=50
    filled=$((progress * bar_length / 100))
    empty=$((bar_length - filled))
    printf "   ["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] $progress%%\n"
    echo

    # Estimated time remaining
    if [ $current_rows -gt 0 ]; then
        # Rough estimate: 1.5 seconds per listing
        remaining_rows=$((target_rows - current_rows))
        remaining_seconds=$((remaining_rows * 2))
        remaining_hours=$((remaining_seconds / 3600))
        remaining_mins=$(((remaining_seconds % 3600) / 60))
        echo "⏱️  Estimated Time Remaining: ${remaining_hours}h ${remaining_mins}m"
    fi
else
    echo "   No data file found yet (scraper may be initializing...)"
fi

echo
echo "========================================================================"
echo "📝 Log Files:"
ls -lht scraping_log_*.txt 2>/dev/null | head -3 || echo "   No log files yet"
echo
echo "========================================================================"
echo "Commands:"
echo "  • Monitor live: tail -f scraping_log_*.txt"
echo "  • Check again: ./monitor_scraping.sh"
echo "  • Stop scraping: pkill -f main.py"
echo "========================================================================"
