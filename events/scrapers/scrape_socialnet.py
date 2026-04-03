#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
socialnet Kalender Scraper

Scrapes events from the socialnet Kalender — the largest event calendar
for the German-speaking social and health sector.

Source: https://www.socialnet.de/kalender/messen-kongresse-und-tagungen
Method: HTML scraping, paginated (20 per page, ~141 total across 8 pages)

Usage:
    python events/scrapers/scrape_socialnet.py [--no-directus] [--verbose] [--max-pages 10]
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

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.directus_client import DirectusClient, calculate_content_hash

load_dotenv()

logger = logging.getLogger(__name__)

SOURCE_NAME = "socialnet Kalender"
BASE_URL = "https://www.socialnet.de/kalender/messen-kongresse-und-tagungen"
DETAIL_BASE = "https://www.socialnet.de"
COLLECTION = "scraped_data"


def fetch_page(page: int = 1) -> str:
    """Fetch a listing page from the socialnet Kalender.

    Args:
        page: Page number (1-indexed)

    Returns:
        HTML content as string
    """
    url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}#pagination"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def fetch_detail(path: str) -> str:
    """Fetch a detail page for a single event.

    Args:
        path: Relative URL path (e.g. /kalender/38616_79197.html)

    Returns:
        Extracted detail text
    """
    url = urljoin(DETAIL_BASE, path)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; digikal-scraper/1.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try common content selectors
        for selector in [".kalender-detail", ".content", "main", "article"]:
            content = soup.select_one(selector)
            if content:
                return content.get_text(separator="\n", strip=True)

        # Fallback: get body text
        body = soup.find("body")
        return body.get_text(separator="\n", strip=True) if body else ""
    except Exception as e:
        logger.warning(f"Failed to fetch detail page {url}: {e}")
        return ""


def parse_date_range(text: str) -> tuple[str, str]:
    """Parse German date range text into start/end dates.

    Handles formats like:
        '14.04.2026' -> ('14.04.2026', '14.04.2026')
        '15.–17.05.2026' -> ('15.05.2026', '17.05.2026')
        '20.04.–15.05.2026' -> ('20.04.2026', '15.05.2026')
        '21.04.–12.11.2026' -> ('21.04.2026', '12.11.2026')

    Args:
        text: Raw date text from the listing

    Returns:
        Tuple of (start_date, end_date) as strings
    """
    text = text.replace("\n", " ").strip()
    text = text.replace("–", "-").replace("—", "-")

    # Full range: DD.MM.-DD.MM.YYYY or DD.MM.YYYY-DD.MM.YYYY
    m = re.match(r'(\d{1,2}\.\d{2}\.?)[\s]*-[\s]*(\d{1,2}\.\d{2}\.\d{4})', text)
    if m:
        start_part = m.group(1).rstrip(".")
        end_full = m.group(2)
        # If start has no year, borrow from end
        if len(start_part.split(".")) == 2:
            year = end_full.split(".")[-1]
            # Check if start has month
            parts = start_part.split(".")
            if len(parts) == 2 and len(parts[1]) >= 2:
                start = f"{start_part}.{year}"
            else:
                # Day only range like 15.-17.05.2026
                end_parts = end_full.split(".")
                start = f"{parts[0]}.{end_parts[1]}.{end_parts[2]}"
        else:
            start = start_part
        return start, end_full

    # Day-only range within same month: DD.-DD.MM.YYYY
    m = re.match(r'(\d{1,2})\.[\s]*-[\s]*(\d{1,2}\.\d{2}\.\d{4})', text)
    if m:
        day_start = m.group(1)
        end_full = m.group(2)
        end_parts = end_full.split(".")
        start = f"{day_start}.{end_parts[1]}.{end_parts[2]}"
        return start, end_full

    # Single date: DD.MM.YYYY
    m = re.match(r'(\d{1,2}\.\d{2}\.\d{4})', text)
    if m:
        date = m.group(1)
        return date, date

    return text, text


def parse_listing_page(html: str) -> list[dict]:
    """Parse a socialnet Kalender listing page into event dicts.

    Structure: <dl class="eventresults"> with alternating <dt> (date/location)
    and <dd> (title link, organizer, category) pairs.

    Args:
        html: Raw HTML of the listing page

    Returns:
        List of event dicts with basic info from the listing
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    dl = soup.select_one("dl.eventresults")
    if not dl:
        return events

    # Iterate dt/dd pairs
    current_dt = None
    for child in dl.children:
        if not hasattr(child, "name") or child.name not in ("dt", "dd"):
            continue

        if child.name == "dt":
            current_dt = child
            continue

        if child.name == "dd" and current_dt is not None:
            # Parse <dt>: date and location
            dt_text = current_dt.get_text(separator="\n", strip=True)
            lines = [l.strip() for l in dt_text.split("\n") if l.strip()]
            date_raw = lines[0] if lines else ""
            location = lines[1] if len(lines) > 1 else ""

            start_date, end_date = parse_date_range(date_raw)

            # Parse <dd>: title link, organizer, category
            link = child.select_one("a[href*='kalender/']")
            if not link:
                current_dt = None
                continue

            href = link.get("href", "")
            title = link.get_text(strip=True)

            # Organizer: text after title, before <small>
            dd_text = child.get_text(separator="\n", strip=True)
            dd_lines = [l.strip() for l in dd_text.split("\n") if l.strip()]
            organizer = ""
            category = ""
            for line in dd_lines:
                if line == title:
                    continue
                if not organizer:
                    organizer = line
                else:
                    category = line

            # Build full URL — href is relative like "kalender/38616_79197.html"
            event_url = urljoin(DETAIL_BASE + "/", href)

            events.append({
                "url": event_url,
                "source_name": SOURCE_NAME,
                "title": title,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "organizer": organizer,
                "category": category,
                "detail_path": "/" + href if not href.startswith("/") else href,
            })

            current_dt = None

    return events


def scrape_all(max_pages: int = 10, fetch_details: bool = True) -> list[dict]:
    """Scrape all pages of the socialnet Kalender.

    Args:
        max_pages: Maximum pages to scrape
        fetch_details: Whether to fetch detail pages for each event

    Returns:
        List of event dicts with listing and detail text
    """
    all_events = []
    seen_urls = set()

    for page in range(1, max_pages + 1):
        logger.info(f"Fetching listing page {page}...")
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

            # Build listing text
            listing_text = (
                f"{event['title']}\n"
                f"{event['start_date']} – {event['end_date']}\n"
                f"{event['location']}\n"
                f"{event['organizer']}\n"
                f"{event.get('category', '')}"
            )
            event["listing_text"] = listing_text

            # Fetch detail page
            if fetch_details:
                logger.debug(f"Fetching detail: {event['title']}")
                event["detail_text"] = fetch_detail(event["detail_path"])
            else:
                event["detail_text"] = ""

            all_events.append(event)

        logger.info(f"Page {page}: {len(events)} events (total: {len(all_events)})")

    logger.info(f"Total events scraped: {len(all_events)}")
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
    parser = argparse.ArgumentParser(description="Scrape socialnet Kalender events")
    parser.add_argument("--no-directus", action="store_true", help="Skip Directus, print JSON")
    parser.add_argument("--no-details", action="store_true", help="Skip fetching detail pages")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages to fetch")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("events/logs/scrape_socialnet.log", encoding="utf-8"),
        ],
    )

    logger.info("Starting socialnet Kalender scraper")
    events = scrape_all(max_pages=args.max_pages, fetch_details=not args.no_details)

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
