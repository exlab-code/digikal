#!/usr/bin/env python3
"""
Newsletter Generator for DigiKal

Fetches next month's approved events from Directus,
generates an HTML email, and creates a draft campaign in Listmonk.
"""
import os
import json
import requests
from datetime import datetime, date
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
DIRECTUS_URL = os.getenv("DIRECTUS_API_URL")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_API_TOKEN")
LISTMONK_URL = os.getenv("LISTMONK_URL")
LISTMONK_USER = os.getenv("LISTMONK_USER", "digikal-events")
LISTMONK_API = os.getenv("LISTMONK_API")
LISTMONK_LIST_ID = int(os.getenv("LISTMONK_LIST_ID", "3"))

# --- Colors matching website ---
PRIMARY = "#3178ff"
PRIMARY_DARK = "#2563eb"
GRAY_50 = "#f9fafb"
GRAY_100 = "#f3f4f6"
GRAY_200 = "#e5e7eb"
GRAY_500 = "#6b7280"
GRAY_700 = "#374151"
GRAY_800 = "#1f2937"

# German month names
MONTH_NAMES = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

WEEKDAY_NAMES = [
    "Montag", "Dienstag", "Mittwoch", "Donnerstag",
    "Freitag", "Samstag", "Sonntag"
]


def fetch_events(year, month):
    """Fetch approved events for a given month from Directus."""
    # Build date range for the month
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year + 1}-01-01"
    else:
        end = f"{year}-{month + 1:02d}-01"

    params = {
        "filter": json.dumps({
            "_and": [
                {"approved": {"_eq": True}},
                {"start_date": {"_gte": start}},
                {"start_date": {"_lt": end}},
            ]
        }),
        "sort": "start_date",
        "limit": -1,
    }

    resp = requests.get(
        f"{DIRECTUS_URL}/items/events",
        params=params,
        headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
    )
    resp.raise_for_status()
    return resp.json()["data"]


def group_by_week(events):
    """Group events by calendar week, return list of (week_label, events)."""
    weeks = defaultdict(list)
    for ev in events:
        d = datetime.fromisoformat(ev["start_date"]).date()
        # ISO calendar week
        _, week_num, _ = d.isocalendar()
        weeks[week_num].append(ev)

    result = []
    for week_num in sorted(weeks.keys()):
        week_events = weeks[week_num]
        # Date range label from first/last event in week
        dates = [datetime.fromisoformat(e["start_date"]).date() for e in week_events]
        first, last = min(dates), max(dates)
        if first == last:
            label = f"{first.day}. {MONTH_NAMES[first.month]}"
        else:
            if first.month == last.month:
                label = f"{first.day}.–{last.day}. {MONTH_NAMES[first.month]}"
            else:
                label = f"{first.day}. {MONTH_NAMES[first.month]} – {last.day}. {MONTH_NAMES[last.month]}"
        result.append((f"KW {week_num}: {label}", week_events))

    return result


def format_time(iso_str):
    """Extract HH:MM from ISO datetime, return empty string if midnight/missing."""
    if not iso_str or "T" not in iso_str:
        return ""
    d = datetime.fromisoformat(iso_str)
    if d.hour == 0 and d.minute == 0:
        return ""
    return f"{d.hour:02d}:{d.minute:02d}"


def format_date_short(iso_str):
    """Format as 'Mo, 03.03.'"""
    d = datetime.fromisoformat(iso_str)
    weekday = WEEKDAY_NAMES[d.weekday()][:2]
    return f"{weekday}, {d.day:02d}.{d.month:02d}."


