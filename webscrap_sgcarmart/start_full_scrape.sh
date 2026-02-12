#!/bin/bash
# Start full scraping using the working main.py method

cd ~/Downloads/bigdata_project/webscrap_sgcarmart

echo "================================================================================"
echo "🚀 Starting Full Scraping Run"
echo "================================================================================"
echo "📍 URL: https://www.sgcarmart.com/used_cars/listing.php"
echo "📊 Pages: 250"
echo "📈 Target: ~10,000 listings"
echo "⏱️  Duration: 2-3 hours"
echo "================================================================================"
echo

# Create input file with responses
echo "https://www.sgcarmart.com/used_cars/listing.php" > /tmp/scraper_input.txt
echo "250" >> /tmp/scraper_input.txt

# Start scraping with input redirection
echo "🔄 Starting scraper in background..."
nohup python3 main.py < /tmp/scraper_input.txt > full_scrape.log 2>&1 &

SCRAPER_PID=$!
echo "✅ Scraper started with PID: $SCRAPER_PID"
echo
echo "📝 Monitor progress:"
echo "   tail -f full_scrape.log"
echo
echo "📊 Check data:"
echo "   ./monitor_scraping.sh"
echo
echo "🛑 Stop scraping:"
echo "   kill $SCRAPER_PID"
echo
echo "================================================================================"
