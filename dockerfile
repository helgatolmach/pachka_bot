FROM python:3.11-slim

# Set timezone if needed
ENV TZ=UTC

# Install cron and bash
RUN apt-get update && apt-get install -y cron bash && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app files
COPY . /app
WORKDIR /app

# Ensure log file exists
RUN touch /var/log/cron.log

# Set up cron to run every minute (for testing)
# Important: cron uses SHELL=/bin/bash so ENV are visible
RUN echo "* * * * * root /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron && crontab /etc/cron.d/mycron

# Start cron in foreground
CMD ["cron", "-f"]