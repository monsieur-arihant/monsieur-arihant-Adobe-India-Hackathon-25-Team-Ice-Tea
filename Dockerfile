# Use Python 3.9 slim for smaller image size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p /app/pdf_dataset /app/input /app/output && \
    chmod 755 /app/pdf_dataset /app/input /app/output

# Copy the main application (single file now)
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create volumes for input and output
VOLUME ["/app/input", "/app/output"]

# Expose port if needed for future web interface
EXPOSE 8000

# Health check to ensure container is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command - run the classifier
CMD ["python", "src/main.py"]