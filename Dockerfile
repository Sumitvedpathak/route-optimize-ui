# Use Python 3.11 or 3.12
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY . .

# Chainlit runs on port 8080 by default in Cloud Run
EXPOSE 8080

# Command to run Chainlit in production mode
CMD ["chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "8080"]