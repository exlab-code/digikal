#!/bin/bash
# run_system.sh - Master script for managing the Event Scraper system

# Set up environment
cd "$(dirname "$0")"  # Change to the directory of this script
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create logs directory if it doesn't exist
mkdir -p events/logs

# Start components
case "$1" in
    scrape)
        echo "Running scraper..."
        python events/event_scraper.py
        echo "Running individual scrapers..."
        python events/scrapers/scrape_sigu.py
        python events/scrapers/scrape_socialnet.py
        python events/scrapers/scrape_kgst.py
        python events/scrapers/scrape_negz.py
        python events/scrapers/scrape_paritaetische.py
        python events/scrapers/scrape_hiig.py
        ;;
    ics-import)
        echo "Running ICS import..."
        python events/ics_import.py
        ;;
    analyze)
        echo "Running LLM analysis..."
        python events/event_analyzer.py
        ;;
    generate-ics)
        echo "Generating calendar .ics..."
        python events/generate_ics.py
        ;;
    all)
        echo "Running full pipeline..."
        python events/event_scraper.py > events/logs/scraper.log 2>&1
        echo "Scraper done."
        python events/scrapers/scrape_sigu.py > events/logs/scrape_sigu.log 2>&1
        echo "SIGU scraper done."
        python events/scrapers/scrape_socialnet.py > events/logs/scrape_socialnet.log 2>&1
        echo "socialnet scraper done."
        python events/scrapers/scrape_kgst.py > events/logs/scrape_kgst.log 2>&1
        echo "KGSt scraper done."
        python events/scrapers/scrape_negz.py > events/logs/scrape_negz.log 2>&1
        echo "NEGZ scraper done."
        python events/scrapers/scrape_paritaetische.py > events/logs/scrape_paritaetische.log 2>&1
        echo "Paritätische Akademie scraper done."
        python events/scrapers/scrape_hiig.py > events/logs/scrape_hiig.log 2>&1
        echo "HIIG scraper done."
        python events/ics_import.py > events/logs/ics-import.log 2>&1
        echo "ICS import done."
        python events/event_analyzer.py > events/logs/analysis.log 2>&1
        echo "Analysis done."
        python events/generate_ics.py > events/logs/generate-ics.log 2>&1
        echo "Calendar generated."
        echo "All components completed. View logs in the events/logs/ directory."
        ;;
    *)
        echo "Event Scraper System Management Script"
        echo "-------------------------------------"
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  scrape        Run the scraper once"
        echo "  ics-import    Run the ICS calendar import"
        echo "  analyze       Run the LLM analysis once"
        echo "  generate-ics  Generate static calendar.ics file"
        echo "  all           Run the full pipeline (scrape, import, analyze, generate)"
        echo ""
        echo "Examples:"
        echo "  $0 all        # Run the full pipeline"
        echo "  $0 scrape     # Just run the scraper"
        exit 1
        ;;
esac

exit 0
