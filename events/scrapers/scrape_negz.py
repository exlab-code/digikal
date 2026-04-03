#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEGZ Event Scraper

Scrapes events from NEGZ (Kompetenznetzwerk Digitale Verwaltung) —
a key network for digital government with 220+ members.

Source: https://negz.org/aktuelle-veranstaltungen/
Method: HTML scraping (WordPress + Toolset Views), 2 pages
Selectors: .wpv-block-loop-item with h5.tb-heading for title, first <p> for date

Usage:
    python events/scrapers/scrape_negz.py [--no-directus] [--verbose] [--max-pages 5]
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

SOURCE_NAME = "NEGZ"
BASE_URL = "https://negz.org/aktuelle-veranstaltungen/"
COLLECTION = "scraped_data"


def fetch_page(page: int = 1) -> str:
    """Fetch a listing page from NEGZ.

    Args:
        page: Page number (1-indexed)

    Returns:
        HTML content as string
    """
    params = {}
    if page > 1:
        params = {"wpv_view_count": "506", "wpv_paged": str(page)}

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_german_date(text: str) -> str:
    """Parse German date text like 'Freitag, 10. April 2026' to '10.04.2026'.

    Args:
        text: German date string

    Returns:
        Date in DD.MM.YYYY format, or original text if parsing fails
    """
    months = {
        "januar": "01", "februar": "02", "märz": "03", "april": "04",
        "mai": "05", "juni": "06", "juli": "07", "august": "08",
        "september": "09", "oktober": "10", "november": "11", "dezember": "12",
    }

    text = text.strip().lower()
    # Remove weekday prefix (e.g. "Freitag, ")
    text = re.sub(r'^[a-zäöü]+,\s*', '', text)

    m = re.match(r'(\d{1,2})\.\s*([a-zäöü]+)\s+(\d{4})', text)
    if m:
        day = m.group(1).zfill(2)
        month = months.get(m.group(2), "00")
        year = m.group(3)
        return f"{day}.{month}.{year}"

    return text


def fetch_detail(url: str) -> str:
    """Fetch detail page and extract description text.

    Args:
        url: Full URL to the event detail page

    Returns:
        Extracted description text
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove junk
        for tag in soup.select("style, script, noscript"):
            tag.decompose()

        # Collect real paragraphs (skip base64-encoded CSS noise)
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 30 and not text.startswith("LnR"):
                paragraphs.append(text)

        return "\n".join(paragraphs[:5])
    except Exception as e:
        logger.warning(f"Failed to fetch detail page {url}: {e}")
        return ""


def parse_listing_page(html: str) -> list[dict]:
    """Parse a NEGZ listing page into event dicts.

    Args:
        html: Raw HTML of the listing page

    Returns:
        List of event dicts
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for item in soup.select(".wpv-block-loop-item"):
        # Title and link
        heading = item.select_one("h5.tb-heading a")
        if not heading:
            heading = item.select_one("h5.tb-heading")
        if not heading:
            continue

        title = heading.get_text(strip=True)
        href = heading.get("href", "") if heading.name == "a" else ""
        if not href:
            link = item.select_one("a[href*='/termin/']")
            if link:
                href = link.get("href", "")

        if not href:
            continue

        event_url = urljoin("https://negz.org", href)

        # Date from first <p>
        date_el = item.select_one("p")
        date_raw = date_el.get_text(strip=True) if date_el else ""
        date_parsed = parse_german_date(date_raw) if date_raw else ""

        listing_text = (
            f"{title}\n"
            f"{date_parsed}\n"
            f"NEGZ\n"
        )

        events.append({
            "url": event_url,
            "source_name": SOURCE_NAME,
            "title": title,
            "start_date": date_parsed,
            "end_date": date_parsed,
            "location": "",
            "organizer": "NEGZ",
            "listing_text": listing_text,
            "detail_text": "",
        })

    return events


def scrape_all(max_pages: int = 5) -> list[dict]:
    """Scrape all pages of NEGZ events."""
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
                logger.info(f"Fetching detail: {event['title']}")
                detail = fetch_detail(event["url"])
                event["detail_text"] = detail
                event["listing_text"] += detail
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
    parser = argparse.ArgumentParser(description="Scrape NEGZ events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pages to fetch")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_negz.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting NEGZ scraper")
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
