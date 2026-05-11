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

# Heading text of pretix's "switch to another date" panel (German locale).
_PRETIX_SIBLING_MARKER = "Zu anderem Termin wechseln"


def _strip_pretix_sibling_widget(soup):
    """Drop pretix's "switch to another date" panel from the DOM.

    On a pretix series instance page (hosted pretix.eu or a self-hosted
    instance like tickets.skala-campus.org) pretix renders a collapsible
    panel — a list or a calendar of every sibling instance — before the
    current instance's own details:

        <details class="panel panel-default">
          <summary class="panel-heading">… Zu anderem Termin wechseln …</summary>
          <div><div class="panel-body"> … all siblings … </div></div>
        </details>

    Left in, the downstream LLM picks a sibling's date (or the series
    title) for every instance, collapsing the whole series into one
    duplicate. Removing the panel keeps each page instance-specific.
    """
    for node in soup.find_all(string=lambda s: s and _PRETIX_SIBLING_MARKER in s):
        panel = node.find_parent(["details", "div"], class_="panel")
        if panel:
            panel.decompose()


def scrape_url(url):
    """Fetch a URL and extract its text content."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        _strip_pretix_sibling_widget(soup)

        # Try common content selectors first
        content = None
        for selector in ["main", "article", '[role="main"]', ".content", ".entry-content"]:
            el = soup.select_one(selector)
            if el:
                content = el.get_text(separator="\n", strip=True)
                break

        if not content:
            content = soup.get_text(separator="\n", strip=True)

        if len(content) > 10000:
            content = content[:10000] + "..."

        return content
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None
