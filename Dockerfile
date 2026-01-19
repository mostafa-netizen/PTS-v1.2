# Use a small Python image for the web API and OCR pipeline
FROM python:3.11-slim

# Avoid interactive apt prompts
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies:
# - poppler-utils: required by pdf2image to convert PDFs to images
RUN apt-get update \
 && apt-get install -y --no-install-recommends poppler-utils \
 && rm -rf /var/lib/apt/lists/*

# All app files will live under /app inside the container
WORKDIR /app

# Install Python dependencies from your existing requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project (server.py, config.py, index.html, etc.)
COPY . /app

# Flask server in config.py listens on port 3000
EXPOSE 3000

# Start your Flask server with unbuffered output for better logging
CMD ["python", "-u", "server.py"]