def render_event_row(ev):
    """Render a single event as an HTML table row."""
    d = datetime.fromisoformat(ev["start_date"])
    weekday_short = WEEKDAY_NAMES[d.weekday()][:2]
    day = f"{d.day:02d}"
    month_short = MONTH_NAMES[d.month][:3]

    time_str = format_time(ev["start_date"])
    end_time = format_time(ev.get("end_date", ""))
    time_display = ""
    if time_str:
        time_display = f"{time_str} Uhr"
        if end_time:
            time_display = f"{time_str}–{end_time} Uhr"

    location = ev.get("location") or "Online"
    organizer = ev.get("organizer") or ev.get("source") or ""
    cost = ev.get("cost") or ""
    if cost and cost.lower() in ("0", "kostenlos", "free"):
        cost = "Kostenlos"

    link = ev.get("website") or ev.get("registration_link") or ""
    title = ev.get("title", "")
    description = ev.get("description") or ""
    if len(description) > 200:
        cut = description[:200].rfind(" ")
        description = description[:cut if cut > 0 else 200] + "…"

    # Meta line parts
    meta_parts = []
    if time_display:
        meta_parts.append(time_display)
    meta_parts.append(location)
    if organizer:
        meta_parts.append(organizer)
    if cost:
        meta_parts.append(cost)
    meta_line = " · ".join(meta_parts)

    # Title as link if URL available
    title_html = f'<a href="{link}" style="color:{GRAY_800};text-decoration:none;font-weight:600;">{title}</a>' if link else f'<span style="font-weight:600;color:{GRAY_800};">{title}</span>'

    return f'''
    <tr>
      <td style="padding:12px 16px;border:none;border-bottom:1px solid {GRAY_200};vertical-align:top;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border:none;border-collapse:collapse;">
          <tr>
            <td style="width:48px;vertical-align:top;padding-right:12px;">
              <div style="background-color:{PRIMARY};color:white;border-radius:6px;text-align:center;padding:5px 0;width:44px;">
                <div style="font-size:10px;font-weight:500;line-height:1.2;opacity:0.85;">{weekday_short}</div>
                <div style="font-size:18px;font-weight:700;line-height:1.2;">{day}</div>
                <div style="font-size:10px;line-height:1.2;opacity:0.85;">{month_short}</div>
              </div>
            </td>
            <td style="vertical-align:top;">
              <div style="font-size:15px;line-height:1.4;margin-bottom:2px;">{title_html}</div>
              <div style="font-size:13px;color:{GRAY_500};line-height:1.4;">{meta_line}</div>
              {f'<div style="font-size:13px;color:{GRAY_700};line-height:1.5;margin-top:4px;">{description}</div>' if description else ''}
            </td>
          </tr>
        </table>
      </td>
    </tr>'''


def render_newsletter(events, year, month, editorial=""):
    """Render the full newsletter HTML."""
    month_name = MONTH_NAMES[month]
    weeks = group_by_week(events)
    event_count = len(events)

    # Editorial section (optional custom text block)
    if editorial:
        editorial_section = f'''
          <tr>
            <td style="background-color:white;padding:0 24px 20px 24px;">
              <div style="font-size:14px;color:{GRAY_700};line-height:1.6;">{editorial}</div>
            </td>
          </tr>'''
    else:
        editorial_section = ""

    # Build week sections
    week_sections = ""
    for week_label, week_events in weeks:
        rows = "\n".join(render_event_row(ev) for ev in week_events)
        week_sections += f'''
        <tr>
          <td style="padding:24px 20px 8px 20px;">
            <div style="font-size:14px;font-weight:600;color:{PRIMARY};text-transform:uppercase;letter-spacing:0.5px;">{week_label}</div>
          </td>
        </tr>
        <tr>
          <td style="padding:0 20px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:white;border-radius:8px;border:none;border-collapse:collapse;">
              {rows}
            </table>
          </td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>DigiKal Newsletter – {month_name} {year}</title>
  <style>
    table, tr, td, th {{ border: none !important; border-collapse: collapse !important; }}
    table {{ mso-table-lspace: 0pt !important; mso-table-rspace: 0pt !important; }}
    img {{ border: 0; }}
  </style>
</head>
<body style="margin:0;padding:0;background:transparent;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:transparent;border:none;border-collapse:collapse;">
    <tr>
      <td align="center" style="padding:0;">
        <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px;width:100%;border:none;border-collapse:collapse;">

          <!-- Header -->
          <tr>
            <td style="background-color:{PRIMARY};border-radius:12px 12px 0 0;padding:28px 24px;text-align:center;">
              <a href="https://digikal.org" style="text-decoration:none;color:white;font-size:24px;font-weight:700;letter-spacing:-0.5px;">DigiKal</a>
            </td>
          </tr>

          <!-- Intro -->
          <tr>
            <td style="background-color:white;padding:24px 24px 16px 24px;">
              <h1 style="margin:0 0 8px 0;font-size:22px;font-weight:700;color:{GRAY_800};">Veranstaltungen im {month_name} {year}</h1>
              <p style="margin:0;font-size:14px;color:{GRAY_500};line-height:1.5;">{event_count} Webinare, Workshops und Seminare für gemeinnützige Organisationen. Filterbare Events fürs ganze Jahr findest du auf <a href="https://digikal.org" style="color:{PRIMARY};text-decoration:none;font-weight:500;">digikal.org</a></p>
            </td>
          </tr>

          <!-- Editorial (optional custom text) -->
          {editorial_section}

          <!-- Events by week -->
          <tr>
            <td style="background-color:{GRAY_50};">
              <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border:none;border-collapse:collapse;">
                {week_sections}
                <tr><td style="height:24px;"></td></tr>
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="background-color:white;padding:24px;text-align:center;">
              <a href="https://digikal.org" style="display:inline-block;background-color:{PRIMARY};color:white;text-decoration:none;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;">Alle Veranstaltungen auf digikal.org</a>
              <p style="margin:12px 0 0 0;font-size:13px;color:{GRAY_500};">Kalender abonnieren · Filter nach Thema, Format und Monat</p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:{GRAY_800};border-radius:0 0 12px 12px;padding:20px 24px;text-align:center;">
              <div style="font-size:13px;color:rgba(255,255,255,0.6);line-height:1.6;">
                DigiKal – Julius Falk / <a href="https://ex-lab.de" style="color:rgba(255,255,255,0.8);text-decoration:underline;">ex:lab</a><br>
                <a href="{{{{ UnsubscribeURL }}}}" style="color:rgba(255,255,255,0.6);text-decoration:underline;">Newsletter abbestellen</a>
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>'''


