FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app/

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create configuration directory
RUN mkdir -p /config

# Set environment variable pointing to config file
ENV CONFIG_PATH=/config/config.yaml

# Set entrypoint
CMD ["/app/entrypoint.sh"]
