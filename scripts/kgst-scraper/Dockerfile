FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p events/logs

RUN echo "30 4 * * * root cd /app && python events/scrapers/scrape_kgst.py >> /proc/1/fd/1 2>&1" > /etc/cron.d/kgst
RUN chmod 0644 /etc/cron.d/kgst

CMD ["cron", "-f"]
