# Use Python 3.9 slim for smaller image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code from src folder
COPY . .

# Create directories
RUN mkdir -p /app/input /app/output /app/pdf_dataset

# Create non-root user
RUN useradd -m -u 1000 pdfuser && chown -R pdfuser:pdfuser /app
USER pdfuser

# Set environment
ENV PYTHONUNBUFFERED=1

# Mount points
VOLUME ["/app/input", "/app/output"]

# Run the application
CMD ["python", "src/main.py"]