# Python 3.13+ required by audioop-lts (Chainlit / deps)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY . .

# Cloud Run startup: bind PORT env + PYTHONPATH so `agents` / `constants` resolve
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]