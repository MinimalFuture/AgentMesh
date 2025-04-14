FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libwayland-client0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files first for better layer caching
COPY requirements.txt requirements-optional.txt /app/

# Install required and optional dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-optional.txt

# Install Playwright
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium

# Copy project files
COPY . /app/

# Copy and make entrypoint script executable
COPY docker/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Install the package itself
RUN pip install --no-cache-dir -e .

# Create configuration directory
RUN mkdir -p /config

# Set environment variables
ENV CONFIG_PATH=/app/config.yaml
ENV DOCKER_CONTAINER=true
# Set Playwright environment variables
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Set entrypoint
CMD ["/app/entrypoint.sh"]
