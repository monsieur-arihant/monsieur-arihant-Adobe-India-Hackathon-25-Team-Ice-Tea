FROM python:3.9

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific index
RUN pip install --no-cache-dir --index-url https://pypi.org/simple/ -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/pdf_dataset /app/input /app/output

# Copy the main application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create volumes for input and output
VOLUME ["/app/input", "/app/output"]

# Default command
CMD ["python", "src/main.py"]