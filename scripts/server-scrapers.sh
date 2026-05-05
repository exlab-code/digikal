#!/usr/bin/env bash
# Run scrapers that can't run on GitHub Actions (blocked IPs).
# Deployed on Coolify server, triggered by system cron.
#
# One-time setup on server:
#   git clone https://github.com/exlab-code/digikal /opt/digikal
#   cd /opt/digikal && python3 -m venv venv && venv/bin/pip install -r requirements.txt
#   cp .env.example .env  # then fill in DIRECTUS_API_URL + DIRECTUS_API_TOKEN
#   chmod +x scripts/server-scrapers.sh
#
# Add to crontab (crontab -e) — runs at 04:30 UTC daily, after GHA at 03:00:
#   30 4 * * * /opt/digikal/scripts/server-scrapers.sh >> /var/log/digikal-scrapers.log 2>&1

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo "=== $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="

# Pull latest scraper code
git pull --quiet

# Run scrapers that are blocked on GitHub Actions
"$REPO_DIR/venv/bin/python" events/scrapers/scrape_kgst.py

echo "=== done ==="
