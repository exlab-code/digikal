# Event Scrapers

Active scrapers run daily via `.github/workflows/update-events.yml`.

## Paused

### `scrape_socialnet.py` — socialnet Kalender

Paused 2026-04-13. The socialnet calendar is broad (social/health sector) and
yields only a handful of digitalization-relevant events per cycle, while
detail pages mostly link out to the organizer ("Infos beim Veranstalter")
rather than carrying real content. Not worth the noise vs. signal.

To re-enable: uncomment the line in `.github/workflows/update-events.yml`.
The scraper itself is left in place and still runnable manually:

```bash
python events/scrapers/scrape_socialnet.py --no-directus
```
