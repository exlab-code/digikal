#!/usr/bin/env python3
"""
Email submission poller for DigiKal.

Checks the eintragen@digikal.org inbox via IMAP, extracts URLs from emails,
scrapes each URL, and creates scraped_data entries in Directus for the
existing LLM extraction pipeline to process.

Usage:
    python email_submit.py          # Process new emails once
    python email_submit.py --dry    # Preview without scraping/creating entries

Env vars (in .env):
    SUBMIT_IMAP_HOST     - IMAP server hostname
    SUBMIT_IMAP_USER     - Email address / login
    SUBMIT_IMAP_PASSWORD - Email password
"""
import imaplib
import email
from email.header import decode_header
import re
import json
import hashlib
import os
import sys
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.page_scraper import scrape_url

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Config
IMAP_HOST = os.getenv('SUBMIT_IMAP_HOST', '')
IMAP_USER = os.getenv('SUBMIT_IMAP_USER', 'eintragen@digikal.org')
IMAP_PASSWORD = os.getenv('SUBMIT_IMAP_PASSWORD', '')

DIRECTUS_URL = os.getenv('DIRECTUS_API_URL', '')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_API_TOKEN', '')
COLLECTION = 'scraped_data'

# URL pattern — match http/https links
URL_PATTERN = re.compile(r'https?://[^\s<>"\')\]]+')

# Domains to ignore (tracking pixels, email footers, etc.)
IGNORE_DOMAINS = {
    'mailto:', 'unsubscribe', 'list-manage.com', 'mailchimp.com',
    'google.com/maps', 'fonts.googleapis.com', 'schema.org',
    'w3.org', 'facebook.com/tr', 'doubleclick.net',
}

# Trusted sender domains → hardcoded organizer name.
# Needed when the submitted URL is a booking/platform page (e.g. pretix.eu)
# where the scraped content carries the platform's branding rather than the
# real organizer, causing the downstream LLM to guess "pretix" etc.
# Events from these senders also get auto-approved.
TRUSTED_ORGANIZERS = {
    'buergermut.de': 'Stiftung Bürgermut',
}
TRUSTED_SENDERS = set(TRUSTED_ORGANIZERS.keys())


def decode_mime_header(raw):
    """Decode a MIME-encoded header value."""
    parts = decode_header(raw or '')
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or 'utf-8', errors='replace'))
        else:
            decoded.append(part)
    return ' '.join(decoded)


def get_email_body(msg):
    """Extract plain text body from an email message."""
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                charset = part.get_content_charset() or 'utf-8'
                body += part.get_payload(decode=True).decode(charset, errors='replace')
            elif content_type == 'text/html' and not body:
                charset = part.get_content_charset() or 'utf-8'
                html = part.get_payload(decode=True).decode(charset, errors='replace')
                body += html
    else:
        charset = msg.get_content_charset() or 'utf-8'
        body = msg.get_payload(decode=True).decode(charset, errors='replace')
    return body


FORWARD_BODY_MARKERS = re.compile(
    r'^[\s>]*(?:'
    r'-{3,}\s*Forwarded message\s*-{3,}|'
    r'-{3,}\s*Weitergeleitete Nachricht\s*-{3,}|'
    r'Begin forwarded message:'
    r')',
    re.IGNORECASE | re.MULTILINE
)

FORWARD_SUBJECT_PREFIX = re.compile(r'^\s*(?:Fwd?|WG)\s*:', re.IGNORECASE)


def detect_forwarded(subject, body):
    """Detect if an email is a forward.

    Returns (is_forwarded, inner_body). If a body marker is present, inner_body
    is the content after the marker so the forwarder's own sign-off doesn't
    truncate URL extraction downstream.
    """
    match = FORWARD_BODY_MARKERS.search(body)
    if match:
        return True, body[match.end():]
    if FORWARD_SUBJECT_PREFIX.match(subject or ''):
        return True, body
    return False, body


SIGNATURE_MARKERS = re.compile(
    r'^[\s]*(?:'
    r'-[\s-]*-|'
    r'___+|'
    r'Mit freundlichen Grüßen|'
    r'Viele Grüße|'
    r'Beste Grüße|'
    r'Freundliche Grüße|'
    r'Herzliche Grüße|'
    r'Liebe Grüße|'
    r'MfG|'
    r'Best regards|'
    r'Kind regards|'
    r'Cheers|'
    r'Gesendet von meinem iPhone|'
    r'Sent from my'
    r')',
    re.IGNORECASE | re.MULTILINE
)


def extract_urls(text):
    """Extract and filter URLs from text, ignoring signatures."""
    # Strip signature before extracting URLs
    match = SIGNATURE_MARKERS.search(text)
    if match:
        text = text[:match.start()]
    urls = URL_PATTERN.findall(text)
    filtered = []
    seen = set()
    for url in urls:
        # Clean trailing punctuation
        url = url.rstrip('.,;:!?)>]')
        # Skip ignored domains
        if any(domain in url.lower() for domain in IGNORE_DOMAINS):
            continue
        # Deduplicate
        if url not in seen:
            seen.add(url)
            filtered.append(url)
    return filtered


def sender_to_source(from_header):
    """Derive a source name from the sender email/name."""
    name = decode_mime_header(from_header)
    # Try to extract just the display name
    match = re.match(r'^(.+?)\s*<', name)
    if match:
        return match.group(1).strip().strip('"')
    # Fall back to email address prefix
    match = re.match(r'([^@]+)@', name)
    if match:
        return match.group(1).strip()
    return 'email-submit'