def get_send_date(year, month):
    """Get the day before the 1st of the target month, at 09:00 CET."""
    first_of_month = date(year, month, 1)
    day_before = first_of_month - __import__('datetime').timedelta(days=1)
    # 09:00 CET = 08:00 UTC
    return f"{day_before.isoformat()}T08:00:00Z"


def create_campaign(html, year, month, schedule=True):
    """Create a campaign in Listmonk and optionally schedule it."""
    month_name = MONTH_NAMES[month]
    send_at = get_send_date(year, month)

    payload = {
        "name": f"DigiKal – {month_name} {year}",
        "subject": f"DigiKal: Veranstaltungen im {month_name} {year}",
        "from_email": "DigiKal.org <email@mg.buerofalk.de>",
        "lists": [LISTMONK_LIST_ID],
        "body": html,
        "content_type": "html",
        "type": "regular",
        "tags": ["newsletter", "monthly"],
        "headers": [{"Reply-To": "julius@ex-lab.de"}],
        "send_at": send_at,
    }

    resp = requests.post(
        f"{LISTMONK_URL}/api/campaigns",
        json=payload,
        auth=(LISTMONK_USER, LISTMONK_API),
    )
    resp.raise_for_status()
    data = resp.json()["data"]
    campaign_id = data["id"]
    print(f"Campaign created: #{campaign_id} – {data['name']}")
    print(f"Scheduled for: {send_at} (09:00 CET)")

    if schedule:
        resp = requests.put(
            f"{LISTMONK_URL}/api/campaigns/{campaign_id}/status",
            json={"status": "scheduled"},
            auth=(LISTMONK_USER, LISTMONK_API),
        )
        resp.raise_for_status()
        print(f"Status: scheduled")

    return data


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate DigiKal monthly newsletter")
    parser.add_argument("--month", type=int, help="Month (1-12), default: next month")
    parser.add_argument("--year", type=int, help="Year, default: current/next year")
    parser.add_argument("--editorial", type=str, default="", help="Custom editorial text (HTML allowed)")
    parser.add_argument("--preview", action="store_true", help="Write HTML to file instead of creating campaign")
    parser.add_argument("--no-schedule", action="store_true", help="Create as draft without scheduling")
    args = parser.parse_args()

    # Default to next month
    today = date.today()
    if args.month:
        month = args.month
        year = args.year or today.year
    else:
        if today.month == 12:
            month, year = 1, today.year + 1
        else:
            month, year = today.month + 1, today.year

    print(f"Fetching events for {MONTH_NAMES[month]} {year}...")
    events = fetch_events(year, month)
    print(f"Found {len(events)} approved events.")

    if not events:
        print("No events found. Exiting.")
        return

    html = render_newsletter(events, year, month, editorial=args.editorial)

    if args.preview:
        path = f"newsletter_{year}_{month:02d}.html"
        with open(path, "w") as f:
            f.write(html)
        print(f"Preview written to {path}")
    else:
        create_campaign(html, year, month, schedule=not args.no_schedule)


if __name__ == "__main__":
    main()
