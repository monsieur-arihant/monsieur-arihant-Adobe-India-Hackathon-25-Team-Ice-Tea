# Use official Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Create output directory if it doesn't exist
RUN mkdir -p output pdf_dataset

# Run the main script by default
CMD ["python", "src/main.py"]
