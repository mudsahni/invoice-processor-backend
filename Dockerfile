FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies including SSL certificates
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Update pip and install certificates
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir certifi

# Copy requirements file
COPY src/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY src /app/

# Set environment variable for SSL verification
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Expose port
EXPOSE 5000

# Command to run Gunicorn with your app (replace 'app:main' with the correct entry point)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
