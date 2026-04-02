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

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; DigiKal/1.0; +https://www.digikal.org)'
}

# Trusted sender domains/addresses — events from these get auto-approved
TRUSTED_SENDERS = {
    'buergermut.de',
}


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


def is_trusted_sender(from_header):
    """Check if the sender is a trusted source for auto-approval."""
    raw = decode_mime_header(from_header)
    email_match = re.search(r'[\w.-]+@([\w.-]+)', raw)
    if not email_match:
        return False
    domain = email_match.group(1).lower()
    return any(domain == d or domain.endswith('.' + d) for d in TRUSTED_SENDERS)


def scrape_url(url):
    """Fetch a URL and extract text content."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script/style elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # Try common content selectors first
        content = None
        for selector in ['main', 'article', '[role="main"]', '.content', '.entry-content']:
            el = soup.select_one(selector)
            if el:
                content = el.get_text(separator='\n', strip=True)
                break

        if not content:
            content = soup.get_text(separator='\n', strip=True)

        # Truncate very long content
        if len(content) > 10000:
            content = content[:10000] + '...'

        return content
    except Exception as e:
        logger.error(f'Failed to scrape {url}: {e}')
        return None


def create_scraped_entry(url, raw_content, source_name, trusted=False):
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

    data = {
        'url': url,
        'source_name': 'email-submit',
        'content_hash': content_hash,
        'auto_approve': trusted,
        'raw_content': json.dumps({
            'url': url,
            'source_name': source_name,
            'detail_text': raw_content,
            'submitted_via': 'email',
        }, ensure_ascii=False),
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
        body = get_email_body(msg)
        urls = extract_urls(body)

        logger.info(f'Email from {source_name}: "{subject}" — {len(urls)} URL(s) found{" [TRUSTED]" if trusted else ""}')

        for url in urls:
            if dry_run:
                logger.info(f'  [DRY RUN] Would scrape and create entry for: {url}')
            else:
                try:
                    raw_content = scrape_url(url)
                    if not raw_content:
                        logger.warning(f'  No content scraped from: {url}')
                        continue
                    item_id = create_scraped_entry(url, raw_content, source_name, trusted=trusted)
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
