#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Analysis App with Instructor

A streamlined application that processes event data from a Directus database
using GPT-4o Mini with Instructor for structured extraction and validation.
Processes events with automatic date parsing, validation, and relevance determination.
"""
import json
import requests
import argparse
import re
import os
import logging
import time
from datetime import datetime, date
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
import instructor
from dotenv import load_dotenv

# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class TagGroups(BaseModel):
    """Organized tags by category"""
    topic: List[str] = Field(default_factory=list, description="Themen-Tags")
    format: List[str] = Field(default_factory=list, description="Format-Tags (Workshop, Webinar, etc.)")
    audience: List[str] = Field(default_factory=list, description="Zielgruppen-Tags")
    cost: List[str] = Field(default_factory=list, description="Kosten-Tags")


class EventData(BaseModel):
    """Structured event data with validation"""
    title: str = Field(..., min_length=1, max_length=500, description="Titel der Veranstaltung")
    description: str = Field(..., max_length=450, description="Prägnante Beschreibung (max 450 Zeichen)")
    start_date: str = Field(..., description="Startdatum im ISO-Format (YYYY-MM-DD)")
    start_time: Optional[str] = Field(None, description="Startzeit (HH:MM)")
    end_date: Optional[str] = Field(None, description="Enddatum im ISO-Format")
    end_time: Optional[str] = Field(None, description="Endzeit (HH:MM)")
    location: str = Field(..., min_length=1, description="'Online' oder nur der Stadtname (kein Adressdetail)")
    organizer: str = Field(..., min_length=1, description="Veranstalter (Organisation, nicht Einzelperson)")
    speaker: Optional[str] = Field(None, description="Referent*in / Dozent*in / Sprecher*in")
    tags: List[str] = Field(default_factory=list, max_length=5, description="Schlagwörter (max 5)")
    tag_groups: Optional[TagGroups] = Field(None, description="Tags nach Kategorien organisiert")
    cost: str = Field(default="Kostenlos", description="Preisinformationen")
    registration_link: Optional[str] = Field(None, description="URL für Anmeldung")
    relevancy_score: int = Field(..., ge=0, le=100, description="Relevanzwert für Non-Profit digitale Transformation (0-100)")

    # Additional fields added by processor
    source: Optional[str] = Field(None, description="Quelle der Veranstaltung")
    review_status: Optional[str] = Field("pending", description="Freigabestatus: pending, approved, rejected")
    website: Optional[str] = Field(None, description="Event-Website URL")

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate ISO date format (YYYY-MM-DD)"""
        if v is None:
            return v

        # Check if already in ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                pass

        # Try to parse German date formats
        german_formats = [
            (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', '%d.%m.%Y'),  # DD.MM.YYYY
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%d/%m/%Y'),    # DD/MM/YYYY
        ]

        for pattern, format_str in german_formats:
            match = re.match(pattern, v)
            if match:
                try:
                    parsed_date = datetime.strptime(v, format_str)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        # If we can't parse it, raise an error
        raise ValueError(f"Date must be in ISO format (YYYY-MM-DD) or German format (DD.MM.YYYY). Got: {v}")

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format (HH:MM)"""
        if v is None:
            return v

        # Check if in HH:MM format
        if re.match(r'^\d{1,2}:\d{2}$', v):
            parts = v.split(':')
            hour = int(parts[0])
            minute = int(parts[1])

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"

        raise ValueError(f"Time must be in HH:MM format. Got: {v}")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and clean tags"""
        if len(v) > 5:
            # Truncate to 5 tags if too many
            v = v[:5]

        # Clean and validate each tag
        cleaned_tags = []
        for tag in v:
            tag = tag.strip()
            if tag:  # Only add non-empty tags
                cleaned_tags.append(tag)

        return cleaned_tags

    @model_validator(mode='after')
    def validate_dates_consistency(self):
        """Ensure end_date is not before start_date"""
        if self.start_date and self.end_date:
            try:
                start = datetime.strptime(self.start_date, '%Y-%m-%d')
                end = datetime.strptime(self.end_date, '%Y-%m-%d')

                if end < start:
                    raise ValueError(f"End date ({self.end_date}) cannot be before start date ({self.start_date})")
            except ValueError as e:
                if "End date" in str(e):
                    raise
                # If date parsing fails, it will be caught by field validators
                pass

        return self

# ============================================================================

# Set up logging - only log to file, not console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("events/logs/llm_extraction.log")
    ]
)
logger = logging.getLogger("event_extraction")

# Load environment variables from .env file
load_dotenv()

