FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY rcon_client.py .
COPY monitoring_client.py .
COPY docker_monitor.py .
COPY death_messages.py .

CMD ["python", "main.py"]

