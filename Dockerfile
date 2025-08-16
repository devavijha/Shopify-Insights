# ShopifyScope Intelligence Platform Container
# Advanced E-commerce Analytics with AI-Driven Business Intelligence

FROM python:3.12-slim-bookworm

# Set metadata for the image
LABEL maintainer="ShopifyScope Intelligence Team"
LABEL version="2.1.0"
LABEL description="Advanced E-commerce Analytics Platform with AI Intelligence"

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r shopifyscope && useradd -r -g shopifyscope shopifyscope

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt ./

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership of the app directory to non-root user
RUN chown -R shopifyscope:shopifyscope /app

# Switch to non-root user
USER shopifyscope

# Expose application port
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)" || exit 1

# Run the ShopifyScope Intelligence Platform
CMD ["python3", "main.py"]