def _sender_domain(from_header):
    raw = decode_mime_header(from_header)
    email_match = re.search(r'[\w.-]+@([\w.-]+)', raw)
    return email_match.group(1).lower() if email_match else None


def is_trusted_sender(from_header):
    """Check if the sender is a trusted source for auto-approval."""
    domain = _sender_domain(from_header)
    if not domain:
        return False
    return any(domain == d or domain.endswith('.' + d) for d in TRUSTED_SENDERS)


def trusted_organizer(from_header):
    """Return the hardcoded organizer name for a trusted sender, or None."""
    domain = _sender_domain(from_header)
    if not domain:
        return None
    for trusted_domain, organizer in TRUSTED_ORGANIZERS.items():
        if domain == trusted_domain or domain.endswith('.' + trusted_domain):
            return organizer
    return None


def create_scraped_entry(url, raw_content, source_name, trusted=False, organizer_override=None):
    """Create a scraped_data entry in Directus with scraped page content."""
    content_hash = hashlib.md5(raw_content.encode()).hexdigest()

    # Check if this content already exists
    check_response = requests.get(
        f'{DIRECTUS_URL}/items/{COLLECTION}',
        headers={'Authorization': f'Bearer {DIRECTUS_TOKEN}'},
        params={'filter[content_hash][_eq]': content_hash, 'limit': 1}
    )
    if check_response.ok:
        existing = check_response.json().get('data', [])
        if existing:
            logger.info(f'  Skipped (duplicate): {url}')
            return None

    payload = {
        'url': url,
        'source_name': source_name,
        'detail_text': raw_content,
        'submitted_via': 'email',
    }
    if organizer_override:
        # Picked up in event_analyzer.py to overwrite the LLM-inferred organizer.
        payload['organizer_override'] = organizer_override

    data = {
        'url': url,
        'source_name': 'email-submit',
        'content_hash': content_hash,
        'auto_approve': trusted,
        'raw_content': json.dumps(payload, ensure_ascii=False),
        'scraped_at': datetime.now().isoformat(),
        'processed': False,
        'processing_status': 'pending'
    }

    response = requests.post(
        f'{DIRECTUS_URL}/items/{COLLECTION}',
        headers={
            'Authorization': f'Bearer {DIRECTUS_TOKEN}',
            'Content-Type': 'application/json'
        },
        json=data
    )
    response.raise_for_status()
    item = response.json().get('data', {})
    return item.get('id')


def process_inbox(dry_run=False):
    """Connect to IMAP, read unseen emails, extract URLs, scrape and create entries."""
    if not all([IMAP_HOST, IMAP_USER, IMAP_PASSWORD]):
        logger.error('Missing IMAP credentials. Set SUBMIT_IMAP_HOST, SUBMIT_IMAP_USER, SUBMIT_IMAP_PASSWORD in .env')
        sys.exit(1)

    if not dry_run and not all([DIRECTUS_URL, DIRECTUS_TOKEN]):
        logger.error('Missing Directus credentials. Set DIRECTUS_API_URL, DIRECTUS_API_TOKEN in .env')
        sys.exit(1)

    # Connect to IMAP
    logger.info(f'Connecting to {IMAP_HOST} as {IMAP_USER}...')
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    mail.select('INBOX')

    # Search for unseen emails
    status, data = mail.search(None, 'UNSEEN')
    if status != 'OK' or not data[0]:
        logger.info('No new emails.')
        mail.logout()
        return

    message_ids = data[0].split()
    logger.info(f'Found {len(message_ids)} new email(s).')

    total_urls = 0

    for msg_id in message_ids:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_mime_header(msg.get('Subject', ''))
        sender = msg.get('From', '')
        source_name = sender_to_source(sender)
        trusted = is_trusted_sender(sender)
        organizer_override = trusted_organizer(sender)
        body = get_email_body(msg)
        is_forwarded, inner_body = detect_forwarded(subject, body)
        urls = extract_urls(inner_body)

        # Forwarded trusted submissions keep auto-approval, but drop the
        # organizer override — the trusted sender is the courier, not the
        # actual organizer. Let the downstream LLM infer the organizer from
        # the scraped page.
        if is_forwarded:
            organizer_override = None

        if trusted and is_forwarded:
            trust_tag = ' [TRUSTED, FORWARDED]'
        elif trusted and organizer_override:
            trust_tag = f' [TRUSTED → {organizer_override}]'
        elif trusted:
            trust_tag = ' [TRUSTED]'
        elif is_forwarded:
            trust_tag = ' [FORWARDED]'
        else:
            trust_tag = ''
        logger.info(f'Email from {source_name}: "{subject}" — {len(urls)} URL(s) found{trust_tag}')

        for url in urls:
            if dry_run:
                logger.info(f'  [DRY RUN] Would scrape and create entry for: {url}')
            else:
                try:
                    raw_content = scrape_url(url)
                    if not raw_content:
                        logger.warning(f'  No content scraped from: {url}')
                        continue
                    item_id = create_scraped_entry(
                        url, raw_content, source_name,
                        trusted=trusted, organizer_override=organizer_override,
                    )
                    if item_id:
                        logger.info(f'  Created scraped_data #{item_id} for: {url}')
                        total_urls += 1
                except Exception as e:
                    logger.error(f'  Failed to process {url}: {e}')

        if not urls:
            logger.warning(f'  No URLs found in email from {source_name}')

    mail.logout()
    logger.info(f'Done. Created {total_urls} entries from {len(message_ids)} email(s).')


if __name__ == '__main__':
    dry_run = '--dry' in sys.argv
    process_inbox(dry_run=dry_run)
