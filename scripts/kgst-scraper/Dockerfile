FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY scripts/kgst-scraper/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p events/logs

# cron runs jobs with a minimal environment (no PATH to /usr/local/bin where
# python lives, and none of the container env vars like DIRECTUS_API_URL).
# entrypoint.sh snapshots the container env into /etc/cron-env at startup,
# which the cron job sources before running the scraper.
RUN printf '30 4 * * * root . /etc/cron-env; cd /app && python events/scrapers/scrape_kgst.py >> /proc/1/fd/1 2>&1\n' > /etc/cron.d/kgst
RUN chmod 0644 /etc/cron.d/kgst

CMD ["/entrypoint.sh"]