# Configuration
DIRECTUS_URL = os.getenv("DIRECTUS_API_URL", "https://calapi.buerofalk.de")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_API_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Validate required environment variables
if not DIRECTUS_TOKEN:
    raise ValueError("DIRECTUS_API_TOKEN environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

class DirectusClient:
    """Client for Directus API interactions - managing scraped data and events"""
    
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_unprocessed_items(self, limit=10):
        """Get unprocessed items from scraped_data collection"""
        # Use Directus filter to get only unprocessed items directly
        url = f"{self.base_url}/items/scraped_data?filter[processed][_eq]=false&sort=-id&limit={limit}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        items = response.json().get('data', [])

        print(f"Retrieved {len(items)} unprocessed items")
        return items
    
    def update_item_status(self, item_id, success=True, processed_content=None):
        """Update item status in Directus with retry and exponential backoff"""
        update_data = {
            "processed": True,
            "processed_at": datetime.now().isoformat(),
            "processing_status": "processed" if success else "failed"
        }

        if processed_content:
            update_data["processed_content"] = processed_content

        url = f"{self.base_url}/items/scraped_data/{item_id}"

        max_retries = 3
        for attempt in range(max_retries):
            if attempt > 0:
                delay = 2 ** attempt  # 2s, 4s
                print(f"  Retry {attempt}/{max_retries - 1} for item {item_id} (HTTP {response.status_code}), waiting {delay}s...")
                time.sleep(delay)
            response = requests.patch(url, headers=self.headers, json=update_data)
            if response.status_code in (200, 204):
                return
            if response.status_code in (403, 429) or response.status_code >= 500:
                continue
            response.raise_for_status()

        # Final attempt failed — raise so callers can handle it
        response.raise_for_status()
    
    def save_event(self, event_data):
        """Save processed event to events collection"""
        # Check if event already exists
        filter_params = {
            "filter": {
                "_and": [
                    {"title": {"_eq": event_data.get("title", "")}},
                    {"start_date": {"_eq": event_data.get("start_date", "")}}
                ]
            }
        }
        
        # Convert filter to query string
        filter_json = json.dumps(filter_params["filter"])
        encoded_filter = f"filter={requests.utils.quote(filter_json)}"
        
        # Check for duplicates
        check_url = f"{self.base_url}/items/events?{encoded_filter}"
        check_response = requests.get(check_url, headers=self.headers)
        
        if check_response.status_code == 200:
            existing = check_response.json().get("data", [])
            if existing:
                return False, "duplicate"

        # Add the event (with delay to avoid rate limiting)
        time.sleep(0.5)
        response = requests.post(f"{self.base_url}/items/events", headers=self.headers, json=event_data)
        
        if response.status_code in (200, 201, 204):
            return True, "created"
        else:
            return False, f"Error: {response.status_code}"


class GPT4MiniProcessor:
    """Processes event data with GPT-4o Mini using Instructor for structured extraction"""

    def __init__(self, api_key, directus_client):
        # Wrap OpenAI client with Instructor for structured output with validation
        self.client = instructor.from_openai(OpenAI(api_key=api_key))
        self.directus = directus_client
        
    def process_event(self, event_data):
        """Process a single event with GPT-4o Mini and enhanced extraction"""
        # Extract raw content
        raw_content = event_data.get('raw_content', '{}')
        if isinstance(raw_content, str):
            try:
                content = json.loads(raw_content)
            except json.JSONDecodeError:
                content = {"text": raw_content}
        else:
            content = raw_content
        
        # Build prompt for LLM extraction
        prompt = self._build_prompt(content)
        
        try:
            # Get item ID for logging
            item_id_str = event_data.get('id', 'unknown')
            
            # Log the prompt being sent to the LLM
            system_prompt = "Extract structured information from German event descriptions with focus on dates, times, and links. Provide a relevancy score (0-100) based on how well the event matches the Non-Profit digital transformation use case."
            
            logger.info(f"\n--- LLM INPUT for item {item_id_str} ---\nSYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{prompt}\n--- END LLM INPUT ---")

            # Call GPT-4o Mini with Instructor for structured output and automatic validation
            event = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=EventData,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_retries=3  # Instructor will automatically retry on validation errors
            )

            # The event is already a validated Pydantic model, convert to dict
            structured_data = event.model_dump(exclude_none=True)

            # Log the validated response
            logger.info(f"\n--- VALIDATED RESPONSE for item {item_id_str} ---\n{json.dumps(structured_data, indent=2, ensure_ascii=False)}\n--- END VALIDATED RESPONSE ---")

            # Log the extracted date information
            date_log = f"""
Date extraction for item {item_id_str}:
Title: {structured_data.get('title', 'Unknown')}

VALIDATED EXTRACTION:
  start_date: {structured_data.get('start_date', 'Not found')}
  end_date: {structured_data.get('end_date', 'Not found')}
  start_time: {structured_data.get('start_time', 'Not found')}
  end_time: {structured_data.get('end_time', 'Not found')}
"""
            logger.info(date_log)
            
            # Combine date + time into ISO datetime strings for Directus
            # (Directus has no separate start_time/end_time fields)
            start_date = structured_data.get('start_date', '')
            start_time = structured_data.get('start_time')
            end_date = structured_data.get('end_date')
            end_time = structured_data.get('end_time')

            # Merge start_time into start_date
            if start_date:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', start_date)
                if date_match:
                    date_part = date_match.group(1)
                    if start_time:
                        time_match = re.search(r'(\d{1,2}):(\d{2})', start_time)
                        if time_match:
                            h, m = time_match.groups()
                            structured_data['start_date'] = f"{date_part}T{h.zfill(2)}:{m}:00"
                    else:
                        # No time extracted — keep date-only so Directus stores T00:00:00
                        structured_data['start_date'] = date_part

            # Merge end_time into end_date (use start_date's date if end_date is missing)
            if end_time:
                time_match = re.search(r'(\d{1,2}):(\d{2})', end_time)
                if time_match:
                    h, m = time_match.groups()
                    time_str = f"{h.zfill(2)}:{m}:00"
                    if end_date:
                        ed_match = re.search(r'(\d{4}-\d{2}-\d{2})', end_date)
                        if ed_match:
                            structured_data['end_date'] = f"{ed_match.group(1)}T{time_str}"
                    elif start_date:
                        # Same-day event: use start_date's date part
                        sd_match = re.search(r'(\d{4}-\d{2}-\d{2})', start_date)
                        if sd_match:
                            structured_data['end_date'] = f"{sd_match.group(1)}T{time_str}"
            elif end_date:
                # end_date exists but no end_time — keep date-only
                ed_match = re.search(r'(\d{4}-\d{2}-\d{2})', end_date)
                if ed_match:
                    structured_data['end_date'] = ed_match.group(1)

            # Remove separate time fields (Directus doesn't have them)
            structured_data.pop('start_time', None)
            structured_data.pop('end_time', None)

            # Add metadata
            structured_data["source"] = content.get("source_name", event_data.get("source_name", "Unknown"))
            if event_data.get("auto_approve"):
                structured_data["review_status"] = "approved"
                structured_data["status"] = "auto-published"
            else:
                structured_data["review_status"] = "pending"
            
            # Add URL if available
            if content.get("url") and not structured_data.get("website"):
                structured_data["website"] = content.get("url")

            # Add token usage info
            # Note: Instructor wraps the response, so we need to access the raw response
            # For now, we'll provide a default token usage since Instructor doesn't expose it directly
            # The token tracking is primarily for monitoring, not critical for functionality
            token_usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }

            # Try to get token usage from the raw response if available
            try:
                if hasattr(event, '_raw_response') and hasattr(event._raw_response, 'usage'):
                    token_usage = {
                        "prompt_tokens": event._raw_response.usage.prompt_tokens,
                        "completion_tokens": event._raw_response.usage.completion_tokens,
                        "total_tokens": event._raw_response.usage.total_tokens
                    }
            except AttributeError:
                # If we can't access token usage, continue with defaults
                pass

            return structured_data, token_usage
            
        except Exception as e:
            print(f"Error processing with GPT: {str(e)}")
            return None, {"total_tokens": 0}
    
    # Cache for prompt templates to avoid rebuilding them each time
    _prompt_template = """\
Extrahiere strukturierte Veranstaltungsdaten aus folgenden Rohdaten.

{raw_content}

--- REGELN ---

DESCRIPTION (max 450 Zeichen):
Starte DIREKT mit dem inhaltlichen Kern. NICHT wiederholen: Titel, Veranstalter, Format, Datum, Ort.
Schlecht: "In diesem Webinar der Bitkom Akademie lernen Sie..."
Gut: "Grundlagen der KI-gestützten Textgenerierung für Öffentlichkeitsarbeit..."

ORGANIZER vs. SPEAKER:
- organizer = IMMER eine Organisation (Verband, Stiftung, Akademie), NIE eine Person
- speaker = Referent*in, Dozent*in, Trainer*in (Personennamen)
- Labels wie "Kontakt:", "Ansprechpartner*in:", "Referent*in:" → speaker, NICHT organizer
- Keine Organisation im Text → aus der URL/Webseite ableiten (Domain-Name als Fallback)
- NIE "Unbekannt", "null" oder "email-submit" als organizer

TAGS (max 5, in tag_groups einordnen):
- Allgemein und wiederverwendbar, nicht zu spezifisch
- Akronyme: "KI" (nicht "Künstliche Intelligenz"), "DSGVO", "NGO"
- Title Case: "Machine Learning", "Social Media"
- "Online" als Tag bei virtuellen Events (zusätzlich zum Format-Tag)
- "Kostenlos" als Tag wenn kostenlos

LOCATION:
- "Online" bei virtuellen/digitalen Events
- Bei Präsenz-Events NUR den Stadtnamen (z.B. "Berlin", "Frankfurt am Main"), KEINE Adresse/Straße/Gebäude

DATUM/ZEIT:
- Format: YYYY-MM-DD / HH:MM. Europäisch: DD.MM.YYYY
- "Beginn"/"Start" vor "Einlass"/"Türöffnung" priorisieren
- Fehlendes Jahr → aktuelles Jahr wenn Datum in Zukunft
- Vage Zeiten: Vormittag→10:00, Mittag→12:00, Nachmittag→14:00, Abend→19:00, Ganztägig→09:00-17:00

RELEVANCY_SCORE (0-100) — DIGITALISIERUNGS-Kalender für NPOs:
Primärfrage: Hat die Veranstaltung DIGITALEN/TECHNISCHEN Bezug?

75-100: Digitale Themen + NPO-Bezug (KI für Vereine, Datenschutz für Stiftungen, Social Media für NPOs)
50-74:  Digitale Themen ohne NPO-Bezug (Prompt Engineering, IT-Sicherheit, E-Rechnung)
20-49:  Kein digitaler Bezug (Fundraising-Strategie, Inklusion, Sozialpolitik, interne Sitzungen)
0-19:   Weder digital noch NPO-relevant

Kosten sind KEIN Ausschlusskriterium. Im Zweifel: digital > NPO.

Nutze null für unbekannte Felder."""
    
    def _build_prompt(self, content):
        """Build prompt with full raw content for LLM extraction"""
        # Truncate very long text fields to manage token usage
        content_copy = dict(content)
        for key in ('listing_text', 'detail_text', 'description'):
            if key in content_copy and isinstance(content_copy[key], str) and len(content_copy[key]) > 5000:
                content_copy[key] = content_copy[key][:5000] + "..."

        raw_content = json.dumps(content_copy, indent=2, ensure_ascii=False, default=str)

        return self._prompt_template.format(raw_content=raw_content)

