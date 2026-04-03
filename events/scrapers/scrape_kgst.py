#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KGSt Veranstaltungskalender Scraper

Scrapes events from KGSt (Kommunale Gemeinschaftsstelle für
Verwaltungsmanagement) — the largest municipal association in Germany.

Source: https://www.kgst.de/veranstaltungskalender
Method: HTML scraping, paginated (20/page, ~100 total, Liferay portal)
Selectors: .searchResultBox with pipe-delimited date/location in span.date

Usage:
    python events/scrapers/scrape_kgst.py [--no-directus] [--verbose] [--max-pages 5]
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

SOURCE_NAME = "KGSt"
BASE_URL = "https://www.kgst.de/veranstaltungskalender"
COLLECTION = "scraped_data"
ITEMS_PER_PAGE = 20


def fetch_page(page: int = 1) -> str:
    """Fetch a listing page from the KGSt Veranstaltungskalender.

    Args:
        page: Page number (1-indexed)

    Returns:
        HTML content as string
    """
    params = {"delta": ITEMS_PER_PAGE, "start": page}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_date_location(raw: str) -> tuple[str, str, str, str]:
    """Parse KGSt's pipe-delimited date/location string.

    Example: '08.12.2026 10:00 - 09.12.2026 00:00 | KGSt-Campus.digital | Veranstaltungen | Digital'

    Returns:
        Tuple of (start_date, end_date, start_time, location)
    """
    parts = [p.strip() for p in raw.split("|")]
    date_part = parts[0] if parts else ""
    location = parts[1] if len(parts) > 1 else ""

    start_date, end_date, start_time = "", "", ""

    # Parse date range: 'DD.MM.YYYY HH:MM - DD.MM.YYYY HH:MM'
    m = re.match(
        r'(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2})',
        date_part,
    )
    if m:
        start_date = m.group(1)
        start_time = m.group(2)
        end_date = m.group(3)
    else:
        # Single date
        m = re.match(r'(\d{2}\.\d{2}\.\d{4})', date_part)
        if m:
            start_date = m.group(1)
            end_date = start_date

    return start_date, end_date, start_time, location


def parse_listing_page(html: str) -> list[dict]:
    """Parse a KGSt listing page into event dicts.

    Args:
        html: Raw HTML of the listing page

    Returns:
        List of event dicts
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for box in soup.select(".searchResultBox"):
        # Title and link
        title_el = box.select_one(".searchResultHeadline a")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        event_url = urljoin("https://www.kgst.de", href)

        # Date and location from pipe-delimited span
        date_el = box.select_one(".searchResultTopic span.date")
        date_raw = date_el.get_text(strip=True) if date_el else ""
        start_date, end_date, start_time, location = parse_date_location(date_raw)

        # Description
        desc_el = box.select_one(".searchResultDescription")
        description = desc_el.get_text(strip=True) if desc_el else ""

        listing_text = (
            f"{title}\n"
            f"{start_date} {start_time} – {end_date}\n"
            f"{location}\n"
            f"KGSt\n"
            f"{description}"
        )

        events.append({
            "url": event_url,
            "source_name": SOURCE_NAME,
            "title": title,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "location": location,
            "organizer": "KGSt",
            "description": description,
            "listing_text": listing_text,
            "detail_text": "",
        })

    return events


def scrape_all(max_pages: int = 5) -> list[dict]:
    """Scrape all pages of the KGSt Veranstaltungskalender.

    Args:
        max_pages: Maximum pages to scrape

    Returns:
        List of event dicts
    """
    all_events = []
    seen_urls = set()

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
            if event["url"] not in seen_urls:
                seen_urls.add(event["url"])
                all_events.append(event)

        logger.info(f"Page {page}: {len(events)} events (total: {len(all_events)})")

    logger.info(f"Total events scraped: {len(all_events)}")
    return all_events


def save_to_directus(events: list[dict], client: DirectusClient) -> tuple[int, int]:
    """Save events to Directus, skipping duplicates."""
    saved, skipped = 0, 0

    for event in events:
        existing = client.get_item_by_url(COLLECTION, event["url"])
        if existing:
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
    parser = argparse.ArgumentParser(description="Scrape KGSt events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pages to fetch")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_kgst.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting KGSt scraper")
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
