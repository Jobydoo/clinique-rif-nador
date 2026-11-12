# Dockerfile for Clinique Médico-Chirurgicale du Rif - Nador
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for reportlab, pillow, and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Seed initial database if not existing
RUN python seed_data.py

# Expose port
EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run with Gunicorn production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "2", "run:app"]
