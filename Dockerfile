# Base image with Python
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies required by PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libopenjp2-7 \
    libpoppler-cpp-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip install --no-cache-dir pandas scikit-learn PyMuPDF requests

# Copy the full project into the container
COPY . /app

# Set the default command to run your script
CMD ["python", "src/main.py"]
