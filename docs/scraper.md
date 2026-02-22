# Event Scraper Setup and Usage Guide

This guide explains how to set up and use the Event Scraper for Non-Profit Digitalization Events.

## Quick Start (Easiest Method)

### On macOS/Linux:

Simply run:
```bash
./run-scraper.sh
```

This script will:
1. Check if a virtual environment exists, and create one if needed
2. Activate the virtual environment
3. Run the scraper
4. Deactivate the virtual environment when done

You can pass command line arguments to the scraper:
```bash
./run-scraper.sh --verbose --max-events 5
```

### On Windows:

Simply run:
```
run-scraper.bat
```

This script will:
1. Check if a virtual environment exists, and create one if needed
2. Activate the virtual environment
3. Run the scraper
4. Deactivate the virtual environment when done

You can pass command line arguments to the scraper:
```
run-scraper.bat --verbose --max-events 5
```

## Alternative Setup Method

### On macOS/Linux:

1. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./setup.sh
   ```

2. The script will automatically activate the virtual environment for the current session.

3. Run the scraper:
   ```bash
   python event_scraper.py
   ```

### On Windows:

1. Run the setup script to create a virtual environment and install dependencies:
   ```
   setup.bat
   ```

2. The script will automatically activate the virtual environment for the current session.

3. Run the scraper:
   ```
   python event_scraper.py
   ```

## Manual Setup (if the setup scripts don't work)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate.bat`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the scraper:
   ```bash
   python event_scraper.py
   ```

## Configuration

The scraper uses two configuration files:

1. `config/sources.json` - Contains the sources to scrape
2. `config/directus.json` - Contains Directus API configuration

These files will be created automatically with default values if they don't exist.

You can also set environment variables in a `.env` file:
```
DIRECTUS_API_URL=https://your-directus-api-url
DIRECTUS_API_TOKEN=your-api-token-here
DIRECTUS_COLLECTION=scraped_data
```

## Event Sources

The scraper is configured to collect events from the following sources (defined in `config/sources.json`):

### Original Sources

| Source | URL | Focus |
|--------|-----|-------|
| Stifter-helfen.de | hausdesstiftens.org | Non-profit webinars and training |
| Deutsche Stiftung für Engagement und Ehrenamt | deutsche-stiftung-engagement-und-ehrenamt.de | Civic engagement events |
| Aktion Zivilcourage Weiterbildungsforum | eveeno.com | Volunteer training courses |
| Smart Services BW | smart-service-bw.de | Digital transformation events |
| Bitkom Akademie | bitkom-akademie.de | Tech seminars (paginated, up to 20 pages) |
| Open Transfer | opentransfer.de | Community sector events |
| Skala Campus | skala-campus.org | Non-profit capacity building (paginated, up to 10 pages) |
| Fraunhofer IAO | iao.fraunhofer.de | Innovation and digitalization |

### Added February 2026

| Source | URL | Focus | CSS Selector |
|--------|-----|-------|--------------|
| Stiftung Datenschutz | stiftungdatenschutz.org/ehrenamt/webinare | DSGVO/data protection webinars for Vereine | `.die-news-list-more-items` |
| Wegweiser Bürgergesellschaft | buergergesellschaft.de/.../veranstaltungskalender | Aggregated civil society event calendar (Stiftung Mitarbeit) | `.tx_wwbgeventdatabase .row` |
| Paritätischer Wohlfahrtsverband | der-paritaetische.de/veranstaltungen/ | Welfare association, social sector digitalization (TYPO3/sf_event_mgt) | `.liste-artikel-element` |
| Initiative D21 | initiatived21.de/veranstaltungen | Digital society partnership, #D21talk series | `.grid__item` |
| Deutscher Fundraising Verband | dfrv.de/veranstaltungen/ | Digital fundraising workshops, training, annual congress | `.events-table tbody tr` |

### Investigated but Not Added (Require JavaScript Rendering)

The following sources were researched but cannot be scraped with the current BeautifulSoup-based static HTML scraper. They would require adding Playwright or Selenium support:

