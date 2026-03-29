#!/usr/bin/env python3
"""Generate a static .ics calendar file from approved Directus events."""

import requests
import json
import os
import sys
import logging
from datetime import timedelta
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from datetime import datetime
import dateutil.parser
from dateutil import tz
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("generate-ics")

DIRECTUS_URL = os.getenv("DIRECTUS_API_URL")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_API_TOKEN")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "website", "static", "calendar.ics")
BERLIN = tz.gettz("Europe/Berlin")


def fetch_approved_events():
    """Fetch all approved events from Directus."""
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
    params = {
        "filter": json.dumps({"review_status": {"_eq": "approved"}}),
        "sort": "start_date",
        "limit": -1,
    }
    response = requests.get(f"{DIRECTUS_URL}/items/events", headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])


def build_calendar(events):
    """Build an iCalendar object from a list of Directus events."""
    cal = Calendar()
    cal.add("prodid", "-//DigiKal//Veranstaltungskalender//DE")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", "DigiKal – Veranstaltungen für Nonprofits")
    cal.add("x-wr-timezone", "Europe/Berlin")

    # VTIMEZONE for Europe/Berlin
    vtz = Timezone()
    vtz.add("tzid", "Europe/Berlin")
    std = TimezoneStandard()
    std.add("dtstart", datetime(1970, 10, 25, 3, 0, 0))
    std.add("rrule", {"freq": "yearly", "bymonth": 10, "byday": "-1su"})
    std.add("tzoffsetfrom", timedelta(hours=2))
    std.add("tzoffsetto", timedelta(hours=1))
    std.add("tzname", "CET")
    vtz.add_component(std)
    dst = TimezoneDaylight()
    dst.add("dtstart", datetime(1970, 3, 29, 2, 0, 0))
    dst.add("rrule", {"freq": "yearly", "bymonth": 3, "byday": "-1su"})
    dst.add("tzoffsetfrom", timedelta(hours=1))
    dst.add("tzoffsetto", timedelta(hours=2))
    dst.add("tzname", "CEST")
    vtz.add_component(dst)
    cal.add_component(vtz)

    skipped = 0
    for event in events:
        if not event.get("start_date"):
            skipped += 1
            continue

        try:
            start = dateutil.parser.parse(event["start_date"])
            if start.tzinfo is None:
                start = start.replace(tzinfo=BERLIN)
        except (TypeError, ValueError):
            skipped += 1
            continue

        end_raw = event.get("end_date")
        if end_raw:
            try:
                end = dateutil.parser.parse(end_raw)
                if end.tzinfo is None:
                    end = end.replace(tzinfo=BERLIN)
            except (TypeError, ValueError):
                end = start + timedelta(hours=1)
        else:
            end = start + timedelta(hours=1)

        ve = Event()
        ve.add("uid", f"nonprofit-{event['id']}@digikal.org")
        ve.add("summary", event.get("title", "Untitled"))
        ve.add("dtstart", start)
        ve.add("dtend", end)
        ve.add("dtstamp", datetime.now(tz=BERLIN))

        # Description
        parts = []
        if event.get("description"):
            parts.append(event["description"])
        if event.get("organizer"):
            parts.append(f"Veranstalter: {event['organizer']}")
        if event.get("cost"):
            parts.append(f"Kosten: {event['cost']}")
        tags = event.get("tags") or []
        if isinstance(tags, list) and tags:
            parts.append(f"Themen: {', '.join(str(t) for t in tags if t)}")
        if event.get("website"):
            parts.append(f"Mehr Infos: {event['website']}")
        if parts:
            ve.add("description", "\n\n".join(parts))

        if event.get("website"):
            ve.add("url", event["website"])
        if event.get("location"):
            ve.add("location", event["location"])
        if event.get("organizer"):
            ve.add("x-organizer", event["organizer"])

        cal.add_component(ve)

    logger.info(f"Added {len(events) - skipped} events to calendar ({skipped} skipped)")
    return cal


def main():
    if not DIRECTUS_URL or not DIRECTUS_TOKEN:
        logger.error("DIRECTUS_API_URL and DIRECTUS_API_TOKEN must be set")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description="Generate static .ics calendar file")
    parser.add_argument("-o", "--output", default=OUTPUT_PATH, help="Output file path")
    args = parser.parse_args()

    logger.info("Fetching approved events from Directus...")
    events = fetch_approved_events()
    logger.info(f"Fetched {len(events)} approved events")

    cal = build_calendar(events)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "wb") as f:
        f.write(cal.to_ical())

    logger.info(f"Written calendar to {args.output}")


if __name__ == "__main__":
    main()
