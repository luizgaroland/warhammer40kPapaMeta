FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install Python packages
RUN pip install --no-cache-dir \
    beautifulsoup4==4.12.2 \
    requests==2.31.0 \
    redis==5.0.1 \
    psycopg2-binary==2.9.9 \
    sqlalchemy==2.0.23 \
    pydantic==2.5.2 \
    python-dotenv==1.0.0 \
    lxml==4.9.3

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Create non-root user
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app

USER scraper

# Use different ways to run the module
CMD ["python", "src/main.py"]
