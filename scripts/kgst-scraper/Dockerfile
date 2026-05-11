FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p events/logs

# cron runs jobs with a minimal PATH that omits /usr/local/bin, where the
# official python image installs the `python` binary — set PATH explicitly.
RUN printf 'PATH=/usr/local/bin:/usr/bin:/bin\n30 4 * * * root cd /app && python events/scrapers/scrape_kgst.py >> /proc/1/fd/1 2>&1\n' > /etc/cron.d/kgst
RUN chmod 0644 /etc/cron.d/kgst

CMD ["cron", "-f"]
