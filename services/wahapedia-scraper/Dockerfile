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

# Create requirements.txt with ALL dependencies
RUN echo "beautifulsoup4==4.12.2" > requirements.txt && \
    echo "requests==2.31.0" >> requirements.txt && \
    echo "redis==5.0.1" >> requirements.txt && \
    echo "psycopg2-binary==2.9.9" >> requirements.txt && \
    echo "sqlalchemy==2.0.23" >> requirements.txt && \
    echo "pydantic==2.5.2" >> requirements.txt && \
    echo "pydantic-settings==2.1.0" >> requirements.txt && \
    echo "python-dotenv==1.0.0" >> requirements.txt && \
    echo "lxml==4.9.3" >> requirements.txt && \
    echo "structlog==23.2.0" >> requirements.txt && \
    echo "tenacity==8.2.3" >> requirements.txt && \
    echo "httpx==0.25.2" >> requirements.txt && \
    echo "celery==5.3.4" >> requirements.txt && \
    echo "fastapi==0.104.1" >> requirements.txt && \
    echo "uvicorn==0.24.0" >> requirements.txt && \
    echo "alembic==1.13.0" >> requirements.txt

# Install all Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Create non-root user
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app

USER scraper

CMD ["python", "src/main.py"]
