# Event Scraper & Management System

A comprehensive system for collecting, analyzing, moderating, and sharing events relevant to non-profit organizations.

## Overview

This project is a complete event management system that:

1. **Scrapes Events**: Collects event information from various websites
2. **Analyzes with AI**: Uses LLM to extract structured data and determine event relevance
3. **Provides Moderation**: Web interface for reviewing and approving events
4. **Exports Calendar**: Generates a static `.ics` calendar file from approved events
5. **Displays Events**: Website for showcasing approved events

## Documentation

Detailed documentation for each component of the system is available in the `docs` directory:

- [Installation Guide](docs/installation.md) - Complete guide to setting up and using the system
- [Scraper Documentation](docs/scraper.md) - Details on the event scraper component
- [ICS Import Documentation](docs/ics_import.md) - Guide to importing events from ICS calendars
- [Analyzer Documentation](docs/analyzer.md) - Information about the LLM analysis component
- [Moderation Interface](docs/moderation.md) - Guide to the moderation web interface
- [Website Documentation](docs/website.md) - Information about the website component
- [CSS Customization](docs/customization.md) - How to customize the website appearance

## System Requirements

- Python 3.6+
- [Directus](https://directus.io/) instance for data storage
- OpenAI API key for LLM analysis
- Web server for hosting the moderation interface (optional)

## Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Event-Scraper.git
   cd Event-Scraper
   ```

2. **Install dependencies**:
   ```bash
   # Create a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install required packages
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** with your credentials (see `.env.example` for template)

4. **Run the system components**:
   ```bash
   # Event Management System
   python events/event_scraper.py
   python events/ics_import.py
   python events/event_analyzer.py
   python events/generate_ics.py

   # Fördermittel (Funding) System
   python foerdermittel/foerdermittel_scraper.py
   python foerdermittel/foerdermittel_analyzer.py
   python foerdermittel/foerdermittel_importer.py

   # Moderate content using Directus admin interface
   # Access at: https://calapi.buerofalk.de/admin
   ```

## Command Line Arguments

### Master Script (run_system.sh)

The master script provides a convenient way to run all components:

```bash
./run_system.sh {command}
```

Available commands:
- `scrape` - Run the scraper once
- `ics-import` - Run the ICS calendar import
- `analyze` - Run the LLM analysis once
- `generate-ics` - Generate static `calendar.ics` file
- `all` - Run the full pipeline (scrape, import, analyze, generate)

### Scraper (event_scraper.py)

```bash
python event_scraper.py [options]
```

Options:
- `--config`, `-c` - Path to configuration file (default: config/sources.json)
- `--output`, `-o` - Output directory for scraped data (default: data)
- `--max-events`, `-m` - Maximum events to scrape per source (-1 for all)
- `--verbose`, `-v` - Enable verbose logging
- `--no-directus` - Disable Directus database integration
- `--save-html` - Save HTML files to disk
- `--cache-dir` - Directory to store cache files (default: .cache)
- `--clear-cache` - Clear URL cache before running

### LLM Analysis (event_analyzer.py)

```bash
python event_analyzer.py [options]
```

Options:
- `--limit`, `-l` - Maximum number of items to process (default: 10)
- `--batch`, `-b` - Batch size for processing (default: 3)
- `--flag-mismatches`, `-f` - Flag events where LLM determination doesn't match human feedback
- `--only-flag`, `-o` - Only flag mismatches without processing new events
- `--log-file` - Path to log file for LLM extraction results (default: llm_extraction.log)

### Calendar Export (generate_ics.py)

```bash
python events/generate_ics.py [options]
```

Options:
- `-o`, `--output` - Output file path (default: `website/static/calendar.ics`)

### Event Moderation

Event moderation is handled through the Directus admin interface at `https://calapi.buerofalk.de/admin`. The admin interface provides:
- Filtering and sorting events
- Bulk approval/rejection operations
- Custom fields and workflows
- User permission management

## Project Structure

```
digikal/
├── events/                     # Event management system
│   ├── config/                # Event source configurations
│   │   ├── sources.json       # Web scraping sources
│   │   └── ics_sources.json   # ICS calendar sources
│   ├── event_scraper.py       # Main event scraper
│   ├── event_analyzer.py      # LLM-based event analysis
│   ├── ics_import.py          # ICS calendar import
│   └── generate_ics.py        # Static .ics calendar generation
│
├── foerdermittel/             # Funding opportunity system
│   ├── config/                # Funding sources config
│   ├── scrape_dsee.py         # DSEE funding scraper
│   └── mcp_server.py          # MCP server for funding data
│
├── shared/                    # Shared utilities
│   └── directus_client.py     # Directus API client
│
├── website/                   # Public event website (GitHub Pages)
│   ├── src/                   # SvelteKit components
│   └── static/                # Static assets (incl. calendar.ics)
│
├── newsletter/                # Newsletter generation
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
└── run_system.sh             # Master control script
```

## License

[MIT License](LICENSE)
