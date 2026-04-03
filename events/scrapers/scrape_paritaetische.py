#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paritätische Akademie Berlin Scraper

Scrapes digitalization events from the Paritätische Akademie Berlin.
All data conveniently available in data-* attributes on .event divs.

Source: https://akademie.org/themen/digitalisierung/
Method: HTML scraping, no pagination (all events loaded at once)
Selectors: .event with data-title, data-date, data-summary, data-tag etc.

Usage:
    python events/scrapers/scrape_paritaetische.py [--no-directus] [--verbose]
"""

import sys
import os
import json
import logging
import argparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.directus_client import DirectusClient, calculate_content_hash

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_NAME = "Paritätische Akademie Berlin"
PAGE_URL = "https://akademie.org/themen/digitalisierung/"
COLLECTION = "scraped_data"


def fetch_page() -> str:
    """Fetch the Paritätische Akademie digitalization events page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    response = requests.get(PAGE_URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_events(html: str) -> list[dict]:
    """Parse events from data-* attributes on .event elements.

    Args:
        html: Raw HTML of the page

    Returns:
        List of event dicts
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for el in soup.select(".event"):
        title = el.get("data-title", "").strip()
        if not title:
            continue

        # Link from inner <a>
        link = el.select_one("a[href*='/veranstaltung/']")
        href = link.get("href", "") if link else ""
        if href and not href.startswith("http"):
            href = f"https://akademie.org{href}"

        date_str = el.get("data-date", "")
        summary = el.get("data-summary", "").strip()
        tags = el.get("data-tag", "")
        is_online = el.get("data-online", "0") == "1"
        event_id = el.get("data-eventid", "")

        location = "Online" if is_online else ""

        listing_text = (
            f"{title}\n"
            f"{date_str}\n"
            f"{location}\n"
            f"Paritätische Akademie Berlin\n"
            f"{summary}\n"
            f"Tags: {tags}"
        )

        events.append({
            "url": href,
            "source_name": SOURCE_NAME,
            "title": title,
            "start_date": date_str,
            "end_date": date_str,
            "location": location,
            "organizer": "Paritätische Akademie Berlin",
            "description": summary,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "event_id": event_id,
            "listing_text": listing_text,
            "detail_text": "",
        })

    return events


def scrape_all() -> list[dict]:
    """Scrape all events from the digitalization page."""
    logger.info("Fetching Paritätische Akademie page...")
    html = fetch_page()
    events = parse_events(html)
    logger.info(f"Total events scraped: {len(events)}")
    return events


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
    parser = argparse.ArgumentParser(description="Scrape Paritätische Akademie events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_paritaetische.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting Paritätische Akademie scraper")
    events = scrape_all()

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
