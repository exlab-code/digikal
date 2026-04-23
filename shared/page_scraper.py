#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared HTML page scraper used wherever we need to turn an event URL into
text the downstream LLM can reason about.

Callers: events/email_submit.py (inbound user submissions) and
events/ics_import.py (optional detail-page enrichment for iCal feeds).
"""

import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DigiKal/1.0; +https://www.digikal.org)"
}


def _strip_pretix_sibling_list(text, url):
    """Remove pretix's inline "switch to another date" sibling list.

    On pretix instance pages (e.g. /d3/series/4909821/), pretix renders a
    list of all sibling instances between the page's own title and its
    actual details. Feeding that to the LLM causes it to pick the series
    title or the first sibling's date for every instance in the series
    (all 3 get collapsed into one duplicate).

    The sibling list starts with "Zu anderem Termin wechseln" and ends at
    the last standalone "Tickets" line before the current instance's
    "Beginn:" section. We keep the outer frame and drop what's in between.
    """
    if "pretix.eu" not in url:
        return text
    start_marker = "Zu anderem Termin wechseln"
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return text
    beginn_idx = text.find("Beginn:", start_idx)
    if beginn_idx == -1:
        return text
    tickets_idx = text.rfind("Tickets", start_idx, beginn_idx)
    if tickets_idx == -1:
        return text
    return text[:start_idx] + text[tickets_idx + len("Tickets"):]


def scrape_url(url):
    """Fetch a URL and extract its text content."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Try common content selectors first
        content = None
        for selector in ["main", "article", '[role="main"]', ".content", ".entry-content"]:
            el = soup.select_one(selector)
            if el:
                content = el.get_text(separator="\n", strip=True)
                break

        if not content:
            content = soup.get_text(separator="\n", strip=True)

        content = _strip_pretix_sibling_list(content, url)

        if len(content) > 10000:
            content = content[:10000] + "..."

        return content
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None
