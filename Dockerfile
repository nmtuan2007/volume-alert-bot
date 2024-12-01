# Use Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Ensure the script is in the Python path
ENV PYTHONPATH=/app

# Create directory for logs
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Set non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the application
WORKDIR /app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 "main:app"