def process_events(limit=10, batch_size=3):
    """Main processing function for event extraction and analysis"""
    # Initialize clients
    directus = DirectusClient(DIRECTUS_URL, DIRECTUS_TOKEN)

    # Initialize processor
    gpt = GPT4MiniProcessor(OPENAI_API_KEY, directus)
    
    # Get unprocessed items
    items = directus.get_unprocessed_items(limit)
    
    if not items:
        print("No unprocessed items found")
        return
    
    # Process statistics
    processed = 0
    duplicates = 0
    errors = 0
    skipped_past = 0
    total_tokens = 0
    today_str = date.today().isoformat()
    
    # OPTIMIZATION 4: Process in smaller batches for better memory usage
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} items)")
        
        batch_results = []  # Store batch results to reduce API calls
        
        for item in batch:
            item_id = item.get('id')
            
            # Process with GPT
            structured_data, token_usage = gpt.process_event(item)
            total_tokens += token_usage["total_tokens"]
            
            if not structured_data:
                print(f"Failed to process item {item_id}")
                try:
                    directus.update_item_status(item_id, success=False)
                except requests.exceptions.HTTPError as e:
                    print(f"Warning: Could not update item status in DB: {e}")
                errors += 1
                continue
            
            # Add to batch results
            batch_results.append({
                'item_id': item_id,
                'structured_data': structured_data
            })
        
        # OPTIMIZATION 5: Process batch results together
        for result in batch_results:
            item_id = result['item_id']
            structured_data = result['structured_data']

            # Format event information for console output
            title = structured_data.get('title', 'Unknown')
            start_date = structured_data.get('start_date', 'No date')
            date_display = start_date[:10] if start_date and len(start_date) > 10 else start_date

            # Skip past events: mark as processed but don't save to events collection
            if start_date and start_date[:10] < today_str:
                skipped_past += 1
                print(f"⏭ Skipped (past event): {title} | {date_display}")
                try:
                    directus.update_item_status(item_id, success=True)
                except requests.exceptions.HTTPError as e:
                    print(f"Warning: Could not update item {item_id} status in DB: {e}")
                time.sleep(0.3)
                continue

            # Save all events to Directus, but mark them as pending approval
            structured_data["review_status"] = "pending"  # Pending approval

            # Save to events collection
            success, status = directus.save_event(structured_data)

            relevancy_score = structured_data.get('relevancy_score', 0)

            # Print a single, well-formatted line for each event
            if success:
                processed += 1
                print(f"✓ {title} | {date_display} | Score: {relevancy_score}/100")
            elif status == "duplicate":
                duplicates += 1
                print(f"↺ Duplicate: {title}")
            else:
                errors += 1
                print(f"✗ Error: {title} - {status}")

            # Update item status (no processed_content — Directus token lacks write permission to that field)
            try:
                directus.update_item_status(item_id, success=True)
            except requests.exceptions.HTTPError as e:
                print(f"Warning: Could not update item {item_id} status in DB: {e}")

            time.sleep(0.3)
    
    # Calculate cost (approx. $0.15 per 1M tokens)
    cost = (total_tokens / 1_000_000) * 0.15
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Processed: {processed}")
    print(f"Skipped (past): {skipped_past}")
    print(f"Duplicates: {duplicates}")
    print(f"Errors: {errors}")
    print(f"Total tokens: {total_tokens}")
    print(f"Estimated cost: ${cost:.4f}")

