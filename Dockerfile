# Use official Python slim image as base
FROM python:3.12-slim-bookworm

# Set working directory inside container
WORKDIR /app

# Install system dependencies for Pillow and other required libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev && apt-get clean

# Copy requirements.txt into the container and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files into the container
COPY app.py app.py

# Expose port 5000 for Flask app
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
