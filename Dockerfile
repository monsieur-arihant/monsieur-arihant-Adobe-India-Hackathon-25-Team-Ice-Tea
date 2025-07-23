# Use official Python image
FROM python:3.10-slim

# Set work directory inside the container
WORKDIR /app

# Copy all files from host to container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir pandas scikit-learn PyMuPDF requests

# Create output directory inside container
RUN mkdir -p pdf_dataset

# Run the script
CMD ["python", "src/main.py"]
