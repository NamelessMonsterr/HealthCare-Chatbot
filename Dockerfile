# Use official slim Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a Python virtual environment
RUN python3 -m venv /opt/venv

# Update PATH environment variable to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install Python dependencies inside the venv
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code to container
COPY . .

# Download necessary NLTK data for your app
RUN python -m nltk.downloader punkt wordnet stopwords

# Create log and upload directories if your app uses them
RUN mkdir -p logs static/uploads

# Expose the Flask port
EXPOSE 5000

# Health check endpoint for container orchestrators
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:5000/health || exit 1

# Command to run the app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