def mark_old_items(before_date, dry_run=False):
    """Bulk-mark old unprocessed scraped_data items as processed without LLM extraction.

    Fetches all unprocessed items and filters locally by date_created (since the
    Directus token may not permit filtering on system fields). Items created before
    `before_date` are marked as processed so they stop cycling through the pipeline.
    """
    directus = DirectusClient(DIRECTUS_URL, DIRECTUS_TOKEN)

    # Fetch all unprocessed items, paginated
    all_items = []
    page = 1
    page_size = 100
    while True:
        url = (
            f"{directus.base_url}/items/scraped_data"
            f"?filter[processed][_eq]=false"
            f"&sort=id"
            f"&limit={page_size}"
            f"&page={page}"
        )
        response = requests.get(url, headers=directus.headers)
        response.raise_for_status()
        batch = response.json().get("data", [])
        if not batch:
            break
        all_items.extend(batch)
        page += 1

    # Filter locally by date_created
    old_items = [
        item for item in all_items
        if (item.get("date_created") or "") < before_date
    ]

    print(f"Found {len(all_items)} total unprocessed items, {len(old_items)} created before {before_date}")

    if dry_run:
        print("Dry run — no changes made.")
        return

    marked = 0
    failed = 0
    for item in old_items:
        item_id = item["id"]
        try:
            directus.update_item_status(item_id, success=True)
            marked += 1
            if marked % 25 == 0:
                print(f"  Marked {marked}/{len(old_items)}...")
        except requests.exceptions.HTTPError as e:
            print(f"  Failed to mark item {item_id}: {e}")
            failed += 1
        time.sleep(0.3)  # Rate-limit-safe pacing

    print(f"\nDone: marked {marked}, failed {failed}")


def main():
    parser = argparse.ArgumentParser(description="Process events with structured extraction using Instructor")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum number of items to process")
    parser.add_argument("--batch", "-b", type=int, default=3, help="Batch size for processing")
    parser.add_argument("--log-file", default="events/logs/llm_extraction.log", help="Path to log file for LLM extraction results")
    parser.add_argument("--mark-old", nargs="?", const="auto", metavar="DATE",
                        help="Bulk-mark old unprocessed items as processed (default: items older than 30 days). Accepts YYYY-MM-DD.")
    parser.add_argument("--dry-run", action="store_true", help="Preview --mark-old without making changes")

    args = parser.parse_args()

    # Handle --mark-old mode
    if args.mark_old is not None:
        if args.mark_old == "auto":
            from datetime import timedelta
            before_date = (date.today() - timedelta(days=30)).isoformat()
        else:
            before_date = args.mark_old
        mark_old_items(before_date, dry_run=args.dry_run)
        return

    # Configure log file if specified
    if args.log_file != "llm_extraction.log":
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)

        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    logger.info(f"Starting event processing with limit={args.limit}, batch_size={args.batch}")

    # Process events
    process_events(limit=args.limit, batch_size=args.batch)

if __name__ == "__main__":
    main()
