# Use an official Python runtime as a parent image
FROM python:3.9-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only to save space)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the rest of the application code
COPY . .

# Run the daemon script by default
CMD ["python", "run_daemon.py"]
