FROM python:3.11-slim

# Set timezone if needed
ENV TZ=UTC

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app
WORKDIR /app

# Copy crontab
COPY mycron /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron && crontab /etc/cron.d/mycron

# Ensure log file exists
RUN touch /var/log/cron.log

# Start cron in foreground
CMD ["cron", "-f"]