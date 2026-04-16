#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIGU-Plattform Event Scraper

Scrapes events from the SIGU-Plattform (Soziale Innovationen &
Gemeinwohlorientierte Unternehmen) via their Tribe Events REST API.

API: https://sigu-plattform.de/wp-json/tribe/events/v1/events
Total: ~49 active events, paginated (10 per page default)

Usage:
    python events/scrapers/scrape_sigu.py [--no-directus] [--verbose] [--max-pages 20]
"""

import sys
import os
import json
import logging
import hashlib
import argparse
import re
from datetime import datetime

import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.directus_client import DirectusClient, calculate_content_hash

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_NAME = "SIGU-Plattform"
API_BASE = "https://sigu-plattform.de/wp-json/tribe/events/v1/events"
COLLECTION = "scraped_data"
PER_PAGE = 50


def strip_html(text: str) -> str:
    """Remove HTML tags and clean whitespace."""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def fetch_events_page(page: int = 1, per_page: int = PER_PAGE) -> dict:
    """Fetch a page of events from the Tribe Events API.

    Args:
        page: Page number (1-indexed)
        per_page: Events per page (max 50)

    Returns:
        Raw API response as dict
    """
    params = {
        "page": page,
        "per_page": per_page,
        "status": "publish",
    }
    response = requests.get(API_BASE, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_event(raw: dict) -> dict:
    """Parse a single Tribe Events API event into our scraper format.

    Args:
        raw: Single event dict from the API response

    Returns:
        Normalized event dict ready for Directus
    """
    # Extract venue
    venue = raw.get("venue", {})
    location = venue.get("venue", "Online") if venue else "Online"

    # Extract organizer(s)
    organizers = raw.get("organizer", [])
    organizer_name = ""
    if organizers:
        organizer_name = organizers[0].get("organizer", "") if isinstance(organizers[0], dict) else str(organizers[0])

    # Build listing text for LLM analysis
    description = strip_html(raw.get("description", ""))
    listing_text = (
        f"{raw.get('title', '')}\n"
        f"{raw.get('start_date', '')} – {raw.get('end_date', '')}\n"
        f"{location}\n"
        f"{organizer_name}\n"
        f"{description}"
    )

    return {
        "url": raw.get("url", ""),
        "source_name": SOURCE_NAME,
        "listing_text": listing_text,
        "detail_text": description,
        "title": raw.get("title", ""),
        "start_date": raw.get("start_date", ""),
        "end_date": raw.get("end_date", ""),
        "location": location,
        "organizer": organizer_name,
        "cost": raw.get("cost", ""),
        "website": raw.get("website", ""),
        "image_url": raw.get("image", {}).get("url", "") if raw.get("image") else "",
        "categories": [c.get("name", "") for c in raw.get("categories", [])],
        "tags": [t.get("name", "") for t in raw.get("tags", [])],
        "tribe_id": raw.get("id"),
    }


def scrape_all(max_pages: int = 20) -> list[dict]:
    """Fetch all events from the SIGU API, paginating through all pages.

    Args:
        max_pages: Safety limit on pages to fetch

    Returns:
        List of parsed event dicts
    """
    all_events = []
    page = 1

    while page <= max_pages:
        logger.info(f"Fetching page {page}...")
        try:
            data = fetch_events_page(page=page)
        except Exception as e:
            logger.error(f"Failed to fetch page {page}: {e}")
            break

        events = data.get("events", [])
        if not events:
            break

        for raw in events:
            all_events.append(parse_event(raw))

        total_pages = data.get("total_pages", 1)
        logger.info(f"Page {page}/{total_pages} — got {len(events)} events")

        if page >= total_pages:
            break
        page += 1

    logger.info(f"Total events fetched: {len(all_events)}")
    return all_events


def save_to_directus(events: list[dict], client: DirectusClient) -> tuple[int, int]:
    """Save events to Directus, skipping duplicates.

    Args:
        events: List of parsed event dicts
        client: DirectusClient instance

    Returns:
        Tuple of (saved_count, skipped_count)
    """
    saved, skipped = 0, 0

    for event in events:
        # Check duplicate by URL
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
    parser = argparse.ArgumentParser(description="Scrape SIGU-Plattform events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument("--max-pages", type=int, default=20, help="Max pages to fetch")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_sigu.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting SIGU-Plattform scraper")
    events = scrape_all(max_pages=args.max_pages)

    if args.no_directus:
        print(json.dumps(events, ensure_ascii=False, indent=2))
        logger.info(f"Printed {len(events)} events to stdout")
        return

    client = DirectusClient(
        base_url=os.environ["DIRECTUS_API_URL"],
        token=os.environ.get("DIRECTUS_API_TOKEN"),
    )

    saved, skipped = save_to_directus(events, client)
    logger.info(f"Done — saved: {saved}, skipped (duplicates): {skipped}")


if __name__ == "__main__":
    main()
