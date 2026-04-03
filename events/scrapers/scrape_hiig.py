#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HIIG Event Scraper

Scrapes events from the Alexander von Humboldt Institut für Internet
und Gesellschaft (HIIG).

Source: https://www.hiig.de/events/
Method: HTML scraping, single page (all events rendered server-side)
Note: Page contains ~2 upcoming + ~785 past events. We only scrape upcoming
      and recent past events (configurable cutoff).

Selectors:
  Upcoming: li.events.upcoming -> h3.title a, p.date
  Past: li.hiig__events--past -> .hiig__event__info h3 a, span.hiig-general__categories

Usage:
    python events/scrapers/scrape_hiig.py [--no-directus] [--verbose] [--include-past 30]
"""

import sys
import os
import json
import logging
import re
import argparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.directus_client import DirectusClient, calculate_content_hash

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_NAME = "HIIG"
PAGE_URL = "https://www.hiig.de/events/"
COLLECTION = "scraped_data"


def fetch_page() -> str:
    """Fetch the HIIG events page (single large page)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    response = requests.get(PAGE_URL, headers=headers, timeout=60)
    response.raise_for_status()
    return response.text


def parse_date(text: str) -> str:
    """Parse date from text like '28.04.2026' or '25. März 2026'.

    Returns:
        Date in DD.MM.YYYY format
    """
    text = text.strip()
    # Already in DD.MM.YYYY
    m = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
    if m:
        return m.group(1)
    return text



def fetch_detail(url: str) -> tuple[str, str, str]:
    """Fetch detail page and extract description, location, and time.

    Args:
        url: Full URL to the event detail page

    Returns:
        Tuple of (description, location, time)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.select("style, script, noscript"):
            tag.decompose()

        # Description from paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 30:
                paragraphs.append(text)
        description = "\n".join(paragraphs[:5])

        # Location from .event-meta
        location = ""
        meta = soup.select_one(".event-meta")
        if meta:
            meta_text = meta.get_text(separator="\n", strip=True)
            # Look for address line (contains street/city)
            for line in meta_text.split("\n"):
                if any(kw in line for kw in ["Straße", "straße", "Berlin", "10"]):
                    location = line.strip()
                    break

        # Time from meta
        time_str = ""
        m = re.search(r'(\d{1,2}[.:]\d{2})\s*(?:Uhr|p\.m\.|a\.m\.)', meta_text if meta else "")
        if m:
            time_str = m.group(1).replace(".", ":")

        return description, location, time_str
    except Exception as e:
        logger.warning(f"Failed to fetch detail page {url}: {e}")
        return "", "", ""


def parse_events(html: str) -> list[dict]:
    """Parse upcoming events from the HIIG events page.

    Args:
        html: Raw HTML

    Returns:
        List of event dicts
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for li in soup.select("li.events.upcoming"):
        title_el = li.select_one("h3.title a")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        date_el = li.select_one("p.date")
        date_str = parse_date(date_el.get_text(strip=True)) if date_el else ""

        listing_text = f"{title}\n{date_str}\nHIIG\n"

        events.append({
            "url": href,
            "source_name": SOURCE_NAME,
            "title": title,
            "start_date": date_str,
            "end_date": date_str,
            "location": "",
            "organizer": "HIIG",
            "listing_text": listing_text,
            "detail_text": "",
        })

    return events


def scrape_all() -> list[dict]:
    """Scrape upcoming events from HIIG with detail page enrichment."""
    logger.info("Fetching HIIG events page...")
    html = fetch_page()
    events = parse_events(html)

    for event in events:
        logger.info(f"Fetching detail: {event['title']}")
        description, location, time_str = fetch_detail(event["url"])
        event["detail_text"] = description
        event["location"] = location or event["location"]
        event["start_time"] = time_str
        event["listing_text"] += description
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
    parser = argparse.ArgumentParser(description="Scrape HIIG events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_hiig.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting HIIG scraper")
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