| Source | URL | Reason | Notes |
|--------|-----|--------|-------|
| D3 — so geht digital | so-geht-digital.de/events/ | WordPress + Elementor, JS-rendered | Events RSS feed exists at `/events/feed/` but is empty. Main RSS at `/feed/` contains blog posts only. No WP REST API for events. |
| CorrelAid | correlaid.org/en/events | SvelteKit, client-side rendered | Event data is embedded as JSON inside a `<script>` tag in the page source. Could be extracted with a custom parser. |
| betterplace academy | betterplace-academy.org | LearnWorlds platform, webinar-termine returns 404 | Alternative via Eventbrite organizer page (React-rendered). Eventbrite API could be used as alternative. |
| Civic Coding | civic-coding.de/angebote/veranstaltungen | Government site returns empty response to curl | AI-for-common-good events (BMAS/BMFSFJ/BMUV initiative). May require specific headers or JS rendering. |

### Other Potential Sources for Future Addition

These sources were identified during research and could be added if their HTML structure is verified:

- **Deutsche Stiftungsakademie** (stiftungsakademie.de/veranstaltungen) — Foundation management courses, paginated card layout
- **Bundesverband Deutscher Stiftungen** (stiftungen.org/aktuelles/terminkalender.html) — Foundation sector calendar, annual Stiftungstag
- **HIIG** (hiig.de/en/events/) — Monthly "Digitaler Salon", WordPress Events Manager (may support ICS export)
- **Weizenbaum-Institut** (weizenbaum-institut.de/en/events/) — Annual conference on AI and society
- **Akademie für Ehrenamtlichkeit** (ehrenamt.de/Seminare/502_...) — Volunteer coordination seminars (plain text format, no structured cards)
- **AlgorithmWatch** (algorithmwatch.org/en/events/) — AI ethics, algorithmic accountability
- **Digitaltag** (digitaltag.eu/veranstaltungen) — Annual action day in June with hundreds of events
- **ZiviZ** (ziviz.de/veranstaltungen) — Civil society research events
- **Körber-Stiftung** (koerber-stiftung.de/en/events/) — "Eingeloggt!" digital literacy week
- **Bits & Bäume** (bits-und-baeume.org) — Sustainable digitalization conferences

### Adding a New Source

Each source in `config/sources.json` requires:

```json
{
  "name": "Source Display Name",
  "url": "https://example.com/events/",
  "type": "html",
  "event_selector": ".css-selector-for-event-items",
  "link_selector": "a",
  "full_page_selector": ".css-selector-for-detail-page-content"
}
```

- **event_selector**: CSS selector that matches each individual event listing on the overview page
- **link_selector**: CSS selector (relative to the event element) to find the link to the detail page
- **full_page_selector**: CSS selector for the main content area on the event detail page

Optional pagination for sources with multiple pages:
```json
{
  "pagination": {
    "type": "url-param",
    "param_name": "page",
    "start_index": 0,
    "max_pages": 20
  }
}
```

To verify selectors for a new source, inspect the page HTML and test that:
1. `document.querySelectorAll(event_selector)` returns the expected event elements
2. Each event element contains a link matching `link_selector`
3. The detail page has content matching `full_page_selector`

## Command Line Options

```
python event_scraper.py --help
```

Available options:
- `--config`, `-c`: Path to configuration file (default: config/sources.json)
- `--directus-config`, `-d`: Path to Directus configuration file (default: config/directus.json)
- `--output`, `-o`: Output directory for scraped data (default: data)
- `--max-events`, `-m`: Maximum events to scrape per source (-1 for all)
- `--verbose`, `-v`: Enable verbose logging
- `--no-directus`: Disable Directus database integration
- `--save-html`: Save HTML files to disk
- `--cache-dir`: Directory to store cache files (default: .cache)
- `--clear-cache`: Clear URL cache before running

## Next Time You Run the Scraper

Once the setup is complete, you only need to:

1. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate.bat`

2. Run the scraper:
   ```bash
   python event_scraper.py
   ```

## Troubleshooting

If you encounter any issues:

1. Make sure Python 3 is installed and in your PATH
2. Check that you have activated the virtual environment
3. Try running the setup script again
4. Check the logs in the `logs` directory
