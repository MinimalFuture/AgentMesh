FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create configuration directory
RUN mkdir -p /config

# Set environment variable pointing to config file
ENV CONFIG_PATH=/config/config.yaml

# Set entrypoint
ENTRYPOINT ["python", "-m", "agentmesh"]
