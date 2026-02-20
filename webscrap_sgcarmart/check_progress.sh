#!/bin/bash
# Monitor scraping progress

echo "=========================================="
echo "📊 Web Scraping Progress Monitor"
echo "=========================================="
echo

# Check if process is running
if pgrep -f "test_scraper.py\|main.py" > /dev/null; then
    echo "✅ Scraper is RUNNING"
else
    echo "⏸️  Scraper is NOT running"
fi

echo
echo "📁 Files in data folder:"
ls -lh data/ 2>/dev/null || echo "   (No data folder yet)"

echo
echo "📝 Recent CSV files:"
find . -name "carlist_*.csv" -type f -exec ls -lh {} \; 2>/dev/null | tail -3 || echo "   (No CSV files yet)"

echo
echo "=========================================="
echo "To monitor live: tail -f /private/tmp/claude/-Users-jai/tasks/b7e0628.output"
echo "=========================================="
