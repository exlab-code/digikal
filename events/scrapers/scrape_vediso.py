#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vediso Event Scraper

Scrapes events from vediso (Verband für digitale Sozialwirtschaft) —
Germany's association for digital transformation in the social and health sector.

Source: https://vediso.de/event?date=scheduled
Method: HTML scraping (Odoo CMS), paginated card grid
Selectors: .col-md-6.col-lg-4 cards, h5.card-title for title, .o_wevent_event for detail

Usage:
    python events/scrapers/scrape_vediso.py [--no-directus] [--verbose] [--max-pages 10]
"""

import sys
import os
import json
import logging
import re
import argparse
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.directus_client import DirectusClient, calculate_content_hash

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_NAME = "vediso"
BASE_URL = "https://vediso.de/event?date=scheduled"
PAGE_URL = "https://vediso.de/event/page/{page}?date=scheduled&search=&tags=&type=all&country=all"
COLLECTION = "scraped_data"

GERMAN_MONTHS = {
    "januar": "01", "februar": "02", "märz": "03", "april": "04",
    "mai": "05", "juni": "06", "juli": "07", "august": "08",
    "september": "09", "oktober": "10", "november": "11", "dezember": "12",
}

NOISE_LINES = {
    "alle veranstaltungen", "europe/berlin", "zum kalender hinzufügen",
    "anmeldungen geschlossen", "jetzt anmelden", "ausgebucht",
}


def fetch_page(page: int = 1) -> str:
    url = BASE_URL if page == 1 else PAGE_URL.format(page=page)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_german_date(text: str) -> str:
    """Convert '5. Mai 2026' → '05.05.2026'."""
    text = text.strip()
    m = re.match(r'(\d{1,2})\.\s*([A-Za-zäöü]+)\s+(\d{4})', text)
    if m:
        day = m.group(1).zfill(2)
        month = GERMAN_MONTHS.get(m.group(2).lower(), "00")
        year = m.group(3)
        return f"{day}.{month}.{year}"
    return text


def fetch_detail(url: str) -> str:
    """Fetch detail page and extract description text.

    vediso uses Odoo CMS; detail URLs redirect to /register variant.
    Description lives in .o_wevent_event — filter out navigation noise.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all(["script", "style", "nav"]):
            tag.decompose()

        main = soup.select_one(".o_wevent_event")
        if not main:
            body = soup.find("body")
            raw = body.get_text(separator="\n", strip=True) if body else ""
        else:
            raw = main.get_text(separator="\n", strip=True)

        lines = []
        for line in raw.split("\n"):
            line = line.strip()
            if len(line) > 40 and line.lower() not in NOISE_LINES:
                lines.append(line)

        return "\n".join(lines[:20])
    except Exception as e:
        logger.warning(f"Failed to fetch detail {url}: {e}")
        return ""


def parse_listing_page(html: str) -> list[dict]:
    """Parse a vediso listing page into event dicts.

    Card structure (.col-md-6.col-lg-4):
      - a[href] → /event/{slug}/register
      - h5.card-title → title
      - span (in date div, first) → '5. Mai 2026'
      - address → location (or 'Online event')
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for card in soup.select(".col-md-6.col-lg-4"):
        link = card.find("a", href=True)
        if not link:
            continue

        href = link["href"]
        if "/event/" not in href:
            continue

        # Canonical URL: strip /register suffix for deduplication
        event_url = urljoin("https://vediso.de", href.rstrip("/"))
        if event_url.endswith("/register"):
            event_url = event_url[: -len("/register")]

        title_el = card.select_one("h5.card-title")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)

        # Date: anonymous div after h5.card-title contains '5. Mai 2026' span
        date_raw = ""
        if title_el:
            date_div = title_el.find_next_sibling("div")
            if date_div:
                date_span = date_div.find("span")
                if date_span:
                    date_raw = date_span.get_text(strip=True)

        # Fallback: any span matching 'DD. Month YYYY' format
        if not date_raw:
            for span in card.find_all("span"):
                txt = span.get_text(strip=True)
                if re.match(r'\d{1,2}\.\s+[A-Za-zäöü]+\s+\d{4}', txt):
                    date_raw = txt
                    break

        date_parsed = parse_german_date(date_raw) if date_raw else ""

        # Location
        address = card.select_one("address")
        location = address.get_text(strip=True) if address else ""

        events.append({
            "url": event_url,
            "source_name": SOURCE_NAME,
            "title": title,
            "start_date": date_parsed,
            "end_date": date_parsed,
            "location": location,
            "organizer": "vediso",
            "listing_text": f"{title}\n{date_parsed}\n{location}\nvediso",
            "detail_text": "",
        })

    return events


def scrape_all(max_pages: int = 10) -> list[dict]:
    all_events = []
    seen_urls: set[str] = set()

    for page in range(1, max_pages + 1):
        logger.info(f"Fetching page {page}...")
        try:
            html = fetch_page(page)
        except Exception as e:
            logger.error(f"Failed to fetch page {page}: {e}")
            break

        events = parse_listing_page(html)
        if not events:
            logger.info(f"No events on page {page}, stopping")
            break

        for event in events:
            if event["url"] in seen_urls:
                continue
            seen_urls.add(event["url"])

            logger.debug(f"Fetching detail: {event['title']}")
            event["detail_text"] = fetch_detail(event["url"])
            event["listing_text"] += "\n" + event["detail_text"]

            all_events.append(event)

        logger.info(f"Page {page}: {len(events)} events (total: {len(all_events)})")

    logger.info(f"Total events scraped: {len(all_events)}")
    return all_events


def save_to_directus(events: list[dict], client: DirectusClient) -> tuple[int, int]:
    saved, skipped = 0, 0

    for event in events:
        existing = client.get_item_by_url(COLLECTION, event["url"])
        if existing:
            logger.debug(f"Skipping duplicate: {event['title']}")
            skipped += 1
            continue

        content_hash = calculate_content_hash(event["listing_text"])
        directus_data = {
            "url": event["url"],
            "source_name": SOURCE_NAME,
            "content_hash": content_hash,
            "raw_content": json.dumps(event, ensure_ascii=False),
            "scraped_at": datetime.now().isoformat(),
            "processed": False,
            "processing_status": "pending",
        }

        try:
            client.create_item(COLLECTION, directus_data)
            saved += 1
            logger.info(f"Saved: {event['title']}")
        except Exception as e:
            logger.error(f"Failed to save '{event['title']}': {e}")

    return saved, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape vediso events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages to fetch")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_vediso.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting vediso scraper")
    events = scrape_all(max_pages=args.max_pages)

    if args.no_directus:
        print(json.dumps(events, ensure_ascii=False, indent=2))
        return

    client = DirectusClient(
        base_url=os.environ["DIRECTUS_API_URL"],
        token=os.environ.get("DIRECTUS_API_TOKEN"),
    )
    saved, skipped = save_to_directus(events, client)
    logger.info(f"Done — saved: {saved}, skipped: {skipped}")


if __name__ == "__main__":
    main()
