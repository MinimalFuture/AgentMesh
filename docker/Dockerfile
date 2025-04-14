FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app/

# Copy and make entrypoint script executable
COPY docker/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create configuration directory
RUN mkdir -p /config

# Set environment variables
ENV CONFIG_PATH=/app/config.yaml
ENV DOCKER_CONTAINER=true

# Set entrypoint
CMD ["/app/entrypoint.sh"]
