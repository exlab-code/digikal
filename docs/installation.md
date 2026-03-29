# Quick Start Guide: Non-Profit Event Scraper & Management System

This guide provides a quick overview of how to set up and use the complete Non-Profit Event Scraper and Management System.

## What This Project Does

This project is a comprehensive system for collecting, analyzing, moderating, and sharing events relevant to non-profit organizations:

1. **Scraper**: Collects event information from various websites
2. **LLM Analysis**: Uses AI to extract structured data and determine event relevance
3. **Moderation Interface**: Web interface for reviewing and approving events
4. **Calendar Export**: Generates a static `.ics` calendar file from approved events

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

3. **Create a `.env` file** with your credentials:
   ```
   # Directus Configuration
   DIRECTUS_API_URL=https://your-directus-api-url
   DIRECTUS_API_TOKEN=your-api-token-here

   # OpenAI API Configuration
   OPENAI_API_KEY=your-openai-api-key
   ```

## Complete Workflow

### 1. Scraping Events

The scraper collects event information from configured websites:

```bash
python event_scraper.py
```

- Events are scraped based on configurations in the `config/` directory
- Each source has its own configuration file (e.g., `config/bitkom_akademie_config.json`)
- Scraped events are saved to the Directus database

To add a new source:
1. Create a new configuration file in the `config/` directory
2. Add the source to `events/config/sources.json`
3. Run the scraper

### 2. LLM Analysis

After scraping, you can run the LLM analysis to enhance event data:

```bash
python event_analyzer.py
```

This script:
- Processes events that haven't been analyzed yet
- Uses OpenAI's API to extract structured data
- Determines event relevance for non-profit organizations
- Updates events in the Directus database with enhanced information

### 3. Event Moderation

The moderation interface allows you to review and approve events. It runs on the server and is accessible through a web browser.

In the moderation interface, you can:
- View all scraped events
- Edit event details
- Approve or reject events
- Filter events by source, category, or approval status

### 4. Calendar Export

Generate a static `.ics` calendar file from approved events:

```bash
python events/generate_ics.py
```

The file is written to `website/static/calendar.ics` and served at `https://digikal.org/calendar.ics`.

## Common Use Cases

### Initial Setup

For a fresh installation:

1. Set up your `.env` file with all credentials
2. Run the scraper: `python event_scraper.py`
3. Run the LLM analysis: `python event_analyzer.py`
4. Review and approve events in Directus admin: https://calapi.buerofalk.de/admin
5. Generate calendar: `python events/generate_ics.py`

### Regular Maintenance

For ongoing operation:

1. Schedule the scraper to run daily: `cron job or task scheduler`
2. Schedule the LLM analysis to run after scraping
3. Moderate events regularly through the web interface
4. Generate calendar after approving events: `python events/generate_ics.py`

## Troubleshooting

### Scraper Issues
- Check source configurations in `config/` directory
- Verify Directus API connection
- Look for errors in the console output

### LLM Analysis Issues
- Verify your OpenAI API key is correct
- Check API rate limits
- Look for errors in the console output

### Moderation Interface Issues
- Ensure `config-secrets.js` is properly configured
- Check browser console for JavaScript errors
- Verify Directus API connection

## Additional Resources

- [Directus Documentation](https://docs.directus.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
